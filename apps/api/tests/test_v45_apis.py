"""V4.5 Tests — Daily Summary API + Achievement showcase verification."""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestDailySummary:
    def test_returns_200(self):
        resp = client.get("/api/analytics/daily-summary")
        assert resp.status_code == 200

    def test_has_date(self):
        data = client.get("/api/analytics/daily-summary").json()
        assert "date" in data
        assert len(data["date"]) == 10  # YYYY-MM-DD

    def test_has_streak(self):
        data = client.get("/api/analytics/daily-summary").json()
        assert "streak" in data
        assert "current" in data["streak"]
        assert "longest" in data["streak"]

    def test_has_today(self):
        data = client.get("/api/analytics/daily-summary").json()
        assert "today" in data
        t = data["today"]
        assert "events" in t
        assert "mastered" in t
        assert "domains_active" in t

    def test_has_reviews(self):
        data = client.get("/api/analytics/daily-summary").json()
        r = data["reviews"]
        assert "due" in r
        assert "overdue" in r

    def test_has_progress(self):
        data = client.get("/api/analytics/daily-summary").json()
        p = data["progress"]
        assert "total_mastered" in p
        assert "total_learning" in p
        assert p["total_concepts"] > 0

    def test_has_recommended_action(self):
        data = client.get("/api/analytics/daily-summary").json()
        ra = data["recommended_action"]
        assert "type" in ra
        assert ra["type"] in ("review", "continue", "explore")
        assert "label" in ra
        assert "priority" in ra
        assert "route" in ra

    def test_has_motivation(self):
        data = client.get("/api/analytics/daily-summary").json()
        assert "motivation" in data
        assert len(data["motivation"]) > 0


class TestAchievementsForShowcase:
    """Verify the existing achievements API has the fields needed by AchievementShowcaseWidget."""

    def test_returns_200(self):
        resp = client.get("/api/learning/achievements")
        assert resp.status_code == 200

    def test_has_total_and_unlocked(self):
        data = client.get("/api/learning/achievements").json()
        assert "total" in data
        assert "unlocked_count" in data
        assert data["total"] >= 20

    def test_has_categories(self):
        data = client.get("/api/learning/achievements").json()
        cats = data["categories"]
        for cat in ["learning", "streak", "domain", "assessment", "review", "special"]:
            assert cat in cats
            assert "total" in cats[cat]
            assert "unlocked" in cats[cat]

    def test_achievement_schema(self):
        data = client.get("/api/learning/achievements").json()
        for a in data["achievements"][:5]:
            assert "key" in a
            assert "category" in a
            assert "name" in a
            assert "description" in a
            assert "tier" in a
            assert a["tier"] in ("bronze", "silver", "gold", "platinum")
            assert "unlocked" in a


class TestV45CodeHealth:
    def test_analytics_profile_under_800(self):
        with open("routers/analytics_profile.py") as f:
            lines = len(f.readlines())
        assert lines <= 800, f"analytics_profile.py is {lines}L"
