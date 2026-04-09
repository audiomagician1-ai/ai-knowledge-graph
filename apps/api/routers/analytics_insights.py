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


# ── V3.2: Domain Mastery Forecast ─────────────────────────


@router.get("/analytics/mastery-forecast/{domain_id}")
async def mastery_forecast(
    domain_id: str,
    daily_minutes: int = Query(30, ge=5, le=240, description="Expected daily study time"),
):
    """Forecast when a user will master a domain at their current pace.

    Uses historical learning velocity (concepts mastered per hour) to project
    completion of remaining unmastered concepts. Accounts for difficulty
    weighting — harder concepts take proportionally longer.

    Returns estimated days to completion, per-subdomain breakdown, and
    a confidence level based on data availability.
    """
    import json as _json, os, sys, math

    progress = get_all_progress()
    history = get_history(limit=10000)
    concept_domain_map, concept_info, domain_map = load_seed_metadata()

    if getattr(sys, "frozen", False):
        data_root = os.path.join(sys._MEIPASS, "seed_data")
    else:
        data_root = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "data", "seed",
        )

    seed_path = os.path.join(data_root, domain_id, "seed_graph.json")
    if not os.path.isfile(seed_path):
        return {"domain_id": domain_id, "error": "Domain not found"}

    with open(seed_path, "r", encoding="utf-8") as f:
        seed = _json.load(f)

    concepts = seed.get("concepts", [])
    progress_map = {p["concept_id"]: p for p in progress}

    # Classify concepts
    mastered = []
    remaining = []
    for c in concepts:
        cid = c["id"]
        p = progress_map.get(cid)
        if p and p.get("status") == "mastered":
            mastered.append(c)
        else:
            remaining.append(c)

    total = len(concepts)
    mastered_count = len(mastered)
    remaining_count = len(remaining)

    if remaining_count == 0:
        return {
            "domain_id": domain_id,
            "domain_name": domain_map.get(domain_id, {}).get("name", domain_id),
            "total_concepts": total,
            "mastered": mastered_count,
            "remaining": 0,
            "completion_pct": 100.0,
            "estimated_days": 0,
            "estimated_hours": 0,
            "confidence": "high",
            "subdomain_forecast": [],
        }

    # Calculate learning velocity from history
    now = time.time()
    recent_mastered = [
        e for e in history
        if e.get("mastered") and (now - e.get("timestamp", 0)) < 30 * 86400
    ]

    # Estimate minutes per concept mastery
    if len(recent_mastered) >= 3:
        # Use actual velocity
        min_per_concept = daily_minutes * 30 / max(1, len(recent_mastered))
        confidence = "high" if len(recent_mastered) >= 10 else "medium"
    elif mastered_count > 0:
        # Fallback: assume 15 min per concept
        min_per_concept = 15
        confidence = "low"
    else:
        # No data: assume 20 min per concept
        min_per_concept = 20
        confidence = "low"

    # Weight by difficulty
    total_weighted_min = 0
    sub_forecast: dict[str, dict] = {}
    for c in remaining:
        diff = c.get("difficulty", 5)
        weight = 0.5 + diff * 0.15  # difficulty 1 = 0.65x, 10 = 2.0x
        est_min = min_per_concept * weight
        total_weighted_min += est_min

        sid = c.get("subdomain_id", "other")
        if sid not in sub_forecast:
            sub_forecast[sid] = {"remaining": 0, "est_minutes": 0}
        sub_forecast[sid]["remaining"] += 1
        sub_forecast[sid]["est_minutes"] += est_min

    est_hours = round(total_weighted_min / 60, 1)
    est_days = math.ceil(total_weighted_min / daily_minutes)

    subdomain_list = []
    for sid, sf in sorted(sub_forecast.items(), key=lambda x: -x[1]["remaining"]):
        subdomain_list.append({
            "subdomain_id": sid,
            "remaining": sf["remaining"],
            "estimated_hours": round(sf["est_minutes"] / 60, 1),
            "estimated_days": math.ceil(sf["est_minutes"] / daily_minutes),
        })

    return {
        "domain_id": domain_id,
        "domain_name": domain_map.get(domain_id, {}).get("name", domain_id),
        "total_concepts": total,
        "mastered": mastered_count,
        "remaining": remaining_count,
        "completion_pct": round(mastered_count / total * 100, 1),
        "estimated_days": est_days,
        "estimated_hours": est_hours,
        "daily_minutes": daily_minutes,
        "confidence": confidence,
        "subdomain_forecast": subdomain_list,
    }


# ── V3.6: FSRS Retention Analytics ──────────────────────

@router.get("/analytics/fsrs-insights")
async def fsrs_insights():
    """FSRS retention analytics — forgetting risk, review efficiency, and optimal intervals.

    Analyzes all reviewed concepts to provide:
    - Retention summary (reviewed/due/overdue/avg stability)
    - Forgetting risk distribution (high/medium/low risk buckets)
    - Review efficiency metrics (avg reviews to stable, lapse rate)
    - Top at-risk concepts (sorted by urgency)
    """
    from db.sqlite_client import get_db
    from engines.learning.fsrs_scheduler import FSRSScheduler

    now = time.time()
    scheduler = FSRSScheduler()

    # Get all concepts with FSRS state > 0 (reviewed at least once)
    with get_db() as conn:
        rows = conn.execute(
            """SELECT concept_id, status, mastery_score, fsrs_stability, fsrs_difficulty,
                      fsrs_due, fsrs_elapsed_days, fsrs_scheduled_days, fsrs_reps,
                      fsrs_lapses, fsrs_state, fsrs_last_review
               FROM concept_progress
               WHERE fsrs_state > 0
               ORDER BY fsrs_due ASC""",
        ).fetchall()
    cards = [dict(r) for r in rows]

    if not cards:
        return {
            "total_reviewed": 0,
            "retention_summary": {},
            "risk_distribution": {"high": 0, "medium": 0, "low": 0},
            "efficiency": {},
            "at_risk_concepts": [],
        }

    # ── Retention Summary ──
    total = len(cards)
    due_count = sum(1 for c in cards if c["fsrs_due"] <= now)
    overdue_count = sum(1 for c in cards if c["fsrs_due"] <= now and (now - c["fsrs_due"]) > 86400)
    avg_stability = sum(c["fsrs_stability"] for c in cards) / total
    avg_difficulty = sum(c["fsrs_difficulty"] for c in cards) / total
    total_reps = sum(c["fsrs_reps"] for c in cards)
    total_lapses = sum(c["fsrs_lapses"] for c in cards)

    # ── Risk Distribution ──
    high_risk, medium_risk, low_risk = [], [], []
    for c in cards:
        retrievability = scheduler.forgetting_curve(
            max(0, (now - (c["fsrs_last_review"] or now)) / 86400),
            max(0.01, c["fsrs_stability"]),
        )
        c["_retrievability"] = retrievability
        if retrievability < 0.5:
            high_risk.append(c)
        elif retrievability < 0.8:
            medium_risk.append(c)
        else:
            low_risk.append(c)

    # ── Efficiency Metrics ──
    stable_cards = [c for c in cards if c["fsrs_stability"] >= 10.0]
    lapse_rate = total_lapses / max(1, total_reps)

    # ── At-risk concepts (top 10 by urgency = low retrievability + high downstream value) ──
    concept_domain_map, concept_info, _ = load_seed_metadata()
    at_risk = sorted(high_risk + medium_risk, key=lambda c: c["_retrievability"])[:10]
    at_risk_out = []
    for c in at_risk:
        cid = c["concept_id"]
        info = concept_info.get(cid, {})
        at_risk_out.append({
            "concept_id": cid,
            "name": info.get("name", cid),
            "domain": concept_domain_map.get(cid, "unknown"),
            "retrievability": round(c["_retrievability"], 3),
            "stability": round(c["fsrs_stability"], 2),
            "difficulty": round(c["fsrs_difficulty"], 2),
            "reps": c["fsrs_reps"],
            "lapses": c["fsrs_lapses"],
            "overdue_days": round(max(0, (now - c["fsrs_due"]) / 86400), 1) if c["fsrs_due"] <= now else 0,
        })

    return {
        "total_reviewed": total,
        "retention_summary": {
            "due_count": due_count,
            "overdue_count": overdue_count,
            "avg_stability": round(avg_stability, 2),
            "avg_difficulty": round(avg_difficulty, 2),
            "total_reviews": total_reps,
            "total_lapses": total_lapses,
        },
        "risk_distribution": {
            "high": len(high_risk),
            "medium": len(medium_risk),
            "low": len(low_risk),
        },
        "efficiency": {
            "stable_concepts": len(stable_cards),
            "stable_pct": round(len(stable_cards) / total * 100, 1),
            "lapse_rate": round(lapse_rate, 3),
            "avg_reps_per_concept": round(total_reps / total, 1),
        },
        "at_risk_concepts": at_risk_out,
    }


# ── V3.6: Goal Recommendations ──────────────────────────

@router.get("/analytics/goal-recommendations")
async def goal_recommendations():
    """Smart study goal suggestions based on learning pace and history.

    Analyzes recent activity patterns to recommend:
    - Daily concept target (based on 7-day average)
    - Weekly mastery target
    - Suggested study time
    - Domain focus recommendations
    """
    all_progress = get_all_progress()
    history = get_history(2000)
    streak_data = get_streak()
    now = time.time()

    # ── Calculate recent pace (7-day window) ──
    week_ago = now - 7 * 86400
    recent_history = [h for h in history if h.get("timestamp", 0) >= week_ago]

    # Daily activity distribution
    from collections import defaultdict
    daily_events: dict[str, int] = defaultdict(int)
    daily_mastered: dict[str, int] = defaultdict(int)
    for h in recent_history:
        day = time.strftime("%Y-%m-%d", time.localtime(h.get("timestamp", 0)))
        daily_events[day] += 1
        if h.get("mastered"):
            daily_mastered[day] += 1

    active_days = len(daily_events)
    avg_daily_events = sum(daily_events.values()) / max(1, active_days)
    avg_daily_mastered = sum(daily_mastered.values()) / max(1, active_days)
    total_mastered = sum(1 for p in all_progress if p["status"] == "mastered")

    # ── Smart goal calculation ──
    # Base: slight stretch from current average (10-20% more)
    concept_target = max(2, round(avg_daily_events * 1.15))
    mastery_weekly = max(1, round(avg_daily_mastered * 7 * 1.1))
    est_minutes = max(10, round(concept_target * 8))  # ~8 min per concept average

    # Adjust based on streak (momentum bonus)
    current_streak = streak_data.get("current", 0)
    if current_streak >= 7:
        concept_target = max(concept_target, round(concept_target * 1.1))
    elif current_streak == 0:
        # Cold start: lower targets
        concept_target = max(2, min(concept_target, 3))
        est_minutes = max(10, min(est_minutes, 25))

    # ── Domain focus ──
    concept_domain_map, _, domain_map = load_seed_metadata()
    domain_progress: dict[str, dict] = {}
    for p in all_progress:
        did = concept_domain_map.get(p["concept_id"])
        if did:
            if did not in domain_progress:
                domain_progress[did] = {"mastered": 0, "learning": 0, "total": 0}
            domain_progress[did][p["status"]] = domain_progress[did].get(p["status"], 0) + 1

    # Find domains with most "in progress" concepts
    focus_domains = []
    for did, dp in domain_progress.items():
        learning = dp.get("learning", 0)
        mastered = dp.get("mastered", 0)
        if learning > 0:
            meta = domain_map.get(did, {})
            focus_domains.append({
                "domain_id": did,
                "domain_name": meta.get("name", did),
                "learning_count": learning,
                "mastered_count": mastered,
                "reason": "有进行中的概念" if learning > mastered else "接近完成",
            })
    focus_domains.sort(key=lambda d: d["learning_count"], reverse=True)

    # ── Recommendations list ──
    recommendations = []
    recommendations.append({
        "type": "daily_concepts",
        "title": f"每天学习 {concept_target} 个概念",
        "value": concept_target,
        "unit": "concepts/day",
        "rationale": f"基于你近7天平均 {round(avg_daily_events, 1)} 次/天 (+15%挑战)",
    })
    recommendations.append({
        "type": "weekly_mastery",
        "title": f"每周掌握 {mastery_weekly} 个概念",
        "value": mastery_weekly,
        "unit": "mastered/week",
        "rationale": f"基于近期掌握速度 ({round(avg_daily_mastered, 1)}/天)",
    })
    recommendations.append({
        "type": "daily_minutes",
        "title": f"每天学习 {est_minutes} 分钟",
        "value": est_minutes,
        "unit": "minutes/day",
        "rationale": f"约 {concept_target} 概念 × 8分钟/概念",
    })

    if current_streak > 0:
        next_milestone = next((m for m in [7, 14, 30, 60, 90] if m > current_streak), 365)
        recommendations.append({
            "type": "streak_goal",
            "title": f"保持连续学习到 {next_milestone} 天",
            "value": next_milestone,
            "unit": "days",
            "rationale": f"当前连续 {current_streak} 天，距下一里程碑 {next_milestone - current_streak} 天",
        })

    return {
        "recommendations": recommendations,
        "focus_domains": focus_domains[:4],
        "context": {
            "active_days_7d": active_days,
            "avg_daily_events": round(avg_daily_events, 1),
            "avg_daily_mastered": round(avg_daily_mastered, 1),
            "current_streak": current_streak,
            "total_mastered": total_mastered,
        },
    }
