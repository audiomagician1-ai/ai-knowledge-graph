"""Onboarding API — intelligent first-visit domain recommendations + domain previews.

V3.0: Help new users discover the best starting point based on domain characteristics.

Provides:
- GET /onboarding/recommended-start: ranked domain recommendations for new users
- GET /onboarding/domain-preview/{domain_id}: entry concepts + difficulty + time estimate
"""

import json
import os
import sys
from collections import Counter

from fastapi import APIRouter, HTTPException, Response
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


# ── Seed data helpers ─────────────────────────────────────

def _data_root() -> str:
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, "seed_data")
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        "data", "seed",
    )


_domains_cache: list | None = None
_seed_cache: dict[str, dict] = {}


def _load_domains() -> list[dict]:
    global _domains_cache
    if _domains_cache is not None:
        return _domains_cache
    path = os.path.join(_data_root(), "domains.json")
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        _domains_cache = raw.get("domains", raw) if isinstance(raw, dict) else raw
    else:
        _domains_cache = []
    return _domains_cache


def _load_seed(domain_id: str) -> dict:
    if domain_id in _seed_cache:
        return _seed_cache[domain_id]
    path = os.path.join(_data_root(), domain_id, "seed_graph.json")
    if not os.path.isfile(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    _seed_cache[domain_id] = data
    return data


# ── GET /onboarding/recommended-start ─────────────────────

@router.get("/onboarding/recommended-start")
async def recommended_start(response: Response):
    """Recommend best starting domains for new users.

    Scoring: beginner-friendliness (low avg difficulty), breadth (concept count),
    accessibility (low prerequisite density), estimated time to first milestone.
    """
    domains = _load_domains()
    results = []

    for d in domains:
        did = d["id"]
        seed = _load_seed(did)
        concepts = seed.get("concepts", [])
        edges = seed.get("edges", [])
        if not concepts:
            continue

        total = len(concepts)
        difficulties = [c.get("difficulty", 5) for c in concepts]
        avg_diff = sum(difficulties) / total
        entry_count = 0
        target_ids = {e.get("target_id") or e.get("target", "") for e in edges}
        for c in concepts:
            if c["id"] not in target_ids:
                entry_count += 1
        entry_ratio = entry_count / total if total else 0

        # Prerequisite density = edges / concepts
        prereq_density = len(edges) / total if total else 0

        # Estimated minutes for entry concepts
        entry_concepts = [c for c in concepts if c["id"] not in target_ids]
        est_first_hour = sum(c.get("estimated_minutes", 15) for c in entry_concepts[:5])

        # Beginner-friendliness score (0-100)
        diff_score = max(0, 100 - (avg_diff - 1) * 11)  # diff 1→100, 10→1
        entry_score = min(entry_ratio * 200, 40)  # more entries = easier start
        density_score = max(0, 30 - prereq_density * 10)  # fewer prereqs = better
        total_score = round(diff_score * 0.5 + entry_score + density_score, 1)

        results.append({
            "domain_id": did,
            "name": d.get("name", did),
            "icon": d.get("icon", ""),
            "color": d.get("color", "#6366f1"),
            "total_concepts": total,
            "avg_difficulty": round(avg_diff, 1),
            "entry_concepts": entry_count,
            "est_first_session_min": est_first_hour,
            "beginner_score": min(total_score, 100),
            "reason": _recommend_reason(avg_diff, entry_count, total),
        })

    results.sort(key=lambda x: x["beginner_score"], reverse=True)
    response.headers["Cache-Control"] = "public, max-age=3600, stale-while-revalidate=86400"
    return {"recommendations": results[:12], "total_domains": len(results)}


def _recommend_reason(avg_diff: float, entry_count: int, total: int) -> str:
    if avg_diff <= 3:
        return "入门友好，概念难度较低"
    if entry_count >= 5:
        return "多个入口概念，灵活开始"
    if total <= 100:
        return "精炼领域，易于掌握全貌"
    return "丰富的知识网络"


# ── GET /onboarding/domain-preview/{domain_id} ───────────

@router.get("/onboarding/domain-preview/{domain_id}")
async def domain_preview(domain_id: str, response: Response):
    """Preview a domain for new users: entry concepts, difficulty distribution,
    subdomains, and estimated learning time."""
    seed = _load_seed(domain_id)
    if not seed:
        raise HTTPException(404, f"Domain '{domain_id}' not found")

    concepts = seed.get("concepts", [])
    edges = seed.get("edges", [])
    subdomains = seed.get("subdomains", [])

    if not concepts:
        raise HTTPException(404, f"Domain '{domain_id}' has no concepts")

    target_ids = {e.get("target_id") or e.get("target", "") for e in edges}
    entry_concepts = [
        {
            "id": c["id"],
            "name": c.get("name", c["id"]),
            "difficulty": c.get("difficulty", 5),
            "estimated_minutes": c.get("estimated_minutes", 15),
            "content_type": c.get("content_type", "concept"),
            "subdomain": c.get("subdomain_id", ""),
        }
        for c in concepts
        if c["id"] not in target_ids
    ]
    entry_concepts.sort(key=lambda x: x["difficulty"])

    # Difficulty distribution
    diff_dist = Counter(c.get("difficulty", 5) for c in concepts)
    difficulty_distribution = [
        {"level": lvl, "count": diff_dist.get(lvl, 0)}
        for lvl in range(1, 11)
    ]

    # Subdomain summary
    sub_map: dict[str, int] = {}
    for c in concepts:
        sid = c.get("subdomain_id", "other")
        sub_map[sid] = sub_map.get(sid, 0) + 1
    subdomain_summary = []
    sub_name_map = {s["id"]: s.get("name", s["id"]) for s in subdomains}
    for sid, cnt in sorted(sub_map.items(), key=lambda x: -x[1]):
        subdomain_summary.append({
            "id": sid,
            "name": sub_name_map.get(sid, sid),
            "concept_count": cnt,
        })

    total_minutes = sum(c.get("estimated_minutes", 15) for c in concepts)

    response.headers["Cache-Control"] = "public, max-age=3600, stale-while-revalidate=86400"
    return {
        "domain_id": domain_id,
        "total_concepts": len(concepts),
        "total_edges": len(edges),
        "total_subdomains": len(subdomains),
        "entry_concepts": entry_concepts[:10],
        "difficulty_distribution": difficulty_distribution,
        "subdomain_summary": subdomain_summary,
        "estimated_total_hours": round(total_minutes / 60, 1),
        "avg_difficulty": round(
            sum(c.get("difficulty", 5) for c in concepts) / len(concepts), 1
        ),
    }