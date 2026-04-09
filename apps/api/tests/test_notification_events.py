"""Tests for V2.12 Event-Driven Notification triggers."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from main import app
    return TestClient(app)


@pytest.fixture(autouse=True)
def _clear_stores():
    """Clear notification store and init SQLite between tests."""
    from routers.notifications import _notifications
    _notifications.clear()
    try:
        from db.sqlite_client import init_db
        init_db()
    except Exception:
        pass
    yield
    _notifications.clear()


class TestNotificationEvents:
    """V2.12 — Event-driven notification triggers from learning actions."""

    def test_mastery_assessment_generates_notification(self, client):
        """Recording a mastery assessment should create a mastery notification."""
        from routers.notifications import _notifications
        assert len(_notifications) == 0

        # Record a mastery assessment
        resp = client.post("/api/learning/assess", json={
            "concept_id": "test-concept-1",
            "concept_name": "Test Concept 1",
            "score": 85,
            "mastered": True,
        })
        assert resp.status_code == 200
        assert resp.json()["mastered"] is True

        # Check notification was created
        mastery_notifs = [n for n in _notifications.values() if n["type"] == "mastery"]
        assert len(mastery_notifs) == 1
        assert "Test Concept 1" in mastery_notifs[0]["message"]

    def test_non_mastery_assessment_no_notification(self, client):
        """Non-mastery assessment should NOT create a mastery notification."""
        from routers.notifications import _notifications

        resp = client.post("/api/learning/assess", json={
            "concept_id": "test-concept-2",
            "concept_name": "Test Concept 2",
            "score": 50,
            "mastered": False,
        })
        assert resp.status_code == 200

        mastery_notifs = [n for n in _notifications.values() if n["type"] == "mastery"]
        assert len(mastery_notifs) == 0

    def test_emit_does_not_crash_assessment(self, client):
        """Notification failures should not affect the assessment response."""
        # Even if notification system has issues, assessment should succeed
        resp = client.post("/api/learning/assess", json={
            "concept_id": "test-concept-3",
            "concept_name": "Test Concept 3",
            "score": 90,
            "mastered": True,
        })
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_community_split_discussions_still_work(self, client):
        """V2.12 split: discussions should still work via community_discussions router."""
        from routers.community_discussions import _discussions
        _discussions.clear()

        resp = client.post("/api/community/discussions", json={
            "concept_id": "test-c",
            "title": "Test discussion",
            "content": "Test content here",
            "type": "question",
        })
        assert resp.status_code == 200
        assert resp.json()["concept_id"] == "test-c"

        # List should work
        resp = client.get("/api/community/discussions?concept_id=test-c")
        assert resp.status_code == 200
        assert resp.json()["total"] == 1

        _discussions.clear()

    def test_community_split_content_feedback_still_works(self, client):
        """V2.12 split: content feedback should still work via community_content router."""
        from routers.community_content import _content_feedback
        _content_feedback.clear()

        resp = client.post("/api/community/content-feedback", json={
            "concept_id": "test-concept",
            "category": "inaccurate",
        })
        assert resp.status_code == 200
        assert resp.json()["category"] == "inaccurate"

        # Health dashboard should work
        resp = client.get("/api/community/content-health")
        assert resp.status_code == 200
        assert resp.json()["summary"]["total_feedback"] == 1

        _content_feedback.clear()

    def test_community_original_suggestions_still_work(self, client):
        """V2.12 split: original suggestions should still work in community.py."""
        from routers.community import _suggestions
        _suggestions.clear()

        resp = client.post("/api/community/suggestions", json={
            "type": "concept",
            "title": "New concept suggestion",
            "description": "This is a test suggestion with enough detail",
        })
        assert resp.status_code == 200
        assert resp.json()["type"] == "concept"

        _suggestions.clear()
