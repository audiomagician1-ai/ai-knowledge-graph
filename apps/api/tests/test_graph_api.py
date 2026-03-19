"""Graph API endpoint tests — seed graph data/subdomains/concept/neighbors/stats/rag"""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app

transport = ASGITransport(app=app)


# ── Graph Data ──────────────────────────────────────

@pytest.mark.asyncio
async def test_get_graph_data():
    """GET /api/graph/data should return all nodes and edges."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data")
        assert resp.status_code == 200
        data = resp.json()
        assert "nodes" in data
        assert "edges" in data
        assert len(data["nodes"]) == 282
        assert len(data["edges"]) == 367


@pytest.mark.asyncio
async def test_get_graph_data_with_subdomain_filter():
    """GET /api/graph/data?subdomain_id=cs-fundamentals should filter nodes."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?subdomain_id=cs-fundamentals")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["nodes"]) > 0
        assert len(data["nodes"]) < 267  # filtered subset
        # All nodes should belong to the requested subdomain
        for node in data["nodes"]:
            assert node["subdomain_id"] == "cs-fundamentals"
        # All edges should connect nodes within the subdomain
        node_ids = {n["id"] for n in data["nodes"]}
        for edge in data["edges"]:
            assert edge["source"] in node_ids
            assert edge["target"] in node_ids


@pytest.mark.asyncio
async def test_get_graph_data_node_structure():
    """Each node should have required fields."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data")
        data = resp.json()
        node = data["nodes"][0]
        required_keys = {"id", "label", "domain_id", "subdomain_id", "difficulty",
                         "status", "is_milestone", "estimated_minutes", "content_type", "tags"}
        assert required_keys.issubset(set(node.keys()))
        assert node["status"] == "not_started"  # default status


@pytest.mark.asyncio
async def test_get_graph_data_edge_structure():
    """Each edge should have required fields."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data")
        data = resp.json()
        edge = data["edges"][0]
        required_keys = {"id", "source", "target", "relation_type", "strength"}
        assert required_keys.issubset(set(edge.keys()))


@pytest.mark.asyncio
async def test_get_graph_data_nonexistent_subdomain():
    """Filtering by nonexistent subdomain should return empty."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?subdomain_id=nonexistent-domain")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["nodes"]) == 0
        assert len(data["edges"]) == 0


# ── Domains ──────────────────────────────────────

@pytest.mark.asyncio
async def test_get_domains():
    """GET /api/graph/domains should return domain list."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/domains")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["id"] == "ai-engineering"


# ── Subdomains ──────────────────────────────────────

@pytest.mark.asyncio
async def test_get_subdomains():
    """GET /api/graph/subdomains should return subdomain list with counts."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/subdomains")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 15
        # Each subdomain should have concept_count
        for sd in data:
            assert "id" in sd
            assert "name" in sd
            assert "concept_count" in sd
            assert sd["concept_count"] > 0


# ── Concept Detail ──────────────────────────────────

@pytest.mark.asyncio
async def test_get_concept_detail():
    """GET /api/graph/concepts/{id} should return concept with prereqs and dependents."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/concepts/binary-system")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "binary-system"
        assert data["name"] == "二进制与数制"
        assert "prerequisites" in data
        assert "dependents" in data
        assert isinstance(data["prerequisites"], list)
        assert isinstance(data["dependents"], list)


@pytest.mark.asyncio
async def test_get_concept_not_found():
    """GET /api/graph/concepts/{nonexistent} should return 404."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/concepts/nonexistent-concept-xyz")
        assert resp.status_code == 404


# ── Neighbors ──────────────────────────────────────

@pytest.mark.asyncio
async def test_get_neighbors():
    """GET /api/graph/concepts/{id}/neighbors should return subgraph."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/concepts/binary-system/neighbors?depth=1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["center"] == "binary-system"
        assert data["depth"] == 1
        assert len(data["nodes"]) >= 2  # at least the node itself + 1 neighbor
        # Center node should be included
        node_ids = {n["id"] for n in data["nodes"]}
        assert "binary-system" in node_ids


@pytest.mark.asyncio
async def test_get_neighbors_depth2():
    """Depth=2 should return more nodes than depth=1."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp1 = await client.get("/api/graph/concepts/binary-system/neighbors?depth=1")
        resp2 = await client.get("/api/graph/concepts/binary-system/neighbors?depth=2")
        data1 = resp1.json()
        data2 = resp2.json()
        assert len(data2["nodes"]) >= len(data1["nodes"])


@pytest.mark.asyncio
async def test_get_neighbors_depth_limit():
    """Depth > 3 should be rejected (max depth=3)."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/concepts/binary-system/neighbors?depth=4")
        assert resp.status_code == 422  # validation error


@pytest.mark.asyncio
async def test_get_neighbors_not_found():
    """Nonexistent concept should return 404."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/concepts/nonexistent-xyz/neighbors")
        assert resp.status_code == 404


# ── Stats ──────────────────────────────────────

@pytest.mark.asyncio
async def test_get_graph_stats():
    """GET /api/graph/stats should return meta statistics."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_concepts"] == 282
        assert data["total_edges"] == 367
        assert "subdomain_counts" in data
        assert "difficulty_distribution" in data


# ── RAG ──────────────────────────────────────

@pytest.mark.asyncio
async def test_get_rag_stats():
    """GET /api/graph/rag should return RAG index stats."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_docs" in data
        assert "total_chars" in data


@pytest.mark.asyncio
async def test_get_rag_document_not_found():
    """GET /api/graph/rag/{nonexistent} should return 404."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag/nonexistent-concept-xyz")
        assert resp.status_code == 404
