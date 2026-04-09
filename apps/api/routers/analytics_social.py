"""Analytics Social API — V2.8 leaderboard and peer comparison.

Extracted from analytics_insights.py (V2.10 code health) to keep router files under 800 lines.

Provides:
- Leaderboard with context-aware mock peers (V2.8)
- Peer comparison percentiles (V2.8)
"""

import hashlib
import time

from fastapi import APIRouter, Query
from utils.logger import get_logger

from db.sqlite_client import get_all_progress, get_history, get_streak
from routers.analytics_utils import load_seed_metadata

logger = get_logger(__name__)

router = APIRouter()


# ── V2.8: Social & Collaborative Learning ────────────────


@router.get("/analytics/leaderboard")
async def leaderboard(
    limit: int = Query(20, ge=5, le=100),
    sort_by: str = Query("mastered", description="Sort key: mastered | efficiency | streak | score"),
):
    """Real leaderboard using actual user progress data.

    Aggregates learning metrics across all domains into a ranking system.
    In single-user mode, generates context-aware mock peers based on real user stats.
    """
    progress = get_all_progress()
    streak_data = get_streak()
    history = get_history(limit=10000)

    concept_domain_map, _, domain_map = load_seed_metadata()

    # Calculate real user stats
    mastered_count = sum(1 for p in progress if p.get("status") == "mastered")
    learning_count = sum(1 for p in progress if p.get("status") == "learning")
    total_sessions = sum(p.get("sessions", 0) for p in progress)
    total_score = sum(p.get("mastery_score", 0) for p in progress if p.get("sessions", 0) > 0)
    avg_efficiency = round(total_score / max(1, total_sessions), 1)
    current_streak = streak_data.get("current", 0) if isinstance(streak_data, dict) else 0
    longest_streak = streak_data.get("longest", 0) if isinstance(streak_data, dict) else 0

    # Domains started
    user_domains: set[str] = set()
    for p in progress:
        did = concept_domain_map.get(p["concept_id"])
        if did and p.get("status") in ("learning", "mastered"):
            user_domains.add(did)

    user_composite = round(mastered_count * 3 + current_streak * 2 + avg_efficiency * 0.5 + len(user_domains) * 5, 1)

    user_entry = {
        "name": "\u6211",
        "is_self": True,
        "mastered": mastered_count,
        "learning": learning_count,
        "domains_started": len(user_domains),
        "avg_efficiency": avg_efficiency,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "composite_score": user_composite,
        "total_sessions": total_sessions,
    }

    # Generate context-aware mock peers
    today = time.strftime("%Y-%m-%d")
    peer_names = [
        "\u77e5\u8bc6\u63a2\u7d22\u8005", "\u56fe\u8c31\u4e4b\u661f", "\u6c42\u77e5\u82e5\u6e34", "\u82cf\u683c\u62c9\u5e95\u95e8\u5f92",
        "\u8d39\u66fc\u5b66\u4e60\u6cd5\u5927\u5e08", "\u6982\u5ff5\u8fde\u63a5\u8005", "\u77e5\u8bc6\u5b87\u5b99\u65c5\u4eba", "\u6df1\u5ea6\u5b66\u4e60\u8005",
        "\u597d\u5947\u5fc3\u9a71\u52a8", "\u901a\u8bc6\u8fbe\u4eba", "\u4ea4\u53c9\u5b66\u79d1\u7231\u597d\u8005", "\u6c38\u4e0d\u6b62\u6b65",
        "\u903b\u8f91\u63a8\u7406\u738b", "\u5b66\u6d77\u65e0\u6daf", "\u77e5\u8bc6\u5efa\u7b51\u5e08", "\u8ba4\u77e5\u63a2\u9669\u5bb6",
        "\u8de8\u57df\u5927\u5e08", "\u6301\u7eed\u8fdb\u6b65\u8005", "\u7cfb\u7edf\u601d\u8003\u8005",
    ]

    peers = []
    for i, name in enumerate(peer_names):
        seed_str = f"{name}-{today}-{i}"
        seed_hash = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)

        base_mastered = max(1, mastered_count)
        peer_mastered = max(0, int(base_mastered * (0.3 + (seed_hash % 140) / 100)))
        peer_streak = max(0, int(current_streak * (0.2 + (seed_hash % 180) / 100)))
        peer_eff = max(5, round(avg_efficiency * (0.5 + (seed_hash % 100) / 100), 1))
        peer_domains = max(1, int(len(user_domains) * (0.3 + (seed_hash % 150) / 100)))
        peer_composite = round(peer_mastered * 3 + peer_streak * 2 + peer_eff * 0.5 + peer_domains * 5, 1)

        peers.append({
            "name": name,
            "is_self": False,
            "mastered": peer_mastered,
            "learning": max(0, peer_mastered // 2),
            "domains_started": peer_domains,
            "avg_efficiency": peer_eff,
            "current_streak": peer_streak,
            "longest_streak": max(peer_streak, peer_streak + (seed_hash % 5)),
            "composite_score": peer_composite,
            "total_sessions": max(1, peer_mastered * 2 + (seed_hash % 10)),
        })

    all_entries = [user_entry] + peers
    sort_key_map = {
        "mastered": lambda x: x["mastered"],
        "efficiency": lambda x: x["avg_efficiency"],
        "streak": lambda x: x["current_streak"],
        "score": lambda x: x["composite_score"],
    }
    sort_fn = sort_key_map.get(sort_by, sort_key_map["mastered"])
    all_entries.sort(key=sort_fn, reverse=True)

    for i, entry in enumerate(all_entries):
        entry["rank"] = i + 1

    user_rank = next((e["rank"] for e in all_entries if e["is_self"]), 0)

    return {
        "leaderboard": all_entries[:limit],
        "user_rank": user_rank,
        "total_participants": len(all_entries),
        "sort_by": sort_by,
        "user_stats": user_entry,
    }


@router.get("/analytics/peer-comparison")
async def peer_comparison():
    """Compare user's performance against aggregate peer metrics.

    Provides percentile-based comparison across multiple dimensions.
    """
    progress = get_all_progress()
    streak_data = get_streak()
    history = get_history(limit=10000)

    concept_domain_map, _, _ = load_seed_metadata()

    # Real user stats
    mastered = sum(1 for p in progress if p.get("status") == "mastered")
    total_sessions = sum(p.get("sessions", 0) for p in progress)
    scores = [p.get("mastery_score", 0) for p in progress if p.get("sessions", 0) > 0]
    avg_score = round(sum(scores) / max(1, len(scores)), 1)
    current_streak = streak_data.get("current", 0) if isinstance(streak_data, dict) else 0

    # Domains
    user_domains = set()
    for p in progress:
        did = concept_domain_map.get(p["concept_id"])
        if did and p.get("status") in ("learning", "mastered"):
            user_domains.add(did)

    # Estimate learning speed (concepts per week from history)
    if history:
        first_ts = min(e.get("timestamp", 0) for e in history)
        weeks = max(1, (time.time() - first_ts) / (7 * 86400))
        learn_speed = round(mastered / weeks, 1)
    else:
        learn_speed = 0

    # Simulated percentile calculations based on reasonable distributions
    peer_count = 50
    percentiles = {
        "mastery_speed": min(99, max(1, int(min(learn_speed / 5.0, 1.0) * 80 + 10))),
        "streak_consistency": min(99, max(1, int(min(current_streak / 14.0, 1.0) * 75 + 15))),
        "avg_score": min(99, max(1, int(min(avg_score / 85.0, 1.0) * 70 + 20))),
        "breadth": min(99, max(1, int(min(len(user_domains) / 8.0, 1.0) * 80 + 10))),
    }

    return {
        "user": {
            "mastered": mastered,
            "avg_score": avg_score,
            "current_streak": current_streak,
            "domains_started": len(user_domains),
            "learn_speed_per_week": learn_speed,
            "total_sessions": total_sessions,
        },
        "percentiles": percentiles,
        "summary": {
            "overall_percentile": round(sum(percentiles.values()) / len(percentiles)),
            "strongest": max(percentiles, key=percentiles.get),
            "growth_area": min(percentiles, key=percentiles.get),
        },
        "peer_count": peer_count,
    }
