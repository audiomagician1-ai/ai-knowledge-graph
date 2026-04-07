"""Tests for Analytics API — difficulty map, domain heatmap, learning velocity, content quality signals."""

import pytest
from httpx import ASGITransport, AsyncClient

from main import app


# ── Difficulty Map ──

@pytest.mark.asyncio
async def test_difficulty_map_structure():
    """GET /api/analytics/difficulty-map should return proper structure."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/analytics/difficulty-map")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_assessed" in data
        assert "distribution" in data
        assert "struggling_concepts" in data
        assert "recently_mastered" in data
        # Distribution should have all 4 buckets
        dist = data["distribution"]
        for bucket in ("struggling", "developing", "proficient", "mastered"):
            assert bucket in dist
            assert isinstance(dist[bucket], int)


@pytest.mark.asyncio
async def test_difficulty_map_total():
    """Total assessed should be sum of distribution buckets."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/analytics/difficulty-map")
        data = resp.json()
        bucket_sum = sum(data["distribution"].values())
        assert data["total_assessed"] == bucket_sum


# ── Domain Heatmap ──

@pytest.mark.asyncio
async def test_domain_heatmap_structure():
    """GET /api/analytics/domain-heatmap should return per-domain stats."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/analytics/domain-heatmap")
        assert resp.status_code == 200
        data = resp.json()
        assert "domains" in data
        assert "total_domains" in data
        assert isinstance(data["domains"], dict)
        # Each domain should have required fields
        for domain_id, stats in data["domains"].items():
            assert "total" in stats
            assert "mastered" in stats
            assert "avg_score" in stats
            assert "mastery_rate" in stats


# ── Learning Velocity ──

@pytest.mark.asyncio
async def test_learning_velocity_default():
    """GET /api/analytics/learning-velocity should return 30 days by default."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/analytics/learning-velocity")
        assert resp.status_code == 200
        data = resp.json()
        assert data["days"] == 30
        assert "daily" in data
        assert len(data["daily"]) == 30
        assert "streak" in data
        assert "summary" in data
        # Each day entry should have expected fields
        for day in data["daily"]:
            assert "date" in day
            assert "assessments" in day
            assert "concepts_started" in day
            assert "mastered" in day


@pytest.mark.asyncio
async def test_learning_velocity_custom_days():
    """GET with days=7 should return 7-day data."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/analytics/learning-velocity?days=7")
        data = resp.json()
        assert data["days"] == 7
        assert len(data["daily"]) == 7


@pytest.mark.asyncio
async def test_learning_velocity_chronological():
    """Daily data should be in chronological order."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/analytics/learning-velocity?days=7")
        data = resp.json()
        dates = [d["date"] for d in data["daily"]]
        assert dates == sorted(dates)


# ── Content Quality Signals ──

@pytest.mark.asyncio
async def test_content_quality_signals_structure():
    """GET /api/analytics/content-quality-signals should return signal data."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/analytics/content-quality-signals")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_signals" in data
        assert "high_severity" in data
        assert "medium_severity" in data
        assert "signals" in data
        assert isinstance(data["signals"], list)


@pytest.mark.asyncio
async def test_content_quality_signals_limit():
    """Signals list should have max 50 entries."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/analytics/content-quality-signals")
        data = resp.json()
        assert len(data["signals"]) <= 50
