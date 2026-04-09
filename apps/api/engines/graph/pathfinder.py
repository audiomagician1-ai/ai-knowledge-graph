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


@dataclass
class AdaptiveStep:
    """A single step in an adaptive learning path."""
    concept_id: str
    name: str
    priority: float
    action: str  # "learn" | "review" | "fill_gap"
    reasons: list[str] = field(default_factory=list)
    estimated_minutes: int = 20
    difficulty: int = 1
    subdomain_id: str = ""


@dataclass
class KnowledgeGap:
    """An unmastered prerequisite blocking downstream progress."""
    concept_id: str
    name: str
    blocked_count: int  # how many downstream concepts are blocked
    blocked_concepts: list[str] = field(default_factory=list)
    difficulty: int = 1
    status: str = "not_started"


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

    # ── Adaptive Learning Path ──────────────────────────────

    def adaptive_path(
        self,
        progress: dict[str, UserProgress],
        domain_id: str | None = None,
        fsrs_due: dict[str, float] | None = None,
        limit: int = 10,
    ) -> list[AdaptiveStep]:
        """Build a personalized learning path fusing topology + mastery + FSRS.

        The path interleaves three action types:
        1. **review**: FSRS-due concepts (overdue reviews get highest priority)
        2. **fill_gap**: unmastered prerequisites blocking frontier progress
        3. **learn**: new concepts on the optimal frontier

        Args:
            progress: concept_id → UserProgress
            domain_id: filter to a domain
            fsrs_due: concept_id → due timestamp (epoch s); concepts past now are due
            limit: max steps to return

        Returns:
            Ordered list of AdaptiveStep with action, priority, and reasons.
        """
        import time as _time
        now = _time.time()
        fsrs_due = fsrs_due or {}

        cids = self._filter_concepts(domain_id, None)
        mastered_ids = {
            cid for cid, p in progress.items()
            if p.status == "mastered" and cid in cids
        }

        steps: list[AdaptiveStep] = []

        # ── Phase 1: FSRS reviews (highest priority) ──
        for cid in cids:
            if cid not in fsrs_due:
                continue
            due_ts = fsrs_due[cid]
            if due_ts > now:
                continue  # not due yet
            if cid not in self._concepts:
                continue
            c = self._concepts[cid]
            overdue_days = max(0, (now - due_ts) / 86400)
            priority = 100.0 + min(overdue_days * 5.0, 50.0)
            reasons = ["📅 复习到期"]
            if overdue_days >= 3:
                reasons.append(f"逾期 {overdue_days:.0f} 天")
            steps.append(AdaptiveStep(
                concept_id=cid,
                name=c.name,
                priority=priority,
                action="review",
                reasons=reasons,
                estimated_minutes=max(5, c.estimated_minutes // 2),
                difficulty=c.difficulty,
                subdomain_id=c.subdomain_id,
            ))

        # ── Phase 2: Knowledge gaps (prerequisites blocking frontier) ──
        gaps = self.knowledge_gaps(progress, domain_id, limit=limit)
        gap_ids_added: set[str] = set()
        for gap in gaps:
            if gap.concept_id in mastered_ids:
                continue
            if gap.concept_id in {s.concept_id for s in steps}:
                continue
            c = self._concepts.get(gap.concept_id)
            if not c:
                continue
            priority = 60.0 + min(gap.blocked_count * 5.0, 30.0)
            reasons = [f"🔓 解锁 {gap.blocked_count} 个后续概念"]
            steps.append(AdaptiveStep(
                concept_id=gap.concept_id,
                name=c.name,
                priority=priority,
                action="fill_gap",
                reasons=reasons,
                estimated_minutes=c.estimated_minutes,
                difficulty=c.difficulty,
                subdomain_id=c.subdomain_id,
            ))
            gap_ids_added.add(gap.concept_id)

        # ── Phase 3: New frontier concepts ──
        recs = self.recommend(progress, domain_id=domain_id, limit=limit * 2)
        for rec in recs:
            if rec.concept_id in {s.concept_id for s in steps}:
                continue
            c = self._concepts.get(rec.concept_id)
            if not c:
                continue
            priority = min(rec.score, 55.0)
            reasons = list(rec.reasons)
            action = "learn"
            # Boost in-progress concepts
            p = progress.get(rec.concept_id)
            if p and p.status == "learning":
                priority += 10.0
                action = "learn"
            steps.append(AdaptiveStep(
                concept_id=rec.concept_id,
                name=c.name,
                priority=priority,
                action=action,
                reasons=reasons,
                estimated_minutes=c.estimated_minutes,
                difficulty=c.difficulty,
                subdomain_id=c.subdomain_id,
            ))

        # Sort by priority descending, take top limit
        steps.sort(key=lambda s: s.priority, reverse=True)
        return steps[:limit]

    # ── Knowledge Gap Detection ───────────────────────────

    def knowledge_gaps(
        self,
        progress: dict[str, UserProgress],
        domain_id: str | None = None,
        limit: int = 10,
    ) -> list[KnowledgeGap]:
        """Find unmastered prerequisites that block the most downstream concepts.

        A gap is a concept that:
        1. Is NOT mastered
        2. IS a prerequisite for at least one other concept whose OTHER prereqs are met

        Gaps are ranked by how many downstream concepts they unblock.
        """
        cids = self._filter_concepts(domain_id, None)
        mastered_ids = {
            cid for cid, p in progress.items()
            if p.status == "mastered" and cid in cids
        }

        # For each non-mastered concept, check if it blocks downstream concepts
        gap_scores: dict[str, list[str]] = defaultdict(list)

        for cid in cids:
            if cid in mastered_ids:
                continue
            # Check all concepts that depend on cid
            for dependent in self._dependents.get(cid, []):
                if dependent not in cids or dependent in mastered_ids:
                    continue
                # Check if cid is the only/one of few unmet prereqs for dependent
                prereqs_of_dep = self._prereqs.get(dependent, [])
                unmet = [
                    p for p in prereqs_of_dep
                    if p in cids and p not in mastered_ids
                ]
                if cid in unmet:
                    gap_scores[cid].append(dependent)

        gaps: list[KnowledgeGap] = []
        for gid, blocked in gap_scores.items():
            c = self._concepts.get(gid)
            if not c:
                continue
            p = progress.get(gid, UserProgress(gid))
            gaps.append(KnowledgeGap(
                concept_id=gid,
                name=c.name,
                blocked_count=len(blocked),
                blocked_concepts=blocked[:5],
                difficulty=c.difficulty,
                status=p.status,
            ))

        # Sort by blocked_count descending
        gaps.sort(key=lambda g: g.blocked_count, reverse=True)
        return gaps[:limit]

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
