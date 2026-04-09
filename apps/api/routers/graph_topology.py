"""Graph topology analysis APIs — V3.0+ relationship strength, clusters, dependency trees.

Extracted from graph_advanced.py (V3.4 code health) to keep router files under 800 lines.

Provides:
- Relationship strength analysis (V3.0: hubs, bridges, isolated, density)
- Concept cluster detection (V3.1: connected components, gateways)
- Dependency tree traversal (V3.3: BFS upstream/downstream)
"""

import json
import os
import sys

from fastapi import APIRouter, HTTPException, Query
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

# ── Shared utilities (same as graph_advanced.py) ──

from routers.graph_advanced import _load_seed, _load_domains, _get_seed_path, _get_domains_path

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


# ── V3.3: Concept Dependency Tree ─────────────────────────


@router.get("/dependency-tree/{concept_id}")
async def dependency_tree(
    concept_id: str,
    depth: int = Query(3, ge=1, le=5),
):
    """Build upstream/downstream dependency tree for a concept.

    Returns a directed tree showing:
    - Upstream: all prerequisite concepts (what you need to know first)
    - Downstream: all dependent concepts (what this concept unlocks)
    - Depth-limited BFS traversal (max 5 levels)

    Useful for understanding concept importance and learning paths.
    """
    domains_path = _get_domains_path()
    if not os.path.isfile(domains_path):
        raise HTTPException(404, "domains.json not found")

    with open(domains_path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    domain_list = raw.get("domains", raw) if isinstance(raw, dict) else raw

    # Find domain containing this concept
    target_seed = None
    for d in domain_list:
        did = d.get("id", "")
        try:
            seed = _load_seed(did)
            if any(c["id"] == concept_id for c in seed.get("concepts", [])):
                target_seed = seed
                break
        except Exception:
            continue

    if not target_seed:
        raise HTTPException(404, f"Concept '{concept_id}' not found")

    concepts = target_seed.get("concepts", [])
    edges = target_seed.get("edges", [])
    cmap = {c["id"]: c for c in concepts}

    # Build adjacency: upstream (prereqs) and downstream (dependents)
    upstream: dict[str, list[str]] = {}
    downstream: dict[str, list[str]] = {}
    for e in edges:
        src = e.get("source_id") or e.get("source", "")
        tgt = e.get("target_id") or e.get("target", "")
        downstream.setdefault(src, []).append(tgt)
        upstream.setdefault(tgt, []).append(src)

    def _bfs_tree(start: str, adj: dict[str, list[str]], max_d: int) -> list[dict]:
        visited: set[str] = {start}
        queue: list[tuple[str, int]] = [(start, 0)]
        nodes: list[dict] = []
        while queue:
            nid, d = queue.pop(0)
            if d > max_d:
                break
            c = cmap.get(nid, {})
            nodes.append({"id": nid, "name": c.get("name", nid), "depth": d,
                          "difficulty": c.get("difficulty", 5)})
            if d < max_d:
                for nb in adj.get(nid, []):
                    if nb not in visited and nb in cmap:
                        visited.add(nb)
                        queue.append((nb, d + 1))
        return nodes

    up_nodes = _bfs_tree(concept_id, upstream, depth)
    down_nodes = _bfs_tree(concept_id, downstream, depth)
    root = cmap.get(concept_id, {})

    return {
        "concept_id": concept_id,
        "concept_name": root.get("name", concept_id),
        "upstream": up_nodes[1:],  # exclude root
        "downstream": down_nodes[1:],
        "upstream_count": len(up_nodes) - 1,
        "downstream_count": len(down_nodes) - 1,
    }

