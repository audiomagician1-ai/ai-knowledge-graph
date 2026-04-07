"""Analytics API — Learning analytics, content quality insights, and usage statistics.

Provides aggregate views for:
- Concept difficulty distribution (which concepts are hardest)
- Domain mastery heatmap
- Time-based learning trends
- Content quality signals (low-scoring concepts → improvement priority)
"""

import time

from fastapi import APIRouter
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
