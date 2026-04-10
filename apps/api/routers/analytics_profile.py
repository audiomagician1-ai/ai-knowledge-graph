"""Analytics Profile API — Unified learning profile + concept journey + learning heatmap.

Extracted from analytics_experience.py (V3.9 code health) to keep router files under 800 lines.

Provides:
- Unified learning profile (V3.7)
- Concept journey timeline (V3.8)
- Domain learning heatmap (V3.8)
"""

import time

from fastapi import APIRouter
from utils.logger import get_logger

from db.sqlite_client import get_all_progress, get_history, get_streak

logger = get_logger(__name__)

router = APIRouter()


# ── V3.7: Unified Learning Profile ──────────────────────

@router.get("/analytics/learning-profile")
async def learning_profile():
    """Comprehensive user learning profile — single API call replacing 5+ separate calls.

    Aggregates: progress overview, streak, recent activity, domain breakdown,
    strengths/weaknesses, and current goals into one payload.
    """
    from routers.analytics_utils import load_seed_metadata
    from db.sqlite_client import get_all_bkt_states, get_due_concepts
    from collections import defaultdict

    all_progress = get_all_progress()
    history = get_history(500)
    streak_data = get_streak()
    concept_domain_map, concept_info, domain_map = load_seed_metadata()
    now = time.time()

    # ── Progress Overview ──
    mastered = [p for p in all_progress if p["status"] == "mastered"]
    learning = [p for p in all_progress if p["status"] == "learning"]
    total_concepts = len(concept_info)
    mastered_count = len(mastered)
    learning_count = len(learning)

    # ── Streak ──
    current_streak = streak_data.get("current", 0) if isinstance(streak_data, dict) else 0
    longest_streak = streak_data.get("longest", 0) if isinstance(streak_data, dict) else 0

    # ── Recent Activity (7 days) ──
    week_ago = now - 7 * 86400
    recent = [h for h in history if h.get("timestamp", 0) >= week_ago]
    recent_mastered = sum(1 for h in recent if h.get("mastered"))
    recent_events = len(recent)
    recent_avg_score = round(
        sum(h.get("score", 0) for h in recent) / max(1, recent_events), 1
    ) if recent_events else 0

    # ── Domain Breakdown (active domains only) ──
    domain_stats: dict[str, dict] = defaultdict(lambda: {"mastered": 0, "learning": 0, "total": 0})
    for cid, did in concept_domain_map.items():
        domain_stats[did]["total"] += 1
    for p in all_progress:
        did = concept_domain_map.get(p["concept_id"])
        if did:
            domain_stats[did][p["status"]] = domain_stats[did].get(p["status"], 0) + 1

    active_domains = []
    for did, ds in domain_stats.items():
        if ds.get("mastered", 0) > 0 or ds.get("learning", 0) > 0:
            meta = domain_map.get(did, {})
            total = ds["total"]
            m = ds.get("mastered", 0)
            active_domains.append({
                "domain_id": did,
                "name": meta.get("name", did),
                "mastered": m,
                "learning": ds.get("learning", 0),
                "total": total,
                "progress_pct": round(m / max(1, total) * 100, 1),
            })
    active_domains.sort(key=lambda d: d["mastered"], reverse=True)

    # ── Strengths & Weaknesses (from BKT) ──
    bkt_states = get_all_bkt_states()
    strengths = []
    weaknesses = []
    for bkt in sorted(bkt_states, key=lambda b: b["bkt_mastery"], reverse=True):
        info = concept_info.get(bkt["concept_id"], {})
        entry = {
            "concept_id": bkt["concept_id"],
            "name": info.get("name", bkt["concept_id"]),
            "p_mastery": round(bkt["bkt_mastery"], 3),
            "observations": bkt["bkt_observations"],
        }
        if bkt["bkt_mastery"] >= 0.8 and len(strengths) < 5:
            strengths.append(entry)
        elif bkt["bkt_mastery"] < 0.4 and bkt["bkt_observations"] >= 2 and len(weaknesses) < 5:
            weaknesses.append(entry)

    # ── FSRS Review Status ──
    due_items = get_due_concepts(before=now, limit=100)
    due_count = len(due_items)
    overdue_count = sum(1 for d in due_items if (now - d["fsrs_due"]) > 86400)

    # ── Level Estimate ──
    mastered_diffs = [concept_info.get(p["concept_id"], {}).get("difficulty", 3)
                      for p in mastered if p["concept_id"] in concept_info]
    avg_difficulty = round(sum(mastered_diffs) / max(1, len(mastered_diffs)), 1) if mastered_diffs else 0

    return {
        "overview": {
            "total_concepts": total_concepts,
            "mastered": mastered_count,
            "learning": learning_count,
            "not_started": total_concepts - mastered_count - learning_count,
            "completion_pct": round(mastered_count / max(1, total_concepts) * 100, 1),
            "avg_mastered_difficulty": avg_difficulty,
        },
        "streak": {
            "current": current_streak,
            "longest": longest_streak,
        },
        "recent_7d": {
            "events": recent_events,
            "mastered": recent_mastered,
            "avg_score": recent_avg_score,
        },
        "domains": active_domains[:12],
        "strengths": strengths,
        "weaknesses": weaknesses,
        "review_status": {
            "due_count": due_count,
            "overdue_count": overdue_count,
        },
    }


# ── V3.8: Concept Journey ────────────────────────────────

@router.get("/analytics/concept-journey/{concept_id}")
async def concept_journey(concept_id: str):
    """Full learning journey for a single concept — every assessment, score change, and milestone."""
    from routers.analytics_utils import load_seed_metadata

    history = get_history(10000)
    progress = get_all_progress()
    concept_domain_map, concept_info, domain_map = load_seed_metadata()

    events = [h for h in history if h.get("concept_id") == concept_id]
    events.sort(key=lambda e: e.get("timestamp", 0))

    progress_map = {p["concept_id"]: p for p in progress}
    current = progress_map.get(concept_id, {})
    info = concept_info.get(concept_id, {})
    did = concept_domain_map.get(concept_id, "")

    if not events and not current:
        return {"concept_id": concept_id, "found": False, "events": [], "stats": {}}

    timeline = []
    prev_score = 0
    best_score = 0
    mastery_step = None

    for i, ev in enumerate(events):
        score = ev.get("score", 0)
        delta = score - prev_score if i > 0 else 0
        is_mastered = ev.get("mastered", False)
        timeline.append({
            "step": i + 1, "score": score, "delta": round(delta, 1),
            "mastered": is_mastered, "timestamp": ev.get("timestamp", 0),
            "concept_name": ev.get("concept_name", concept_id),
        })
        if score > best_score:
            best_score = score
        if is_mastered and mastery_step is None:
            mastery_step = i + 1
        prev_score = score

    scores = [e["score"] for e in timeline]
    time_span_days = 0
    if len(events) >= 2:
        first_ts, last_ts = events[0].get("timestamp", 0), events[-1].get("timestamp", 0)
        time_span_days = round((last_ts - first_ts) / 86400, 1) if last_ts > first_ts else 0
    improvement = scores[-1] - scores[0] if len(scores) >= 2 else 0

    return {
        "concept_id": concept_id, "found": True,
        "concept_name": info.get("name", current.get("concept_name", concept_id)),
        "domain_id": did, "domain_name": domain_map.get(did, {}).get("name", did),
        "difficulty": info.get("difficulty", current.get("difficulty", 5)),
        "subdomain_id": info.get("subdomain_id", ""),
        "current_status": current.get("status", "not_started"),
        "current_score": current.get("mastery_score", 0),
        "events": timeline,
        "stats": {
            "total_attempts": len(timeline), "best_score": best_score,
            "first_score": scores[0] if scores else 0,
            "latest_score": scores[-1] if scores else 0,
            "improvement": round(improvement, 1), "mastered_at_step": mastery_step,
            "time_span_days": time_span_days,
            "avg_score": round(sum(scores) / len(scores), 1) if scores else 0,
        },
    }


# ── V3.8: Learning Heatmap ───────────────────────────────

@router.get("/analytics/learning-heatmap/{domain_id}")
async def learning_heatmap(domain_id: str):
    """Domain learning activity heatmap — concept-level engagement intensity."""
    import json as _json, os, sys

    from routers.analytics_utils import validate_domain_id
    if not validate_domain_id(domain_id):
        return {"domain_id": domain_id, "error": "Invalid domain_id", "subdomains": []}

    progress = get_all_progress()
    progress_map = {p["concept_id"]: p for p in progress}

    if getattr(sys, "frozen", False):
        data_root = os.path.join(sys._MEIPASS, "seed_data")
    else:
        data_root = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "data", "seed",
        )

    seed_path = os.path.join(data_root, domain_id, "seed_graph.json")
    if not os.path.isfile(seed_path):
        return {"domain_id": domain_id, "error": "Domain not found", "subdomains": []}

    with open(seed_path, "r", encoding="utf-8") as f:
        seed = _json.load(f)

    concepts = seed.get("concepts", [])
    if not concepts:
        return {"domain_id": domain_id, "subdomains": [], "summary": {}}

    from collections import defaultdict
    subdomain_groups: dict[str, list[dict]] = defaultdict(list)
    max_sessions = 1
    for c in concepts:
        cid = c["id"]
        p = progress_map.get(cid, {})
        sessions = p.get("sessions", 0)
        if sessions > max_sessions:
            max_sessions = sessions
        subdomain_groups[c.get("subdomain_id", "other")].append({
            "concept_id": cid, "name": c.get("name", cid),
            "difficulty": c.get("difficulty", 5), "status": p.get("status", "not_started"),
            "sessions": sessions, "score": p.get("mastery_score", 0),
        })

    subdomains = []
    total_active = total_mastered = 0
    total_concepts = len(concepts)

    for sid in sorted(subdomain_groups.keys()):
        cells = subdomain_groups[sid]
        for cell in cells:
            si = min(1.0, cell["sessions"] / max(1, max_sessions))
            cell["intensity"] = round(si * 0.4 + cell["score"] / 100.0 * 0.6, 2)
            if cell["sessions"] > 0:
                total_active += 1
            if cell["status"] == "mastered":
                total_mastered += 1
        cells.sort(key=lambda x: x["difficulty"])
        avg_i = sum(c["intensity"] for c in cells) / len(cells) if cells else 0
        subdomains.append({
            "subdomain_id": sid, "concepts": cells, "count": len(cells),
            "avg_intensity": round(avg_i, 2),
            "mastered_count": sum(1 for c in cells if c["status"] == "mastered"),
        })

    return {
        "domain_id": domain_id, "subdomains": subdomains,
        "summary": {
            "total_concepts": total_concepts, "active_concepts": total_active,
            "mastered_concepts": total_mastered,
            "coverage_pct": round(total_active / max(1, total_concepts) * 100, 1),
            "mastery_pct": round(total_mastered / max(1, total_concepts) * 100, 1),
        },
    }


# ── V4.5: Daily Summary ───────────────────────


@router.get("/analytics/daily-summary")
async def daily_summary():
    """Consolidated 'What should I do today?' single-call summary.

    Aggregates: streak status, FSRS due count, today's activity,
    recommended next action, motivation message — all in one request.
    """
    from datetime import datetime

    from routers.analytics_utils import load_seed_metadata

    progress = get_all_progress()
    history = get_history(limit=500)
    streak = get_streak()
    concept_domain_map, concept_info, _ = load_seed_metadata()

    today = datetime.now().date().isoformat()

    # ── Streak ──
    current_streak = streak.get("current", 0) if isinstance(streak, dict) else 0
    longest_streak = streak.get("longest", 0) if isinstance(streak, dict) else 0

    # ── Today's activity ──
    today_events = 0
    today_mastered = 0
    today_domains: set = set()
    for h in history:
        ts = h.get("timestamp", "")
        ts_date = ""
        if isinstance(ts, (int, float)):
            try:
                ts_date = datetime.fromtimestamp(ts).date().isoformat()
            except (OSError, ValueError, OverflowError):
                pass
        else:
            ts_str = str(ts)
            ts_date = ts_str[:10] if len(ts_str) >= 10 else ""
        if ts_date == today:
            today_events += 1
            if h.get("action") == "mastered" or (h.get("action") == "assessment" and h.get("score", 0) >= 75):
                today_mastered += 1
            did = concept_domain_map.get(h.get("concept_id", ""), "")
            if did:
                today_domains.add(did)

    # ── FSRS Due ──
    due_count = 0
    overdue_count = 0
    for p in progress:
        nr = p.get("next_review")
        if not nr:
            continue
        try:
            nr_date = datetime.fromisoformat(str(nr)[:10]).date()
            today_date = datetime.now().date()
            if nr_date <= today_date:
                due_count += 1
                if nr_date < today_date:
                    overdue_count += 1
        except (ValueError, TypeError):
            continue

    # ── Progress ──
    total_mastered = sum(1 for p in progress if p.get("status") == "mastered")
    total_learning = sum(1 for p in progress if p.get("status") == "learning")

    # ── Recommended action ──
    if due_count > 0:
        action = {"type": "review", "label": f"复习 {due_count} 个到期概念", "priority": "high", "route": "/review"}
    elif total_learning > 0:
        lc = next((p for p in progress if p.get("status") == "learning"), None)
        cid = lc["concept_id"] if lc else ""
        did = concept_domain_map.get(cid, "")
        cname = concept_info.get(cid, {}).get("name", cid)
        action = {"type": "continue", "label": f"继续学习: {cname}", "priority": "medium",
                  "route": f"/graph?domain={did}&concept={cid}" if did else "/"}
    else:
        action = {"type": "explore", "label": "开始你的学习之旅" if total_mastered == 0 else "探索新领域",
                  "priority": "low", "route": "/"}

    # ── Motivation ──
    if current_streak >= 7:
        motivation = f"🔥 连续学习 {current_streak} 天！坚持住！"
    elif current_streak >= 3:
        motivation = f"🌟 连续 {current_streak} 天，再接再厉！"
    elif today_events > 0:
        motivation = "👍 今天已经开始学习了，继续保持！"
    else:
        motivation = "📚 新的一天，从一个概念开始吧！"

    return {
        "date": today,
        "streak": {"current": current_streak, "longest": longest_streak},
        "today": {"events": today_events, "mastered": today_mastered, "domains_active": len(today_domains)},
        "reviews": {"due": due_count, "overdue": overdue_count},
        "progress": {"total_mastered": total_mastered, "total_learning": total_learning,
                     "total_concepts": len(concept_info)},
        "recommended_action": action,
        "motivation": motivation,
    }