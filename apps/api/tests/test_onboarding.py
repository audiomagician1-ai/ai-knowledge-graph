"""Onboarding API tests — recommended start + domain preview."""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestRecommendedStart:
    """GET /api/onboarding/recommended-start"""

    def test_returns_200(self):
        r = client.get("/api/onboarding/recommended-start")
        assert r.status_code == 200

    def test_response_structure(self):
        r = client.get("/api/onboarding/recommended-start")
        data = r.json()
        assert "recommendations" in data
        assert "total_domains" in data
        assert isinstance(data["recommendations"], list)
        assert data["total_domains"] > 0

    def test_recommendation_fields(self):
        r = client.get("/api/onboarding/recommended-start")
        recs = r.json()["recommendations"]
        assert len(recs) > 0
        first = recs[0]
        for key in ("domain_id", "name", "total_concepts", "avg_difficulty",
                     "entry_concepts", "beginner_score", "reason"):
            assert key in first, f"Missing key: {key}"

    def test_sorted_by_beginner_score(self):
        r = client.get("/api/onboarding/recommended-start")
        recs = r.json()["recommendations"]
        scores = [rec["beginner_score"] for rec in recs]
        assert scores == sorted(scores, reverse=True)

    def test_max_12_recommendations(self):
        r = client.get("/api/onboarding/recommended-start")
        assert len(r.json()["recommendations"]) <= 12

    def test_cache_header(self):
        r = client.get("/api/onboarding/recommended-start")
        assert "max-age=3600" in r.headers.get("cache-control", "")


class TestDomainPreview:
    """GET /api/onboarding/domain-preview/{domain_id}"""

    def test_returns_200_for_valid_domain(self):
        r = client.get("/api/onboarding/domain-preview/ai-engineering")
        assert r.status_code == 200

    def test_404_for_invalid_domain(self):
        r = client.get("/api/onboarding/domain-preview/nonexistent-domain")
        assert r.status_code == 404

    def test_response_structure(self):
        r = client.get("/api/onboarding/domain-preview/ai-engineering")
        data = r.json()
        for key in ("domain_id", "total_concepts", "total_edges",
                     "entry_concepts", "difficulty_distribution",
                     "subdomain_summary", "estimated_total_hours",
                     "avg_difficulty"):
            assert key in data, f"Missing key: {key}"

    def test_entry_concepts_sorted_by_difficulty(self):
        r = client.get("/api/onboarding/domain-preview/ai-engineering")
        entries = r.json()["entry_concepts"]
        diffs = [e["difficulty"] for e in entries]
        assert diffs == sorted(diffs)

    def test_entry_concepts_max_10(self):
        r = client.get("/api/onboarding/domain-preview/ai-engineering")
        assert len(r.json()["entry_concepts"]) <= 10

    def test_difficulty_distribution_10_levels(self):
        r = client.get("/api/onboarding/domain-preview/ai-engineering")
        dist = r.json()["difficulty_distribution"]
        assert len(dist) == 10
        assert dist[0]["level"] == 1
        assert dist[-1]["level"] == 10

    def test_subdomain_summary_non_empty(self):
        r = client.get("/api/onboarding/domain-preview/ai-engineering")
        assert len(r.json()["subdomain_summary"]) > 0

    def test_entry_concept_fields(self):
        r = client.get("/api/onboarding/domain-preview/ai-engineering")
        entries = r.json()["entry_concepts"]
        if entries:
            first = entries[0]
            for key in ("id", "name", "difficulty", "estimated_minutes"):
                assert key in first, f"Missing key: {key}"