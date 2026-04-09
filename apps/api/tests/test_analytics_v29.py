"""Tests for V2.9 Analytics Insights — concept similarity, content search, learning report."""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app

transport = ASGITransport(app=app)

BASE = "http://test:8006"


@pytest.mark.anyio
async def test_concept_similarity_returns_list():
    async with AsyncClient(transport=transport, base_url=BASE) as c:
        r = await c.get("/api/analytics/concept-similarity/supervised-learning?limit=5")
    assert r.status_code == 200
    data = r.json()
    assert "concept_id" in data
    assert "similar" in data
    assert isinstance(data["similar"], list)


@pytest.mark.anyio
async def test_concept_similarity_unknown_concept():
    async with AsyncClient(transport=transport, base_url=BASE) as c:
        r = await c.get("/api/analytics/concept-similarity/this-concept-does-not-exist-xyz")
    assert r.status_code == 200
    data = r.json()
    assert data["similar"] == []


@pytest.mark.anyio
async def test_concept_similarity_has_fields():
    async with AsyncClient(transport=transport, base_url=BASE) as c:
        r = await c.get("/api/analytics/concept-similarity/supervised-learning?limit=3")
    data = r.json()
    if data["similar"]:
        item = data["similar"][0]
        for field in ["concept_id", "name", "domain_id", "similarity_score", "reasons"]:
            assert field in item, f"Missing field: {field}"
        assert isinstance(item["reasons"], list)
        assert item["similarity_score"] > 0


@pytest.mark.anyio
async def test_content_search_returns_results():
    async with AsyncClient(transport=transport, base_url=BASE) as c:
        r = await c.get("/api/analytics/content-search?q=machine+learning&limit=5")
    assert r.status_code == 200
    data = r.json()
    assert "query" in data
    assert "results" in data
    assert isinstance(data["results"], list)
    assert data["query"] == "machine learning"


@pytest.mark.anyio
async def test_content_search_short_query():
    async with AsyncClient(transport=transport, base_url=BASE) as c:
        r = await c.get("/api/analytics/content-search?q=a")
    # FastAPI validation should reject queries shorter than 2 chars
    assert r.status_code == 422


@pytest.mark.anyio
async def test_content_search_result_fields():
    async with AsyncClient(transport=transport, base_url=BASE) as c:
        r = await c.get("/api/analytics/content-search?q=neural+network&limit=3")
    data = r.json()
    if data["results"]:
        item = data["results"][0]
        for field in ["concept_id", "name", "domain_id", "domain_name", "score"]:
            assert field in item, f"Missing field: {field}"


@pytest.mark.anyio
async def test_learning_report_structure():
    async with AsyncClient(transport=transport, base_url=BASE) as c:
        r = await c.get("/api/analytics/learning-report")
    assert r.status_code == 200
    data = r.json()
    assert "generated_at" in data
    assert "overview" in data
    assert "streak" in data
    assert "domains" in data
    assert "strengths" in data
    assert "weaknesses" in data
    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)


@pytest.mark.anyio
async def test_learning_report_overview_fields():
    async with AsyncClient(transport=transport, base_url=BASE) as c:
        r = await c.get("/api/analytics/learning-report")
    data = r.json()
    overview = data["overview"]
    for field in ["total_concepts_available", "mastered", "learning", "completion_percentage", "total_sessions", "avg_score"]:
        assert field in overview, f"Missing overview field: {field}"
    assert overview["total_concepts_available"] > 0  # We have 6300 concepts


@pytest.mark.anyio
async def test_learning_report_has_domains():
    async with AsyncClient(transport=transport, base_url=BASE) as c:
        r = await c.get("/api/analytics/learning-report")
    data = r.json()
    assert data["domains_total"] >= 36  # We have at least 36 domains


# ── Verify existing V2.7/V2.8 endpoints still work after split ──

@pytest.mark.anyio
async def test_weak_concepts_still_works():
    async with AsyncClient(transport=transport, base_url=BASE) as c:
        r = await c.get("/api/analytics/weak-concepts?limit=5")
    assert r.status_code == 200
    assert "weak_concepts" in r.json()


@pytest.mark.anyio
async def test_learning_efficiency_still_works():
    async with AsyncClient(transport=transport, base_url=BASE) as c:
        r = await c.get("/api/analytics/learning-efficiency")
    assert r.status_code == 200
    data = r.json()
    assert "global" in data


@pytest.mark.anyio
async def test_leaderboard_still_works():
    async with AsyncClient(transport=transport, base_url=BASE) as c:
        r = await c.get("/api/analytics/leaderboard?limit=10&sort_by=mastered")
    assert r.status_code == 200
    data = r.json()
    assert "leaderboard" in data
    assert len(data["leaderboard"]) <= 10


@pytest.mark.anyio
async def test_peer_comparison_still_works():
    async with AsyncClient(transport=transport, base_url=BASE) as c:
        r = await c.get("/api/analytics/peer-comparison")
    assert r.status_code == 200
    data = r.json()
    assert "percentiles" in data


@pytest.mark.anyio
async def test_difficulty_calibration_still_works():
    async with AsyncClient(transport=transport, base_url=BASE) as c:
        r = await c.get("/api/analytics/difficulty-calibration?domain_id=ai-engineering")
    assert r.status_code == 200
    data = r.json()
    assert "domain_id" in data
