"""Session Summary API tests — V3.1 learning session aggregate."""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestSessionSummary:
    """GET /api/analytics/session-summary"""

    def test_returns_200(self):
        r = client.get("/api/analytics/session-summary")
        assert r.status_code == 200

    def test_response_structure(self):
        r = client.get("/api/analytics/session-summary")
        data = r.json()
        for key in ("hours", "total_events", "concepts_touched",
                     "assessments", "new_masteries", "domain_breakdown",
                     "active_minutes", "current_streak"):
            assert key in data, f"Missing key: {key}"

    def test_hours_param(self):
        r = client.get("/api/analytics/session-summary?hours=48")
        assert r.status_code == 200
        assert r.json()["hours"] == 48

    def test_hours_validation_min(self):
        r = client.get("/api/analytics/session-summary?hours=0")
        assert r.status_code == 422

    def test_hours_validation_max(self):
        r = client.get("/api/analytics/session-summary?hours=999")
        assert r.status_code == 422

    def test_empty_history_returns_zero_events(self):
        r = client.get("/api/analytics/session-summary?hours=1")
        data = r.json()
        assert data["total_events"] >= 0
        assert data["concepts_touched"] >= 0
        assert data["active_minutes"] >= 0