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

from fastapi import APIRouter, HTTPException, Query
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


# ════════════════════════════════════════════
# V3.1 Prerequisite Readiness Check
# ════════════════════════════════════════════


@router.get("/prerequisite-check/{concept_id}")
async def prerequisite_check(
    concept_id: str,
    progress: Optional[str] = Query(None, description="JSON: {concept_id: {status, mastery}}"),
):
    """Check readiness to learn a specific concept based on prerequisite mastery.

    Analyses the concept's direct prerequisites and returns:
    - Overall readiness score (0-100)
    - Per-prerequisite status (mastered/learning/not_started)
    - Recommendation: ready / partially_ready / not_ready
    - Suggested prerequisites to study first

    This powers the pre-learning readiness check widget.
    """
    import json as _json
    from routers.graph import _load_seed, _load_domains

    # Find which domain this concept belongs to
    all_domains = _load_domains()
    target_domain = None
    seed = None

    for d in all_domains:
        did = d.get("id", "")
        try:
            s = _load_seed(did)
            cids = {c["id"] for c in s.get("concepts", [])}
            if concept_id in cids:
                target_domain = did
                seed = s
                break
        except Exception:
            continue

    if not seed:
        raise HTTPException(404, f"Concept '{concept_id}' not found in any domain")

    concepts = seed.get("concepts", [])
    edges = seed.get("edges", [])
    concept_map = {c["id"]: c for c in concepts}

    # Find direct prerequisites (edges where target = concept_id)
    prereq_ids: list[str] = []
    for e in edges:
        tgt = e.get("target_id") or e.get("target", "")
        src = e.get("source_id") or e.get("source", "")
        if tgt == concept_id and src in concept_map:
            prereq_ids.append(src)

    # Parse user progress
    user_progress: dict[str, dict] = {}
    if progress:
        try:
            user_progress = _json.loads(progress)
        except (ValueError, TypeError):
            pass

    if not user_progress:
        all_db = get_all_progress()
        for p in all_db:
            user_progress[p["concept_id"]] = {
                "status": p.get("status", "not_started"),
                "mastery": p.get("mastery_score", 0),
            }

    # Evaluate each prerequisite
    prereq_details = []
    mastered_count = 0
    learning_count = 0
    total_mastery = 0.0

    for pid in prereq_ids:
        pc = concept_map.get(pid, {})
        up = user_progress.get(pid, {})
        status = up.get("status", "not_started")
        mastery = float(up.get("mastery", up.get("mastery_score", 0)))
        if status == "mastered":
            mastered_count += 1
        elif status == "learning":
            learning_count += 1
        total_mastery += mastery

        prereq_details.append({
            "concept_id": pid,
            "name": pc.get("name", pid),
            "difficulty": pc.get("difficulty", 5),
            "status": status,
            "mastery": round(mastery, 1),
        })

    n = len(prereq_ids)
    if n == 0:
        readiness = 100.0
        recommendation = "ready"
    else:
        readiness = round(total_mastery / n, 1)
        if mastered_count == n:
            recommendation = "ready"
        elif mastered_count + learning_count >= n * 0.5:
            recommendation = "partially_ready"
        else:
            recommendation = "not_ready"

    # Suggest which prereqs to study first (unmastered, sorted by difficulty)
    suggested = sorted(
        [p for p in prereq_details if p["status"] != "mastered"],
        key=lambda x: x["difficulty"],
    )

    target_concept = concept_map.get(concept_id, {})

    return {
        "concept_id": concept_id,
        "concept_name": target_concept.get("name", concept_id),
        "domain_id": target_domain,
        "readiness_score": readiness,
        "recommendation": recommendation,
        "total_prerequisites": n,
        "mastered_prerequisites": mastered_count,
        "learning_prerequisites": learning_count,
        "prerequisites": prereq_details,
        "suggested_next": suggested[:5],
    }


# ════════════════════════════════════════════
# V3.2 Smart Review Priority
# ════════════════════════════════════════════


@router.get("/review-priority")
async def review_priority(
    limit: int = Query(15, ge=1, le=50),
):
    """Intelligent review prioritization combining FSRS scheduling with learning context.

    Goes beyond simple due-date ordering by factoring in:
    1. **Overdue urgency**: how far past the scheduled review date
    2. **Stability risk**: low FSRS stability = more likely to forget
    3. **Downstream value**: concepts that are prerequisites for many others
    4. **Lapse history**: concepts with more lapses need more attention

    Returns a priority-ranked review queue with reasons for each item.
    """
    from db.sqlite_client import get_due_concepts
    from routers.analytics_utils import load_seed_metadata

    now = time.time()
    # Get items due within next 24 hours (includes overdue)
    due_items = get_due_concepts(before=now + 86400, limit=200)

    if not due_items:
        return {"items": [], "total": 0}

    concept_domain_map, concept_info, domain_map = load_seed_metadata()

    # Build downstream dependency counts from all seeds
    downstream_counts: dict[str, int] = {}
    for did in domain_map:
        try:
            import json as _json, os as _os, sys as _sys
            if getattr(_sys, "frozen", False):
                sp = _os.path.join(_sys._MEIPASS, "seed_data", did, "seed_graph.json")
            else:
                sp = _os.path.join(
                    _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.dirname(__file__)))),
                    "data", "seed", did, "seed_graph.json",
                )
            if _os.path.isfile(sp):
                with open(sp, "r", encoding="utf-8") as f:
                    seed = _json.load(f)
                for e in seed.get("edges", []):
                    src = e.get("source_id") or e.get("source", "")
                    if src:
                        downstream_counts[src] = downstream_counts.get(src, 0) + 1
        except Exception:
            pass

    scored_items = []
    for item in due_items:
        cid = item["concept_id"]
        overdue_sec = max(0, now - item["fsrs_due"]) if item["fsrs_due"] > 0 else 0
        overdue_hours = overdue_sec / 3600
        stability = item.get("fsrs_stability", 1.0)
        lapses = item.get("fsrs_lapses", 0)
        downstream = downstream_counts.get(cid, 0)

        # Priority score (higher = more urgent)
        priority = 0.0
        reasons: list[str] = []

        # Factor 1: Overdue urgency (0-40 points)
        if overdue_hours > 0:
            urgency = min(40, overdue_hours * 2)
            priority += urgency
            if overdue_hours > 24:
                reasons.append(f"逾期{round(overdue_hours / 24, 1)}天")
            else:
                reasons.append(f"逾期{round(overdue_hours, 1)}小时")

        # Factor 2: Stability risk (0-30 points, lower stability = higher score)
        if stability < 10:
            risk = (10 - stability) * 3
            priority += risk
            reasons.append(f"记忆稳定性低({round(stability, 1)})")

        # Factor 3: Downstream value (0-20 points)
        if downstream > 0:
            value = min(20, downstream * 4)
            priority += value
            reasons.append(f"后续{downstream}个概念依赖此知识")

        # Factor 4: Lapse history (0-10 points)
        if lapses > 0:
            lapse_score = min(10, lapses * 3)
            priority += lapse_score
            reasons.append(f"曾遗忘{lapses}次")

        info = concept_info.get(cid, {})
        scored_items.append({
            "concept_id": cid,
            "name": info.get("name", cid),
            "domain_id": concept_domain_map.get(cid, ""),
            "difficulty": info.get("difficulty", 5),
            "priority_score": round(priority, 1),
            "reasons": reasons,
            "overdue_hours": round(overdue_hours, 1),
            "stability": round(stability, 2),
            "lapses": lapses,
            "downstream_count": downstream,
            "mastery_score": item.get("mastery_score", 0),
        })

    scored_items.sort(key=lambda x: x["priority_score"], reverse=True)

    return {
        "items": scored_items[:limit],
        "total": len(scored_items),
    }


# ════════════════════════════════════════════
# Session Replay (V3.5)
# ════════════════════════════════════════════

@router.get("/session-replay")
async def get_session_replay(
    concept_id: str = Query("", max_length=200),
    domain: str = Query("", max_length=100),
    limit: int = Query(50, ge=1, le=200),
):
    """Reconstruct a learning session timeline for review/replay.

    Groups history entries by concept and constructs a step-by-step
    learning journey with score progression and mastery events.

    Optional filters: concept_id (single concept) or domain (all concepts in domain).
    """
    from routers.graph import _load_seed

    history = get_history(1000)  # Get rich history
    if not history:
        return {"sessions": [], "total_events": 0, "summary": {}}

    # Optional domain filter
    domain_concept_ids = None
    if domain:
        try:
            seed = _load_seed(domain)
            domain_concept_ids = {c["id"] for c in seed["concepts"]}
        except Exception:
            pass

    # Filter history
    filtered = []
    for h in history:
        cid = h.get("concept_id", "")
        if concept_id and cid != concept_id:
            continue
        if domain_concept_ids is not None and cid not in domain_concept_ids:
            continue
        filtered.append(h)

    if not filtered:
        return {"sessions": [], "total_events": 0, "summary": {}}

    # Group by concept_id to build per-concept timelines
    from collections import defaultdict
    concept_groups: dict[str, list[dict]] = defaultdict(list)
    for h in filtered:
        concept_groups[h.get("concept_id", "unknown")].append(h)

    sessions = []
    total_mastered = 0
    total_attempts = 0
    best_score = 0

    for cid, events in concept_groups.items():
        # Sort by timestamp ascending
        events.sort(key=lambda e: e.get("timestamp", 0))

        steps = []
        prev_score = 0
        mastery_event = None

        for i, ev in enumerate(events):
            score = ev.get("score", 0)
            delta = score - prev_score if i > 0 else 0
            step = {
                "step": i + 1,
                "score": score,
                "delta": round(delta, 1),
                "mastered": ev.get("mastered", False),
                "timestamp": ev.get("timestamp", 0),
            }
            steps.append(step)
            prev_score = score
            if ev.get("mastered") and mastery_event is None:
                mastery_event = i + 1
            if score > best_score:
                best_score = score

        total_attempts += len(events)
        if mastery_event:
            total_mastered += 1

        sessions.append({
            "concept_id": cid,
            "concept_name": events[0].get("concept_name", cid),
            "total_attempts": len(events),
            "first_score": events[0].get("score", 0),
            "best_score": max(e.get("score", 0) for e in events),
            "latest_score": events[-1].get("score", 0),
            "mastered": any(e.get("mastered") for e in events),
            "mastered_at_step": mastery_event,
            "steps": steps[:limit],  # Cap steps per concept
        })

    # Sort by most recent activity
    sessions.sort(key=lambda s: s["steps"][-1]["timestamp"] if s["steps"] else 0, reverse=True)

    return {
        "sessions": sessions[:limit],
        "total_events": total_attempts,
        "summary": {
            "concepts_practiced": len(sessions),
            "total_attempts": total_attempts,
            "mastered_count": total_mastered,
            "best_score": best_score,
            "avg_attempts_to_master": round(
                sum(s["mastered_at_step"] for s in sessions if s["mastered_at_step"]) /
                max(1, total_mastered), 1
            ),
        },
    }

