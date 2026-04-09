"""Analytics API — Core learning analytics, content quality insights, and usage statistics.

Provides aggregate views for:
- Concept difficulty distribution (which concepts are hardest)
- Domain mastery heatmap
- Time-based learning trends
- Content quality signals (low-scoring concepts → improvement priority)
- Dashboard batch endpoint (V2.4)

V2.5 endpoints moved to analytics_experience.py (V2.10 split)
V2.6 endpoints moved to analytics_planning.py (V2.10 split)
V2.7+ endpoints in analytics_insights.py (V2.9 split)
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


# ── V2.5 endpoints moved to analytics_experience.py (V2.10 split) ──
# ── V2.6 endpoints moved to analytics_planning.py (V2.10 split) ──
# ── V2.7+ endpoints in analytics_insights.py (V2.9 split) ──

