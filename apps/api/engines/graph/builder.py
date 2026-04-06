"""
知识图谱构建器
动态子图构建 + 实体对齐 + 个性化图谱生成

Phase 2 算法:
1. 个性化子图 — 基于学习进度动态生成用户可见子图
2. 实体对齐 — 利用跨域链接映射同概念在不同域的表示
3. 学习区域聚焦 — Zone of Proximal Development (ZPD) 图谱提取
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

from .pathfinder import Pathfinder, UserProgress, Concept


@dataclass
class SubgraphResult:
    """A personalized subgraph for a user."""
    nodes: list[dict]
    edges: list[dict]
    stats: dict = field(default_factory=dict)


@dataclass
class AlignedEntity:
    """A concept that exists across multiple domains."""
    canonical_id: str
    canonical_name: str
    occurrences: list[dict] = field(default_factory=list)
    description: str = ""


class GraphBuilder:
    """知识图谱构建引擎 — 基于种子数据 + 用户进度生成个性化视图。"""

    def __init__(
        self,
        concepts: list[dict],
        edges: list[dict],
        cross_links: list[dict] | None = None,
    ):
        self._concepts = {c["id"]: c for c in concepts}
        self._edges = edges
        self._cross_links = cross_links or []

        # Build pathfinder for graph algorithms
        self._pathfinder = Pathfinder(concepts, edges, cross_links)

        # Index cross links by concept
        self._cross_by_concept: dict[str, list[dict]] = defaultdict(list)
        for link in self._cross_links:
            self._cross_by_concept[link["source_id"]].append(link)
            self._cross_by_concept[link["target_id"]].append(link)

    # ── Personalized Subgraph ────────────────────────────────

    def build_personalized_subgraph(
        self,
        progress: dict[str, UserProgress],
        domain_id: str | None = None,
        include_mastered: bool = True,
        zpd_depth: int = 2,
    ) -> SubgraphResult:
        """Build a Zone of Proximal Development (ZPD) subgraph.

        The ZPD contains:
        - Mastered concepts (if include_mastered=True, for context)
        - Currently learning concepts
        - Frontier concepts (prereqs met, ready to learn)
        - Near-frontier (1-2 steps beyond frontier, for preview)

        Args:
            progress: User's concept progress dict
            domain_id: Filter to specific domain
            include_mastered: Include mastered nodes for context
            zpd_depth: How many layers beyond frontier to include
        """
        mastered = set()
        learning = set()
        for cid, p in progress.items():
            if p.status == "mastered":
                mastered.add(cid)
            elif p.status == "learning":
                learning.add(cid)

        # Filter concepts by domain
        domain_concepts = set()
        for cid, c in self._concepts.items():
            if domain_id and c.get("domain_id") != domain_id:
                continue
            domain_concepts.add(cid)

        # Build prerequisite adjacency for domain
        prereqs: dict[str, list[str]] = defaultdict(list)
        dependents: dict[str, list[str]] = defaultdict(list)
        for e in self._edges:
            src = e.get("source_id") or e.get("source", "")
            tgt = e.get("target_id") or e.get("target", "")
            rel = e.get("relation_type") or e.get("type", "related")
            if rel == "prerequisite" and src in domain_concepts and tgt in domain_concepts:
                prereqs[tgt].append(src)
                dependents[src].append(tgt)

        # Frontier: concepts whose prereqs are all mastered but not yet mastered
        frontier = set()
        for cid in domain_concepts:
            if cid in mastered:
                continue
            cid_prereqs = prereqs.get(cid, [])
            if not cid_prereqs or all(p in mastered for p in cid_prereqs):
                frontier.add(cid)

        # Near-frontier: BFS from frontier through dependents
        near_frontier = set()
        current_layer = frontier
        for _ in range(zpd_depth):
            next_layer = set()
            for cid in current_layer:
                for dep in dependents.get(cid, []):
                    if dep not in mastered and dep not in frontier and dep not in near_frontier:
                        next_layer.add(dep)
            near_frontier |= next_layer
            current_layer = next_layer

        # Assemble node set
        visible_nodes = set()
        if include_mastered:
            visible_nodes |= (mastered & domain_concepts)
        visible_nodes |= (learning & domain_concepts)
        visible_nodes |= frontier
        visible_nodes |= near_frontier

        # Build output
        nodes = []
        for cid in visible_nodes:
            c = self._concepts.get(cid)
            if not c:
                continue
            status = "mastered" if cid in mastered else (
                "learning" if cid in learning else (
                    "available" if cid in frontier else "locked"
                )
            )
            nodes.append({
                "id": cid,
                "label": c.get("name", cid),
                "domain_id": c.get("domain_id", ""),
                "subdomain_id": c.get("subdomain_id", ""),
                "difficulty": c.get("difficulty", 1),
                "status": status,
                "is_milestone": c.get("is_milestone", False),
                "zone": "mastered" if cid in mastered else (
                    "learning" if cid in learning else (
                        "frontier" if cid in frontier else "preview"
                    )
                ),
            })

        # Edges within visible set
        edges_out = []
        for e in self._edges:
            src = e.get("source_id") or e.get("source", "")
            tgt = e.get("target_id") or e.get("target", "")
            if src in visible_nodes and tgt in visible_nodes:
                edges_out.append({
                    "source": src,
                    "target": tgt,
                    "relation_type": e.get("relation_type", "related"),
                    "strength": e.get("strength", 0.5),
                })

        return SubgraphResult(
            nodes=nodes,
            edges=edges_out,
            stats={
                "total_visible": len(nodes),
                "mastered": len(mastered & domain_concepts) if include_mastered else 0,
                "learning": len(learning & domain_concepts & visible_nodes),
                "frontier": len(frontier),
                "preview": len(near_frontier),
            },
        )

    # ── Entity Alignment (Cross-Domain) ──────────────────────

    def find_aligned_entities(
        self,
        concept_id: str | None = None,
        domain_id: str | None = None,
    ) -> list[AlignedEntity]:
        """Find concepts that exist across multiple domains.

        Uses cross_sphere_links.json with relation='same_concept'.
        """
        results: list[AlignedEntity] = []

        if concept_id:
            # Find all cross-links for a specific concept
            links = self._cross_by_concept.get(concept_id, [])
            if links:
                occurrences = [{"domain": concept_id.split("/")[0] if "/" in concept_id else "",
                                "concept_id": concept_id}]
                for link in links:
                    if link.get("relation") == "same_concept":
                        other_id = (link["target_id"]
                                    if link["source_id"] == concept_id
                                    else link["source_id"])
                        other_domain = (link["target_domain"]
                                        if link["source_id"] == concept_id
                                        else link["source_domain"])
                        occurrences.append({
                            "domain": other_domain,
                            "concept_id": other_id,
                            "description": link.get("description", ""),
                        })
                if len(occurrences) > 1:
                    c = self._concepts.get(concept_id, {})
                    results.append(AlignedEntity(
                        canonical_id=concept_id,
                        canonical_name=c.get("name", concept_id) if isinstance(c, dict) else concept_id,
                        occurrences=occurrences,
                        description=links[0].get("description", ""),
                    ))
        else:
            # Find all same_concept links
            seen = set()
            for link in self._cross_links:
                if link.get("relation") != "same_concept":
                    continue
                key = tuple(sorted([link["source_id"], link["target_id"]]))
                if key in seen:
                    continue
                seen.add(key)
                if domain_id and link["source_domain"] != domain_id and link["target_domain"] != domain_id:
                    continue
                src_c = self._concepts.get(link["source_id"], {})
                results.append(AlignedEntity(
                    canonical_id=link["source_id"],
                    canonical_name=src_c.get("name", link["source_id"]) if isinstance(src_c, dict) else link["source_id"],
                    occurrences=[
                        {"domain": link["source_domain"], "concept_id": link["source_id"]},
                        {"domain": link["target_domain"], "concept_id": link["target_id"]},
                    ],
                    description=link.get("description", ""),
                ))

        return results

    # ── Learning Zone Summary ────────────────────────────────

    def learning_zone_summary(
        self,
        progress: dict[str, UserProgress],
        domain_id: str,
    ) -> dict:
        """Generate a high-level learning zone summary for a domain.

        Returns zone distribution and key metrics for dashboard display.
        """
        subgraph = self.build_personalized_subgraph(
            progress, domain_id, include_mastered=True, zpd_depth=2,
        )
        stats = self._pathfinder.domain_progress_stats(domain_id, progress)

        # Identify bottleneck concepts (many dependents, not yet mastered)
        dependents_count: dict[str, int] = defaultdict(int)
        for e in self._edges:
            src = e.get("source_id") or e.get("source", "")
            rel = e.get("relation_type", "related")
            if rel == "prerequisite":
                dependents_count[src] += 1

        bottlenecks = []
        mastered_ids = {cid for cid, p in progress.items() if p.status == "mastered"}
        for node in subgraph.nodes:
            if node["status"] in ("available", "learning"):
                dep_count = dependents_count.get(node["id"], 0)
                if dep_count >= 3:
                    bottlenecks.append({
                        "concept_id": node["id"],
                        "label": node["label"],
                        "unlocks": dep_count,
                    })

        bottlenecks.sort(key=lambda x: x["unlocks"], reverse=True)

        return {
            **stats,
            "zpd": subgraph.stats,
            "bottlenecks": bottlenecks[:5],
        }
