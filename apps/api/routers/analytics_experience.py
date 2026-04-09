"""Analytics Experience API — V2.5 session/mastery/time analytics + V3.7 profile + V3.8 journey/heatmap."""

import math
import time

from fastapi import APIRouter, Query
from utils.logger import get_logger

from db.sqlite_client import get_all_progress, get_history, get_streak

logger = get_logger(__name__)

router = APIRouter()


# ── V2.5: Session History Timeline ───────────────────────


@router.get("/analytics/session-history")
async def session_history(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    action_filter: str = Query("all", description="Filter: all | assessment | start | mastered"),
    concept_filter: str = Query("", description="Filter by concept_id substring"),
    days: int = Query(90, ge=1, le=365, description="Limit to last N days"),
):
    """Paginated learning event timeline with filtering.

    Returns a chronological list of learning events (assessments, starts, mastery)
    for the user, supporting pagination and multiple filters.
    """
    all_history = get_history(limit=10000)
    now = time.time()
    cutoff = now - (days * 86400)

    # Apply filters
    filtered = []
    for entry in all_history:
        ts = entry.get("timestamp", 0)
        if ts < cutoff:
            continue

        if concept_filter and concept_filter.lower() not in entry.get("concept_id", "").lower():
            continue

        # Derive action from entry data
        mastered = entry.get("mastered", 0)
        score = entry.get("score", 0)
        if mastered:
            action = "mastered"
        elif score > 0:
            action = "assessment"
        else:
            action = "start"

        if action_filter != "all" and action != action_filter:
            continue

        filtered.append({
            "id": entry.get("id", 0),
            "concept_id": entry.get("concept_id", ""),
            "concept_name": entry.get("concept_name", ""),
            "score": round(score, 1),
            "mastered": bool(mastered),
            "action": action,
            "timestamp": ts,
            "date": time.strftime("%Y-%m-%d", time.localtime(ts)),
            "time": time.strftime("%H:%M", time.localtime(ts)),
        })

    # Pagination
    total = len(filtered)
    total_pages = max(1, math.ceil(total / per_page))
    start = (page - 1) * per_page
    end = start + per_page
    page_items = filtered[start:end]

    return {
        "items": page_items,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        },
        "filters": {
            "action": action_filter,
            "concept": concept_filter,
            "days": days,
        },
    }


# ── V2.5: Mastery Timeline per Concept ──────────────────


@router.get("/analytics/mastery-timeline/{concept_id}")
async def mastery_timeline(concept_id: str):
    """Return the score progression over time for a specific concept.

    Shows how the user's understanding evolved across sessions —
    useful for visualizing learning curves.
    """
    all_history = get_history(limit=10000)

    # Filter entries for this concept
    timeline = []
    for entry in all_history:
        if entry.get("concept_id") != concept_id:
            continue
        score = entry.get("score", 0)
        ts = entry.get("timestamp", 0)
        mastered = entry.get("mastered", 0)
        timeline.append({
            "score": round(score, 1),
            "mastered": bool(mastered),
            "timestamp": ts,
            "date": time.strftime("%Y-%m-%d", time.localtime(ts)),
            "time": time.strftime("%H:%M", time.localtime(ts)),
        })

    # Reverse to chronological order (oldest first)
    timeline.reverse()

    # Get current progress
    progress_list = get_all_progress()
    current = None
    for p in progress_list:
        if p.get("concept_id") == concept_id:
            current = {
                "status": p.get("status", "not_started"),
                "mastery_score": round(p.get("mastery_score", 0), 1),
                "sessions": p.get("sessions", 0),
            }
            break

    # Compute delta if multiple entries
    improvement = 0.0
    if len(timeline) >= 2:
        improvement = round(timeline[-1]["score"] - timeline[0]["score"], 1)

    return {
        "concept_id": concept_id,
        "data_points": timeline,
        "total_sessions": len(timeline),
        "current": current or {"status": "not_started", "mastery_score": 0, "sessions": 0},
        "improvement": improvement,
        "first_seen": timeline[0]["date"] if timeline else None,
        "last_seen": timeline[-1]["date"] if timeline else None,
    }


# ── V2.5: Study Time Report ─────────────────────────────


@router.get("/analytics/study-time-report")
async def study_time_report(days: int = Query(30, ge=1, le=365)):
    """Daily and weekly study time breakdown with productivity metrics.

    Estimates study time from inter-event gaps (events within 30min = same session).
    Reports daily totals, weekly averages, and productivity trends.
    """
    all_history = get_history(limit=10000)
    now = time.time()
    cutoff = now - (days * 86400)

    # Collect timestamps in chronological order
    timestamps = []
    for entry in all_history:
        ts = entry.get("timestamp", 0)
        if ts >= cutoff:
            timestamps.append(ts)
    timestamps.sort()

    # Estimate sessions: events within 30min gap = same session
    SESSION_GAP = 30 * 60  # 30 minutes
    MIN_SESSION = 60  # minimum 1 minute per session start
    daily_minutes: dict[str, float] = {}
    concepts_per_day: dict[str, set] = {}

    if timestamps:
        session_start = timestamps[0]
        prev_ts = timestamps[0]

        for ts in timestamps[1:]:
            gap = ts - prev_ts
            if gap > SESSION_GAP:
                # End previous session
                session_duration = max(prev_ts - session_start, MIN_SESSION)
                day = time.strftime("%Y-%m-%d", time.localtime(session_start))
                daily_minutes[day] = daily_minutes.get(day, 0) + session_duration / 60
                session_start = ts
            prev_ts = ts

        # Close last session
        session_duration = max(prev_ts - session_start, MIN_SESSION)
        day = time.strftime("%Y-%m-%d", time.localtime(session_start))
        daily_minutes[day] = daily_minutes.get(day, 0) + session_duration / 60

    # Track concepts per day
    for entry in all_history:
        ts = entry.get("timestamp", 0)
        if ts >= cutoff:
            day = time.strftime("%Y-%m-%d", time.localtime(ts))
            if day not in concepts_per_day:
                concepts_per_day[day] = set()
            concepts_per_day[day].add(entry.get("concept_id", ""))

    # Build daily report with zero-fill
    daily_report = []
    for i in range(days):
        day_ts = now - (i * 86400)
        day = time.strftime("%Y-%m-%d", time.localtime(day_ts))
        minutes = round(daily_minutes.get(day, 0), 1)
        concepts = len(concepts_per_day.get(day, set()))
        daily_report.append({
            "date": day,
            "minutes": minutes,
            "concepts_touched": concepts,
        })
    daily_report.reverse()

    # Weekly aggregation
    total_minutes = sum(d["minutes"] for d in daily_report)
    active_days = sum(1 for d in daily_report if d["minutes"] > 0)
    weeks = max(1, days / 7)

    # Productivity: minutes per concept touched
    total_concepts_touched = sum(d["concepts_touched"] for d in daily_report)
    productivity = round(total_minutes / total_concepts_touched, 1) if total_concepts_touched > 0 else 0

    return {
        "period_days": days,
        "daily": daily_report,
        "summary": {
            "total_minutes": round(total_minutes, 1),
            "total_hours": round(total_minutes / 60, 1),
            "active_days": active_days,
            "avg_daily_minutes": round(total_minutes / max(active_days, 1), 1),
            "avg_weekly_minutes": round(total_minutes / weeks, 1),
            "total_concepts_touched": total_concepts_touched,
            "minutes_per_concept": productivity,
        },
    }


# ── V2.5: Streak Insights & Consistency Analysis ────────


@router.get("/analytics/streak-insights")
async def streak_insights():
    """Advanced streak analysis: consistency score, best/worst periods, and habit formation.

    Helps users understand their learning consistency patterns
    and provides actionable insights for habit building.
    """
    history = get_history(limit=10000)
    streak_data = get_streak()
    now = time.time()

    # Collect active dates (last 90 days)
    active_dates: set[str] = set()
    for entry in history:
        ts = entry.get("timestamp", 0)
        if now - ts < 90 * 86400:
            active_dates.add(time.strftime("%Y-%m-%d", time.localtime(ts)))

    # Build 90-day activity array
    days_90 = []
    for i in range(90):
        day_ts = now - (i * 86400)
        day = time.strftime("%Y-%m-%d", time.localtime(day_ts))
        days_90.append({"date": day, "active": day in active_dates})
    days_90.reverse()

    # Find all streaks (consecutive active days)
    streaks = []
    current_len = 0
    streak_start = ""
    for d in days_90:
        if d["active"]:
            if current_len == 0:
                streak_start = d["date"]
            current_len += 1
        else:
            if current_len > 0:
                streaks.append({"start": streak_start, "length": current_len})
            current_len = 0
    if current_len > 0:
        streaks.append({"start": streak_start, "length": current_len})

    # Best streak
    best_streak = max(streaks, key=lambda s: s["length"]) if streaks else {"start": "", "length": 0}

    # Weekly consistency (how many weeks had >= 3 active days)
    weekly_active: dict[int, int] = {}  # week_num -> active_days
    for i, d in enumerate(days_90):
        week = i // 7
        if d["active"]:
            weekly_active[week] = weekly_active.get(week, 0) + 1
    total_weeks = max(1, 90 // 7)
    consistent_weeks = sum(1 for v in weekly_active.values() if v >= 3)

    # Activity rate
    total_active = len(active_dates)
    activity_rate = round(total_active / 90 * 100, 1)

    # Weekday distribution
    weekday_counts = [0] * 7  # Mon=0
    for entry in history:
        ts = entry.get("timestamp", 0)
        if now - ts < 90 * 86400:
            lt = time.localtime(ts)
            weekday_counts[lt.tm_wday] += 1
    weekday_names = ["\u5468\u4e00", "\u5468\u4e8c", "\u5468\u4e09", "\u5468\u56db", "\u5468\u4e94", "\u5468\u516d", "\u5468\u65e5"]
    best_day_idx = weekday_counts.index(max(weekday_counts)) if any(weekday_counts) else 0

    # Habit formation score (0-100)
    # Based on: current streak weight + consistency + recent activity
    recent_7 = sum(1 for d in days_90[-7:] if d["active"])
    recent_30 = sum(1 for d in days_90[-30:] if d["active"])
    current_streak = streak_data.get("current", 0) if isinstance(streak_data, dict) else 0

    habit_score = min(100, round(
        (current_streak / 30 * 30) +  # streak contribution (max 30)
        (recent_7 / 7 * 25) +          # recent week (max 25)
        (recent_30 / 30 * 25) +         # recent month (max 25)
        (consistent_weeks / total_weeks * 20)  # weekly consistency (max 20)
    ))

    return {
        "current_streak": current_streak,
        "longest_streak": streak_data.get("longest", 0) if isinstance(streak_data, dict) else 0,
        "best_streak_90d": best_streak,
        "total_active_days_90d": total_active,
        "activity_rate_90d": activity_rate,
        "habit_score": habit_score,
        "weekly_consistency": {
            "consistent_weeks": consistent_weeks,
            "total_weeks": total_weeks,
            "rate": round(consistent_weeks / total_weeks * 100, 1),
        },
        "recent": {
            "last_7_days": recent_7,
            "last_30_days": recent_30,
        },
        "best_day": {
            "name": weekday_names[best_day_idx],
            "activity_count": weekday_counts[best_day_idx],
        },
        "weekday_distribution": dict(zip(weekday_names, weekday_counts)),
        "all_streaks": sorted(streaks, key=lambda s: s["length"], reverse=True)[:5],
    }


# ── V3.1: Session Summary (current session aggregate) ────


@router.get("/analytics/session-summary")
async def session_summary(
    hours: int = Query(24, ge=1, le=168, description="Lookback window in hours"),
):
    """Aggregate summary of recent learning activity (session-style snapshot).

    Returns a compact snapshot of the user's recent learning session:
    - Total concepts touched, assessments completed, new masteries
    - Domain breakdown of activity
    - Best score and weakest concept in the window
    - Active minutes estimate

    Useful for a "session recap" or "today's learning" dashboard widget.
    """
    from routers.analytics_utils import load_seed_metadata

    now = time.time()
    cutoff = now - hours * 3600

    history = get_history(limit=10000)
    progress = get_all_progress()
    streak = get_streak()

    # Filter to recent window
    recent = [h for h in history if h.get("timestamp", 0) >= cutoff]

    if not recent:
        return {
            "hours": hours,
            "total_events": 0,
            "concepts_touched": 0,
            "assessments": 0,
            "new_masteries": 0,
            "best_score": None,
            "weakest": None,
            "domain_breakdown": [],
            "active_minutes": 0,
            "current_streak": streak.get("current", 0) if isinstance(streak, dict) else 0,
        }

    concept_domain_map, concept_info, domain_map = load_seed_metadata()

    # Aggregate
    concepts_seen: set[str] = set()
    assessments = 0
    new_masteries = 0
    best_score = -1.0
    best_concept = ""
    worst_score = 101.0
    worst_concept = ""
    domain_counts: dict[str, int] = {}
    timestamps: list[float] = []

    for h in recent:
        cid = h.get("concept_id", "")
        concepts_seen.add(cid)
        score = float(h.get("score", 0))
        timestamps.append(h.get("timestamp", 0))

        action = h.get("action", "assessment")
        if action in ("assessment", "assess"):
            assessments += 1
        if h.get("mastered"):
            new_masteries += 1
        if score > best_score:
            best_score = score
            best_concept = cid
        if score < worst_score and score > 0:
            worst_score = score
            worst_concept = cid

        did = concept_domain_map.get(cid, "unknown")
        domain_counts[did] = domain_counts.get(did, 0) + 1

    # Estimate active minutes (gaps > 10min = idle)
    timestamps.sort()
    active_sec = 0.0
    for i in range(1, len(timestamps)):
        gap = timestamps[i] - timestamps[i - 1]
        if gap < 600:  # 10 minutes idle threshold
            active_sec += gap

    domain_breakdown = []
    for did, count in sorted(domain_counts.items(), key=lambda x: -x[1]):
        dinfo = domain_map.get(did, {})
        domain_breakdown.append({
            "domain_id": did,
            "domain_name": dinfo.get("name", did),
            "events": count,
        })

    return {
        "hours": hours,
        "total_events": len(recent),
        "concepts_touched": len(concepts_seen),
        "assessments": assessments,
        "new_masteries": new_masteries,
        "best_score": {
            "score": round(best_score, 1),
            "concept_id": best_concept,
            "concept_name": concept_info.get(best_concept, {}).get("name", best_concept),
        } if best_score >= 0 else None,
        "weakest": {
            "score": round(worst_score, 1),
            "concept_id": worst_concept,
            "concept_name": concept_info.get(worst_concept, {}).get("name", worst_concept),
        } if worst_score <= 100 else None,
        "domain_breakdown": domain_breakdown,
        "active_minutes": round(active_sec / 60, 1),
        "current_streak": streak.get("current", 0) if isinstance(streak, dict) else 0,
    }


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
    """Full learning journey for a single concept — every assessment, score change, and milestone.

    Returns a rich timeline including:
    - Chronological assessment events with scores and deltas
    - Current status and mastery info
    - Journey stats (total attempts, time span, improvement rate)
    - Domain context (which domain, difficulty, subdomain)
    """
    from routers.analytics_utils import load_seed_metadata

    history = get_history(10000)
    progress = get_all_progress()

    concept_domain_map, concept_info, domain_map = load_seed_metadata()

    # Filter history for this concept
    events = [h for h in history if h.get("concept_id") == concept_id]
    events.sort(key=lambda e: e.get("timestamp", 0))

    # Current progress
    progress_map = {p["concept_id"]: p for p in progress}
    current = progress_map.get(concept_id, {})
    info = concept_info.get(concept_id, {})
    did = concept_domain_map.get(concept_id, "")

    if not events and not current:
        return {
            "concept_id": concept_id,
            "found": False,
            "events": [],
            "stats": {},
        }

    # Build timeline
    timeline = []
    prev_score = 0
    best_score = 0
    mastery_step = None

    for i, ev in enumerate(events):
        score = ev.get("score", 0)
        delta = score - prev_score if i > 0 else 0
        is_mastered = ev.get("mastered", False)

        entry = {
            "step": i + 1,
            "score": score,
            "delta": round(delta, 1),
            "mastered": is_mastered,
            "timestamp": ev.get("timestamp", 0),
            "concept_name": ev.get("concept_name", concept_id),
        }
        timeline.append(entry)

        if score > best_score:
            best_score = score
        if is_mastered and mastery_step is None:
            mastery_step = i + 1
        prev_score = score

    # Calculate stats
    scores = [e["score"] for e in timeline]
    time_span_days = 0
    if len(events) >= 2:
        first_ts = events[0].get("timestamp", 0)
        last_ts = events[-1].get("timestamp", 0)
        time_span_days = round((last_ts - first_ts) / 86400, 1) if last_ts > first_ts else 0

    improvement = scores[-1] - scores[0] if len(scores) >= 2 else 0

    return {
        "concept_id": concept_id,
        "found": True,
        "concept_name": info.get("name", current.get("concept_name", concept_id)),
        "domain_id": did,
        "domain_name": domain_map.get(did, {}).get("name", did),
        "difficulty": info.get("difficulty", current.get("difficulty", 5)),
        "subdomain_id": info.get("subdomain_id", ""),
        "current_status": current.get("status", "not_started"),
        "current_score": current.get("mastery_score", 0),
        "events": timeline,
        "stats": {
            "total_attempts": len(timeline),
            "best_score": best_score,
            "first_score": scores[0] if scores else 0,
            "latest_score": scores[-1] if scores else 0,
            "improvement": round(improvement, 1),
            "mastered_at_step": mastery_step,
            "time_span_days": time_span_days,
            "avg_score": round(sum(scores) / len(scores), 1) if scores else 0,
        },
    }


# ── V3.8: Learning Heatmap ───────────────────────────────

@router.get("/analytics/learning-heatmap/{domain_id}")
async def learning_heatmap(domain_id: str):
    """Domain learning activity heatmap — concept-level engagement intensity.

    Groups concepts by subdomain and shows per-concept activity intensity
    (sessions, score, status) as a 2D heatmap data structure.

    Returns:
    - Per-subdomain rows with concept cells
    - Each cell: concept_id, name, sessions, score, status, intensity (0-1)
    - Domain-level summary stats
    """
    import json as _json, os, sys

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

    # Group by subdomain
    from collections import defaultdict
    subdomain_groups: dict[str, list[dict]] = defaultdict(list)

    max_sessions = 1  # For normalization
    for c in concepts:
        cid = c["id"]
        p = progress_map.get(cid, {})
        sessions = p.get("sessions", 0)
        if sessions > max_sessions:
            max_sessions = sessions

        cell = {
            "concept_id": cid,
            "name": c.get("name", cid),
            "difficulty": c.get("difficulty", 5),
            "status": p.get("status", "not_started"),
            "sessions": sessions,
            "score": p.get("mastery_score", 0),
        }
        sid = c.get("subdomain_id", "other")
        subdomain_groups[sid].append(cell)

    # Add intensity (0-1 normalized)
    subdomains = []
    total_active = 0
    total_mastered = 0
    total_concepts = len(concepts)

    for sid in sorted(subdomain_groups.keys()):
        cells = subdomain_groups[sid]
        for cell in cells:
            # Intensity: composite of sessions + score
            session_intensity = min(1.0, cell["sessions"] / max(1, max_sessions))
            score_intensity = cell["score"] / 100.0
            cell["intensity"] = round(session_intensity * 0.4 + score_intensity * 0.6, 2)
            if cell["sessions"] > 0:
                total_active += 1
            if cell["status"] == "mastered":
                total_mastered += 1

        # Sort by difficulty within subdomain
        cells.sort(key=lambda x: x["difficulty"])

        avg_intensity = sum(c["intensity"] for c in cells) / len(cells) if cells else 0
        subdomains.append({
            "subdomain_id": sid,
            "concepts": cells,
            "count": len(cells),
            "avg_intensity": round(avg_intensity, 2),
            "mastered_count": sum(1 for c in cells if c["status"] == "mastered"),
        })

    return {
        "domain_id": domain_id,
        "subdomains": subdomains,
        "summary": {
            "total_concepts": total_concepts,
            "active_concepts": total_active,
            "mastered_concepts": total_mastered,
            "coverage_pct": round(total_active / max(1, total_concepts) * 100, 1),
            "mastery_pct": round(total_mastered / max(1, total_concepts) * 100, 1),
        },
    }
