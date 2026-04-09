"""Next Milestones API tests — V3.3 upcoming achievement detection."""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestNextMilestones:
    """GET /api/analytics/next-milestones"""

    def test_returns_200(self):
        r = client.get("/api/analytics/next-milestones")
        assert r.status_code == 200

    def test_response_structure(self):
        r = client.get("/api/analytics/next-milestones")
        data = r.json()
        assert "milestones" in data
        assert "total" in data
        assert isinstance(data["milestones"], list)

    def test_limit_param(self):
        r = client.get("/api/analytics/next-milestones?limit=3")
        assert r.status_code == 200
        assert len(r.json()["milestones"]) <= 3

    def test_milestone_fields(self):
        r = client.get("/api/analytics/next-milestones")
        ms = r.json()["milestones"]
        if ms:
            m = ms[0]
            for key in ("type", "label", "current", "target",
                        "remaining", "progress_pct", "badge"):
                assert key in m, f"Milestone missing: {key}"

    def test_sorted_by_remaining(self):
        r = client.get("/api/analytics/next-milestones")
        ms = r.json()["milestones"]
        remainings = [m["remaining"] for m in ms]
        assert remainings == sorted(remainings)

    def test_has_streak_milestone(self):
        r = client.get("/api/analytics/next-milestones?limit=30")
        types = [m["type"] for m in r.json()["milestones"]]
        assert "streak" in types or "total_concepts" in types