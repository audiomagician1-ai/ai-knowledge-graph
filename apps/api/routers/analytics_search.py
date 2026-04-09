"""Analytics Search API — V2.9 concept similarity, learning report, and content search.

Extracted from analytics_insights.py (V2.10 code health) to keep router files under 800 lines.

Provides:
- Concept similarity engine (V2.9)
- Comprehensive learning report (V2.9)
- Full-text RAG content search (V2.9)
"""

import time

from fastapi import APIRouter, Query
from utils.logger import get_logger

from db.sqlite_client import get_all_progress, get_history, get_streak
from routers.analytics_utils import load_seed_metadata

logger = get_logger(__name__)

router = APIRouter()


# ── V2.9: Concept Similarity Engine ─────────────────────


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
                reasons.append(f"\u5171\u4eab{shared_in}\u4e2a\u524d\u7f6e\u77e5\u8bc6")

        # Factor 2: Shared dependents (Jaccard)
        cid_out = outgoing.get(cid, set())
        if target_out and cid_out:
            shared_out = len(target_out & cid_out)
            union_out = len(target_out | cid_out)
            if shared_out > 0:
                jaccard_out = shared_out / union_out
                score += jaccard_out * 25
                reasons.append(f"\u5171\u4eab{shared_out}\u4e2a\u540e\u7eed\u6982\u5ff5")

        # Factor 3: Tag overlap
        cid_tags = meta["tags"]
        if target_tags and cid_tags:
            shared_tags = len(target_tags & cid_tags)
            if shared_tags > 0:
                score += shared_tags * 8
                reasons.append(f"{shared_tags}\u4e2a\u5171\u540c\u6807\u7b7e")

        # Factor 4: Same subdomain bonus
        if meta["subdomain"] == target["subdomain"] and meta["subdomain"]:
            score += 10
            reasons.append("\u540c\u4e00\u5b50\u9886\u57df")

        # Factor 5: Cross-domain bridge link
        if cid in cross_neighbors:
            score += 20
            reasons.append("\u8de8\u57df\u5173\u8054")

        # Factor 6: Similar difficulty (within +/-2)
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


# ── V2.9: Comprehensive Learning Report ─────────────────


@router.get("/analytics/learning-report")
async def learning_report():
    """Generate a comprehensive learning report aggregating all key metrics.

    Combines data from multiple analytics endpoints into a single
    exportable/printable summary.
    """
    progress = get_all_progress()
    history = get_history(limit=10000)
    streak_data = get_streak()
    now = time.time()

    concept_domain_map, concept_info, domain_map = load_seed_metadata()

    # Overall stats
    mastered = sum(1 for p in progress if p.get("status") == "mastered")
    learning = sum(1 for p in progress if p.get("status") == "learning")
    total_concepts = len(concept_info)
    total_sessions = sum(p.get("sessions", 0) for p in progress)
    scores = [p.get("mastery_score", 0) for p in progress if p.get("sessions", 0) > 0]
    avg_score = round(sum(scores) / max(1, len(scores)), 1)

    current_streak = streak_data.get("current", 0) if isinstance(streak_data, dict) else 0
    longest_streak = streak_data.get("longest", 0) if isinstance(streak_data, dict) else 0

    # Active days
    active_dates: set[str] = set()
    for entry in history:
        ts = entry.get("timestamp", 0)
        if now - ts < 90 * 86400:
            active_dates.add(time.strftime("%Y-%m-%d", time.localtime(ts)))

    # Domain breakdown
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

    # Strengths (top domains)
    strengths = [d for d in domain_breakdown if d["percentage"] >= 20 and d["mastered"] >= 3][:5]

    # Weaknesses (concepts with low scores + many attempts)
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

    # Recommendations
    recommendations: list[str] = []
    if mastered == 0:
        recommendations.append("\u5f00\u59cb\u4f60\u7684\u7b2c\u4e00\u4e2a\u77e5\u8bc6\u6982\u5ff5\u5b66\u4e60\uff0c\u70b9\u4eae\u56fe\u8c31\u6280\u80fd\u6811\uff01")
    elif mastered < 10:
        recommendations.append("\u7ee7\u7eed\u5b66\u4e60\u5f53\u524d\u9886\u57df\u7684\u57fa\u7840\u6982\u5ff5\uff0c\u6253\u597d\u6839\u57fa")
    if current_streak == 0:
        recommendations.append("\u4eca\u5929\u5c31\u5f00\u59cb\u5b66\u4e60\uff0c\u4fdd\u6301\u8fde\u7eed\u5b66\u4e60\u8bb0\u5f55\uff01")
    elif current_streak >= 7:
        recommendations.append(f"\u8fde\u7eed\u5b66\u4e60{current_streak}\u5929\uff0c\u592a\u68d2\u4e86\uff01\u5c1d\u8bd5\u6311\u6218\u65b0\u7684\u77e5\u8bc6\u9886\u57df")
    if len(domain_stats) <= 2 and mastered >= 5:
        recommendations.append("\u4f60\u5df2\u7ecf\u5728\u5f53\u524d\u9886\u57df\u6709\u6240\u79ef\u7d2f\uff0c\u5c1d\u8bd5\u63a2\u7d22\u8de8\u57df\u5173\u8054\u6982\u5ff5")
    if weak_concepts:
        recommendations.append(f"\u6709{len(weak_concepts)}\u4e2a\u8584\u5f31\u6982\u5ff5\u9700\u8981\u5de9\u56fa\uff0c\u5efa\u8bae\u4f18\u5148\u590d\u4e60")
    if total_sessions > 50 and avg_score < 60:
        recommendations.append("\u5b66\u4e60\u6548\u7387\u504f\u4f4e\uff0c\u5efa\u8bae\u8c03\u6574\u5b66\u4e60\u7b56\u7565\u6216\u5148\u5de9\u56fa\u524d\u7f6e\u77e5\u8bc6")

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


# ── V2.9: Full-Text RAG Content Search ──────────────────


@router.get("/analytics/content-search")
async def content_search(
    q: str = Query(..., min_length=2, max_length=200, description="Search query"),
    limit: int = Query(10, ge=1, le=50),
):
    """Full-text search across RAG knowledge documents.

    Searches document content (not just concept names) for matching terms.
    Returns ranked results with content snippets showing match context.
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
