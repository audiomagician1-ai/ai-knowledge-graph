"""V4.1 tests — latency report + widget error boundary + api health."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from main import app
    return TestClient(app)


class TestLatencyReport:
    """Verify /health/latency-report endpoint."""

    def test_latency_report_200(self, client):
        r = client.get("/api/health/latency-report")
        assert r.status_code == 200
        data = r.json()
        assert "uptime_seconds" in data
        assert "total_requests" in data
        assert "global_error_rate" in data
        assert "global_avg_ms" in data
        assert "slowest_endpoints" in data
        assert "high_error_endpoints" in data
        assert "total_tracked" in data

    def test_latency_report_types(self, client):
        r = client.get("/api/health/latency-report")
        data = r.json()
        assert isinstance(data["uptime_seconds"], int)
        assert isinstance(data["total_requests"], int)
        assert isinstance(data["slowest_endpoints"], list)
        assert isinstance(data["high_error_endpoints"], list)

    def test_latency_report_after_traffic(self, client):
        """Make a few requests then check they appear in latency data."""
        # Generate some traffic
        client.get("/api/health")
        client.get("/api/health/project")
        client.get("/api/health/api-catalog")
        # Now check latency report
        r = client.get("/api/health/latency-report")
        data = r.json()
        assert data["total_requests"] >= 4  # at least the 3 above + this one
        assert data["total_tracked"] >= 1

    def test_latency_slowest_shape(self, client):
        """Verify slowest endpoint entries have correct fields."""
        client.get("/api/health")
        r = client.get("/api/health/latency-report")
        data = r.json()
        if data["slowest_endpoints"]:
            ep = data["slowest_endpoints"][0]
            assert "path" in ep
            assert "avg_ms" in ep
            assert "requests" in ep

    def test_latency_report_sorted_desc(self, client):
        """Slowest endpoints should be sorted by avg_ms descending."""
        client.get("/api/health")
        client.get("/api/health/project")
        r = client.get("/api/health/latency-report")
        data = r.json()
        avgs = [e["avg_ms"] for e in data["slowest_endpoints"]]
        assert avgs == sorted(avgs, reverse=True), "Slowest endpoints not sorted desc"


class TestCodeHealthV41:
    """Verify file integrity after V4.1."""

    def test_health_router_under_limit(self):
        import os
        path = os.path.join(os.path.dirname(__file__), "..", "routers", "health.py")
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        assert len(lines) <= 800, f"health.py: {len(lines)} lines (limit: 800)"

    def test_total_router_count(self):
        import os
        router_dir = os.path.join(os.path.dirname(__file__), "..", "routers")
        count = sum(1 for f in os.listdir(router_dir) if f.endswith(".py") and not f.startswith("__"))
        assert count >= 25, f"Expected >=25 routers, got {count}"
