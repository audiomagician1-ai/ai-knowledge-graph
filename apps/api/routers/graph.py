"""图谱引擎 API — 知识图谱查询（JSON fallback + Neo4j）"""

import json
import os
from fastapi import APIRouter, Query, HTTPException
from typing import Optional

router = APIRouter()

# 种子图谱 JSON 路径（Neo4j 不可用时 fallback）
SEED_JSON = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data", "seed", "programming", "seed_graph.json",
)

_seed_cache: dict | None = None


def _load_seed() -> dict:
    """懒加载种子图谱 JSON"""
    global _seed_cache
    if _seed_cache is None:
        with open(SEED_JSON, "r", encoding="utf-8") as f:
            _seed_cache = json.load(f)
    return _seed_cache


@router.get("/data")
async def get_graph_data(
    domain_id: Optional[str] = Query(None),
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
        edges = [e for e in edges if e["source_id"] in concept_ids or e["target_id"] in concept_ids]

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

