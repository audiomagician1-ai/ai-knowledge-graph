"""V3.7 Sprint tests — learning-profile + domain-overview-batch."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from main import app
    return TestClient(app)


# ════════════════════════════════════════════
# Learning Profile API
# ════════════════════════════════════════════

class TestLearningProfile:
    def test_profile_basic(self, client):
        resp = client.get("/api/analytics/learning-profile")
        assert resp.status_code == 200
        data = resp.json()
        assert "overview" in data
        assert "streak" in data
        assert "recent_7d" in data
        assert "domains" in data
        assert "strengths" in data
        assert "weaknesses" in data
        assert "review_status" in data

    def test_profile_overview_shape(self, client):
        resp = client.get("/api/analytics/learning-profile")
        ov = resp.json()["overview"]
        for key in ["total_concepts", "mastered", "learning", "not_started", "completion_pct", "avg_mastered_difficulty"]:
            assert key in ov
        assert ov["completion_pct"] >= 0

    def test_profile_streak_shape(self, client):
        resp = client.get("/api/analytics/learning-profile")
        streak = resp.json()["streak"]
        assert "current" in streak
        assert "longest" in streak

    def test_profile_recent_7d_shape(self, client):
        resp = client.get("/api/analytics/learning-profile")
        r7 = resp.json()["recent_7d"]
        assert "events" in r7
        assert "mastered" in r7
        assert "avg_score" in r7

    def test_profile_review_status(self, client):
        resp = client.get("/api/analytics/learning-profile")
        rs = resp.json()["review_status"]
        assert "due_count" in rs
        assert "overdue_count" in rs

    def test_profile_domains_are_list(self, client):
        resp = client.get("/api/analytics/learning-profile")
        domains = resp.json()["domains"]
        assert isinstance(domains, list)
        for d in domains:
            assert "domain_id" in d
            assert "name" in d
            assert "progress_pct" in d

    def test_profile_strengths_weaknesses(self, client):
        resp = client.get("/api/analytics/learning-profile")
        data = resp.json()
        for entry in data["strengths"] + data["weaknesses"]:
            assert "concept_id" in entry
            assert "name" in entry
            assert "p_mastery" in entry


# ════════════════════════════════════════════
# Domain Overview Batch API
# ════════════════════════════════════════════

class TestDomainOverviewBatch:
    def test_batch_basic(self, client):
        resp = client.get("/api/graph/domain-overview-batch")
        assert resp.status_code == 200
        data = resp.json()
        assert "domains" in data
        assert "total" in data
        assert "aggregate" in data

    def test_batch_has_domains(self, client):
        resp = client.get("/api/graph/domain-overview-batch")
        data = resp.json()
        # In test environment, seed data may or may not be found
        assert data["total"] >= 0
        if data["total"] > 0:
            assert data["total"] == 36  # 36 knowledge spheres when seed data available

    def test_batch_domain_shape(self, client):
        resp = client.get("/api/graph/domain-overview-batch")
        domains = resp.json()["domains"]
        for d in domains:
            assert "domain_id" in d
            assert "name" in d
            assert "concepts" in d
            assert "edges" in d
            assert "subdomains" in d
            assert "difficulty" in d
            assert "progress" in d
            assert d["concepts"] > 0

    def test_batch_domain_difficulty(self, client):
        resp = client.get("/api/graph/domain-overview-batch")
        domains = resp.json()["domains"]
        for d in domains:
            diff = d["difficulty"]
            assert "avg" in diff
            assert "min" in diff
            assert "max" in diff
            if diff["avg"] > 0:
                assert diff["min"] <= diff["avg"] <= diff["max"]

    def test_batch_domain_progress(self, client):
        resp = client.get("/api/graph/domain-overview-batch")
        domains = resp.json()["domains"]
        for d in domains:
            prog = d["progress"]
            assert "mastered" in prog
            assert "learning" in prog
            assert "not_started" in prog
            assert "pct" in prog
            assert prog["mastered"] + prog["learning"] + prog["not_started"] == d["concepts"]

    def test_batch_aggregate(self, client):
        resp = client.get("/api/graph/domain-overview-batch")
        agg = resp.json()["aggregate"]
        assert "total_concepts" in agg
        assert "total_edges" in agg
        assert "domains_started" in agg
