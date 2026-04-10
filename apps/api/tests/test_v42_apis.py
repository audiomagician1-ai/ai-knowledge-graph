"""V4.2 tests — learning portfolio + difficulty tuner."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from main import app
    return TestClient(app)


class TestLearningPortfolio:
    """Verify /learning/portfolio endpoint."""

    def test_portfolio_200(self, client):
        r = client.get("/api/learning/portfolio")
        assert r.status_code == 200
        data = r.json()
        assert "portfolio" in data

    def test_portfolio_overview_shape(self, client):
        r = client.get("/api/learning/portfolio")
        ov = r.json()["portfolio"]["overview"]
        assert "total_mastered" in ov
        assert "total_concepts" in ov
        assert "mastery_pct" in ov
        assert "domains_explored" in ov
        assert "avg_score" in ov
        assert "current_streak" in ov
        assert "learning_days" in ov

    def test_portfolio_skills_radar_is_list(self, client):
        r = client.get("/api/learning/portfolio")
        radar = r.json()["portfolio"]["skills_radar"]
        assert isinstance(radar, list)

    def test_portfolio_has_timeline(self, client):
        r = client.get("/api/learning/portfolio")
        tl = r.json()["portfolio"]["timeline"]
        assert "first_activity" in tl
        assert "last_activity" in tl
        assert "total_sessions" in tl

    def test_portfolio_has_strengths_and_growth(self, client):
        r = client.get("/api/learning/portfolio")
        data = r.json()["portfolio"]
        assert "strengths" in data
        assert "growth_areas" in data
        assert isinstance(data["strengths"], list)
        assert isinstance(data["growth_areas"], list)

    def test_portfolio_has_milestones(self, client):
        r = client.get("/api/learning/portfolio")
        data = r.json()["portfolio"]
        assert "milestones" in data
        assert isinstance(data["milestones"], list)

    def test_portfolio_generated_at(self, client):
        r = client.get("/api/learning/portfolio")
        data = r.json()["portfolio"]
        assert "generated_at" in data
        assert "T" in data["generated_at"]  # ISO 8601 format


class TestDifficultyTuner:
    """Verify /analytics/difficulty-tuner endpoint."""

    def test_tuner_200(self, client):
        r = client.get("/api/analytics/difficulty-tuner")
        assert r.status_code == 200
        data = r.json()
        assert "suggestions" in data
        assert "summary" in data

    def test_tuner_summary_shape(self, client):
        r = client.get("/api/analytics/difficulty-tuner")
        s = r.json()["summary"]
        assert "total_analyzed" in s
        assert "total_flagged" in s
        assert "too_easy" in s
        assert "too_hard" in s

    def test_tuner_custom_threshold(self, client):
        r = client.get("/api/analytics/difficulty-tuner?threshold=1.0&limit=5")
        assert r.status_code == 200
        data = r.json()
        assert len(data["suggestions"]) <= 5

    def test_tuner_suggestion_shape(self, client):
        r = client.get("/api/analytics/difficulty-tuner?threshold=0.5")
        data = r.json()
        if data["suggestions"]:
            s = data["suggestions"][0]
            assert "concept_id" in s
            assert "seed_difficulty" in s
            assert "observed_difficulty" in s
            assert "direction" in s
            assert "confidence" in s
            assert s["direction"] in ("too_easy", "too_hard")

    def test_tuner_sorted_by_confidence(self, client):
        r = client.get("/api/analytics/difficulty-tuner?threshold=0.5")
        data = r.json()
        confs = [s["confidence"] for s in data["suggestions"]]
        assert confs == sorted(confs, reverse=True), "Should be sorted by confidence desc"


class TestCodeHealthV42:
    """File size checks."""

    def test_learning_extended_under_limit(self):
        import os
        path = os.path.join(os.path.dirname(__file__), "..", "routers", "learning_extended.py")
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        assert len(lines) <= 800, f"learning_extended.py: {len(lines)} lines"

    def test_analytics_insights_under_limit(self):
        import os
        path = os.path.join(os.path.dirname(__file__), "..", "routers", "analytics_insights.py")
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        assert len(lines) <= 800, f"analytics_insights.py: {len(lines)} lines"
