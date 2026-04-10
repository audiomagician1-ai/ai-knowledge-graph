"""V3.8 tests — code health splits + concept-journey + learning-heatmap APIs."""
import importlib
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from main import app
    return TestClient(app)


# ── Code Health: Split verification ──


class TestCodeHealthSplits:
    """Verify V3.8 router splits maintain all endpoints."""

    def test_learning_intelligence_module_exists(self):
        mod = importlib.import_module("routers.learning_intelligence")
        assert hasattr(mod, "router")

    def test_analytics_forecast_module_exists(self):
        mod = importlib.import_module("routers.analytics_forecast")
        assert hasattr(mod, "router")

    def test_learning_extended_size_reduced(self):
        """learning_extended.py should be under 800 lines."""
        import os
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "routers", "learning_extended.py")
        with open(path) as f:
            lines = len(f.readlines())
        assert lines < 800, f"learning_extended.py has {lines} lines, expected < 800"

    def test_analytics_insights_size_reduced(self):
        """analytics_insights.py should be under 800 lines."""
        import os
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "routers", "analytics_insights.py")
        with open(path) as f:
            lines = len(f.readlines())
        assert lines < 800, f"analytics_insights.py has {lines} lines, expected < 800"

    def test_learning_intelligence_has_review_priority(self):
        mod = importlib.import_module("routers.learning_intelligence")
        assert hasattr(mod, "review_priority")

    def test_learning_intelligence_has_session_replay(self):
        mod = importlib.import_module("routers.learning_intelligence")
        assert hasattr(mod, "get_session_replay")

    def test_analytics_forecast_has_mastery_forecast(self):
        mod = importlib.import_module("routers.analytics_forecast")
        assert hasattr(mod, "mastery_forecast")

    def test_analytics_forecast_has_fsrs_insights(self):
        mod = importlib.import_module("routers.analytics_forecast")
        assert hasattr(mod, "fsrs_insights")

    def test_analytics_forecast_has_goal_recommendations(self):
        mod = importlib.import_module("routers.analytics_forecast")
        assert hasattr(mod, "goal_recommendations")


# ── Concept Journey API ──


class TestConceptJourney:
    """Test GET /api/analytics/concept-journey/{concept_id}."""

    def test_journey_returns_200(self, client):
        resp = client.get("/api/analytics/concept-journey/nonexistent-concept-xyz")
        assert resp.status_code == 200

    def test_journey_not_found_structure(self, client):
        data = client.get("/api/analytics/concept-journey/nonexistent-xyz").json()
        assert data["concept_id"] == "nonexistent-xyz"
        # Should have events and stats keys
        assert "events" in data
        assert "stats" in data

    def test_journey_valid_concept_has_structure(self, client):
        """Test with a concept that may exist in seed data."""
        resp = client.get("/api/analytics/concept-journey/supervised-learning")
        data = resp.json()
        assert resp.status_code == 200
        assert "concept_id" in data
        assert "events" in data
        assert "stats" in data

    def test_journey_stats_fields(self, client):
        data = client.get("/api/analytics/concept-journey/test-concept").json()
        stats = data.get("stats", {})
        if stats:
            for field in ["total_attempts", "best_score", "improvement", "avg_score"]:
                assert field in stats


# ── Learning Heatmap API ──


class TestLearningHeatmap:
    """Test GET /api/analytics/learning-heatmap/{domain_id}."""

    def test_heatmap_valid_domain(self, client):
        resp = client.get("/api/analytics/learning-heatmap/ai-engineering")
        assert resp.status_code == 200
        data = resp.json()
        assert data["domain_id"] == "ai-engineering"
        assert "subdomains" in data
        assert "summary" in data

    def test_heatmap_summary_fields(self, client):
        data = client.get("/api/analytics/learning-heatmap/ai-engineering").json()
        sm = data["summary"]
        for field in ["total_concepts", "active_concepts", "mastered_concepts", "coverage_pct", "mastery_pct"]:
            assert field in sm

    def test_heatmap_subdomain_structure(self, client):
        data = client.get("/api/analytics/learning-heatmap/machine-learning").json()
        if data.get("subdomains"):
            sub = data["subdomains"][0]
            assert "subdomain_id" in sub
            assert "concepts" in sub
            assert "count" in sub
            assert "avg_intensity" in sub

    def test_heatmap_cell_structure(self, client):
        data = client.get("/api/analytics/learning-heatmap/ai-engineering").json()
        if data.get("subdomains") and data["subdomains"][0].get("concepts"):
            cell = data["subdomains"][0]["concepts"][0]
            for field in ["concept_id", "name", "difficulty", "status", "sessions", "score", "intensity"]:
                assert field in cell
            assert 0 <= cell["intensity"] <= 1

    def test_heatmap_nonexistent_domain(self, client):
        data = client.get("/api/analytics/learning-heatmap/nonexistent-domain").json()
        assert "error" in data or data.get("subdomains") == []


# ── Existing endpoint regressions ──


class TestSplitRegressions:
    """Verify split endpoints still work through the new routers."""

    def test_review_priority_endpoint(self, client):
        resp = client.get("/api/learning/review-priority")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data

    def test_session_replay_endpoint(self, client):
        resp = client.get("/api/learning/session-replay")
        assert resp.status_code == 200
        data = resp.json()
        assert "sessions" in data
        assert "summary" in data

    def test_mastery_forecast_endpoint(self, client):
        resp = client.get("/api/analytics/mastery-forecast/ai-engineering")
        assert resp.status_code == 200
        data = resp.json()
        assert "domain_id" in data
        assert "estimated_days" in data or "error" in data

    def test_fsrs_insights_endpoint(self, client):
        resp = client.get("/api/analytics/fsrs-insights")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_reviewed" in data

    def test_goal_recommendations_endpoint(self, client):
        resp = client.get("/api/analytics/goal-recommendations")
        assert resp.status_code == 200
        data = resp.json()
        assert "recommendations" in data
