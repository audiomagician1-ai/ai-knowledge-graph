"""Prerequisite Check API tests — V3.1 learning readiness analysis."""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestPrerequisiteCheck:
    """GET /api/learning/prerequisite-check/{concept_id}"""

    def test_returns_200_for_valid_concept(self):
        """Find a real concept in ai-engineering and check."""
        import json, os, sys
        data_root = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "data", "seed",
        )
        seed_path = os.path.join(data_root, "ai-engineering", "seed_graph.json")
        with open(seed_path, "r", encoding="utf-8") as f:
            seed = json.load(f)
        cid = seed["concepts"][0]["id"]
        r = client.get(f"/api/learning/prerequisite-check/{cid}")
        assert r.status_code == 200

    def test_404_for_nonexistent_concept(self):
        r = client.get("/api/learning/prerequisite-check/nonexistent-concept-xyz-999")
        assert r.status_code == 404

    def test_response_structure(self):
        import json, os
        data_root = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "data", "seed",
        )
        seed_path = os.path.join(data_root, "ai-engineering", "seed_graph.json")
        with open(seed_path, "r", encoding="utf-8") as f:
            seed = json.load(f)
        cid = seed["concepts"][0]["id"]
        r = client.get(f"/api/learning/prerequisite-check/{cid}")
        data = r.json()
        for key in ("concept_id", "concept_name", "domain_id",
                     "readiness_score", "recommendation",
                     "total_prerequisites", "mastered_prerequisites",
                     "prerequisites", "suggested_next"):
            assert key in data, f"Missing key: {key}"

    def test_readiness_score_range(self):
        import json, os
        data_root = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "data", "seed",
        )
        seed_path = os.path.join(data_root, "ai-engineering", "seed_graph.json")
        with open(seed_path, "r", encoding="utf-8") as f:
            seed = json.load(f)
        cid = seed["concepts"][0]["id"]
        r = client.get(f"/api/learning/prerequisite-check/{cid}")
        data = r.json()
        assert 0 <= data["readiness_score"] <= 100

    def test_recommendation_valid_values(self):
        import json, os
        data_root = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "data", "seed",
        )
        seed_path = os.path.join(data_root, "ai-engineering", "seed_graph.json")
        with open(seed_path, "r", encoding="utf-8") as f:
            seed = json.load(f)
        cid = seed["concepts"][0]["id"]
        r = client.get(f"/api/learning/prerequisite-check/{cid}")
        data = r.json()
        assert data["recommendation"] in ("ready", "partially_ready", "not_ready")

    def test_prerequisites_list_structure(self):
        import json, os
        data_root = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "data", "seed",
        )
        seed_path = os.path.join(data_root, "ai-engineering", "seed_graph.json")
        with open(seed_path, "r", encoding="utf-8") as f:
            seed = json.load(f)
        # Find a concept with prerequisites
        edges = seed.get("edges", [])
        targets = set(e.get("target_id") or e.get("target", "") for e in edges)
        cid = next(iter(targets), seed["concepts"][0]["id"])
        r = client.get(f"/api/learning/prerequisite-check/{cid}")
        data = r.json()
        assert isinstance(data["prerequisites"], list)
        if data["prerequisites"]:
            p = data["prerequisites"][0]
            for key in ("concept_id", "name", "difficulty", "status", "mastery"):
                assert key in p, f"Prereq missing key: {key}"

    def test_concept_without_prereqs_is_ready(self):
        """A root concept (no incoming edges) should be 'ready'."""
        import json, os
        data_root = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "data", "seed",
        )
        seed_path = os.path.join(data_root, "ai-engineering", "seed_graph.json")
        with open(seed_path, "r", encoding="utf-8") as f:
            seed = json.load(f)
        edges = seed.get("edges", [])
        targets = set(e.get("target_id") or e.get("target", "") for e in edges)
        all_ids = {c["id"] for c in seed["concepts"]}
        roots = all_ids - targets
        if roots:
            root_id = next(iter(roots))
            r = client.get(f"/api/learning/prerequisite-check/{root_id}")
            data = r.json()
            assert data["recommendation"] == "ready"
            assert data["readiness_score"] == 100
            assert data["total_prerequisites"] == 0

    def test_with_progress_query_param(self):
        import json, os
        data_root = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "data", "seed",
        )
        seed_path = os.path.join(data_root, "ai-engineering", "seed_graph.json")
        with open(seed_path, "r", encoding="utf-8") as f:
            seed = json.load(f)
        cid = seed["concepts"][0]["id"]
        fake_progress = json.dumps({cid: {"status": "mastered", "mastery": 90}})
        r = client.get(f"/api/learning/prerequisite-check/{cid}", params={"progress": fake_progress})
        assert r.status_code == 200