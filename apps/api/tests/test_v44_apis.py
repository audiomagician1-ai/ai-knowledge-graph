"""V4.4 Tests — Learning Calendar API + Knowledge Map Stats API."""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestLearningCalendar:
    def test_returns_200(self):
        resp = client.get("/api/analytics/learning-calendar")
        assert resp.status_code == 200

    def test_has_months_and_summary(self):
        data = client.get("/api/analytics/learning-calendar").json()
        assert "months" in data
        assert "summary" in data
        assert isinstance(data["months"], list)

    def test_summary_schema(self):
        s = client.get("/api/analytics/learning-calendar").json()["summary"]
        assert "total_active_days" in s
        assert "total_events" in s
        assert "total_mastered" in s
        assert "upcoming_reviews" in s
        assert "period_start" in s
        assert "period_end" in s

    def test_months_param(self):
        data = client.get("/api/analytics/learning-calendar?months=1").json()
        # At least 1 month, plus the future projection month
        assert len(data["months"]) >= 1

    def test_month_structure(self):
        data = client.get("/api/analytics/learning-calendar?months=2").json()
        for m in data["months"]:
            assert "month" in m
            assert "label" in m
            assert "days" in m
            assert isinstance(m["days"], list)
            assert "total_events" in m

    def test_day_cell_schema(self):
        data = client.get("/api/analytics/learning-calendar?months=1").json()
        for m in data["months"]:
            for d in m["days"][:3]:
                assert "date" in d
                assert "events_count" in d
                assert "mastered_count" in d
                assert "reviews_due" in d
                assert "intensity" in d
                assert d["intensity"] >= 0 and d["intensity"] <= 4


class TestKnowledgeMapStats:
    def test_returns_200(self):
        resp = client.get("/api/analytics/knowledge-map-stats")
        assert resp.status_code == 200

    def test_has_coverage(self):
        data = client.get("/api/analytics/knowledge-map-stats").json()
        assert "coverage" in data
        c = data["coverage"]
        assert "total_concepts" in c
        assert c["total_concepts"] > 0
        assert "mastered" in c
        assert "coverage_pct" in c

    def test_has_domains(self):
        data = client.get("/api/analytics/knowledge-map-stats").json()
        assert "domains" in data
        d = data["domains"]
        assert "total" in d
        assert d["total"] == 36
        assert "explored" in d
        assert "top" in d

    def test_has_difficulty_breakdown(self):
        data = client.get("/api/analytics/knowledge-map-stats").json()
        assert "difficulty_breakdown" in data
        assert isinstance(data["difficulty_breakdown"], list)

    def test_has_exploration_profile(self):
        data = client.get("/api/analytics/knowledge-map-stats").json()
        assert "exploration_profile" in data
        ep = data["exploration_profile"]
        assert "depth_score" in ep
        assert "breadth_score" in ep
        assert "style" in ep
        assert ep["style"] in ("深度型", "广度型", "均衡型")


class TestV44CodeHealth:
    def test_analytics_experience_under_800(self):
        with open("routers/analytics_experience.py") as f:
            lines = len(f.readlines())
        assert lines <= 800, f"analytics_experience.py is {lines}L"

    def test_analytics_planning_under_800(self):
        with open("routers/analytics_planning.py") as f:
            lines = len(f.readlines())
        assert lines <= 800, f"analytics_planning.py is {lines}L"
