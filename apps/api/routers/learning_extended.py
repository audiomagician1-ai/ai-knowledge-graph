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


# -- V3.2 review-priority moved to learning_intelligence.py (V3.8 split) --
# -- V3.5 session-replay moved to learning_intelligence.py (V3.8 split) --


# ═══════════════════════════════════════════
# V4.2: Learning Portfolio
# ═══════════════════════════════════════════

@router.get("/portfolio")
async def learning_portfolio():
    """Comprehensive exportable learning portfolio.

    Aggregates all user learning data into a structured portfolio suitable for
    export, sharing, or resume inclusion. Includes:
    - Skills radar (per-domain mastery percentages)
    - Achievement highlights
    - Learning timeline (first/last activity, milestones)
    - Knowledge graph stats
    - Strengths and growth areas
    """
    from routers.analytics_utils import load_seed_metadata

    progress = get_all_progress()
    history = get_history(limit=5000)
    streak_data = get_streak()

    concept_domain_map, concept_info, domain_map = load_seed_metadata()

    # ── Per-domain mastery ──
    domain_mastered: dict[str, int] = {}
    domain_total: dict[str, int] = {}
    domain_scores: dict[str, list[int]] = {}

    for cid in concept_info:
        did = concept_domain_map.get(cid, "")
        if did:
            domain_total[did] = domain_total.get(did, 0) + 1

    for p in progress:
        cid = p["concept_id"]
        did = concept_domain_map.get(cid, "")
        if not did:
            continue
        if p.get("status") == "mastered":
            domain_mastered[did] = domain_mastered.get(did, 0) + 1
        score = p.get("mastery_score") or p.get("best_score", 0)
        if score:
            domain_scores.setdefault(did, []).append(score)

    # Build skills radar
    skills_radar = []
    for did, total in sorted(domain_total.items(), key=lambda x: -x[1]):
        mastered = domain_mastered.get(did, 0)
        scores = domain_scores.get(did, [])
        avg_score = round(sum(scores) / len(scores), 1) if scores else 0
        pct = round(mastered / max(1, total) * 100, 1)
        if mastered > 0 or scores:
            skills_radar.append({
                "domain_id": did,
                "domain_name": domain_map.get(did, {}).get("name", did),
                "icon": domain_map.get(did, {}).get("icon", ""),
                "mastered": mastered,
                "total": total,
                "mastery_pct": pct,
                "avg_score": avg_score,
            })
    skills_radar.sort(key=lambda x: x["mastery_pct"], reverse=True)

    # ── Overall stats ──
    total_mastered = sum(domain_mastered.values())
    total_concepts = sum(domain_total.values())
    domains_started = len([d for d in domain_mastered if domain_mastered[d] > 0])
    all_scores = [s for ss in domain_scores.values() for s in ss]
    overall_avg = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0

    # ── Timeline ──
    timestamps = [h.get("timestamp", 0) for h in history if h.get("timestamp", 0) > 0]
    first_activity = min(timestamps) if timestamps else 0
    last_activity = max(timestamps) if timestamps else 0
    total_days = max(1, int((last_activity - first_activity) / 86400)) if timestamps else 0

    # ── Strengths & Growth ──
    strengths = [s for s in skills_radar if s["mastery_pct"] >= 50][:5]
    growth_areas = [s for s in skills_radar if 0 < s["mastery_pct"] < 30][:5]

    # ── Achievement highlights ──
    milestones_hit = []
    for did, mastered in domain_mastered.items():
        total = domain_total.get(did, 0)
        if total > 0:
            pct = mastered / total * 100
            dname = domain_map.get(did, {}).get("name", did)
            if pct >= 100:
                milestones_hit.append({"domain": dname, "badge": "🌟", "label": "100% 完成"})
            elif pct >= 75:
                milestones_hit.append({"domain": dname, "badge": "⭐", "label": f"{round(pct)}% 掌握"})

    cur_streak = streak_data.get("current", 0) if isinstance(streak_data, dict) else 0
    longest = streak_data.get("longest", 0) if isinstance(streak_data, dict) else 0

    return {
        "portfolio": {
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "overview": {
                "total_mastered": total_mastered,
                "total_concepts": total_concepts,
                "mastery_pct": round(total_mastered / max(1, total_concepts) * 100, 1),
                "domains_explored": domains_started,
                "total_domains": len(domain_total),
                "avg_score": overall_avg,
                "current_streak": cur_streak,
                "longest_streak": longest,
                "learning_days": total_days,
            },
            "skills_radar": skills_radar,
            "strengths": [{"domain": s["domain_name"], "mastery_pct": s["mastery_pct"]} for s in strengths],
            "growth_areas": [{"domain": g["domain_name"], "mastery_pct": g["mastery_pct"]} for g in growth_areas],
            "milestones": milestones_hit,
            "timeline": {
                "first_activity": first_activity,
                "last_activity": last_activity,
                "total_days": total_days,
                "total_sessions": len(history),
            },
        },
    }

