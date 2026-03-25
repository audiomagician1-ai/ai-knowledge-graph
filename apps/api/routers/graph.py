"""图谱引擎 API — 多域知识图谱查询（JSON fallback + Neo4j）"""

import json
import os
import sys
import threading
from fastapi import APIRouter, Query, HTTPException
from typing import Optional

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
async def get_domains():
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
    return result


# ── 图谱数据 API ─────────────────────────────────────────

@router.get("/data")
async def get_graph_data(
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

