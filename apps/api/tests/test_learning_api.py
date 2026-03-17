"""Tests for learning API endpoints."""
import os
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient
import pytest

# Setup temp DB
_tmp_dir = tempfile.mkdtemp()
import db.sqlite_client as sc
sc._DB_DIR = Path(_tmp_dir)
sc.DB_PATH = sc._DB_DIR / "test_learning_api.db"
sc.init_db()

from main import app

client = TestClient(app)


class TestLearningEndpoints:
    def setup_method(self):
        with sc.get_db() as conn:
            conn.execute("DELETE FROM concept_progress")
            conn.execute("DELETE FROM learning_history")
            conn.execute("UPDATE streak SET current_streak=0, longest_streak=0, last_date=''")

    def test_get_stats(self):
        res = client.get("/api/learning/stats?total_concepts=100")
        assert res.status_code == 200
        data = res.json()
        assert data["total_concepts"] == 100
        assert data["mastered_count"] == 0

    def test_start_learning(self):
        res = client.post("/api/learning/start", json={"concept_id": "neural_net"})
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["progress"]["status"] == "learning"

    def test_record_assessment(self):
        client.post("/api/learning/start", json={"concept_id": "backprop"})
        res = client.post("/api/learning/assess", json={
            "concept_id": "backprop",
            "concept_name": "Backpropagation",
            "score": 85.0,
            "mastered": True,
        })
        assert res.status_code == 200
        data = res.json()
        assert data["mastered"] is True

    def test_record_assessment_score_validation(self):
        res = client.post("/api/learning/assess", json={
            "concept_id": "test",
            "concept_name": "Test",
            "score": 150.0,
            "mastered": False,
        })
        assert res.status_code == 422  # Validation error: score > 100

    def test_get_history(self):
        client.post("/api/learning/start", json={"concept_id": "attention"})
        client.post("/api/learning/assess", json={
            "concept_id": "attention",
            "concept_name": "Attention",
            "score": 70,
            "mastered": False,
        })
        res = client.get("/api/learning/history?limit=10")
        assert res.status_code == 200
        data = res.json()
        assert len(data) >= 1

    def test_get_streak(self):
        res = client.get("/api/learning/streak")
        assert res.status_code == 200
        data = res.json()
        assert "current_streak" in data

    def test_get_progress(self):
        client.post("/api/learning/start", json={"concept_id": "cnn"})
        res = client.get("/api/learning/progress/cnn")
        assert res.status_code == 200
        data = res.json()
        assert data["concept_id"] == "cnn"
        assert data["status"] == "learning"

    def test_get_all_progress(self):
        client.post("/api/learning/start", json={"concept_id": "a"})
        client.post("/api/learning/start", json={"concept_id": "b"})
        res = client.get("/api/learning/progress")
        assert res.status_code == 200
        data = res.json()
        assert len(data) >= 2

    def test_sync_endpoint(self):
        res = client.post("/api/learning/sync", json={
            "progress": {
                "concept_x": {
                    "status": "mastered",
                    "mastery_score": 95,
                    "sessions": 5,
                    "last_learn_at": 1710000000,
                }
            },
            "history": [
                {"concept_id": "concept_x", "concept_name": "X", "score": 95, "mastered": True, "timestamp": 1710000000}
            ],
            "streak": {"current": 3, "longest": 7, "lastDate": "2026-03-16"}
        })
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["synced_progress"] >= 1

    def test_sync_validation_limits(self):
        # Progress > 500 should fail
        big_progress = {f"c_{i}": {"status": "learning"} for i in range(501)}
        res = client.post("/api/learning/sync", json={"progress": big_progress})
        assert res.status_code == 422

    def test_recommend(self):
        res = client.get("/api/learning/recommend?top_k=3")
        assert res.status_code == 200
        data = res.json()
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)

    def test_sync_status_whitelist(self):
        """m-11: Invalid status values should be normalized to 'not_started'."""
        res = client.post("/api/learning/sync", json={
            "progress": {
                "wl_valid": {"status": "mastered", "mastery_score": 90, "sessions": 1, "last_learn_at": 9999999999},
                "wl_invalid": {"status": "hacked", "mastery_score": 100, "sessions": 1, "last_learn_at": 9999999999},
                "wl_missing": {"mastery_score": 50, "sessions": 1, "last_learn_at": 9999999999},
            }
        })
        assert res.status_code == 200

        # Valid status should be preserved
        from db.sqlite_client import get_progress
        valid = get_progress("wl_valid")
        assert valid is not None
        assert valid["status"] == "mastered"

        # Invalid status should be normalized to 'not_started'
        invalid = get_progress("wl_invalid")
        assert invalid is not None
        assert invalid["status"] == "not_started"

        # Missing status should default to 'not_started'
        missing = get_progress("wl_missing")
        assert missing is not None
        assert missing["status"] == "not_started"
