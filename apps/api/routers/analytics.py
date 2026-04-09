"""Analytics API — Learning analytics, content quality insights, and usage statistics.

Provides aggregate views for:
- Concept difficulty distribution (which concepts are hardest)
- Domain mastery heatmap
- Time-based learning trends
- Content quality signals (low-scoring concepts → improvement priority)
- Session history timeline (V2.5)
- Mastery timeline per concept (V2.5)
- Study time report with productivity metrics (V2.5)
"""

import math
import time

from fastapi import APIRouter, Query
from utils.logger import get_logger

from db.sqlite_client import get_all_progress, get_history, get_streak

logger = get_logger(__name__)

router = APIRouter()


@router.get("/analytics/difficulty-map")
async def difficulty_map():
    """Return concept mastery distribution — helps identify hard concepts.
    
    Groups all assessed concepts by their mastery_score into buckets:
    - struggling (0-40): needs content improvement
    - developing (41-60): normal learning
    - proficient (61-75): near mastery
    - mastered (76-100): fully mastered
    """
    progress_list = get_all_progress()  # list[dict]
    
    buckets: dict[str, list] = {
        "struggling": [],
        "developing": [],
        "proficient": [],
        "mastered": [],
    }
    
    for row in progress_list:
        status = row.get("status", "not_started")
        if status not in ("learning", "mastered"):
            continue
        
        score = row.get("mastery_score", 0) or 0
        entry = {
            "concept_id": row.get("concept_id", ""),
            "overall": round(score, 1),
            "status": status,
        }
        
        if score <= 40:
            buckets["struggling"].append(entry)
        elif score <= 60:
            buckets["developing"].append(entry)
        elif score <= 75:
            buckets["proficient"].append(entry)
        else:
            buckets["mastered"].append(entry)
    
    # Sort each bucket by score ascending (worst first)
    for key in buckets:
        buckets[key].sort(key=lambda x: x["overall"])
    
    return {
        "total_assessed": sum(len(v) for v in buckets.values()),
        "distribution": {k: len(v) for k, v in buckets.items()},
        "struggling_concepts": buckets["struggling"][:20],
        "recently_mastered": buckets["mastered"][-10:],
    }


@router.get("/analytics/domain-heatmap")
async def domain_heatmap():
    """Return per-domain mastery statistics for heatmap visualization."""
    progress_list = get_all_progress()
    
    domain_stats: dict[str, dict] = {}
    
    for row in progress_list:
        concept_id = row.get("concept_id", "")
        # Extract domain prefix from concept_id (e.g., "variables" → "unknown")
        # Use a simple heuristic — most concept_ids have no domain prefix
        domain_id = "all"
        
        if domain_id not in domain_stats:
            domain_stats[domain_id] = {
                "total": 0,
                "mastered": 0,
                "learning": 0,
                "not_started": 0,
                "scores": [],
            }
        
        stats = domain_stats[domain_id]
        status = row.get("status", "not_started")
        stats["total"] += 1
        stats[status] = stats.get(status, 0) + 1
        
        mastery = row.get("mastery_score", 0) or 0
        if mastery > 0:
            stats["scores"].append(mastery)
    
    # Compute averages and remove raw scores
    result = {}
    for domain_id, stats in domain_stats.items():
        scores = stats.pop("scores")
        stats["avg_score"] = round(sum(scores) / len(scores), 1) if scores else 0
        stats["mastery_rate"] = round(stats["mastered"] / stats["total"] * 100, 1) if stats["total"] > 0 else 0
        result[domain_id] = stats
    
    return {
        "domains": result,
        "total_domains": len(result),
    }


@router.get("/analytics/learning-velocity")
async def learning_velocity(days: int = 30):
    """Return daily learning activity for the past N days."""
    history = get_history(limit=5000)  # Get plenty of history
    now = time.time()
    cutoff = now - (days * 86400)
    
    # Group by day
    daily: dict[str, dict] = {}
    
    for entry in history:
        ts = entry.get("timestamp", 0)
        if ts < cutoff:
            continue
        
        day = time.strftime("%Y-%m-%d", time.localtime(ts))
        if day not in daily:
            daily[day] = {"assessments": 0, "concepts_started": 0, "mastered": 0}
        
        action = entry.get("action", "")
        if action == "assessment":
            daily[day]["assessments"] += 1
        elif action == "start":
            daily[day]["concepts_started"] += 1
    
    # Fill missing days
    result = []
    for i in range(days):
        day_ts = now - (i * 86400)
        day = time.strftime("%Y-%m-%d", time.localtime(day_ts))
        result.append({
            "date": day,
            **(daily.get(day, {"assessments": 0, "concepts_started": 0, "mastered": 0})),
        })
    
    result.reverse()  # chronological order
    
    streak = get_streak()
    
    return {
        "days": days,
        "daily": result,
        "streak": streak,
        "summary": {
            "total_assessments": sum(d["assessments"] for d in result),
            "total_concepts_started": sum(d["concepts_started"] for d in result),
            "active_days": sum(1 for d in result if d["assessments"] > 0 or d["concepts_started"] > 0),
        },
    }


@router.get("/analytics/content-quality-signals")
async def content_quality_signals():
    """Identify concepts that may need content improvement based on learning data.
    
    Signals:
    - Low average scores after multiple sessions
    - High abandon rate (started but never assessed)
    """
    progress_list = get_all_progress()
    
    signals = []
    
    for row in progress_list:
        concept_id = row.get("concept_id", "")
        mastery = row.get("mastery_score", 0) or 0
        status = row.get("status", "not_started")
        sessions = row.get("sessions", 0) or 0
        
        # Signal 1: Multiple sessions but still low score
        if sessions >= 2 and mastery < 50 and status == "learning":
            signals.append({
                "concept_id": concept_id,
                "signal": "low_score_multiple_attempts",
                "severity": "high",
                "detail": f"Score {mastery:.0f} after {sessions} sessions",
                "overall": round(mastery, 1),
                "sessions": sessions,
            })
        
        # Signal 2: Started but no meaningful progress
        elif status == "learning" and sessions <= 1 and mastery < 20:
            signals.append({
                "concept_id": concept_id,
                "signal": "started_not_assessed",
                "severity": "medium",
                "detail": "Started learning but minimal progress",
                "overall": round(mastery, 1),
                "sessions": sessions,
            })
    
    # Sort by severity then score
    severity_order = {"high": 0, "medium": 1, "low": 2}
    signals.sort(key=lambda s: (severity_order.get(s["severity"], 9), s["overall"]))
    
    return {
        "total_signals": len(signals),
        "high_severity": sum(1 for s in signals if s["severity"] == "high"),
        "medium_severity": sum(1 for s in signals if s["severity"] == "medium"),
        "signals": signals[:50],
    }


@router.get("/analytics/weekly-report")
async def weekly_report():
    """Generate a weekly progress summary comparing this week vs last week.

    Includes:
    - Concepts mastered (this week vs last week)
    - Concepts started
    - Total study sessions
    - Active days
    - Streak data
    - Top domains by activity
    """
    history = get_history(limit=10000)
    progress_list = get_all_progress()
    streak_data = get_streak()
    now = time.time()

    # This week: last 7 days, Last week: 8-14 days ago
    this_week_start = now - (7 * 86400)
    last_week_start = now - (14 * 86400)

    this_week = {"mastered": 0, "started": 0, "assessments": 0, "active_days": set()}
    last_week = {"mastered": 0, "started": 0, "assessments": 0, "active_days": set()}

    for entry in history:
        ts = entry.get("timestamp", 0)
        action = entry.get("action", "")
        day = time.strftime("%Y-%m-%d", time.localtime(ts))

        if ts >= this_week_start:
            bucket = this_week
        elif ts >= last_week_start:
            bucket = last_week
        else:
            continue

        if action == "assessment":
            bucket["assessments"] += 1
        elif action == "start":
            bucket["started"] += 1
        elif action == "mastered":
            bucket["mastered"] += 1
        bucket["active_days"].add(day)

    # Convert sets to counts
    this_week["active_days"] = len(this_week["active_days"])
    last_week["active_days"] = len(last_week["active_days"])

    # Compute deltas (positive = improvement)
    def delta(current, previous):
        if previous == 0:
            return 100 if current > 0 else 0
        return round(((current - previous) / previous) * 100, 1)

    # Overall mastery summary
    total_mastered = sum(1 for p in progress_list if p.get("status") == "mastered")
    total_learning = sum(1 for p in progress_list if p.get("status") == "learning")

    return {
        "period": {
            "this_week": time.strftime("%m/%d", time.localtime(this_week_start)) + " - " + time.strftime("%m/%d", time.localtime(now)),
            "last_week": time.strftime("%m/%d", time.localtime(last_week_start)) + " - " + time.strftime("%m/%d", time.localtime(this_week_start)),
        },
        "this_week": {
            "mastered": this_week["mastered"],
            "started": this_week["started"],
            "assessments": this_week["assessments"],
            "active_days": this_week["active_days"],
        },
        "last_week": {
            "mastered": last_week["mastered"],
            "started": last_week["started"],
            "assessments": last_week["assessments"],
            "active_days": last_week["active_days"],
        },
        "deltas": {
            "mastered_pct": delta(this_week["mastered"], last_week["mastered"]),
            "started_pct": delta(this_week["started"], last_week["started"]),
            "assessments_pct": delta(this_week["assessments"], last_week["assessments"]),
            "active_days_pct": delta(this_week["active_days"], last_week["active_days"]),
        },
        "overall": {
            "total_mastered": total_mastered,
            "total_learning": total_learning,
            "streak_current": streak_data.get("current", 0) if isinstance(streak_data, dict) else 0,
            "streak_longest": streak_data.get("longest", 0) if isinstance(streak_data, dict) else 0,
        },
    }


@router.get("/analytics/study-patterns")
async def study_patterns(days: int = 30):
    """Analyze study patterns — preferred times, session lengths, and consistency.

    Helps users understand their learning habits.
    """
    history = get_history(limit=10000)
    now = time.time()
    cutoff = now - (days * 86400)

    # Hour-of-day distribution
    hour_dist = [0] * 24
    weekday_dist = [0] * 7  # 0=Mon, 6=Sun
    session_gaps = []
    prev_ts = None

    for entry in history:
        ts = entry.get("timestamp", 0)
        if ts < cutoff:
            continue

        lt = time.localtime(ts)
        hour_dist[lt.tm_hour] += 1
        weekday_dist[lt.tm_wday] += 1

        if prev_ts and (ts - prev_ts) < 3600:  # Within 1 hour = same session
            session_gaps.append(ts - prev_ts)
        prev_ts = ts

    # Find peak hours
    peak_hour = hour_dist.index(max(hour_dist)) if any(hour_dist) else 12
    weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    peak_day = weekday_dist.index(max(weekday_dist)) if any(weekday_dist) else 0

    # Avg session gap (proxy for session length)
    avg_gap = round(sum(session_gaps) / len(session_gaps), 1) if session_gaps else 0

    return {
        "period_days": days,
        "hour_distribution": hour_dist,
        "weekday_distribution": dict(zip(weekday_names, weekday_dist)),
        "peak_hour": peak_hour,
        "peak_hour_label": f"{peak_hour}:00-{peak_hour+1}:00",
        "peak_day": weekday_names[peak_day],
        "total_events": sum(hour_dist),
        "avg_inter_action_gap_seconds": avg_gap,
        "consistency_score": round(
            sum(1 for d in weekday_dist if d > 0) / 7 * 100, 1
        ),
    }


@router.get("/analytics/dashboard-batch")
async def dashboard_batch():
    """Batch endpoint — returns weekly-report + study-patterns + learning-velocity in one call.

    V2.4 performance: reduces 3 HTTP round-trips to 1 for the Dashboard page.
    Each sub-result matches the individual endpoint's schema exactly.
    """
    try:
        wr = await weekly_report()
    except Exception:
        wr = None

    try:
        sp = await study_patterns(days=30)
    except Exception:
        sp = None

    try:
        lv = await learning_velocity(days=14)
    except Exception:
        lv = None

    return {
        "weekly_report": wr,
        "study_patterns": sp,
        "learning_velocity": lv,
    }


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
    weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
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


# ── V2.6: Multi-Domain Intelligence ─────────────────────


@router.get("/analytics/domain-recommendation")
async def domain_recommendation(
    limit: int = Query(5, ge=1, le=15),
):
    """Recommend next knowledge domains based on user learning history + cross-links.

    Strategy:
    1. Find domains user has started learning (has progress)
    2. Analyze cross-links from active domains to undiscovered domains
    3. Score candidates: cross-link count * diversity bonus + difficulty match
    4. Return ranked list of recommended domains with reasons
    """
    import json as _json, os, sys

    progress = get_all_progress()
    history = get_history(limit=5000)

    # Group progress by domain
    domain_progress: dict[str, dict] = {}  # domain_id -> {mastered, learning, total}
    concept_to_domain: dict[str, str] = {}
    for p in progress:
        cid = p["concept_id"]
        parts = cid.split("/") if "/" in cid else [cid]
        # We need seed data to map concept→domain; collect concept_ids for now
        domain_progress.setdefault("_raw", []).append(p)

    # Load domains + seed data
    if getattr(sys, "frozen", False):
        data_root = os.path.join(sys._MEIPASS, "seed_data")
    else:
        data_root = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data", "seed")

    domains_path = os.path.join(data_root, "domains.json")
    if not os.path.isfile(domains_path):
        return {"recommendations": [], "active_domains": []}
    with open(domains_path, "r", encoding="utf-8") as f:
        raw = _json.load(f)
    domain_list = raw.get("domains", raw) if isinstance(raw, dict) else raw
    domain_map = {d["id"]: d for d in domain_list}

    # Map concepts to domains from seed data
    concept_domain_map: dict[str, str] = {}
    domain_concept_sets: dict[str, set] = {}
    for d in domain_list:
        did = d["id"]
        seed_path = os.path.join(data_root, did, "seed_graph.json")
        if os.path.isfile(seed_path):
            with open(seed_path, "r", encoding="utf-8") as f:
                seed = _json.load(f)
            for c in seed.get("concepts", []):
                concept_domain_map[c["id"]] = did
                domain_concept_sets.setdefault(did, set()).add(c["id"])

    # Identify active vs undiscovered domains
    active_domains: dict[str, dict] = {}  # domain_id -> {mastered, learning, total_progress}
    for p in progress:
        cid = p["concept_id"]
        did = concept_domain_map.get(cid)
        if not did:
            continue
        if did not in active_domains:
            active_domains[did] = {"mastered": 0, "learning": 0, "total": 0}
        active_domains[did]["total"] += 1
        if p.get("status") == "mastered":
            active_domains[did]["mastered"] += 1
        elif p.get("status") == "learning":
            active_domains[did]["learning"] += 1

    undiscovered = [did for did in domain_map if did not in active_domains]

    # Load cross-links
    cross_links_path = os.path.join(data_root, "cross_sphere_links.json")
    cross_links: list[dict] = []
    if os.path.isfile(cross_links_path):
        with open(cross_links_path, "r", encoding="utf-8") as f:
            cl_data = _json.load(f)
        cross_links = cl_data.get("links", [])

    # Score undiscovered domains
    candidates = []
    for target_did in undiscovered:
        score = 0.0
        reasons = []
        link_count = 0
        linking_domains: set[str] = set()

        for lk in cross_links:
            src_d = lk.get("source_domain", "")
            tgt_d = lk.get("target_domain", "")
            if tgt_d == target_did and src_d in active_domains:
                link_count += 1
                linking_domains.add(src_d)
            elif src_d == target_did and tgt_d in active_domains:
                link_count += 1
                linking_domains.add(tgt_d)

        if link_count > 0:
            score += link_count * 2.0
            score += len(linking_domains) * 3.0  # diversity bonus
            reasons.append(f"与{len(linking_domains)}个已学域有{link_count}条知识关联")

        # Difficulty match: prefer domains with avg difficulty close to user's active domains
        target_info = domain_map.get(target_did, {})
        target_seed_path = os.path.join(data_root, target_did, "seed_graph.json")
        target_concepts = 0
        target_avg_diff = 5.0
        if os.path.isfile(target_seed_path):
            with open(target_seed_path, "r", encoding="utf-8") as f:
                tseed = _json.load(f)
            tcs = tseed.get("concepts", [])
            target_concepts = len(tcs)
            if tcs:
                target_avg_diff = sum(c.get("difficulty", 5) for c in tcs) / len(tcs)

        # Breadth bonus: smaller domains are easier to complete
        if target_concepts > 0:
            completion_ease = max(0, 50 - target_concepts) / 50.0 * 5.0
            score += completion_ease
            if target_concepts <= 100:
                reasons.append(f"精品小域({target_concepts}概念)，易于快速掌握")

        # Popular domain bonus
        sort_order = target_info.get("sort_order", 99)
        if sort_order <= 10:
            score += 2.0
            reasons.append("热门核心领域")

        if not reasons:
            reasons.append("拓展知识面的全新领域")

        candidates.append({
            "domain_id": target_did,
            "domain_name": target_info.get("name", target_did),
            "icon": target_info.get("icon", ""),
            "color": target_info.get("color", "#888"),
            "score": round(score, 1),
            "reasons": reasons,
            "cross_link_count": link_count,
            "linking_domains": list(linking_domains),
            "total_concepts": target_concepts,
            "avg_difficulty": round(target_avg_diff, 1),
        })

    candidates.sort(key=lambda x: x["score"], reverse=True)

    return {
        "recommendations": candidates[:limit],
        "active_domains": [
            {
                "domain_id": did,
                "domain_name": domain_map.get(did, {}).get("name", did),
                **stats,
            }
            for did, stats in active_domains.items()
        ],
        "total_undiscovered": len(undiscovered),
    }


@router.get("/analytics/study-plan")
async def study_plan(
    daily_minutes: int = Query(30, ge=5, le=480, description="Daily study budget in minutes"),
    days: int = Query(7, ge=1, le=30, description="Plan horizon in days"),
):
    """Generate a personalized study plan based on progress, FSRS review schedule, and goals.

    Allocates daily time across three activity types:
    - Review: FSRS-due items (highest priority)
    - Fill Gaps: Unmastered prerequisites blocking progress
    - Learn New: Next concepts in topological order
    """
    import json as _json, os, sys

    progress = get_all_progress()
    history = get_history(limit=2000)
    streak_data = get_streak()

    # Load domain/seed data
    if getattr(sys, "frozen", False):
        data_root = os.path.join(sys._MEIPASS, "seed_data")
    else:
        data_root = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data", "seed")

    # Map concepts to domains
    concept_domain_map: dict[str, str] = {}
    concept_info: dict[str, dict] = {}
    domains_path = os.path.join(data_root, "domains.json")
    domain_map: dict[str, dict] = {}
    if os.path.isfile(domains_path):
        with open(domains_path, "r", encoding="utf-8") as f:
            raw = _json.load(f)
        domain_list = raw.get("domains", raw) if isinstance(raw, dict) else raw
        domain_map = {d["id"]: d for d in domain_list}
        for d in domain_list:
            did = d["id"]
            seed_path = os.path.join(data_root, did, "seed_graph.json")
            if os.path.isfile(seed_path):
                with open(seed_path, "r", encoding="utf-8") as f:
                    seed = _json.load(f)
                for c in seed.get("concepts", []):
                    concept_domain_map[c["id"]] = did
                    concept_info[c["id"]] = {
                        "name": c.get("name", c["id"]),
                        "difficulty": c.get("difficulty", 5),
                        "estimated_minutes": c.get("estimated_minutes", 20),
                        "subdomain_id": c.get("subdomain_id", ""),
                    }

    # Categorize progress
    progress_map = {p["concept_id"]: p for p in progress}
    mastered_ids = {p["concept_id"] for p in progress if p.get("status") == "mastered"}
    learning_ids = {p["concept_id"] for p in progress if p.get("status") == "learning"}

    # Simulate FSRS due items (concepts with mastery_score < 90 that were assessed >24h ago)
    now = time.time()
    review_queue: list[dict] = []
    for p in progress:
        if p.get("status") == "mastered":
            last_learn = p.get("last_learn_at", 0) or 0
            score = p.get("mastery_score", 0)
            # FSRS-like decay: lower score = more urgent review
            days_since = (now - last_learn) / 86400 if last_learn else 999
            urgency = max(0, 100 - score) + days_since * 2
            if days_since > 3:  # only suggest review after 3+ days
                cid = p["concept_id"]
                review_queue.append({
                    "concept_id": cid,
                    "name": concept_info.get(cid, {}).get("name", cid),
                    "domain_id": concept_domain_map.get(cid, ""),
                    "urgency": round(urgency, 1),
                    "days_since_review": round(days_since, 1),
                    "estimated_minutes": 10,  # review is shorter
                    "type": "review",
                })
    review_queue.sort(key=lambda x: x["urgency"], reverse=True)

    # Learning queue: concepts currently in "learning" status
    learn_continue: list[dict] = []
    for cid in learning_ids:
        info = concept_info.get(cid, {})
        learn_continue.append({
            "concept_id": cid,
            "name": info.get("name", cid),
            "domain_id": concept_domain_map.get(cid, ""),
            "estimated_minutes": info.get("estimated_minutes", 20),
            "type": "continue",
        })

    # New concepts: not started, prerequisites met
    new_concepts: list[dict] = []
    for cid, info in concept_info.items():
        if cid not in mastered_ids and cid not in learning_ids:
            new_concepts.append({
                "concept_id": cid,
                "name": info.get("name", cid),
                "domain_id": concept_domain_map.get(cid, ""),
                "difficulty": info.get("difficulty", 5),
                "estimated_minutes": info.get("estimated_minutes", 20),
                "type": "new",
            })
    # Prefer lower difficulty first
    new_concepts.sort(key=lambda x: x["difficulty"])

    # Build daily plan
    daily_plans: list[dict] = []
    review_idx = 0
    continue_idx = 0
    new_idx = 0

    for day in range(days):
        remaining = daily_minutes
        day_items: list[dict] = []

        # Phase 1: Review (40% of time max)
        review_budget = int(daily_minutes * 0.4)
        while remaining > 0 and review_budget > 0 and review_idx < len(review_queue):
            item = review_queue[review_idx]
            cost = item["estimated_minutes"]
            if cost <= remaining:
                day_items.append(item)
                remaining -= cost
                review_budget -= cost
            review_idx += 1

        # Phase 2: Continue learning (30% of time max)
        continue_budget = int(daily_minutes * 0.3)
        while remaining > 0 and continue_budget > 0 and continue_idx < len(learn_continue):
            item = learn_continue[continue_idx]
            cost = item["estimated_minutes"]
            if cost <= remaining:
                day_items.append(item)
                remaining -= cost
                continue_budget -= cost
            continue_idx += 1

        # Phase 3: New concepts (remaining time)
        while remaining >= 10 and new_idx < len(new_concepts):
            item = new_concepts[new_idx]
            cost = item["estimated_minutes"]
            if cost <= remaining:
                day_items.append(item)
                remaining -= cost
            new_idx += 1

        daily_plans.append({
            "day": day + 1,
            "items": day_items,
            "total_minutes": daily_minutes - remaining,
            "review_count": sum(1 for i in day_items if i["type"] == "review"),
            "learn_count": sum(1 for i in day_items if i["type"] in ("continue", "new")),
        })

    # Summary
    total_items = sum(len(d["items"]) for d in daily_plans)
    total_review = sum(d["review_count"] for d in daily_plans)
    total_learn = sum(d["learn_count"] for d in daily_plans)

    return {
        "plan": daily_plans,
        "summary": {
            "days": days,
            "daily_minutes": daily_minutes,
            "total_items": total_items,
            "total_review": total_review,
            "total_learn": total_learn,
            "total_minutes": sum(d["total_minutes"] for d in daily_plans),
        },
        "queues": {
            "review_pending": len(review_queue),
            "continue_pending": len(learn_continue),
            "new_available": len(new_concepts),
        },
    }


@router.get("/analytics/learning-journey")
async def learning_journey():
    """Cross-domain learning journey — achievement timeline across all domains.

    Returns milestones, domain completions, and learning streaks as a timeline.
    Useful for a "Journey" page showing user's entire learning evolution.
    """
    import json as _json, os, sys

    progress = get_all_progress()
    history = get_history(limit=10000)
    streak_data = get_streak()

    # Load domain data
    if getattr(sys, "frozen", False):
        data_root = os.path.join(sys._MEIPASS, "seed_data")
    else:
        data_root = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data", "seed")

    concept_domain_map: dict[str, str] = {}
    concept_info: dict[str, dict] = {}
    domain_concept_counts: dict[str, int] = {}
    domain_map: dict[str, dict] = {}

    domains_path = os.path.join(data_root, "domains.json")
    if os.path.isfile(domains_path):
        with open(domains_path, "r", encoding="utf-8") as f:
            raw = _json.load(f)
        domain_list = raw.get("domains", raw) if isinstance(raw, dict) else raw
        domain_map = {d["id"]: d for d in domain_list}
        for d in domain_list:
            did = d["id"]
            seed_path = os.path.join(data_root, did, "seed_graph.json")
            if os.path.isfile(seed_path):
                with open(seed_path, "r", encoding="utf-8") as f:
                    seed = _json.load(f)
                concepts = seed.get("concepts", [])
                domain_concept_counts[did] = len(concepts)
                for c in concepts:
                    concept_domain_map[c["id"]] = did
                    concept_info[c["id"]] = {
                        "name": c.get("name", c["id"]),
                        "is_milestone": c.get("is_milestone", False),
                    }

    # Build timeline events from history
    events: list[dict] = []
    domain_mastered: dict[str, int] = {}

    for entry in history:
        cid = entry.get("concept_id", "")
        ts = entry.get("timestamp", 0)
        mastered = entry.get("mastered", False)
        score = entry.get("score", 0)
        did = concept_domain_map.get(cid, "")
        info = concept_info.get(cid, {})

        if mastered:
            domain_mastered.setdefault(did, 0)
            domain_mastered[did] += 1

            event = {
                "type": "mastered",
                "concept_id": cid,
                "concept_name": info.get("name", cid),
                "domain_id": did,
                "domain_name": domain_map.get(did, {}).get("name", did),
                "score": score,
                "timestamp": ts,
            }

            # Check if this was a milestone concept
            if info.get("is_milestone"):
                event["type"] = "milestone"
                event["badge"] = "🏆"

            events.append(event)

            # Check domain completion milestones (25/50/75/100%)
            total = domain_concept_counts.get(did, 0)
            if total > 0:
                count = domain_mastered[did]
                for pct in [25, 50, 75, 100]:
                    threshold = int(total * pct / 100)
                    if count == threshold and threshold > 0:
                        events.append({
                            "type": "domain_milestone",
                            "domain_id": did,
                            "domain_name": domain_map.get(did, {}).get("name", did),
                            "percentage": pct,
                            "mastered_count": count,
                            "total_concepts": total,
                            "timestamp": ts,
                            "badge": "🌟" if pct == 100 else "⭐" if pct >= 75 else "📈",
                        })

    # Sort by timestamp (newest first)
    events.sort(key=lambda x: x.get("timestamp", 0), reverse=True)

    # Domain progress summary
    domain_summary = []
    for did, d_info in domain_map.items():
        total = domain_concept_counts.get(did, 0)
        mastered = domain_mastered.get(did, 0)
        if mastered > 0 or total > 0:
            domain_summary.append({
                "domain_id": did,
                "domain_name": d_info.get("name", did),
                "icon": d_info.get("icon", ""),
                "color": d_info.get("color", "#888"),
                "mastered": mastered,
                "total": total,
                "percentage": round(mastered / max(1, total) * 100, 1),
            })
    domain_summary.sort(key=lambda x: x["percentage"], reverse=True)

    return {
        "events": events[:200],  # Latest 200 events
        "total_events": len(events),
        "domain_summary": domain_summary,
        "stats": {
            "total_mastered": sum(d["mastered"] for d in domain_summary),
            "domains_started": sum(1 for d in domain_summary if d["mastered"] > 0),
            "domains_completed": sum(1 for d in domain_summary if d["percentage"] >= 100),
            "current_streak": streak_data.get("current", 0) if isinstance(streak_data, dict) else 0,
        },
    }
