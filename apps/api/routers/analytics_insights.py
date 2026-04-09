"""Analytics Insights API — V2.7+ Smart analytics, engagement, and social features.

Extracted from analytics.py (V2.9 code health) to keep router files < 800 lines.

Provides:
- Weak concept detection (V2.7)
- Learning efficiency analysis (V2.7)
- Difficulty calibration (V2.7)
- Leaderboard with mock peers (V2.8)
- Peer comparison percentiles (V2.8)
- Comprehensive learning report (V2.9)
- Concept similarity engine (V2.9)
"""

import hashlib
import math
import time

from fastapi import APIRouter, Query
from utils.logger import get_logger

from db.sqlite_client import get_all_progress, get_history, get_streak

logger = get_logger(__name__)

router = APIRouter()


# ── Shared Helpers ────────────────────────────────────────


def _load_seed_metadata() -> tuple[dict[str, str], dict[str, dict], dict[str, dict]]:
    """Load domain/concept metadata from seed files.

    Returns (concept_domain_map, concept_info, domain_map).
    """
    import json as _json, os, sys

    if getattr(sys, "frozen", False):
        data_root = os.path.join(sys._MEIPASS, "seed_data")
    else:
        data_root = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "data", "seed",
        )

    concept_domain_map: dict[str, str] = {}
    concept_info: dict[str, dict] = {}
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
                for c in seed.get("concepts", []):
                    concept_domain_map[c["id"]] = did
                    concept_info[c["id"]] = {
                        "name": c.get("name", c["id"]),
                        "difficulty": c.get("difficulty", 5),
                        "subdomain": c.get("subdomain_id", ""),
                        "tags": c.get("tags", []),
                    }

    return concept_domain_map, concept_info, domain_map


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

    concept_domain_map, concept_info, domain_map = _load_seed_metadata()

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

    concept_domain_map, _, domain_map = _load_seed_metadata()

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
        "name": "我",
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
        "知识探索者", "图谱之星", "求知若渴", "苏格拉底门徒",
        "费曼学习法大师", "概念连接者", "知识宇宙旅人", "深度学习者",
        "好奇心驱动", "通识达人", "交叉学科爱好者", "永不止步",
        "逻辑推理王", "学海无涯", "知识建筑师", "认知探险家",
        "跨域大师", "持续进步者", "系统思考者",
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
    now = time.time()

    mastered = sum(1 for p in progress if p.get("status") == "mastered")
    learning = sum(1 for p in progress if p.get("status") == "learning")
    scores = [p.get("mastery_score", 0) for p in progress if p.get("sessions", 0) > 0]
    avg_score = round(sum(scores) / max(1, len(scores)), 1)
    current_streak = streak_data.get("current", 0) if isinstance(streak_data, dict) else 0

    # Active days (from history, last 90 days)
    active_dates: set[str] = set()
    for entry in history:
        ts = entry.get("timestamp", 0)
        if now - ts < 90 * 86400:
            active_dates.add(time.strftime("%Y-%m-%d", time.localtime(ts)))
    active_days = max(1, len(active_dates))
    mastery_speed = round(mastered / active_days, 2)

    today = time.strftime("%Y-%m-%d")
    peer_count = 50

    peer_mastery_speeds = []
    peer_streaks = []
    peer_scores = []
    peer_mastered_counts = []

    for i in range(peer_count):
        seed_str = f"peer-{today}-{i}"
        h = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
        peer_mastery_speeds.append(round(mastery_speed * (0.2 + (h % 200) / 100), 2))
        peer_streaks.append(max(0, int(current_streak * (0.1 + (h % 200) / 100))))
        peer_scores.append(max(20, round(avg_score * (0.4 + (h % 120) / 100), 1)))
        peer_mastered_counts.append(max(0, int(mastered * (0.2 + (h % 180) / 100))))

    def _percentile(user_val: float, peer_vals: list[float]) -> int:
        below = sum(1 for v in peer_vals if v < user_val)
        return min(99, max(1, round(below / max(1, len(peer_vals)) * 100)))

    return {
        "user": {
            "mastered": mastered,
            "learning": learning,
            "avg_score": avg_score,
            "current_streak": current_streak,
            "active_days_90d": len(active_dates),
            "mastery_speed": mastery_speed,
        },
        "percentiles": {
            "mastery_speed": _percentile(mastery_speed, peer_mastery_speeds),
            "streak": _percentile(current_streak, peer_streaks),
            "avg_score": _percentile(avg_score, peer_scores),
            "total_mastered": _percentile(mastered, peer_mastered_counts),
        },
        "comparison_labels": {
            "mastery_speed": "学习速度 (概念/天)",
            "streak": "连续学习天数",
            "avg_score": "平均评估分数",
            "total_mastered": "已掌握概念数",
        },
        "peer_count": peer_count,
    }


# ── V2.9: Advanced Content Intelligence ──────────────────


@router.get("/analytics/concept-similarity/{concept_id}")
async def concept_similarity(
    concept_id: str,
    limit: int = Query(10, ge=1, le=30),
):
    """Find similar concepts across all domains using graph topology + tag overlap.

    Similarity factors:
    - Shared prerequisites (Jaccard index on incoming edges)
    - Shared dependents (Jaccard index on outgoing edges)
    - Tag overlap (exact tag intersection)
    - Same subdomain bonus
    - Cross-domain bridge link bonus

    Returns ranked list of similar concepts with similarity scores and reasons.
    """
    import json as _json, os, sys

    if getattr(sys, "frozen", False):
        data_root = os.path.join(sys._MEIPASS, "seed_data")
    else:
        data_root = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "data", "seed",
        )

    # Load all seed graphs to build a global edge map
    domains_path = os.path.join(data_root, "domains.json")
    if not os.path.isfile(domains_path):
        return {"concept_id": concept_id, "similar": [], "total": 0}

    with open(domains_path, "r", encoding="utf-8") as f:
        raw = _json.load(f)
    domain_list = raw.get("domains", raw) if isinstance(raw, dict) else raw

    # Global concept info + edge maps
    concept_meta: dict[str, dict] = {}  # id -> {name, domain_id, subdomain, tags, difficulty}
    incoming: dict[str, set[str]] = {}  # concept -> set of prerequisite concepts
    outgoing: dict[str, set[str]] = {}  # concept -> set of dependent concepts
    target_domain = ""

    for d in domain_list:
        did = d["id"]
        seed_path = os.path.join(data_root, did, "seed_graph.json")
        if not os.path.isfile(seed_path):
            continue
        with open(seed_path, "r", encoding="utf-8") as f:
            seed = _json.load(f)

        for c in seed.get("concepts", []):
            cid = c["id"]
            concept_meta[cid] = {
                "name": c.get("name", cid),
                "domain_id": did,
                "domain_name": d.get("name", did),
                "subdomain": c.get("subdomain_id", ""),
                "tags": set(c.get("tags", [])),
                "difficulty": c.get("difficulty", 5),
            }
            if cid == concept_id:
                target_domain = did

        for e in seed.get("edges", []):
            src = e.get("source", "")
            tgt = e.get("target", "")
            if src and tgt:
                outgoing.setdefault(src, set()).add(tgt)
                incoming.setdefault(tgt, set()).add(src)

    # Also check cross-domain links
    cross_path = os.path.join(data_root, "cross_sphere_links.json")
    cross_neighbors: set[str] = set()
    if os.path.isfile(cross_path):
        with open(cross_path, "r", encoding="utf-8") as f:
            cross_data = _json.load(f)
        cross_links = cross_data.get("links", []) if isinstance(cross_data, dict) else cross_data
        for link in cross_links:
            if not isinstance(link, dict):
                continue
            src = link.get("source_id", "")
            tgt = link.get("target_id", "")
            if src == concept_id:
                cross_neighbors.add(tgt)
            elif tgt == concept_id:
                cross_neighbors.add(src)

    if concept_id not in concept_meta:
        return {"concept_id": concept_id, "similar": [], "total": 0, "error": "concept_not_found"}

    target = concept_meta[concept_id]
    target_in = incoming.get(concept_id, set())
    target_out = outgoing.get(concept_id, set())
    target_tags = target["tags"]

    # Compute similarity for all other concepts
    similarities: list[dict] = []

    for cid, meta in concept_meta.items():
        if cid == concept_id:
            continue

        score = 0.0
        reasons: list[str] = []

        # Factor 1: Shared prerequisites (Jaccard)
        cid_in = incoming.get(cid, set())
        if target_in and cid_in:
            shared_in = len(target_in & cid_in)
            union_in = len(target_in | cid_in)
            if shared_in > 0:
                jaccard_in = shared_in / union_in
                score += jaccard_in * 30
                reasons.append(f"共享{shared_in}个前置知识")

        # Factor 2: Shared dependents (Jaccard)
        cid_out = outgoing.get(cid, set())
        if target_out and cid_out:
            shared_out = len(target_out & cid_out)
            union_out = len(target_out | cid_out)
            if shared_out > 0:
                jaccard_out = shared_out / union_out
                score += jaccard_out * 25
                reasons.append(f"共享{shared_out}个后续概念")

        # Factor 3: Tag overlap
        cid_tags = meta["tags"]
        if target_tags and cid_tags:
            shared_tags = len(target_tags & cid_tags)
            if shared_tags > 0:
                score += shared_tags * 8
                reasons.append(f"{shared_tags}个共同标签")

        # Factor 4: Same subdomain bonus
        if meta["subdomain"] == target["subdomain"] and meta["subdomain"]:
            score += 10
            reasons.append("同一子领域")

        # Factor 5: Cross-domain bridge link
        if cid in cross_neighbors:
            score += 20
            reasons.append("跨域关联")

        # Factor 6: Similar difficulty (within ±2)
        if abs(meta["difficulty"] - target["difficulty"]) <= 2:
            score += 5

        if score > 5:
            similarities.append({
                "concept_id": cid,
                "name": meta["name"],
                "domain_id": meta["domain_id"],
                "domain_name": meta["domain_name"],
                "subdomain": meta["subdomain"],
                "difficulty": meta["difficulty"],
                "similarity_score": round(score, 1),
                "reasons": reasons,
                "is_cross_domain": meta["domain_id"] != target_domain,
            })

    similarities.sort(key=lambda x: x["similarity_score"], reverse=True)

    return {
        "concept_id": concept_id,
        "concept_name": target["name"],
        "domain_id": target_domain,
        "similar": similarities[:limit],
        "total_candidates": len(similarities),
    }


@router.get("/analytics/learning-report")
async def learning_report():
    """Generate a comprehensive learning report aggregating all key metrics.

    Combines data from multiple analytics endpoints into a single
    exportable/printable summary. Includes:
    - Overall progress stats
    - Domain-level breakdown
    - Strength and weakness analysis
    - Streak and consistency data
    - Efficiency metrics
    - Personalized recommendations
    """
    progress = get_all_progress()
    history = get_history(limit=10000)
    streak_data = get_streak()
    now = time.time()

    concept_domain_map, concept_info, domain_map = _load_seed_metadata()

    # ── Overall stats ──
    mastered = sum(1 for p in progress if p.get("status") == "mastered")
    learning = sum(1 for p in progress if p.get("status") == "learning")
    not_started = sum(1 for p in progress if p.get("status") == "not_started")
    total_concepts = len(concept_info)
    total_sessions = sum(p.get("sessions", 0) for p in progress)
    scores = [p.get("mastery_score", 0) for p in progress if p.get("sessions", 0) > 0]
    avg_score = round(sum(scores) / max(1, len(scores)), 1)

    current_streak = streak_data.get("current", 0) if isinstance(streak_data, dict) else 0
    longest_streak = streak_data.get("longest", 0) if isinstance(streak_data, dict) else 0

    # ── Active days ──
    active_dates: set[str] = set()
    for entry in history:
        ts = entry.get("timestamp", 0)
        if now - ts < 90 * 86400:
            active_dates.add(time.strftime("%Y-%m-%d", time.localtime(ts)))

    # ── Domain breakdown ──
    domain_stats: dict[str, dict] = {}
    for p in progress:
        cid = p["concept_id"]
        did = concept_domain_map.get(cid, "unknown")
        if did not in domain_stats:
            total_in_domain = sum(1 for k, v in concept_domain_map.items() if v == did)
            domain_stats[did] = {
                "domain_id": did,
                "domain_name": domain_map.get(did, {}).get("name", did),
                "mastered": 0, "learning": 0, "not_started": 0,
                "total": total_in_domain,
                "total_sessions": 0,
                "score_sum": 0, "score_count": 0,
            }
        status = p.get("status", "not_started")
        if status == "mastered":
            domain_stats[did]["mastered"] += 1
        elif status == "learning":
            domain_stats[did]["learning"] += 1
        else:
            domain_stats[did]["not_started"] += 1
        domain_stats[did]["total_sessions"] += p.get("sessions", 0)
        if p.get("sessions", 0) > 0:
            domain_stats[did]["score_sum"] += p.get("mastery_score", 0)
            domain_stats[did]["score_count"] += 1

    domain_breakdown = []
    for did, ds in domain_stats.items():
        pct = round(ds["mastered"] / max(1, ds["total"]) * 100, 1)
        avg = round(ds["score_sum"] / max(1, ds["score_count"]), 1)
        domain_breakdown.append({
            "domain_id": did,
            "domain_name": ds["domain_name"],
            "mastered": ds["mastered"],
            "learning": ds["learning"],
            "total": ds["total"],
            "percentage": pct,
            "avg_score": avg,
            "total_sessions": ds["total_sessions"],
        })
    domain_breakdown.sort(key=lambda x: x["percentage"], reverse=True)

    # ── Strengths (top domains) ──
    strengths = [d for d in domain_breakdown if d["percentage"] >= 20 and d["mastered"] >= 3][:5]

    # ── Weaknesses (concepts with low scores + many attempts) ──
    weak_concepts: list[dict] = []
    for p in progress:
        sessions = p.get("sessions", 0)
        score = p.get("mastery_score", 0)
        if sessions >= 2 and score < 60 and p.get("status") != "mastered":
            cid = p["concept_id"]
            info = concept_info.get(cid, {})
            weak_concepts.append({
                "concept_id": cid,
                "name": info.get("name", cid),
                "domain_id": concept_domain_map.get(cid, ""),
                "score": score,
                "sessions": sessions,
            })
    weak_concepts.sort(key=lambda x: x["score"])

    # ── Recommendations ──
    recommendations: list[str] = []
    if mastered == 0:
        recommendations.append("开始你的第一个知识概念学习，点亮图谱技能树！")
    elif mastered < 10:
        recommendations.append("继续学习当前领域的基础概念，打好根基")
    if current_streak == 0:
        recommendations.append("今天就开始学习，保持连续学习记录！")
    elif current_streak >= 7:
        recommendations.append(f"连续学习{current_streak}天，太棒了！尝试挑战新的知识领域")
    if len(domain_stats) <= 2 and mastered >= 5:
        recommendations.append("你已经在当前领域有所积累，尝试探索跨域关联概念")
    if weak_concepts:
        recommendations.append(f"有{len(weak_concepts)}个薄弱概念需要巩固，建议优先复习")
    if total_sessions > 50 and avg_score < 60:
        recommendations.append("学习效率偏低，建议调整学习策略或先巩固前置知识")

    return {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "overview": {
            "total_concepts_available": total_concepts,
            "mastered": mastered,
            "learning": learning,
            "not_started": total_concepts - mastered - learning,
            "completion_percentage": round(mastered / max(1, total_concepts) * 100, 1),
            "total_sessions": total_sessions,
            "avg_score": avg_score,
            "active_days_90d": len(active_dates),
        },
        "streak": {
            "current": current_streak,
            "longest": longest_streak,
        },
        "domains": domain_breakdown[:20],
        "strengths": strengths,
        "weaknesses": weak_concepts[:10],
        "recommendations": recommendations,
        "domains_started": len([d for d in domain_breakdown if d["mastered"] + d["learning"] > 0]),
        "domains_total": len(domain_map),
    }


@router.get("/analytics/content-search")
async def content_search(
    q: str = Query(..., min_length=2, max_length=200, description="Search query"),
    limit: int = Query(10, ge=1, le=50),
):
    """Full-text search across RAG knowledge documents.

    Searches document content (not just concept names) for matching terms.
    Returns ranked results with content snippets showing match context.

    This complements the existing concept name search by enabling discovery
    of concepts through their content — useful when users know a topic
    but not the exact concept name.
    """
    import json as _json, os, sys, re

    if getattr(sys, "frozen", False):
        rag_root = os.path.join(sys._MEIPASS, "rag_data")
        data_root = os.path.join(sys._MEIPASS, "seed_data")
    else:
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        rag_root = os.path.join(project_root, "data", "rag")
        data_root = os.path.join(project_root, "data", "seed")

    # Load domain names
    domain_names: dict[str, str] = {}
    domains_path = os.path.join(data_root, "domains.json")
    if os.path.isfile(domains_path):
        with open(domains_path, "r", encoding="utf-8") as f:
            raw = _json.load(f)
        domain_list = raw.get("domains", raw) if isinstance(raw, dict) else raw
        domain_names = {d["id"]: d.get("name", d["id"]) for d in domain_list}

    query_lower = q.lower()
    query_terms = query_lower.split()
    results: list[dict] = []

    # Scan RAG indices for all domains
    if not os.path.isdir(rag_root):
        return {"query": q, "results": [], "total": 0}

    for domain_dir in os.listdir(rag_root):
        domain_path = os.path.join(rag_root, domain_dir)
        if not os.path.isdir(domain_path):
            continue

        idx_path = os.path.join(domain_path, "_index.json")
        if not os.path.isfile(idx_path):
            continue

        with open(idx_path, "r", encoding="utf-8") as f:
            idx_data = _json.load(f)

        for doc in idx_data.get("documents", []):
            doc_id = doc.get("id", "")
            doc_name = doc.get("name", doc_id)
            doc_file = doc.get("file", "")

            # Quick name match check first (cheap)
            name_match = query_lower in doc_name.lower() or query_lower in doc_id.lower()

            # Content match (expensive — only read files for promising candidates)
            content_snippet = ""
            content_score = 0.0

            if name_match:
                content_score += 50  # Strong name match bonus

            # Read content for top candidates or all if query is specific enough
            filepath = os.path.join(rag_root, doc_file)
            if os.path.isfile(filepath):
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read(8000)  # Read first 8KB

                    content_lower = content.lower()

                    # Count term matches
                    term_hits = sum(1 for t in query_terms if t in content_lower)
                    if term_hits > 0:
                        content_score += term_hits * 15

                        # Extract snippet around first match
                        for t in query_terms:
                            pos = content_lower.find(t)
                            if pos >= 0:
                                start = max(0, pos - 80)
                                end = min(len(content), pos + len(t) + 120)
                                snippet = content[start:end].strip()
                                # Clean up snippet
                                snippet = re.sub(r'\s+', ' ', snippet)
                                if start > 0:
                                    snippet = "..." + snippet
                                if end < len(content):
                                    snippet = snippet + "..."
                                content_snippet = snippet
                                break

                    # Exact phrase match bonus
                    if query_lower in content_lower:
                        content_score += 30

                except Exception:
                    pass

            if content_score > 10:
                results.append({
                    "concept_id": doc_id,
                    "name": doc_name,
                    "domain_id": domain_dir,
                    "domain_name": domain_names.get(domain_dir, domain_dir),
                    "subdomain": doc.get("subdomain_id", ""),
                    "score": round(content_score, 1),
                    "snippet": content_snippet[:300] if content_snippet else "",
                    "name_match": name_match,
                })

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)

    return {
        "query": q,
        "results": results[:limit],
        "total": len(results),
    }
