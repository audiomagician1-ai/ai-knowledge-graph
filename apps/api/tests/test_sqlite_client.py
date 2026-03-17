"""Tests for sqlite_client — CRUD + streak + stats logic."""
import os
import tempfile
import time
from pathlib import Path
import pytest

# Redirect DB to temp dir before importing
_tmp_dir = tempfile.mkdtemp()
os.environ.setdefault("AKG_DB_DIR", _tmp_dir)

# Patch _DB_DIR before import
import db.sqlite_client as sc
sc._DB_DIR = Path(_tmp_dir)
sc.DB_PATH = sc._DB_DIR / "test_akg.db"
sc.init_db()


class TestConceptProgress:
    def setup_method(self):
        """Clean concept_progress table before each test."""
        with sc.get_db() as conn:
            conn.execute("DELETE FROM concept_progress")
            conn.execute("DELETE FROM learning_history")
            conn.execute("UPDATE streak SET current_streak=0, longest_streak=0, last_date=''")

    def test_start_learning_new_concept(self):
        result = sc.start_learning("neural_networks")
        assert result["concept_id"] == "neural_networks"
        assert result["status"] == "learning"
        assert result["sessions"] == 1

    def test_start_learning_increments_sessions(self):
        sc.start_learning("backprop")
        result = sc.start_learning("backprop")
        assert result["sessions"] == 2
        assert result["status"] == "learning"

    def test_start_learning_keeps_mastered(self):
        sc.upsert_progress("gradient_descent", status="mastered", mastery_score=90, sessions=3)
        result = sc.start_learning("gradient_descent")
        assert result["status"] == "mastered"
        assert result["sessions"] == 4

    def test_record_assessment_marks_mastered(self):
        sc.start_learning("attention")
        result = sc.record_assessment("attention", "Attention Mechanism", 85.0, True)
        assert result["status"] == "mastered"
        assert result["mastery_score"] >= 85.0
        assert result["mastered_at"] is not None

    def test_record_assessment_keeps_learning(self):
        sc.start_learning("transformers")
        result = sc.record_assessment("transformers", "Transformers", 60.0, False)
        assert result["status"] == "learning"
        assert result["mastery_score"] == 60.0

    def test_record_assessment_no_demotion(self):
        """C-06: Once mastered, re-assessment with mastered=False should NOT demote back to learning."""
        sc.start_learning("bert")
        sc.record_assessment("bert", "BERT", 85.0, True)
        p1 = sc.get_progress("bert")
        assert p1["status"] == "mastered"
        assert p1["mastered_at"] is not None
        old_mastered_at = p1["mastered_at"]

        # Re-assess with lower score, mastered=False → should still be mastered
        result = sc.record_assessment("bert", "BERT", 55.0, False)
        assert result["status"] == "mastered", "mastered should not be demoted"
        assert result["mastery_score"] >= 85.0, "mastery_score should keep the higher value"
        assert result["last_score"] == 55.0, "last_score should reflect the new assessment"
        assert result["mastered_at"] == old_mastered_at, "mastered_at should not change"

    def test_upsert_progress_atomic(self):
        sc.upsert_progress("rl", status="learning", mastery_score=30)
        sc.upsert_progress("rl", status="mastered", mastery_score=90)
        result = sc.get_progress("rl")
        assert result is not None
        assert result["status"] == "mastered"
        assert result["mastery_score"] == 90

    def test_get_all_progress(self):
        sc.start_learning("a")
        sc.start_learning("b")
        all_p = sc.get_all_progress()
        assert len(all_p) == 2

    def test_start_learning_atomic_sessions(self):
        """C-05: start_learning should atomically increment sessions in a single connection."""
        # First call: create
        r1 = sc.start_learning("atomic_test")
        assert r1["sessions"] == 1
        assert r1["status"] == "learning"
        # Second call: increment
        r2 = sc.start_learning("atomic_test")
        assert r2["sessions"] == 2
        # Third call: increment again
        r3 = sc.start_learning("atomic_test")
        assert r3["sessions"] == 3

    def test_start_learning_preserves_mastery_score(self):
        """start_learning on existing concept should not reset mastery_score."""
        sc.upsert_progress("preserve_test", status="learning", mastery_score=60, sessions=2)
        result = sc.start_learning("preserve_test")
        assert result["sessions"] == 3
        assert result["status"] == "learning"
        # mastery_score should not be reset
        assert result["mastery_score"] == 60


class TestLearningHistory:
    def setup_method(self):
        with sc.get_db() as conn:
            conn.execute("DELETE FROM learning_history")

    def test_add_and_get_history(self):
        sc.add_history("cnn", "CNN", 80.0, True, time.time())
        sc.add_history("rnn", "RNN", 60.0, False, time.time())
        history = sc.get_history(10)
        assert len(history) == 2
        # Most recent first
        assert history[0]["concept_id"] == "rnn"

    def test_history_limit(self):
        for i in range(20):
            sc.add_history(f"concept_{i}", f"Concept {i}", 50.0 + i, False, time.time() + i)
        history = sc.get_history(5)
        assert len(history) == 5


class TestStreak:
    def setup_method(self):
        with sc.get_db() as conn:
            conn.execute("UPDATE streak SET current_streak=0, longest_streak=0, last_date=''")

    def test_update_streak_first_day(self):
        result = sc.update_streak()
        assert result["current_streak"] == 1
        assert result["longest_streak"] == 1
        assert result["last_date"] == sc._today_str()

    def test_update_streak_same_day_no_increment(self):
        sc.update_streak()
        result = sc.update_streak()
        assert result["current_streak"] == 1

    def test_refresh_streak_broken(self):
        with sc.get_db() as conn:
            conn.execute("UPDATE streak SET current_streak=5, longest_streak=10, last_date='2020-01-01'")
        result = sc.refresh_streak()
        assert result["current_streak"] == 0
        assert result["longest_streak"] == 10


class TestComputeStats:
    def setup_method(self):
        with sc.get_db() as conn:
            conn.execute("DELETE FROM concept_progress")
            conn.execute("UPDATE streak SET current_streak=3, longest_streak=7, last_date=''")

    def test_compute_stats(self):
        sc.upsert_progress("a", status="mastered", mastery_score=90, total_time_sec=120)
        sc.upsert_progress("b", status="learning", mastery_score=50, total_time_sec=60)
        stats = sc.compute_stats(10)
        assert stats["mastered_count"] == 1
        assert stats["learning_count"] == 1
        assert stats["not_started_count"] == 8
        assert stats["total_study_time_sec"] == 180
