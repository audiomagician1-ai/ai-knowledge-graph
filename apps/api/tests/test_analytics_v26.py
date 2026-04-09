"""V2.6 Multi-Domain Intelligence API tests.

Tests:
- GET /api/analytics/domain-recommendation
- GET /api/analytics/study-plan
- GET /api/analytics/learning-journey
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    """Create test client with fresh DB."""
    import os
    os.environ.setdefault("AKG_TEST", "1")

    from main import app
    return TestClient(app)


# ── Domain Recommendation ──────────────────────────────


class TestDomainRecommendation:
    def test_returns_structure(self, client):
        resp = client.get("/api/analytics/domain-recommendation")
        assert resp.status_code == 200
        data = resp.json()
        assert "recommendations" in data
        assert "active_domains" in data
        assert "total_undiscovered" in data
        assert isinstance(data["recommendations"], list)

    def test_limit_param(self, client):
        resp = client.get("/api/analytics/domain-recommendation?limit=3")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["recommendations"]) <= 3

    def test_recommendation_fields(self, client):
        resp = client.get("/api/analytics/domain-recommendation?limit=1")
        data = resp.json()
        if data["recommendations"]:
            rec = data["recommendations"][0]
            assert "domain_id" in rec
            assert "domain_name" in rec
            assert "score" in rec
            assert "reasons" in rec
            assert "cross_link_count" in rec
            assert "total_concepts" in rec
            assert isinstance(rec["reasons"], list)

    def test_invalid_limit(self, client):
        resp = client.get("/api/analytics/domain-recommendation?limit=0")
        assert resp.status_code == 422

    def test_all_domains_covered(self, client):
        """Recommendations + active domains should cover some subset of all domains."""
        resp = client.get("/api/analytics/domain-recommendation?limit=15")
        data = resp.json()
        rec_ids = {r["domain_id"] for r in data["recommendations"]}
        active_ids = {a["domain_id"] for a in data["active_domains"]}
        # No overlap between recommended and active
        assert len(rec_ids & active_ids) == 0


# ── Study Plan ─────────────────────────────────────────


class TestStudyPlan:
    def test_returns_structure(self, client):
        resp = client.get("/api/analytics/study-plan")
        assert resp.status_code == 200
        data = resp.json()
        assert "plan" in data
        assert "summary" in data
        assert "queues" in data
        assert isinstance(data["plan"], list)

    def test_default_7_days(self, client):
        resp = client.get("/api/analytics/study-plan")
        data = resp.json()
        assert len(data["plan"]) == 7
        assert data["summary"]["days"] == 7

    def test_custom_params(self, client):
        resp = client.get("/api/analytics/study-plan?daily_minutes=60&days=3")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["plan"]) == 3
        assert data["summary"]["daily_minutes"] == 60

    def test_plan_day_structure(self, client):
        resp = client.get("/api/analytics/study-plan?days=1")
        data = resp.json()
        day = data["plan"][0]
        assert "day" in day
        assert "items" in day
        assert "total_minutes" in day
        assert "review_count" in day
        assert "learn_count" in day
        assert day["day"] == 1

    def test_summary_totals(self, client):
        resp = client.get("/api/analytics/study-plan?days=3")
        data = resp.json()
        summary = data["summary"]
        assert summary["total_items"] >= 0
        assert summary["total_review"] >= 0
        assert summary["total_learn"] >= 0
        assert summary["total_minutes"] >= 0

    def test_queues_structure(self, client):
        resp = client.get("/api/analytics/study-plan")
        data = resp.json()
        queues = data["queues"]
        assert "review_pending" in queues
        assert "continue_pending" in queues
        assert "new_available" in queues

    def test_invalid_minutes(self, client):
        resp = client.get("/api/analytics/study-plan?daily_minutes=2")
        assert resp.status_code == 422


# ── Learning Journey ───────────────────────────────────


class TestLearningJourney:
    def test_returns_structure(self, client):
        resp = client.get("/api/analytics/learning-journey")
        assert resp.status_code == 200
        data = resp.json()
        assert "events" in data
        assert "total_events" in data
        assert "domain_summary" in data
        assert "stats" in data

    def test_stats_fields(self, client):
        resp = client.get("/api/analytics/learning-journey")
        data = resp.json()
        stats = data["stats"]
        assert "total_mastered" in stats
        assert "domains_started" in stats
        assert "domains_completed" in stats
        assert "current_streak" in stats
        assert stats["total_mastered"] >= 0

    def test_domain_summary_fields(self, client):
        resp = client.get("/api/analytics/learning-journey")
        data = resp.json()
        for ds in data["domain_summary"]:
            assert "domain_id" in ds
            assert "domain_name" in ds
            assert "mastered" in ds
            assert "total" in ds
            assert "percentage" in ds
            assert ds["percentage"] >= 0
            assert ds["percentage"] <= 100

    def test_events_capped_at_200(self, client):
        resp = client.get("/api/analytics/learning-journey")
        data = resp.json()
        assert len(data["events"]) <= 200
