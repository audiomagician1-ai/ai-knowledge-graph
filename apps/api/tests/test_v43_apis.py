"""V4.3 Tests — DifficultyTunerWidget + PortfolioExportWidget API verification.

Tests the response schemas and business logic for:
- GET /api/analytics/difficulty-tuner (auto-calibration suggestions)
- GET /api/learning/portfolio (comprehensive exportable learning portfolio)
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# ── Difficulty Tuner API ──
class TestDifficultyTuner:
    def test_returns_200(self):
        resp = client.get("/api/analytics/difficulty-tuner")
        assert resp.status_code == 200

    def test_has_suggestions_key(self):
        data = client.get("/api/analytics/difficulty-tuner").json()
        assert "suggestions" in data
        assert isinstance(data["suggestions"], list)

    def test_has_summary_key(self):
        data = client.get("/api/analytics/difficulty-tuner").json()
        assert "summary" in data
        s = data["summary"]
        assert "total_flagged" in s
        assert "too_easy" in s
        assert "too_hard" in s

    def test_limit_param(self):
        data = client.get("/api/analytics/difficulty-tuner?limit=5").json()
        assert len(data["suggestions"]) <= 5

    def test_threshold_param(self):
        resp = client.get("/api/analytics/difficulty-tuner?threshold=1.0")
        assert resp.status_code == 200

    def test_suggestion_schema(self):
        data = client.get("/api/analytics/difficulty-tuner?limit=50").json()
        for s in data["suggestions"][:5]:
            assert "concept_id" in s
            assert "name" in s
            assert "direction" in s
            assert s["direction"] in ("too_easy", "too_hard")
            assert "confidence" in s
            assert 0 <= s["confidence"] <= 1
            assert "seed_difficulty" in s
            assert "suggested_difficulty" in s

    def test_summary_consistency(self):
        data = client.get("/api/analytics/difficulty-tuner?limit=100").json()
        easy = sum(1 for s in data["suggestions"] if s["direction"] == "too_easy")
        hard = sum(1 for s in data["suggestions"] if s["direction"] == "too_hard")
        assert data["summary"]["too_easy"] >= easy or data["summary"]["too_easy"] == easy
        assert data["summary"]["too_hard"] >= hard or data["summary"]["too_hard"] == hard


# ── Learning Portfolio API ──
class TestLearningPortfolio:
    def test_returns_200(self):
        resp = client.get("/api/learning/portfolio")
        assert resp.status_code == 200

    def test_has_skills_radar(self):
        data = client.get("/api/learning/portfolio").json()
        p = data["portfolio"]
        assert "skills_radar" in p
        assert isinstance(p["skills_radar"], list)

    def test_has_overview(self):
        data = client.get("/api/learning/portfolio").json()
        p = data["portfolio"]
        assert "overview" in p
        o = p["overview"]
        assert "total_concepts" in o
        assert "total_mastered" in o
        assert "domains_explored" in o
        assert "mastery_pct" in o

    def test_has_milestones(self):
        data = client.get("/api/learning/portfolio").json()
        p = data["portfolio"]
        assert "milestones" in p
        assert isinstance(p["milestones"], list)

    def test_has_strengths_and_growth(self):
        data = client.get("/api/learning/portfolio").json()
        p = data["portfolio"]
        assert "strengths" in p
        assert "growth_areas" in p
        assert isinstance(p["strengths"], list)
        assert isinstance(p["growth_areas"], list)

    def test_has_timeline(self):
        data = client.get("/api/learning/portfolio").json()
        p = data["portfolio"]
        assert "timeline" in p
        tl = p["timeline"]
        assert "total_days" in tl

    def test_skills_radar_schema(self):
        data = client.get("/api/learning/portfolio").json()
        p = data["portfolio"]
        for s in p["skills_radar"][:3]:
            assert "domain_id" in s
            assert "domain_name" in s
            assert "mastery_pct" in s
            assert isinstance(s["mastery_pct"], (int, float))


# ── Code Health Verification ──
class TestV43CodeHealth:
    def test_all_routers_under_800_lines(self):
        import glob
        for path in glob.glob("routers/*.py"):
            with open(path) as f:
                lines = len(f.readlines())
            name = path.split("\\")[-1] if "\\" in path else path.split("/")[-1]
            assert lines <= 800, f"{name} is {lines}L, exceeds 800L limit"
