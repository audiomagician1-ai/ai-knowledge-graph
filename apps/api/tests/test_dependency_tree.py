"""Dependency Tree API tests — V3.3 concept upstream/downstream tree."""

import json, os
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def _get_concept_id():
    data_root = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        "data", "seed",
    )
    with open(os.path.join(data_root, "ai-engineering", "seed_graph.json"), "r", encoding="utf-8") as f:
        seed = json.load(f)
    return seed["concepts"][0]["id"]


class TestDependencyTree:
    """GET /api/graph/dependency-tree/{concept_id}"""

    def test_returns_200(self):
        cid = _get_concept_id()
        r = client.get(f"/api/graph/dependency-tree/{cid}")
        assert r.status_code == 200

    def test_404_for_nonexistent(self):
        r = client.get("/api/graph/dependency-tree/nonexistent-xyz-999")
        assert r.status_code == 404

    def test_response_structure(self):
        cid = _get_concept_id()
        r = client.get(f"/api/graph/dependency-tree/{cid}")
        data = r.json()
        for key in ("concept_id", "concept_name", "upstream", "downstream",
                     "upstream_count", "downstream_count"):
            assert key in data, f"Missing key: {key}"

    def test_depth_param(self):
        cid = _get_concept_id()
        r = client.get(f"/api/graph/dependency-tree/{cid}?depth=1")
        assert r.status_code == 200
        data = r.json()
        for node in data["upstream"]:
            assert node["depth"] <= 1
        for node in data["downstream"]:
            assert node["depth"] <= 1

    def test_node_fields(self):
        cid = _get_concept_id()
        r = client.get(f"/api/graph/dependency-tree/{cid}")
        data = r.json()
        all_nodes = data["upstream"] + data["downstream"]
        if all_nodes:
            n = all_nodes[0]
            for key in ("id", "name", "depth", "difficulty"):
                assert key in n, f"Node missing: {key}"

    def test_depth_validation_max(self):
        cid = _get_concept_id()
        r = client.get(f"/api/graph/dependency-tree/{cid}?depth=10")
        assert r.status_code == 422

    def test_counts_match_lists(self):
        cid = _get_concept_id()
        r = client.get(f"/api/graph/dependency-tree/{cid}")
        data = r.json()
        assert data["upstream_count"] == len(data["upstream"])
        assert data["downstream_count"] == len(data["downstream"])