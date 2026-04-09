"""Relationship Strength API tests — V3.0 graph topology analysis."""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestRelationshipStrength:
    """GET /api/graph/relationship-strength/{domain_id}"""

    def test_returns_200_for_valid_domain(self):
        r = client.get("/api/graph/relationship-strength/ai-engineering")
        assert r.status_code == 200

    def test_404_for_invalid_domain(self):
        r = client.get("/api/graph/relationship-strength/nonexistent-xyz")
        assert r.status_code == 404

    def test_response_structure(self):
        r = client.get("/api/graph/relationship-strength/ai-engineering")
        data = r.json()
        for key in ("domain_id", "total_concepts", "total_edges",
                     "hubs", "bridges", "isolated", "subdomain_density",
                     "avg_degree"):
            assert key in data, f"Missing key: {key}"

    def test_hubs_max_10(self):
        r = client.get("/api/graph/relationship-strength/ai-engineering")
        assert len(r.json()["hubs"]) <= 10

    def test_hub_fields(self):
        r = client.get("/api/graph/relationship-strength/ai-engineering")
        hubs = r.json()["hubs"]
        if hubs:
            h = hubs[0]
            for key in ("id", "name", "in_degree", "out_degree", "total_degree"):
                assert key in h, f"Hub missing key: {key}"

    def test_hubs_sorted_descending(self):
        r = client.get("/api/graph/relationship-strength/ai-engineering")
        hubs = r.json()["hubs"]
        degrees = [h["total_degree"] for h in hubs]
        assert degrees == sorted(degrees, reverse=True)

    def test_bridges_have_cross_subdomains(self):
        r = client.get("/api/graph/relationship-strength/ai-engineering")
        bridges = r.json()["bridges"]
        for b in bridges:
            assert "cross_subdomains" in b
            assert len(b["cross_subdomains"]) > 0
            assert "bridge_score" in b

    def test_subdomain_density_non_empty(self):
        r = client.get("/api/graph/relationship-strength/ai-engineering")
        sd = r.json()["subdomain_density"]
        assert len(sd) > 0
        first = sd[0]
        assert "subdomain_id" in first
        assert "concepts" in first
        assert "density" in first
        assert 0 <= first["density"] <= 1

    def test_avg_degree_positive(self):
        r = client.get("/api/graph/relationship-strength/ai-engineering")
        assert r.json()["avg_degree"] > 0

    def test_works_for_software_engineering_domain(self):
        """Edge format differs (source/target vs source_id/target_id)."""
        r = client.get("/api/graph/relationship-strength/software-engineering")
        assert r.status_code == 200
        data = r.json()
        assert data["total_concepts"] > 0