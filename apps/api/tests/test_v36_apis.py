"""V3.6 Sprint tests — FSRS insights + goal recommendations."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from main import app
    return TestClient(app)


# ════════════════════════════════════════════
# FSRS Insights API
# ════════════════════════════════════════════

class TestFSRSInsights:
    def test_fsrs_insights_basic(self, client):
        resp = client.get("/api/analytics/fsrs-insights")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_reviewed" in data
        assert "retention_summary" in data
        assert "risk_distribution" in data
        assert "efficiency" in data
        assert "at_risk_concepts" in data

    def test_fsrs_insights_risk_distribution_shape(self, client):
        resp = client.get("/api/analytics/fsrs-insights")
        rd = resp.json()["risk_distribution"]
        assert "high" in rd
        assert "medium" in rd
        assert "low" in rd
        assert all(isinstance(v, int) for v in rd.values())

    def test_fsrs_insights_efficiency_shape(self, client):
        resp = client.get("/api/analytics/fsrs-insights")
        eff = resp.json()["efficiency"]
        # Empty or has expected keys
        if eff:
            for key in ["stable_concepts", "stable_pct", "lapse_rate", "avg_reps_per_concept"]:
                assert key in eff

    def test_fsrs_insights_after_review(self, client):
        """After submitting a review, FSRS insights should have data."""
        # Create review data
        client.post("/api/learning/start", json={"concept_id": "fsrs-insight-test"})
        client.post("/api/learning/assess", json={
            "concept_id": "fsrs-insight-test",
            "concept_name": "FSRS Insight Test",
            "score": 80, "mastered": True,
        })
        client.post("/api/learning/review", json={"concept_id": "fsrs-insight-test", "rating": 3})

        resp = client.get("/api/analytics/fsrs-insights")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_reviewed"] >= 1

    def test_fsrs_insights_retention_summary(self, client):
        resp = client.get("/api/analytics/fsrs-insights")
        data = resp.json()
        rs = data["retention_summary"]
        if data["total_reviewed"] > 0:
            assert "due_count" in rs
            assert "overdue_count" in rs
            assert "avg_stability" in rs
            assert "total_reviews" in rs

    def test_fsrs_insights_at_risk_shape(self, client):
        resp = client.get("/api/analytics/fsrs-insights")
        data = resp.json()
        for c in data["at_risk_concepts"]:
            assert "concept_id" in c
            assert "name" in c
            assert "retrievability" in c
            assert 0 <= c["retrievability"] <= 1
            assert "stability" in c


# ════════════════════════════════════════════
# Goal Recommendations API
# ════════════════════════════════════════════

class TestGoalRecommendations:
    def test_goal_recommendations_basic(self, client):
        resp = client.get("/api/analytics/goal-recommendations")
        assert resp.status_code == 200
        data = resp.json()
        assert "recommendations" in data
        assert "focus_domains" in data
        assert "context" in data

    def test_goal_recommendations_has_entries(self, client):
        resp = client.get("/api/analytics/goal-recommendations")
        data = resp.json()
        recs = data["recommendations"]
        assert len(recs) >= 3  # At least daily_concepts, weekly_mastery, daily_minutes
        types = {r["type"] for r in recs}
        assert "daily_concepts" in types
        assert "weekly_mastery" in types
        assert "daily_minutes" in types

    def test_goal_recommendations_shape(self, client):
        resp = client.get("/api/analytics/goal-recommendations")
        data = resp.json()
        for rec in data["recommendations"]:
            assert "type" in rec
            assert "title" in rec
            assert "value" in rec
            assert "unit" in rec
            assert "rationale" in rec

    def test_goal_context_fields(self, client):
        resp = client.get("/api/analytics/goal-recommendations")
        ctx = resp.json()["context"]
        assert "active_days_7d" in ctx
        assert "avg_daily_events" in ctx
        assert "current_streak" in ctx
        assert "total_mastered" in ctx

    def test_goal_focus_domains_shape(self, client):
        resp = client.get("/api/analytics/goal-recommendations")
        for d in resp.json()["focus_domains"]:
            assert "domain_id" in d
            assert "domain_name" in d
            assert "learning_count" in d
            assert "reason" in d
