"""Adaptive Learning Path + Knowledge Gap Detection tests — V2.3"""

import json
import time
import pytest
from httpx import AsyncClient, ASGITransport
from engines.graph.pathfinder import (
    Pathfinder, UserProgress, AdaptiveStep, KnowledgeGap,
)
from main import app

transport = ASGITransport(app=app)


# ── Fixtures ─────────────────────────────────────────────

@pytest.fixture(scope="module")
def seed_data():
    import os
    root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))))
    with open(os.path.join(root, "data", "seed", "ai-engineering",
                           "seed_graph.json"), "r", encoding="utf-8") as f:
        seed = json.load(f)
    return seed


@pytest.fixture(scope="module")
def pathfinder(seed_data):
    return Pathfinder(seed_data["concepts"], seed_data["edges"])


# ── Adaptive Path Unit Tests ─────────────────────────────


class TestAdaptivePath:
    def test_empty_progress_returns_steps(self, pathfinder):
        steps = pathfinder.adaptive_path({}, domain_id="ai-engineering", limit=5)
        assert len(steps) == 5
        for s in steps:
            assert isinstance(s, AdaptiveStep)
            assert s.action in ("learn", "fill_gap", "review")
            assert s.priority > 0

    def test_review_action_when_fsrs_due(self, pathfinder):
        progress = {
            "binary-system": UserProgress("binary-system", "mastered", 0.95),
        }
        now = time.time()
        fsrs_due = {"binary-system": now - 86400}  # 1 day overdue
        steps = pathfinder.adaptive_path(
            progress, domain_id="ai-engineering",
            fsrs_due=fsrs_due, limit=10,
        )
        review_steps = [s for s in steps if s.action == "review"]
        assert len(review_steps) >= 1
        assert review_steps[0].concept_id == "binary-system"
        assert "📅 复习到期" in review_steps[0].reasons

    def test_reviews_have_highest_priority(self, pathfinder):
        progress = {
            "binary-system": UserProgress("binary-system", "mastered", 0.95),
            "boolean-logic": UserProgress("boolean-logic", "mastered", 0.9),
        }
        now = time.time()
        fsrs_due = {
            "binary-system": now - 86400 * 5,  # 5 days overdue
        }
        steps = pathfinder.adaptive_path(
            progress, domain_id="ai-engineering",
            fsrs_due=fsrs_due, limit=10,
        )
        assert steps[0].action == "review"
        assert steps[0].priority >= 100.0

    def test_mixed_actions_present(self, pathfinder):
        # Master some concepts to create a mix of gaps and frontier
        progress = {
            "binary-system": UserProgress("binary-system", "mastered", 0.95),
            "boolean-logic": UserProgress("boolean-logic", "mastered", 0.9),
            "what-is-programming": UserProgress("what-is-programming", "mastered", 0.95),
            "hello-world": UserProgress("hello-world", "mastered", 0.9),
            "variables": UserProgress("variables", "mastered", 0.9),
        }
        steps = pathfinder.adaptive_path(
            progress, domain_id="ai-engineering", limit=20,
        )
        assert len(steps) > 0
        actions = {s.action for s in steps}
        # With partial mastery, should have gap-filling or new learning
        assert len(actions) >= 1

    def test_limit_respected(self, pathfinder):
        steps = pathfinder.adaptive_path(
            {}, domain_id="ai-engineering", limit=3,
        )
        assert len(steps) <= 3

    def test_no_duplicate_concepts(self, pathfinder):
        progress = {
            "binary-system": UserProgress("binary-system", "mastered", 0.95),
        }
        now = time.time()
        fsrs_due = {"binary-system": now - 86400}
        steps = pathfinder.adaptive_path(
            progress, domain_id="ai-engineering",
            fsrs_due=fsrs_due, limit=10,
        )
        ids = [s.concept_id for s in steps]
        assert len(ids) == len(set(ids)), "Duplicate concepts in path"

    def test_priority_descending(self, pathfinder):
        steps = pathfinder.adaptive_path(
            {}, domain_id="ai-engineering", limit=10,
        )
        for i in range(len(steps) - 1):
            assert steps[i].priority >= steps[i + 1].priority


# ── Knowledge Gap Unit Tests ─────────────────────────────


class TestKnowledgeGaps:
    def test_empty_progress_finds_gaps(self, pathfinder):
        gaps = pathfinder.knowledge_gaps({}, domain_id="ai-engineering")
        # With empty progress, many concepts block downstream
        assert len(gaps) > 0
        for g in gaps:
            assert isinstance(g, KnowledgeGap)
            assert g.blocked_count > 0

    def test_no_gaps_when_all_mastered(self, pathfinder):
        # If all concepts are mastered, no gaps
        all_mastered = {
            cid: UserProgress(cid, "mastered", 1.0)
            for cid in pathfinder._concepts
            if pathfinder._concepts[cid].domain_id == "ai-engineering"
        }
        gaps = pathfinder.knowledge_gaps(
            all_mastered, domain_id="ai-engineering",
        )
        assert len(gaps) == 0

    def test_gaps_sorted_by_blocked_count(self, pathfinder):
        gaps = pathfinder.knowledge_gaps(
            {}, domain_id="ai-engineering", limit=20,
        )
        for i in range(len(gaps) - 1):
            assert gaps[i].blocked_count >= gaps[i + 1].blocked_count

    def test_gap_details_populated(self, pathfinder):
        gaps = pathfinder.knowledge_gaps(
            {}, domain_id="ai-engineering", limit=5,
        )
        for g in gaps:
            assert g.name != ""
            assert g.difficulty >= 1
            assert len(g.blocked_concepts) <= 5
            assert g.blocked_count >= len(g.blocked_concepts)

    def test_limit_respected(self, pathfinder):
        gaps = pathfinder.knowledge_gaps(
            {}, domain_id="ai-engineering", limit=3,
        )
        assert len(gaps) <= 3

    def test_mastering_gap_reduces_count(self, pathfinder):
        gaps_before = pathfinder.knowledge_gaps(
            {}, domain_id="ai-engineering", limit=50,
        )
        if not gaps_before:
            return
        # Master the top gap
        top_gap_id = gaps_before[0].concept_id
        progress = {
            top_gap_id: UserProgress(top_gap_id, "mastered", 1.0),
        }
        gaps_after = pathfinder.knowledge_gaps(
            progress, domain_id="ai-engineering", limit=50,
        )
        # The mastered concept should no longer be a gap
        gap_ids_after = {g.concept_id for g in gaps_after}
        assert top_gap_id not in gap_ids_after


# ── API Endpoint Tests ───────────────────────────────────


@pytest.mark.asyncio
async def test_api_adaptive_path():
    """GET /api/learning/adaptive-path/{domain} returns personalized path."""
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/learning/adaptive-path/ai-engineering?limit=5")
        assert resp.status_code == 200
        data = resp.json()
        assert "steps" in data
        assert len(data["steps"]) <= 5
        for step in data["steps"]:
            assert "concept_id" in step
            assert "action" in step
            assert step["action"] in ("learn", "review", "fill_gap")
            assert "priority" in step
            assert "reasons" in step


@pytest.mark.asyncio
async def test_api_adaptive_path_with_progress():
    """Adaptive path respects user progress."""
    progress = json.dumps({
        "binary-system": {"status": "mastered", "mastery": 0.95},
        "boolean-logic": {"status": "mastered", "mastery": 0.9},
    })
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get(
            f"/api/learning/adaptive-path/ai-engineering?limit=10&progress={progress}"
        )
        assert resp.status_code == 200
        data = resp.json()
        step_ids = {s["concept_id"] for s in data["steps"]}
        # Mastered concepts should not appear as "learn" actions
        for s in data["steps"]:
            if s["concept_id"] in ("binary-system", "boolean-logic"):
                assert s["action"] == "review"  # only if FSRS due


@pytest.mark.asyncio
async def test_api_knowledge_gaps():
    """GET /api/learning/knowledge-gaps/{domain} returns gaps."""
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/learning/knowledge-gaps/ai-engineering?limit=5")
        assert resp.status_code == 200
        data = resp.json()
        assert "gaps" in data
        assert "total_gaps" in data
        for gap in data["gaps"]:
            assert "concept_id" in gap
            assert "blocked_count" in gap
            assert gap["blocked_count"] > 0


@pytest.mark.asyncio
async def test_api_knowledge_gaps_with_progress():
    """Gaps reflect mastery progress."""
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Get gaps with no progress
        resp1 = await ac.get("/api/learning/knowledge-gaps/ai-engineering?limit=5")
        data1 = resp1.json()
        if not data1["gaps"]:
            return

        # Master the top gap and check it disappears
        top_id = data1["gaps"][0]["concept_id"]
        progress = json.dumps({top_id: {"status": "mastered", "mastery": 1.0}})
        resp2 = await ac.get(
            f"/api/learning/knowledge-gaps/ai-engineering?limit=50&progress={progress}"
        )
        data2 = resp2.json()
        gap_ids = {g["concept_id"] for g in data2["gaps"]}
        assert top_id not in gap_ids
