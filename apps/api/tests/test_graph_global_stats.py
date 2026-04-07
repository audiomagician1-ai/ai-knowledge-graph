"""Tests for /api/graph/stats/global endpoint."""

import pytest
from httpx import AsyncClient, ASGITransport

from main import app


@pytest.mark.asyncio
async def test_global_stats_structure():
    """Should return domains list and totals."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/api/graph/stats/global")
        assert r.status_code == 200
        data = r.json()
        assert "domains" in data
        assert "totals" in data
        assert isinstance(data["domains"], list)
        assert len(data["domains"]) > 0


@pytest.mark.asyncio
async def test_global_stats_totals():
    """Totals should have expected fields with positive values."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/api/graph/stats/global")
        data = r.json()
        totals = data["totals"]
        assert totals["domains"] > 0
        assert totals["concepts"] > 0
        assert totals["edges"] > 0
        assert totals["cross_links"] >= 0
        assert 1 <= totals["avg_difficulty"] <= 10


@pytest.mark.asyncio
async def test_global_stats_domain_fields():
    """Each domain entry should have required fields."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/api/graph/stats/global")
        data = r.json()
        d = data["domains"][0]
        assert "id" in d
        assert "name" in d
        assert "concepts" in d
        assert "edges" in d
        assert "avg_difficulty" in d
        assert "subdomains" in d
