"""Tests for V2.11 Content Quality Feedback API."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from main import app
    return TestClient(app)


@pytest.fixture(autouse=True)
def _clear_store():
    """Clear content feedback store between tests."""
    from routers.community_content import _content_feedback
    _content_feedback.clear()
    yield
    _content_feedback.clear()


ADMIN_HEADER = {"Authorization": "Bearer akg-admin-2026"}


class TestContentFeedbackAPI:
    """V2.11 — Content Quality Feedback."""

    def test_submit_content_feedback(self, client):
        resp = client.post("/api/community/content-feedback", json={
            "concept_id": "binary-search",
            "domain_id": "algorithms",
            "category": "inaccurate",
            "comment": "The time complexity mentioned is wrong, should be O(log n) not O(n)",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["concept_id"] == "binary-search"
        assert data["category"] == "inaccurate"
        assert data["resolved"] is False
        assert "id" in data

    def test_submit_positive_feedback(self, client):
        resp = client.post("/api/community/content-feedback", json={
            "concept_id": "sorting-algorithms",
            "domain_id": "algorithms",
            "category": "excellent",
            "comment": "Great explanation with clear examples!",
        })
        assert resp.status_code == 200
        assert resp.json()["category"] == "excellent"

    def test_list_content_feedback_empty(self, client):
        resp = client.get("/api/community/content-feedback")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["feedback"] == []

    def test_list_content_feedback_with_filters(self, client):
        # Submit multiple feedback items
        client.post("/api/community/content-feedback", json={
            "concept_id": "binary-search", "domain_id": "algorithms", "category": "inaccurate"
        })
        client.post("/api/community/content-feedback", json={
            "concept_id": "sorting", "domain_id": "algorithms", "category": "unclear"
        })
        client.post("/api/community/content-feedback", json={
            "concept_id": "neural-nets", "domain_id": "ai", "category": "outdated"
        })

        # Filter by domain
        resp = client.get("/api/community/content-feedback?domain_id=algorithms")
        assert resp.json()["total"] == 2

        # Filter by category
        resp = client.get("/api/community/content-feedback?category=inaccurate")
        assert resp.json()["total"] == 1

        # Filter by concept
        resp = client.get("/api/community/content-feedback?concept_id=neural-nets")
        assert resp.json()["total"] == 1

    def test_resolve_content_feedback(self, client):
        # Submit
        fb = client.post("/api/community/content-feedback", json={
            "concept_id": "binary-search", "domain_id": "algorithms", "category": "inaccurate"
        }).json()

        # Resolve (admin)
        resp = client.patch(f"/api/community/content-feedback/{fb['id']}/resolve", headers=ADMIN_HEADER)
        assert resp.status_code == 200
        assert resp.json()["resolved"] is True
        assert resp.json()["resolved_at"] is not None

    def test_resolve_feedback_requires_admin(self, client):
        fb = client.post("/api/community/content-feedback", json={
            "concept_id": "test", "category": "unclear"
        }).json()
        resp = client.patch(f"/api/community/content-feedback/{fb['id']}/resolve")
        assert resp.status_code == 401

    def test_unresolved_only_filter(self, client):
        client.post("/api/community/content-feedback", json={
            "concept_id": "a", "category": "inaccurate"
        })
        fb2 = client.post("/api/community/content-feedback", json={
            "concept_id": "b", "category": "unclear"
        }).json()
        # Resolve one
        client.patch(f"/api/community/content-feedback/{fb2['id']}/resolve", headers=ADMIN_HEADER)

        resp = client.get("/api/community/content-feedback?unresolved_only=true")
        assert resp.json()["total"] == 1

    def test_content_health_dashboard_empty(self, client):
        resp = client.get("/api/community/content-health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["summary"]["total_feedback"] == 0
        assert data["concepts"] == []

    def test_content_health_dashboard_aggregation(self, client):
        # Multiple feedback for same concept
        client.post("/api/community/content-feedback", json={
            "concept_id": "binary-search", "domain_id": "algorithms", "category": "inaccurate"
        })
        client.post("/api/community/content-feedback", json={
            "concept_id": "binary-search", "domain_id": "algorithms", "category": "unclear"
        })
        client.post("/api/community/content-feedback", json={
            "concept_id": "sorting", "domain_id": "algorithms", "category": "excellent"
        })

        resp = client.get("/api/community/content-health")
        data = resp.json()
        assert data["summary"]["total_feedback"] == 3
        assert data["summary"]["total_issues"] == 2
        assert data["summary"]["concepts_with_issues"] == 1
        # binary-search should be first (more issues)
        assert data["concepts"][0]["concept_id"] == "binary-search"
        assert data["concepts"][0]["issues"] == 2

    def test_content_health_domain_filter(self, client):
        client.post("/api/community/content-feedback", json={
            "concept_id": "binary-search", "domain_id": "algorithms", "category": "inaccurate"
        })
        client.post("/api/community/content-feedback", json={
            "concept_id": "neural-nets", "domain_id": "ai", "category": "outdated"
        })

        resp = client.get("/api/community/content-health?domain_id=algorithms")
        data = resp.json()
        assert data["summary"]["total_feedback"] == 1
        assert len(data["concepts"]) == 1
        assert data["concepts"][0]["concept_id"] == "binary-search"
