"""Learning Intelligence API — Review prioritization + Session replay.

Extracted from learning_extended.py (V3.8 code health) to keep router files under 800 lines.

Provides:
- Smart review priority (V3.2)
- Session replay timeline (V3.5)
"""

import time

from typing import Optional

from fastapi import APIRouter, Query
from utils.logger import get_logger

from db.sqlite_client import get_all_progress, get_history, get_streak

logger = get_logger(__name__)

router = APIRouter()


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
# V3.5 Session Replay
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
