"""学习引擎 API — 进度追踪 + 连续天数 + 历史记录
全部基于 SQLite 持久化，支持前端同步"""

import time
from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field, field_validator
from utils.logger import get_logger

logger = get_logger(__name__)

from db.sqlite_client import (
    get_all_progress, get_progress, start_learning, record_assessment,
    get_history, get_streak, refresh_streak, update_streak,
    compute_stats, get_bkt_state, update_bkt_state,
    get_unlocked_keys, get_unlocked_map, unlock_achievement,
    mark_achievements_seen, get_unseen_achievements,
)

router = APIRouter()


# ── Request Models ──

class StartLearningRequest(BaseModel):
    concept_id: str = Field(..., max_length=200)


class RecordAssessmentRequest(BaseModel):
    concept_id: str = Field(..., max_length=200)
    concept_name: str = Field(..., max_length=200)
    score: float = Field(..., ge=0, le=100)
    mastered: bool


class SyncProgressRequest(BaseModel):
    """Bulk sync from frontend localStorage → backend SQLite"""
    progress: dict[str, dict] = Field(default_factory=dict)  # concept_id → { status, mastery_score, ... }
    history: list[dict] = Field(default_factory=list)         # learning history entries
    streak: Optional[dict] = None

    @field_validator('progress')
    @classmethod
    def validate_progress_size(cls, v):
        if len(v) > 500:
            raise ValueError("progress entries cannot exceed 500")
        return v

    @field_validator('history')
    @classmethod
    def validate_history_size(cls, v):
        if len(v) > 1000:
            raise ValueError("history entries cannot exceed 1000")
        return v


# ── Endpoints ──

@router.get("/stats")
async def get_learning_stats(total_concepts: int = Query(default=400, ge=1, le=10000)):
    """获取学习统计 — total_concepts default must match ai-engineering seed_graph concept count"""
    return compute_stats(total_concepts)


@router.get("/progress")
async def get_all_concept_progress():
    """获取所有概念的学习进度"""
    return get_all_progress()


@router.get("/progress/{concept_id}")
async def get_concept_progress(concept_id: str):
    """获取单个概念的学习进度"""
    p = get_progress(concept_id)
    if not p:
        return {"concept_id": concept_id, "status": "not_started", "mastery_score": 0, "sessions": 0}
    return p


@router.post("/start")
async def start_learning_session(req: StartLearningRequest):
    """开始学习一个概念 — 标记为 learning, 计数 +1"""
    progress = start_learning(req.concept_id)
    update_streak()
    return {"success": True, "progress": progress}


@router.post("/assess")
async def record_assessment_result(req: RecordAssessmentRequest):
    """记录评估结果 — 更新学习进度 + BKT知识追踪"""
    import json as _json
    from engines.learning.tracker import KnowledgeTracker, BKTState, BKTParams

    progress = record_assessment(req.concept_id, req.concept_name, req.score, req.mastered)

    # Emit notifications for learning events (non-blocking)
    _emit_learning_notifications(req.concept_id, req.concept_name or "", req.mastered, req.score)

    # ── BKT Update ──
    tracker = KnowledgeTracker()

    # Load existing BKT state or initialize
    bkt_data = get_bkt_state(req.concept_id)
    if bkt_data:
        state = BKTState.from_db(
            p_mastery=bkt_data['p_mastery'],
            observations=bkt_data['observations'],
            correct_count=bkt_data['correct_count'],
            params_json=bkt_data['params_json'],
        )
    else:
        state = tracker.init_state()  # default params

    # Update with observation (score >= 70 = correct)
    state = tracker.update_from_score(state, req.score, threshold=70.0)

    # Persist updated BKT state
    update_bkt_state(
        req.concept_id,
        p_mastery=state.p_mastery,
        observations=state.observations,
        correct_count=state.correct_count,
        params_json=_json.dumps(state.params.to_dict()),
    )

    from routers.learning_review import check_and_unlock_achievements

    return {
        "success": True,
        "progress": progress,
        "mastered": req.mastered,
        "bkt": {
            "p_mastery": round(state.p_mastery, 4),
            "classification": state.classification,
            "observations": state.observations,
            "is_mastered": state.is_mastered,
        },
        "achievements_unlocked": check_and_unlock_achievements(),
    }


def _emit_learning_notifications(concept_id: str, concept_name: str, mastered: bool, score: int):
    """Emit notifications for learning events (mastery, milestones).

    Called after assessment recording. Failures are silently ignored
    to avoid disrupting core learning flow.
    """
    try:
        from routers.notifications import create_notification, NotificationType

        if mastered:
            create_notification(
                NotificationType.mastery,
                "概念已掌握!",
                f"你已掌握 '{concept_name or concept_id}' — 继续保持!",
                None,
                {"concept_id": concept_id, "score": score},
            )

        # Check streak milestones
        streak_data = get_streak()
        current_streak = streak_data.get("current", 0)
        milestones = [7, 14, 30, 60, 90, 180, 365]
        for ms in milestones:
            if current_streak == ms:
                create_notification(
                    NotificationType.streak,
                    f"连续学习 {ms} 天!",
                    f"太棒了! 你已连续学习 {ms} 天，保持这个势头!",
                    "/dashboard",
                    {"streak_days": ms},
                )
                break

    except Exception as e:
        logger.debug("Notification emit failed (non-critical): %s", e)


@router.get("/history")
async def get_learning_history(limit: int = Query(100, ge=1, le=1000)):
    """获取学习历史"""
    return get_history(limit)


@router.get("/streak")
async def get_learning_streak():
    """获取连续学习天数"""
    return refresh_streak()


@router.get("/mastery/{concept_id}")
async def get_concept_mastery(concept_id: str):
    """Get BKT mastery analysis for a concept.

    Returns probabilistic mastery estimate based on Bayesian Knowledge Tracing,
    including P(L), observation history, mastery classification, and predicted
    performance on next attempt.
    """
    from engines.learning.tracker import KnowledgeTracker, BKTState

    bkt_data = get_bkt_state(concept_id)
    if not bkt_data:
        return {
            "concept_id": concept_id,
            "has_bkt_data": False,
            "p_mastery": 0.0,
            "classification": "novice",
            "observations": 0,
            "is_mastered": False,
            "message": "No BKT data — concept has not been assessed yet",
        }

    state = BKTState.from_db(
        p_mastery=bkt_data['p_mastery'],
        observations=bkt_data['observations'],
        correct_count=bkt_data['correct_count'],
        params_json=bkt_data['params_json'],
    )

    tracker = KnowledgeTracker()
    predicted_correct = tracker.predict_correct(state)
    est_attempts = tracker.expected_attempts_to_mastery(state)

    return {
        "concept_id": concept_id,
        "has_bkt_data": True,
        **state.to_dict(),
        "predicted_correct_probability": round(predicted_correct, 4),
        "estimated_attempts_to_mastery": est_attempts if not state.is_mastered else 0,
    }


@router.get("/mastery")
async def get_all_mastery():
    """Get BKT mastery data for all tracked concepts."""
    from db.sqlite_client import get_all_bkt_states
    from engines.learning.tracker import BKTState

    all_bkt = get_all_bkt_states()
    results = []
    for row in all_bkt:
        state = BKTState.from_db(
            p_mastery=row['bkt_mastery'],
            observations=row['bkt_observations'],
            correct_count=row['bkt_correct_count'],
            params_json=row['bkt_params_json'],
        )
        results.append({
            "concept_id": row['concept_id'],
            "p_mastery": round(state.p_mastery, 4),
            "classification": state.classification,
            "observations": state.observations,
            "is_mastered": state.is_mastered,
        })

    mastered_count = sum(1 for r in results if r['is_mastered'])
    return {
        "total_tracked": len(results),
        "mastered_count": mastered_count,
        "items": results,
    }


@router.post("/sync")
async def sync_from_frontend(req: SyncProgressRequest):
    """从前端 localStorage 同步数据到 SQLite (一次性迁移)"""
    from db.sqlite_client import upsert_progress, add_history, get_db
    import re

    synced_progress = 0
    synced_history = 0

    # m-11 fix: Whitelist valid status values to prevent arbitrary status injection
    _valid_statuses = {'not_started', 'learning', 'mastered'}

    # Sync progress
    for concept_id, data in req.progress.items():
        if not concept_id or not isinstance(concept_id, str) or len(concept_id) > 200:
            continue  # Skip invalid concept_id
        existing = get_progress(concept_id)
        # Only sync if backend doesn't have it or frontend has newer data
        if not existing or (data.get('last_learn_at', 0) > (existing.get('last_learn_at') or 0)):
            raw_status = data.get('status', 'not_started')
            safe_status = raw_status if raw_status in _valid_statuses else 'not_started'
            # Mastered demotion protection: never downgrade mastered status via sync
            if existing and existing.get('status') == 'mastered':
                safe_status = 'mastered'
            upsert_progress(
                concept_id,
                status=safe_status,
                mastery_score=data.get('mastery_score', 0),
                last_score=data.get('last_score'),
                sessions=data.get('sessions', 0),
                total_time_sec=data.get('total_time_sec', 0),
                mastered_at=data.get('mastered_at'),
                last_learn_at=data.get('last_learn_at'),
            )
            synced_progress += 1

    # Sync history (with KeyError protection)
    for entry in req.history:
        concept_id = entry.get('concept_id')
        if not concept_id or not isinstance(concept_id, str):
            continue  # Skip invalid entries
        add_history(
            concept_id=concept_id,
            concept_name=str(entry.get('concept_name', concept_id))[:200],
            score=max(0.0, min(100.0, float(entry.get('score', 0)))),
            mastered=bool(entry.get('mastered', False)),
            timestamp=float(entry.get('timestamp', time.time())),
        )
        synced_history += 1

    # Sync streak (with input validation)
    if req.streak:
        last_date = str(req.streak.get('lastDate', ''))[:10]
        if last_date and not re.match(r'^\d{4}-\d{2}-\d{2}$', last_date):
            last_date = ''
        current = max(0, min(int(req.streak.get('current', 0)), 9999))
        longest = max(0, min(int(req.streak.get('longest', 0)), 9999))
        with get_db() as conn:
            conn.execute(
                "UPDATE streak SET current_streak = MAX(current_streak, ?), longest_streak = MAX(longest_streak, ?), last_date = ? WHERE id = 1",
                (current, longest, last_date),
            )

    return {
        "success": True,
        "synced_progress": synced_progress,
        "synced_history": synced_history,
    }


@router.get("/recommend")
async def recommend_next(
    top_k: int = Query(5, ge=1, le=50),
    domain: str = Query("ai-engineering", max_length=100),
):
    """推荐下一批最优学习节点

    算法:
    1. 收集所有 "可学习" 节点 (前置全部 mastered 或无前置)
    2. 排除已 mastered 节点
    3. 多因子打分:
       - 里程碑加权 (x1.5)
       - 难度匹配 (接近当前水平最优)
       - 下游影响力 (解锁后续节点多的优先)
       - 已开始但未完成的优先 (鼓励继续)
    4. 返回 top_k 推荐
    """
    from routers.graph import _load_seed

    seed = _load_seed(domain)
    concepts = seed["concepts"]
    edges = seed["edges"]

    # Build maps
    id_to_concept = {c["id"]: c for c in concepts}
    prereq_map: dict[str, list[str]] = {}  # target → [prereqs]
    dependents_map: dict[str, list[str]] = {}  # source → [dependents]
    for e in edges:
        if e["relation_type"] == "prerequisite":
            prereq_map.setdefault(e["target_id"], []).append(e["source_id"])
            dependents_map.setdefault(e["source_id"], []).append(e["target_id"])

    # Get current progress
    all_progress = get_all_progress()
    progress_map = {p["concept_id"]: p for p in all_progress}
    mastered_ids = {p["concept_id"] for p in all_progress if p["status"] == "mastered"}

    # Determine user's current level from mastered concepts
    mastered_difficulties = [id_to_concept[cid]["difficulty"] for cid in mastered_ids if cid in id_to_concept]
    current_level = sum(mastered_difficulties) / len(mastered_difficulties) if mastered_difficulties else 0.0
    is_new_user = len(mastered_ids) == 0

    # Find available nodes: all prereqs mastered, not yet mastered
    candidates = []
    for c in concepts:
        cid = c["id"]
        if cid in mastered_ids:
            continue
        prereqs = prereq_map.get(cid, [])
        if all(p in mastered_ids for p in prereqs):
            candidates.append(c)

    # Collect FSRS due concepts for priority boosting
    from db.sqlite_client import get_due_concepts
    now = time.time()
    due_items = get_due_concepts(before=now, limit=200)
    due_concept_ids = {d["concept_id"]: d for d in due_items}

    # Collect BKT mastery data for smarter prioritization
    from db.sqlite_client import get_all_bkt_states
    bkt_states = {r["concept_id"]: r for r in get_all_bkt_states()}

    # Score each candidate
    scored = []
    for c in candidates:
        cid = c["id"]
        score = 0.0

        diff = c["difficulty"]

        if is_new_user:
            # New user: strongly prefer lowest difficulty (dominant factor)
            # diff=1 → 50, diff=2 → 40, diff=3 → 30, diff=4 → 20, diff=5 → 10
            score += max(0, 60.0 - diff * 10.0)
            # Minor tiebreakers (cannot override difficulty ordering)
            if c.get("is_milestone", False):
                score += 3.0
            downstream = len(dependents_map.get(cid, []))
            score += min(downstream * 0.5, 3.0)
            est_min = c.get("estimated_minutes", 30)
            if est_min <= 15:
                score += 1.0
        else:
            # Factor 1: Milestone bonus
            if c.get("is_milestone", False):
                score += 15.0

            # Factor 2: Difficulty match (bell curve around current level, prefer slightly harder)
            optimal_diff = current_level + 1.0  # aim slightly above
            distance = abs(diff - optimal_diff)
            score += max(0, 10.0 - distance * 2.0)

            # Factor 3: Downstream influence (more dependents = higher value)
            downstream = len(dependents_map.get(cid, []))
            score += min(downstream * 2.0, 10.0)

            # Factor 4: Already started (encourage completion)
            prog = progress_map.get(cid)
            if prog and prog["status"] == "learning":
                score += 8.0
                # Higher bonus if they've already scored on it
                if prog.get("last_score") and prog["last_score"] > 0:
                    score += 5.0

            # Factor 5: Estimated time (prefer shorter when tied)
            est_min = c.get("estimated_minutes", 30)
            if est_min <= 15:
                score += 2.0
            elif est_min <= 25:
                score += 1.0

            # Factor 6: FSRS due-review priority boost
            if cid in due_concept_ids:
                due_data = due_concept_ids[cid]
                overdue_days = max(0, (now - due_data["fsrs_due"]) / 86400)
                # Strong boost for due reviews: 20 base + overdue bonus
                score += 20.0 + min(overdue_days * 2.0, 10.0)

            # Factor 7: BKT mastery-aware prioritization
            # Concepts with partial mastery (0.3-0.7) are "in the zone of proximal development"
            # — ideal for learning. Very low P(L) may need prerequisites; very high may be close to mastered.
            if cid in bkt_states:
                bkt = bkt_states[cid]
                p_l = bkt["bkt_mastery"]
                if 0.30 <= p_l < 0.70:
                    # Zone of proximal development — high learning potential
                    score += 8.0
                elif 0.70 <= p_l < 0.90:
                    # Close to mastery — one more push
                    score += 5.0
                elif p_l < 0.30 and bkt["bkt_observations"] >= 2:
                    # Struggling — slight deprioritize (may need prerequisites)
                    score -= 3.0

        scored.append({"concept": c, "score": score})

    # Sort by score descending, then difficulty ascending (tiebreaker for same score)
    scored.sort(key=lambda x: (-x["score"], x["concept"]["difficulty"], x["concept"]["id"]))

    # Return top_k
    recommendations = []
    for item in scored[:top_k]:
        c = item["concept"]
        prog = progress_map.get(c["id"])
        bkt = bkt_states.get(c["id"])
        rec = {
            "concept_id": c["id"],
            "name": c["name"],
            "subdomain_id": c["subdomain_id"],
            "difficulty": c["difficulty"],
            "estimated_minutes": c["estimated_minutes"],
            "is_milestone": c.get("is_milestone", False),
            "score": round(item["score"], 1),
            "reason": _recommend_reason(c, prog, current_level, dependents_map, due_concept_ids, bkt_states),
            "status": prog["status"] if prog else "not_started",
        }
        if bkt:
            rec["bkt_mastery"] = round(bkt["bkt_mastery"], 4)
        recommendations.append(rec)

    return {
        "recommendations": recommendations,
        "current_level": round(current_level, 1),
        "mastered_count": len(mastered_ids),
        "total_concepts": len(concepts),
        "due_review_count": len(due_concept_ids),
    }


def _recommend_reason(concept: dict, progress: dict | None, current_level: float,
                      deps_map: dict, due_map: dict | None = None,
                      bkt_map: dict | None = None) -> str:
    """Generate a human-readable reason for the recommendation."""
    reasons = []
    if due_map and concept["id"] in due_map:
        reasons.append("📅 复习到期")
    if progress and progress["status"] == "learning":
        reasons.append("继续上次的学习")
    if concept.get("is_milestone"):
        reasons.append("🏆 里程碑节点")
    downstream = len(deps_map.get(concept["id"], []))
    if downstream >= 3:
        reasons.append(f"解锁 {downstream} 个后续知识点")
    # BKT mastery-aware reason
    if bkt_map and concept["id"] in bkt_map:
        p_l = bkt_map[concept["id"]]["bkt_mastery"]
        if 0.30 <= p_l < 0.70:
            reasons.append("🧠 学习关键期")
        elif 0.70 <= p_l < 0.90:
            reasons.append("🔥 即将掌握")
    if not reasons:
        diff = concept["difficulty"]
        if diff <= current_level:
            reasons.append("难度匹配，易于掌握")
        else:
            reasons.append("适当挑战，提升水平")
    return " · ".join(reasons)


# -- FSRS Review + Achievement endpoints moved to learning_review.py (V3.5 split) --
# -- Export/Import/Adaptive endpoints moved to learning_extended.py (V2.10 split) --
