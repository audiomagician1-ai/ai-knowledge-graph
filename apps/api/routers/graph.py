"""图谱引擎 API — 知识图谱查询（JSON fallback + Neo4j）"""

import json
import os
import sys
import threading
from fastapi import APIRouter, Query, HTTPException
from typing import Optional

router = APIRouter()


def _get_seed_path() -> str:
    """Get seed graph JSON path — works both in dev and PyInstaller frozen mode"""
    if getattr(sys, 'frozen', False):
        # PyInstaller: data bundled under _MEIPASS
        return os.path.join(sys._MEIPASS, "seed_data", "seed_graph.json")
    # Dev mode: relative to project root (apps/api/routers/graph.py → 4 levels up)
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        "data", "seed", "programming", "seed_graph.json",
    )


SEED_JSON = _get_seed_path()

_seed_cache: dict | None = None
_seed_lock = threading.Lock()


def _load_seed() -> dict:
    """懒加载种子图谱 JSON（线程安全）"""
    global _seed_cache
    if _seed_cache is not None:
        return _seed_cache
    with _seed_lock:
        if _seed_cache is None:  # double-check after lock
            with open(SEED_JSON, "r", encoding="utf-8") as f:
                _seed_cache = json.load(f)
    return _seed_cache


@router.get("/data")
async def get_graph_data(
    subdomain_id: Optional[str] = Query(None),
):
    """获取图谱数据（节点+边）"""
    seed = _load_seed()
    concepts = seed["concepts"]
    edges = seed["edges"]

    # 过滤
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
            "id": f"{e['source_id']}-{e['target_id']}",
            "source": e["source_id"],
            "target": e["target_id"],
            "relation_type": e["relation_type"],
            "strength": e["strength"],
        }
        for e in edges
    ]

    return {"nodes": nodes, "edges": graph_edges}


@router.get("/domains")
async def get_domains():
    """获取所有领域"""
    seed = _load_seed()
    return [seed["domain"]]


@router.get("/subdomains")
async def get_subdomains(domain_id: Optional[str] = Query(None)):
    """获取子域列表"""
    seed = _load_seed()
    subdomains = seed["subdomains"]
    # 附加概念数量
    concept_counts = {}
    for c in seed["concepts"]:
        sd = c["subdomain_id"]
        concept_counts[sd] = concept_counts.get(sd, 0) + 1

    return [
        {**sd, "concept_count": concept_counts.get(sd["id"], 0)}
        for sd in subdomains
    ]


@router.get("/concepts/{concept_id}")
async def get_concept(concept_id: str):
    """获取概念详情"""
    seed = _load_seed()
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
async def get_neighbors(concept_id: str, depth: int = Query(1, ge=1, le=3)):
    """获取概念的邻居节点"""
    seed = _load_seed()
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
async def get_graph_stats():
    """图谱统计信息"""
    seed = _load_seed()
    return seed["meta"]


# ── RAG 知识库文档 API ─────────────────────────────────

def _get_rag_dir() -> str:
    """获取 RAG 文档目录路径"""
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, "rag_data")
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "data", "rag",
    )


RAG_DIR = _get_rag_dir()
_rag_index_cache: dict | None = None
_rag_lock = threading.Lock()  # m-18: Thread safety for RAG index loading


def _load_rag_index() -> dict:
    """懒加载 RAG 索引 (thread-safe)"""
    global _rag_index_cache
    if _rag_index_cache is not None:
        return _rag_index_cache
    with _rag_lock:
        # Double-check after acquiring lock
        if _rag_index_cache is not None:
            return _rag_index_cache
        index_path = os.path.join(RAG_DIR, "_index.json")
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                _rag_index_cache = json.load(f)
        else:
            _rag_index_cache = {"documents": [], "stats": {}}
    return _rag_index_cache


@router.get("/rag/{concept_id}")
async def get_rag_document(concept_id: str):
    """获取概念的 RAG 参考文档"""
    # 查找文档路径
    index = _load_rag_index()
    doc_entry = None
    for d in index.get("documents", []):
        if d["id"] == concept_id:
            doc_entry = d
            break

    if not doc_entry:
        raise HTTPException(status_code=404, detail=f"RAG 文档不存在: {concept_id}")

    doc_path = os.path.normpath(os.path.join(RAG_DIR, doc_entry["file"]))
    # Path traversal protection (case-insensitive on Windows)
    if not os.path.normcase(doc_path).startswith(os.path.normcase(os.path.normpath(RAG_DIR))):
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
        "difficulty": doc_entry.get("difficulty", 0),
        "is_milestone": doc_entry.get("is_milestone", False),
        "content": content,
        "char_count": len(content),
    }


@router.get("/rag")
async def get_rag_stats():
    """获取 RAG 知识库统计"""
    index = _load_rag_index()
    return {
        "total_docs": index.get("stats", {}).get("total_docs", 0),
        "total_chars": index.get("stats", {}).get("total_chars", 0),
        "by_subdomain": index.get("stats", {}).get("by_subdomain", {}),
        "version": index.get("version", ""),
        "generated_at": index.get("generated_at", ""),
    }

