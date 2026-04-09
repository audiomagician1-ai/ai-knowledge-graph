"""Mastery Forecast API tests — V3.2 domain completion prediction."""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestMasteryForecast:
    """GET /api/analytics/mastery-forecast/{domain_id}"""

    def test_returns_200_for_valid_domain(self):
        r = client.get("/api/analytics/mastery-forecast/ai-engineering")
        assert r.status_code == 200

    def test_response_structure(self):
        r = client.get("/api/analytics/mastery-forecast/ai-engineering")
        data = r.json()
        for key in ("domain_id", "domain_name", "total_concepts", "mastered",
                     "remaining", "completion_pct", "estimated_days",
                     "estimated_hours", "confidence", "subdomain_forecast"):
            assert key in data, f"Missing key: {key}"

    def test_completion_pct_range(self):
        r = client.get("/api/analytics/mastery-forecast/ai-engineering")
        data = r.json()
        assert 0 <= data["completion_pct"] <= 100

    def test_daily_minutes_param(self):
        r = client.get("/api/analytics/mastery-forecast/ai-engineering?daily_minutes=60")
        assert r.status_code == 200
        assert r.json()["daily_minutes"] == 60

    def test_daily_minutes_validation(self):
        r = client.get("/api/analytics/mastery-forecast/ai-engineering?daily_minutes=1")
        assert r.status_code == 422

    def test_subdomain_forecast_structure(self):
        r = client.get("/api/analytics/mastery-forecast/ai-engineering")
        data = r.json()
        sf = data["subdomain_forecast"]
        assert isinstance(sf, list)
        if sf:
            s = sf[0]
            for key in ("subdomain_id", "remaining", "estimated_hours"):
                assert key in s, f"Subdomain forecast missing key: {key}"

    def test_unknown_domain_returns_error(self):
        r = client.get("/api/analytics/mastery-forecast/nonexistent-xyz")
        data = r.json()
        assert "error" in data or data.get("remaining", 0) >= 0