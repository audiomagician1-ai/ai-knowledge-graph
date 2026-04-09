"""V2.7 Smart Analytics API tests.

Tests:
- GET /api/analytics/weak-concepts
- GET /api/analytics/learning-efficiency
- GET /api/analytics/difficulty-calibration
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    import os
    os.environ.setdefault("AKG_TEST", "1")
    from main import app
    return TestClient(app)


# ── Weak Concepts ──────────────────────────────────────


class TestWeakConcepts:
    def test_returns_structure(self, client):
        resp = client.get("/api/analytics/weak-concepts")
        assert resp.status_code == 200
        data = resp.json()
        assert "weak_concepts" in data
        assert "total_weak" in data
        assert "total_assessed" in data
        assert isinstance(data["weak_concepts"], list)
        assert data["total_assessed"] >= 0

    def test_limit_param(self, client):
        resp = client.get("/api/analytics/weak-concepts?limit=3")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["weak_concepts"]) <= 3

    def test_weak_concept_fields(self, client):
        resp = client.get("/api/analytics/weak-concepts")
        data = resp.json()
        for wc in data["weak_concepts"]:
            assert "concept_id" in wc
            assert "weakness_score" in wc
            assert "reasons" in wc
            assert "suggestion" in wc
            assert isinstance(wc["reasons"], list)
            assert wc["weakness_score"] > 0

    def test_invalid_limit(self, client):
        resp = client.get("/api/analytics/weak-concepts?limit=0")
        assert resp.status_code == 422

    def test_ordered_by_weakness(self, client):
        resp = client.get("/api/analytics/weak-concepts?limit=20")
        data = resp.json()
        scores = [wc["weakness_score"] for wc in data["weak_concepts"]]
        assert scores == sorted(scores, reverse=True)


# ── Learning Efficiency ────────────────────────────────


class TestLearningEfficiency:
    def test_returns_structure(self, client):
        resp = client.get("/api/analytics/learning-efficiency")
        assert resp.status_code == 200
        data = resp.json()
        assert "concepts" in data
        assert "total_assessed" in data
        assert "domain_efficiency" in data
        assert "global" in data

    def test_global_stats_fields(self, client):
        resp = client.get("/api/analytics/learning-efficiency")
        data = resp.json()
        g = data["global"]
        assert "avg_efficiency" in g
        assert "median_efficiency" in g
        assert "total_concepts_assessed" in g
        assert "total_mastered" in g
        assert g["total_concepts_assessed"] >= 0

    def test_concept_fields(self, client):
        resp = client.get("/api/analytics/learning-efficiency")
        data = resp.json()
        for c in data["concepts"]:
            assert "concept_id" in c
            assert "efficiency" in c
            assert "sessions" in c
            assert "score" in c
            assert c["sessions"] > 0

    def test_domain_efficiency_fields(self, client):
        resp = client.get("/api/analytics/learning-efficiency")
        data = resp.json()
        for de in data["domain_efficiency"]:
            assert "domain_id" in de
            assert "avg_efficiency" in de
            assert "concepts_attempted" in de
            assert "concepts_mastered" in de
            assert "avg_sessions_per_concept" in de

    def test_concepts_sorted_by_efficiency(self, client):
        resp = client.get("/api/analytics/learning-efficiency")
        data = resp.json()
        effs = [c["efficiency"] for c in data["concepts"]]
        assert effs == sorted(effs)


# ── Difficulty Calibration ─────────────────────────────


class TestDifficultyCalibration:
    def test_returns_structure(self, client):
        resp = client.get("/api/analytics/difficulty-calibration")
        assert resp.status_code == 200
        data = resp.json()
        assert "domain_id" in data
        assert "calibration" in data
        assert "total_assessed" in data
        assert "miscalibrated_count" in data
        assert "difficulty_summary" in data

    def test_custom_domain(self, client):
        resp = client.get("/api/analytics/difficulty-calibration?domain_id=programming")
        assert resp.status_code == 200
        data = resp.json()
        assert data["domain_id"] == "programming"

    def test_nonexistent_domain(self, client):
        resp = client.get("/api/analytics/difficulty-calibration?domain_id=nonexistent-domain-xyz")
        assert resp.status_code == 200
        data = resp.json()
        assert data["calibration"] == []

    def test_calibration_fields(self, client):
        resp = client.get("/api/analytics/difficulty-calibration")
        data = resp.json()
        for c in data["calibration"]:
            assert "concept_id" in c
            assert "seed_difficulty" in c
            assert "actual_score" in c
            assert "gap" in c
            assert "miscalibrated" in c
            assert isinstance(c["miscalibrated"], bool)

    def test_difficulty_summary_fields(self, client):
        resp = client.get("/api/analytics/difficulty-calibration")
        data = resp.json()
        for s in data["difficulty_summary"]:
            assert "difficulty" in s
            assert "count" in s
            assert "avg_score" in s
            assert "mastery_rate" in s
            assert s["count"] > 0

    def test_calibration_sorted_by_gap(self, client):
        resp = client.get("/api/analytics/difficulty-calibration")
        data = resp.json()
        gaps = [abs(c["gap"]) for c in data["calibration"]]
        assert gaps == sorted(gaps, reverse=True)
