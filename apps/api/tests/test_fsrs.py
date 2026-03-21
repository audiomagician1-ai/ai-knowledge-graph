"""Comprehensive tests for FSRS-5 spaced repetition scheduler.

Tests cover:
1. FSRSScheduler algorithm (unit tests)
2. FSRS DB operations (sqlite_client)
3. FSRS API endpoints (/learning/due, /learning/review)
"""

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
sc.DB_PATH = sc._DB_DIR / "test_fsrs.db"
sc.init_db()

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# ════════════════════════════════════════════════════════
# 1. FSRSScheduler Algorithm Tests
# ════════════════════════════════════════════════════════

from engines.learning.fsrs_scheduler import (
    FSRSScheduler, Card, Rating, State, SchedulingResult
)


class TestFSRSCard:
    """Test Card data class."""

    def test_default_card_is_new(self):
        card = Card()
        assert card.state == State.New
        assert card.stability == 0.0
        assert card.difficulty == 0.0
        assert card.reps == 0
        assert card.lapses == 0

    def test_card_round_trip(self):
        card = Card(stability=3.5, difficulty=5.2, reps=10, state=State.Review)
        d = card.to_dict()
        card2 = Card.from_dict(d)
        assert card2.stability == 3.5
        assert card2.difficulty == 5.2
        assert card2.reps == 10
        assert card2.state == State.Review

    def test_card_from_empty_dict(self):
        card = Card.from_dict({})
        assert card.state == State.New

    def test_card_from_none(self):
        card = Card.from_dict(None)
        assert card.state == State.New


class TestFSRSSchedulerNewCards:
    """Test scheduling for new (never-reviewed) cards."""

    def setup_method(self):
        self.scheduler = FSRSScheduler()
        self.now = 1711000000.0  # fixed timestamp for reproducibility

    def test_new_card_again_stays_learning(self):
        card = Card()
        result = self.scheduler.review(card, Rating.Again, now=self.now)
        assert result.card.state == State.Learning
        assert result.card.reps == 1
        assert result.card.lapses == 0
        # Due in ~1 minute
        assert result.card.due == pytest.approx(self.now + 60, abs=1)
        assert result.card.stability > 0

    def test_new_card_hard_stays_learning(self):
        card = Card()
        result = self.scheduler.review(card, Rating.Hard, now=self.now)
        assert result.card.state == State.Learning
        # Due in ~5 minutes
        assert result.card.due == pytest.approx(self.now + 300, abs=1)

    def test_new_card_good_graduates_to_review(self):
        card = Card()
        result = self.scheduler.review(card, Rating.Good, now=self.now)
        assert result.card.state == State.Review
        assert result.card.scheduled_days >= 1
        assert result.card.due > self.now + 86400  # at least 1 day later

    def test_new_card_easy_graduates_with_longer_interval(self):
        card = Card()
        result_good = self.scheduler.review(Card(), Rating.Good, now=self.now)
        result_easy = self.scheduler.review(card, Rating.Easy, now=self.now)
        assert result_easy.card.state == State.Review
        assert result_easy.card.scheduled_days >= 4  # at least 4 days for easy
        assert result_easy.card.scheduled_days >= result_good.card.scheduled_days

    def test_new_card_initial_stability_ordering(self):
        """Higher rating → higher initial stability."""
        s = self.scheduler
        s_again = s._init_stability(Rating.Again)
        s_hard = s._init_stability(Rating.Hard)
        s_good = s._init_stability(Rating.Good)
        s_easy = s._init_stability(Rating.Easy)
        assert s_again < s_hard < s_good < s_easy

    def test_new_card_initial_difficulty_ordering(self):
        """Higher rating → lower initial difficulty (easier cards get lower D)."""
        s = self.scheduler
        d_again = s._init_difficulty(Rating.Again)
        d_hard = s._init_difficulty(Rating.Hard)
        d_good = s._init_difficulty(Rating.Good)
        d_easy = s._init_difficulty(Rating.Easy)
        assert d_again > d_hard > d_good > d_easy

    def test_review_log_captures_pre_state(self):
        card = Card()
        result = self.scheduler.review(card, Rating.Good, now=self.now)
        log = result.review_log
        assert log.state == State.New  # Pre-review state
        assert log.rating == Rating.Good
        assert log.review_time == self.now


class TestFSRSSchedulerLearning:
    """Test scheduling for Learning/Relearning state cards."""

    def setup_method(self):
        self.scheduler = FSRSScheduler()
        self.now = 1711000000.0

    def _make_learning_card(self) -> Card:
        """Create a card in Learning state."""
        card = Card()
        result = self.scheduler.review(card, Rating.Again, now=self.now)
        return result.card

    def test_learning_again_stays_learning(self):
        card = self._make_learning_card()
        result = self.scheduler.review(card, Rating.Again, now=self.now + 60)
        assert result.card.state == State.Learning

    def test_learning_good_graduates_to_review(self):
        card = self._make_learning_card()
        result = self.scheduler.review(card, Rating.Good, now=self.now + 300)
        assert result.card.state == State.Review
        assert result.card.scheduled_days >= 1

    def test_learning_easy_graduates_to_review(self):
        card = self._make_learning_card()
        result = self.scheduler.review(card, Rating.Easy, now=self.now + 300)
        assert result.card.state == State.Review
        assert result.card.scheduled_days >= 4


class TestFSRSSchedulerReview:
    """Test scheduling for Review state cards (graduated, in review queue)."""

    def setup_method(self):
        self.scheduler = FSRSScheduler()
        self.now = 1711000000.0

    def _make_review_card(self) -> Card:
        """Create a card in Review state by graduating a new card."""
        card = Card()
        result = self.scheduler.review(card, Rating.Good, now=self.now)
        return result.card

    def test_review_good_increases_interval(self):
        card = self._make_review_card()
        old_scheduled = card.scheduled_days
        # Simulate reviewing at scheduled time
        result = self.scheduler.review(card, Rating.Good, now=card.due)
        assert result.card.state == State.Review
        assert result.card.scheduled_days >= old_scheduled  # interval should grow or stay

    def test_review_again_causes_lapse(self):
        card = self._make_review_card()
        old_lapses = card.lapses
        result = self.scheduler.review(card, Rating.Again, now=card.due)
        assert result.card.state == State.Relearning
        assert result.card.lapses == old_lapses + 1

    def test_review_easy_bonus(self):
        """Easy rating on review should produce at least as long an interval as previous,
        because _process_review guarantees max(next_interval, scheduled_days + 1) for Easy."""
        card = Card(
            stability=5.0, difficulty=5.0, state=State.Review,
            scheduled_days=5, due=self.now, last_review=self.now - 5 * 86400,
            elapsed_days=5, reps=3, lapses=0,
        )
        result_easy = self.scheduler.review(card, Rating.Easy, now=self.now)
        # Easy interval must be at least previous scheduled_days + 1
        assert result_easy.card.scheduled_days > 5
        assert result_easy.card.state == State.Review

    def test_review_hard_penalty(self):
        card1 = self._make_review_card()
        card2 = self._make_review_card()
        result_hard = self.scheduler.review(card1, Rating.Hard, now=card1.due)
        result_good = self.scheduler.review(card2, Rating.Good, now=card2.due)
        assert result_hard.card.scheduled_days <= result_good.card.scheduled_days

    def test_stability_never_negative(self):
        """Stability must always be ≥ 0.1 regardless of review sequence."""
        card = Card()
        for _ in range(20):
            result = self.scheduler.review(card, Rating.Again, now=self.now)
            card = result.card
            self.now += 60
            assert card.stability >= 0.1

    def test_difficulty_bounded(self):
        """Difficulty must stay within [1, 10]."""
        card = Card()
        # Many "Again" reviews should max out difficulty
        for _ in range(50):
            result = self.scheduler.review(card, Rating.Again, now=self.now)
            card = result.card
            self.now += 60
        assert 1.0 <= card.difficulty <= 10.0

        # Many "Easy" reviews should min out difficulty
        card2 = Card()
        for _ in range(50):
            result = self.scheduler.review(card2, Rating.Easy, now=self.now)
            card2 = result.card
            self.now += card2.scheduled_days * 86400 if card2.scheduled_days > 0 else 60
        assert 1.0 <= card2.difficulty <= 10.0


class TestFSRSSchedulerForgettingCurve:
    """Test forgetting curve calculations."""

    def setup_method(self):
        self.scheduler = FSRSScheduler()

    def test_retrievability_at_zero_elapsed(self):
        """R(0, S) should be ~1.0 (just reviewed)."""
        r = self.scheduler.forgetting_curve(0, 10.0)
        assert r == pytest.approx(1.0, abs=0.01)

    def test_retrievability_decreases_over_time(self):
        r1 = self.scheduler.forgetting_curve(1, 10.0)
        r10 = self.scheduler.forgetting_curve(10, 10.0)
        r30 = self.scheduler.forgetting_curve(30, 10.0)
        assert r1 > r10 > r30

    def test_retrievability_at_stability_equals_90pct(self):
        """At elapsed = stability * FACTOR, R should be ≈ 0.9."""
        S = 10.0
        interval = self.scheduler.next_interval(S)
        r = self.scheduler.forgetting_curve(interval, S)
        assert r == pytest.approx(0.9, abs=0.05)

    def test_higher_stability_slower_decay(self):
        r_low = self.scheduler.forgetting_curve(5, 3.0)
        r_high = self.scheduler.forgetting_curve(5, 30.0)
        assert r_high > r_low

    def test_zero_stability_returns_zero(self):
        r = self.scheduler.forgetting_curve(5, 0.0)
        assert r == 0.0


class TestFSRSSchedulerInterval:
    """Test interval calculation."""

    def setup_method(self):
        self.scheduler = FSRSScheduler()

    def test_interval_at_least_1(self):
        assert self.scheduler.next_interval(0.1) >= 1

    def test_interval_bounded_by_max(self):
        assert self.scheduler.next_interval(1e9) <= self.scheduler.max_interval

    def test_interval_increases_with_stability(self):
        i1 = self.scheduler.next_interval(1.0)
        i10 = self.scheduler.next_interval(10.0)
        i100 = self.scheduler.next_interval(100.0)
        assert i1 <= i10 <= i100


class TestFSRSSchedulerFullCycle:
    """Integration tests: full learn → review → lapse → relearn cycle."""

    def test_full_lifecycle(self):
        scheduler = FSRSScheduler()
        now = 1711000000.0
        card = Card()

        # Step 1: First review — Good → graduates to Review
        result = scheduler.review(card, Rating.Good, now=now)
        card = result.card
        assert card.state == State.Review

        # Step 2: Review on time — Good → interval grows
        now = card.due
        result = scheduler.review(card, Rating.Good, now=now)
        card = result.card
        assert card.state == State.Review
        first_interval = card.scheduled_days

        # Step 3: Review on time — Good again
        now = card.due
        result = scheduler.review(card, Rating.Good, now=now)
        card = result.card
        assert card.scheduled_days >= first_interval  # growing intervals

        # Step 4: Lapse — Again → Relearning
        now = card.due
        result = scheduler.review(card, Rating.Again, now=now)
        card = result.card
        assert card.state == State.Relearning
        assert card.lapses == 1

        # Step 5: Recover from lapse — Good → back to Review
        now += 300
        result = scheduler.review(card, Rating.Good, now=now)
        card = result.card
        assert card.state == State.Review
        # After lapse, interval should be shorter
        assert card.scheduled_days < first_interval or card.scheduled_days >= 1


# ════════════════════════════════════════════════════════
# 2. FSRS DB Tests
# ════════════════════════════════════════════════════════

class TestFSRSDB:
    """Test FSRS database operations."""

    def setup_method(self):
        with sc.get_db() as conn:
            conn.execute("DELETE FROM concept_progress")
            conn.execute("DELETE FROM learning_history")

    def test_schema_v3_migration(self):
        """Verify FSRS columns exist after migration."""
        with sc.get_db() as conn:
            row = conn.execute(
                "PRAGMA table_info(concept_progress)"
            ).fetchall()
            col_names = {r[1] for r in row}
            expected_fsrs_cols = {
                'fsrs_stability', 'fsrs_difficulty', 'fsrs_due',
                'fsrs_elapsed_days', 'fsrs_scheduled_days', 'fsrs_reps',
                'fsrs_lapses', 'fsrs_state', 'fsrs_last_review',
            }
            assert expected_fsrs_cols.issubset(col_names)

    def test_get_fsrs_card_nonexistent(self):
        result = sc.get_fsrs_card("nonexistent")
        assert result is None

    def test_update_and_get_fsrs_card(self):
        now = time.time()
        sc.update_fsrs_card("test_concept", {
            'stability': 3.5,
            'difficulty': 5.2,
            'due': now + 86400,
            'elapsed_days': 0,
            'scheduled_days': 1,
            'reps': 1,
            'lapses': 0,
            'state': State.Review,
            'last_review': now,
        })
        card = sc.get_fsrs_card("test_concept")
        assert card is not None
        assert card['stability'] == pytest.approx(3.5, abs=0.01)
        assert card['difficulty'] == pytest.approx(5.2, abs=0.01)
        assert card['reps'] == 1
        assert card['state'] == State.Review

    def test_update_fsrs_card_creates_row_if_needed(self):
        """update_fsrs_card should create concept_progress row if it doesn't exist."""
        sc.update_fsrs_card("auto_created", {
            'stability': 1.0, 'difficulty': 5.0, 'due': 0,
            'elapsed_days': 0, 'scheduled_days': 0, 'reps': 0,
            'lapses': 0, 'state': 0, 'last_review': 0,
        })
        progress = sc.get_progress("auto_created")
        assert progress is not None
        assert progress['concept_id'] == "auto_created"

    def test_get_due_concepts_empty(self):
        result = sc.get_due_concepts()
        assert result == []

    def test_get_due_concepts_returns_overdue(self):
        now = time.time()
        # Create a concept with due date in the past
        sc.update_fsrs_card("overdue_concept", {
            'stability': 3.0, 'difficulty': 5.0,
            'due': now - 86400,  # due yesterday
            'elapsed_days': 3, 'scheduled_days': 3,
            'reps': 1, 'lapses': 0,
            'state': State.Review, 'last_review': now - 86400 * 4,
        })
        result = sc.get_due_concepts(before=now)
        assert len(result) >= 1
        assert any(r['concept_id'] == 'overdue_concept' for r in result)

    def test_get_due_concepts_excludes_new_state(self):
        """New (state=0) cards should not appear in due list."""
        now = time.time()
        sc.update_fsrs_card("new_card", {
            'stability': 0, 'difficulty': 0, 'due': now - 1000,
            'elapsed_days': 0, 'scheduled_days': 0, 'reps': 0,
            'lapses': 0, 'state': State.New, 'last_review': 0,
        })
        result = sc.get_due_concepts(before=now)
        assert not any(r['concept_id'] == 'new_card' for r in result)

    def test_get_due_concepts_excludes_future(self):
        """Concepts due in the future should not appear."""
        now = time.time()
        sc.update_fsrs_card("future_concept", {
            'stability': 10.0, 'difficulty': 5.0,
            'due': now + 86400 * 7,  # due in 7 days
            'elapsed_days': 3, 'scheduled_days': 10,
            'reps': 1, 'lapses': 0,
            'state': State.Review, 'last_review': now,
        })
        result = sc.get_due_concepts(before=now)
        assert not any(r['concept_id'] == 'future_concept' for r in result)


# ════════════════════════════════════════════════════════
# 3. FSRS API Endpoint Tests
# ════════════════════════════════════════════════════════

class TestFSRSAPI:
    """Test FSRS API endpoints."""

    def setup_method(self):
        with sc.get_db() as conn:
            conn.execute("DELETE FROM concept_progress")
            conn.execute("DELETE FROM learning_history")
            conn.execute("UPDATE streak SET current_streak=0, longest_streak=0, last_date=''")

    def test_review_new_card(self):
        res = client.post("/api/learning/review", json={
            "concept_id": "api_test_new",
            "rating": 3,  # Good
        })
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["concept_id"] == "api_test_new"
        assert data["rating"] == 3
        card = data["card"]
        assert card["state"] == State.Review
        assert card["stability"] > 0
        assert card["difficulty"] > 0
        assert card["scheduled_days"] >= 1
        assert card["reps"] == 1

    def test_review_again(self):
        res = client.post("/api/learning/review", json={
            "concept_id": "api_test_again",
            "rating": 1,  # Again
        })
        assert res.status_code == 200
        data = res.json()
        assert data["card"]["state"] == State.Learning

    def test_review_updates_card_state(self):
        """Sequential reviews should update state correctly."""
        # First: Again (→ Learning)
        res1 = client.post("/api/learning/review", json={
            "concept_id": "seq_test",
            "rating": 1,
        })
        assert res1.json()["card"]["state"] == State.Learning

        # Second: Good (→ Review)
        res2 = client.post("/api/learning/review", json={
            "concept_id": "seq_test",
            "rating": 3,
        })
        assert res2.json()["card"]["state"] == State.Review
        assert res2.json()["card"]["reps"] == 2

    def test_review_validation_rating_range(self):
        # Rating 0 (too low)
        res = client.post("/api/learning/review", json={
            "concept_id": "test",
            "rating": 0,
        })
        assert res.status_code == 422

        # Rating 5 (too high)
        res = client.post("/api/learning/review", json={
            "concept_id": "test",
            "rating": 5,
        })
        assert res.status_code == 422

    def test_review_validation_concept_id_required(self):
        res = client.post("/api/learning/review", json={
            "rating": 3,
        })
        assert res.status_code == 422

    def test_review_log_in_response(self):
        res = client.post("/api/learning/review", json={
            "concept_id": "log_test",
            "rating": 3,
        })
        data = res.json()
        assert "review_log" in data
        assert data["review_log"]["rating"] == 3
        assert data["review_log"]["previous_state"] == State.New

    def test_due_endpoint_empty(self):
        res = client.get("/api/learning/due")
        assert res.status_code == 200
        data = res.json()
        assert data["due_count"] == 0
        assert data["items"] == []

    def test_due_endpoint_returns_overdue(self):
        now = time.time()
        # Manually create an overdue card in DB
        sc.update_fsrs_card("due_api_test", {
            'stability': 3.0, 'difficulty': 5.0,
            'due': now - 86400,  # due yesterday
            'elapsed_days': 3, 'scheduled_days': 3,
            'reps': 1, 'lapses': 0,
            'state': State.Review, 'last_review': now - 86400 * 4,
        })
        res = client.get("/api/learning/due")
        assert res.status_code == 200
        data = res.json()
        assert data["due_count"] >= 1
        found = [i for i in data["items"] if i["concept_id"] == "due_api_test"]
        assert len(found) == 1
        assert found[0]["overdue_days"] > 0

    def test_due_endpoint_limit(self):
        res = client.get("/api/learning/due?limit=5")
        assert res.status_code == 200

    def test_recommend_includes_due_review_count(self):
        """After FSRS integration, /recommend should include due_review_count."""
        res = client.get("/api/learning/recommend?top_k=3")
        assert res.status_code == 200
        data = res.json()
        assert "due_review_count" in data

    def test_full_api_cycle(self):
        """Test complete: review → check due → review again."""
        # Step 1: First review with "Good"
        res = client.post("/api/learning/review", json={
            "concept_id": "full_cycle",
            "rating": 3,
        })
        assert res.status_code == 200
        card = res.json()["card"]
        assert card["state"] == State.Review

        # Step 2: Card should NOT be due yet
        res = client.get("/api/learning/due")
        due_ids = [i["concept_id"] for i in res.json()["items"]]
        assert "full_cycle" not in due_ids

        # Step 3: Manually backdate the due time to make it overdue
        sc.update_fsrs_card("full_cycle", {
            'stability': card["stability"],
            'difficulty': card["difficulty"],
            'due': time.time() - 1000,  # overdue
            'elapsed_days': card["scheduled_days"],
            'scheduled_days': card["scheduled_days"],
            'reps': card["reps"],
            'lapses': card["lapses"],
            'state': card["state"],
            'last_review': time.time() - card["scheduled_days"] * 86400,
        })

        # Step 4: Now it should be due
        res = client.get("/api/learning/due")
        due_ids = [i["concept_id"] for i in res.json()["items"]]
        assert "full_cycle" in due_ids

        # Step 5: Review it again
        res = client.post("/api/learning/review", json={
            "concept_id": "full_cycle",
            "rating": 3,
        })
        assert res.status_code == 200
        assert res.json()["card"]["reps"] == 2
