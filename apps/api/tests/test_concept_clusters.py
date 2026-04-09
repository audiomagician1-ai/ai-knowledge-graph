"""Concept Cluster Analysis API tests — V3.1 graph module detection."""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestConceptClusters:
    """GET /api/graph/concept-clusters/{domain_id}"""

    def test_returns_200_for_valid_domain(self):
        r = client.get("/api/graph/concept-clusters/ai-engineering")
        assert r.status_code == 200

    def test_404_for_invalid_domain(self):
        r = client.get("/api/graph/concept-clusters/nonexistent-xyz")
        assert r.status_code == 404

    def test_response_structure(self):
        r = client.get("/api/graph/concept-clusters/ai-engineering")
        data = r.json()
        for key in ("domain_id", "total_clusters",
                     "total_concepts_in_clusters", "clusters"):
            assert key in data, f"Missing key: {key}"

    def test_clusters_sorted_by_size(self):
        r = client.get("/api/graph/concept-clusters/ai-engineering")
        clusters = r.json()["clusters"]
        sizes = [c["size"] for c in clusters]
        assert sizes == sorted(sizes, reverse=True)

    def test_cluster_fields(self):
        r = client.get("/api/graph/concept-clusters/ai-engineering")
        clusters = r.json()["clusters"]
        if clusters:
            c = clusters[0]
            for key in ("cluster_id", "size", "internal_edges", "density",
                        "avg_difficulty", "difficulty_range",
                        "primary_subdomain", "subdomain_composition",
                        "gateways", "concepts"):
                assert key in c, f"Cluster missing key: {key}"

    def test_min_cluster_size_param(self):
        r = client.get("/api/graph/concept-clusters/ai-engineering?min_cluster_size=10")
        assert r.status_code == 200
        clusters = r.json()["clusters"]
        for c in clusters:
            assert c["size"] >= 10

    def test_density_in_range(self):
        r = client.get("/api/graph/concept-clusters/ai-engineering")
        for c in r.json()["clusters"]:
            assert 0 <= c["density"] <= 1

    def test_gateway_fields(self):
        r = client.get("/api/graph/concept-clusters/ai-engineering")
        clusters = r.json()["clusters"]
        for c in clusters:
            for g in c["gateways"]:
                assert "id" in g
                assert "name" in g
                assert "external_connections" in g
                assert g["external_connections"] > 0