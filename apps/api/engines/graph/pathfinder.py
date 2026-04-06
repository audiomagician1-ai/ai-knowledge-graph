"""
学习路径计算器
基于图谱拓扑排序 + 用户状态的动态路径推荐

算法:
1. 拓扑排序 — Kahn's algorithm, 基于先修依赖的基础顺序
2. 最短学习路径 — BFS on prerequisite DAG, 给定目标返回最优前置序列
3. 动态推荐 — 基于用户掌握度 + 拓扑位置 + 难度梯度打分
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Concept:
    id: str
    name: str
    domain_id: str
    subdomain_id: str
    difficulty: int = 1
    estimated_minutes: int = 20
    is_milestone: bool = False


@dataclass
class Edge:
    source_id: str
    target_id: str
    relation_type: str = "prerequisite"
    strength: float = 0.5


@dataclass
class UserProgress:
    """Per-concept learning status from the learning store."""
    concept_id: str
    status: str = "not_started"  # not_started | learning | mastered
    mastery: float = 0.0  # BKT probability [0, 1]


@dataclass
class PathResult:
    """Result of a path computation."""
    path: list[str]
    total_estimated_minutes: int = 0
    steps: int = 0


@dataclass
class RecommendResult:
    """A single recommended concept with score breakdown."""
    concept_id: str
    score: float
    reasons: list[str] = field(default_factory=list)


class Pathfinder:
    """学习路径推荐引擎 — operates on in-memory graph data (JSON seed)."""

    def __init__(
        self,
        concepts: list[dict],
        edges: list[dict],
        cross_links: list[dict] | None = None,
    ):
        # Index concepts
        self._concepts: dict[str, Concept] = {}
        for c in concepts:
            self._concepts[c["id"]] = Concept(
                id=c["id"],
                name=c.get("name", c["id"]),
                domain_id=c.get("domain_id", ""),
                subdomain_id=c.get("subdomain_id", ""),
                difficulty=c.get("difficulty", 1),
                estimated_minutes=c.get("estimated_minutes", 20),
                is_milestone=c.get("is_milestone", False),
            )

        # Build adjacency lists (prerequisite edges only)
        # prereqs[target] = [source1, source2, ...] (what must come before target)
        self._prereqs: dict[str, list[str]] = defaultdict(list)
        # dependents[source] = [target1, ...] (what is unlocked after source)
        self._dependents: dict[str, list[str]] = defaultdict(list)
        # All edges for reference
        self._all_edges: list[Edge] = []

        for e in edges:
            src = e.get("source_id") or e.get("source", "")
            tgt = e.get("target_id") or e.get("target", "")
            rel = e.get("relation_type") or e.get("type", "related")
            strength = e.get("strength", 0.5)
            self._all_edges.append(Edge(src, tgt, rel, strength))
            if rel == "prerequisite":
                self._prereqs[tgt].append(src)
                self._dependents[src].append(tgt)

        # Cross-domain links (optional)
        self._cross_links = cross_links or []

    # ── Topological Sort (Kahn's Algorithm) ──────────────────

    def topological_sort(
        self,
        domain_id: str | None = None,
        subdomain_id: str | None = None,
    ) -> list[str]:
        """Return concepts in topological order (prerequisites first).

        Filters by domain/subdomain if specified.
        Concepts with no ordering constraints are sorted by difficulty.
        """
        # Filter concept set
        cids = self._filter_concepts(domain_id, subdomain_id)
        if not cids:
            return []

        # Build in-degree map for filtered set
        in_degree: dict[str, int] = {cid: 0 for cid in cids}
        adj: dict[str, list[str]] = defaultdict(list)
        for cid in cids:
            for dep in self._dependents.get(cid, []):
                if dep in cids:
                    adj[cid].append(dep)
                    in_degree[dep] = in_degree.get(dep, 0) + 1

        # Kahn's: start from nodes with in_degree 0, break ties by difficulty
        queue: list[str] = sorted(
            [cid for cid, d in in_degree.items() if d == 0],
            key=lambda x: self._concepts[x].difficulty,
        )
        result: list[str] = []

        while queue:
            # Pick the easiest available node (stable sort by difficulty)
            node = queue.pop(0)
            result.append(node)
            for neighbor in sorted(adj.get(node, []),
                                   key=lambda x: self._concepts[x].difficulty):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
                    queue.sort(key=lambda x: self._concepts[x].difficulty)

        # If result is smaller than cids, there's a cycle — append remaining
        remaining = cids - set(result)
        if remaining:
            result.extend(sorted(remaining,
                                 key=lambda x: self._concepts[x].difficulty))
        return result

    # ── Shortest Learning Path to Target ─────────────────────

    def shortest_path(
        self,
        target_id: str,
        progress: dict[str, UserProgress] | None = None,
    ) -> PathResult:
        """Compute the shortest prerequisite chain to reach *target_id*.

        If *progress* is provided, already-mastered concepts are skipped
        (they don't need to be re-learned but are still in the path for
        ordering context).

        Returns concepts in learning order (prerequisites first, target last).
        """
        if target_id not in self._concepts:
            return PathResult(path=[], total_estimated_minutes=0, steps=0)

        progress = progress or {}

        # BFS backwards from target through prerequisite edges
        needed: set[str] = set()
        queue = deque([target_id])
        visited: set[str] = set()

        while queue:
            node = queue.popleft()
            if node in visited:
                continue
            visited.add(node)
            needed.add(node)
            for prereq in self._prereqs.get(node, []):
                if prereq in self._concepts and prereq not in visited:
                    queue.append(prereq)

        # Topological sort within the needed set
        ordered = self._topo_subset(needed)

        # Filter out already mastered if progress provided
        if progress:
            filtered = [
                cid for cid in ordered
                if progress.get(cid, UserProgress(cid)).status != "mastered"
            ]
        else:
            filtered = ordered

        total_min = sum(
            self._concepts[cid].estimated_minutes
            for cid in filtered
            if cid in self._concepts
        )
        return PathResult(
            path=filtered,
            total_estimated_minutes=total_min,
            steps=len(filtered),
        )

    # ── Recommend Next Concepts ──────────────────────────────

    def recommend(
        self,
        progress: dict[str, UserProgress],
        domain_id: str | None = None,
        limit: int = 5,
    ) -> list[RecommendResult]:
        """Recommend next concepts to learn based on current progress.

        Scoring factors:
        - Prerequisites met (mandatory gate)
        - Difficulty gradient (prefer next-level difficulty)
        - Milestone bonus
        - BKT mastery of prerequisites (higher = more ready)
        - Subdomain continuity bonus
        """
        cids = self._filter_concepts(domain_id, None)
        candidates: list[RecommendResult] = []

        # Find the user's current "frontier" — concepts whose prereqs are met
        # but not yet mastered
        mastered_ids = {
            cid for cid, p in progress.items()
            if p.status == "mastered"
        }
        learning_ids = {
            cid for cid, p in progress.items()
            if p.status == "learning"
        }

        # Current max difficulty among mastered concepts
        max_mastered_diff = max(
            (self._concepts[cid].difficulty for cid in mastered_ids
             if cid in self._concepts),
            default=0,
        )

        # Active subdomain (most recent learning activity)
        active_subdomains = {
            self._concepts[cid].subdomain_id
            for cid in (learning_ids | mastered_ids)
            if cid in self._concepts
        }

        for cid in cids:
            if cid in mastered_ids:
                continue  # already mastered
            concept = self._concepts[cid]

            # Gate: all prerequisites must be mastered
            prereqs = self._prereqs.get(cid, [])
            prereqs_in_set = [p for p in prereqs if p in self._concepts]
            if prereqs_in_set and not all(p in mastered_ids for p in prereqs_in_set):
                continue

            score = 0.0
            reasons: list[str] = []

            # 1. Difficulty gradient: prefer concepts at current level + 1
            diff_delta = concept.difficulty - max_mastered_diff
            if diff_delta <= 0:
                score += 20  # catch-up: easy unlearned concept
                reasons.append("catch-up (below current level)")
            elif diff_delta == 1:
                score += 40  # ideal next step
                reasons.append("ideal difficulty step (+1)")
            elif diff_delta == 2:
                score += 25  # stretch goal
                reasons.append("stretch goal (+2 difficulty)")
            else:
                score += max(5, 30 - diff_delta * 5)
                reasons.append(f"difficulty gap (+{diff_delta})")

            # 2. Milestone bonus
            if concept.is_milestone:
                score += 15
                reasons.append("milestone concept")

            # 3. Subdomain continuity
            if concept.subdomain_id in active_subdomains:
                score += 10
                reasons.append("active subdomain continuity")

            # 4. Prerequisite mastery confidence
            if prereqs_in_set:
                avg_mastery = sum(
                    progress.get(p, UserProgress(p)).mastery
                    for p in prereqs_in_set
                ) / len(prereqs_in_set)
                mastery_bonus = avg_mastery * 15  # 0-15 points
                score += mastery_bonus
                if avg_mastery > 0.8:
                    reasons.append("strong prereq mastery")

            # 5. Currently learning bonus (continue what you started)
            if cid in learning_ids:
                score += 25
                reasons.append("already in progress")

            # 6. Short estimated time bonus (low friction)
            if concept.estimated_minutes <= 15:
                score += 5
                reasons.append("quick lesson")

            candidates.append(RecommendResult(
                concept_id=cid,
                score=round(score, 1),
                reasons=reasons,
            ))

        # Sort by score descending, take top N
        candidates.sort(key=lambda r: r.score, reverse=True)
        return candidates[:limit]

    # ── Prerequisite Validation ──────────────────────────────

    def validate_prereqs(
        self,
        concept_id: str,
        progress: dict[str, UserProgress],
    ) -> tuple[bool, list[str]]:
        """Check if prerequisites for a concept are met.

        Returns (is_met, list_of_unmet_prereq_ids).
        """
        prereqs = self._prereqs.get(concept_id, [])
        mastered = {
            cid for cid, p in progress.items()
            if p.status == "mastered"
        }
        unmet = [p for p in prereqs if p not in mastered and p in self._concepts]
        return (len(unmet) == 0, unmet)

    # ── Domain Statistics ────────────────────────────────────

    def domain_progress_stats(
        self,
        domain_id: str,
        progress: dict[str, UserProgress],
    ) -> dict:
        """Compute progress statistics for a domain."""
        cids = self._filter_concepts(domain_id, None)
        total = len(cids)
        mastered = sum(
            1 for cid in cids
            if progress.get(cid, UserProgress(cid)).status == "mastered"
        )
        learning = sum(
            1 for cid in cids
            if progress.get(cid, UserProgress(cid)).status == "learning"
        )
        not_started = total - mastered - learning

        # Average BKT mastery
        masteries = [
            progress.get(cid, UserProgress(cid)).mastery
            for cid in cids
        ]
        avg_mastery = sum(masteries) / len(masteries) if masteries else 0.0

        return {
            "domain_id": domain_id,
            "total": total,
            "mastered": mastered,
            "learning": learning,
            "not_started": not_started,
            "completion_pct": round(mastered / total * 100, 1) if total else 0,
            "avg_mastery": round(avg_mastery, 3),
        }

    # ── Internal Helpers ─────────────────────────────────────

    def _filter_concepts(
        self,
        domain_id: str | None,
        subdomain_id: str | None,
    ) -> set[str]:
        """Return set of concept IDs matching the filter."""
        result = set()
        for cid, c in self._concepts.items():
            if domain_id and c.domain_id != domain_id:
                continue
            if subdomain_id and c.subdomain_id != subdomain_id:
                continue
            result.add(cid)
        return result

    def _topo_subset(self, subset: set[str]) -> list[str]:
        """Topological sort within a subset of concepts."""
        in_degree: dict[str, int] = {cid: 0 for cid in subset}
        adj: dict[str, list[str]] = defaultdict(list)
        for cid in subset:
            for dep in self._dependents.get(cid, []):
                if dep in subset:
                    adj[cid].append(dep)
                    in_degree[dep] = in_degree.get(dep, 0) + 1

        queue = sorted(
            [cid for cid, d in in_degree.items() if d == 0],
            key=lambda x: self._concepts[x].difficulty,
        )
        result: list[str] = []
        while queue:
            node = queue.pop(0)
            result.append(node)
            for nb in adj.get(node, []):
                in_degree[nb] -= 1
                if in_degree[nb] == 0:
                    queue.append(nb)
                    queue.sort(key=lambda x: self._concepts[x].difficulty)

        remaining = subset - set(result)
        if remaining:
            result.extend(sorted(remaining,
                                 key=lambda x: self._concepts[x].difficulty))
        return result
