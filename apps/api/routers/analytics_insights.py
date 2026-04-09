"""Analytics Insights API — V2.7 Smart analytics and engagement.


Provides:
- Weak concept detection (V2.7)
- Learning efficiency analysis (V2.7)
- Difficulty calibration (V2.7)
"""

import time

from fastapi import APIRouter, Query
from utils.logger import get_logger

from db.sqlite_client import get_all_progress, get_history, get_streak
from routers.analytics_utils import load_seed_metadata

logger = get_logger(__name__)

router = APIRouter()



# ── V2.7: Smart Analytics & Engagement ──────────────────


@router.get("/analytics/weak-concepts")
async def weak_concepts(
    limit: int = Query(10, ge=1, le=50),
):
    """Detect concepts the user struggles with most.

    Criteria (any combination raises the "weakness" score):
    - Multiple assessment sessions without reaching mastery
    - Low mastery score relative to number of sessions
    - Score decreased between consecutive attempts
    - High session count but still "learning" status

    Returns ranked list with actionable insights.
    """
    progress = get_all_progress()
    history = get_history(limit=10000)

    # Build per-concept assessment history
    concept_assessments: dict[str, list[dict]] = {}
    for entry in history:
        cid = entry.get("concept_id", "")
        if cid and entry.get("score") is not None:
            concept_assessments.setdefault(cid, []).append(entry)

    # Sort each concept's history by timestamp
    for cid in concept_assessments:
        concept_assessments[cid].sort(key=lambda x: x.get("timestamp", 0))

    progress_map = {p["concept_id"]: p for p in progress}
    weak: list[dict] = []

    for cid, attempts in concept_assessments.items():
        p = progress_map.get(cid, {})
        status = p.get("status", "not_started")
        sessions = p.get("sessions", len(attempts))
        current_score = p.get("mastery_score", 0)

        if sessions < 2:
            continue  # Need at least 2 attempts to detect weakness

        scores = [a.get("score", 0) for a in attempts if a.get("score") is not None]
        if not scores:
            continue

        weakness_score = 0.0
        reasons: list[str] = []

        # Factor 1: Many sessions but not mastered
        if sessions >= 3 and status != "mastered":
            weakness_score += min(30, sessions * 5)
            reasons.append(f"已尝试{sessions}次仍未掌握")

        # Factor 2: Low score despite multiple attempts
        avg_score = sum(scores) / len(scores)
        if avg_score < 60 and len(scores) >= 2:
            weakness_score += (60 - avg_score) * 0.5
            reasons.append(f"平均分{round(avg_score, 1)}偏低")

        # Factor 3: Score regression (later score < earlier score)
        if len(scores) >= 2 and scores[-1] < scores[0]:
            regression = scores[0] - scores[-1]
            weakness_score += regression * 0.3
            reasons.append(f"分数下降了{round(regression, 1)}分")

        # Factor 4: Plateau (last 3 scores within 5 points)
        if len(scores) >= 3:
            recent_3 = scores[-3:]
            spread = max(recent_3) - min(recent_3)
            if spread <= 5 and avg_score < 75:
                weakness_score += 10
                reasons.append("学习进展停滞")

        if weakness_score > 5 and reasons:
            weak.append({
                "concept_id": cid,
                "status": status,
                "current_score": current_score,
                "sessions": sessions,
                "avg_score": round(avg_score, 1),
                "score_trend": scores[-3:] if len(scores) >= 3 else scores,
                "weakness_score": round(weakness_score, 1),
                "reasons": reasons,
                "suggestion": _get_weakness_suggestion(reasons, sessions, avg_score),
            })

    weak.sort(key=lambda x: x["weakness_score"], reverse=True)
    return {
        "weak_concepts": weak[:limit],
        "total_weak": len(weak),
        "total_assessed": len(concept_assessments),
    }


def _get_weakness_suggestion(reasons: list[str], sessions: int, avg: float) -> str:
    """Generate actionable suggestion based on weakness pattern."""
    if any("下降" in r for r in reasons):
        return "建议回顾基础前置知识，可能存在知识盲点"
    if any("停滞" in r for r in reasons):
        return "尝试换个角度理解，或查看跨域关联概念获取新视角"
    if sessions >= 5:
        return "建议拆解为更小的子概念逐步攻克"
    if avg < 40:
        return "建议先学习前置概念，打好基础再回来"
    return "多做练习巩固理解，关注薄弱的评估维度"


@router.get("/analytics/learning-efficiency")
async def learning_efficiency():
    """Compute learning efficiency metrics — time-to-mastery and per-concept efficiency.

    Efficiency = mastery_score / sessions (how quickly concepts are mastered).
    Also computes domain-level efficiency comparisons.
    """
    progress = get_all_progress()
    history = get_history(limit=10000)

    concept_domain_map, concept_info, domain_map = load_seed_metadata()

    # Per-concept efficiency
    concept_metrics: list[dict] = []
    domain_efficiency: dict[str, dict] = {}

    for p in progress:
        cid = p["concept_id"]
        sessions = p.get("sessions", 0)
        score = p.get("mastery_score", 0)
        status = p.get("status", "not_started")
        did = concept_domain_map.get(cid, "")

        if sessions <= 0:
            continue

        efficiency = round(score / sessions, 1)

        # Time to mastery (if mastered)
        first_ts = None
        mastered_ts = p.get("mastered_at")
        for entry in history:
            if entry.get("concept_id") == cid:
                ts = entry.get("timestamp", 0)
                if first_ts is None or ts < first_ts:
                    first_ts = ts

        ttm = None
        if mastered_ts and first_ts and mastered_ts > first_ts:
            ttm = round((mastered_ts - first_ts) / 3600, 1)

        concept_metrics.append({
            "concept_id": cid,
            "name": concept_info.get(cid, {}).get("name", cid),
            "domain_id": did,
            "difficulty": concept_info.get(cid, {}).get("difficulty", 5),
            "sessions": sessions,
            "score": score,
            "status": status,
            "efficiency": efficiency,
            "time_to_mastery_hours": ttm,
        })

        # Aggregate by domain
        if did:
            if did not in domain_efficiency:
                domain_efficiency[did] = {"total_eff": 0, "count": 0, "mastered_count": 0, "total_sessions": 0}
            domain_efficiency[did]["total_eff"] += efficiency
            domain_efficiency[did]["count"] += 1
            domain_efficiency[did]["total_sessions"] += sessions
            if status == "mastered":
                domain_efficiency[did]["mastered_count"] += 1

    concept_metrics.sort(key=lambda x: x["efficiency"])

    # Domain summary
    domain_summary = []
    for did, stats in domain_efficiency.items():
        if stats["count"] > 0:
            domain_summary.append({
                "domain_id": did,
                "domain_name": domain_map.get(did, {}).get("name", did),
                "avg_efficiency": round(stats["total_eff"] / stats["count"], 1),
                "concepts_attempted": stats["count"],
                "concepts_mastered": stats["mastered_count"],
                "avg_sessions_per_concept": round(stats["total_sessions"] / stats["count"], 1),
            })
    domain_summary.sort(key=lambda x: x["avg_efficiency"], reverse=True)

    all_eff = [m["efficiency"] for m in concept_metrics]
    all_ttm = [m["time_to_mastery_hours"] for m in concept_metrics if m["time_to_mastery_hours"] is not None]

    return {
        "concepts": concept_metrics[:50],
        "total_assessed": len(concept_metrics),
        "domain_efficiency": domain_summary,
        "global": {
            "avg_efficiency": round(sum(all_eff) / max(1, len(all_eff)), 1),
            "median_efficiency": round(sorted(all_eff)[len(all_eff) // 2], 1) if all_eff else 0,
            "avg_time_to_mastery_hours": round(sum(all_ttm) / max(1, len(all_ttm)), 1) if all_ttm else None,
            "total_concepts_assessed": len(concept_metrics),
            "total_mastered": sum(1 for m in concept_metrics if m["status"] == "mastered"),
        },
    }


@router.get("/analytics/difficulty-calibration")
async def difficulty_calibration(
    domain_id: str = Query("ai-engineering", description="Domain to calibrate"),
):
    """Compare seed difficulty ratings with actual user performance.

    Identifies miscalibrated concepts where:
    - Easy concepts (low difficulty) have low mastery scores
    - Hard concepts (high difficulty) have high mastery rates
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
        return {"domain_id": domain_id, "calibration": [], "summary": {}}

    with open(seed_path, "r", encoding="utf-8") as f:
        seed = _json.load(f)

    concepts = seed.get("concepts", [])
    calibration: list[dict] = []
    difficulty_buckets: dict[int, dict] = {}

    for c in concepts:
        cid = c["id"]
        seed_diff = c.get("difficulty", 5)
        p = progress_map.get(cid)

        if not p or p.get("sessions", 0) == 0:
            continue

        score = p.get("mastery_score", 0)
        sessions = p.get("sessions", 0)
        status = p.get("status", "not_started")

        expected_score_range = max(30, 100 - seed_diff * 8)
        gap = score - expected_score_range
        miscalibrated = abs(gap) > 25

        entry = {
            "concept_id": cid,
            "name": c.get("name", cid),
            "seed_difficulty": seed_diff,
            "actual_score": score,
            "sessions": sessions,
            "status": status,
            "expected_score_range": expected_score_range,
            "gap": round(gap, 1),
            "miscalibrated": miscalibrated,
        }

        if miscalibrated:
            if gap > 0:
                entry["signal"] = "easier_than_labeled"
                entry["suggestion"] = f"标注难度{seed_diff}偏高，实际表现优于预期"
            else:
                entry["signal"] = "harder_than_labeled"
                entry["suggestion"] = f"标注难度{seed_diff}偏低，用户实际掌握困难"

        calibration.append(entry)

        if seed_diff not in difficulty_buckets:
            difficulty_buckets[seed_diff] = {"scores": [], "sessions": [], "mastered": 0, "total": 0}
        difficulty_buckets[seed_diff]["scores"].append(score)
        difficulty_buckets[seed_diff]["sessions"].append(sessions)
        difficulty_buckets[seed_diff]["total"] += 1
        if status == "mastered":
            difficulty_buckets[seed_diff]["mastered"] += 1

    calibration.sort(key=lambda x: abs(x["gap"]), reverse=True)

    summary: list[dict] = []
    for diff in sorted(difficulty_buckets.keys()):
        b = difficulty_buckets[diff]
        scores = b["scores"]
        sessions = b["sessions"]
        summary.append({
            "difficulty": diff,
            "count": b["total"],
            "avg_score": round(sum(scores) / len(scores), 1) if scores else 0,
            "avg_sessions": round(sum(sessions) / len(sessions), 1) if sessions else 0,
            "mastery_rate": round(b["mastered"] / b["total"] * 100, 1) if b["total"] > 0 else 0,
        })

    miscalibrated_count = sum(1 for c in calibration if c.get("miscalibrated"))

    return {
        "domain_id": domain_id,
        "calibration": calibration[:30],
        "total_assessed": len(calibration),
        "miscalibrated_count": miscalibrated_count,
        "difficulty_summary": summary,
    }

# -- V2.8 endpoints moved to analytics_social.py (V2.10 split) --
# -- V2.9 endpoints moved to analytics_search.py (V2.10 split) --
# -- V3.2 mastery-forecast moved to analytics_forecast.py (V3.8 split) --
# -- V3.6 fsrs-insights + goal-recommendations moved to analytics_forecast.py (V3.8 split) --
