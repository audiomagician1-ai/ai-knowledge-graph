"""V3.9 tests — analytics_experience split + cross-domain-insights + learning-style APIs."""
import importlib
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from main import app
    return TestClient(app)


# ── Code Health: Split verification ──


class TestCodeHealthV39:
    """Verify V3.9 router splits maintain all endpoints."""

    def test_analytics_profile_module_exists(self):
        mod = importlib.import_module("routers.analytics_profile")
        assert hasattr(mod, "router")

    def test_analytics_profile_has_learning_profile(self):
        mod = importlib.import_module("routers.analytics_profile")
        assert hasattr(mod, "learning_profile")

    def test_analytics_profile_has_concept_journey(self):
        mod = importlib.import_module("routers.analytics_profile")
        assert hasattr(mod, "concept_journey")

    def test_analytics_profile_has_learning_heatmap(self):
        mod = importlib.import_module("routers.analytics_profile")
        assert hasattr(mod, "learning_heatmap")

    def test_analytics_experience_size_reduced(self):
        """analytics_experience.py should be under 800 lines (universal limit)."""
        import os
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "routers", "analytics_experience.py")
        with open(path) as f:
            lines = len(f.readlines())
        assert lines < 800, f"analytics_experience.py has {lines} lines"

    def test_analytics_planning_under_800(self):
        """analytics_planning.py must stay under 800 lines with new V3.9 endpoints."""
        import os
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "routers", "analytics_planning.py")
        with open(path) as f:
            lines = len(f.readlines())
        assert lines < 800, f"analytics_planning.py has {lines} lines"


# ── Split regression: V3.7+V3.8 endpoints via new router ──


class TestProfileRegressions:
    """Verify V3.7+V3.8 endpoints still work through analytics_profile.py."""

    def test_learning_profile_endpoint(self, client):
        resp = client.get("/api/analytics/learning-profile")
        assert resp.status_code == 200
        data = resp.json()
        assert "overview" in data
        assert "streak" in data
        assert "domains" in data

    def test_concept_journey_endpoint(self, client):
        resp = client.get("/api/analytics/concept-journey/test-concept")
        assert resp.status_code == 200
        assert "concept_id" in resp.json()

    def test_learning_heatmap_endpoint(self, client):
        resp = client.get("/api/analytics/learning-heatmap/ai-engineering")
        assert resp.status_code == 200
        data = resp.json()
        assert "subdomains" in data
        assert "summary" in data


# ── Cross-Domain Insights API ──


class TestCrossDomainInsights:
    """Test GET /api/analytics/cross-domain-insights."""

    def test_returns_200(self, client):
        resp = client.get("/api/analytics/cross-domain-insights")
        assert resp.status_code == 200

    def test_response_structure(self, client):
        data = client.get("/api/analytics/cross-domain-insights").json()
        assert "domain_pairs" in data
        assert "total_cross_links" in data
        assert "active_domains" in data
        assert "suggested_next" in data

    def test_cross_links_positive(self, client):
        data = client.get("/api/analytics/cross-domain-insights").json()
        assert data["total_cross_links"] > 0  # We have 633 cross-sphere links

    def test_domain_pairs_structure(self, client):
        data = client.get("/api/analytics/cross-domain-insights").json()
        if data["domain_pairs"]:
            pair = data["domain_pairs"][0]
            for field in ["domain_a", "domain_a_name", "domain_b", "domain_b_name", "shared_links", "transfer_score"]:
                assert field in pair
            assert pair["shared_links"] > 0


# ── Learning Style API ──


class TestLearningStyle:
    """Test GET /api/analytics/learning-style."""

    def test_returns_200(self, client):
        resp = client.get("/api/analytics/learning-style")
        assert resp.status_code == 200

    def test_response_structure(self, client):
        data = client.get("/api/analytics/learning-style").json()
        assert "style" in data
        assert "traits" in data
        assert "metrics" in data

    def test_metrics_fields(self, client):
        data = client.get("/api/analytics/learning-style").json()
        m = data["metrics"]
        if m:  # Only check fields when there's data
            for field in ["total_mastered", "total_sessions", "active_domains",
                           "consistency_pct", "peak_hour", "time_preference"]:
                assert field in m

    def test_time_distribution(self, client):
        data = client.get("/api/analytics/learning-style").json()
        if "time_distribution" in data:
            td = data["time_distribution"]
            for period in ["morning", "afternoon", "evening", "night"]:
                assert period in td
                assert isinstance(td[period], (int, float))

    def test_style_is_string(self, client):
        data = client.get("/api/analytics/learning-style").json()
        assert isinstance(data["style"], str)
        assert len(data["style"]) > 0
