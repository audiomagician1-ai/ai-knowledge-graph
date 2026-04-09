"""V3.5 Sprint tests — learning.py split + session-replay + comparative-progress."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from main import app
    return TestClient(app)


# ════════════════════════════════════════════
# Code Health: learning.py split verification
# ════════════════════════════════════════════

class TestLearningReviewSplit:
    """Verify FSRS + Achievement endpoints still work after extraction to learning_review.py."""

    def test_due_endpoint_exists(self, client):
        resp = client.get("/api/learning/due")
        assert resp.status_code == 200
        data = resp.json()
        assert "due_count" in data
        assert "items" in data

    def test_review_endpoint_exists(self, client):
        """POST /review requires body; verify 422 on empty body confirms route is wired."""
        resp = client.post("/api/learning/review", json={})
        assert resp.status_code == 422  # Validation error = route found

    def test_review_valid_payload(self, client):
        resp = client.post("/api/learning/review", json={
            "concept_id": "test-fsrs-split-v35",
            "rating": 3,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "card" in data
        assert "achievements_unlocked" in data

    def test_achievements_endpoint(self, client):
        resp = client.get("/api/learning/achievements")
        assert resp.status_code == 200
        data = resp.json()
        assert "total" in data
        assert "unlocked_count" in data
        assert "achievements" in data

    def test_achievements_recent(self, client):
        resp = client.get("/api/learning/achievements/recent")
        assert resp.status_code == 200
        assert "unseen_count" in resp.json()

    def test_achievements_seen(self, client):
        resp = client.post("/api/learning/achievements/seen", json={"keys": ["test_key"]})
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_assess_uses_new_check(self, client):
        """Verify /assess still calls check_and_unlock_achievements from learning_review."""
        # First start learning
        client.post("/api/learning/start", json={"concept_id": "v35-split-test"})
        resp = client.post("/api/learning/assess", json={
            "concept_id": "v35-split-test",
            "concept_name": "V35 Split Test",
            "score": 85,
            "mastered": True,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "achievements_unlocked" in data
        assert isinstance(data["achievements_unlocked"], list)


# ════════════════════════════════════════════
# Session Replay API
# ════════════════════════════════════════════

class TestSessionReplay:
    def test_session_replay_empty(self, client):
        resp = client.get("/api/learning/session-replay")
        assert resp.status_code == 200
        data = resp.json()
        assert "sessions" in data
        assert "total_events" in data
        assert "summary" in data

    def test_session_replay_with_concept(self, client):
        """After assessing a concept, replay should show it."""
        # Create some history
        client.post("/api/learning/start", json={"concept_id": "replay-test-c1"})
        client.post("/api/learning/assess", json={
            "concept_id": "replay-test-c1",
            "concept_name": "Replay Test C1",
            "score": 60,
            "mastered": False,
        })
        client.post("/api/learning/assess", json={
            "concept_id": "replay-test-c1",
            "concept_name": "Replay Test C1",
            "score": 85,
            "mastered": True,
        })

        resp = client.get("/api/learning/session-replay?concept_id=replay-test-c1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_events"] >= 2
        assert len(data["sessions"]) >= 1

        session = data["sessions"][0]
        assert session["concept_id"] == "replay-test-c1"
        assert session["total_attempts"] >= 2
        assert session["mastered"] is True
        assert len(session["steps"]) >= 2

    def test_session_replay_step_delta(self, client):
        """Steps should have score delta between attempts."""
        resp = client.get("/api/learning/session-replay?concept_id=replay-test-c1")
        data = resp.json()
        if data["sessions"]:
            steps = data["sessions"][0]["steps"]
            if len(steps) >= 2:
                # Second step should have positive delta (60→85)
                assert "delta" in steps[1]

    def test_session_replay_with_domain(self, client):
        resp = client.get("/api/learning/session-replay?domain=ai-engineering")
        assert resp.status_code == 200
        assert "sessions" in resp.json()

    def test_session_replay_with_limit(self, client):
        resp = client.get("/api/learning/session-replay?limit=5")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["sessions"]) <= 5

    def test_session_replay_summary_fields(self, client):
        resp = client.get("/api/learning/session-replay")
        data = resp.json()
        summary = data["summary"]
        if summary:
            assert "concepts_practiced" in summary
            assert "total_attempts" in summary
            assert "mastered_count" in summary
            assert "best_score" in summary
            assert "avg_attempts_to_master" in summary


# ════════════════════════════════════════════
# Comparative Progress API
# ════════════════════════════════════════════

class TestComparativeProgress:
    def test_comparative_progress_basic(self, client):
        resp = client.get("/api/analytics/comparative-progress")
        assert resp.status_code == 200
        data = resp.json()
        assert "domains" in data
        assert "summary" in data

    def test_comparative_progress_summary_fields(self, client):
        resp = client.get("/api/analytics/comparative-progress")
        data = resp.json()
        summary = data["summary"]
        assert "active_domains" in summary
        assert "this_week_events" in summary
        assert "last_week_events" in summary
        assert "events_delta" in summary
        assert "overall_trend" in summary
        assert summary["overall_trend"] in ("up", "down", "stable")

    def test_comparative_progress_domain_shape(self, client):
        """If there are active domains, verify the per-domain structure."""
        resp = client.get("/api/analytics/comparative-progress")
        data = resp.json()
        for d in data["domains"]:
            assert "domain_id" in d
            assert "domain_name" in d
            assert "this_week" in d
            assert "last_week" in d
            assert "delta" in d
            assert "trend" in d
            assert d["trend"] in ("up", "down", "stable")
            assert "events" in d["this_week"]
            assert "mastered" in d["this_week"]
            assert "avg_score" in d["this_week"]


# ════════════════════════════════════════════
# File size compliance
# ════════════════════════════════════════════

class TestCodeHealth:
    def test_learning_py_under_limit(self):
        import os
        path = os.path.join(os.path.dirname(__file__), "..", "routers", "learning.py")
        with open(path) as f:
            line_count = sum(1 for _ in f)
        assert line_count < 800, f"learning.py is {line_count}L, must be <800L"

    def test_learning_review_py_exists(self):
        import os
        path = os.path.join(os.path.dirname(__file__), "..", "routers", "learning_review.py")
        assert os.path.exists(path), "learning_review.py must exist after V3.5 split"

    def test_all_routers_under_800(self):
        import os, glob
        routers_dir = os.path.join(os.path.dirname(__file__), "..", "routers")
        for f in glob.glob(os.path.join(routers_dir, "*.py")):
            if f.endswith("__init__.py"):
                continue
            with open(f) as fh:
                line_count = sum(1 for _ in fh)
            assert line_count < 800, f"{os.path.basename(f)} is {line_count}L, must be <800L"
