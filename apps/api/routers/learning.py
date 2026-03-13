"""学习引擎 API — 进度追踪 + FSRS调度 + 知识追踪"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/stats/{user_id}")
async def get_learning_stats(user_id: str):
    """获取用户学习统计"""
    # TODO: Phase 3 — Supabase查询
    return {
        "total_concepts": 0,
        "mastered_count": 0,
        "learning_count": 0,
        "available_count": 0,
        "locked_count": 0,
        "total_study_time_sec": 0,
        "current_streak": 0,
        "longest_streak": 0,
        "message": "学习统计将在 Phase 3 实现",
    }


@router.get("/status/{user_id}")
async def get_concept_statuses(user_id: str):
    """获取用户所有概念的学习状态"""
    # TODO: Phase 3 — 状态机查询
    return []


@router.post("/unlock/{concept_id}")
async def unlock_concept(concept_id: str):
    """点亮/解锁概念节点"""
    # TODO: Phase 3 — 前置依赖检查 + 状态转换
    return {"success": False, "message": "节点点亮将在 Phase 3 实现"}
