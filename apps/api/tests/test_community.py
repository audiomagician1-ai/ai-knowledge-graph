"""Tests for Community API — suggestions, voting, stats."""

import pytest
from httpx import ASGITransport, AsyncClient

from main import app


def _clear_store():
    from routers.community import _suggestions
    _suggestions.clear()


# ── Create ──

@pytest.mark.asyncio
async def test_create_concept_suggestion():
    """POST /api/community/suggestions should create a concept suggestion."""
    _clear_store()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/community/suggestions", json={
            "type": "concept",
            "domain_id": "programming",
            "title": "Add WebAssembly Concept",
            "description": "WebAssembly (Wasm) should be covered under programming as a compilation target for C/C++/Rust.",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["type"] == "concept"
        assert data["status"] == "pending"
        assert data["title"] == "Add WebAssembly Concept"
        assert data["id"].startswith("sug_")
        assert data["votes"] == 0


@pytest.mark.asyncio
async def test_create_link_suggestion():
    """POST should accept link suggestions with source/target."""
    _clear_store()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/community/suggestions", json={
            "type": "link",
            "title": "Connect recursion to fractals",
            "description": "Recursion in programming is fundamentally related to fractal geometry in mathematics.",
            "source_concept": "recursion",
            "target_concept": "fractal-geometry",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["type"] == "link"
        assert data["source_concept"] == "recursion"
        assert data["target_concept"] == "fractal-geometry"


@pytest.mark.asyncio
async def test_create_feedback_suggestion():
    """POST should accept feedback type."""
    _clear_store()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/community/suggestions", json={
            "type": "feedback",
            "title": "Graph visualization is slow",
            "description": "When opening domains with >200 nodes, the 3D graph takes 5+ seconds to render.",
        })
        assert resp.status_code == 200
        assert resp.json()["type"] == "feedback"


@pytest.mark.asyncio
async def test_create_suggestion_validation():
    """POST should reject too-short title/description."""
    _clear_store()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/community/suggestions", json={
            "type": "concept",
            "title": "AB",  # min_length=3
            "description": "Too short",  # min_length=10
        })
        assert resp.status_code == 422


# ── Read ──

@pytest.mark.asyncio
async def test_list_suggestions_empty():
    """GET /api/community/suggestions should return empty list."""
    _clear_store()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/community/suggestions")
        assert resp.status_code == 200
        assert resp.json() == []


@pytest.mark.asyncio
async def test_list_suggestions_filter_by_type():
    """GET with type filter should only return matching suggestions."""
    _clear_store()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post("/api/community/suggestions", json={
            "type": "concept", "title": "New concept", "description": "A detailed description of the new concept",
        })
        await client.post("/api/community/suggestions", json={
            "type": "feedback", "title": "UI feedback", "description": "Some detailed feedback about the UI",
        })

        resp = await client.get("/api/community/suggestions?type=concept")
        data = resp.json()
        assert len(data) == 1
        assert data[0]["type"] == "concept"


@pytest.mark.asyncio
async def test_get_suggestion_by_id():
    """GET /api/community/suggestions/{id} should return the suggestion."""
    _clear_store()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post("/api/community/suggestions", json={
            "type": "correction", "concept_id": "recursion",
            "title": "Fix recursion example",
            "description": "The fibonacci example has an off-by-one error in the base case.",
        })
        sid = r.json()["id"]

        resp = await client.get(f"/api/community/suggestions/{sid}")
        assert resp.status_code == 200
        assert resp.json()["id"] == sid


@pytest.mark.asyncio
async def test_get_suggestion_not_found():
    """GET non-existent suggestion should return 404."""
    _clear_store()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/community/suggestions/sug_nonexistent")
        assert resp.status_code == 404


# ── Voting ──

@pytest.mark.asyncio
async def test_vote_suggestion():
    """POST vote should increment the vote count."""
    _clear_store()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post("/api/community/suggestions", json={
            "type": "concept", "title": "Add Docker concept",
            "description": "Docker is widely used and should be part of the DevOps domain.",
        })
        sid = r.json()["id"]

        v1 = await client.post(f"/api/community/suggestions/{sid}/vote")
        assert v1.json()["votes"] == 1

        v2 = await client.post(f"/api/community/suggestions/{sid}/vote")
        assert v2.json()["votes"] == 2


@pytest.mark.asyncio
async def test_suggestions_sorted_by_votes():
    """List should return suggestions sorted by votes descending."""
    _clear_store()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r1 = await client.post("/api/community/suggestions", json={
            "type": "concept", "title": "Low vote item",
            "description": "A concept suggestion that won't get many votes",
        })
        r2 = await client.post("/api/community/suggestions", json={
            "type": "concept", "title": "Popular item",
            "description": "A concept suggestion that will be popular with users",
        })

        # Vote for r2 twice
        sid2 = r2.json()["id"]
        await client.post(f"/api/community/suggestions/{sid2}/vote")
        await client.post(f"/api/community/suggestions/{sid2}/vote")

        resp = await client.get("/api/community/suggestions")
        data = resp.json()
        assert len(data) == 2
        assert data[0]["title"] == "Popular item"
        assert data[0]["votes"] == 2


# ── Stats ──

@pytest.mark.asyncio
async def test_community_stats():
    """GET /api/community/stats should return aggregate data."""
    _clear_store()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post("/api/community/suggestions", json={
            "type": "concept", "title": "Concept A",
            "description": "Description for concept A with enough detail",
        })
        await client.post("/api/community/suggestions", json={
            "type": "feedback", "title": "Feedback B",
            "description": "Description for feedback B with enough detail",
        })

        resp = await client.get("/api/community/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_suggestions"] == 2
        assert data["by_type"]["concept"] == 1
        assert data["by_type"]["feedback"] == 1
        assert data["total_votes"] == 0
