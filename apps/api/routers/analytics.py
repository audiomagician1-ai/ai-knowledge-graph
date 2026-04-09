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
