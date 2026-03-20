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


# ── RAG Multi-domain Tests ────────────────────────────────────────


@pytest.mark.asyncio
async def test_rag_default_domain_backwards_compat():
    """RAG stats without domain param should return ai-engineering data."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag")
        assert resp.status_code == 200
        data = resp.json()
        assert data["domain"] == "ai-engineering"
        assert data["total_docs"] == 400


@pytest.mark.asyncio
async def test_rag_math_stats():
    """RAG stats for mathematics domain should return correct counts."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag?domain=mathematics")
        assert resp.status_code == 200
        data = resp.json()
        assert data["domain"] == "mathematics"
        assert data["total_docs"] == 269
        assert data["total_chars"] > 0
        assert len(data["by_subdomain"]) == 12


@pytest.mark.asyncio
async def test_rag_math_document_with_latex():
    """Should fetch a math RAG doc with LaTeX content (templated concept)."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag/derivative-concept?domain=mathematics")
        assert resp.status_code == 200
        data = resp.json()
        assert data["concept_id"] == "derivative-concept"
        assert data["domain"] == "mathematics"
        assert data["is_milestone"] is True
        # Should contain LaTeX formulas
        assert "\\lim" in data["content"] or "lim" in data["content"]
        assert data["char_count"] > 100


@pytest.mark.asyncio
async def test_rag_math_document_generic():
    """Should fetch a generic (non-templated) math RAG doc."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag/decimals?domain=mathematics")
        assert resp.status_code == 200
        data = resp.json()
        assert data["concept_id"] == "decimals"
        assert data["domain"] == "mathematics"
        assert "核心内容" in data["content"]


@pytest.mark.asyncio
async def test_rag_math_404_wrong_domain():
    """Math concept should 404 when queried against ai-engineering RAG."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag/derivative-concept?domain=ai-engineering")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_rag_overlapping_concept_ids():
    """Concepts with same ID in different domains should return different content."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # linear-regression exists in both domains
        resp_ai = await client.get("/api/graph/rag/linear-regression?domain=ai-engineering")
        resp_math = await client.get("/api/graph/rag/linear-regression?domain=mathematics")
        assert resp_ai.status_code == 200
        assert resp_math.status_code == 200
        # They should be different documents
        assert resp_ai.json()["domain"] == "ai-engineering"
        assert resp_math.json()["domain"] == "mathematics"
        assert resp_ai.json()["content"] != resp_math.json()["content"]


# ── English Domain Tests ───────────────────────────

@pytest.mark.asyncio
async def test_english_domain_graph_data():
    """GET /api/graph/data?domain=english should return english concepts."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=english")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["nodes"]) == 200
        assert len(data["edges"]) == 229
        # All nodes should be english domain
        for node in data["nodes"]:
            assert node["domain_id"] == "english"


@pytest.mark.asyncio
async def test_english_domain_node_structure():
    """English nodes should have required fields."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=english")
        data = resp.json()
        node = data["nodes"][0]
        required = {"id", "label", "domain_id", "subdomain_id",
                     "difficulty", "estimated_minutes", "content_type", "tags",
                     "is_milestone"}
        assert required.issubset(set(node.keys()))


@pytest.mark.asyncio
async def test_english_domain_subdomains():
    """English should have 10 subdomains."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/subdomains?domain=english")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 10
        sub_ids = {s["id"] for s in data}
        expected = {"phonetics", "basic-grammar", "vocabulary", "tenses",
                    "sentence-patterns", "advanced-grammar", "reading",
                    "writing-en", "speaking", "idioms-culture"}
        assert sub_ids == expected


@pytest.mark.asyncio
async def test_english_domain_stats():
    """English stats should reflect seed data."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/stats?domain=english")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_concepts"] == 200
        assert data["total_edges"] == 229
        assert data["total_milestones"] == 27


@pytest.mark.asyncio
async def test_english_domain_concept_detail():
    """Should fetch an english concept by ID."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/concepts/present-perfect?domain=english")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "present-perfect"
        assert data["domain_id"] == "english"
        assert data["subdomain_id"] == "tenses"
        assert data["is_milestone"] is True


@pytest.mark.asyncio
async def test_english_domain_neighbors():
    """Should return neighbors for an english concept."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/concepts/adjective-clauses/neighbors?domain=english")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["nodes"]) > 0
        assert len(data["edges"]) > 0


@pytest.mark.asyncio
async def test_english_domain_in_domain_list():
    """English should appear in the domain list with correct stats."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/domains")
        assert resp.status_code == 200
        data = resp.json()
        eng = next((d for d in data if d["id"] == "english"), None)
        assert eng is not None
        assert eng["name"] == "英语"
        assert eng["icon"] == "🟡"
        assert eng["stats"]["total_concepts"] == 200
        assert eng["stats"]["total_edges"] == 229
        assert eng["stats"]["subdomains"] == 10


@pytest.mark.asyncio
async def test_english_domain_subdomain_filter():
    """Filtering by subdomain should return only matching concepts."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=english&subdomain_id=tenses")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["nodes"]) == 20
        for node in data["nodes"]:
            assert node["subdomain_id"] == "tenses"


@pytest.mark.asyncio
async def test_three_domains_listed():
    """Domain list should include all 13 active domains."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/domains")
        assert resp.status_code == 200
        data = resp.json()
        domain_ids = {d["id"] for d in data}
        assert domain_ids == {"ai-engineering", "mathematics", "english", "physics", "product-design", "finance", "psychology", "philosophy", "biology", "economics", "writing", "game-design", "level-design"}


# ── English RAG Tests ───────────────────────────

@pytest.mark.asyncio
async def test_rag_english_stats():
    """English RAG stats should reflect 200 documents."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag?domain=english")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_docs"] == 200
        assert data["domain"] == "english"


@pytest.mark.asyncio
async def test_rag_english_concept():
    """Should return RAG content for an English concept."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag/present-perfect?domain=english")
        assert resp.status_code == 200
        data = resp.json()
        assert data["concept_id"] == "present-perfect"
        assert data["domain"] == "english"
        assert "核心内容" in data["content"]


@pytest.mark.asyncio
async def test_rag_english_404_wrong_domain():
    """English concept should 404 when queried against math RAG."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag/present-perfect?domain=mathematics")
        assert resp.status_code == 404


# ── Cross-Sphere Links (Phase 9.5) ──────────────────────


@pytest.mark.asyncio
async def test_cross_links_all():
    """GET /api/graph/cross-links should return all cross-sphere links."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/cross-links")
        assert resp.status_code == 200
        data = resp.json()
        assert "links" in data
        assert "total" in data
        assert data["total"] >= 20  # We defined 25 links
        # Each link has required fields
        for link in data["links"]:
            assert "source_domain" in link
            assert "source_id" in link
            assert "target_domain" in link
            assert "target_id" in link
            assert "relation" in link
            assert "description" in link


@pytest.mark.asyncio
async def test_cross_links_filter_by_domain():
    """Cross-links should be filterable by domain."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/cross-links?domain=mathematics")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] > 0
        for link in data["links"]:
            assert link["source_domain"] == "mathematics" or link["target_domain"] == "mathematics"


@pytest.mark.asyncio
async def test_cross_links_filter_by_concept():
    """Cross-links should be filterable by concept_id."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/cross-links?concept_id=linear-regression")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1  # linear-regression has same_concept link
        for link in data["links"]:
            assert link["source_id"] == "linear-regression" or link["target_id"] == "linear-regression"


@pytest.mark.asyncio
async def test_cross_links_filter_domain_and_concept():
    """Cross-links should support combined domain + concept filter."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/cross-links?domain=english&concept_id=word-formation")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        for link in data["links"]:
            domain_match = link["source_domain"] == "english" or link["target_domain"] == "english"
            concept_match = link["source_id"] == "word-formation" or link["target_id"] == "word-formation"
            assert domain_match and concept_match


@pytest.mark.asyncio
async def test_cross_links_no_results():
    """Non-existent domain/concept should return empty results."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/cross-links?domain=nonexistent")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["links"] == []


@pytest.mark.asyncio
async def test_cross_links_relation_types():
    """Cross-links should have valid relation types."""
    valid_relations = {"same_concept", "requires", "enables", "applies_to", "related"}
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/cross-links")
        data = resp.json()
        for link in data["links"]:
            assert link["relation"] in valid_relations, f"Invalid relation: {link['relation']}"


@pytest.mark.asyncio
async def test_cross_links_same_concept_pairs():
    """Same_concept links should exist for known overlapping IDs."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/cross-links")
        data = resp.json()
        same_concepts = [lk for lk in data["links"] if lk["relation"] == "same_concept"]
        same_ids = {(lk["source_id"], lk["target_id"]) for lk in same_concepts}
        # linear-regression and gradient-descent should be in same_concept pairs
        assert ("linear-regression", "linear-regression") in same_ids
        assert ("gradient-descent", "gradient-descent") in same_ids


@pytest.mark.asyncio
async def test_cross_links_concepts_exist_in_domains():
    """All concept IDs in cross-links should exist in their respective domain seed graphs."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        links_resp = await client.get("/api/graph/cross-links")
        links = links_resp.json()["links"]

        # Cache domain concept IDs
        domain_concepts = {}
        for domain_id in ["ai-engineering", "mathematics", "english", "physics", "product-design", "finance", "psychology", "philosophy", "biology", "economics", "writing", "game-design", "level-design"]:
            resp = await client.get(f"/api/graph/data?domain={domain_id}")
            data = resp.json()
            domain_concepts[domain_id] = {n["id"] for n in data["nodes"]}

        for link in links:
            src_domain = link["source_domain"]
            src_id = link["source_id"]
            tgt_domain = link["target_domain"]
            tgt_id = link["target_id"]
            assert src_id in domain_concepts.get(src_domain, set()), \
                f"Source concept {src_domain}:{src_id} not found"
            assert tgt_id in domain_concepts.get(tgt_domain, set()), \
                f"Target concept {tgt_domain}:{tgt_id} not found"


# ── Physics Domain Tests (Phase 10.1) ──────────────────────


@pytest.mark.asyncio
async def test_physics_graph_data():
    """Physics domain should return graph data with correct structure."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=physics")
        assert resp.status_code == 200
        data = resp.json()
        assert "nodes" in data
        assert "edges" in data
        assert len(data["nodes"]) >= 190  # ~194 concepts


@pytest.mark.asyncio
async def test_physics_node_count():
    """Physics domain should have ~194 concepts."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=physics")
        data = resp.json()
        assert len(data["nodes"]) >= 190
        assert len(data["edges"]) >= 220


@pytest.mark.asyncio
async def test_physics_subdomains():
    """Physics should have 10 subdomains."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/subdomains?domain=physics")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 10
        sub_ids = {s["id"] for s in data}
        assert "classical-mechanics" in sub_ids
        assert "quantum-mechanics" in sub_ids
        assert "thermodynamics" in sub_ids
        assert "electromagnetism" in sub_ids


@pytest.mark.asyncio
async def test_physics_concept_detail():
    """Should return concept detail for a physics concept."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/concepts/newtons-second-law?domain=physics")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "newtons-second-law"
        assert data["domain_id"] == "physics"
        assert data["subdomain_id"] == "classical-mechanics"


@pytest.mark.asyncio
async def test_physics_stats():
    """Physics domain stats should show correct counts."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/stats?domain=physics")
        assert resp.status_code == 200
        data = resp.json()
        stats = data["stats"]
        assert stats["total_concepts"] >= 190
        assert stats["total_edges"] >= 220
        assert stats["subdomains"] == 10


@pytest.mark.asyncio
async def test_physics_subdomain_filter():
    """Physics should filter by subdomain."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=physics&subdomain_id=classical-mechanics")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["nodes"]) >= 25  # classical-mechanics has 31 concepts
        for node in data["nodes"]:
            assert node["subdomain_id"] == "classical-mechanics"


@pytest.mark.asyncio
async def test_physics_four_domains_listed():
    """Domains endpoint should now include physics."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/domains")
        assert resp.status_code == 200
        data = resp.json()
        domain_ids = {d["id"] for d in data}
        assert "physics" in domain_ids
        physics_domain = [d for d in data if d["id"] == "physics"][0]
        assert physics_domain["name"] == "物理"
        assert physics_domain["color"] == "#22c55e"


# ── Physics RAG Tests (Phase 10.2) ──────────────────────


@pytest.mark.asyncio
async def test_rag_physics_stats():
    """Physics RAG stats should reflect 194 documents."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag?domain=physics")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_docs"] >= 190  # ~194
        assert data["domain"] == "physics"


@pytest.mark.asyncio
async def test_rag_physics_concept():
    """Should return RAG content for a physics concept with LaTeX."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag/newtons-second-law?domain=physics")
        assert resp.status_code == 200
        data = resp.json()
        assert data["concept_id"] == "newtons-second-law"
        assert data["domain"] == "physics"
        assert "F" in data["content"] or "力" in data["content"]


@pytest.mark.asyncio
async def test_rag_physics_latex_content():
    """Physics RAG docs should contain LaTeX formulas."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag/schrodinger-equation?domain=physics")
        assert resp.status_code == 200
        data = resp.json()
        # Should contain LaTeX math notation
        assert "hbar" in data["content"] or "\\hbar" in data["content"] or "$" in data["content"]


@pytest.mark.asyncio
async def test_rag_physics_404_wrong_domain():
    """Physics concept should 404 when queried against math RAG."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag/newtons-second-law?domain=mathematics")
        assert resp.status_code == 404


# ── Product Design Domain Tests (Phase 11.1) ──────────────────────


@pytest.mark.asyncio
async def test_product_design_graph_data():
    """Product Design domain should return graph data with correct structure."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=product-design")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["nodes"]) >= 180
        assert len(data["edges"]) >= 180


@pytest.mark.asyncio
async def test_product_design_node_count():
    """Product Design domain should have 182 concepts."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=product-design")
        data = resp.json()
        assert len(data["nodes"]) == 182


@pytest.mark.asyncio
async def test_product_design_subdomain_filter():
    """Filtering by subdomain should return only matching concepts."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=product-design&subdomain_id=user-research")
        assert resp.status_code == 200
        data = resp.json()
        for node in data["nodes"]:
            assert node["subdomain_id"] == "user-research"
        assert len(data["nodes"]) == 24


@pytest.mark.asyncio
async def test_product_design_subdomains():
    """Product Design should have 8 subdomains."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/subdomains?domain=product-design")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 8


@pytest.mark.asyncio
async def test_product_design_stats():
    """Product Design stats should report correct concept count."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/stats?domain=product-design")
        assert resp.status_code == 200
        data = resp.json()
        assert data["stats"]["total_concepts"] == 182


@pytest.mark.asyncio
async def test_product_design_concept_detail():
    """Should return detail for a product design concept."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/concepts/design-thinking?domain=product-design")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "design-thinking"
        assert data["domain_id"] == "product-design"


@pytest.mark.asyncio
async def test_domains_list_includes_product_design():
    """Domains list should include product-design."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/domains")
        assert resp.status_code == 200
        data = resp.json()
        domain_ids = [d["id"] for d in data]
        assert "product-design" in domain_ids


# ── Product Design RAG Tests (Phase 11.2) ──────────────────────


@pytest.mark.asyncio
async def test_rag_product_design_document():
    """Should return RAG content for a product design concept."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag/design-thinking?domain=product-design")
        assert resp.status_code == 200
        data = resp.json()
        assert data["concept_id"] == "design-thinking"
        assert data["domain"] == "product-design"
        assert len(data["content"]) > 100


@pytest.mark.asyncio
async def test_rag_product_design_stats():
    """Product Design RAG stats should report 182 docs."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag?domain=product-design")
        assert resp.status_code == 200
        data = resp.json()
        assert data["domain"] == "product-design"
        assert data["total_docs"] == 182


@pytest.mark.asyncio
async def test_rag_product_design_404_wrong_domain():
    """Product design concept should 404 when queried against math RAG."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag/design-thinking?domain=mathematics")
        assert resp.status_code == 404


# ── Phase 12: Finance Knowledge Sphere (#8) ──


@pytest.mark.asyncio
async def test_finance_graph_data():
    """Finance graph data loads with concepts and edges."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=finance")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["nodes"]) > 0
        assert len(data["edges"]) > 0


@pytest.mark.asyncio
async def test_finance_node_count():
    """Finance domain has ~160 concepts."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=finance")
        data = resp.json()
        assert len(data["nodes"]) >= 150
        assert len(data["nodes"]) <= 180


@pytest.mark.asyncio
async def test_finance_subdomain_filter():
    """Finance subdomain filter returns relevant concepts only."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=finance&subdomain_id=personal-finance")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["nodes"]) > 0
        for c in data["nodes"]:
            assert c["subdomain_id"] == "personal-finance"
        assert len(data["nodes"]) == 20


@pytest.mark.asyncio
async def test_finance_subdomains():
    """Finance domain has 8 subdomains."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/subdomains?domain=finance")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 8


@pytest.mark.asyncio
async def test_finance_stats():
    """Finance stats endpoint returns valid counts."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/stats?domain=finance")
        assert resp.status_code == 200
        data = resp.json()
        assert data["stats"]["total_concepts"] >= 150
        assert data["stats"]["total_edges"] >= 170


@pytest.mark.asyncio
async def test_finance_concept_detail():
    """Finance concept detail returns valid data."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/concepts/compound-interest?domain=finance")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "compound-interest"
        assert data["domain_id"] == "finance"


@pytest.mark.asyncio
async def test_domains_list_includes_finance():
    """Domains list includes finance as sixth domain."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/domains")
        assert resp.status_code == 200
        data = resp.json()
        domain_ids = [d["id"] for d in data]
        assert "finance" in domain_ids
        assert len(data) >= 6


@pytest.mark.asyncio
async def test_rag_finance_document():
    """Finance RAG document loads for a known concept."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag/compound-interest?domain=finance")
        assert resp.status_code == 200
        data = resp.json()
        assert "content" in data
        assert "复利" in data["content"]


@pytest.mark.asyncio
async def test_rag_finance_stats():
    """Finance RAG stats returns 160 documents."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag?domain=finance")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_docs"] == 160


@pytest.mark.asyncio
async def test_rag_finance_404_wrong_domain():
    """Finance concept should 404 when queried against math RAG."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag/compound-interest?domain=product-design")
        # compound-interest only exists in finance domain RAG
        assert resp.status_code == 404


# ── Psychology Domain Tests (Phase 13.1) ──────────────────────


@pytest.mark.asyncio
async def test_psychology_graph_data():
    """Psychology domain should return graph data with correct structure."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=psychology")
        assert resp.status_code == 200
        data = resp.json()
        assert "nodes" in data
        assert "edges" in data
        assert len(data["nodes"]) == 183
        assert len(data["edges"]) >= 200


@pytest.mark.asyncio
async def test_psychology_node_structure():
    """Psychology concept nodes should have expected fields."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=psychology")
        data = resp.json()
        node = data["nodes"][0]
        assert "id" in node
        assert "label" in node
        assert "subdomain_id" in node
        assert node.get("domain_id") == "psychology"


@pytest.mark.asyncio
async def test_psychology_subdomains():
    """Psychology domain should have 8 subdomains."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/subdomains?domain=psychology")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 8
        subdomain_ids = {s["id"] for s in data}
        assert "cognitive-psychology" in subdomain_ids
        assert "clinical-psychology" in subdomain_ids
        assert "research-methods" in subdomain_ids


@pytest.mark.asyncio
async def test_psychology_stats():
    """Psychology domain stats should reflect seed graph counts."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/stats?domain=psychology")
        assert resp.status_code == 200
        data = resp.json()
        assert data["stats"]["total_concepts"] == 183
        assert data["stats"]["total_edges"] >= 200


@pytest.mark.asyncio
async def test_psychology_concept_detail():
    """Psychology concept detail should return correct data."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/concepts/working-memory?domain=psychology")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "working-memory"
        assert data["name"] == "工作记忆"
        assert data["subdomain_id"] == "cognitive-psychology"


@pytest.mark.asyncio
async def test_psychology_subdomain_filter():
    """Should be able to filter psychology concepts by subdomain."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=psychology&subdomain_id=clinical-psychology")
        assert resp.status_code == 200
        data = resp.json()
        for node in data["nodes"]:
            assert node["subdomain_id"] == "clinical-psychology"
        assert len(data["nodes"]) == 23


@pytest.mark.asyncio
async def test_domains_list_includes_psychology():
    """Domains list includes psychology as seventh domain."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/domains")
        assert resp.status_code == 200
        data = resp.json()
        domain_ids = [d["id"] for d in data]
        assert "psychology" in domain_ids
        assert len(data) >= 7


@pytest.mark.asyncio
async def test_rag_psychology_stats():
    """Psychology RAG stats should reflect 183 documents."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag?domain=psychology")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_docs"] == 183
        assert data["domain"] == "psychology"


@pytest.mark.asyncio
async def test_rag_psychology_concept():
    """Should return RAG content for a psychology concept."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag/working-memory?domain=psychology")
        assert resp.status_code == 200
        data = resp.json()
        assert data["concept_id"] == "working-memory"
        assert data["domain"] == "psychology"
        assert "核心内容" in data["content"]


@pytest.mark.asyncio
async def test_rag_psychology_404_wrong_domain():
    """Psychology concept should 404 when queried against another domain."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag/working-memory?domain=finance")
        assert resp.status_code == 404


# ── Philosophy Domain Tests (Phase 14.1) ──────────────────────


@pytest.mark.asyncio
async def test_philosophy_graph_data():
    """Philosophy domain should return graph data with correct structure."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=philosophy")
        assert resp.status_code == 200
        data = resp.json()
        assert "nodes" in data
        assert "edges" in data
        assert len(data["nodes"]) >= 165  # ~170 concepts


@pytest.mark.asyncio
async def test_philosophy_node_structure():
    """Philosophy nodes should have required fields and domain_id."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=philosophy")
        data = resp.json()
        node = data["nodes"][0]
        assert "id" in node
        assert "label" in node
        assert "subdomain_id" in node
        assert node.get("domain_id") == "philosophy"


@pytest.mark.asyncio
async def test_philosophy_subdomain_count():
    """Philosophy domain should have 8 subdomains."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/subdomains?domain=philosophy")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 8


@pytest.mark.asyncio
async def test_philosophy_concept_detail():
    """Should return details for a philosophy concept."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/concepts/socrates?domain=philosophy")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "socrates"
        assert data["domain_id"] == "philosophy"
        assert "苏格拉底" in data["name"]


@pytest.mark.asyncio
async def test_philosophy_concept_404():
    """Non-existent philosophy concept should 404."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/concepts/nonexistent-phil?domain=philosophy")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_philosophy_neighbors():
    """Should return neighbors for a philosophy concept."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/concepts/plato/neighbors?domain=philosophy&depth=1")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["nodes"]) >= 2  # plato has multiple connections


@pytest.mark.asyncio
async def test_philosophy_stats():
    """Philosophy stats should reflect ~170 concepts."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/stats?domain=philosophy")
        assert resp.status_code == 200
        data = resp.json()
        # Stats endpoint returns meta with stats sub-object
        stats = data.get("stats", data)
        assert stats["total_concepts"] >= 165


@pytest.mark.asyncio
async def test_philosophy_subdomain_filter():
    """Should filter philosophy concepts by subdomain."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=philosophy&subdomain_id=ethics")
        assert resp.status_code == 200
        data = resp.json()
        for node in data["nodes"]:
            assert node["subdomain_id"] == "ethics"
        assert len(data["nodes"]) >= 20  # ~25 ethics concepts


@pytest.mark.asyncio
async def test_philosophy_in_domain_list():
    """Philosophy should appear in the domain list."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/domains")
        data = resp.json()
        phil = [d for d in data if d["id"] == "philosophy"]
        assert len(phil) == 1
        assert phil[0]["name"] == "哲学"


# ── Philosophy RAG Tests (Phase 14.2) ──────────────────────


@pytest.mark.asyncio
async def test_rag_philosophy_stats():
    """Philosophy RAG stats should reflect 170 documents."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag?domain=philosophy")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_docs"] == 170
        assert data["domain"] == "philosophy"


@pytest.mark.asyncio
async def test_rag_philosophy_concept():
    """Should return RAG content for a philosophy concept."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag/socrates?domain=philosophy")
        assert resp.status_code == 200
        data = resp.json()
        assert data["concept_id"] == "socrates"
        assert data["domain"] == "philosophy"
        assert "核心内容" in data["content"]


@pytest.mark.asyncio
async def test_rag_philosophy_404_wrong_domain():
    """Philosophy concept should 404 when queried against another domain."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag/socrates?domain=mathematics")
        assert resp.status_code == 404


# ── Workers Sync Regression ──────────────────────────────────────

def test_workers_seedmap_covers_all_domains():
    """Workers route files must import+register all active domains in seedMap.

    Regression: Phases 15-17 added biology/economics/writing seed data but
    Workers src/routes/{graph,dialogue,learning}.ts were not updated, causing
    404 for those domains on the Cloudflare Workers backend.
    """
    import json
    import os

    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    domains_path = os.path.join(project_root, "data", "seed", "domains.json")
    with open(domains_path, encoding="utf-8") as f:
        all_domains = [d["id"] for d in json.load(f)["domains"] if d.get("is_active", True)]

    workers_route_files = [
        os.path.join(project_root, "workers", "src", "routes", "graph.ts"),
        os.path.join(project_root, "workers", "src", "routes", "dialogue.ts"),
        os.path.join(project_root, "workers", "src", "routes", "learning.ts"),
    ]

    for route_file in workers_route_files:
        assert os.path.exists(route_file), f"Workers route file missing: {route_file}"
        content = open(route_file, encoding="utf-8").read()
        for domain_id in all_domains:
            assert f"'{domain_id}'" in content, (
                f"Domain '{domain_id}' missing from Workers {os.path.basename(route_file)} seedMap. "
                f"When adding a new knowledge sphere, all 3 Workers route files must be updated."
            )


def test_workers_ragmap_covers_all_domains():
    """Workers graph.ts ragMap must include RAG index imports for all domains with RAG data.

    Regression: philosophy/biology/economics/writing RAG indices existed but
    Workers graph.ts had a stub ({ documents: [], stats: {} }) or no entry,
    causing /api/graph/rag/:concept_id to 404 on Workers backend.
    """
    import json
    import os

    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    domains_path = os.path.join(project_root, "data", "seed", "domains.json")
    with open(domains_path, encoding="utf-8") as f:
        all_domains = [d["id"] for d in json.load(f)["domains"] if d.get("is_active", True)]

    graph_ts = os.path.join(project_root, "workers", "src", "routes", "graph.ts")
    content = open(graph_ts, encoding="utf-8").read()

    # Every domain with a RAG _index.json should have a real import in graph.ts (not a stub)
    for domain_id in all_domains:
        rag_index = os.path.join(project_root, "data", "rag", domain_id, "_index.json")
        if os.path.exists(rag_index):
            # Check it's imported (not a stub with empty documents/stats)
            assert f"rag/{domain_id}/_index.json" in content or f"rag/{domain_id.replace('-', '')}/_index.json" in content, (
                f"RAG index for '{domain_id}' exists but is not imported in Workers graph.ts. "
                f"Add: import ragXxx from '../../data/rag/{domain_id}/_index.json';"
            )


def test_workers_data_directory_synced():
    """Workers data/ directory must contain seed_graph.json for all domains.

    The Workers import seed data at build time. If workers/data/seed/{domain}/
    is missing, the build will fail with import resolution errors.
    """
    import json
    import os

    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    domains_path = os.path.join(project_root, "data", "seed", "domains.json")
    with open(domains_path, encoding="utf-8") as f:
        all_domains = [d["id"] for d in json.load(f)["domains"] if d.get("is_active", True)]

    for domain_id in all_domains:
        seed_file = os.path.join(project_root, "workers", "data", "seed", domain_id, "seed_graph.json")
        assert os.path.exists(seed_file), (
            f"Workers data/seed/{domain_id}/seed_graph.json missing. "
            f"Copy from data/seed/{domain_id}/ to workers/data/seed/{domain_id}/"
        )


# ── Three-Way Supplement Sync Regression ───────────────────────────


def _extract_ts_map_keys(content: str, map_name: str) -> set:
    """Extract keys from a TypeScript `const MAP_NAME: Record<string, string> = { ... };` block.

    Works for both inline template-literal values (``'key': `...`,``) and
    const-reference values (``'key': CONST_NAME,``).
    """
    import re

    # Locate the block:  const MAP_NAME: Record<string, string> = { ... };
    pattern = re.compile(
        rf"const\s+{re.escape(map_name)}\s*:\s*Record<string,\s*string>\s*=\s*\{{(.*?)\}};",
        re.DOTALL,
    )
    m = pattern.search(content)
    assert m, f"Could not find '{map_name}' map block in TypeScript source"
    block = m.group(1)
    # Keys are always single-quoted identifiers at the start of each entry
    return set(re.findall(r"'([\w-]+)'\s*:", block))


def test_domain_supplements_three_way_sync():
    """DOMAIN_SUPPLEMENTS keys must be identical across BE, FE, and Workers.

    Regression: Round 71 found FE direct-llm.ts missing economics+writing;
    Round 72 found Workers prompts.ts missing biology/economics/writing.
    This test catches any future drift between the three codebases.
    """
    import os

    project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )

    # BE: read from Python dict
    from engines.dialogue.prompts.feynman_system import DOMAIN_SUPPLEMENTS
    be_keys = set(DOMAIN_SUPPLEMENTS.keys())

    # FE: parse direct-llm.ts DOMAIN_SUPPLEMENTS map block
    fe_file = os.path.join(project_root, "packages", "web", "src", "lib", "direct-llm.ts")
    assert os.path.exists(fe_file), f"FE direct-llm.ts not found: {fe_file}"
    fe_content = open(fe_file, encoding="utf-8").read()
    fe_keys = _extract_ts_map_keys(fe_content, "DOMAIN_SUPPLEMENTS")

    # Workers: parse prompts.ts DOMAIN_SUPPLEMENTS map block
    workers_file = os.path.join(project_root, "workers", "src", "prompts.ts")
    assert os.path.exists(workers_file), f"Workers prompts.ts not found: {workers_file}"
    workers_content = open(workers_file, encoding="utf-8").read()
    workers_keys = _extract_ts_map_keys(workers_content, "DOMAIN_SUPPLEMENTS")

    # All three should have the same set of domain keys
    assert be_keys == workers_keys, (
        f"BE vs Workers DOMAIN_SUPPLEMENTS mismatch.\n"
        f"  BE only: {be_keys - workers_keys}\n"
        f"  Workers only: {workers_keys - be_keys}"
    )
    assert be_keys == fe_keys, (
        f"BE vs FE DOMAIN_SUPPLEMENTS mismatch.\n"
        f"  BE only: {be_keys - fe_keys}\n"
        f"  FE only: {fe_keys - be_keys}"
    )


def test_assessment_supplements_three_way_sync():
    """ASSESSMENT_SUPPLEMENTS keys must be identical across BE, FE, and Workers."""
    import os

    project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )

    # BE
    from engines.dialogue.prompts.feynman_system import ASSESSMENT_SUPPLEMENTS
    be_keys = set(ASSESSMENT_SUPPLEMENTS.keys())

    # FE: parse ASSESSMENT_SUPPLEMENTS map block in direct-llm.ts
    fe_file = os.path.join(project_root, "packages", "web", "src", "lib", "direct-llm.ts")
    fe_content = open(fe_file, encoding="utf-8").read()
    fe_keys = _extract_ts_map_keys(fe_content, "ASSESSMENT_SUPPLEMENTS")

    # Workers: parse ASSESSMENT_SUPPLEMENTS map block in prompts.ts
    workers_file = os.path.join(project_root, "workers", "src", "prompts.ts")
    workers_content = open(workers_file, encoding="utf-8").read()
    workers_keys = _extract_ts_map_keys(workers_content, "ASSESSMENT_SUPPLEMENTS")

    assert be_keys == workers_keys, (
        f"BE vs Workers ASSESSMENT_SUPPLEMENTS mismatch.\n"
        f"  BE only: {be_keys - workers_keys}\n"
        f"  Workers only: {workers_keys - be_keys}"
    )
    assert be_keys == fe_keys, (
        f"BE vs FE ASSESSMENT_SUPPLEMENTS mismatch.\n"
        f"  BE only: {be_keys - fe_keys}\n"
        f"  FE only: {fe_keys - be_keys}"
    )


# ── Workers Opening Domain-Neutral Regression ─────────────────────

def test_workers_opening_domain_neutral():
    """Workers dialogue opening messages must be domain-neutral (no '编程' reference).

    Regression: Round 78 found getOpening() contained '编程中很基础' (basic in programming),
    which misleads non-CS domains (biology, economics, writing, etc.).
    BE and FE both use domain-neutral openings; Workers must match.
    """
    import os

    project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
    dialogue_file = os.path.join(project_root, "workers", "src", "routes", "dialogue.ts")
    assert os.path.exists(dialogue_file), f"Workers dialogue.ts not found: {dialogue_file}"
    content = open(dialogue_file, encoding="utf-8").read()

    # Extract the getOpening function body (between "function getOpening" and closing "}")
    import re
    m = re.search(r"function getOpening\b.*?\n\}", content, re.DOTALL)
    assert m, "getOpening function not found in workers/src/routes/dialogue.ts"
    fn_body = m.group(0)

    # Domain-specific terms that should NOT appear in generic opening messages
    forbidden_terms = ["编程", "代码", "programming", "coding"]
    for term in forbidden_terms:
        assert term not in fn_body, (
            f"Workers getOpening() contains domain-specific term '{term}'. "
            f"Opening messages must be domain-neutral for all 11 domains."
        )
