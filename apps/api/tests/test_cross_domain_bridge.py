"""Tests for V2.5 cross-domain bridge API."""

import pytest
from httpx import AsyncClient, ASGITransport

from main import app


@pytest.mark.asyncio
async def test_cross_domain_bridge_structure():
    """Cross-domain bridge should return expected schema."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/graph/cross-domain-bridge/variables",
            params={"domain": "programming"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "concept_id" in data
        assert data["concept_id"] == "variables"
        assert "source_domain" in data
        assert "bridges" in data
        assert "total" in data
        assert "domains_connected" in data
        assert "by_domain" in data
        assert isinstance(data["bridges"], list)
        assert isinstance(data["total"], int)


@pytest.mark.asyncio
async def test_cross_domain_bridge_nonexistent():
    """Nonexistent concept should return empty bridges (not 404)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/graph/cross-domain-bridge/nonexistent-xyz",
            params={"domain": "programming"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["bridges"] == []
        assert data["domains_connected"] == []


@pytest.mark.asyncio
async def test_cross_domain_bridge_item_schema():
    """Bridge items should have all required fields."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/graph/cross-domain-bridge/variables",
            params={"domain": "programming"},
        )
        data = response.json()
        for bridge in data["bridges"]:
            assert "concept_id" in bridge
            assert "concept_name" in bridge
            assert "domain_id" in bridge
            assert "domain_name" in bridge
            assert "relation_type" in bridge
            assert "direction" in bridge
            assert bridge["direction"] in ("incoming", "outgoing")


@pytest.mark.asyncio
async def test_cross_domain_bridge_by_domain_grouping():
    """by_domain should group bridges correctly."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/graph/cross-domain-bridge/variables",
            params={"domain": "programming"},
        )
        data = response.json()
        # Verify by_domain is consistent with bridges
        total_in_groups = sum(len(v) for v in data["by_domain"].values())
        assert total_in_groups == data["total"]
        # All keys in by_domain should be in domains_connected
        for domain_id in data["by_domain"]:
            assert domain_id in data["domains_connected"]
