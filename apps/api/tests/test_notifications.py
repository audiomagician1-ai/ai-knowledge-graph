"""Tests for V2.11 Notification Center API."""

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
    """Clear notification store between tests."""
    from routers.notifications import _notifications
    _notifications.clear()
    yield
    _notifications.clear()


class TestNotificationsAPI:
    """V2.11 — Notification Center."""

    def test_list_notifications_empty(self, client):
        resp = client.get("/api/notifications")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["unread_count"] == 0
        assert data["notifications"] == []

    def test_generate_sample_notifications(self, client):
        resp = client.post("/api/notifications/generate")
        assert resp.status_code == 200
        data = resp.json()
        assert data["generated"] == 6
        assert len(data["notifications"]) == 6
        # All should be unread
        assert all(not n["read"] for n in data["notifications"])

    def test_list_notifications_after_generate(self, client):
        client.post("/api/notifications/generate")
        resp = client.get("/api/notifications")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 6
        assert data["unread_count"] == 6

    def test_list_unread_only(self, client):
        client.post("/api/notifications/generate")
        # Mark one as read
        notifs = client.get("/api/notifications").json()["notifications"]
        nid = notifs[0]["id"]
        client.post(f"/api/notifications/{nid}/read")
        # Now filter unread only
        resp = client.get("/api/notifications?unread_only=true")
        data = resp.json()
        assert data["total"] == 5
        assert all(not n["read"] for n in data["notifications"])

    def test_list_by_type(self, client):
        client.post("/api/notifications/generate")
        resp = client.get("/api/notifications?type=mastery")
        data = resp.json()
        assert data["total"] == 1
        assert data["notifications"][0]["type"] == "mastery"

    def test_mark_notification_read(self, client):
        client.post("/api/notifications/generate")
        notifs = client.get("/api/notifications").json()["notifications"]
        nid = notifs[0]["id"]
        resp = client.post(f"/api/notifications/{nid}/read")
        assert resp.status_code == 200
        assert resp.json()["read"] is True
        assert resp.json()["read_at"] is not None

    def test_mark_notification_read_404(self, client):
        resp = client.post("/api/notifications/nonexistent/read")
        assert resp.status_code == 404

    def test_mark_all_read(self, client):
        client.post("/api/notifications/generate")
        resp = client.post("/api/notifications/read-all")
        assert resp.status_code == 200
        assert resp.json()["marked_read"] == 6
        # Verify all are read
        data = client.get("/api/notifications").json()
        assert data["unread_count"] == 0

    def test_dismiss_notification(self, client):
        client.post("/api/notifications/generate")
        notifs = client.get("/api/notifications").json()["notifications"]
        nid = notifs[0]["id"]
        resp = client.delete(f"/api/notifications/{nid}")
        assert resp.status_code == 200
        assert resp.json()["dismissed"] == nid
        # Verify count decreased
        data = client.get("/api/notifications").json()
        assert data["total"] == 5

    def test_dismiss_notification_404(self, client):
        resp = client.delete("/api/notifications/nonexistent")
        assert resp.status_code == 404

    def test_notification_summary(self, client):
        client.post("/api/notifications/generate")
        resp = client.get("/api/notifications/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 6
        assert data["unread"] == 6
        assert "mastery" in data["by_type"]
        assert "streak" in data["by_type"]

    def test_notification_pagination(self, client):
        client.post("/api/notifications/generate")
        resp = client.get("/api/notifications?limit=2&offset=0")
        data = resp.json()
        assert len(data["notifications"]) == 2
        assert data["total"] == 6

    def test_notifications_sorted_newest_first(self, client):
        from routers.notifications import create_notification, NotificationType
        create_notification(NotificationType.mastery, "First", "First message")
        import time; time.sleep(0.01)
        create_notification(NotificationType.streak, "Second", "Second message")
        resp = client.get("/api/notifications")
        notifs = resp.json()["notifications"]
        assert notifs[0]["title"] == "Second"
        assert notifs[1]["title"] == "First"
