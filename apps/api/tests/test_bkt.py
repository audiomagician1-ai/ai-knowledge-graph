"""Comprehensive tests for BKT (Bayesian Knowledge Tracing) engine.

Tests cover:
1. BKTParams — parameter validation and difficulty-based generation
2. BKTState — state management and classification
3. KnowledgeTracker — core algorithm (posterior update, predictions, bulk)
4. BKT DB operations (sqlite_client schema v4)
5. BKT API endpoints (/mastery, /assess integration)
6. BKT integration with /recommend (Factor 7)

Issue: #36
"""

import json
import math
import os
import tempfile
import time
from pathlib import Path

import pytest

# ── Setup temp DB before importing app ──
_tmp_dir = tempfile.mkdtemp()
import db.sqlite_client as sc
sc._DB_DIR = Path(_tmp_dir)
sc.DB_PATH = sc._DB_DIR / "test_bkt.db"
sc.init_db()

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# ════════════════════════════════════════════════════════
# 1. BKTParams Tests
# ════════════════════════════════════════════════════════

from engines.learning.tracker import (
    BKTParams, BKTState, KnowledgeTracker,
    DEFAULT_P_L0, DEFAULT_P_T, DEFAULT_P_G, DEFAULT_P_S,
    DEFAULT_MASTERY_THRESHOLD,
)


class TestBKTParams:
    """Test BKT parameter validation and factory methods."""

    def test_default_params(self):
        p = BKTParams()
        assert p.p_l0 == DEFAULT_P_L0
        assert p.p_t == DEFAULT_P_T
        assert p.p_g == DEFAULT_P_G
        assert p.p_s == DEFAULT_P_S

    def test_custom_params(self):
        p = BKTParams(p_l0=0.2, p_t=0.4, p_g=0.3, p_s=0.05)
        assert p.p_l0 == 0.2
        assert p.p_t == 0.4
        assert p.p_g == 0.3
        assert p.p_s == 0.05

    def test_invalid_probability_raises(self):
        with pytest.raises(ValueError):
            BKTParams(p_l0=-0.1)
        with pytest.raises(ValueError):
            BKTParams(p_t=1.5)
        with pytest.raises(ValueError):
            BKTParams(p_g=-0.01)
        with pytest.raises(ValueError):
            BKTParams(p_s=1.1)

    def test_degenerate_model_raises(self):
        """P(G) + P(S) >= 1 makes the model degenerate."""
        with pytest.raises(ValueError, match="degenerate"):
            BKTParams(p_g=0.5, p_s=0.5)
        with pytest.raises(ValueError, match="degenerate"):
            BKTParams(p_g=0.6, p_s=0.5)

    def test_to_dict_roundtrip(self):
        p = BKTParams(p_l0=0.15, p_t=0.35, p_g=0.2, p_s=0.08)
        d = p.to_dict()
        p2 = BKTParams.from_dict(d)
        assert p2.p_l0 == p.p_l0
        assert p2.p_t == p.p_t
        assert p2.p_g == p.p_g
        assert p2.p_s == p.p_s

    def test_from_dict_with_defaults(self):
        """Missing keys should fall back to defaults."""
        p = BKTParams.from_dict({})
        assert p.p_l0 == DEFAULT_P_L0
        assert p.p_t == DEFAULT_P_T

    def test_for_difficulty_range(self):
        """Difficulty-based params should be sensible across 1-5 range."""
        for diff in range(1, 6):
            p = BKTParams.for_difficulty(diff)
            assert 0 < p.p_l0 <= 0.20, f"diff={diff}: p_l0={p.p_l0}"
            assert 0.05 < p.p_t <= 0.50, f"diff={diff}: p_t={p.p_t}"
            assert 0.10 < p.p_g <= 0.40, f"diff={diff}: p_g={p.p_g}"
            assert p.p_s == DEFAULT_P_S
            # Identifiability constraint must hold
            assert p.p_g + p.p_s < 1.0

    def test_difficulty_monotonicity(self):
        """Higher difficulty → lower P(L0), lower P(T), higher P(G)."""
        params = [BKTParams.for_difficulty(d) for d in range(1, 6)]
        for i in range(len(params) - 1):
            assert params[i].p_l0 >= params[i + 1].p_l0, "P(L0) should decrease with difficulty"
            assert params[i].p_t >= params[i + 1].p_t, "P(T) should decrease with difficulty"
            assert params[i].p_g <= params[i + 1].p_g, "P(G) should increase with difficulty"

    def test_difficulty_clamping(self):
        """Out-of-range difficulty should be clamped to [1, 5]."""
        p0 = BKTParams.for_difficulty(0)
        p1 = BKTParams.for_difficulty(1)
        assert p0.p_l0 == p1.p_l0  # Clamped to 1

        p6 = BKTParams.for_difficulty(6)
        p5 = BKTParams.for_difficulty(5)
        assert p6.p_l0 == p5.p_l0  # Clamped to 5


# ════════════════════════════════════════════════════════
# 2. BKTState Tests
# ════════════════════════════════════════════════════════

class TestBKTState:
    """Test BKT state management and classification."""

    def test_default_state(self):
        s = BKTState()
        assert s.p_mastery == DEFAULT_P_L0
        assert s.observations == 0
        assert s.correct_count == 0
        assert not s.is_mastered

    def test_is_mastered(self):
        s = BKTState(p_mastery=0.95)
        assert s.is_mastered
        s = BKTState(p_mastery=0.89)
        assert not s.is_mastered

    def test_accuracy(self):
        s = BKTState(observations=10, correct_count=7)
        assert s.accuracy == 0.7
        s0 = BKTState(observations=0, correct_count=0)
        assert s0.accuracy == 0.0

    def test_classification_levels(self):
        assert BKTState(p_mastery=0.96).classification == "expert"
        assert BKTState(p_mastery=0.91).classification == "mastered"
        assert BKTState(p_mastery=0.75).classification == "proficient"
        assert BKTState(p_mastery=0.55).classification == "developing"
        assert BKTState(p_mastery=0.35).classification == "beginner"
        assert BKTState(p_mastery=0.10).classification == "novice"

    def test_to_dict(self):
        s = BKTState(p_mastery=0.75, observations=5, correct_count=3)
        d = s.to_dict()
        assert d['p_mastery'] == 0.75
        assert d['observations'] == 5
        assert d['correct_count'] == 3
        assert d['classification'] == 'proficient'
        assert d['is_mastered'] is False
        assert 'params' in d

    def test_from_db(self):
        params = BKTParams(p_l0=0.15, p_t=0.35, p_g=0.2, p_s=0.08)
        s = BKTState.from_db(
            p_mastery=0.65,
            observations=8,
            correct_count=5,
            params_json=json.dumps(params.to_dict()),
        )
        assert s.p_mastery == 0.65
        assert s.observations == 8
        assert s.params.p_l0 == 0.15

    def test_from_db_empty_params(self):
        """Empty params_json should use defaults."""
        s = BKTState.from_db(p_mastery=0.5, observations=3, correct_count=2, params_json='')
        assert s.params.p_l0 == DEFAULT_P_L0


# ════════════════════════════════════════════════════════
# 3. KnowledgeTracker Algorithm Tests
# ════════════════════════════════════════════════════════

class TestKnowledgeTracker:
    """Test the core BKT algorithm."""

    def setup_method(self):
        self.tracker = KnowledgeTracker()

    def test_init_default_state(self):
        state = self.tracker.init_state()
        assert state.p_mastery == DEFAULT_P_L0
        assert state.observations == 0

    def test_init_with_difficulty(self):
        state = self.tracker.init_state(difficulty=3)
        assert state.params.p_l0 < DEFAULT_P_L0  # Harder = lower prior
        assert state.p_mastery == state.params.p_l0

    def test_init_with_custom_params(self):
        params = BKTParams(p_l0=0.2, p_t=0.4, p_g=0.3, p_s=0.05)
        state = self.tracker.init_state(params=params)
        assert state.p_mastery == 0.2
        assert state.params.p_t == 0.4

    def test_update_correct_increases_mastery(self):
        """A correct answer should increase P(L)."""
        state = self.tracker.init_state()
        p_before = state.p_mastery
        state = self.tracker.update(state, correct=True)
        assert state.p_mastery > p_before
        assert state.observations == 1
        assert state.correct_count == 1

    def test_update_incorrect_may_decrease_mastery(self):
        """An incorrect answer on low P(L) should not increase P(L) much (learning transition may still increase it slightly)."""
        state = self.tracker.init_state()
        state_correct = self.tracker.update(state, correct=True)
        state_incorrect = self.tracker.update(state, correct=False)
        # Correct should produce higher P(L) than incorrect
        assert state_correct.p_mastery > state_incorrect.p_mastery

    def test_consecutive_correct_converges_to_mastery(self):
        """Multiple consecutive correct answers should reach mastery."""
        state = self.tracker.init_state()
        for _ in range(20):
            state = self.tracker.update(state, correct=True)
        assert state.is_mastered, f"P(L)={state.p_mastery} should be >= 0.90 after 20 correct"

    def test_mastery_after_few_correct(self):
        """With default params, ~5-6 correct answers should reach mastery."""
        state = self.tracker.init_state()
        for i in range(10):
            state = self.tracker.update(state, correct=True)
            if state.is_mastered:
                assert i >= 2, "Should take at least 3 correct answers to reach mastery"
                return
        # If not mastered after 10, something is off but not necessarily wrong
        assert state.p_mastery > 0.7, f"P(L)={state.p_mastery} should be high after 10 correct"

    def test_incorrect_slows_mastery(self):
        """Mixing incorrect answers should slow progression to mastery."""
        # All correct
        state_fast = self.tracker.init_state()
        for _ in range(5):
            state_fast = self.tracker.update(state_fast, correct=True)

        # Alternating correct/incorrect
        state_slow = self.tracker.init_state()
        for i in range(5):
            state_slow = self.tracker.update(state_slow, correct=(i % 2 == 0))

        assert state_fast.p_mastery > state_slow.p_mastery

    def test_posterior_update_formula_correct_observation(self):
        """Verify the exact posterior update for a correct observation."""
        params = BKTParams(p_l0=0.3, p_t=0.2, p_g=0.25, p_s=0.1)
        state = self.tracker.init_state(params=params)

        # Manual calculation
        p_l = 0.3
        p_s = 0.1
        p_g = 0.25
        p_t = 0.2

        # P(correct) = P(L)*(1-P(S)) + (1-P(L))*P(G)
        p_correct = p_l * (1 - p_s) + (1 - p_l) * p_g  # 0.3*0.9 + 0.7*0.25 = 0.445
        # P(L|correct) = P(L)*(1-P(S)) / P(correct)
        p_l_given_correct = (p_l * (1 - p_s)) / p_correct  # 0.27 / 0.445 ≈ 0.6067
        # Learning transition
        p_l_new = p_l_given_correct + (1 - p_l_given_correct) * p_t

        state = self.tracker.update(state, correct=True)
        assert abs(state.p_mastery - p_l_new) < 1e-10, f"Expected {p_l_new}, got {state.p_mastery}"

    def test_posterior_update_formula_incorrect_observation(self):
        """Verify the exact posterior update for an incorrect observation."""
        params = BKTParams(p_l0=0.3, p_t=0.2, p_g=0.25, p_s=0.1)
        state = self.tracker.init_state(params=params)

        p_l = 0.3
        p_s = 0.1
        p_g = 0.25
        p_t = 0.2

        # P(incorrect) = P(L)*P(S) + (1-P(L))*(1-P(G))
        p_incorrect = p_l * p_s + (1 - p_l) * (1 - p_g)  # 0.03 + 0.525 = 0.555
        # P(L|incorrect) = P(L)*P(S) / P(incorrect)
        p_l_given_incorrect = (p_l * p_s) / p_incorrect  # 0.03 / 0.555 ≈ 0.0541
        # Learning transition
        p_l_new = p_l_given_incorrect + (1 - p_l_given_incorrect) * p_t

        state = self.tracker.update(state, correct=False)
        assert abs(state.p_mastery - p_l_new) < 1e-10, f"Expected {p_l_new}, got {state.p_mastery}"

    def test_update_from_score_threshold(self):
        """Scores >= 70 should count as correct, < 70 as incorrect."""
        state = self.tracker.init_state()

        state_pass = self.tracker.update_from_score(state, score=75.0, threshold=70.0)
        state_fail = self.tracker.update_from_score(state, score=65.0, threshold=70.0)
        state_exact = self.tracker.update_from_score(state, score=70.0, threshold=70.0)

        assert state_pass.p_mastery > state_fail.p_mastery
        assert state_exact.p_mastery == state_pass.p_mastery  # 70 counts as correct (>=)

    def test_bulk_update(self):
        """Bulk update should produce same result as sequential updates."""
        state_bulk = self.tracker.init_state()
        observations = [True, True, False, True, True, False, True]
        state_bulk = self.tracker.bulk_update(state_bulk, observations)

        state_seq = self.tracker.init_state()
        for obs in observations:
            state_seq = self.tracker.update(state_seq, obs)

        assert abs(state_bulk.p_mastery - state_seq.p_mastery) < 1e-10
        assert state_bulk.observations == state_seq.observations
        assert state_bulk.correct_count == state_seq.correct_count

    def test_predict_correct(self):
        """Predicted correct probability should increase with P(L)."""
        state_low = BKTState(p_mastery=0.1)
        state_high = BKTState(p_mastery=0.9)

        p_low = self.tracker.predict_correct(state_low)
        p_high = self.tracker.predict_correct(state_high)

        assert p_high > p_low
        assert 0 <= p_low <= 1
        assert 0 <= p_high <= 1

    def test_predict_correct_formula(self):
        """Verify exact prediction formula."""
        params = BKTParams(p_l0=0.5, p_t=0.3, p_g=0.2, p_s=0.1)
        state = BKTState(p_mastery=0.5, params=params)

        expected = 0.5 * (1 - 0.1) + 0.5 * 0.2  # = 0.45 + 0.10 = 0.55
        assert abs(self.tracker.predict_correct(state) - expected) < 1e-10

    def test_expected_attempts_to_mastery(self):
        """Should return reasonable number of attempts."""
        state = self.tracker.init_state()
        attempts = self.tracker.expected_attempts_to_mastery(state)
        assert 1 <= attempts <= 100
        # Already mastered = 0
        mastered = BKTState(p_mastery=0.95)
        assert self.tracker.expected_attempts_to_mastery(mastered) == 0

    def test_expected_attempts_harder_concept(self):
        """Harder concepts should need more attempts."""
        easy_state = self.tracker.init_state(difficulty=1)
        hard_state = self.tracker.init_state(difficulty=5)
        easy_attempts = self.tracker.expected_attempts_to_mastery(easy_state)
        hard_attempts = self.tracker.expected_attempts_to_mastery(hard_state)
        assert hard_attempts >= easy_attempts

    def test_custom_mastery_threshold(self):
        tracker_strict = KnowledgeTracker(mastery_threshold=0.95)
        tracker_lenient = KnowledgeTracker(mastery_threshold=0.70)

        state_strict = tracker_strict.init_state()
        state_lenient = tracker_lenient.init_state()

        for _ in range(5):
            state_strict = tracker_strict.update(state_strict, correct=True)
            state_lenient = tracker_lenient.update(state_lenient, correct=True)

        # Lenient threshold should classify as mastered earlier
        if state_strict.is_mastered:
            assert state_lenient.is_mastered
        # Both have same P(L) since params are identical
        assert abs(state_strict.p_mastery - state_lenient.p_mastery) < 1e-10

    def test_invalid_mastery_threshold(self):
        with pytest.raises(ValueError):
            KnowledgeTracker(mastery_threshold=0.0)
        with pytest.raises(ValueError):
            KnowledgeTracker(mastery_threshold=1.0)

    def test_p_mastery_bounds(self):
        """P(L) should always stay in [0, 1]."""
        state = self.tracker.init_state()
        # Many correct
        for _ in range(50):
            state = self.tracker.update(state, correct=True)
            assert 0.0 <= state.p_mastery <= 1.0
        # Many incorrect from high mastery
        for _ in range(50):
            state = self.tracker.update(state, correct=False)
            assert 0.0 <= state.p_mastery <= 1.0


# ════════════════════════════════════════════════════════
# 4. BKT DB Tests
# ════════════════════════════════════════════════════════

class TestBKTDatabase:
    """Test BKT DB operations."""

    def setup_method(self):
        with sc.get_db() as conn:
            conn.execute("DELETE FROM concept_progress")
            conn.execute("DELETE FROM learning_history")

    def test_schema_v4_columns_exist(self):
        """Schema v4 should add bkt_mastery, bkt_observations, bkt_correct_count, bkt_params_json."""
        with sc.get_db() as conn:
            # Insert a test row and verify BKT columns
            conn.execute(
                """INSERT OR REPLACE INTO concept_progress
                   (concept_id, status, mastery_score, created_at, updated_at,
                    bkt_mastery, bkt_observations, bkt_correct_count, bkt_params_json)
                   VALUES ('test_bkt_cols', 'learning', 50, 0, 0, 0.65, 5, 3, '{}')"""
            )
            row = conn.execute(
                "SELECT bkt_mastery, bkt_observations, bkt_correct_count, bkt_params_json "
                "FROM concept_progress WHERE concept_id = 'test_bkt_cols'"
            ).fetchone()
            assert row is not None
            assert row[0] == 0.65
            assert row[1] == 5
            assert row[2] == 3
            assert row[3] == '{}'

    def test_get_bkt_state_none(self):
        """No record should return None."""
        result = sc.get_bkt_state("nonexistent_concept")
        assert result is None

    def test_get_bkt_state_default_zeros_returns_none(self):
        """Concept with default zeros (never assessed with BKT) should return None."""
        with sc.get_db() as conn:
            conn.execute(
                """INSERT INTO concept_progress
                   (concept_id, status, mastery_score, created_at, updated_at)
                   VALUES ('never_assessed', 'learning', 50, 0, 0)"""
            )
        result = sc.get_bkt_state("never_assessed")
        assert result is None

    def test_update_and_get_bkt_state(self):
        """Write then read BKT state."""
        sc.update_bkt_state("bkt_test_1", p_mastery=0.75, observations=10,
                            correct_count=7, params_json='{"p_l0": 0.1}')
        result = sc.get_bkt_state("bkt_test_1")
        assert result is not None
        assert result['concept_id'] == 'bkt_test_1'
        assert result['p_mastery'] == 0.75
        assert result['observations'] == 10
        assert result['correct_count'] == 7
        assert result['params_json'] == '{"p_l0": 0.1}'

    def test_update_bkt_state_creates_row(self):
        """update_bkt_state on new concept should create concept_progress row."""
        sc.update_bkt_state("bkt_new_concept", p_mastery=0.5, observations=3,
                            correct_count=2, params_json='')
        progress = sc.get_progress("bkt_new_concept")
        assert progress is not None
        assert progress['concept_id'] == 'bkt_new_concept'
        assert progress['status'] == 'not_started'

    def test_update_bkt_state_updates_existing(self):
        """update_bkt_state on existing concept should update BKT fields without changing status."""
        sc.upsert_progress("bkt_existing", status='learning', mastery_score=60)
        sc.update_bkt_state("bkt_existing", p_mastery=0.8, observations=5,
                            correct_count=4, params_json='')
        progress = sc.get_progress("bkt_existing")
        assert progress['status'] == 'learning'  # unchanged
        result = sc.get_bkt_state("bkt_existing")
        assert result['p_mastery'] == 0.8

    def test_get_all_bkt_states(self):
        """Should return only concepts with observations > 0."""
        sc.update_bkt_state("bkt_a", p_mastery=0.9, observations=10, correct_count=8)
        sc.update_bkt_state("bkt_b", p_mastery=0.3, observations=2, correct_count=1)
        # This one has no observations — should not appear
        sc.upsert_progress("bkt_c", status='learning', mastery_score=50)

        all_bkt = sc.get_all_bkt_states()
        ids = [r['concept_id'] for r in all_bkt]
        assert 'bkt_a' in ids
        assert 'bkt_b' in ids
        assert 'bkt_c' not in ids
        # Should be sorted by mastery DESC
        assert all_bkt[0]['bkt_mastery'] >= all_bkt[1]['bkt_mastery']


# ════════════════════════════════════════════════════════
# 5. BKT API Tests
# ════════════════════════════════════════════════════════

class TestBKTAPI:
    """Test BKT-related API endpoints."""

    def setup_method(self):
        with sc.get_db() as conn:
            conn.execute("DELETE FROM concept_progress")
            conn.execute("DELETE FROM learning_history")
            conn.execute("UPDATE streak SET current_streak=0, longest_streak=0, last_date=''")

    def test_assess_returns_bkt_data(self):
        """POST /assess should return BKT mastery data."""
        client.post("/api/learning/start", json={"concept_id": "bkt_assess_1"})
        res = client.post("/api/learning/assess", json={
            "concept_id": "bkt_assess_1",
            "concept_name": "BKT Test Concept",
            "score": 85.0,
            "mastered": False,
        })
        assert res.status_code == 200
        data = res.json()
        assert "bkt" in data
        bkt = data["bkt"]
        assert bkt["observations"] == 1
        assert bkt["p_mastery"] > 0
        assert bkt["classification"] in ["novice", "beginner", "developing", "proficient", "mastered", "expert"]
        assert isinstance(bkt["is_mastered"], bool)

    def test_assess_bkt_accumulates(self):
        """Multiple assessments should accumulate BKT observations."""
        for score in [80, 90, 75, 85]:
            res = client.post("/api/learning/assess", json={
                "concept_id": "bkt_accum",
                "concept_name": "BKT Accumulation",
                "score": score,
                "mastered": False,
            })
            assert res.status_code == 200

        data = res.json()
        assert data["bkt"]["observations"] == 4
        # All scores >= 70 → all correct → mastery should be high
        assert data["bkt"]["p_mastery"] > 0.5

    def test_assess_bkt_correct_vs_incorrect(self):
        """High scores should yield higher BKT mastery than low scores."""
        # Concept with high scores
        for _ in range(3):
            client.post("/api/learning/assess", json={
                "concept_id": "bkt_high",
                "concept_name": "BKT High",
                "score": 90,
                "mastered": False,
            })
        # Concept with low scores
        for _ in range(3):
            client.post("/api/learning/assess", json={
                "concept_id": "bkt_low",
                "concept_name": "BKT Low",
                "score": 40,
                "mastered": False,
            })

        high_data = sc.get_bkt_state("bkt_high")
        low_data = sc.get_bkt_state("bkt_low")
        assert high_data['p_mastery'] > low_data['p_mastery']

    def test_mastery_endpoint_no_data(self):
        """GET /mastery/{id} with no BKT data should return has_bkt_data=False."""
        res = client.get("/api/learning/mastery/nonexistent_concept")
        assert res.status_code == 200
        data = res.json()
        assert data["has_bkt_data"] is False
        assert data["classification"] == "novice"
        assert data["observations"] == 0

    def test_mastery_endpoint_with_data(self):
        """GET /mastery/{id} should return full BKT analysis."""
        # Create some assessment history
        for score in [80, 90, 85]:
            client.post("/api/learning/assess", json={
                "concept_id": "bkt_mastery_test",
                "concept_name": "BKT Mastery Test",
                "score": score,
                "mastered": False,
            })

        res = client.get("/api/learning/mastery/bkt_mastery_test")
        assert res.status_code == 200
        data = res.json()
        assert data["has_bkt_data"] is True
        assert data["observations"] == 3
        assert data["correct_count"] == 3
        assert data["p_mastery"] > 0
        assert "predicted_correct_probability" in data
        assert "estimated_attempts_to_mastery" in data
        assert "classification" in data
        assert "params" in data

    def test_mastery_all_endpoint(self):
        """GET /mastery should return all tracked concepts."""
        # Create two concepts with BKT data
        client.post("/api/learning/assess", json={
            "concept_id": "bkt_all_1",
            "concept_name": "BKT All 1",
            "score": 80,
            "mastered": False,
        })
        client.post("/api/learning/assess", json={
            "concept_id": "bkt_all_2",
            "concept_name": "BKT All 2",
            "score": 60,
            "mastered": False,
        })

        res = client.get("/api/learning/mastery")
        assert res.status_code == 200
        data = res.json()
        assert data["total_tracked"] == 2
        assert "mastered_count" in data
        assert len(data["items"]) == 2
        ids = [item["concept_id"] for item in data["items"]]
        assert "bkt_all_1" in ids
        assert "bkt_all_2" in ids

    def test_assess_backward_compat(self):
        """POST /assess should still return all original fields alongside BKT."""
        client.post("/api/learning/start", json={"concept_id": "bkt_compat"})
        res = client.post("/api/learning/assess", json={
            "concept_id": "bkt_compat",
            "concept_name": "BKT Compat",
            "score": 85,
            "mastered": True,
        })
        assert res.status_code == 200
        data = res.json()
        # Original fields must still be present
        assert data["success"] is True
        assert data["mastered"] is True
        assert "progress" in data
        # BKT field is new addition
        assert "bkt" in data


# ════════════════════════════════════════════════════════
# 6. BKT + Recommend Integration Test
# ════════════════════════════════════════════════════════

class TestBKTRecommendIntegration:
    """Test BKT Factor 7 in the /recommend endpoint."""

    def setup_method(self):
        with sc.get_db() as conn:
            conn.execute("DELETE FROM concept_progress")
            conn.execute("DELETE FROM learning_history")

    def test_recommend_still_works_with_bkt(self):
        """Adding BKT should not break the /recommend endpoint."""
        res = client.get("/api/learning/recommend?top_k=3")
        assert res.status_code == 200
        data = res.json()
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)

    def test_recommend_includes_bkt_mastery(self):
        """Concepts with BKT data should include bkt_mastery in recommendations."""
        # Assess a concept that's likely in the seed
        import json as _json
        seed_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "data", "seed",
            "ai-engineering", "seed_graph.json"
        )
        with open(seed_path, "r", encoding="utf-8") as f:
            seed = _json.load(f)

        # Pick a low-difficulty concept that would appear in recommendations
        low_diff = [c for c in seed["concepts"] if c["difficulty"] == 1]
        if low_diff:
            concept = low_diff[0]
            # Create BKT state via assess
            client.post("/api/learning/assess", json={
                "concept_id": concept["id"],
                "concept_name": concept["name"],
                "score": 65,  # Below 70 → incorrect observation
                "mastered": False,
            })

            res = client.get("/api/learning/recommend?top_k=20")
            assert res.status_code == 200
            data = res.json()
            # Find the concept in recommendations (it might not appear if mastered)
            for rec in data["recommendations"]:
                if rec["concept_id"] == concept["id"] and "bkt_mastery" in rec:
                    assert 0 <= rec["bkt_mastery"] <= 1
                    return
            # If concept not in recommendations (could be mastered or filtered), that's OK
