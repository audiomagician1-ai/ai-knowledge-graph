"""Comprehensive tests for Achievement System.

Tests cover:
1. AchievementDef — definitions and catalog integrity
2. AchievementEngine — check logic, status computation
3. Achievement DB operations (schema v5, CRUD)
4. Achievement API endpoints (/achievements, /achievements/recent, /achievements/seen)
5. Integration — achievements triggered by /assess and /review

Issue: #37
"""

import json
import os
import tempfile
import time
from pathlib import Path

import pytest

# ── Setup temp DB before importing app ──
_tmp_dir = tempfile.mkdtemp()
import db.sqlite_client as sc
sc._DB_DIR = Path(_tmp_dir)
sc.DB_PATH = sc._DB_DIR / "test_achievements.db"
sc.init_db()

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# ════════════════════════════════════════════════════════
# 1. Achievement Definition Tests
# ════════════════════════════════════════════════════════

from engines.learning.achievements import (
    ACHIEVEMENTS, ACHIEVEMENT_MAP, AchievementDef, AchievementEngine, _pct,
)


class TestAchievementDefinitions:
    """Test achievement catalog integrity."""

    def test_achievements_not_empty(self):
        assert len(ACHIEVEMENTS) >= 15, "Should have at least 15 achievements"

    def test_unique_keys(self):
        keys = [a.key for a in ACHIEVEMENTS]
        assert len(keys) == len(set(keys)), "Achievement keys must be unique"

    def test_map_matches_list(self):
        assert len(ACHIEVEMENT_MAP) == len(ACHIEVEMENTS)
        for a in ACHIEVEMENTS:
            assert a.key in ACHIEVEMENT_MAP

    def test_valid_categories(self):
        valid = {'learning', 'streak', 'domain', 'assessment', 'review', 'special'}
        for a in ACHIEVEMENTS:
            assert a.category in valid, f"Invalid category '{a.category}' for {a.key}"

    def test_valid_tiers(self):
        valid = {'bronze', 'silver', 'gold', 'platinum'}
        for a in ACHIEVEMENTS:
            assert a.tier in valid, f"Invalid tier '{a.tier}' for {a.key}"

    def test_all_have_required_fields(self):
        for a in ACHIEVEMENTS:
            assert a.key, f"Missing key"
            assert a.name, f"Missing name for {a.key}"
            assert a.description, f"Missing description for {a.key}"
            assert a.icon, f"Missing icon for {a.key}"
            assert callable(a.check), f"check must be callable for {a.key}"

    def test_to_dict(self):
        a = ACHIEVEMENTS[0]
        d = a.to_dict()
        assert d['key'] == a.key
        assert d['category'] == a.category
        assert d['name'] == a.name
        assert d['tier'] == a.tier
        assert 'check' not in d  # check function should not be serialized

    def test_pct_helper(self):
        assert _pct(0, 10) == 0.0
        assert _pct(5, 10) == 50.0
        assert _pct(10, 10) == 100.0
        assert _pct(15, 10) == 100.0  # Clamped
        assert _pct(0, 0) == 100.0    # Edge case


# ════════════════════════════════════════════════════════
# 2. AchievementEngine Tests
# ════════════════════════════════════════════════════════

class TestAchievementEngine:
    """Test the check engine logic."""

    def setup_method(self):
        self.engine = AchievementEngine()

    def _base_stats(self, **overrides) -> dict:
        """Create a base stats dict with all zeros, then apply overrides."""
        stats = {
            'mastered_count': 0, 'learning_count': 0, 'total_concepts': 0,
            'current_streak': 0, 'longest_streak': 0,
            'total_assessments': 0, 'highest_score': 0,
            'high_scores_90': 0, 'perfect_scores': 0,
            'total_reviews': 0, 'domains_started': 0,
            'domains_mastered_5': 0, 'domains_mastered_10': 0,
            'mastered_today': 0, 'mastered_milestones': 0,
            'total_study_time_sec': 0,
        }
        stats.update(overrides)
        return stats

    def test_no_achievements_for_zero_stats(self):
        stats = self._base_stats()
        newly = self.engine.check_all(stats, set())
        assert len(newly) == 0

    def test_first_light_unlocked(self):
        stats = self._base_stats(mastered_count=1)
        newly = self.engine.check_all(stats, set())
        keys = [a['key'] for a in newly]
        assert 'first_light' in keys

    def test_already_unlocked_not_duplicated(self):
        stats = self._base_stats(mastered_count=1)
        newly = self.engine.check_all(stats, {'first_light'})
        keys = [a['key'] for a in newly]
        assert 'first_light' not in keys

    def test_multiple_achievements_at_once(self):
        stats = self._base_stats(
            mastered_count=10,
            total_assessments=5,
            longest_streak=3,
        )
        newly = self.engine.check_all(stats, set())
        keys = [a['key'] for a in newly]
        assert 'first_light' in keys
        assert 'explorer_10' in keys
        assert 'streak_3' in keys
        assert 'first_assessment' in keys

    def test_streak_achievements(self):
        stats = self._base_stats(longest_streak=7)
        newly = self.engine.check_all(stats, set())
        keys = [a['key'] for a in newly]
        assert 'streak_3' in keys
        assert 'streak_7' in keys
        assert 'streak_14' not in keys

    def test_assessment_achievements(self):
        stats = self._base_stats(
            total_assessments=15,
            highest_score=100,
            high_scores_90=10,
        )
        newly = self.engine.check_all(stats, set())
        keys = [a['key'] for a in newly]
        assert 'first_assessment' in keys
        assert 'perfect_score' in keys
        assert 'high_achiever' in keys

    def test_review_achievements(self):
        stats = self._base_stats(total_reviews=10)
        newly = self.engine.check_all(stats, set())
        keys = [a['key'] for a in newly]
        assert 'first_review' in keys
        assert 'review_10' in keys
        assert 'review_50' not in keys

    def test_domain_achievements(self):
        stats = self._base_stats(domains_started=3, domains_mastered_5=1)
        newly = self.engine.check_all(stats, set())
        keys = [a['key'] for a in newly]
        assert 'domain_explorer' in keys
        assert 'domain_deep_5' in keys
        assert 'domain_deep_10' not in keys

    def test_special_achievements(self):
        stats = self._base_stats(mastered_milestones=5, mastered_today=5)
        newly = self.engine.check_all(stats, set())
        keys = [a['key'] for a in newly]
        assert 'milestone_master' in keys
        assert 'speed_learner' in keys

    def test_get_all_with_status(self):
        stats = self._base_stats(mastered_count=5)
        unlocked_map = {
            'first_light': {'unlocked_at': 1000.0, 'seen': True, 'progress': 100.0}
        }
        result = self.engine.get_all_with_status(stats, unlocked_map)
        assert len(result) == len(ACHIEVEMENTS)

        first = next(a for a in result if a['key'] == 'first_light')
        assert first['unlocked'] is True
        assert first['seen'] is True
        assert first['progress'] == 100.0

        explorer = next(a for a in result if a['key'] == 'explorer_10')
        assert explorer['unlocked'] is False
        assert explorer['progress'] == 50.0  # 5/10 = 50%

    def test_progress_values_are_reasonable(self):
        stats = self._base_stats(mastered_count=25, longest_streak=5)
        result = self.engine.get_all_with_status(stats, {})
        for ach in result:
            assert 0 <= ach['progress'] <= 100, f"{ach['key']} progress={ach['progress']}"


# ════════════════════════════════════════════════════════
# 3. Achievement DB Tests
# ════════════════════════════════════════════════════════

class TestAchievementDB:
    """Test achievement DB operations."""

    def setup_method(self):
        with sc.get_db() as conn:
            conn.execute("DELETE FROM user_achievements")
            conn.execute("DELETE FROM concept_progress")
            conn.execute("DELETE FROM learning_history")

    def test_schema_v5_table_exists(self):
        with sc.get_db() as conn:
            row = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='user_achievements'"
            ).fetchone()
            assert row is not None

    def test_get_unlocked_keys_empty(self):
        keys = sc.get_unlocked_keys()
        assert keys == set()

    def test_unlock_achievement(self):
        result = sc.unlock_achievement("first_light", progress=100.0)
        assert result is True  # newly unlocked

    def test_unlock_achievement_idempotent(self):
        sc.unlock_achievement("first_light")
        result = sc.unlock_achievement("first_light")
        assert result is False  # already existed

    def test_get_unlocked_keys_after_unlock(self):
        sc.unlock_achievement("first_light")
        sc.unlock_achievement("streak_3")
        keys = sc.get_unlocked_keys()
        assert keys == {'first_light', 'streak_3'}

    def test_get_unlocked_map(self):
        sc.unlock_achievement("first_light", progress=100.0)
        m = sc.get_unlocked_map()
        assert 'first_light' in m
        assert m['first_light']['progress'] == 100.0
        assert m['first_light']['seen'] is False
        assert m['first_light']['unlocked_at'] > 0

    def test_mark_achievements_seen(self):
        sc.unlock_achievement("first_light")
        sc.unlock_achievement("streak_3")
        count = sc.mark_achievements_seen(["first_light"])
        assert count == 1

        m = sc.get_unlocked_map()
        assert m['first_light']['seen'] is True
        assert m['streak_3']['seen'] is False

    def test_mark_achievements_seen_empty(self):
        count = sc.mark_achievements_seen([])
        assert count == 0

    def test_mark_already_seen(self):
        sc.unlock_achievement("first_light")
        sc.mark_achievements_seen(["first_light"])
        count = sc.mark_achievements_seen(["first_light"])
        assert count == 0  # Already seen

    def test_get_unseen_achievements(self):
        sc.unlock_achievement("first_light")
        sc.unlock_achievement("streak_3")
        sc.mark_achievements_seen(["first_light"])

        unseen = sc.get_unseen_achievements()
        assert len(unseen) == 1
        assert unseen[0]['achievement_key'] == 'streak_3'

    def test_get_all_achievements(self):
        sc.unlock_achievement("a1")
        sc.unlock_achievement("a2")
        all_ach = sc.get_all_achievements()
        assert len(all_ach) == 2


# ════════════════════════════════════════════════════════
# 4. Achievement API Tests
# ════════════════════════════════════════════════════════

class TestAchievementAPI:
    """Test achievement API endpoints."""

    def setup_method(self):
        with sc.get_db() as conn:
            conn.execute("DELETE FROM user_achievements")
            conn.execute("DELETE FROM concept_progress")
            conn.execute("DELETE FROM learning_history")
            conn.execute("UPDATE streak SET current_streak=0, longest_streak=0, last_date=''")

    def test_get_achievements_empty(self):
        res = client.get("/api/learning/achievements")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] >= 15
        assert data["unlocked_count"] == 0
        assert "categories" in data
        assert "achievements" in data
        assert len(data["achievements"]) == data["total"]

    def test_get_achievements_has_categories(self):
        res = client.get("/api/learning/achievements")
        data = res.json()
        cats = data["categories"]
        assert "learning" in cats
        assert "streak" in cats
        assert cats["learning"]["total"] >= 3

    def test_get_achievements_structure(self):
        res = client.get("/api/learning/achievements")
        data = res.json()
        ach = data["achievements"][0]
        assert "key" in ach
        assert "name" in ach
        assert "description" in ach
        assert "icon" in ach
        assert "tier" in ach
        assert "category" in ach
        assert "unlocked" in ach
        assert "progress" in ach

    def test_recent_achievements_empty(self):
        res = client.get("/api/learning/achievements/recent")
        assert res.status_code == 200
        data = res.json()
        assert data["unseen_count"] == 0
        assert data["achievements"] == []

    def test_mark_seen(self):
        sc.unlock_achievement("first_light")
        res = client.post("/api/learning/achievements/seen", json={"keys": ["first_light"]})
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["marked_count"] == 1

    def test_mark_seen_nonexistent(self):
        res = client.post("/api/learning/achievements/seen", json={"keys": ["nonexistent"]})
        assert res.status_code == 200
        data = res.json()
        assert data["marked_count"] == 0


# ════════════════════════════════════════════════════════
# 5. Integration Tests — achievements via /assess and /review
# ════════════════════════════════════════════════════════

class TestAchievementIntegration:
    """Test achievements triggered by learning events."""

    def setup_method(self):
        with sc.get_db() as conn:
            conn.execute("DELETE FROM user_achievements")
            conn.execute("DELETE FROM concept_progress")
            conn.execute("DELETE FROM learning_history")
            conn.execute("UPDATE streak SET current_streak=0, longest_streak=0, last_date=''")

    def test_assess_triggers_first_assessment(self):
        """First assessment should unlock 'first_assessment' achievement."""
        client.post("/api/learning/start", json={"concept_id": "ach_test_1"})
        res = client.post("/api/learning/assess", json={
            "concept_id": "ach_test_1",
            "concept_name": "Achievement Test 1",
            "score": 85,
            "mastered": True,
        })
        assert res.status_code == 200
        data = res.json()
        assert "achievements_unlocked" in data
        unlocked_keys = [a['key'] for a in data['achievements_unlocked']]
        assert 'first_assessment' in unlocked_keys
        assert 'first_light' in unlocked_keys  # Also mastered first concept

    def test_assess_no_duplicate_unlock(self):
        """Second assessment should not re-unlock already earned achievements."""
        client.post("/api/learning/start", json={"concept_id": "dup_1"})
        res1 = client.post("/api/learning/assess", json={
            "concept_id": "dup_1",
            "concept_name": "Dup 1",
            "score": 85,
            "mastered": True,
        })
        first_unlocked = [a['key'] for a in res1.json()['achievements_unlocked']]

        # Second assess
        client.post("/api/learning/start", json={"concept_id": "dup_2"})
        res2 = client.post("/api/learning/assess", json={
            "concept_id": "dup_2",
            "concept_name": "Dup 2",
            "score": 80,
            "mastered": False,
        })
        second_unlocked = [a['key'] for a in res2.json()['achievements_unlocked']]

        # First_light and first_assessment should NOT appear again
        for key in first_unlocked:
            assert key not in second_unlocked, f"{key} should not be re-unlocked"

    def test_review_triggers_achievements(self):
        """Submitting a review should return achievements_unlocked field."""
        # First need to create a concept with FSRS state
        res = client.post("/api/learning/review", json={
            "concept_id": "review_ach_1",
            "rating": 3,
        })
        assert res.status_code == 200
        data = res.json()
        assert "achievements_unlocked" in data
        unlocked_keys = [a['key'] for a in data['achievements_unlocked']]
        assert 'first_review' in unlocked_keys

    def test_recent_after_assess(self):
        """After assess triggers achievements, /achievements/recent should show unseen."""
        client.post("/api/learning/start", json={"concept_id": "recent_1"})
        client.post("/api/learning/assess", json={
            "concept_id": "recent_1",
            "concept_name": "Recent Test",
            "score": 90,
            "mastered": True,
        })

        res = client.get("/api/learning/achievements/recent")
        assert res.status_code == 200
        data = res.json()
        assert data["unseen_count"] > 0
        # Should include first_light and first_assessment at minimum
        keys = [a['key'] for a in data['achievements']]
        assert 'first_light' in keys or 'first_assessment' in keys

    def test_mark_seen_clears_recent(self):
        """After marking achievements as seen, they should not appear in recent."""
        client.post("/api/learning/start", json={"concept_id": "seen_1"})
        client.post("/api/learning/assess", json={
            "concept_id": "seen_1",
            "concept_name": "Seen Test",
            "score": 85,
            "mastered": True,
        })

        # Get unseen
        recent = client.get("/api/learning/achievements/recent").json()
        unseen_keys = [a['key'] for a in recent['achievements']]
        assert len(unseen_keys) > 0

        # Mark all as seen
        client.post("/api/learning/achievements/seen", json={"keys": unseen_keys})

        # Now recent should be empty
        recent2 = client.get("/api/learning/achievements/recent").json()
        assert recent2["unseen_count"] == 0

    def test_achievements_list_shows_unlocked_status(self):
        """GET /achievements should reflect unlocked status after assess."""
        client.post("/api/learning/start", json={"concept_id": "list_1"})
        client.post("/api/learning/assess", json={
            "concept_id": "list_1",
            "concept_name": "List Test",
            "score": 85,
            "mastered": True,
        })

        res = client.get("/api/learning/achievements")
        data = res.json()
        assert data["unlocked_count"] > 0

        first_light = next((a for a in data['achievements'] if a['key'] == 'first_light'), None)
        assert first_light is not None
        assert first_light['unlocked'] is True
        assert first_light['progress'] == 100.0
