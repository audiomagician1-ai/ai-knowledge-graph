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
        assert domain["name"] == "AI编程"
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
        assert len(data["by_subdomain"]) >= 12  # 12 canonical + possible extras from frontmatter


@pytest.mark.asyncio
async def test_rag_math_document_with_latex():
    """Should fetch a math RAG doc with concept-specific content (milestone concept)."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag/derivative-concept?domain=mathematics")
        assert resp.status_code == 200
        data = resp.json()
        assert data["concept_id"] == "derivative-concept"
        assert data["domain"] == "mathematics"
        assert data["is_milestone"] is True
        # Should contain concept-specific content (导数 = derivative)
        assert "导数" in data["content"] or "derivative" in data["content"].lower()
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
        assert "核心内容" in data["content"] or "核心知识点" in data["content"] or "## " in data["content"]


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
    """Domain list should include all 36 active domains."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/domains")
        assert resp.status_code == 200
        data = resp.json()
        domain_ids = {d["id"] for d in data}
        assert domain_ids == {"ai-engineering", "mathematics", "english", "physics", "product-design", "finance", "psychology", "philosophy", "biology", "economics", "writing", "game-design", "level-design", "game-engine", "software-engineering", "computer-graphics", "3d-art", "concept-design", "animation", "technical-art", "vfx", "game-audio-music", "game-ui-ux", "narrative-design", "multiplayer-network", "game-audio-sfx", "game-publishing", "game-live-ops", "game-qa", "game-production", "systems-theory", "cybernetics", "information-theory", "dissipative-structures", "synergetics", "catastrophe-theory"}


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
        assert "核心内容" in data["content"] or "核心知识点" in data["content"] or "## " in data["content"]


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
    valid_relations = {"same_concept", "shared_concept", "requires", "enables", "applies_to", "applied_in", "foundational", "supports", "related", "related_to", "applies", "impacts", "prerequisite", "teaches"}
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
        for domain_id in ["ai-engineering", "mathematics", "english", "physics", "product-design", "finance", "psychology", "philosophy", "biology", "economics", "writing", "game-design", "level-design", "game-engine", "software-engineering", "computer-graphics", "3d-art", "concept-design", "animation", "technical-art", "vfx", "game-audio-music", "game-ui-ux", "narrative-design", "multiplayer-network", "game-audio-sfx", "game-publishing", "game-live-ops", "game-qa", "game-production", "systems-theory", "cybernetics", "information-theory", "dissipative-structures", "synergetics", "catastrophe-theory"]:
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
    """Should return RAG content for a physics concept."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag/newtons-second-law?domain=physics")
        assert resp.status_code == 200
        data = resp.json()
        assert data["concept_id"] == "newtons-second-law"
        assert data["domain"] == "physics"
        # Should contain concept-specific content (Newton's second law)
        assert "牛顿" in data["content"] or "Newton" in data["content"] or "F" in data["content"] or "力" in data["content"]


@pytest.mark.asyncio
async def test_rag_physics_latex_content():
    """Physics RAG docs should contain concept-specific content."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag/schrodinger-equation?domain=physics")
        assert resp.status_code == 200
        data = resp.json()
        # Should contain concept-specific content (Schrödinger equation)
        assert "薛定谔" in data["content"] or "Schrodinger" in data["content"] or "波函数" in data["content"]


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
        assert "核心内容" in data["content"] or "核心知识点" in data["content"] or "## " in data["content"]


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
        assert "核心内容" in data["content"] or "核心知识点" in data["content"] or "## " in data["content"]


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
    """Workers dialogue fallback opening messages must be domain-neutral (no '编程' reference).

    Regression: Round 78 found old getOpening() contained '编程中很基础' (basic in programming),
    which misleads non-CS domains (biology, economics, writing, etc.).
    V2: getOpening replaced by getFallbackOpening (LLM-first with fallback).
    """
    import os

    project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
    dialogue_file = os.path.join(project_root, "workers", "src", "routes", "dialogue.ts")
    assert os.path.exists(dialogue_file), f"Workers dialogue.ts not found: {dialogue_file}"
    content = open(dialogue_file, encoding="utf-8").read()

    # V2: getFallbackOpening replaces old getOpening
    import re
    m = re.search(r"function getFallbackOpening\b.*?\n\}", content, re.DOTALL)
    assert m, "getFallbackOpening function not found in workers/src/routes/dialogue.ts"
    fn_body = m.group(0)

    # Domain-specific terms that should NOT appear in generic opening messages
    forbidden_terms = ["编程", "代码", "programming", "coding"]
    for term in forbidden_terms:
        assert term not in fn_body, (
            f"Workers getFallbackOpening() contains domain-specific term '{term}'. "
            f"Opening messages must be domain-neutral for all domains."
        )

    # V2: Verify opening_choices is returned in the /conversations response
    assert "opening_choices" in content, (
        "Workers dialogue.ts must return opening_choices in /conversations response"
    )


# ── Level Design Integration Tests (Phase 19.6) ─────────────────


@pytest.mark.asyncio
async def test_level_design_seed_graph_integrity():
    """Level-design seed graph: 200 concepts, 213 edges, 10 subdomains, 28 milestones."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=level-design")
        assert resp.status_code == 200
        data = resp.json()
        nodes = data["nodes"]
        edges = data["edges"]
        assert len(nodes) == 200, f"Expected 200 concepts, got {len(nodes)}"
        assert len(edges) == 213, f"Expected 213 edges, got {len(edges)}"
        subdomain_ids = set(n["subdomain_id"] for n in nodes)
        assert len(subdomain_ids) == 10, f"Expected 10 subdomains, got {len(subdomain_ids)}"
        milestones = [n for n in nodes if n.get("is_milestone")]
        assert len(milestones) == 28, f"Expected 28 milestones, got {len(milestones)}"


@pytest.mark.asyncio
async def test_level_design_subdomains():
    """Level-design should have 10 subdomains with correct names."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/subdomains?domain=level-design")
        assert resp.status_code == 200
        subs = resp.json()
        sub_ids = {s["id"] for s in subs}
        expected = {
            "spatial-narrative", "pacing-curve", "guidance-design", "blockout",
            "metrics-design", "combat-space", "level-editor", "terrain-design",
            "lighting-narrative", "ld-documentation",
        }
        assert sub_ids == expected, f"Subdomain mismatch: {sub_ids ^ expected}"


@pytest.mark.asyncio
async def test_rag_level_design_stats():
    """Level-design RAG stats should reflect 200 documents."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag?domain=level-design")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_docs"] == 200
        assert data["domain"] == "level-design"
        assert len(data.get("by_subdomain", {})) >= 10


@pytest.mark.asyncio
async def test_rag_level_design_concept():
    """Should return RAG content for a level-design concept."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag/ld-overview?domain=level-design")
        assert resp.status_code == 200
        data = resp.json()
        assert data["concept_id"] == "ld-overview"
        assert data["domain"] == "level-design"
        assert "核心内容" in data["content"] or "核心知识点" in data["content"] or "## " in data["content"]


@pytest.mark.asyncio
async def test_rag_level_design_404_wrong_domain():
    """Level-design concept should 404 when queried against another domain."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag/ld-overview?domain=mathematics")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_level_design_cross_sphere_links():
    """Cross-sphere links for level-design should exist (game-design ↔ level-design)."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/cross-links?domain=level-design")
        assert resp.status_code == 200
        data = resp.json()
        links = data["links"]
        assert len(links) >= 15, f"Expected >= 15 cross-links, got {len(links)}"
        # Should have links involving game-design
        partner_domains = set()
        for lk in links:
            partner_domains.add(lk.get("source_domain", ""))
            partner_domains.add(lk.get("target_domain", ""))
        assert "game-design" in partner_domains, "Expected cross-links with game-design"


@pytest.mark.asyncio
async def test_level_design_domain_supplements():
    """Level-design should have domain supplements in BE evaluation system."""
    from engines.dialogue.prompts.feynman_system import DOMAIN_SUPPLEMENTS, ASSESSMENT_SUPPLEMENTS
    assert "level-design" in DOMAIN_SUPPLEMENTS, "level-design missing from DOMAIN_SUPPLEMENTS"
    assert "level-design" in ASSESSMENT_SUPPLEMENTS, "level-design missing from ASSESSMENT_SUPPLEMENTS"
    assert "关卡" in DOMAIN_SUPPLEMENTS["level-design"], "Level-design supplement should mention 关卡"


# ─── Phase 20: Game Engine integration tests ───


@pytest.mark.asyncio
async def test_game_engine_seed_graph_integrity():
    """Game-engine seed graph: 300 concepts, 319 edges, 15 subdomains, 44 milestones."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=game-engine")
        assert resp.status_code == 200
        data = resp.json()
        nodes = data["nodes"]
        edges = data["edges"]
        assert len(nodes) == 300, f"Expected 300 concepts, got {len(nodes)}"
        assert len(edges) == 319, f"Expected 319 edges, got {len(edges)}"
        subdomain_ids = set(n["subdomain_id"] for n in nodes)
        assert len(subdomain_ids) == 15, f"Expected 15 subdomains, got {len(subdomain_ids)}"
        milestones = [n for n in nodes if n.get("is_milestone")]
        assert len(milestones) == 44, f"Expected 44 milestones, got {len(milestones)}"


@pytest.mark.asyncio
async def test_game_engine_subdomains():
    """Game-engine should have 15 subdomains with correct IDs."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/subdomains?domain=game-engine")
        assert resp.status_code == 200
        subs = resp.json()
        sub_ids = {s["id"] for s in subs}
        expected = {
            "ue5-architecture", "unity-architecture", "rendering-pipeline",
            "physics-engine", "animation-system", "audio-system", "input-system",
            "resource-management", "scene-management", "serialization",
            "scripting-system", "editor-extension", "plugin-development",
            "platform-abstraction", "performance-profiling",
        }
        assert sub_ids == expected, f"Subdomain mismatch: {sub_ids ^ expected}"


@pytest.mark.asyncio
async def test_rag_game_engine_stats():
    """Game-engine RAG stats should reflect 300 documents across 15 subdomains."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag?domain=game-engine")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_docs"] == 300
        assert data["domain"] == "game-engine"
        assert len(data.get("by_subdomain", {})) >= 15


@pytest.mark.asyncio
async def test_rag_game_engine_concept():
    """Should return RAG content for a game-engine concept."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag/ge-overview?domain=game-engine")
        assert resp.status_code == 200
        data = resp.json()
        assert data["concept_id"] == "ge-overview"
        assert data["domain"] == "game-engine"
        assert "核心内容" in data["content"] or "核心知识点" in data["content"] or "## " in data["content"]


@pytest.mark.asyncio
async def test_rag_game_engine_404_wrong_domain():
    """Game-engine concept should 404 when queried against another domain."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag/ge-overview?domain=mathematics")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_game_engine_cross_sphere_links():
    """Cross-sphere links for game-engine should exist (game-engine ↔ game-design/level-design)."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/cross-links?domain=game-engine")
        assert resp.status_code == 200
        data = resp.json()
        links = data["links"]
        assert len(links) >= 25, f"Expected >= 25 cross-links, got {len(links)}"
        partner_domains = set()
        for lk in links:
            partner_domains.add(lk.get("source_domain", ""))
            partner_domains.add(lk.get("target_domain", ""))
        assert "game-design" in partner_domains, "Expected cross-links with game-design"
        assert "level-design" in partner_domains, "Expected cross-links with level-design"


@pytest.mark.asyncio
async def test_game_engine_domain_supplements():
    """Game-engine should have domain supplements in BE evaluation system."""
    from engines.dialogue.prompts.feynman_system import DOMAIN_SUPPLEMENTS, ASSESSMENT_SUPPLEMENTS
    assert "game-engine" in DOMAIN_SUPPLEMENTS, "game-engine missing from DOMAIN_SUPPLEMENTS"
    assert "game-engine" in ASSESSMENT_SUPPLEMENTS, "game-engine missing from ASSESSMENT_SUPPLEMENTS"
    assert "引擎" in DOMAIN_SUPPLEMENTS["game-engine"], "Game-engine supplement should mention 引擎"


# ─── Phase 21: Software Engineering integration tests ───


@pytest.mark.asyncio
async def test_software_engineering_seed_graph_integrity():
    """Software-engineering seed graph: 280 concepts, 398 edges, 14 subdomains, 47 milestones."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=software-engineering")
        assert resp.status_code == 200
        data = resp.json()
        nodes = data["nodes"]
        edges = data["edges"]
        assert len(nodes) == 280, f"Expected 280 concepts, got {len(nodes)}"
        assert len(edges) == 398, f"Expected 398 edges, got {len(edges)}"
        subdomain_ids = set(n["subdomain_id"] for n in nodes)
        assert len(subdomain_ids) == 14, f"Expected 14 subdomains, got {len(subdomain_ids)}"
        milestones = [n for n in nodes if n.get("is_milestone")]
        assert len(milestones) == 47, f"Expected 47 milestones, got {len(milestones)}"


@pytest.mark.asyncio
async def test_software_engineering_subdomains():
    """Software-engineering should have 14 subdomains with correct IDs."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/subdomains?domain=software-engineering")
        assert resp.status_code == 200
        subs = resp.json()
        sub_ids = {s["id"] for s in subs}
        expected = {
            "architecture-patterns", "design-patterns", "version-control",
            "ci-cd", "code-review", "tdd", "performance-analysis",
            "refactoring", "game-programming-patterns", "ecs-architecture",
            "memory-management", "multithreading", "build-systems",
            "package-management",
        }
        assert sub_ids == expected, f"Subdomain mismatch: {sub_ids ^ expected}"


@pytest.mark.asyncio
async def test_rag_software_engineering_stats():
    """Software-engineering RAG stats should reflect 280 documents across 14 subdomains."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag?domain=software-engineering")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_docs"] == 280
        assert data["domain"] == "software-engineering"
        assert len(data.get("by_subdomain", {})) >= 14


@pytest.mark.asyncio
async def test_rag_software_engineering_concept():
    """Should return RAG content for a software-engineering concept."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag/se-arch-intro?domain=software-engineering")
        assert resp.status_code == 200
        data = resp.json()
        assert data["concept_id"] == "se-arch-intro"
        assert data["domain"] == "software-engineering"
        assert "核心内容" in data["content"] or "核心知识点" in data["content"] or "## " in data["content"]


@pytest.mark.asyncio
async def test_rag_software_engineering_404_wrong_domain():
    """Software-engineering concept should 404 when queried against another domain."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag/se-arch-intro?domain=mathematics")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_software_engineering_cross_sphere_links():
    """Cross-sphere links for software-engineering should exist (SE ↔ game-engine/game-design/level-design)."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/cross-links?domain=software-engineering")
        assert resp.status_code == 200
        data = resp.json()
        links = data["links"]
        assert len(links) >= 25, f"Expected >= 25 cross-links, got {len(links)}"
        partner_domains = set()
        for lk in links:
            partner_domains.add(lk.get("source_domain", ""))
            partner_domains.add(lk.get("target_domain", ""))
        assert "game-engine" in partner_domains, "Expected cross-links with game-engine"
        assert "game-design" in partner_domains, "Expected cross-links with game-design"


@pytest.mark.asyncio
async def test_software_engineering_domain_supplements():
    """Software-engineering should have domain supplements in BE evaluation system."""
    from engines.dialogue.prompts.feynman_system import DOMAIN_SUPPLEMENTS, ASSESSMENT_SUPPLEMENTS
    assert "software-engineering" in DOMAIN_SUPPLEMENTS, "software-engineering missing from DOMAIN_SUPPLEMENTS"
    assert "software-engineering" in ASSESSMENT_SUPPLEMENTS, "software-engineering missing from ASSESSMENT_SUPPLEMENTS"
    assert "SOLID" in DOMAIN_SUPPLEMENTS["software-engineering"], "SE supplement should mention SOLID"


# ============================================================
# Phase 22 — Computer Graphics knowledge sphere
# ============================================================

@pytest.mark.asyncio
async def test_computer_graphics_seed_graph_integrity():
    """Computer-graphics seed graph: 250 concepts, 241 edges, 12 subdomains, 56 milestones."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=computer-graphics")
        assert resp.status_code == 200
        data = resp.json()
        nodes = data["nodes"]
        edges = data["edges"]
        assert len(nodes) == 250, f"Expected 250 concepts, got {len(nodes)}"
        assert len(edges) == 241, f"Expected 241 edges, got {len(edges)}"
        subdomain_ids = set(n["subdomain_id"] for n in nodes)
        assert len(subdomain_ids) == 12, f"Expected 12 subdomains, got {len(subdomain_ids)}"
        milestones = [n for n in nodes if n.get("is_milestone")]
        assert len(milestones) == 56, f"Expected 56 milestones, got {len(milestones)}"


@pytest.mark.asyncio
async def test_computer_graphics_subdomains():
    """Computer-graphics should have 12 subdomains with correct IDs."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/subdomains?domain=computer-graphics")
        assert resp.status_code == 200
        subs = resp.json()
        sub_ids = {s["id"] for s in subs}
        expected = {
            "rasterization", "ray-tracing", "pbr-materials",
            "global-illumination", "post-processing", "gpu-architecture",
            "shader-programming", "texture-techniques", "geometry-processing",
            "volume-rendering", "anti-aliasing", "render-optimization",
        }
        assert sub_ids == expected, f"Subdomain mismatch: {sub_ids ^ expected}"


@pytest.mark.asyncio
async def test_rag_computer_graphics_stats():
    """Computer-graphics RAG stats should reflect 250 documents across 12 subdomains."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag?domain=computer-graphics")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_docs"] == 250
        assert data["domain"] == "computer-graphics"
        assert len(data.get("by_subdomain", {})) >= 12


@pytest.mark.asyncio
async def test_rag_computer_graphics_concept():
    """Should return RAG content for a computer-graphics concept."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag/cg-raster-intro?domain=computer-graphics")
        assert resp.status_code == 200
        data = resp.json()
        assert data["concept_id"] == "cg-raster-intro"
        assert data["domain"] == "computer-graphics"
        assert "核心内容" in data["content"] or "核心知识点" in data["content"] or "## " in data["content"]


@pytest.mark.asyncio
async def test_rag_computer_graphics_404_wrong_domain():
    """Computer-graphics concept should 404 when queried against another domain."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag/cg-raster-intro?domain=mathematics")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_computer_graphics_cross_sphere_links():
    """Cross-sphere links for computer-graphics should exist (CG ↔ game-engine/game-design/math/SE)."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/cross-links?domain=computer-graphics")
        assert resp.status_code == 200
        data = resp.json()
        links = data["links"]
        assert len(links) >= 25, f"Expected >= 25 cross-links, got {len(links)}"
        partner_domains = set()
        for lk in links:
            partner_domains.add(lk.get("source_domain", ""))
            partner_domains.add(lk.get("target_domain", ""))
        assert "game-engine" in partner_domains, "Expected cross-links with game-engine"


@pytest.mark.asyncio
async def test_computer_graphics_domain_supplements():
    """Computer-graphics should have domain supplements in BE evaluation system."""
    from engines.dialogue.prompts.feynman_system import DOMAIN_SUPPLEMENTS, ASSESSMENT_SUPPLEMENTS
    assert "computer-graphics" in DOMAIN_SUPPLEMENTS, "computer-graphics missing from DOMAIN_SUPPLEMENTS"
    assert "computer-graphics" in ASSESSMENT_SUPPLEMENTS, "computer-graphics missing from ASSESSMENT_SUPPLEMENTS"
    assert "Shader" in DOMAIN_SUPPLEMENTS["computer-graphics"], "CG supplement should mention Shader"


# ============================ 3D Art (Phase 23) ============================

@pytest.mark.asyncio
async def test_3d_art_seed_graph_integrity():
    """3D Art seed graph: 226 concepts, 239 edges, 12 subdomains, 31 milestones."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=3d-art")
        assert resp.status_code == 200
        data = resp.json()
        nodes = data["nodes"]
        edges = data["edges"]
        assert len(nodes) == 226, f"Expected 226 concepts, got {len(nodes)}"
        assert len(edges) == 239, f"Expected 239 edges, got {len(edges)}"
        subdomain_ids = set(n["subdomain_id"] for n in nodes)
        assert len(subdomain_ids) == 12, f"Expected 12 subdomains, got {len(subdomain_ids)}"
        milestones = [n for n in nodes if n.get("is_milestone")]
        assert len(milestones) == 31, f"Expected 31 milestones, got {len(milestones)}"


@pytest.mark.asyncio
async def test_3d_art_subdomains():
    """3D Art should have 12 subdomains with correct IDs."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/subdomains?domain=3d-art")
        assert resp.status_code == 200
        subs = resp.json()
        sub_ids = {s["id"] for s in subs}
        expected = {
            "modeling-fundamentals", "hard-surface", "organic-modeling",
            "sculpting", "retopology", "uv-unwrapping",
            "texturing", "baking", "rigging",
            "environment-art", "prop-art", "asset-pipeline",
        }
        assert sub_ids == expected, f"Subdomain mismatch: {sub_ids ^ expected}"


@pytest.mark.asyncio
async def test_rag_3d_art_stats():
    """3D Art RAG stats should reflect 226 documents across 12 subdomains."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag?domain=3d-art")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_docs"] == 226
        assert data["domain"] == "3d-art"
        assert len(data.get("by_subdomain", {})) >= 12


@pytest.mark.asyncio
async def test_rag_3d_art_concept():
    """Should return RAG content for a 3d-art concept."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag/3da-modeling-intro?domain=3d-art")
        assert resp.status_code == 200
        data = resp.json()
        assert data["concept_id"] == "3da-modeling-intro"
        assert data["domain"] == "3d-art"
        assert "建模" in data["content"]


@pytest.mark.asyncio
async def test_rag_3d_art_404_wrong_domain():
    """3D Art concept should 404 when queried against another domain."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag/3da-modeling-intro?domain=mathematics")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_3d_art_cross_sphere_links():
    """Cross-sphere links for 3d-art should exist (3d-art ↔ CG/game-engine/level-design)."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/cross-links?domain=3d-art")
        assert resp.status_code == 200
        data = resp.json()
        links = data["links"]
        assert len(links) >= 15, f"Expected >= 15 cross-links, got {len(links)}"
        partner_domains = set()
        for lk in links:
            partner_domains.add(lk.get("source_domain", ""))
            partner_domains.add(lk.get("target_domain", ""))
        assert "computer-graphics" in partner_domains, "Expected cross-links with computer-graphics"


@pytest.mark.asyncio
async def test_3d_art_domain_supplements():
    """3D Art should have domain supplements in BE evaluation system."""
    from engines.dialogue.prompts.feynman_system import DOMAIN_SUPPLEMENTS, ASSESSMENT_SUPPLEMENTS
    assert "3d-art" in DOMAIN_SUPPLEMENTS, "3d-art missing from DOMAIN_SUPPLEMENTS"
    assert "3d-art" in ASSESSMENT_SUPPLEMENTS, "3d-art missing from ASSESSMENT_SUPPLEMENTS"
    assert "管线" in DOMAIN_SUPPLEMENTS["3d-art"], "3D Art supplement should mention 管线"


# ---------------------------------------------------------------------------
# Phase 24 — Concept Design knowledge sphere tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_concept_design_seed_graph_integrity():
    """Concept Design seed graph: 220 concepts, 240 edges, 11 subdomains, 39 milestones."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=concept-design")
        assert resp.status_code == 200
        data = resp.json()
        nodes = data["nodes"]
        edges = data["edges"]
        assert len(nodes) == 220, f"Expected 220 concepts, got {len(nodes)}"
        assert len(edges) == 240, f"Expected 240 edges, got {len(edges)}"
        subdomain_ids = set(n["subdomain_id"] for n in nodes)
        assert len(subdomain_ids) == 11, f"Expected 11 subdomains, got {len(subdomain_ids)}"
        milestones = [n for n in nodes if n.get("is_milestone")]
        assert len(milestones) == 39, f"Expected 39 milestones, got {len(milestones)}"


@pytest.mark.asyncio
async def test_concept_design_subdomains():
    """Concept Design should have 11 subdomains with correct IDs."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/subdomains?domain=concept-design")
        assert resp.status_code == 200
        subs = resp.json()
        sub_ids = {s["id"] for s in subs}
        expected = {
            "anatomy-sketching", "perspective", "color-theory",
            "composition", "light-shadow", "character-design",
            "environment-design", "prop-design", "visual-development",
            "style-guide", "moodboard-ref",
        }
        assert sub_ids == expected, f"Subdomain mismatch: {sub_ids ^ expected}"


@pytest.mark.asyncio
async def test_rag_concept_design_stats():
    """Concept Design RAG stats should reflect 220 documents across 11 subdomains."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag?domain=concept-design")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_docs"] == 220
        assert data["domain"] == "concept-design"
        assert len(data.get("by_subdomain", {})) >= 11


@pytest.mark.asyncio
async def test_rag_concept_design_concept():
    """Should return RAG content for a concept-design concept."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag/cd-anatomy-intro?domain=concept-design")
        assert resp.status_code == 200
        data = resp.json()
        assert data["concept_id"] == "cd-anatomy-intro"
        assert data["domain"] == "concept-design"
        assert "解剖" in data["content"]


@pytest.mark.asyncio
async def test_rag_concept_design_404_wrong_domain():
    """Concept Design concept should 404 when queried against another domain."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag/cd-anatomy-intro?domain=mathematics")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_concept_design_cross_sphere_links():
    """Cross-sphere links for concept-design should exist (concept-design ↔ 3d-art/game-design/level-design)."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/cross-links?domain=concept-design")
        assert resp.status_code == 200
        data = resp.json()
        links = data["links"]
        assert len(links) >= 20, f"Expected >= 20 cross-links, got {len(links)}"
        partner_domains = set()
        for lk in links:
            partner_domains.add(lk.get("source_domain", ""))
            partner_domains.add(lk.get("target_domain", ""))
        assert "3d-art" in partner_domains, "Expected cross-links with 3d-art"
        assert "game-design" in partner_domains, "Expected cross-links with game-design"


@pytest.mark.asyncio
async def test_concept_design_domain_supplements():
    """Concept Design should have domain supplements in BE evaluation system."""
    from engines.dialogue.prompts.feynman_system import DOMAIN_SUPPLEMENTS, ASSESSMENT_SUPPLEMENTS
    assert "concept-design" in DOMAIN_SUPPLEMENTS, "concept-design missing from DOMAIN_SUPPLEMENTS"
    assert "concept-design" in ASSESSMENT_SUPPLEMENTS, "concept-design missing from ASSESSMENT_SUPPLEMENTS"
    assert "形状语言" in DOMAIN_SUPPLEMENTS["concept-design"], "Concept Design supplement should mention 形状语言"


# ========================= Phase 25: Animation Integration Tests =========================

@pytest.mark.asyncio
async def test_animation_seed_graph_integrity():
    """Animation seed graph: 180 concepts, 184 edges, 10 subdomains, 36 milestones."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=animation")
        assert resp.status_code == 200
        data = resp.json()
        nodes = data["nodes"]
        edges = data["edges"]
        assert len(nodes) == 180, f"Expected 180 concepts, got {len(nodes)}"
        assert len(edges) == 184, f"Expected 184 edges, got {len(edges)}"
        subdomain_ids = set(n["subdomain_id"] for n in nodes)
        assert len(subdomain_ids) == 10, f"Expected 10 subdomains, got {len(subdomain_ids)}"
        milestones = [n for n in nodes if n.get("is_milestone")]
        assert len(milestones) == 36, f"Expected 36 milestones, got {len(milestones)}"


@pytest.mark.asyncio
async def test_animation_subdomains():
    """Animation should have 10 subdomains with correct IDs."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/subdomains?domain=animation")
        assert resp.status_code == 200
        subs = resp.json()
        sub_ids = {s["id"] for s in subs}
        expected = {
            "animation-principles", "skeletal-rigging", "keyframe-animation",
            "motion-capture", "state-machine", "blend-space",
            "ik-fk", "facial-animation", "animation-blueprint",
            "physics-animation",
        }
        assert sub_ids == expected, f"Subdomain mismatch: {sub_ids ^ expected}"


@pytest.mark.asyncio
async def test_rag_animation_stats():
    """Animation RAG stats should reflect 180 documents across 10 subdomains."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag?domain=animation")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_docs"] == 180
        assert data["domain"] == "animation"
        assert len(data.get("by_subdomain", {})) >= 10


@pytest.mark.asyncio
async def test_rag_animation_concept():
    """Should return RAG content for an animation concept."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag/anim-squash-stretch?domain=animation")
        assert resp.status_code == 200
        data = resp.json()
        assert data["concept_id"] == "anim-squash-stretch"
        assert data["domain"] == "animation"
        assert "挤压" in data["content"] or "拉伸" in data["content"]


@pytest.mark.asyncio
async def test_animation_cross_sphere_links():
    """Cross-sphere links for animation should exist (animation ↔ game-engine/concept-design/3d-art/game-design)."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/cross-links?domain=animation")
        assert resp.status_code == 200
        data = resp.json()
        links = data["links"]
        assert len(links) >= 15, f"Expected >= 15 cross-links, got {len(links)}"
        partner_domains = set()
        for lk in links:
            partner_domains.add(lk.get("source_domain", ""))
            partner_domains.add(lk.get("target_domain", ""))
        assert "game-engine" in partner_domains, "Expected cross-links with game-engine"
        assert "concept-design" in partner_domains, "Expected cross-links with concept-design"


@pytest.mark.asyncio
async def test_animation_domain_supplements():
    """Animation should have domain supplements in BE evaluation system."""
    from engines.dialogue.prompts.feynman_system import DOMAIN_SUPPLEMENTS, ASSESSMENT_SUPPLEMENTS
    assert "animation" in DOMAIN_SUPPLEMENTS, "animation missing from DOMAIN_SUPPLEMENTS"
    assert "animation" in ASSESSMENT_SUPPLEMENTS, "animation missing from ASSESSMENT_SUPPLEMENTS"
    assert "12原则" in DOMAIN_SUPPLEMENTS["animation"] or "12条" in DOMAIN_SUPPLEMENTS["animation"], "Animation supplement should mention 12 principles"


# ─── Phase 26: Technical Art (技术美术) ───

@pytest.mark.asyncio
async def test_technical_art_seed_graph_integrity():
    """Technical Art seed graph: 180 concepts, 181 edges, 10 subdomains, 36 milestones."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=technical-art")
        assert resp.status_code == 200
        data = resp.json()
        nodes = data["nodes"]
        edges = data["edges"]
        assert len(nodes) == 180, f"Expected 180 concepts, got {len(nodes)}"
        assert len(edges) == 181, f"Expected 181 edges, got {len(edges)}"
        subdomain_ids = set(n["subdomain_id"] for n in nodes)
        assert len(subdomain_ids) == 10, f"Expected 10 subdomains, got {len(subdomain_ids)}"
        milestones = [n for n in nodes if n.get("is_milestone")]
        assert len(milestones) == 36, f"Expected 36 milestones, got {len(milestones)}"


@pytest.mark.asyncio
async def test_technical_art_subdomains():
    """Technical Art should have 10 subdomains with correct IDs."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/subdomains?domain=technical-art")
        assert resp.status_code == 200
        subs = resp.json()
        sub_ids = {s["id"] for s in subs}
        expected = {
            "shader-dev", "material-system", "pcg",
            "perf-optimization", "tool-dev", "pipeline-build",
            "lod-strategy", "memory-budget", "art-standards",
            "automation",
        }
        assert sub_ids == expected, f"Subdomain mismatch: {sub_ids ^ expected}"


@pytest.mark.asyncio
async def test_rag_technical_art_stats():
    """Technical Art RAG stats should reflect 180 documents across 10 subdomains."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag?domain=technical-art")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_docs"] == 180
        assert data["domain"] == "technical-art"
        assert len(data.get("by_subdomain", {})) >= 10


@pytest.mark.asyncio
async def test_rag_technical_art_concept():
    """Should return RAG content for a technical art concept."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag/ta-gpu-pipeline?domain=technical-art")
        assert resp.status_code == 200
        data = resp.json()
        assert data["concept_id"] == "ta-gpu-pipeline"
        assert data["domain"] == "technical-art"
        assert "渲染管线" in data["content"] or "GPU" in data["content"]


@pytest.mark.asyncio
async def test_technical_art_cross_sphere_links():
    """Cross-sphere links for technical-art should exist (↔ computer-graphics/3d-art/game-engine/software-engineering/animation)."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/cross-links?domain=technical-art")
        assert resp.status_code == 200
        data = resp.json()
        links = data["links"]
        assert len(links) >= 15, f"Expected >= 15 cross-links, got {len(links)}"
        partner_domains = set()
        for lk in links:
            partner_domains.add(lk.get("source_domain", ""))
            partner_domains.add(lk.get("target_domain", ""))
        assert "computer-graphics" in partner_domains, "Expected cross-links with computer-graphics"
        assert "3d-art" in partner_domains, "Expected cross-links with 3d-art"


@pytest.mark.asyncio
async def test_technical_art_domain_supplements():
    """Technical Art should have domain supplements in BE evaluation system."""
    from engines.dialogue.prompts.feynman_system import DOMAIN_SUPPLEMENTS, ASSESSMENT_SUPPLEMENTS
    assert "technical-art" in DOMAIN_SUPPLEMENTS, "technical-art missing from DOMAIN_SUPPLEMENTS"
    assert "technical-art" in ASSESSMENT_SUPPLEMENTS, "technical-art missing from ASSESSMENT_SUPPLEMENTS"
    assert "Shader" in DOMAIN_SUPPLEMENTS["technical-art"], "Technical Art supplement should mention Shader"


# ── Phase 27: VFX (特效) Integration Tests ───────────────────────────

@pytest.mark.asyncio
async def test_vfx_seed_graph():
    """VFX seed graph: 180 concepts, 189 edges, 9 subdomains, 44 milestones."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=vfx")
        assert resp.status_code == 200
        data = resp.json()
        nodes = data["nodes"]
        edges = data["edges"]
        assert len(nodes) == 180, f"Expected 180 concepts, got {len(nodes)}"
        assert len(edges) == 189, f"Expected 189 edges, got {len(edges)}"
        subdomain_ids = set(n["subdomain_id"] for n in nodes)
        assert len(subdomain_ids) == 9, f"Expected 9 subdomains, got {len(subdomain_ids)}"
        milestones = [n for n in nodes if n.get("is_milestone")]
        assert len(milestones) == 44, f"Expected 44 milestones, got {len(milestones)}"


@pytest.mark.asyncio
async def test_vfx_rag_stats():
    """VFX RAG stats should reflect 180 documents across 9 subdomains."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag?domain=vfx")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_docs"] == 180


@pytest.mark.asyncio
async def test_vfx_concept_detail():
    """GET /api/graph/concepts/{id} for a VFX concept."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/concepts/vfx-niagara-overview?domain=vfx")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "vfx-niagara-overview"
        assert data["domain_id"] == "vfx"
        assert data["is_milestone"] is True


@pytest.mark.asyncio
async def test_vfx_subdomains():
    """VFX should have exactly 9 subdomains."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/subdomains?domain=vfx")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 9
        names = {s["name"] for s in data}
        assert "Niagara系统" in names
        assert "特效优化" in names


@pytest.mark.asyncio
async def test_vfx_cross_sphere_links():
    """Cross-sphere links for vfx should exist (↔ computer-graphics/game-engine/technical-art/3d-art)."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/cross-links?domain=vfx")
        assert resp.status_code == 200
        data = resp.json()
        links = data["links"]
        assert len(links) >= 20, f"Expected >= 20 cross-links, got {len(links)}"
        partner_domains = set()
        for lk in links:
            partner_domains.add(lk.get("source_domain", ""))
            partner_domains.add(lk.get("target_domain", ""))
        assert "computer-graphics" in partner_domains, "Expected cross-links with computer-graphics"
        assert "technical-art" in partner_domains, "Expected cross-links with technical-art"


@pytest.mark.asyncio
async def test_vfx_domain_supplements():
    """VFX should have domain supplements in BE evaluation system."""
    from engines.dialogue.prompts.feynman_system import DOMAIN_SUPPLEMENTS, ASSESSMENT_SUPPLEMENTS
    assert "vfx" in DOMAIN_SUPPLEMENTS, "vfx missing from DOMAIN_SUPPLEMENTS"
    assert "vfx" in ASSESSMENT_SUPPLEMENTS, "vfx missing from ASSESSMENT_SUPPLEMENTS"
    assert "粒子" in DOMAIN_SUPPLEMENTS["vfx"] or "特效" in DOMAIN_SUPPLEMENTS["vfx"], "VFX supplement should mention particles/effects"


@pytest.mark.asyncio
async def test_vfx_neighbors():
    """VFX concept should have neighbors."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/concepts/vfx-niagara-overview/neighbors?domain=vfx&depth=1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["center"] == "vfx-niagara-overview"
        assert len(data["nodes"]) >= 2


# ── Game Audio Music (游戏音乐) Knowledge Sphere Tests ─────────────

@pytest.mark.asyncio
async def test_game_audio_music_seed_graph():
    """Game Audio Music seed graph: 180 concepts, 197 edges, 9 subdomains, 43 milestones."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=game-audio-music")
        assert resp.status_code == 200
        data = resp.json()
        nodes = data["nodes"]
        edges = data["edges"]
        assert len(nodes) == 180, f"Expected 180 concepts, got {len(nodes)}"
        assert len(edges) == 197, f"Expected 197 edges, got {len(edges)}"
        subdomain_ids = set(n["subdomain_id"] for n in nodes)
        assert len(subdomain_ids) == 9, f"Expected 9 subdomains, got {len(subdomain_ids)}"
        milestones = [n for n in nodes if n.get("is_milestone")]
        assert len(milestones) == 43, f"Expected 43 milestones, got {len(milestones)}"


@pytest.mark.asyncio
async def test_game_audio_music_rag_stats():
    """Game Audio Music RAG stats should reflect 180 documents across 9 subdomains."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag?domain=game-audio-music")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_docs"] == 180


@pytest.mark.asyncio
async def test_game_audio_music_concept_detail():
    """GET /api/graph/concepts/{id} for a Game Audio Music concept."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/concepts/game-audio-music-composition-overview?domain=game-audio-music")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "game-audio-music-composition-overview"
        assert data["domain_id"] == "game-audio-music"
        assert data["is_milestone"] is True


@pytest.mark.asyncio
async def test_game_audio_music_subdomains():
    """Game Audio Music should have exactly 9 subdomains."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/subdomains?domain=game-audio-music")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 9
        names = {s["name"] for s in data}
        assert "作曲编曲" in names
        assert "自适应音乐" in names
        assert "Wwise音乐系统" in names


@pytest.mark.asyncio
async def test_game_audio_music_cross_sphere_links():
    """Cross-sphere links for game-audio-music should exist (↔ game-design/game-engine/vfx/etc)."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/cross-links?domain=game-audio-music")
        assert resp.status_code == 200
        data = resp.json()
        links = data["links"]
        assert len(links) >= 20, f"Expected >= 20 cross-links, got {len(links)}"
        partner_domains = set()
        for lk in links:
            partner_domains.add(lk.get("source_domain", ""))
            partner_domains.add(lk.get("target_domain", ""))
        assert "game-design" in partner_domains, "Expected cross-links with game-design"
        assert "game-engine" in partner_domains, "Expected cross-links with game-engine"


@pytest.mark.asyncio
async def test_game_audio_music_domain_supplements():
    """Game Audio Music should have domain supplements in BE evaluation system."""
    from engines.dialogue.prompts.feynman_system import DOMAIN_SUPPLEMENTS, ASSESSMENT_SUPPLEMENTS
    assert "game-audio-music" in DOMAIN_SUPPLEMENTS, "game-audio-music missing from DOMAIN_SUPPLEMENTS"
    assert "game-audio-music" in ASSESSMENT_SUPPLEMENTS, "game-audio-music missing from ASSESSMENT_SUPPLEMENTS"
    assert "音乐" in DOMAIN_SUPPLEMENTS["game-audio-music"], "Game Audio Music supplement should mention music"


@pytest.mark.asyncio
async def test_game_audio_music_neighbors():
    """Game Audio Music concept should have neighbors."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/concepts/game-audio-music-composition-overview/neighbors?domain=game-audio-music&depth=1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["center"] == "game-audio-music-composition-overview"
        assert len(data["nodes"]) >= 2


# ── Game UI/UX Knowledge Sphere Tests (Phase 29) ──────────────

@pytest.mark.asyncio
async def test_game_ui_ux_data():
    """Game UI/UX seed graph: 200 concepts, 220 edges, 10 subdomains, 25 milestones."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=game-ui-ux")
        assert resp.status_code == 200
        data = resp.json()
        nodes = data["nodes"]
        edges = data["edges"]
        assert len(nodes) == 200, f"Expected 200 concepts, got {len(nodes)}"
        assert len(edges) == 220, f"Expected 220 edges, got {len(edges)}"
        subdomain_ids = set(n["subdomain_id"] for n in nodes)
        assert len(subdomain_ids) == 10, f"Expected 10 subdomains, got {len(subdomain_ids)}"
        milestones = [n for n in nodes if n.get("is_milestone")]
        assert len(milestones) == 25, f"Expected 25 milestones, got {len(milestones)}"

@pytest.mark.asyncio
async def test_game_ui_ux_rag():
    """Game UI/UX RAG stats should reflect 200 documents across 10 subdomains."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag?domain=game-ui-ux")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_docs"] == 200

@pytest.mark.asyncio
async def test_game_ui_ux_concept_detail():
    """Should retrieve a specific Game UI/UX concept."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/concepts/guiux-hud-design-overview?domain=game-ui-ux")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "guiux-hud-design-overview"
        assert data["domain_id"] == "game-ui-ux"

@pytest.mark.asyncio
async def test_game_ui_ux_subdomains():
    """Game UI/UX should have 10 subdomains."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/subdomains?domain=game-ui-ux")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 10
        names = [s["name"] for s in data]
        assert "HUD设计" in names
        assert "菜单系统" in names
        assert "UI技术实现" in names

@pytest.mark.asyncio
async def test_game_ui_ux_cross_links():
    """Cross-sphere links for game-ui-ux should exist (↔ game-design/game-engine/etc)."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/cross-links?domain=game-ui-ux")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 20

@pytest.mark.asyncio
async def test_game_ui_ux_supplements():
    """Game UI/UX should have domain & assessment supplements."""
    from engines.dialogue.prompts.feynman_system import DOMAIN_SUPPLEMENTS, ASSESSMENT_SUPPLEMENTS
    assert "game-ui-ux" in DOMAIN_SUPPLEMENTS, "game-ui-ux missing from DOMAIN_SUPPLEMENTS"
    assert "game-ui-ux" in ASSESSMENT_SUPPLEMENTS, "game-ui-ux missing from ASSESSMENT_SUPPLEMENTS"
    assert "UI" in DOMAIN_SUPPLEMENTS["game-ui-ux"], "Game UI/UX supplement should mention UI"

@pytest.mark.asyncio
async def test_game_ui_ux_neighbors():
    """Game UI/UX concept should have neighbors."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/concepts/guiux-hud-design-overview/neighbors?domain=game-ui-ux&depth=1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["center"] == "guiux-hud-design-overview"
        assert len(data["nodes"]) >= 2


# ── Narrative Design Knowledge Sphere Tests (Phase 30) ──────────────

@pytest.mark.asyncio
async def test_narrative_design_data():
    """Narrative Design seed graph: 180 concepts, 157 edges, 9 subdomains, 25 milestones."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=narrative-design")
        assert resp.status_code == 200
        data = resp.json()
        nodes = data["nodes"]
        edges = data["edges"]
        assert len(nodes) == 180, f"Expected 180 concepts, got {len(nodes)}"
        assert len(edges) == 157, f"Expected 157 edges, got {len(edges)}"
        subdomain_ids = set(n["subdomain_id"] for n in nodes)
        assert len(subdomain_ids) == 9, f"Expected 9 subdomains, got {len(subdomain_ids)}"
        milestones = [n for n in nodes if n.get("is_milestone")]
        assert len(milestones) == 25, f"Expected 25 milestones, got {len(milestones)}"

@pytest.mark.asyncio
async def test_narrative_design_rag():
    """Narrative Design RAG stats should reflect 180 documents across 9 subdomains."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag?domain=narrative-design")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_docs"] == 180

@pytest.mark.asyncio
async def test_narrative_design_concept_detail():
    """Should retrieve a specific Narrative Design concept."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/concepts/nd-wb-setting-bible?domain=narrative-design")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "nd-wb-setting-bible"
        assert data["domain_id"] == "narrative-design"

@pytest.mark.asyncio
async def test_narrative_design_subdomains():
    """Narrative Design should have 9 subdomains."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/subdomains?domain=narrative-design")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 9
        names = [s["name"] for s in data]
        assert "世界观构建" in names
        assert "角色塑造" in names
        assert "叙事工具" in names

@pytest.mark.asyncio
async def test_narrative_design_cross_links():
    """Cross-sphere links for narrative-design should exist (↔ game-design/level-design/etc)."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/cross-links?domain=narrative-design")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 20

@pytest.mark.asyncio
async def test_narrative_design_supplements():
    """Narrative Design should have domain & assessment supplements."""
    from engines.dialogue.prompts.feynman_system import DOMAIN_SUPPLEMENTS, ASSESSMENT_SUPPLEMENTS
    assert "narrative-design" in DOMAIN_SUPPLEMENTS, "narrative-design missing from DOMAIN_SUPPLEMENTS"
    assert "narrative-design" in ASSESSMENT_SUPPLEMENTS, "narrative-design missing from ASSESSMENT_SUPPLEMENTS"
    assert "叙事" in DOMAIN_SUPPLEMENTS["narrative-design"], "Narrative Design supplement should mention 叙事"

@pytest.mark.asyncio
async def test_narrative_design_neighbors():
    """Narrative Design concept should have neighbors."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/concepts/nd-wb-setting-bible/neighbors?domain=narrative-design&depth=1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["center"] == "nd-wb-setting-bible"
        assert len(data["nodes"]) >= 2


# ── Multiplayer Network Knowledge Sphere Tests (Phase 31) ──────────────

@pytest.mark.asyncio
async def test_multiplayer_network_data():
    """Multiplayer Network seed graph: 200 concepts, 189 edges, 10 subdomains, 37 milestones."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=multiplayer-network")
        assert resp.status_code == 200
        data = resp.json()
        nodes = data["nodes"]
        edges = data["edges"]
        assert len(nodes) == 200, f"Expected 200 concepts, got {len(nodes)}"
        assert len(edges) == 189, f"Expected 189 edges, got {len(edges)}"
        subdomain_ids = set(n["subdomain_id"] for n in nodes)
        assert len(subdomain_ids) == 10, f"Expected 10 subdomains, got {len(subdomain_ids)}"
        milestones = [n for n in nodes if n.get("is_milestone")]
        assert len(milestones) == 37, f"Expected 37 milestones, got {len(milestones)}"

@pytest.mark.asyncio
async def test_multiplayer_network_rag():
    """Multiplayer Network RAG stats should reflect 200 documents."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag?domain=multiplayer-network")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_docs"] == 200

@pytest.mark.asyncio
async def test_multiplayer_network_concept_detail():
    """Should retrieve a specific Multiplayer Network concept."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/concepts/mn-na-client-server?domain=multiplayer-network")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "mn-na-client-server"
        assert data["domain_id"] == "multiplayer-network"

@pytest.mark.asyncio
async def test_multiplayer_network_subdomains():
    """Multiplayer Network should have 10 subdomains."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/subdomains?domain=multiplayer-network")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 10
        names = [s["name"] for s in data]
        assert "网络架构" in names
        assert "状态同步" in names
        assert "排行榜与统计" in names

@pytest.mark.asyncio
async def test_multiplayer_network_cross_links():
    """Cross-sphere links for multiplayer-network should exist (↔ game-engine/software-engineering/etc)."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/cross-links?domain=multiplayer-network")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 20

@pytest.mark.asyncio
async def test_multiplayer_network_supplements():
    """Multiplayer Network should have domain & assessment supplements."""
    from engines.dialogue.prompts.feynman_system import DOMAIN_SUPPLEMENTS, ASSESSMENT_SUPPLEMENTS
    assert "multiplayer-network" in DOMAIN_SUPPLEMENTS, "multiplayer-network missing from DOMAIN_SUPPLEMENTS"
    assert "multiplayer-network" in ASSESSMENT_SUPPLEMENTS, "multiplayer-network missing from ASSESSMENT_SUPPLEMENTS"
    assert "延迟" in DOMAIN_SUPPLEMENTS["multiplayer-network"], "Multiplayer Network supplement should mention 延迟"

@pytest.mark.asyncio
async def test_multiplayer_network_neighbors():
    """Multiplayer Network concept should have neighbors."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/concepts/mn-na-client-server/neighbors?domain=multiplayer-network&depth=1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["center"] == "mn-na-client-server"
        assert len(data["nodes"]) >= 2


# ── Phase 32: Game Audio SFX (game-audio-sfx) Tests ──────────────────

@pytest.mark.asyncio
async def test_game_audio_sfx_seed():
    """Game Audio SFX seed graph: 180 concepts, 190 edges, 9 subdomains, 27 milestones."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=game-audio-sfx")
        assert resp.status_code == 200
        data = resp.json()
        nodes = data["nodes"]
        edges = data["edges"]
        assert len(nodes) == 180, f"Expected 180 concepts, got {len(nodes)}"
        assert len(edges) >= 180, f"Expected >= 180 edges, got {len(edges)}"
        subdomain_ids = {n["subdomain_id"] for n in nodes}
        assert len(subdomain_ids) == 9, f"Expected 9 subdomains, got {len(subdomain_ids)}"
        milestones = [n for n in nodes if n.get("is_milestone")]
        assert len(milestones) == 27, f"Expected 27 milestones, got {len(milestones)}"
        assert all(n["domain_id"] == "game-audio-sfx" for n in nodes)


@pytest.mark.asyncio
async def test_game_audio_sfx_rag():
    """Game Audio SFX RAG stats should reflect 180 documents across 9 subdomains."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag?domain=game-audio-sfx")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_docs"] == 180
        assert len(data.get("by_subdomain", {})) >= 9


@pytest.mark.asyncio
async def test_game_audio_sfx_cross_links():
    """Game Audio SFX should have cross-sphere links."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/cross-links?domain=game-audio-sfx")
        assert resp.status_code == 200
        data = resp.json()
        links = data["links"]
        assert len(links) >= 20, f"Expected >= 20 cross-links, got {len(links)}"


def test_game_audio_sfx_supplements():
    """Game Audio SFX domain/assessment supplements should be registered."""
    from engines.dialogue.prompts.feynman_system import DOMAIN_SUPPLEMENTS, ASSESSMENT_SUPPLEMENTS
    assert "game-audio-sfx" in DOMAIN_SUPPLEMENTS, "game-audio-sfx missing from DOMAIN_SUPPLEMENTS"
    assert "game-audio-sfx" in ASSESSMENT_SUPPLEMENTS, "game-audio-sfx missing from ASSESSMENT_SUPPLEMENTS"
    assert "Wwise" in DOMAIN_SUPPLEMENTS["game-audio-sfx"], "SFX supplement should mention Wwise"
    assert "HRTF" in ASSESSMENT_SUPPLEMENTS["game-audio-sfx"], "SFX assessment should mention HRTF"


@pytest.mark.asyncio
async def test_game_audio_sfx_concept_detail():
    """Game Audio SFX concept detail should return valid data."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/concepts/sfx-sdt-psychoacoustics?domain=game-audio-sfx")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "sfx-sdt-psychoacoustics"
        assert data["name"] == "声音心理学"
        assert data["domain_id"] == "game-audio-sfx"


@pytest.mark.asyncio
async def test_game_audio_sfx_neighbors():
    """Game Audio SFX concept should have neighbors."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/concepts/sfx-am-wwise-overview/neighbors?domain=game-audio-sfx&depth=1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["center"] == "sfx-am-wwise-overview"
        assert len(data["nodes"]) >= 2


# ── Phase 33: Game Publishing (game-publishing) Tests ──────────────────


@pytest.mark.asyncio
async def test_game_publishing_seed():
    """Game Publishing seed graph: 180 concepts, 191 edges, 9 subdomains, 27 milestones."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=game-publishing")
        assert resp.status_code == 200
        data = resp.json()
        nodes = data["nodes"]
        edges = data["edges"]
        assert len(nodes) == 180, f"Expected 180 concepts, got {len(nodes)}"
        assert len(edges) >= 180, f"Expected >= 180 edges, got {len(edges)}"
        subdomain_ids = {n["subdomain_id"] for n in nodes}
        assert len(subdomain_ids) == 9, f"Expected 9 subdomains, got {len(subdomain_ids)}"
        milestones = [n for n in nodes if n.get("is_milestone")]
        assert len(milestones) == 27, f"Expected 27 milestones, got {len(milestones)}"
        assert all(n["domain_id"] == "game-publishing" for n in nodes)


@pytest.mark.asyncio
async def test_game_publishing_rag():
    """Game Publishing RAG stats should reflect 180 documents across 9 subdomains."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag?domain=game-publishing")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_docs"] == 180
        assert len(data.get("by_subdomain", {})) >= 9


@pytest.mark.asyncio
async def test_game_publishing_cross_links():
    """Game Publishing should have cross-sphere links."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/cross-links?domain=game-publishing")
        assert resp.status_code == 200
        data = resp.json()
        links = data["links"]
        assert len(links) >= 20, f"Expected >= 20 cross-links, got {len(links)}"


def test_game_publishing_supplements():
    """Game Publishing domain/assessment supplements should be registered."""
    from engines.dialogue.prompts.feynman_system import DOMAIN_SUPPLEMENTS, ASSESSMENT_SUPPLEMENTS
    assert "game-publishing" in DOMAIN_SUPPLEMENTS, "game-publishing missing from DOMAIN_SUPPLEMENTS"
    assert "game-publishing" in ASSESSMENT_SUPPLEMENTS, "game-publishing missing from ASSESSMENT_SUPPLEMENTS"
    assert "商业思维" in DOMAIN_SUPPLEMENTS["game-publishing"], "Publishing supplement should mention 商业思维"
    assert "ESRB" in ASSESSMENT_SUPPLEMENTS["game-publishing"], "Publishing assessment should mention ESRB"


@pytest.mark.asyncio
async def test_game_publishing_concept_detail():
    """Game Publishing concept detail should return valid data."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/concepts/pub-ms-market-research?domain=game-publishing")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "pub-ms-market-research"
        assert data["name"] == "市场调研"
        assert data["domain_id"] == "game-publishing"


@pytest.mark.asyncio
async def test_game_publishing_neighbors():
    """Game Publishing concept should have neighbors."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/concepts/pub-ms-market-research/neighbors?domain=game-publishing&depth=1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["center"] == "pub-ms-market-research"
        assert len(data["nodes"]) >= 2


# ── Phase 34: Game Live Ops (game-live-ops) Tests ──────────────────


@pytest.mark.asyncio
async def test_game_live_ops_seed():
    """Game Live Ops seed graph: 180 concepts, ~205 edges, 9 subdomains, 35 milestones."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=game-live-ops")
        assert resp.status_code == 200
        data = resp.json()
        nodes = data["nodes"]
        edges = data["edges"]
        assert len(nodes) == 180, f"Expected 180 concepts, got {len(nodes)}"
        assert len(edges) >= 180, f"Expected >= 180 edges, got {len(edges)}"
        subdomain_ids = {n["subdomain_id"] for n in nodes}
        assert len(subdomain_ids) == 9, f"Expected 9 subdomains, got {len(subdomain_ids)}"
        milestones = [n for n in nodes if n.get("is_milestone")]
        assert len(milestones) == 35, f"Expected 35 milestones, got {len(milestones)}"
        assert all(n["domain_id"] == "game-live-ops" for n in nodes)


@pytest.mark.asyncio
async def test_game_live_ops_rag():
    """Game Live Ops RAG stats should reflect 180 documents across 9 subdomains."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag?domain=game-live-ops")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_docs"] == 180
        assert len(data.get("by_subdomain", {})) >= 9


@pytest.mark.asyncio
async def test_game_live_ops_cross_links():
    """Game Live Ops should have cross-sphere links."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/cross-links?domain=game-live-ops")
        assert resp.status_code == 200
        data = resp.json()
        links = data["links"]
        assert len(links) >= 20, f"Expected >= 20 cross-links, got {len(links)}"


def test_game_live_ops_supplements():
    """Game Live Ops domain/assessment supplements should be registered."""
    from engines.dialogue.prompts.feynman_system import DOMAIN_SUPPLEMENTS, ASSESSMENT_SUPPLEMENTS
    assert "game-live-ops" in DOMAIN_SUPPLEMENTS, "game-live-ops missing from DOMAIN_SUPPLEMENTS"
    assert "game-live-ops" in ASSESSMENT_SUPPLEMENTS, "game-live-ops missing from ASSESSMENT_SUPPLEMENTS"
    assert "\u6570\u636e\u9a71\u52a8" in DOMAIN_SUPPLEMENTS["game-live-ops"], "Live Ops supplement should mention \u6570\u636e\u9a71\u52a8"
    assert "A/B\u6d4b\u8bd5" in ASSESSMENT_SUPPLEMENTS["game-live-ops"], "Live Ops assessment should mention A/B\u6d4b\u8bd5"


@pytest.mark.asyncio
async def test_game_live_ops_concept_detail():
    """Game Live Ops concept detail should return valid data."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/concepts/ops-da-data-collection?domain=game-live-ops")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "ops-da-data-collection"
        assert data["name"] == "\u6570\u636e\u91c7\u96c6\u57fa\u7840"
        assert data["domain_id"] == "game-live-ops"


@pytest.mark.asyncio
async def test_game_live_ops_neighbors():
    """Game Live Ops concept should have neighbors."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/concepts/ops-da-data-collection/neighbors?domain=game-live-ops&depth=1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["center"] == "ops-da-data-collection"
        assert len(data["nodes"]) >= 2


# ── Phase 35: Game QA Testing (game-qa) Tests ──────────────────

@pytest.mark.asyncio
async def test_game_qa_seed():
    """Game QA seed graph: 160 concepts, 177 edges, 8 subdomains, 32 milestones."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=game-qa")
        assert resp.status_code == 200
        data = resp.json()
        nodes = data["nodes"]
        edges = data["edges"]
        assert len(nodes) == 160, f"Expected 160 concepts, got {len(nodes)}"
        assert len(edges) == 177, f"Expected 177 edges, got {len(edges)}"
        subdomains = set(n["subdomain_id"] for n in nodes)
        assert len(subdomains) == 8, f"Expected 8 subdomains, got {len(subdomains)}"
        assert all(n["domain_id"] == "game-qa" for n in nodes)

@pytest.mark.asyncio
async def test_game_qa_rag():
    """Game QA RAG: 160 documents across 8 subdomains."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag?domain=game-qa")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_docs"] == 160
        assert len(data.get("by_subdomain", {})) >= 8

@pytest.mark.asyncio
async def test_game_qa_cross_links():
    """Game QA cross-sphere links: 24 links to multiple domains."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/cross-links?domain=game-qa")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["links"]) >= 20, f"Expected ≥20 cross links, got {len(data['links'])}"

def test_game_qa_supplements():
    """Game QA supplements registered in both registries."""
    from engines.dialogue.prompts.feynman_system import DOMAIN_SUPPLEMENTS, ASSESSMENT_SUPPLEMENTS
    assert "game-qa" in DOMAIN_SUPPLEMENTS, "game-qa missing from DOMAIN_SUPPLEMENTS"
    assert "game-qa" in ASSESSMENT_SUPPLEMENTS, "game-qa missing from ASSESSMENT_SUPPLEMENTS"
    assert "质量意识" in DOMAIN_SUPPLEMENTS["game-qa"], "QA supplement should mention 质量意识"
    assert "测试设计能力" in ASSESSMENT_SUPPLEMENTS["game-qa"], "QA assessment should mention 测试设计能力"

@pytest.mark.asyncio
async def test_game_qa_concept_detail():
    """Game QA concept detail: qa-ft-basics."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/concepts/qa-ft-basics?domain=game-qa")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "qa-ft-basics"
        assert data["domain_id"] == "game-qa"

@pytest.mark.asyncio
async def test_game_qa_neighbors():
    """Game QA neighbors: qa-ft-basics should have at least 1 neighbor."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/concepts/qa-ft-basics/neighbors?domain=game-qa&depth=1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["center"] == "qa-ft-basics"
        assert len(data["nodes"]) >= 2


# ── Phase 36: Game Production (game-production) Tests ──────────────────

@pytest.mark.asyncio
async def test_game_production_seed():
    """Game Production seed graph: 160 concepts, 172 edges, 8 subdomains, 32 milestones."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=game-production")
        assert resp.status_code == 200
        data = resp.json()
        nodes = data["nodes"]
        edges = data["edges"]
        assert len(nodes) == 160, f"Expected 160 concepts, got {len(nodes)}"
        assert len(edges) == 172, f"Expected 172 edges, got {len(edges)}"
        subdomains = set(n["subdomain_id"] for n in nodes)
        assert len(subdomains) == 8, f"Expected 8 subdomains, got {len(subdomains)}"
        assert all(n["domain_id"] == "game-production" for n in nodes)

@pytest.mark.asyncio
async def test_game_production_rag():
    """Game Production RAG: 160 documents across 8 subdomains."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag?domain=game-production")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_docs"] == 160
        assert len(data.get("by_subdomain", {})) >= 8

@pytest.mark.asyncio
async def test_game_production_cross_links():
    """Game Production cross-sphere links: 24 links to multiple domains."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/cross-links?domain=game-production")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["links"]) >= 20, f"Expected ≥20 cross links, got {len(data['links'])}"

def test_game_production_supplements():
    """Game Production supplements registered in both registries."""
    from engines.dialogue.prompts.feynman_system import DOMAIN_SUPPLEMENTS, ASSESSMENT_SUPPLEMENTS
    assert "game-production" in DOMAIN_SUPPLEMENTS, "game-production missing from DOMAIN_SUPPLEMENTS"
    assert "game-production" in ASSESSMENT_SUPPLEMENTS, "game-production missing from ASSESSMENT_SUPPLEMENTS"
    assert "管线思维" in DOMAIN_SUPPLEMENTS["game-production"], "Production supplement should mention 管线思维"
    assert "管线设计能力" in ASSESSMENT_SUPPLEMENTS["game-production"], "Production assessment should mention 管线设计能力"

@pytest.mark.asyncio
async def test_game_production_concept_detail():
    """Game Production concept detail: gp-pp-overview."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/concepts/gp-pp-overview?domain=game-production")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "gp-pp-overview"
        assert data["domain_id"] == "game-production"

@pytest.mark.asyncio
async def test_game_production_neighbors():
    """Game Production neighbors: gp-pp-overview should have at least 1 neighbor."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/concepts/gp-pp-overview/neighbors?domain=game-production&depth=1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["center"] == "gp-pp-overview"
        assert len(data["nodes"]) >= 2


# ── Phase 37: Cross-Sphere Link Audit + 30-Sphere Validation ──────────────────


@pytest.mark.asyncio
async def test_phase37_cross_links_total():
    """Phase 37: Total cross-sphere links should be >= 595 after audit."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/cross-links")
        data = resp.json()
        assert data["total"] >= 595, f"Expected >= 595 cross-sphere links, got {data['total']}"


@pytest.mark.asyncio
async def test_phase37_physics_computer_graphics_links():
    """Phase 37: physics <-> computer-graphics cross-sphere links should exist."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/cross-links?domain=physics")
        data = resp.json()
        cg_links = [l for l in data["links"]
                    if l["target_domain"] == "computer-graphics" or l["source_domain"] == "computer-graphics"]
        assert len(cg_links) >= 5, f"Expected >= 5 physics<->CG links, got {len(cg_links)}"


@pytest.mark.asyncio
async def test_phase37_ai_game_design_links():
    """Phase 37: ai-engineering <-> game-design cross-sphere links should exist."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/cross-links?domain=ai-engineering")
        data = resp.json()
        gd_links = [l for l in data["links"]
                    if l["target_domain"] == "game-design" or l["source_domain"] == "game-design"]
        assert len(gd_links) >= 4, f"Expected >= 4 ai-eng<->game-design links, got {len(gd_links)}"


@pytest.mark.asyncio
async def test_phase37_ai_technical_art_links():
    """Phase 37: ai-engineering <-> technical-art cross-sphere links should exist."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/cross-links?domain=ai-engineering")
        data = resp.json()
        ta_links = [l for l in data["links"]
                    if l["target_domain"] == "technical-art" or l["source_domain"] == "technical-art"]
        assert len(ta_links) >= 3, f"Expected >= 3 ai-eng<->TA links, got {len(ta_links)}"


@pytest.mark.asyncio
async def test_phase37_all_30_domains_have_graph_data():
    """Phase 37: All 30 domains should return valid graph data."""
    all_domains = [
        "ai-engineering", "mathematics", "english", "physics", "product-design",
        "finance", "psychology", "philosophy", "biology", "economics", "writing",
        "game-design", "level-design", "game-engine", "software-engineering",
        "computer-graphics", "3d-art", "concept-design", "animation",
        "technical-art", "vfx", "game-audio-music", "game-ui-ux",
        "narrative-design", "multiplayer-network", "game-audio-sfx",
        "game-publishing", "game-live-ops", "game-qa", "game-production"
    ]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for domain_id in all_domains:
            resp = await client.get(f"/api/graph/data?domain={domain_id}")
            assert resp.status_code == 200, f"Domain {domain_id} failed"
            data = resp.json()
            assert len(data["nodes"]) >= 100, f"Domain {domain_id} has too few nodes: {len(data['nodes'])}"
            assert len(data["edges"]) >= 50, f"Domain {domain_id} has too few edges: {len(data['edges'])}"


@pytest.mark.asyncio
async def test_phase37_30_domains_registered():
    """Phase 37: domains.json should have exactly 30 active domains."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/domains")
        data = resp.json()
        assert len(data) >= 30, f"Expected >= 30 domains, got {len(data)}"
