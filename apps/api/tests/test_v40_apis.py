"""V4.0 tests — analytics_planning split + api-catalog + dashboard customization."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from main import app
    return TestClient(app)


# ── Code Health: Split Verification ────────────────────────

class TestAnalyticsPlanningSlim:
    """Verify analytics_planning.py endpoints still work after V3.9 extraction."""

    def test_domain_recommendation(self, client):
        r = client.get("/api/analytics/domain-recommendation?limit=3")
        assert r.status_code == 200
        data = r.json()
        assert "recommendations" in data
        assert "active_domains" in data
        assert "total_undiscovered" in data

    def test_study_plan(self, client):
        r = client.get("/api/analytics/study-plan?daily_minutes=30&days=3")
        assert r.status_code == 200
        data = r.json()
        assert "plan" in data
        assert "summary" in data
        assert data["summary"]["days"] == 3

    def test_learning_journey(self, client):
        r = client.get("/api/analytics/learning-journey")
        assert r.status_code == 200
        data = r.json()
        assert "events" in data
        assert "domain_summary" in data
        assert "stats" in data

    def test_next_milestones(self, client):
        r = client.get("/api/analytics/next-milestones?limit=5")
        assert r.status_code == 200
        data = r.json()
        assert "milestones" in data
        assert "total" in data

    def test_comparative_progress(self, client):
        r = client.get("/api/analytics/comparative-progress")
        assert r.status_code == 200
        data = r.json()
        assert "domains" in data
        assert "summary" in data


class TestAnalyticsAdvancedNew:
    """Verify extracted V3.9 endpoints in analytics_advanced.py."""

    def test_cross_domain_insights(self, client):
        r = client.get("/api/analytics/cross-domain-insights")
        assert r.status_code == 200
        data = r.json()
        assert "domain_pairs" in data
        assert "total_cross_links" in data
        assert isinstance(data["total_cross_links"], int)

    def test_learning_style(self, client):
        r = client.get("/api/analytics/learning-style")
        assert r.status_code == 200
        data = r.json()
        assert "style" in data
        assert "traits" in data
        assert isinstance(data["traits"], list)

    def test_learning_style_has_metrics(self, client):
        r = client.get("/api/analytics/learning-style")
        data = r.json()
        # Even with no history, should return basic structure
        assert "style" in data


class TestApiCatalog:
    """Verify the new /health/api-catalog endpoint."""

    def test_api_catalog_returns_200(self, client):
        r = client.get("/api/health/api-catalog")
        assert r.status_code == 200
        data = r.json()
        assert "total_endpoints" in data
        assert "total_tags" in data
        assert "tags" in data

    def test_api_catalog_count(self, client):
        r = client.get("/api/health/api-catalog")
        data = r.json()
        # We have 132+ endpoints
        assert data["total_endpoints"] >= 100, f"Expected >=100, got {data['total_endpoints']}"

    def test_api_catalog_has_known_tags(self, client):
        r = client.get("/api/health/api-catalog")
        data = r.json()
        tags = set(data["tags"].keys())
        # Should have core tags
        assert "health" in tags
        assert "learning" in tags

    def test_api_catalog_endpoint_shape(self, client):
        r = client.get("/api/health/api-catalog")
        data = r.json()
        # Check first endpoint shape
        for tag, info in data["tags"].items():
            if info["endpoints"]:
                ep = info["endpoints"][0]
                assert "method" in ep
                assert "path" in ep
                assert "name" in ep
                break

    def test_api_catalog_no_internal_routes(self, client):
        r = client.get("/api/health/api-catalog")
        data = r.json()
        all_paths = []
        for tag_info in data["tags"].values():
            for ep in tag_info["endpoints"]:
                all_paths.append(ep["path"])
        # Should not include /openapi.json or /docs
        assert "/openapi.json" not in all_paths
        assert "/docs" not in all_paths


class TestCodeHealthV40:
    """Verify file size limits are maintained."""

    def test_analytics_planning_under_limit(self):
        import os
        path = os.path.join(os.path.dirname(__file__), "..", "routers", "analytics_planning.py")
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        assert len(lines) <= 800, f"analytics_planning.py: {len(lines)} lines (limit: 800)"

    def test_analytics_advanced_exists(self):
        import os
        path = os.path.join(os.path.dirname(__file__), "..", "routers", "analytics_advanced.py")
        assert os.path.isfile(path), "analytics_advanced.py should exist"

    def test_all_routers_under_limit(self):
        import os
        router_dir = os.path.join(os.path.dirname(__file__), "..", "routers")
        violations = []
        for f in os.listdir(router_dir):
            if f.endswith(".py") and not f.startswith("__"):
                path = os.path.join(router_dir, f)
                with open(path, "r", encoding="utf-8") as fh:
                    count = len(fh.readlines())
                if count > 800:
                    violations.append(f"{f}: {count} lines")
        assert not violations, f"Routers over 800L: {violations}"
