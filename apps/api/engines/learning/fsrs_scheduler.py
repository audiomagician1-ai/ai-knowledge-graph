"""
FSRS-5 间隔重复调度器
Self-contained implementation of the FSRS-5 (Free Spaced Repetition Scheduler) algorithm.

Reference: https://github.com/open-spaced-repetition/fsrs4anki/wiki/The-Algorithm
FSRS-5 separates *difficulty* and *stability* into independent parameters,
achieving 97.4% superiority over SM-2 in empirical tests.

Card states:
  - New(0): never reviewed
  - Learning(1): first seen, in initial learning phase
  - Review(2): graduated to review queue
  - Relearning(3): lapsed, re-entering learning

Rating:
  - Again(1): complete failure
  - Hard(2): recalled with difficulty
  - Good(3): recalled correctly
  - Easy(4): recalled effortlessly
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field, asdict
from enum import IntEnum
from typing import Optional


# ── Enums ──────────────────────────────────────────────

class State(IntEnum):
    New = 0
    Learning = 1
    Review = 2
    Relearning = 3


class Rating(IntEnum):
    Again = 1
    Hard = 2
    Good = 3
    Easy = 4


# ── Data classes ───────────────────────────────────────

@dataclass
class Card:
    """Represents the FSRS state of a single review item (concept)."""
    due: float = 0.0               # next review timestamp (epoch seconds)
    stability: float = 0.0         # memory stability S (days until R=90%)
    difficulty: float = 0.0        # item difficulty D ∈ [1, 10]
    elapsed_days: int = 0          # days since last review
    scheduled_days: int = 0        # days scheduled for next review
    reps: int = 0                  # total successful reviews
    lapses: int = 0                # total lapses (Again after Review)
    state: int = State.New         # current state
    last_review: float = 0.0       # last review timestamp (epoch seconds)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> Card:
        if not d:
            return cls()
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class ReviewLog:
    """Record of a single review event."""
    rating: int
    state: int                      # state *before* the review
    due: float
    stability: float
    difficulty: float
    elapsed_days: int
    scheduled_days: int
    review_time: float              # epoch seconds when reviewed


@dataclass
class SchedulingResult:
    """Output of a scheduling operation."""
    card: Card
    review_log: ReviewLog


# ── FSRS-5 Scheduler ──────────────────────────────────

class FSRSScheduler:
    """FSRS spaced repetition engine (compatible with FSRS-6 parameter format).

    Uses the standard FSRS parameter set (default weights from py-fsrs / Anki).
    Separates difficulty (D) and stability (S) for independent tracking.

    Parameter mapping (21 params, FSRS-6 format):
        w[0-3]:   Initial stability S0 for each rating (Again/Hard/Good/Easy)
        w[4]:     Initial difficulty D0 base
        w[5]:     Difficulty exp factor
        w[6]:     Difficulty delta factor
        w[7]:     Difficulty mean reversion weight
        w[8]:     Recall stability: SInc scale (e^w8)
        w[9]:     Recall stability: D-power
        w[10]:    Recall stability: S-power
        w[11]:    Recall stability: R-exp
        w[12]:    Forget stability: scale
        w[13]:    Forget stability: D-power
        w[14]:    Forget stability: S-power
        w[15]:    Recall stability: hard penalty (< 1 for Hard rating)
        w[16]:    Recall stability: easy bonus (> 1 for Easy rating)
        w[17]:    Short-term stability: exp base
        w[18]:    Short-term stability: rating offset
        w[19]:    Short-term stability: S-power
        w[20]:    Decay parameter for forgetting curve
    """

    # FSRS-6 default parameters (from py-fsrs / open-spaced-repetition)
    DEFAULT_WEIGHTS = (
        0.2120,   # w0  - initial stability for Again
        1.2931,   # w1  - initial stability for Hard
        2.3065,   # w2  - initial stability for Good
        8.2956,   # w3  - initial stability for Easy
        6.4133,   # w4  - initial difficulty base
        0.8334,   # w5  - difficulty exp factor
        3.0194,   # w6  - difficulty delta factor
        0.0010,   # w7  - difficulty mean reversion weight
        1.8722,   # w8  - recall stability SInc scale
        0.1666,   # w9  - recall stability D-power
        0.7960,   # w10 - recall stability S-power
        1.4835,   # w11 - recall stability R-exp
        0.0614,   # w12 - forget stability scale
        0.2629,   # w13 - forget stability D-power
        1.6483,   # w14 - forget stability S-power
        0.6014,   # w15 - hard penalty in recall stability (< 1)
        1.8729,   # w16 - easy bonus in recall stability (> 1)
        0.5425,   # w17 - short-term stability exp base
        0.0912,   # w18 - short-term stability rating offset
        0.0658,   # w19 - short-term stability S-power
        0.1542,   # w20 - decay parameter for forgetting curve
    )

    # Desired retention rate (target recall probability at review time)
    DESIRED_RETENTION = 0.9

    # Bounds
    MAX_INTERVAL = 36500  # 100 years (effectively no cap)
    MIN_DIFFICULTY = 1.0
    MAX_DIFFICULTY = 10.0

    def __init__(
        self,
        weights: tuple[float, ...] | None = None,
        desired_retention: float = 0.9,
        max_interval: int = 36500,
    ):
        self.w = weights or self.DEFAULT_WEIGHTS
        self.desired_retention = max(0.7, min(0.99, desired_retention))
        self.max_interval = max_interval
        # Decay from w[20] if available, else use default
        self._decay = -self.w[20] if len(self.w) > 20 else -0.5
        self._factor = 0.9 ** (1 / self._decay) - 1

    # ── Public API ─────────────────────────────────────

    def review(self, card: Card, rating: Rating, now: float | None = None) -> SchedulingResult:
        """Process a review and return the updated card + log.

        Args:
            card: Current card state (may be New)
            rating: User's self-assessment (Again/Hard/Good/Easy)
            now: Review timestamp (epoch seconds). Defaults to current time.

        Returns:
            SchedulingResult with updated card and review log.
        """
        now = now or time.time()
        rating = Rating(rating)

        # Save pre-review state for the log
        log = ReviewLog(
            rating=int(rating),
            state=card.state,
            due=card.due,
            stability=card.stability,
            difficulty=card.difficulty,
            elapsed_days=card.elapsed_days,
            scheduled_days=card.scheduled_days,
            review_time=now,
        )

        # Calculate elapsed days since last review
        if card.last_review > 0:
            elapsed_days = max(0, int((now - card.last_review) / 86400))
        else:
            elapsed_days = 0

        card.elapsed_days = elapsed_days
        card.reps += 1
        card.last_review = now

        old_state = State(card.state)

        if old_state == State.New:
            card = self._process_new(card, rating, now)
        elif old_state in (State.Learning, State.Relearning):
            card = self._process_learning(card, rating, now, old_state)
        elif old_state == State.Review:
            card = self._process_review(card, rating, now)

        return SchedulingResult(card=card, review_log=log)

    def next_interval(self, stability: float) -> int:
        """Calculate the next interval in days from stability.

        interval = (S / FACTOR) * (R^(1/DECAY) - 1)  where R = desired_retention
        Reference: https://github.com/open-spaced-repetition/py-fsrs
        When desired_retention = 0.9, this simplifies to interval ≈ S (stability in days).
        """
        interval = (stability / self._factor) * (self.desired_retention ** (1 / self._decay) - 1)
        return max(1, min(self.max_interval, round(interval)))

    def forgetting_curve(self, elapsed_days: int, stability: float) -> float:
        """Calculate retrievability R given elapsed time and stability.

        R(t, S) = (1 + FACTOR * t / S) ^ DECAY
        """
        if stability <= 0:
            return 0.0
        return (1.0 + self._factor * elapsed_days / stability) ** self._decay

    # ── Internal: process by state ─────────────────────

    def _process_new(self, card: Card, rating: Rating, now: float) -> Card:
        """First review of a new card."""
        card.difficulty = self._init_difficulty(rating)
        card.stability = self._init_stability(rating)

        if rating == Rating.Again:
            card.state = State.Learning
            card.scheduled_days = 0
            card.due = now + 60  # 1 minute
        elif rating == Rating.Hard:
            card.state = State.Learning
            card.scheduled_days = 0
            card.due = now + 300  # 5 minutes
        elif rating == Rating.Good:
            card.state = State.Review
            interval = self.next_interval(card.stability)
            card.scheduled_days = interval
            card.due = now + interval * 86400
        else:  # Easy
            card.state = State.Review
            interval = max(self.next_interval(card.stability), 4)
            card.scheduled_days = interval
            card.due = now + interval * 86400

        return card

    def _process_learning(self, card: Card, rating: Rating, now: float, old_state: State) -> Card:
        """Review during Learning or Relearning phase."""
        card.difficulty = self._next_difficulty(card.difficulty, rating)

        if rating == Rating.Again:
            card.stability = self._short_term_stability(card.stability, rating)
            card.state = old_state  # stay in learning/relearning
            card.scheduled_days = 0
            card.due = now + 300  # 5 minutes
        elif rating == Rating.Hard:
            card.stability = self._short_term_stability(card.stability, rating)
            card.state = old_state
            card.scheduled_days = 0
            card.due = now + 600  # 10 minutes
        elif rating == Rating.Good:
            card.stability = self._short_term_stability(card.stability, rating)
            card.state = State.Review
            interval = self.next_interval(card.stability)
            card.scheduled_days = interval
            card.due = now + interval * 86400
        else:  # Easy
            card.stability = self._short_term_stability(card.stability, rating)
            card.state = State.Review
            interval = max(self.next_interval(card.stability), 4)
            card.scheduled_days = interval
            card.due = now + interval * 86400

        return card

    def _process_review(self, card: Card, rating: Rating, now: float) -> Card:
        """Review of a graduated (Review state) card."""
        retrievability = self.forgetting_curve(card.elapsed_days, card.stability)
        card.difficulty = self._next_difficulty(card.difficulty, rating)

        if rating == Rating.Again:
            card.lapses += 1
            card.stability = self._next_forget_stability(
                card.difficulty, card.stability, retrievability
            )
            card.state = State.Relearning
            card.scheduled_days = 0
            card.due = now + 300  # 5 minutes
        elif rating == Rating.Hard:
            card.stability = self._next_recall_stability(
                card.difficulty, card.stability, retrievability, rating
            )
            card.state = State.Review
            interval = self.next_interval(card.stability)
            card.scheduled_days = interval
            card.due = now + interval * 86400
        elif rating == Rating.Good:
            card.stability = self._next_recall_stability(
                card.difficulty, card.stability, retrievability, rating
            )
            card.state = State.Review
            interval = self.next_interval(card.stability)
            card.scheduled_days = interval
            card.due = now + interval * 86400
        else:  # Easy
            card.stability = self._next_recall_stability(
                card.difficulty, card.stability, retrievability, rating
            )
            card.state = State.Review
            interval = max(self.next_interval(card.stability), card.scheduled_days + 1)
            card.scheduled_days = interval
            card.due = now + interval * 86400

        return card

    # ── FSRS-5 formulas ────────────────────────────────

    def _init_stability(self, rating: Rating) -> float:
        """Initial stability S0 for a new card.
        S0(G) = w[G-1]  where G is the rating (1-4).
        """
        return max(0.1, self.w[int(rating) - 1])

    def _init_difficulty(self, rating: Rating) -> float:
        """Initial difficulty D0 for a new card.
        D0(G) = w4 - exp(w5 * (G - 1)) + 1
        Clamped to [1, 10].
        """
        d = self.w[4] - math.exp(self.w[5] * (int(rating) - 1)) + 1
        return self._clamp_difficulty(d)

    def _next_difficulty(self, d: float, rating: Rating) -> float:
        """Update difficulty after a review.
        Uses linear damping + mean reversion toward D0(Easy).
        Reference: py-fsrs Scheduler._next_difficulty
        """
        d0_easy = self._init_difficulty(Rating.Easy)
        delta_d = -(self.w[6] * (int(rating) - 3))
        # Linear damping: (10 - D) * delta / 9
        linear_damped = (10.0 - d) * delta_d / 9.0
        new_d = d + linear_damped
        # Mean reversion toward D0(Easy)
        new_d = self.w[7] * d0_easy + (1 - self.w[7]) * new_d
        return self._clamp_difficulty(new_d)

    def _next_recall_stability(
        self, d: float, s: float, r: float, rating: Rating
    ) -> float:
        """Stability after successful recall.
        S'_r(D, S, R, G) = S * (e^(w8) * (11-D) * S^(-w9) * (e^(w10*(1-R)) - 1) * hard_penalty * easy_bonus + 1)

        hard_penalty = w[15] if Hard else 1.0 (< 1 reduces growth for Hard)
        easy_bonus = w[16] if Easy else 1.0 (> 1 increases growth for Easy)
        """
        hard_penalty = self.w[15] if rating == Rating.Hard else 1.0
        easy_bonus = self.w[16] if rating == Rating.Easy else 1.0

        inner = (
            math.exp(self.w[8])
            * (11.0 - d)
            * s ** (-self.w[9])
            * (math.exp(self.w[10] * (1.0 - r)) - 1.0)
            * hard_penalty
            * easy_bonus
        )
        new_s = s * (inner + 1.0)
        return max(0.1, new_s)

    def _next_forget_stability(self, d: float, s: float, r: float) -> float:
        """Stability after a lapse (Again on Review card).
        S'_f(D, S, R) = w12 * D^(-w13) * ((S+1)^w14 - 1) * e^(w15*(1-R))
        Note: py-fsrs doesn't use w[15] here; the forget formula uses w[11-14].
        Adjusted to match py-fsrs: w[11] * D^(-w[12]) * ((S+1)^w[13] - 1) * e^(w[14]*(1-R))
        Then clamp: S_forget <= S and good/easy can't decrease.
        """
        new_s = (
            self.w[11]
            * d ** (-self.w[12])
            * ((s + 1.0) ** self.w[13] - 1.0)
            * math.exp(self.w[14] * (1.0 - r))
        )
        return max(0.1, min(new_s, s))  # Never exceed previous stability after failure

    def _short_term_stability(self, s: float, rating: Rating) -> float:
        """Stability update for Learning/Relearning states.
        S'_s(S, G) = S * e^(w17 * (G - 3 + w18)) * S^(-w19)

        For Good/Easy: SInc is clamped to >= 1 (cannot decrease stability).
        Reference: py-fsrs Scheduler._short_term_stability
        """
        sinc = math.exp(self.w[17] * (int(rating) - 3 + self.w[18])) * s ** (-self.w[19])
        if rating in (Rating.Good, Rating.Easy):
            sinc = max(sinc, 1.0)
        new_s = s * sinc
        return max(0.1, new_s)

    def _clamp_difficulty(self, d: float) -> float:
        return max(self.MIN_DIFFICULTY, min(self.MAX_DIFFICULTY, d))
