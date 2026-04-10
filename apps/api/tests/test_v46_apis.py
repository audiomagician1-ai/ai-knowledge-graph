"""
V4.6 Tests — API Explorer backend + code health verification.
Tests the /health/api-catalog response schema used by ApiExplorerPage.
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestApiCatalogForExplorer:
    """Verify the api-catalog endpoint provides data needed by ApiExplorerPage."""

    def test_catalog_has_tags_and_total(self):
        r = client.get("/api/health/api-catalog")
        assert r.status_code == 200
        d = r.json()
        assert "total_endpoints" in d
        assert "tags" in d
        assert isinstance(d["tags"], dict)
        assert d["total_endpoints"] >= 100  # We have 134+ endpoints

    def test_catalog_endpoints_have_method_path_name(self):
        r = client.get("/api/health/api-catalog")
        d = r.json()
        for tag, group in d["tags"].items():
            assert isinstance(group, dict)
            assert "endpoints" in group
            for ep in group["endpoints"][:3]:  # Sample first 3
                assert "method" in ep
                assert "path" in ep
                assert ep["method"] in ("GET", "POST", "PUT", "DELETE", "PATCH")
                assert ep["path"].startswith("/")

    def test_catalog_has_health_tag(self):
        r = client.get("/api/health/api-catalog")
        d = r.json()
        tags = d["tags"]
        all_paths = [ep["path"] for g in tags.values() for ep in g["endpoints"]]
        assert any("/health" in p for p in all_paths)

    def test_catalog_has_analytics_endpoints(self):
        r = client.get("/api/health/api-catalog")
        d = r.json()
        all_paths = [ep["path"] for g in d["tags"].values() for ep in g["endpoints"]]
        analytics = [p for p in all_paths if "/analytics/" in p]
        assert len(analytics) >= 10

    def test_catalog_has_learning_endpoints(self):
        r = client.get("/api/health/api-catalog")
        d = r.json()
        all_paths = [ep["path"] for g in d["tags"].values() for ep in g["endpoints"]]
        learning = [p for p in all_paths if "/learning/" in p]
        assert len(learning) >= 5

    def test_catalog_has_graph_endpoints(self):
        r = client.get("/api/health/api-catalog")
        d = r.json()
        all_paths = [ep["path"] for g in d["tags"].values() for ep in g["endpoints"]]
        graph = [p for p in all_paths if "/graph/" in p]
        assert len(graph) >= 5


class TestLatencyReportForExplorer:
    """Verify the latency-report endpoint used by ApiHealthWidget."""

    def test_latency_report_schema(self):
        r = client.get("/api/health/latency-report")
        assert r.status_code == 200
        d = r.json()
        assert "uptime_seconds" in d
        assert "total_requests" in d
        assert "global_error_rate" in d
        assert "global_avg_ms" in d
        assert "slowest_endpoints" in d
        assert isinstance(d["slowest_endpoints"], list)

    def test_latency_report_has_tracked_count(self):
        r = client.get("/api/health/latency-report")
        d = r.json()
        assert "total_tracked" in d
        assert isinstance(d["total_tracked"], int)


class TestCodeHealthV46:
    """Verify code health metrics after V4.6 refactoring."""

    def test_all_be_routers_under_800_lines(self):
        import os
        routers_dir = os.path.join(os.path.dirname(__file__), "..", "routers")
        violations = []
        for f in os.listdir(routers_dir):
            if f.endswith(".py") and f != "__init__.py":
                path = os.path.join(routers_dir, f)
                lines = len(open(path, encoding="utf-8").readlines())
                if lines > 800:
                    violations.append(f"{f}: {lines}L")
        assert violations == [], f"Router files exceeding 800L: {violations}"
