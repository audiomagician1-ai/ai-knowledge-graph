"""Review Priority API tests — V3.2 intelligent review queue."""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestReviewPriority:
    """GET /api/learning/review-priority"""

    def test_returns_200(self):
        r = client.get("/api/learning/review-priority")
        assert r.status_code == 200

    def test_response_structure(self):
        r = client.get("/api/learning/review-priority")
        data = r.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)

    def test_limit_param(self):
        r = client.get("/api/learning/review-priority?limit=5")
        assert r.status_code == 200
        assert len(r.json()["items"]) <= 5

    def test_limit_validation_min(self):
        r = client.get("/api/learning/review-priority?limit=0")
        assert r.status_code == 422

    def test_limit_validation_max(self):
        r = client.get("/api/learning/review-priority?limit=100")
        assert r.status_code == 422

    def test_item_fields_if_present(self):
        r = client.get("/api/learning/review-priority")
        items = r.json()["items"]
        if items:
            item = items[0]
            for key in ("concept_id", "name", "priority_score",
                        "reasons", "overdue_hours", "stability",
                        "lapses", "downstream_count"):
                assert key in item, f"Item missing key: {key}"

    def test_items_sorted_by_priority(self):
        r = client.get("/api/learning/review-priority")
        items = r.json()["items"]
        scores = [i["priority_score"] for i in items]
        assert scores == sorted(scores, reverse=True)