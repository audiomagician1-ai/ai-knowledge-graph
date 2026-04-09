"""图谱引擎高级 API — V2.1+ 拓扑分析、概念对比、跨域桥接、全局统计。

Extracted from graph.py (V2.10 code health) to keep router files under 800 lines.

Provides:
- Domain topology analysis (V2.1)
- Concept context (prerequisites/dependents/related) (V2.1)
- Concept comparison (V2.1)
- Cross-domain bridge (V2.5)
- Global stats aggregation (V2.2)
"""

import json
import os
import sys

from fastapi import APIRouter, HTTPException, Query
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

DEFAULT_DOMAIN = "ai-engineering"


# ── Shared utilities (imported from graph.py module scope) ──


def _project_root() -> str:
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


def _get_seed_path(domain_id: str = DEFAULT_DOMAIN) -> str:
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, "seed_data", domain_id, "seed_graph.json")
    return os.path.join(_project_root(), "data", "seed", domain_id, "seed_graph.json")


def _get_domains_path() -> str:
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, "seed_data", "domains.json")
    return os.path.join(_project_root(), "data", "seed", "domains.json")


def _load_seed(domain_id: str = DEFAULT_DOMAIN) -> dict:
    path = _get_seed_path(domain_id)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"Domain '{domain_id}' seed not found")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_domains() -> list[dict]:
    path = _get_domains_path()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("domains", [])
    return []


def _get_cross_links_path() -> str:
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, "seed_data", "cross_sphere_links.json")
    return os.path.join(_project_root(), "data", "seed", "cross_sphere_links.json")


def _load_cross_links() -> list[dict]:
    """Load cross-sphere links from seed data."""
    path = _get_cross_links_path()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("links", [])
    return []



@router.get("/topology/{domain_id}")
async def get_domain_topology(domain_id: str = DEFAULT_DOMAIN):
    """
    返回域的拓扑分析: 子域统计、里程碑节点、入度/出度排行、孤立节点检测。
    用于 Graph HUD 展示和学习路径优化。
    """
    seed_path = _get_seed_path(domain_id)
    if not os.path.isfile(seed_path):
        raise HTTPException(status_code=404, detail=f"Domain '{domain_id}' not found")

    seed = _load_seed(domain_id)
    concepts = seed.get("concepts", [])
    edges = seed.get("edges", [])

    # Build adjacency data
    in_degree: dict[str, int] = {}
    out_degree: dict[str, int] = {}
    for c in concepts:
        in_degree[c["id"]] = 0
        out_degree[c["id"]] = 0
    for e in edges:
        src = e.get("source_id", e.get("source", ""))
        tgt = e.get("target_id", e.get("target", ""))
        if src in out_degree:
            out_degree[src] += 1
        if tgt in in_degree:
            in_degree[tgt] += 1

    # Subdomain stats
    subdomain_stats: dict[str, dict] = {}
    for c in concepts:
        sub = c.get("subdomain_id", "other")
        if sub not in subdomain_stats:
            subdomain_stats[sub] = {"total": 0, "milestones": 0, "avg_difficulty": 0.0, "difficulties": []}
        subdomain_stats[sub]["total"] += 1
        subdomain_stats[sub]["difficulties"].append(c.get("difficulty", 5))
        if c.get("is_milestone"):
            subdomain_stats[sub]["milestones"] += 1

    for sub, stats in subdomain_stats.items():
        diffs = stats.pop("difficulties")
        stats["avg_difficulty"] = round(sum(diffs) / len(diffs), 1) if diffs else 0

    # Entry points (in_degree == 0) and terminal nodes (out_degree == 0)
    entry_points = [cid for cid, deg in in_degree.items() if deg == 0]
    terminal_nodes = [cid for cid, deg in out_degree.items() if deg == 0]

    # Orphan nodes (no edges at all)
    connected_ids = set()
    for e in edges:
        connected_ids.add(e.get("source_id", e.get("source", "")))
        connected_ids.add(e.get("target_id", e.get("target", "")))
    orphans = [c["id"] for c in concepts if c["id"] not in connected_ids]

    # Top connected (highest in+out degree)
    combined = {cid: in_degree.get(cid, 0) + out_degree.get(cid, 0) for cid in in_degree}
    top_connected = sorted(combined.items(), key=lambda x: x[1], reverse=True)[:10]

    # Milestones
    milestones = [{"id": c["id"], "name": c.get("name", c["id"]), "difficulty": c.get("difficulty", 5)}
                  for c in concepts if c.get("is_milestone")]

    return {
        "domain_id": domain_id,
        "total_concepts": len(concepts),
        "total_edges": len(edges),
        "subdomains": subdomain_stats,
        "entry_points": entry_points[:20],
        "terminal_nodes": terminal_nodes[:20],
        "orphan_nodes": orphans,
        "milestones": milestones,
        "top_connected": [{"id": cid, "degree": deg} for cid, deg in top_connected],
    }


@router.get("/concepts/{concept_id}/context")
async def get_concept_context(
    concept_id: str,
    domain: str = Query(DEFAULT_DOMAIN),
):
    """
    返回概念的完整上下文：前置知识、后续解锁、同子域概念列表。
    用于 ChatPanel idle 视图的导航增强。
    """
    seed = _load_seed(domain)
    concept_map = {c["id"]: c for c in seed["concepts"]}

    if concept_id not in concept_map:
        raise HTTPException(status_code=404, detail=f"概念不存在: {concept_id}")

    current = concept_map[concept_id]
    edges = seed.get("edges", [])

    # Prerequisites: edges where target = concept_id, type = prerequisite → source is prereq
    prerequisites = []
    for e in edges:
        src = e.get("source_id", e.get("source", ""))
        tgt = e.get("target_id", e.get("target", ""))
        if tgt == concept_id and e.get("relation_type") == "prerequisite" and src in concept_map:
            c = concept_map[src]
            prerequisites.append({
                "id": c["id"],
                "name": c.get("name", c["id"]),
                "difficulty": c.get("difficulty", 5),
                "subdomain_id": c.get("subdomain_id", ""),
            })

    # Dependents: edges where source = concept_id, type = prerequisite → target depends on this
    dependents = []
    for e in edges:
        src = e.get("source_id", e.get("source", ""))
        tgt = e.get("target_id", e.get("target", ""))
        if src == concept_id and e.get("relation_type") == "prerequisite" and tgt in concept_map:
            c = concept_map[tgt]
            dependents.append({
                "id": c["id"],
                "name": c.get("name", c["id"]),
                "difficulty": c.get("difficulty", 5),
                "subdomain_id": c.get("subdomain_id", ""),
            })

    # Related (non-prerequisite edges)
    related = []
    for e in edges:
        src = e.get("source_id", e.get("source", ""))
        tgt = e.get("target_id", e.get("target", ""))
        if e.get("relation_type") != "prerequisite":
            if src == concept_id and tgt in concept_map:
                c = concept_map[tgt]
                related.append({"id": c["id"], "name": c.get("name", c["id"]), "sub_type": e.get("sub_type", "")})
            elif tgt == concept_id and src in concept_map:
                c = concept_map[src]
                related.append({"id": c["id"], "name": c.get("name", c["id"]), "sub_type": e.get("sub_type", "")})

    # Siblings: same subdomain, sorted by difficulty
    subdomain = current.get("subdomain_id", "")
    siblings = [
        {"id": c["id"], "name": c.get("name", c["id"]), "difficulty": c.get("difficulty", 5)}
        for c in seed["concepts"]
        if c.get("subdomain_id") == subdomain and c["id"] != concept_id
    ]
    siblings.sort(key=lambda x: x["difficulty"])

    return {
        "concept_id": concept_id,
        "name": current.get("name", concept_id),
        "subdomain_id": subdomain,
        "difficulty": current.get("difficulty", 5),
        "is_milestone": current.get("is_milestone", False),
        "prerequisites": prerequisites,
        "dependents": dependents,
        "related": related[:10],
        "siblings": siblings[:20],
        "total_siblings": len(siblings) + 1,
    }


@router.get("/compare-concepts")
async def compare_concepts(
    concept_a: str = "variables",
    concept_b: str = "loops",
    domain_id: str = DEFAULT_DOMAIN,
):
    """Compare two concepts side-by-side.

    Returns: names, difficulty, prerequisites, overlap metrics, and shared connections.
    Useful for understanding relationships between two concepts.
    """
    graph_data = _load_seed(domain_id)
    if not graph_data:
        raise HTTPException(status_code=404, detail=f"Domain not found: {domain_id}")

    nodes_by_id = {n["id"]: n for n in graph_data.get("concepts", graph_data.get("nodes", []))}

    node_a = nodes_by_id.get(concept_a)
    node_b = nodes_by_id.get(concept_b)

    if not node_a:
        raise HTTPException(status_code=404, detail=f"Concept not found: {concept_a}")
    if not node_b:
        raise HTTPException(status_code=404, detail=f"Concept not found: {concept_b}")

    # Gather connections for each concept
    edges = graph_data.get("edges", [])

    def get_connections(concept_id: str) -> set:
        connected = set()
        for e in edges:
            src = e.get("source_id", e.get("source", ""))
            tgt = e.get("target_id", e.get("target", ""))
            if src == concept_id:
                connected.add(tgt)
            elif tgt == concept_id:
                connected.add(src)
        return connected

    conn_a = get_connections(concept_a)
    conn_b = get_connections(concept_b)
    shared = conn_a & conn_b

    # Check if directly connected
    directly_connected = concept_b in conn_a or concept_a in conn_b

    # Get prereqs
    prereqs_a = [e.get("source_id", e.get("source", "")) for e in edges if e.get("target_id", e.get("target", "")) == concept_a and e.get("relation_type") == "prerequisite"]
    prereqs_b = [e.get("source_id", e.get("source", "")) for e in edges if e.get("target_id", e.get("target", "")) == concept_b and e.get("relation_type") == "prerequisite"]
    shared_prereqs = set(prereqs_a) & set(prereqs_b)

    return {
        "concept_a": {
            "id": concept_a,
            "name": node_a.get("name", concept_a),
            "difficulty": node_a.get("difficulty", 5),
            "subdomain": node_a.get("subdomain_id", ""),
            "is_milestone": node_a.get("is_milestone", False),
            "connections": len(conn_a),
            "prerequisites": prereqs_a,
        },
        "concept_b": {
            "id": concept_b,
            "name": node_b.get("name", concept_b),
            "difficulty": node_b.get("difficulty", 5),
            "subdomain": node_b.get("subdomain_id", ""),
            "is_milestone": node_b.get("is_milestone", False),
            "connections": len(conn_b),
            "prerequisites": prereqs_b,
        },
        "comparison": {
            "directly_connected": directly_connected,
            "shared_connections": list(shared)[:20],
            "shared_connection_count": len(shared),
            "shared_prerequisites": list(shared_prereqs),
            "same_subdomain": node_a.get("subdomain_id") == node_b.get("subdomain_id"),
            "difficulty_gap": abs(node_a.get("difficulty", 5) - node_b.get("difficulty", 5)),
            "similarity_score": round(
                len(shared) / max(1, len(conn_a | conn_b)) * 100, 1
            ),
        },
    }


# ── V2.5: Cross-Domain Bridge ───────────────────────────


@router.get("/cross-domain-bridge/{concept_id}")
async def cross_domain_bridge(
    concept_id: str,
    domain: str = Query(DEFAULT_DOMAIN),
):
    """Find related concepts in OTHER domains via cross-sphere links.

    For a given concept, returns concepts from other knowledge spheres
    that are connected — enabling cross-domain exploration.
    """
    cross_links = _load_cross_links()

    # Find all cross-links involving this concept
    bridges = []
    for lk in cross_links:
        src_id = lk.get("source_id", "")
        tgt_id = lk.get("target_id", "")
        src_domain = lk.get("source_domain", "")
        tgt_domain = lk.get("target_domain", "")
        relation = lk.get("relation_type", lk.get("type", "related"))
        rationale = lk.get("rationale", lk.get("description", ""))

        matched_side = None
        other_concept_id = ""
        other_domain_id = ""

        if src_id == concept_id:
            matched_side = "source"
            other_concept_id = tgt_id
            other_domain_id = tgt_domain
        elif tgt_id == concept_id:
            matched_side = "target"
            other_concept_id = src_id
            other_domain_id = src_domain

        if not matched_side:
            continue

        # Try to load the other concept's metadata
        other_name = other_concept_id
        other_difficulty = 5
        other_subdomain = ""
        try:
            other_seed = _load_seed(other_domain_id)
            for c in other_seed.get("concepts", []):
                if c["id"] == other_concept_id:
                    other_name = c.get("name", other_concept_id)
                    other_difficulty = c.get("difficulty", 5)
                    other_subdomain = c.get("subdomain_id", "")
                    break
        except Exception:
            pass

        # Get the other domain's display name
        other_domain_name = other_domain_id.replace("-", " ").title()
        try:
            domains_path = _get_domains_path()
            with open(domains_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            dl = raw.get("domains", raw) if isinstance(raw, dict) else raw
            for d in dl:
                if d.get("id") == other_domain_id:
                    other_domain_name = d.get("name", other_domain_name)
                    break
        except Exception:
            pass

        bridges.append({
            "concept_id": other_concept_id,
            "concept_name": other_name,
            "domain_id": other_domain_id,
            "domain_name": other_domain_name,
            "subdomain_id": other_subdomain,
            "difficulty": other_difficulty,
            "relation_type": relation,
            "rationale": rationale,
            "direction": "outgoing" if matched_side == "source" else "incoming",
        })

    # Sort by domain for grouping
    bridges.sort(key=lambda b: (b["domain_id"], b["concept_name"]))

    # Group by domain
    domain_groups: dict[str, list] = {}
    for b in bridges:
        did = b["domain_id"]
        if did not in domain_groups:
            domain_groups[did] = []
        domain_groups[did].append(b)

    return {
        "concept_id": concept_id,
        "source_domain": domain,
        "bridges": bridges,
        "total": len(bridges),
        "domains_connected": list(domain_groups.keys()),
        "by_domain": domain_groups,
    }
@router.get("/stats/global")
async def get_global_stats():
    """Aggregated cross-domain statistics for Dashboard radar/overview."""
    domains_path = _get_domains_path()
    if not os.path.isfile(domains_path):
        return {"domains": [], "totals": {}}

    with open(domains_path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    domain_list = raw.get("domains", raw) if isinstance(raw, dict) else raw

    domain_stats = []
    total_concepts = 0
    total_edges = 0
    total_milestones = 0
    difficulty_sum = 0
    difficulty_count = 0

    for d in domain_list:
        did = d.get("id", "")
        try:
            seed = _load_seed(did)
        except Exception:
            continue
        concepts = seed.get("concepts", [])
        edges = seed.get("edges", [])
        nc = len(concepts)
        ne = len(edges)
        milestones = sum(1 for c in concepts if c.get("is_milestone"))
        diffs = [c.get("difficulty", 5) for c in concepts]
        avg_diff = round(sum(diffs) / max(1, len(diffs)), 1)
        subdomains = set(c.get("subdomain_id", "") for c in concepts)

        domain_stats.append({
            "id": did,
            "name": d.get("name", did),
            "icon": d.get("icon", ""),
            "color": d.get("color", "#888"),
            "concepts": nc,
            "edges": ne,
            "milestones": milestones,
            "subdomains": len(subdomains),
            "avg_difficulty": avg_diff,
        })
        total_concepts += nc
        total_edges += ne
        total_milestones += milestones
        difficulty_sum += sum(diffs)
        difficulty_count += len(diffs)

    cross_links = _load_cross_links()

    return {
        "domains": domain_stats,
        "totals": {
            "domains": len(domain_stats),
            "concepts": total_concepts,
            "edges": total_edges,
            "milestones": total_milestones,
            "cross_links": len(cross_links),
            "avg_difficulty": round(difficulty_sum / max(1, difficulty_count), 1),
        },
    }


# ── V3.0: Relationship Strength Analysis ──────────────────


@router.get("/relationship-strength/{domain_id}")
async def relationship_strength(domain_id: str):
    """Analyze edge topology and relationship strength for a domain.

    Returns: hub concepts (high connectivity), bridge concepts (cross-subdomain),
    isolated concepts (no edges), and per-subdomain density metrics.
    Useful for learning path intelligence and graph visualization emphasis.
    """
    seed = _load_seed(domain_id)
    concepts = seed.get("concepts", [])
    edges = seed.get("edges", [])

    if not concepts:
        raise HTTPException(404, f"Domain '{domain_id}' has no concepts")

    concept_map = {c["id"]: c for c in concepts}

    # Build adjacency counts
    in_degree: dict[str, int] = {}
    out_degree: dict[str, int] = {}
    for e in edges:
        src = e.get("source_id") or e.get("source", "")
        tgt = e.get("target_id") or e.get("target", "")
        out_degree[src] = out_degree.get(src, 0) + 1
        in_degree[tgt] = in_degree.get(tgt, 0) + 1

    # Hub concepts: highest total degree
    degree_list = []
    for c in concepts:
        cid = c["id"]
        total_deg = in_degree.get(cid, 0) + out_degree.get(cid, 0)
        degree_list.append({
            "id": cid,
            "name": c.get("name", cid),
            "subdomain": c.get("subdomain_id", ""),
            "in_degree": in_degree.get(cid, 0),
            "out_degree": out_degree.get(cid, 0),
            "total_degree": total_deg,
        })
    degree_list.sort(key=lambda x: x["total_degree"], reverse=True)
    hubs = degree_list[:10]

    # Isolated concepts: zero edges
    isolated = [d for d in degree_list if d["total_degree"] == 0]

    # Bridge concepts: connected to multiple subdomains
    concept_neighbors: dict[str, set[str]] = {}
    for e in edges:
        src = e.get("source_id") or e.get("source", "")
        tgt = e.get("target_id") or e.get("target", "")
        concept_neighbors.setdefault(src, set()).add(tgt)
        concept_neighbors.setdefault(tgt, set()).add(src)

    bridges = []
    for c in concepts:
        cid = c["id"]
        c_sub = c.get("subdomain_id", "")
        neighbors = concept_neighbors.get(cid, set())
        neighbor_subs = set()
        for nid in neighbors:
            nc = concept_map.get(nid)
            if nc:
                ns = nc.get("subdomain_id", "")
                if ns != c_sub:
                    neighbor_subs.add(ns)
        if neighbor_subs:
            bridges.append({
                "id": cid,
                "name": c.get("name", cid),
                "subdomain": c_sub,
                "cross_subdomains": sorted(neighbor_subs),
                "bridge_score": len(neighbor_subs),
            })
    bridges.sort(key=lambda x: x["bridge_score"], reverse=True)

    # Per-subdomain density
    sub_concepts: dict[str, int] = {}
    sub_internal_edges: dict[str, int] = {}
    for c in concepts:
        sid = c.get("subdomain_id", "other")
        sub_concepts[sid] = sub_concepts.get(sid, 0) + 1

    for e in edges:
        src = e.get("source_id") or e.get("source", "")
        tgt = e.get("target_id") or e.get("target", "")
        src_sub = concept_map.get(src, {}).get("subdomain_id", "other")
        tgt_sub = concept_map.get(tgt, {}).get("subdomain_id", "other")
        if src_sub == tgt_sub:
            sub_internal_edges[src_sub] = sub_internal_edges.get(src_sub, 0) + 1

    subdomain_density = []
    for sid, count in sorted(sub_concepts.items(), key=lambda x: -x[1]):
        internal = sub_internal_edges.get(sid, 0)
        max_edges = count * (count - 1) / 2 if count > 1 else 1
        density = round(internal / max_edges, 3) if max_edges > 0 else 0
        subdomain_density.append({
            "subdomain_id": sid,
            "concepts": count,
            "internal_edges": internal,
            "density": density,
        })

    return {
        "domain_id": domain_id,
        "total_concepts": len(concepts),
        "total_edges": len(edges),
        "hubs": hubs,
        "bridges": bridges[:10],
        "isolated": isolated,
        "subdomain_density": subdomain_density,
        "avg_degree": round(
            sum(d["total_degree"] for d in degree_list) / max(1, len(degree_list)), 2
        ),
    }


# ── V3.1: Concept Cluster Analysis ────────────────────────


@router.get("/concept-clusters/{domain_id}")
async def concept_clusters(
    domain_id: str,
    min_cluster_size: int = Query(2, ge=2, le=20),
):
    """Detect concept clusters (tightly connected groups) within a domain.

    Uses connected component analysis on the undirected graph, then computes
    per-cluster statistics: internal edge density, avg difficulty, subdomain
    composition, and gateway concepts (external connections).

    Useful for identifying natural learning modules and study groups.
    """
    seed = _load_seed(domain_id)
    concepts = seed.get("concepts", [])
    edges = seed.get("edges", [])

    if not concepts:
        raise HTTPException(404, f"Domain '{domain_id}' has no concepts")

    concept_map = {c["id"]: c for c in concepts}
    cid_set = set(concept_map.keys())

    # Build undirected adjacency
    adj: dict[str, set[str]] = {c["id"]: set() for c in concepts}
    for e in edges:
        src = e.get("source_id") or e.get("source", "")
        tgt = e.get("target_id") or e.get("target", "")
        if src in adj and tgt in adj:
            adj[src].add(tgt)
            adj[tgt].add(src)

    # BFS connected components
    visited: set[str] = set()
    components: list[set[str]] = []
    for cid in adj:
        if cid in visited:
            continue
        queue = [cid]
        comp: set[str] = set()
        while queue:
            node = queue.pop()
            if node in visited:
                continue
            visited.add(node)
            comp.add(node)
            for nb in adj[node]:
                if nb not in visited:
                    queue.append(nb)
        if len(comp) >= min_cluster_size:
            components.append(comp)

    # Build cluster details
    clusters = []
    for idx, comp in enumerate(sorted(components, key=len, reverse=True)):
        members = list(comp)
        # Internal edges
        internal_edges = 0
        for e in edges:
            src = e.get("source_id") or e.get("source", "")
            tgt = e.get("target_id") or e.get("target", "")
            if src in comp and tgt in comp:
                internal_edges += 1
        n = len(comp)
        max_edges = n * (n - 1) / 2 if n > 1 else 1
        density = round(internal_edges / max_edges, 3) if max_edges > 0 else 0

        # Difficulty stats
        diffs = [concept_map[m].get("difficulty", 5) for m in members]
        avg_diff = round(sum(diffs) / len(diffs), 1)
        min_diff = min(diffs)
        max_diff = max(diffs)

        # Subdomain composition
        sub_counts: dict[str, int] = {}
        for m in members:
            sid = concept_map[m].get("subdomain_id", "other")
            sub_counts[sid] = sub_counts.get(sid, 0) + 1
        primary_subdomain = max(sub_counts, key=sub_counts.get)

        # Gateway concepts: have edges to concepts outside this cluster
        gateways = []
        for m in members:
            external = adj[m] - comp
            if external:
                gateways.append({
                    "id": m,
                    "name": concept_map[m].get("name", m),
                    "external_connections": len(external),
                })
        gateways.sort(key=lambda g: g["external_connections"], reverse=True)

        clusters.append({
            "cluster_id": idx,
            "size": n,
            "internal_edges": internal_edges,
            "density": density,
            "avg_difficulty": avg_diff,
            "difficulty_range": [min_diff, max_diff],
            "primary_subdomain": primary_subdomain,
            "subdomain_composition": sub_counts,
            "gateways": gateways[:5],
            "concepts": [
                {
                    "id": m,
                    "name": concept_map[m].get("name", m),
                    "difficulty": concept_map[m].get("difficulty", 5),
                    "subdomain_id": concept_map[m].get("subdomain_id", ""),
                }
                for m in sorted(members)
            ],
        })

    return {
        "domain_id": domain_id,
        "total_clusters": len(clusters),
        "total_concepts_in_clusters": sum(c["size"] for c in clusters),
        "clusters": clusters,
    }

