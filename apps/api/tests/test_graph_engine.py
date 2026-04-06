"""Graph Engine tests — Pathfinder + GraphBuilder algorithms + API endpoints #42"""

import json
import pytest
from httpx import AsyncClient, ASGITransport
from engines.graph.pathfinder import Pathfinder, UserProgress, PathResult
from engines.graph.builder import GraphBuilder
from main import app

transport = ASGITransport(app=app)


# ── Fixtures ─────────────────────────────────────────────

@pytest.fixture(scope="module")
def seed_data():
    """Load ai-engineering seed graph for unit tests."""
    import os
    root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))))
    with open(os.path.join(root, "data", "seed", "ai-engineering",
                           "seed_graph.json"), "r", encoding="utf-8") as f:
        seed = json.load(f)
    with open(os.path.join(root, "data", "seed",
                           "cross_sphere_links.json"), "r", encoding="utf-8") as f:
        cross = json.load(f)
    return {"seed": seed, "cross_links": cross.get("links", [])}


@pytest.fixture(scope="module")
def pathfinder(seed_data):
    return Pathfinder(
        seed_data["seed"]["concepts"],
        seed_data["seed"]["edges"],
        seed_data["cross_links"],
    )


@pytest.fixture(scope="module")
def builder(seed_data):
    return GraphBuilder(
        seed_data["seed"]["concepts"],
        seed_data["seed"]["edges"],
        seed_data["cross_links"],
    )


# ── Pathfinder Unit Tests ────────────────────────────────


class TestTopologicalSort:
    def test_returns_all_concepts(self, pathfinder):
        order = pathfinder.topological_sort(domain_id="ai-engineering")
        assert len(order) == 400

    def test_prerequisites_before_dependents(self, pathfinder):
        order = pathfinder.topological_sort(domain_id="ai-engineering")
        pos = {cid: i for i, cid in enumerate(order)}
        # binary-system should come before boolean-logic
        assert pos["binary-system"] < pos["boolean-logic"]
        # variables should come before loops
        assert pos["variables"] < pos["loops"]

    def test_easy_concepts_first(self, pathfinder):
        order = pathfinder.topological_sort(domain_id="ai-engineering")
        # First concepts should be difficulty 1
        first_5 = order[:5]
        for cid in first_5:
            c = pathfinder._concepts[cid]
            assert c.difficulty <= 2, f"{cid} has difficulty {c.difficulty}"

    def test_subdomain_filter(self, pathfinder):
        order = pathfinder.topological_sort(
            domain_id="ai-engineering",
            subdomain_id="cs-fundamentals",
        )
        assert len(order) > 0
        assert len(order) < 400
        for cid in order:
            assert pathfinder._concepts[cid].subdomain_id == "cs-fundamentals"

    def test_empty_domain_returns_empty(self, pathfinder):
        order = pathfinder.topological_sort(domain_id="nonexistent")
        assert order == []


class TestShortestPath:
    def test_path_to_known_concept(self, pathfinder):
        result = pathfinder.shortest_path("neural-network-basics")
        assert isinstance(result, PathResult)
        assert result.steps > 0
        assert result.path[-1] == "neural-network-basics"
        assert result.total_estimated_minutes > 0

    def test_path_preserves_order(self, pathfinder):
        result = pathfinder.shortest_path("neural-network-basics")
        # Every concept's prereqs should appear before it
        pos = {cid: i for i, cid in enumerate(result.path)}
        for cid in result.path:
            for prereq in pathfinder._prereqs.get(cid, []):
                if prereq in pos:
                    assert pos[prereq] < pos[cid]

    def test_path_with_progress_skips_mastered(self, pathfinder):
        progress = {
            "what-is-programming": UserProgress("what-is-programming", "mastered"),
            "hello-world": UserProgress("hello-world", "mastered"),
            "variables": UserProgress("variables", "mastered"),
        }
        result = pathfinder.shortest_path("loops", progress)
        assert "what-is-programming" not in result.path
        assert "hello-world" not in result.path
        assert "variables" not in result.path

    def test_path_nonexistent_target(self, pathfinder):
        result = pathfinder.shortest_path("nonexistent-concept")
        assert result.steps == 0
        assert result.path == []

    def test_path_no_prereqs_concept(self, pathfinder):
        result = pathfinder.shortest_path("binary-system")
        assert result.steps == 1
        assert result.path == ["binary-system"]


class TestRecommend:
    def test_empty_progress(self, pathfinder):
        recs = pathfinder.recommend({}, domain_id="ai-engineering", limit=5)
        assert len(recs) == 5
        # Should recommend difficulty-1 concepts with no prereqs
        for r in recs:
            assert r.score > 0
            assert len(r.reasons) > 0

    def test_with_mastered_concepts(self, pathfinder):
        progress = {
            "binary-system": UserProgress("binary-system", "mastered", 0.95),
            "boolean-logic": UserProgress("boolean-logic", "mastered", 0.88),
        }
        recs = pathfinder.recommend(progress, domain_id="ai-engineering", limit=5)
        assert len(recs) > 0
        # Should not recommend already mastered
        rec_ids = {r.concept_id for r in recs}
        assert "binary-system" not in rec_ids
        assert "boolean-logic" not in rec_ids

    def test_learning_bonus(self, pathfinder):
        progress = {
            "binary-system": UserProgress("binary-system", "mastered", 0.95),
            "character-encoding": UserProgress("character-encoding", "learning", 0.4),
        }
        recs = pathfinder.recommend(progress, domain_id="ai-engineering", limit=10)
        # character-encoding should be recommended with bonus
        ce = next((r for r in recs if r.concept_id == "character-encoding"), None)
        assert ce is not None
        assert "already in progress" in ce.reasons

    def test_limit_respected(self, pathfinder):
        recs = pathfinder.recommend({}, domain_id="ai-engineering", limit=3)
        assert len(recs) <= 3

    def test_scores_descending(self, pathfinder):
        recs = pathfinder.recommend({}, domain_id="ai-engineering", limit=10)
        for i in range(len(recs) - 1):
            assert recs[i].score >= recs[i + 1].score


class TestValidatePrereqs:
    def test_no_prereqs_always_met(self, pathfinder):
        is_met, unmet = pathfinder.validate_prereqs("binary-system", {})
        assert is_met is True
        assert unmet == []

    def test_prereqs_not_met(self, pathfinder):
        is_met, unmet = pathfinder.validate_prereqs("loops", {})
        assert is_met is False
        assert len(unmet) > 0

    def test_prereqs_met_after_mastery(self, pathfinder):
        # Find a concept with prereqs
        target = "boolean-logic"
        prereqs = pathfinder._prereqs.get(target, [])
        progress = {p: UserProgress(p, "mastered") for p in prereqs}
        is_met, unmet = pathfinder.validate_prereqs(target, progress)
        assert is_met is True
        assert unmet == []


class TestDomainProgressStats:
    def test_empty_progress(self, pathfinder):
        stats = pathfinder.domain_progress_stats("ai-engineering", {})
        assert stats["total"] == 400
        assert stats["mastered"] == 0
        assert stats["not_started"] == 400
        assert stats["completion_pct"] == 0.0

    def test_partial_progress(self, pathfinder):
        progress = {
            "binary-system": UserProgress("binary-system", "mastered", 0.95),
            "hello-world": UserProgress("hello-world", "learning", 0.4),
        }
        stats = pathfinder.domain_progress_stats("ai-engineering", progress)
        assert stats["mastered"] == 1
        assert stats["learning"] == 1
        assert stats["not_started"] == 398
        assert stats["completion_pct"] == 0.2  # 1/400 * 100 = 0.25 -> rounded


# ── GraphBuilder Unit Tests ──────────────────────────────


class TestPersonalizedSubgraph:
    def test_empty_progress_shows_frontier(self, builder):
        result = builder.build_personalized_subgraph(
            {}, domain_id="ai-engineering",
        )
        assert len(result.nodes) > 0
        zones = {n["zone"] for n in result.nodes}
        assert "frontier" in zones

    def test_zpd_zones_correct(self, builder):
        progress = {
            "binary-system": UserProgress("binary-system", "mastered", 0.95),
            "hello-world": UserProgress("hello-world", "learning", 0.4),
        }
        result = builder.build_personalized_subgraph(
            progress, domain_id="ai-engineering",
        )
        zones = {}
        for n in result.nodes:
            z = n["zone"]
            zones[z] = zones.get(z, 0) + 1
        assert zones.get("mastered", 0) >= 1
        assert zones.get("learning", 0) >= 1
        assert zones.get("frontier", 0) >= 1

    def test_exclude_mastered(self, builder):
        progress = {
            "binary-system": UserProgress("binary-system", "mastered", 0.95),
        }
        result = builder.build_personalized_subgraph(
            progress, domain_id="ai-engineering",
            include_mastered=False,
        )
        mastered_nodes = [n for n in result.nodes if n["zone"] == "mastered"]
        assert len(mastered_nodes) == 0

    def test_zpd_depth_affects_preview(self, builder):
        progress = {
            "binary-system": UserProgress("binary-system", "mastered", 0.95),
        }
        r1 = builder.build_personalized_subgraph(
            progress, domain_id="ai-engineering", zpd_depth=1,
        )
        r2 = builder.build_personalized_subgraph(
            progress, domain_id="ai-engineering", zpd_depth=3,
        )
        assert len(r2.nodes) >= len(r1.nodes)


class TestEntityAlignment:
    def test_find_specific_entity(self, builder):
        entities = builder.find_aligned_entities(concept_id="linear-regression")
        assert len(entities) >= 1
        e = entities[0]
        assert len(e.occurrences) >= 2

    def test_find_all_same_concept(self, builder):
        entities = builder.find_aligned_entities()
        assert len(entities) > 0

    def test_domain_filter(self, builder):
        entities = builder.find_aligned_entities(domain_id="ai-engineering")
        for e in entities:
            domains = {o["domain"] for o in e.occurrences}
            assert "ai-engineering" in domains or any(
                "ai-engineering" in str(o) for o in e.occurrences
            )


class TestLearningZoneSummary:
    def test_summary_structure(self, builder):
        progress = {
            "binary-system": UserProgress("binary-system", "mastered", 0.95),
        }
        summary = builder.learning_zone_summary(progress, "ai-engineering")
        assert "total" in summary
        assert "mastered" in summary
        assert "zpd" in summary
        assert "bottlenecks" in summary

    def test_bottlenecks_sorted(self, builder):
        summary = builder.learning_zone_summary({}, "ai-engineering")
        bottlenecks = summary["bottlenecks"]
        for i in range(len(bottlenecks) - 1):
            assert bottlenecks[i]["unlocks"] >= bottlenecks[i + 1]["unlocks"]


# ── API Endpoint Tests ───────────────────────────────────


@pytest.mark.asyncio
async def test_api_learning_path():
    """GET /api/graph/path/{target} returns learning path."""
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/graph/path/neural-network-basics")
        assert resp.status_code == 200
        data = resp.json()
        assert data["target"] == "neural-network-basics"
        assert data["steps"] > 0
        assert len(data["path"]) == data["steps"]
        assert data["path"][-1]["id"] == "neural-network-basics"
        assert data["total_estimated_minutes"] > 0


@pytest.mark.asyncio
async def test_api_learning_path_with_progress():
    """Path endpoint respects progress param."""
    progress = json.dumps({
        "what-is-programming": {"status": "mastered", "mastery": 0.9},
        "hello-world": {"status": "mastered", "mastery": 0.85},
    })
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get(f"/api/graph/path/variables?progress={progress}")
        assert resp.status_code == 200
        data = resp.json()
        path_ids = [p["id"] for p in data["path"]]
        assert "what-is-programming" not in path_ids
        assert "hello-world" not in path_ids


@pytest.mark.asyncio
async def test_api_recommendations():
    """GET /api/graph/recommend returns recommendations."""
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/graph/recommend?limit=5")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["recommendations"]) == 5
        for rec in data["recommendations"]:
            assert "concept_id" in rec
            assert "score" in rec
            assert "reasons" in rec
            assert rec["score"] > 0


@pytest.mark.asyncio
async def test_api_recommendations_with_progress():
    """Recommendations exclude mastered concepts."""
    progress = json.dumps({
        "binary-system": {"status": "mastered", "mastery": 0.95},
    })
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get(f"/api/graph/recommend?limit=10&progress={progress}")
        assert resp.status_code == 200
        data = resp.json()
        rec_ids = {r["concept_id"] for r in data["recommendations"]}
        assert "binary-system" not in rec_ids


@pytest.mark.asyncio
async def test_api_topo_sort():
    """GET /api/graph/topo-sort returns topological order."""
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/graph/topo-sort?limit=10")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["order"]) == 10
        assert data["total"] == 400
        for item in data["order"]:
            assert "id" in item
            assert "name" in item
            assert "position" in item


@pytest.mark.asyncio
async def test_api_topo_sort_subdomain():
    """Topo sort with subdomain filter."""
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/graph/topo-sort?subdomain=cs-fundamentals&limit=50")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] > 0
        assert data["total"] < 400


@pytest.mark.asyncio
async def test_api_zpd_subgraph():
    """GET /api/graph/zpd returns personalized subgraph."""
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/graph/zpd")
        assert resp.status_code == 200
        data = resp.json()
        assert "nodes" in data
        assert "edges" in data
        assert "stats" in data


@pytest.mark.asyncio
async def test_api_zpd_with_progress():
    """ZPD subgraph adapts to user progress."""
    progress = json.dumps({
        "binary-system": {"status": "mastered", "mastery": 0.95},
        "boolean-logic": {"status": "mastered", "mastery": 0.88},
    })
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get(f"/api/graph/zpd?progress={progress}")
        assert resp.status_code == 200
        data = resp.json()
        # Should have mastered nodes
        mastered = [n for n in data["nodes"] if n.get("zone") == "mastered"]
        assert len(mastered) >= 2


@pytest.mark.asyncio
async def test_api_aligned_entities():
    """GET /api/graph/aligned-entities returns cross-domain mappings."""
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/graph/aligned-entities?concept_id=linear-regression")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        entity = data["entities"][0]
        assert "canonical_id" in entity
        assert "occurrences" in entity
        assert len(entity["occurrences"]) >= 2


@pytest.mark.asyncio
async def test_api_zone_summary():
    """GET /api/graph/zone-summary returns domain summary."""
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/graph/zone-summary")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 400
        assert "zpd" in data
        assert "bottlenecks" in data


@pytest.mark.asyncio
async def test_api_zone_summary_with_progress():
    """Zone summary reflects progress."""
    progress = json.dumps({
        "binary-system": {"status": "mastered", "mastery": 0.95},
    })
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get(f"/api/graph/zone-summary?progress={progress}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["mastered"] == 1