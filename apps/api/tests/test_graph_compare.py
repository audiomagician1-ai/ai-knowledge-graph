"""Tests for V2.1 concept comparison API."""

import pytest
from httpx import AsyncClient, ASGITransport

from main import app

# Use real concept IDs from the default domain (ai-engineering)
CONCEPT_A = "binary-system"
CONCEPT_B = "boolean-logic"


@pytest.mark.asyncio
async def test_compare_concepts_structure():
    """Compare endpoint should return concept_a, concept_b, and comparison."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(f"/api/graph/compare-concepts?concept_a={CONCEPT_A}&concept_b={CONCEPT_B}")
        assert response.status_code == 200
        data = response.json()
        assert "concept_a" in data
        assert "concept_b" in data
        assert "comparison" in data
        assert data["concept_a"]["id"] == CONCEPT_A
        assert data["concept_b"]["id"] == CONCEPT_B


@pytest.mark.asyncio
async def test_compare_concepts_comparison_fields():
    """Comparison section should have all expected metrics."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(f"/api/graph/compare-concepts?concept_a={CONCEPT_A}&concept_b={CONCEPT_B}")
        assert response.status_code == 200
        data = response.json()
        comp = data["comparison"]
        assert "directly_connected" in comp
        assert "shared_connection_count" in comp
        assert "shared_prerequisites" in comp
        assert "same_subdomain" in comp
        assert "difficulty_gap" in comp
        assert "similarity_score" in comp
        assert isinstance(comp["similarity_score"], (int, float))
        assert 0 <= comp["similarity_score"] <= 100


@pytest.mark.asyncio
async def test_compare_concepts_not_found():
    """Comparing non-existent concepts should 404."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/graph/compare-concepts?concept_a=nonexistent_abc&concept_b=nonexistent_xyz")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_compare_concepts_difficulty_gap():
    """Difficulty gap should be non-negative."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(f"/api/graph/compare-concepts?concept_a={CONCEPT_A}&concept_b={CONCEPT_B}")
        assert response.status_code == 200
        data = response.json()
        assert data["comparison"]["difficulty_gap"] >= 0


@pytest.mark.asyncio
async def test_compare_concepts_with_domain():
    """Compare should accept domain_id parameter."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(f"/api/graph/compare-concepts?concept_a={CONCEPT_A}&concept_b={CONCEPT_B}&domain_id=ai-engineering")
        assert response.status_code == 200
