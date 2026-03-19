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
        assert len(data["nodes"]) == 400
        assert len(data["edges"]) == 615


@pytest.mark.asyncio
async def test_get_graph_data_with_subdomain_filter():
    """GET /api/graph/data?subdomain_id=cs-fundamentals should filter nodes."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?subdomain_id=cs-fundamentals")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["nodes"]) > 0
        assert len(data["nodes"]) < 400  # filtered subset
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
    """GET /api/graph/domains should return domain list with stats."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/domains")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        domain = data[0]
        assert domain["id"] == "ai-engineering"
        assert domain["name"] == "AI工程"
        # Domain list now includes stats
        assert "stats" in domain
        assert domain["stats"]["total_concepts"] == 400
        assert domain["stats"]["total_edges"] == 615
        assert domain["stats"]["subdomains"] == 15


@pytest.mark.asyncio
async def test_get_graph_data_with_domain_param():
    """GET /api/graph/data?domain=ai-engineering should work same as default."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=ai-engineering")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["nodes"]) == 400
        assert len(data["edges"]) == 615


@pytest.mark.asyncio
async def test_get_graph_data_invalid_domain():
    """GET /api/graph/data?domain=nonexistent should return 404."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=nonexistent")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_subdomains_with_domain_param():
    """GET /api/graph/subdomains?domain=ai-engineering should work."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/subdomains?domain=ai-engineering")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 15


@pytest.mark.asyncio
async def test_get_stats_with_domain_param():
    """GET /api/graph/stats?domain=ai-engineering should return stats."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/stats?domain=ai-engineering")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_concepts"] == 400


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
        assert data["total_concepts"] == 400
        assert data["total_edges"] == 615
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


# ── Multi-Domain Integration (Phase 7.7) ──────────────────────────────────

@pytest.mark.asyncio
async def test_domain_consistency_default_vs_explicit():
    """Default request and ?domain=ai-engineering should return identical data."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp_default = await client.get("/api/graph/data")
        resp_explicit = await client.get("/api/graph/data?domain=ai-engineering")
        assert resp_default.status_code == 200
        assert resp_explicit.status_code == 200
        default_data = resp_default.json()
        explicit_data = resp_explicit.json()
        assert len(default_data["nodes"]) == len(explicit_data["nodes"])
        assert len(default_data["edges"]) == len(explicit_data["edges"])


@pytest.mark.asyncio
async def test_domain_all_nodes_have_domain_id():
    """All nodes returned should have a domain_id field matching the requested domain."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=ai-engineering")
        assert resp.status_code == 200
        data = resp.json()
        for node in data["nodes"]:
            assert "domain_id" in node
            assert node["domain_id"] == "ai-engineering"


@pytest.mark.asyncio
async def test_domain_concept_detail_inherits_domain():
    """Concept detail should include domain_id."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/concepts/variables")
        assert resp.status_code == 200
        data = resp.json()
        assert "domain_id" in data
        assert data["domain_id"] == "ai-engineering"


@pytest.mark.asyncio
async def test_domain_invalid_domain_subdomains():
    """GET /api/graph/subdomains?domain=nonexistent should return 404."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/subdomains?domain=nonexistent")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_domain_invalid_domain_stats():
    """GET /api/graph/stats?domain=nonexistent should return 404."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/stats?domain=nonexistent")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_domain_list_structure():
    """GET /api/graph/domains should return complete domain metadata."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/domains")
        assert resp.status_code == 200
        data = resp.json()
        for domain in data:
            # Required fields from domains.json + runtime stats
            assert "id" in domain
            assert "name" in domain
            assert "description" in domain
            assert "icon" in domain
            assert "color" in domain
            assert "stats" in domain
            assert domain["stats"]["total_concepts"] > 0


# ── Mathematics Domain Tests ───────────────────────────

@pytest.mark.asyncio
async def test_math_domain_graph_data():
    """GET /api/graph/data?domain=mathematics should return math concepts."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=mathematics")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["nodes"]) == 269
        assert len(data["edges"]) == 366
        # All nodes should be math domain
        for node in data["nodes"]:
            assert node["domain_id"] == "mathematics"


@pytest.mark.asyncio
async def test_math_domain_subdomains():
    """Mathematics should have 12 subdomains."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/subdomains?domain=mathematics")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 12
        sub_ids = {s["id"] for s in data}
        expected = {"arithmetic", "algebra", "geometry", "trigonometry",
                    "analytic-geometry", "calculus", "linear-algebra",
                    "probability", "statistics", "discrete-math",
                    "number-theory", "optimization"}
        assert sub_ids == expected


@pytest.mark.asyncio
async def test_math_domain_stats():
    """Mathematics stats should reflect seed data."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/stats?domain=mathematics")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_concepts"] == 269
        assert data["total_edges"] == 366
        assert data["total_milestones"] == 29


@pytest.mark.asyncio
async def test_math_domain_concept_detail():
    """Should fetch a math concept by ID."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/concepts/quadratic-equations?domain=mathematics")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "quadratic-equations"
        assert data["domain_id"] == "mathematics"
        assert data["subdomain_id"] == "algebra"
        assert data["is_milestone"] is True


@pytest.mark.asyncio
async def test_math_domain_neighbors():
    """Should return neighbors for a math concept."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/concepts/derivative-concept/neighbors?domain=mathematics")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["nodes"]) > 0
        assert len(data["edges"]) > 0


@pytest.mark.asyncio
async def test_math_domain_in_domain_list():
    """Mathematics should appear in the domain list with correct stats."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/domains")
        assert resp.status_code == 200
        data = resp.json()
        math = next((d for d in data if d["id"] == "mathematics"), None)
        assert math is not None
        assert math["name"] == "数学"
        assert math["icon"] == "🔵"
        assert math["stats"]["total_concepts"] == 269
        assert math["stats"]["total_edges"] == 366
        assert math["stats"]["subdomains"] == 12


@pytest.mark.asyncio
async def test_math_domain_no_orphan_nodes():
    """All math nodes should have at least one edge connection."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=mathematics")
        data = resp.json()
        connected = set()
        for edge in data["edges"]:
            connected.add(edge["source"])
            connected.add(edge["target"])
        node_ids = {n["id"] for n in data["nodes"]}
        orphans = node_ids - connected
        assert len(orphans) == 0, f"Orphan nodes: {orphans}"
