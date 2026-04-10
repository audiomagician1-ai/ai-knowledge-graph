"""Analytics Advanced API — V3.9 cross-domain insights + learning style detection."""

import time

from fastapi import APIRouter
from utils.logger import get_logger

from db.sqlite_client import get_all_progress, get_history, get_streak
from routers.analytics_utils import load_seed_metadata

logger = get_logger(__name__)

router = APIRouter()


# ── V3.9: Cross-Domain Insights ──────────────────────────
@router.get("/analytics/cross-domain-insights")
async def cross_domain_insights():
    """Analyze knowledge transfer patterns across domains — pairs, synergy, suggestions."""
    import json as _json, os, sys

    all_progress = get_all_progress()
    concept_domain_map, concept_info, domain_map = load_seed_metadata()

    # Load cross-sphere links
    if getattr(sys, "frozen", False):
        links_path = os.path.join(sys._MEIPASS, "seed_data", "cross_sphere_links.json")
    else:
        links_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "data", "seed", "cross_sphere_links.json",
        )
    cross_links = []
    if os.path.isfile(links_path):
        with open(links_path, "r", encoding="utf-8") as f:
            raw = _json.load(f)
            cross_links = raw.get("links", raw) if isinstance(raw, dict) else raw

    # Map user mastery per domain
    domain_mastered: dict[str, int] = {}
    domain_learning: dict[str, int] = {}
    for p in all_progress:
        did = concept_domain_map.get(p["concept_id"])
        if did:
            if p["status"] == "mastered":
                domain_mastered[did] = domain_mastered.get(did, 0) + 1
            elif p["status"] == "learning":
                domain_learning[did] = domain_learning.get(did, 0) + 1

    # Count cross-domain links between each pair
    pair_links: dict[tuple[str, str], int] = {}
    for link in cross_links:
        src = link.get("source_id", link.get("source", ""))
        tgt = link.get("target_id", link.get("target", ""))
        d1 = concept_domain_map.get(src)
        d2 = concept_domain_map.get(tgt)
        if d1 and d2 and d1 != d2:
            key = tuple(sorted([d1, d2]))
            pair_links[key] = pair_links.get(key, 0) + 1

    # Build domain pair insights
    pairs = []
    for (d1, d2), link_count in sorted(pair_links.items(), key=lambda x: -x[1])[:15]:
        m1 = domain_mastered.get(d1, 0)
        m2 = domain_mastered.get(d2, 0)
        transfer = round(min(m1, m2) / max(1, link_count) * 10, 1)
        pairs.append({
            "domain_a": d1, "domain_a_name": domain_map.get(d1, {}).get("name", d1),
            "domain_b": d2, "domain_b_name": domain_map.get(d2, {}).get("name", d2),
            "shared_links": link_count, "mastered_a": m1, "mastered_b": m2,
            "transfer_score": transfer,
        })

    # Suggest next domain
    active_domains = set(d for d, m in domain_mastered.items() if m > 0)
    suggestions = []
    for did in domain_map:
        if did in active_domains:
            continue
        synergy = sum(cnt for (d1, d2), cnt in pair_links.items()
                      if did in (d1, d2) and (d2 if d1 == did else d1) in active_domains)
        if synergy > 0:
            suggestions.append({
                "domain_id": did, "domain_name": domain_map.get(did, {}).get("name", did),
                "synergy_score": synergy, "reason": f"与已学领域有{synergy}条跨域链接",
            })
    suggestions.sort(key=lambda s: s["synergy_score"], reverse=True)

    return {
        "domain_pairs": pairs, "total_cross_links": len(cross_links),
        "active_domains": len(active_domains), "suggested_next": suggestions[:5],
    }


# ── V3.9: Learning Style Detection ──────────────────────

@router.get("/analytics/learning-style")
async def learning_style():
    """Detect user's learning style from behavioral patterns.

    Analyzes speed/depth preference, time distribution, domain breadth,
    consistency patterns, and generates personalized learning style traits.
    """
    all_progress = get_all_progress()
    history = get_history(5000)
    streak_data = get_streak()

    if not history:
        return {"style": "新手", "traits": [], "metrics": {}}

    now = time.time()
    concept_domain_map, _, domain_map = load_seed_metadata()

    # ── Speed vs Depth ──
    mastered = [p for p in all_progress if p["status"] == "mastered"]
    total_sessions = sum(p.get("sessions", 0) for p in all_progress)
    avg_stm = sum(p.get("sessions", 1) for p in mastered) / max(1, len(mastered)) if mastered else 0

    # ── Time Distribution ──
    hour_counts = [0] * 24
    for h in history:
        ts = h.get("timestamp", 0)
        if ts > 0:
            hour_counts[time.localtime(ts).tm_hour] += 1

    total_events = sum(hour_counts)
    morning = sum(hour_counts[6:12])
    afternoon = sum(hour_counts[12:18])
    evening = sum(hour_counts[18:24])
    night = sum(hour_counts[0:6])
    peak_hour = hour_counts.index(max(hour_counts)) if total_events > 0 else 12
    time_pref = ("morning" if morning >= max(afternoon, evening, night) else
                 "afternoon" if afternoon >= max(evening, night) else
                 "evening" if evening >= night else "night")

    # ── Domain Breadth ──
    active_doms = {concept_domain_map.get(p["concept_id"]) for p in all_progress
                   if concept_domain_map.get(p["concept_id"])}
    breadth = len(active_doms)

    # ── Consistency ──
    current_streak = streak_data.get("current", 0) if isinstance(streak_data, dict) else 0
    longest_streak = streak_data.get("longest", 0) if isinstance(streak_data, dict) else 0
    from collections import defaultdict as _dd
    day_events: dict[str, int] = _dd(int)
    month_ago = now - 30 * 86400
    for h in history:
        ts = h.get("timestamp", 0)
        if ts >= month_ago:
            day_events[time.strftime("%Y-%m-%d", time.localtime(ts))] += 1
    active_days_30 = len(day_events)
    consistency = round(active_days_30 / 30 * 100, 1)

    # ── Classify ──
    traits = []
    if avg_stm <= 2 and len(mastered) > 5:
        traits.append({"trait": "速学者", "description": "平均仅需少量会话即可掌握概念", "icon": "⚡"})
    elif avg_stm > 4:
        traits.append({"trait": "深耕者", "description": "倾向于多次练习确保深度理解", "icon": "🔬"})
    if breadth >= 5:
        traits.append({"trait": "通才型", "description": f"已探索{breadth}个领域", "icon": "🌍"})
    elif breadth <= 2 and len(mastered) > 10:
        traits.append({"trait": "专家型", "description": "专注深耕少数领域", "icon": "🎯"})
    if consistency >= 70:
        traits.append({"trait": "自律型", "description": f"30天内{active_days_30}天在学", "icon": "📅"})
    elif consistency < 30 and total_events > 20:
        traits.append({"trait": "冲刺型", "description": "集中时间大量学习", "icon": "🏃"})
    tp_map = {"morning": ("晨型学习者", "🌅"), "evening": ("夜型学习者", "🌙"), "night": ("夜猫子", "🦉")}
    if time_pref in tp_map:
        t, ic = tp_map[time_pref]
        traits.append({"trait": t, "description": f"高峰时段 {peak_hour}:00", "icon": ic})

    style = ("新手" if not mastered else "全能学者" if breadth >= 5 and consistency >= 50 else
             "快速掌握者" if avg_stm <= 2 else "坚持不懈者" if consistency >= 70 else
             "知识探险家" if breadth >= 4 else "探索者")

    return {
        "style": style, "traits": traits,
        "metrics": {
            "total_mastered": len(mastered), "total_sessions": total_sessions,
            "avg_sessions_to_master": round(avg_stm, 1), "active_domains": breadth,
            "consistency_pct": consistency, "active_days_30d": active_days_30,
            "peak_hour": peak_hour, "time_preference": time_pref,
            "current_streak": current_streak, "longest_streak": longest_streak,
        },
        "time_distribution": {"morning": morning, "afternoon": afternoon, "evening": evening, "night": night},
    }
