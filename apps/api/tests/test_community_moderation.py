"""Tests for V2.1 AI auto-moderation endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport

from main import app

ADMIN_HEADERS = {"Authorization": "Bearer akg-admin-2026"}


async def _create_suggestion(client, **overrides):
    """Helper to create a test suggestion."""
    payload = {
        "type": "concept",
        "domain_id": "programming-basics",
        "concept_id": "test-concept",
        "title": "Add concept about recursion patterns",
        "description": "It would be great to have a concept covering common recursion patterns like divide-and-conquer, backtracking, and memoization approaches in algorithm design.",
        **overrides,
    }
    res = await client.post("/api/community/suggestions", json=payload)
    assert res.status_code == 200
    return res.json()["id"]


@pytest.mark.asyncio
async def test_auto_moderate_returns_score():
    """Auto-moderation should return a quality score and recommendation."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        sid = await _create_suggestion(client)
        res = await client.post(
            f"/api/community/suggestions/{sid}/auto-moderate",
            headers=ADMIN_HEADERS,
        )
        assert res.status_code == 200
        data = res.json()
        assert "quality_score" in data
        assert "recommendation" in data
        assert "signals" in data
        assert 0 <= data["quality_score"] <= 100
        assert data["recommendation"] in ("approve", "review", "reject")


@pytest.mark.asyncio
async def test_auto_moderate_detailed_suggestion_scores_high():
    """A detailed, well-formed suggestion should score higher."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        sid = await _create_suggestion(
            client,
            type="correction",
            domain_id="algorithms",
            concept_id="binary-search",
            title="Correction: Binary search requires sorted array as precondition",
            description="The current explanation of binary search does not clearly state that the input array must be sorted. This is a critical precondition that should be highlighted at the beginning of the concept description. Many students make errors because they don't check this first.",
        )

        # Vote it up
        for _ in range(3):
            await client.post(f"/api/community/suggestions/{sid}/vote")

        mod = await client.post(
            f"/api/community/suggestions/{sid}/auto-moderate",
            headers=ADMIN_HEADERS,
        )
        data = mod.json()
        assert data["quality_score"] >= 60
        assert data["recommendation"] in ("approve", "review")


@pytest.mark.asyncio
async def test_auto_moderate_spam_scores_low():
    """A spammy suggestion should score low."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        sid = await _create_suggestion(
            client,
            type="feedback",
            domain_id=None,
            concept_id=None,
            title="Buy cheap stuff click here now",
            description="http://spam.example.com free money casino win big prizes",
        )

        mod = await client.post(
            f"/api/community/suggestions/{sid}/auto-moderate",
            headers=ADMIN_HEADERS,
        )
        data = mod.json()
        assert data["quality_score"] < 40
        assert data["recommendation"] == "reject"


@pytest.mark.asyncio
async def test_auto_moderate_requires_admin():
    """Auto-moderation should require admin auth."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        sid = await _create_suggestion(client)
        res = await client.post(f"/api/community/suggestions/{sid}/auto-moderate")
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_auto_moderate_not_found():
    """Auto-moderation of non-existent suggestion should 404."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/api/community/suggestions/nonexistent_123/auto-moderate",
            headers=ADMIN_HEADERS,
        )
        assert res.status_code == 404


@pytest.mark.asyncio
async def test_batch_auto_moderate():
    """Batch auto-moderate should process multiple pending suggestions."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for i in range(3):
            await _create_suggestion(
                client,
                title=f"Batch test suggestion item {i} with good length",
                description=f"This is a detailed description for batch test item {i} with enough content to get a reasonable quality score from the auto-moderator system.",
            )

        res = await client.post(
            "/api/community/suggestions/batch-auto-moderate",
            headers=ADMIN_HEADERS,
        )
        assert res.status_code == 200
        data = res.json()
        assert "total_pending" in data
        assert "results" in data
        assert "auto_approve_count" in data
        assert len(data["results"]) > 0
        scores = [r["quality_score"] for r in data["results"]]
        assert scores == sorted(scores, reverse=True)


@pytest.mark.asyncio
async def test_batch_auto_moderate_requires_admin():
    """Batch auto-moderate should require admin auth."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/community/suggestions/batch-auto-moderate")
        assert res.status_code == 401