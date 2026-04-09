"""学习引擎扩展 API — 数据导入导出 + 自适应学习路径 + 知识缺口检测。

Extracted from learning.py (V2.10 code health) to keep router files under 800 lines.

Provides:
- Full data export (GDPR compliant) (V1.3)
- Full data import with merge (V1.3)
- Adaptive learning path (V2.3)
- Knowledge gap detection (V2.3)
"""

import json
import os
import sys
import time

from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from utils.logger import get_logger

from db.sqlite_client import (
    get_all_progress, get_progress, get_history, get_streak, get_bkt_state,
    get_unlocked_keys, start_learning, record_assessment, refresh_streak,
    update_streak, update_bkt_state, unlock_achievement,
)

logger = get_logger(__name__)

router = APIRouter()



# ── Data Export (GDPR / portability) ────────────────────────

@router.get("/export")
async def export_all_data():
    """Export all user learning data as a JSON bundle.
    
    Returns progress, history, streak, achievements, and FSRS/BKT state.
    This data can be imported on another device or used as backup.
    """
    from db.sqlite_client import (
        get_all_progress, get_history, get_streak,
        get_all_bkt_states, get_all_achievements,
    )
    try:
        progress = get_all_progress()
        history = get_history(limit=10000)
        streak = get_streak()
        bkt_states = get_all_bkt_states()
        achievements = get_all_achievements()
    except Exception as e:
        logger.error("Export failed: %s", e)
        raise HTTPException(status_code=500, detail="数据导出失败")
    
    return {
        "version": "1.0",
        "exported_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat().replace("+00:00", "Z"),
        "progress": progress,
        "history": history,
        "streak": streak,
        "bkt_states": bkt_states,
        "achievements": achievements,
    }


class ImportDataRequest(BaseModel):
    """Import request — accepts the same format as /export output."""
    version: str = Field(default="1.0")
    progress: list[dict] = Field(default_factory=list)
    history: list[dict] = Field(default_factory=list)
    streak: Optional[dict] = None
    achievements: list[dict] = Field(default_factory=list)


@router.post("/import")
async def import_data(req: ImportDataRequest):
    """Import learning data from a JSON backup (exported via /export).

    Merge strategy:
    - Progress: upsert — existing data with higher mastery is preserved
    - History: append — deduplicated by (concept_id, timestamp)
    - Streak: max — keeps the longer streak
    - Achievements: merge — keeps all unlocked achievements
    
    Returns counts of imported items.
    """
    from db.sqlite_client import upsert_progress, add_history, get_db, get_progress

    imported_progress = 0
    imported_history = 0
    imported_achievements = 0

    _valid_statuses = {'not_started', 'learning', 'mastered'}

    # Import progress
    for item in req.progress:
        concept_id = item.get("concept_id", "")
        if not concept_id or len(concept_id) > 200:
            continue
        status = item.get("status", "learning")
        if status not in _valid_statuses:
            status = "learning"

        existing = get_progress(concept_id)
        if existing and existing.get("status") == "mastered":
            continue  # Never downgrade mastered concepts

        mastery = min(100, max(0, float(item.get("mastery_score", 0))))
        mastered = status == "mastered"

        upsert_progress(
            concept_id=concept_id,
            concept_name=item.get("concept_name", concept_id),
            status=status,
            mastery_score=mastery,
            sessions=int(item.get("sessions", 1)),
            total_time_sec=int(item.get("total_time_sec", 0)),
        )
        imported_progress += 1

    # Import history (deduplicate by concept_id + timestamp)
    existing_history = set()
    try:
        with get_db() as conn:
            rows = conn.execute("SELECT concept_id, timestamp FROM learning_history").fetchall()
            existing_history = {(r["concept_id"], r["timestamp"]) for r in rows}
    except Exception:
        pass

    for entry in req.history:
        cid = entry.get("concept_id", "")
        ts = entry.get("timestamp", 0)
        if not cid or (cid, ts) in existing_history:
            continue
        try:
            add_history(
                concept_id=cid,
                concept_name=entry.get("concept_name", cid),
                score=float(entry.get("score", 0)),
                mastered=bool(entry.get("mastered", False)),
            )
            imported_history += 1
        except Exception:
            continue

    # Import streak (max merge)
    if req.streak:
        try:
            with get_db() as conn:
                imported_streak = req.streak
                conn.execute(
                    """UPDATE streak SET 
                       current_streak = MAX(current_streak, ?),
                       longest_streak = MAX(longest_streak, ?),
                       last_date = MAX(last_date, COALESCE(?, last_date))
                       WHERE id = 1""",
                    (
                        imported_streak.get("current_streak", 0),
                        imported_streak.get("longest_streak", 0),
                        imported_streak.get("last_date"),
                    ),
                )
        except Exception as e:
            logger.warning("Streak import failed: %s", e)

    # Import achievements
    for ach in req.achievements:
        key = ach.get("key", "")
        if not key or not ach.get("unlocked"):
            continue
        try:
            unlock_achievement(key)
            imported_achievements += 1
        except Exception:
            continue

    logger.info("Import completed: %d progress, %d history, %d achievements",
                imported_progress, imported_history, imported_achievements)

    return {
        "success": True,
        "imported_progress": imported_progress,
        "imported_history": imported_history,
        "imported_achievements": imported_achievements,
    }


# ════════════════════════════════════════════
# V2.3 Adaptive Learning Intelligence
# ════════════════════════════════════════════

@router.get("/adaptive-path/{domain_id}")
async def get_adaptive_path(
    domain_id: str,
    limit: int = Query(10, ge=1, le=30),
    progress: Optional[str] = Query(None, description="JSON: {concept_id: {status, mastery}}"),
):
    """Get personalized adaptive learning path for a domain.

    Fuses three signal sources into a unified priority queue:
    1. **FSRS reviews**: overdue spaced-repetition items (highest priority)
    2. **Knowledge gaps**: unmastered prereqs blocking downstream progress
    3. **Frontier learning**: new concepts on the optimal next-step frontier

    Returns an ordered list of steps, each with action type and reasons.
    """
    import json as _json
    from routers.graph import _load_seed, _load_cross_links
    from engines.graph.pathfinder import Pathfinder, UserProgress as PFUserProgress
    from db.sqlite_client import get_due_concepts

    seed = _load_seed(domain_id)
    pf = Pathfinder(seed["concepts"], seed["edges"], _load_cross_links())

    # Parse user progress
    user_progress: dict[str, PFUserProgress] = {}
    if progress:
        try:
            raw = _json.loads(progress)
            for cid, data in raw.items():
                if isinstance(data, dict):
                    user_progress[cid] = PFUserProgress(
                        concept_id=cid,
                        status=data.get("status", "not_started"),
                        mastery=float(data.get("mastery", 0.0)),
                    )
        except (ValueError, TypeError):
            pass

    # Also load DB progress if no query param provided
    if not user_progress:
        all_db_progress = get_all_progress()
        for p in all_db_progress:
            cid = p["concept_id"]
            user_progress[cid] = PFUserProgress(
                concept_id=cid,
                status=p.get("status", "not_started"),
                mastery=p.get("mastery_score", 0) / 100.0,
            )

    # Get FSRS due concepts
    now = time.time()
    due_items = get_due_concepts(before=now + 86400, limit=200)
    domain_cids = {c["id"] for c in seed["concepts"]}
    fsrs_due = {
        d["concept_id"]: d["fsrs_due"]
        for d in due_items
        if d["concept_id"] in domain_cids and d["fsrs_due"] > 0
    }

    steps = pf.adaptive_path(
        user_progress,
        domain_id=domain_id,
        fsrs_due=fsrs_due,
        limit=limit,
    )

    concept_map = {c["id"]: c for c in seed["concepts"]}
    return {
        "domain_id": domain_id,
        "steps": [
            {
                "concept_id": s.concept_id,
                "name": s.name,
                "action": s.action,
                "priority": round(s.priority, 1),
                "reasons": s.reasons,
                "estimated_minutes": s.estimated_minutes,
                "difficulty": s.difficulty,
                "subdomain_id": s.subdomain_id,
            }
            for s in steps
        ],
        "total_steps": len(steps),
        "review_count": sum(1 for s in steps if s.action == "review"),
        "gap_count": sum(1 for s in steps if s.action == "fill_gap"),
        "learn_count": sum(1 for s in steps if s.action == "learn"),
    }


@router.get("/knowledge-gaps/{domain_id}")
async def get_knowledge_gaps(
    domain_id: str,
    limit: int = Query(10, ge=1, le=50),
    progress: Optional[str] = Query(None, description="JSON: {concept_id: {status, mastery}}"),
):
    """Detect knowledge gaps: unmastered prerequisites blocking downstream progress.

    A gap is a concept that is not yet mastered but is required by one or more
    downstream concepts. Gaps are ranked by how many concepts they unblock.

    Use this to identify the highest-leverage concepts to study next.
    """
    import json as _json
    from routers.graph import _load_seed, _load_cross_links
    from engines.graph.pathfinder import Pathfinder, UserProgress as PFUserProgress

    seed = _load_seed(domain_id)
    pf = Pathfinder(seed["concepts"], seed["edges"], _load_cross_links())

    user_progress: dict[str, PFUserProgress] = {}
    if progress:
        try:
            raw = _json.loads(progress)
            for cid, data in raw.items():
                if isinstance(data, dict):
                    user_progress[cid] = PFUserProgress(
                        concept_id=cid,
                        status=data.get("status", "not_started"),
                        mastery=float(data.get("mastery", 0.0)),
                    )
        except (ValueError, TypeError):
            pass

    if not user_progress:
        all_db_progress = get_all_progress()
        for p in all_db_progress:
            cid = p["concept_id"]
            user_progress[cid] = PFUserProgress(
                concept_id=cid,
                status=p.get("status", "not_started"),
                mastery=p.get("mastery_score", 0) / 100.0,
            )

    gaps = pf.knowledge_gaps(user_progress, domain_id=domain_id, limit=limit)

    return {
        "domain_id": domain_id,
        "gaps": [
            {
                "concept_id": g.concept_id,
                "name": g.name,
                "blocked_count": g.blocked_count,
                "blocked_concepts": g.blocked_concepts,
                "difficulty": g.difficulty,
                "status": g.status,
            }
            for g in gaps
        ],
        "total_gaps": len(gaps),
    }

