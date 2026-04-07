"""图谱引擎 API — 多域知识图谱查询（JSON fallback + Neo4j）"""

import hashlib
import json
import os
import sys
import threading
from fastapi import APIRouter, Query, HTTPException, Request, Response
from typing import Optional
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

DEFAULT_DOMAIN = "ai-engineering"


# ── 路径工具 ──────────────────────────────────────────────

def _project_root() -> str:
    """项目根目录 — 兼容 dev 和 PyInstaller frozen 模式"""
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


def _get_seed_path(domain_id: str = DEFAULT_DOMAIN) -> str:
    """Get seed graph JSON path for a given domain."""
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, "seed_data", domain_id, "seed_graph.json")
    return os.path.join(_project_root(), "data", "seed", domain_id, "seed_graph.json")


def _get_domains_path() -> str:
    """Get the domain registry JSON path."""
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, "seed_data", "domains.json")
    return os.path.join(_project_root(), "data", "seed", "domains.json")


# ── 种子图谱缓存 (per-domain) ────────────────────────────

_seed_cache: dict[str, dict] = {}
_seed_lock = threading.Lock()


def _load_seed(domain_id: str = DEFAULT_DOMAIN) -> dict:
    """懒加载指定域的种子图谱 JSON（线程安全，per-domain 缓存）"""
    if domain_id in _seed_cache:
        return _seed_cache[domain_id]
    with _seed_lock:
        if domain_id not in _seed_cache:
            path = _get_seed_path(domain_id)
            if not os.path.exists(path):
                raise HTTPException(
                    status_code=404,
                    detail=f"域 '{domain_id}' 的种子数据不存在",
                )
            with open(path, "r", encoding="utf-8") as f:
                _seed_cache[domain_id] = json.load(f)
            logger.info("Loaded seed graph: %s", domain_id)
    return _seed_cache[domain_id]


# ── 域注册表缓存 ─────────────────────────────────────────

_domains_cache: list | None = None
_domains_lock = threading.Lock()


def _load_domains() -> list[dict]:
    """懒加载域注册表 JSON（线程安全）"""
    global _domains_cache
    if _domains_cache is not None:
        return _domains_cache
    with _domains_lock:
        if _domains_cache is None:
            path = _get_domains_path()
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                _domains_cache = data.get("domains", [])
            else:
                # Fallback: 从默认域的 seed_graph 中读取 domain 字段
                seed = _load_seed(DEFAULT_DOMAIN)
                _domains_cache = [seed.get("domain", {"id": DEFAULT_DOMAIN, "name": "AI工程"})]
    return _domains_cache


# ── 域列表 API ────────────────────────────────────────────

@router.get("/domains")
async def get_domains(response: Response):
    """获取所有可用知识域列表，包含每个域的统计信息"""
    domains = _load_domains()
    result = []
    for d in domains:
        domain_id = d["id"]
        stats = {}
        try:
            seed = _load_seed(domain_id)
            stats = {
                "total_concepts": len(seed.get("concepts", [])),
                "total_edges": len(seed.get("edges", [])),
                "subdomains": len(seed.get("subdomains", [])),
            }
        except HTTPException:
            stats = {"total_concepts": 0, "total_edges": 0, "subdomains": 0}
        result.append({**d, "stats": stats})
    # Domain list is static — cache for 1 hour, revalidate in background
    response.headers["Cache-Control"] = "public, max-age=3600, stale-while-revalidate=86400"
    return result


# ── 图谱数据 API ─────────────────────────────────────────

@router.get("/data")
async def get_graph_data(
    response: Response,
    domain: str = Query(DEFAULT_DOMAIN, description="知识域ID"),
    subdomain_id: Optional[str] = Query(None),
):
    """获取图谱数据（节点+边），支持按域和子域过滤"""
    seed = _load_seed(domain)
    concepts = seed["concepts"]
    edges = seed["edges"]

    # 子域过滤
    if subdomain_id:
        concept_ids = {c["id"] for c in concepts if c["subdomain_id"] == subdomain_id}
        concepts = [c for c in concepts if c["subdomain_id"] == subdomain_id]
        edges = [e for e in edges if e["source_id"] in concept_ids and e["target_id"] in concept_ids]

    # 转换为前端 GraphData 格式
    nodes = [
        {
            "id": c["id"],
            "label": c["name"],
            "domain_id": c["domain_id"],
            "subdomain_id": c["subdomain_id"],
            "difficulty": c["difficulty"],
            "status": "not_started",  # 默认状态，需结合用户数据
            "is_milestone": c.get("is_milestone", False),
            "estimated_minutes": c["estimated_minutes"],
            "content_type": c["content_type"],
            "tags": c["tags"],
        }
        for c in concepts
    ]

    graph_edges = [
        {
            "id": f"{e.get('source_id') or e.get('source')}-{e.get('target_id') or e.get('target')}",
            "source": e.get("source_id") or e.get("source"),
            "target": e.get("target_id") or e.get("target"),
            "relation_type": e.get("relation_type") or e.get("type", "related"),
            "strength": e.get("strength", 0.5),
        }
        for e in edges
    ]

    # Graph data is static seed data — cache for 1 hour
    response.headers["Cache-Control"] = "public, max-age=3600, stale-while-revalidate=86400"
    return {"nodes": nodes, "edges": graph_edges}


@router.get("/subdomains")
async def get_subdomains(domain: str = Query(DEFAULT_DOMAIN, description="知识域ID")):
    """获取指定域的子域列表"""
    seed = _load_seed(domain)
    subdomains = seed["subdomains"]
    # 附加概念数量
    concept_counts: dict[str, int] = {}
    for c in seed["concepts"]:
        sd = c["subdomain_id"]
        concept_counts[sd] = concept_counts.get(sd, 0) + 1

    return [
        {**sd, "concept_count": concept_counts.get(sd["id"], 0)}
        for sd in subdomains
    ]


@router.get("/concepts/{concept_id}")
async def get_concept(concept_id: str, domain: str = Query(DEFAULT_DOMAIN)):
    """获取概念详情"""
    seed = _load_seed(domain)
    for c in seed["concepts"]:
        if c["id"] == concept_id:
            # 找到先修和后续
            prerequisites = []
            dependents = []
            for e in seed["edges"]:
                if e["relation_type"] == "prerequisite":
                    if e["target_id"] == concept_id:
                        prerequisites.append(e["source_id"])
                    if e["source_id"] == concept_id:
                        dependents.append(e["target_id"])

            return {
                **c,
                "prerequisites": prerequisites,
                "dependents": dependents,
            }
    raise HTTPException(status_code=404, detail=f"概念不存在: {concept_id}")


@router.get("/concepts/{concept_id}/neighbors")
async def get_neighbors(
    concept_id: str,
    depth: int = Query(1, ge=1, le=3),
    domain: str = Query(DEFAULT_DOMAIN),
):
    """获取概念的邻居节点"""
    seed = _load_seed(domain)
    concept_ids = {c["id"] for c in seed["concepts"]}
    if concept_id not in concept_ids:
        raise HTTPException(status_code=404, detail=f"概念不存在: {concept_id}")

    # BFS 获取邻居
    visited = {concept_id}
    frontier = {concept_id}
    all_edges = seed["edges"]

    for _ in range(depth):
        next_frontier = set()
        for e in all_edges:
            if e["source_id"] in frontier and e["target_id"] not in visited:
                next_frontier.add(e["target_id"])
                visited.add(e["target_id"])
            if e["target_id"] in frontier and e["source_id"] not in visited:
                next_frontier.add(e["source_id"])
                visited.add(e["source_id"])
        frontier = next_frontier

    # 构建子图
    nodes = [
        {
            "id": c["id"],
            "label": c["name"],
            "domain_id": c["domain_id"],
            "subdomain_id": c["subdomain_id"],
            "difficulty": c["difficulty"],
            "status": "not_started",
            "is_milestone": c.get("is_milestone", False),
        }
        for c in seed["concepts"]
        if c["id"] in visited
    ]

    graph_edges = [
        {
            "id": f"{e['source_id']}-{e['target_id']}",
            "source": e["source_id"],
            "target": e["target_id"],
            "relation_type": e["relation_type"],
            "strength": e["strength"],
        }
        for e in all_edges
        if e["source_id"] in visited and e["target_id"] in visited
    ]

    return {"nodes": nodes, "edges": graph_edges, "center": concept_id, "depth": depth}


@router.get("/stats")
async def get_graph_stats(domain: str = Query(DEFAULT_DOMAIN)):
    """图谱统计信息"""
    seed = _load_seed(domain)
    return seed["meta"]


# ── RAG 知识库文档 API ─────────────────────────────────

def _get_rag_base_dir() -> str:
    """获取 RAG 文档根目录路径"""
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, "rag_data")
    return os.path.join(_project_root(), "data", "rag")


RAG_BASE_DIR = _get_rag_base_dir()
_rag_index_cache: dict[str, dict] = {}  # domain_id -> index data
_rag_lock = threading.Lock()  # m-18: Thread safety for RAG index loading

# Default domain for backwards compatibility
_DEFAULT_RAG_DOMAIN = "ai-engineering"


def _rag_index_path(domain_id: str) -> str:
    """Get the RAG index file path for a domain."""
    # Check domain-specific path first (works for all domains including ai-engineering)
    domain_path = os.path.join(RAG_BASE_DIR, domain_id, "_index.json")
    if os.path.exists(domain_path):
        return domain_path
    if domain_id == "ai-engineering":
        # Legacy fallback: flat index at data/rag/_index.json
        return os.path.join(RAG_BASE_DIR, "_index.json")
    return domain_path  # will not exist, _load_rag_index handles missing files


def _load_rag_index(domain_id: str = "ai-engineering") -> dict:
    """懒加载 RAG 索引 (thread-safe, per-domain)"""
    if domain_id in _rag_index_cache:
        return _rag_index_cache[domain_id]
    with _rag_lock:
        # Double-check after acquiring lock
        if domain_id in _rag_index_cache:
            return _rag_index_cache[domain_id]
        index_path = _rag_index_path(domain_id)
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                _rag_index_cache[domain_id] = json.load(f)
        else:
            _rag_index_cache[domain_id] = {"documents": [], "stats": {}}
    return _rag_index_cache[domain_id]


@router.get("/rag/{concept_id}")
async def get_rag_document(concept_id: str, domain: str = "ai-engineering"):
    """获取概念的 RAG 参考文档"""
    # 查找文档路径
    index = _load_rag_index(domain)
    doc_entry = None
    for d in index.get("documents", []):
        if d["id"] == concept_id:
            doc_entry = d
            break

    if not doc_entry:
        raise HTTPException(status_code=404, detail=f"RAG 文档不存在: {concept_id}")

    doc_path = os.path.normpath(os.path.join(RAG_BASE_DIR, doc_entry["file"]))
    # Path traversal protection (case-insensitive on Windows)
    if not os.path.normcase(doc_path).startswith(os.path.normcase(os.path.normpath(RAG_BASE_DIR))):
        raise HTTPException(status_code=400, detail="Invalid file path")
    if not os.path.exists(doc_path):
        raise HTTPException(status_code=404, detail=f"RAG 文档文件不存在: {doc_entry['file']}")

    with open(doc_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 去掉 YAML frontmatter 只返回 Markdown 正文
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            content = content[end + 3:].strip()

    return {
        "concept_id": concept_id,
        "name": doc_entry.get("name", concept_id),
        "subdomain": doc_entry.get("subdomain_id", ""),
        "domain": domain,
        "difficulty": doc_entry.get("difficulty", 0),
        "is_milestone": doc_entry.get("is_milestone", False),
        "content": content,
        "char_count": len(content),
    }


@router.get("/rag")
async def get_rag_stats(domain: str = "ai-engineering"):
    """获取 RAG 知识库统计"""
    index = _load_rag_index(domain)
    return {
        "domain": domain,
        "total_docs": index.get("stats", {}).get("total_docs", 0) or index.get("stats", {}).get("total", 0) or index.get("total_concepts", 0),
        "total_chars": index.get("stats", {}).get("total_chars", 0),
        "by_subdomain": index.get("stats", {}).get("by_subdomain", {}),
        "version": index.get("version", ""),
        "generated_at": index.get("generated_at", ""),
    }


# ── 跨球体关联链接 API ─────────────────────────────────

_cross_links_cache: list | None = None
_cross_links_lock = threading.Lock()


def _get_cross_links_path() -> str:
    """Get the cross-sphere links JSON path."""
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, "seed_data", "cross_sphere_links.json")
    return os.path.join(_project_root(), "data", "seed", "cross_sphere_links.json")


def _load_cross_links() -> list[dict]:
    """懒加载跨球体关联链接（线程安全）"""
    global _cross_links_cache
    if _cross_links_cache is not None:
        return _cross_links_cache
    with _cross_links_lock:
        if _cross_links_cache is None:
            path = _get_cross_links_path()
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                _cross_links_cache = data.get("links", [])
            else:
                _cross_links_cache = []
    return _cross_links_cache


@router.get("/cross-links")
async def get_cross_links(
    domain: Optional[str] = Query(None, description="Filter by source or target domain"),
    concept_id: Optional[str] = Query(None, description="Filter by source or target concept"),
):
    """获取跨球体关联链接，可按域或概念过滤"""
    links = _load_cross_links()

    if domain:
        links = [
            lk for lk in links
            if lk["source_domain"] == domain or lk["target_domain"] == domain
        ]

    if concept_id:
        links = [
            lk for lk in links
            if lk["source_id"] == concept_id or lk["target_id"] == concept_id
        ]

    return {
        "links": links,
        "total": len(links),
    }


# ── 图谱引擎 API (Pathfinder + Builder) ────────────────

from engines.graph.pathfinder import Pathfinder, UserProgress
from engines.graph.builder import GraphBuilder

# Engine instance cache (lazy per-domain)
_engine_cache: dict[str, dict] = {}
_engine_lock = threading.Lock()


def _get_engines(domain_id: str) -> dict:
    """Get or create Pathfinder + GraphBuilder for a domain (thread-safe)."""
    if domain_id in _engine_cache:
        return _engine_cache[domain_id]
    with _engine_lock:
        if domain_id not in _engine_cache:
            seed = _load_seed(domain_id)
            cross_links = _load_cross_links()
            pf = Pathfinder(seed["concepts"], seed["edges"], cross_links)
            gb = GraphBuilder(seed["concepts"], seed["edges"], cross_links)
            _engine_cache[domain_id] = {"pathfinder": pf, "builder": gb}
    return _engine_cache[domain_id]


def _parse_progress(progress_json: Optional[str]) -> dict[str, UserProgress]:
    """Parse progress query param (JSON string) into UserProgress dict."""
    if not progress_json:
        return {}
    try:
        raw = json.loads(progress_json)
        result = {}
        for cid, data in raw.items():
            if isinstance(data, dict):
                result[cid] = UserProgress(
                    concept_id=cid,
                    status=data.get("status", "not_started"),
                    mastery=float(data.get("mastery", 0.0)),
                )
            elif isinstance(data, str):
                result[cid] = UserProgress(concept_id=cid, status=data)
        return result
    except (json.JSONDecodeError, TypeError, ValueError):
        return {}


@router.get("/path/{target_id}")
async def get_learning_path(
    target_id: str,
    domain: str = Query(DEFAULT_DOMAIN),
    progress: Optional[str] = Query(None, description="JSON: {concept_id: {status, mastery}}"),
):
    """计算到达目标概念的最短学习路径"""
    engines = _get_engines(domain)
    pf: Pathfinder = engines["pathfinder"]
    user_progress = _parse_progress(progress)
    result = pf.shortest_path(target_id, user_progress)
    # Enrich path with concept details
    seed = _load_seed(domain)
    concept_map = {c["id"]: c for c in seed["concepts"]}
    path_details = []
    for cid in result.path:
        c = concept_map.get(cid, {})
        path_details.append({
            "id": cid,
            "name": c.get("name", cid),
            "difficulty": c.get("difficulty", 1),
            "estimated_minutes": c.get("estimated_minutes", 20),
            "status": user_progress.get(cid, UserProgress(cid)).status,
        })
    return {
        "target": target_id,
        "path": path_details,
        "total_estimated_minutes": result.total_estimated_minutes,
        "steps": result.steps,
    }


@router.get("/recommend")
async def get_recommendations(
    domain: str = Query(DEFAULT_DOMAIN),
    limit: int = Query(5, ge=1, le=20),
    progress: Optional[str] = Query(None, description="JSON: {concept_id: {status, mastery}}"),
):
    """基于用户进度推荐下一步学习概念"""
    engines = _get_engines(domain)
    pf: Pathfinder = engines["pathfinder"]
    user_progress = _parse_progress(progress)
    results = pf.recommend(user_progress, domain_id=domain, limit=limit)
    seed = _load_seed(domain)
    concept_map = {c["id"]: c for c in seed["concepts"]}
    return {
        "recommendations": [
            {
                "concept_id": r.concept_id,
                "name": concept_map.get(r.concept_id, {}).get("name", r.concept_id),
                "difficulty": concept_map.get(r.concept_id, {}).get("difficulty", 1),
                "estimated_minutes": concept_map.get(r.concept_id, {}).get("estimated_minutes", 20),
                "score": r.score,
                "reasons": r.reasons,
            }
            for r in results
        ],
        "total_candidates": len(results),
    }


@router.get("/topo-sort")
async def get_topological_order(
    domain: str = Query(DEFAULT_DOMAIN),
    subdomain: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
):
    """获取拓扑排序的学习顺序"""
    engines = _get_engines(domain)
    pf: Pathfinder = engines["pathfinder"]
    ordered = pf.topological_sort(domain_id=domain, subdomain_id=subdomain)
    seed = _load_seed(domain)
    concept_map = {c["id"]: c for c in seed["concepts"]}
    return {
        "order": [
            {
                "id": cid,
                "name": concept_map.get(cid, {}).get("name", cid),
                "difficulty": concept_map.get(cid, {}).get("difficulty", 1),
                "position": i + 1,
            }
            for i, cid in enumerate(ordered[:limit])
        ],
        "total": len(ordered),
    }


@router.get("/zpd")
async def get_zpd_subgraph(
    domain: str = Query(DEFAULT_DOMAIN),
    progress: Optional[str] = Query(None, description="JSON: {concept_id: {status, mastery}}"),
    include_mastered: bool = Query(True),
    zpd_depth: int = Query(2, ge=1, le=5),
):
    """获取个性化学习区域 (Zone of Proximal Development) 子图"""
    engines = _get_engines(domain)
    gb: GraphBuilder = engines["builder"]
    user_progress = _parse_progress(progress)
    result = gb.build_personalized_subgraph(
        user_progress,
        domain_id=domain,
        include_mastered=include_mastered,
        zpd_depth=zpd_depth,
    )
    return {
        "nodes": result.nodes,
        "edges": result.edges,
        "stats": result.stats,
    }


@router.get("/aligned-entities")
async def get_aligned_entities(
    domain: str = Query(DEFAULT_DOMAIN),
    concept_id: Optional[str] = Query(None),
):
    """获取跨域对齐实体（同一概念在不同域的映射）"""
    engines = _get_engines(domain)
    gb: GraphBuilder = engines["builder"]
    entities = gb.find_aligned_entities(concept_id=concept_id, domain_id=domain)
    return {
        "entities": [
            {
                "canonical_id": e.canonical_id,
                "canonical_name": e.canonical_name,
                "occurrences": e.occurrences,
                "description": e.description,
            }
            for e in entities
        ],
        "total": len(entities),
    }


@router.get("/zone-summary")
async def get_zone_summary(
    domain: str = Query(DEFAULT_DOMAIN),
    progress: Optional[str] = Query(None, description="JSON: {concept_id: {status, mastery}}"),
):
    """获取域级学习区域摘要（含进度统计 + 瓶颈分析）"""
    engines = _get_engines(domain)
    gb: GraphBuilder = engines["builder"]
    user_progress = _parse_progress(progress)
    return gb.learning_zone_summary(user_progress, domain)


# ── RAG Search API (fuzzy matching) ────────────────────

from engines.graph.rag import rag_retriever


@router.get("/rag/search")
async def search_rag_documents(
    q: str = Query(..., min_length=1, description="Search query"),
    domain: str = Query(DEFAULT_DOMAIN),
    limit: int = Query(5, ge=1, le=20),
):
    """搜索RAG知识文档（模糊名称/ID匹配）"""
    results = rag_retriever.search(q, domain_id=domain, limit=limit)
    return {
        "query": q,
        "domain": domain,
        "results": [
            {
                "concept_id": r.concept_id,
                "name": r.name,
                "subdomain_id": r.subdomain_id,
                "match_score": r.match_score,
                "preview": r.content[:200] + "..." if len(r.content) > 200 else r.content,
            }
            for r in results
        ],
        "total": len(results),
    }


@router.get("/rag/search/global")
async def search_rag_global(
    q: str = Query(..., min_length=2, description="Search query (min 2 chars)"),
    limit: int = Query(10, ge=1, le=30),
):
    """跨域全局搜索RAG知识文档 — 在所有域中搜索匹配概念"""
    import json as _json

    all_results = []
    # Load domains list
    data_root = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data")
    domains_file = os.path.join(data_root, "seed", "domains.json")
    if os.path.isfile(domains_file):
        with open(domains_file, "r", encoding="utf-8") as f:
            raw = _json.load(f)
        domain_list = raw.get("domains", raw) if isinstance(raw, dict) else raw
        for d in domain_list:
            domain_id = d.get("id", "")
            try:
                results = rag_retriever.search(q, domain_id=domain_id, limit=3)
                for r in results:
                    all_results.append({
                        "concept_id": r.concept_id,
                        "name": r.name,
                        "domain_id": domain_id,
                        "domain_name": d.get("name", ""),
                        "subdomain_id": r.subdomain_id,
                        "match_score": r.match_score,
                        "preview": r.content[:150] + "..." if len(r.content) > 150 else r.content,
                    })
            except Exception:
                continue

    # Sort by score and limit
    all_results.sort(key=lambda x: x["match_score"], reverse=True)
    all_results = all_results[:limit]

    return {
        "query": q,
        "results": all_results,
        "total": len(all_results),
    }


@router.get("/topology/{domain_id}")
async def get_domain_topology(domain_id: str = DEFAULT_DOMAIN):
    """
    返回域的拓扑分析: 子域统计、里程碑节点、入度/出度排行、孤立节点检测。
    用于 Graph HUD 展示和学习路径优化。
    """
    seed_path = _get_seed_path(domain_id)
    if not os.path.isfile(seed_path):
        raise HTTPException(status_code=404, detail=f"Domain '{domain_id}' not found")

    seed = _load_seed(domain_id)
    concepts = seed.get("concepts", [])
    edges = seed.get("edges", [])

    # Build adjacency data
    in_degree: dict[str, int] = {}
    out_degree: dict[str, int] = {}
    for c in concepts:
        in_degree[c["id"]] = 0
        out_degree[c["id"]] = 0
    for e in edges:
        src = e.get("source_id", e.get("source", ""))
        tgt = e.get("target_id", e.get("target", ""))
        if src in out_degree:
            out_degree[src] += 1
        if tgt in in_degree:
            in_degree[tgt] += 1

    # Subdomain stats
    subdomain_stats: dict[str, dict] = {}
    for c in concepts:
        sub = c.get("subdomain_id", "other")
        if sub not in subdomain_stats:
            subdomain_stats[sub] = {"total": 0, "milestones": 0, "avg_difficulty": 0.0, "difficulties": []}
        subdomain_stats[sub]["total"] += 1
        subdomain_stats[sub]["difficulties"].append(c.get("difficulty", 5))
        if c.get("is_milestone"):
            subdomain_stats[sub]["milestones"] += 1

    for sub, stats in subdomain_stats.items():
        diffs = stats.pop("difficulties")
        stats["avg_difficulty"] = round(sum(diffs) / len(diffs), 1) if diffs else 0

    # Entry points (in_degree == 0) and terminal nodes (out_degree == 0)
    entry_points = [cid for cid, deg in in_degree.items() if deg == 0]
    terminal_nodes = [cid for cid, deg in out_degree.items() if deg == 0]

    # Orphan nodes (no edges at all)
    connected_ids = set()
    for e in edges:
        connected_ids.add(e.get("source_id", e.get("source", "")))
        connected_ids.add(e.get("target_id", e.get("target", "")))
    orphans = [c["id"] for c in concepts if c["id"] not in connected_ids]

    # Top connected (highest in+out degree)
    combined = {cid: in_degree.get(cid, 0) + out_degree.get(cid, 0) for cid in in_degree}
    top_connected = sorted(combined.items(), key=lambda x: x[1], reverse=True)[:10]

    # Milestones
    milestones = [{"id": c["id"], "name": c.get("name", c["id"]), "difficulty": c.get("difficulty", 5)}
                  for c in concepts if c.get("is_milestone")]

    return {
        "domain_id": domain_id,
        "total_concepts": len(concepts),
        "total_edges": len(edges),
        "subdomains": subdomain_stats,
        "entry_points": entry_points[:20],
        "terminal_nodes": terminal_nodes[:20],
        "orphan_nodes": orphans,
        "milestones": milestones,
        "top_connected": [{"id": cid, "degree": deg} for cid, deg in top_connected],
    }


@router.get("/concepts/{concept_id}/context")
async def get_concept_context(
    concept_id: str,
    domain: str = Query(DEFAULT_DOMAIN),
):
    """
    返回概念的完整上下文：前置知识、后续解锁、同子域概念列表。
    用于 ChatPanel idle 视图的导航增强。
    """
    seed = _load_seed(domain)
    concept_map = {c["id"]: c for c in seed["concepts"]}

    if concept_id not in concept_map:
        raise HTTPException(status_code=404, detail=f"概念不存在: {concept_id}")

    current = concept_map[concept_id]
    edges = seed.get("edges", [])

    # Prerequisites: edges where target = concept_id, type = prerequisite → source is prereq
    prerequisites = []
    for e in edges:
        src = e.get("source_id", e.get("source", ""))
        tgt = e.get("target_id", e.get("target", ""))
        if tgt == concept_id and e.get("relation_type") == "prerequisite" and src in concept_map:
            c = concept_map[src]
            prerequisites.append({
                "id": c["id"],
                "name": c.get("name", c["id"]),
                "difficulty": c.get("difficulty", 5),
                "subdomain_id": c.get("subdomain_id", ""),
            })

    # Dependents: edges where source = concept_id, type = prerequisite → target depends on this
    dependents = []
    for e in edges:
        src = e.get("source_id", e.get("source", ""))
        tgt = e.get("target_id", e.get("target", ""))
        if src == concept_id and e.get("relation_type") == "prerequisite" and tgt in concept_map:
            c = concept_map[tgt]
            dependents.append({
                "id": c["id"],
                "name": c.get("name", c["id"]),
                "difficulty": c.get("difficulty", 5),
                "subdomain_id": c.get("subdomain_id", ""),
            })

    # Related (non-prerequisite edges)
    related = []
    for e in edges:
        src = e.get("source_id", e.get("source", ""))
        tgt = e.get("target_id", e.get("target", ""))
        if e.get("relation_type") != "prerequisite":
            if src == concept_id and tgt in concept_map:
                c = concept_map[tgt]
                related.append({"id": c["id"], "name": c.get("name", c["id"]), "sub_type": e.get("sub_type", "")})
            elif tgt == concept_id and src in concept_map:
                c = concept_map[src]
                related.append({"id": c["id"], "name": c.get("name", c["id"]), "sub_type": e.get("sub_type", "")})

    # Siblings: same subdomain, sorted by difficulty
    subdomain = current.get("subdomain_id", "")
    siblings = [
        {"id": c["id"], "name": c.get("name", c["id"]), "difficulty": c.get("difficulty", 5)}
        for c in seed["concepts"]
        if c.get("subdomain_id") == subdomain and c["id"] != concept_id
    ]
    siblings.sort(key=lambda x: x["difficulty"])

    return {
        "concept_id": concept_id,
        "name": current.get("name", concept_id),
        "subdomain_id": subdomain,
        "difficulty": current.get("difficulty", 5),
        "is_milestone": current.get("is_milestone", False),
        "prerequisites": prerequisites,
        "dependents": dependents,
        "related": related[:10],
        "siblings": siblings[:20],
        "total_siblings": len(siblings) + 1,
    }


@router.get("/compare-concepts")
async def compare_concepts(
    concept_a: str = "variables",
    concept_b: str = "loops",
    domain_id: str = DEFAULT_DOMAIN,
):
    """Compare two concepts side-by-side.

    Returns: names, difficulty, prerequisites, overlap metrics, and shared connections.
    Useful for understanding relationships between two concepts.
    """
    graph_data = _load_seed(domain_id)
    if not graph_data:
        raise HTTPException(status_code=404, detail=f"Domain not found: {domain_id}")

    nodes_by_id = {n["id"]: n for n in graph_data.get("concepts", graph_data.get("nodes", []))}

    node_a = nodes_by_id.get(concept_a)
    node_b = nodes_by_id.get(concept_b)

    if not node_a:
        raise HTTPException(status_code=404, detail=f"Concept not found: {concept_a}")
    if not node_b:
        raise HTTPException(status_code=404, detail=f"Concept not found: {concept_b}")

    # Gather connections for each concept
    edges = graph_data.get("edges", [])

    def get_connections(concept_id: str) -> set:
        connected = set()
        for e in edges:
            src = e.get("source_id", e.get("source", ""))
            tgt = e.get("target_id", e.get("target", ""))
            if src == concept_id:
                connected.add(tgt)
            elif tgt == concept_id:
                connected.add(src)
        return connected

    conn_a = get_connections(concept_a)
    conn_b = get_connections(concept_b)
    shared = conn_a & conn_b

    # Check if directly connected
    directly_connected = concept_b in conn_a or concept_a in conn_b

    # Get prereqs
    prereqs_a = [e.get("source_id", e.get("source", "")) for e in edges if e.get("target_id", e.get("target", "")) == concept_a and e.get("relation_type") == "prerequisite"]
    prereqs_b = [e.get("source_id", e.get("source", "")) for e in edges if e.get("target_id", e.get("target", "")) == concept_b and e.get("relation_type") == "prerequisite"]
    shared_prereqs = set(prereqs_a) & set(prereqs_b)

    return {
        "concept_a": {
            "id": concept_a,
            "name": node_a.get("name", concept_a),
            "difficulty": node_a.get("difficulty", 5),
            "subdomain": node_a.get("subdomain_id", ""),
            "is_milestone": node_a.get("is_milestone", False),
            "connections": len(conn_a),
            "prerequisites": prereqs_a,
        },
        "concept_b": {
            "id": concept_b,
            "name": node_b.get("name", concept_b),
            "difficulty": node_b.get("difficulty", 5),
            "subdomain": node_b.get("subdomain_id", ""),
            "is_milestone": node_b.get("is_milestone", False),
            "connections": len(conn_b),
            "prerequisites": prereqs_b,
        },
        "comparison": {
            "directly_connected": directly_connected,
            "shared_connections": list(shared)[:20],
            "shared_connection_count": len(shared),
            "shared_prerequisites": list(shared_prereqs),
            "same_subdomain": node_a.get("subdomain_id") == node_b.get("subdomain_id"),
            "difficulty_gap": abs(node_a.get("difficulty", 5) - node_b.get("difficulty", 5)),
            "similarity_score": round(
                len(shared) / max(1, len(conn_a | conn_b)) * 100, 1
            ),
        },
    }

