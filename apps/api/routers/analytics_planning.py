"""Analytics Planning API — V2.6 domain recommendation, study plan, and learning journey.

Extracted from analytics.py (V2.10 code health) to keep router files under 800 lines.

Provides:
- Domain recommendation engine (V2.6)
- Personalized study plan generation (V2.6)
- Cross-domain learning journey timeline (V2.6)
"""

import time

from fastapi import APIRouter, Query
from utils.logger import get_logger

from db.sqlite_client import get_all_progress, get_history, get_streak
from routers.analytics_utils import load_seed_metadata

logger = get_logger(__name__)

router = APIRouter()


# ── Shared: Seed Data Loader ─────────────────────────────


def _load_seed_data():
    """Load domain + concept metadata from seed files.

    Returns (concept_domain_map, concept_info, domain_map, domain_concept_sets, domain_concept_counts).
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
    domain_concept_sets: dict[str, set] = {}
    domain_concept_counts: dict[str, int] = {}

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
                    domain_concept_sets.setdefault(did, set()).add(c["id"])
                    concept_info[c["id"]] = {
                        "name": c.get("name", c["id"]),
                        "difficulty": c.get("difficulty", 5),
                        "estimated_minutes": c.get("estimated_minutes", 20),
                        "subdomain_id": c.get("subdomain_id", ""),
                        "tags": c.get("tags", []),
                        "is_milestone": c.get("is_milestone", False),
                    }

    return concept_domain_map, concept_info, domain_map, domain_concept_sets, domain_concept_counts, data_root


def _load_cross_links(data_root: str) -> list[dict]:
    """Load cross-sphere links from seed data."""
    import json as _json, os

    cross_links_path = os.path.join(data_root, "cross_sphere_links.json")
    if os.path.isfile(cross_links_path):
        with open(cross_links_path, "r", encoding="utf-8") as f:
            cl_data = _json.load(f)
        return cl_data.get("links", [])
    return []


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
    import json as _json, os

    progress = get_all_progress()
    concept_domain_map, concept_info, domain_map, domain_concept_sets, domain_concept_counts, data_root = _load_seed_data()

    # Identify active vs undiscovered domains
    active_domains: dict[str, dict] = {}  # domain_id -> {mastered, learning, total}
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
    cross_links = _load_cross_links(data_root)

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
            reasons.append(f"\u4e0e{len(linking_domains)}\u4e2a\u5df2\u5b66\u57df\u6709{link_count}\u6761\u77e5\u8bc6\u5173\u8054")

        # Difficulty match: prefer domains with avg difficulty close to user's active domains
        target_info = domain_map.get(target_did, {})
        target_concepts = domain_concept_counts.get(target_did, 0)
        target_avg_diff = 5.0
        target_seed_path = os.path.join(data_root, target_did, "seed_graph.json")
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
                reasons.append(f"\u7cbe\u54c1\u5c0f\u57df({target_concepts}\u6982\u5ff5)\uff0c\u6613\u4e8e\u5feb\u901f\u638c\u63e1")

        # Popular domain bonus
        sort_order = target_info.get("sort_order", 99)
        if sort_order <= 10:
            score += 2.0
            reasons.append("\u70ed\u95e8\u6838\u5fc3\u9886\u57df")

        if not reasons:
            reasons.append("\u62d3\u5c55\u77e5\u8bc6\u9762\u7684\u5168\u65b0\u9886\u57df")

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
    progress = get_all_progress()
    concept_domain_map, concept_info, domain_map, _, _, _ = _load_seed_data()
    now = time.time()

    # Categorize progress
    mastered_ids = {p["concept_id"] for p in progress if p.get("status") == "mastered"}
    learning_ids = {p["concept_id"] for p in progress if p.get("status") == "learning"}

    # Simulate FSRS due items (concepts with mastery_score < 90 that were assessed >24h ago)
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
    progress = get_all_progress()
    history = get_history(limit=10000)
    streak_data = get_streak()

    concept_domain_map, concept_info, domain_map, _, domain_concept_counts, _ = _load_seed_data()

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
                event["badge"] = "\U0001f3c6"

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
                            "badge": "\U0001f31f" if pct == 100 else "\u2b50" if pct >= 75 else "\U0001f4c8",
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


# ── V3.3: Next Milestones ─────────────────────────────────


@router.get("/analytics/next-milestones")
async def next_milestones(
    limit: int = Query(10, ge=1, le=30),
):
    """Identify the closest upcoming milestones across all domains.

    Milestones include:
    - Domain completion thresholds (25%/50%/75%/100%)
    - Total concept count milestones (every 50 mastered)
    - Streak milestones (7/14/30/60/90/180/365 days)

    Returns a list of upcoming milestones sorted by closeness.
    """
    progress = get_all_progress()
    streak = get_streak()
    concept_domain_map, concept_info, domain_map = load_seed_metadata()

    domain_mastered: dict[str, int] = {}
    domain_total: dict[str, int] = {}
    for cid in concept_info:
        did = concept_domain_map.get(cid, "")
        if did:
            domain_total[did] = domain_total.get(did, 0) + 1

    for p in progress:
        if p.get("status") == "mastered":
            did = concept_domain_map.get(p["concept_id"], "")
            if did:
                domain_mastered[did] = domain_mastered.get(did, 0) + 1

    milestones: list[dict] = []

    # Domain percentage milestones
    for did, total in domain_total.items():
        mastered = domain_mastered.get(did, 0)
        dname = domain_map.get(did, {}).get("name", did)
        for threshold in [25, 50, 75, 100]:
            needed = int(total * threshold / 100)
            if needed > 0 and mastered < needed:
                milestones.append({
                    "type": "domain_pct",
                    "label": f"{dname} {threshold}%",
                    "domain_id": did,
                    "current": mastered,
                    "target": needed,
                    "remaining": needed - mastered,
                    "progress_pct": round(mastered / needed * 100, 1),
                    "badge": "🌟" if threshold == 100 else "⭐",
                })
                break

    # Total concept milestones
    total_mastered = sum(domain_mastered.values())
    next_50 = ((total_mastered // 50) + 1) * 50
    milestones.append({
        "type": "total_concepts",
        "label": f"掌握 {next_50} 个概念",
        "current": total_mastered,
        "target": next_50,
        "remaining": next_50 - total_mastered,
        "progress_pct": round(total_mastered / max(1, next_50) * 100, 1),
        "badge": "🎯",
    })

    # Streak milestones
    cur_streak = streak.get("current", 0) if isinstance(streak, dict) else 0
    for st in [7, 14, 30, 60, 90, 180, 365]:
        if cur_streak < st:
            milestones.append({
                "type": "streak", "label": f"连续学习 {st} 天",
                "current": cur_streak, "target": st,
                "remaining": st - cur_streak,
                "progress_pct": round(cur_streak / st * 100, 1),
                "badge": "🔥",
            })
            break

    milestones.sort(key=lambda m: m["remaining"])
    return {"milestones": milestones[:limit], "total": len(milestones)}