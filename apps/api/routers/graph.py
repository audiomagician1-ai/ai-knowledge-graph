"""图谱引擎 API — 知识图谱 CRUD + 路径计算"""

from fastapi import APIRouter, Query
from typing import Optional

router = APIRouter()


@router.get("/data")
async def get_graph_data(domain_id: Optional[str] = Query(None)):
    """获取图谱数据（节点+边）"""
    # TODO: Phase 1 — Neo4j 查询
    return {"nodes": [], "edges": [], "message": "图谱引擎将在 Phase 1 实现"}


@router.get("/domains")
async def get_domains():
    """获取所有领域"""
    return [
        {
            "id": "programming",
            "name": "编程",
            "description": "从Hello World到系统架构",
            "icon": "💻",
            "color": "#6366f1",
        }
    ]


@router.get("/concepts/{concept_id}")
async def get_concept(concept_id: str):
    """获取概念详情"""
    # TODO: Phase 1 — Neo4j 查询
    return {"id": concept_id, "message": "概念查询将在 Phase 1 实现"}


@router.get("/concepts/{concept_id}/neighbors")
async def get_neighbors(concept_id: str, depth: int = Query(1, ge=1, le=3)):
    """获取概念的邻居节点"""
    # TODO: Phase 1 — Neo4j 图遍历
    return {"nodes": [], "edges": [], "depth": depth}
