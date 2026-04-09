"""Analytics Experience API — V2.5 session history, mastery timeline, study time, and streak insights.

Extracted from analytics.py (V2.10 code health) to keep router files under 800 lines.

Provides:
- Session history timeline with filtering & pagination (V2.5)
- Per-concept mastery timeline (V2.5)
- Study time report with productivity metrics (V2.5)
- Streak insights & consistency analysis (V2.5)
"""

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
