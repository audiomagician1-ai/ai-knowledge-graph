"""
BKT 知识追踪器 — Bayesian Knowledge Tracing
贝叶斯知识追踪引擎，MVP阶段使用。

隐马尔可夫模型:
- 隐状态: 学习者是否已掌握概念 (L=1) 或未掌握 (L=0)
- 观测: 评估作答是否正确 (correct=1 / incorrect=0)
- 参数:
    P(L0) — 先验知识概率: 学习者在首次接触前已掌握的概率
    P(T)  — 学习转换概率: 每次练习机会从未掌握变为掌握的概率
    P(G)  — 猜测概率:     未掌握时答对的概率
    P(S)  — 失误概率:     已掌握时答错的概率

更新公式 (posterior update):
    观测 correct=1:
        P(L|correct) = P(L_n) * (1 - P(S)) / P(correct)
        P(correct)   = P(L_n) * (1 - P(S)) + (1 - P(L_n)) * P(G)

    观测 correct=0:
        P(L|incorrect) = P(L_n) * P(S) / P(incorrect)
        P(incorrect)   = P(L_n) * P(S) + (1 - P(L_n)) * (1 - P(G))

    学习转换 (在后验基础上应用):
        P(L_{n+1}) = P(L|obs) + (1 - P(L|obs)) * P(T)

参考文献:
- Corbett & Anderson (1994). "Knowledge tracing: Modeling the acquisition of procedural knowledge"
- Baker et al. (2008). "More Accurate Student Modeling through Contextual Estimation of Slip and Guess Probabilities in Bayesian Knowledge Tracing"
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from typing import Optional


# ── Default parameters ────────────────────────────────

# Standard BKT defaults from literature
DEFAULT_P_L0 = 0.10   # Low prior: most concepts start unknown
DEFAULT_P_T = 0.30     # Moderate learning rate per opportunity
DEFAULT_P_G = 0.25     # ~25% chance of guessing correctly (4-option MCQ baseline)
DEFAULT_P_S = 0.10     # Low slip rate: mastered knowledge is reliable

# Mastery threshold — P(L) above this is classified as "mastered"
DEFAULT_MASTERY_THRESHOLD = 0.90


# ── Data classes ──────────────────────────────────────

@dataclass
class BKTParams:
    """BKT model parameters for a concept.

    Can be customized per-concept based on difficulty, domain, etc.
    Higher difficulty → lower P(T) (slower learning), higher P(G) (more guessing).
    """
    p_l0: float = DEFAULT_P_L0    # Prior: P(L0)
    p_t: float = DEFAULT_P_T      # Learn: P(T)
    p_g: float = DEFAULT_P_G      # Guess: P(G)
    p_s: float = DEFAULT_P_S      # Slip: P(S)

    def __post_init__(self):
        """Validate all probabilities are in [0, 1] and constraints hold."""
        for name, val in [('p_l0', self.p_l0), ('p_t', self.p_t),
                          ('p_g', self.p_g), ('p_s', self.p_s)]:
            if not 0.0 <= val <= 1.0:
                raise ValueError(f"BKT param {name}={val} must be in [0, 1]")
        # Identifiability constraint: P(G) + P(S) < 1
        # Otherwise the model becomes degenerate
        if self.p_g + self.p_s >= 1.0:
            raise ValueError(
                f"P(G)={self.p_g} + P(S)={self.p_s} >= 1.0 — model is degenerate"
            )

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> BKTParams:
        return cls(
            p_l0=d.get('p_l0', DEFAULT_P_L0),
            p_t=d.get('p_t', DEFAULT_P_T),
            p_g=d.get('p_g', DEFAULT_P_G),
            p_s=d.get('p_s', DEFAULT_P_S),
        )

    @classmethod
    def for_difficulty(cls, difficulty: int) -> BKTParams:
        """Generate sensible BKT params based on concept difficulty (1-5).

        Higher difficulty:
        - Lower P(L0): less likely to already know
        - Lower P(T): harder to learn per opportunity
        - Higher P(G): more guessing (complex questions)
        - Same P(S): slip rate stays consistent
        """
        diff = max(1, min(5, difficulty))  # clamp to [1, 5]
        return cls(
            p_l0=max(0.02, 0.20 - diff * 0.04),   # diff1=0.16, diff3=0.08, diff5=0.02
            p_t=max(0.10, 0.45 - diff * 0.08),      # diff1=0.37, diff3=0.21, diff5=0.10
            p_g=min(0.35, 0.15 + diff * 0.04),      # diff1=0.19, diff3=0.27, diff5=0.35
            p_s=DEFAULT_P_S,                          # constant 0.10
        )


@dataclass
class BKTState:
    """Current BKT state for a concept.

    Tracks the evolving mastery probability P(L) and observation history.
    """
    p_mastery: float = DEFAULT_P_L0          # Current P(L) after all observations
    observations: int = 0                     # Number of observations processed
    correct_count: int = 0                    # Number of correct observations
    params: BKTParams = field(default_factory=BKTParams)
    mastery_threshold: float = DEFAULT_MASTERY_THRESHOLD

    @property
    def is_mastered(self) -> bool:
        """Whether P(L) exceeds the mastery threshold."""
        return self.p_mastery >= self.mastery_threshold

    @property
    def accuracy(self) -> float:
        """Observed accuracy rate."""
        return self.correct_count / self.observations if self.observations > 0 else 0.0

    @property
    def classification(self) -> str:
        """Human-readable mastery classification."""
        p = self.p_mastery
        if p >= 0.95:
            return "expert"
        elif p >= self.mastery_threshold:
            return "mastered"
        elif p >= 0.70:
            return "proficient"
        elif p >= 0.50:
            return "developing"
        elif p >= 0.30:
            return "beginner"
        else:
            return "novice"

    def to_dict(self) -> dict:
        return {
            'p_mastery': self.p_mastery,
            'observations': self.observations,
            'correct_count': self.correct_count,
            'params': self.params.to_dict(),
            'mastery_threshold': self.mastery_threshold,
            'is_mastered': self.is_mastered,
            'accuracy': round(self.accuracy, 4),
            'classification': self.classification,
        }

    @classmethod
    def from_db(cls, p_mastery: float, observations: int, correct_count: int,
                params_json: str = '') -> BKTState:
        """Reconstruct from DB columns."""
        params = BKTParams.from_dict(json.loads(params_json)) if params_json else BKTParams()
        return cls(
            p_mastery=p_mastery,
            observations=observations,
            correct_count=correct_count,
            params=params,
        )


# ── Core BKT Engine ───────────────────────────────────

class KnowledgeTracker:
    """BKT 知识追踪引擎

    贝叶斯隐马尔可夫模型:
    - P(L0): 先验知识概率
    - P(T):  学习转换概率
    - P(G):  猜测概率
    - P(S):  失误概率

    MVP 阶段使用 BKT，中期过渡到 DKT (RNN)

    Usage:
        tracker = KnowledgeTracker()

        # Initialize state for a new concept
        state = tracker.init_state(difficulty=3)

        # Update after a correct answer
        state = tracker.update(state, correct=True)

        # Check mastery
        if state.is_mastered:
            print("Concept mastered!")
    """

    def __init__(self, mastery_threshold: float = DEFAULT_MASTERY_THRESHOLD):
        """Initialize the tracker.

        Args:
            mastery_threshold: P(L) threshold to classify as mastered (default 0.90)
        """
        if not 0.0 < mastery_threshold < 1.0:
            raise ValueError(f"mastery_threshold={mastery_threshold} must be in (0, 1)")
        self.mastery_threshold = mastery_threshold

    def init_state(self, params: Optional[BKTParams] = None,
                   difficulty: Optional[int] = None) -> BKTState:
        """Create initial BKT state for a concept.

        Args:
            params: Custom BKT parameters. If None, derived from difficulty.
            difficulty: Concept difficulty (1-5). Used only if params is None.

        Returns:
            Fresh BKTState with P(L) = P(L0)
        """
        if params is None:
            params = BKTParams.for_difficulty(difficulty) if difficulty else BKTParams()

        return BKTState(
            p_mastery=params.p_l0,
            observations=0,
            correct_count=0,
            params=params,
            mastery_threshold=self.mastery_threshold,
        )

    def update(self, state: BKTState, correct: bool) -> BKTState:
        """Process a single observation and return updated state.

        Implements the standard BKT posterior update:
        1. Compute P(L|observation) using Bayes' rule
        2. Apply learning transition: P(L') = P(L|obs) + (1 - P(L|obs)) * P(T)

        Args:
            state: Current BKT state
            correct: Whether the student answered correctly

        Returns:
            New BKTState with updated P(L)
        """
        p_l = state.p_mastery
        p_t = state.params.p_t
        p_g = state.params.p_g
        p_s = state.params.p_s

        # Step 1: Posterior update using Bayes' rule
        if correct:
            # P(correct) = P(L)*P(correct|L) + P(~L)*P(correct|~L)
            #            = P(L)*(1-P(S)) + (1-P(L))*P(G)
            p_obs = p_l * (1 - p_s) + (1 - p_l) * p_g
            # Avoid division by zero (shouldn't happen with valid params)
            if p_obs > 0:
                p_l_given_obs = (p_l * (1 - p_s)) / p_obs
            else:
                p_l_given_obs = p_l
        else:
            # P(incorrect) = P(L)*P(S) + (1-P(L))*(1-P(G))
            p_obs = p_l * p_s + (1 - p_l) * (1 - p_g)
            if p_obs > 0:
                p_l_given_obs = (p_l * p_s) / p_obs
            else:
                p_l_given_obs = p_l

        # Step 2: Learning transition
        # Even if the student didn't know before, they may have learned from the attempt
        p_l_new = p_l_given_obs + (1 - p_l_given_obs) * p_t

        # Clamp to [0, 1] for numerical safety
        p_l_new = max(0.0, min(1.0, p_l_new))

        return BKTState(
            p_mastery=p_l_new,
            observations=state.observations + 1,
            correct_count=state.correct_count + (1 if correct else 0),
            params=state.params,
            mastery_threshold=state.mastery_threshold,
        )

    def update_from_score(self, state: BKTState, score: float,
                          threshold: float = 70.0) -> BKTState:
        """Update BKT from a numerical score (0-100).

        Converts score to binary correct/incorrect using a threshold,
        then delegates to standard BKT update.

        Args:
            state: Current BKT state
            score: Assessment score (0-100)
            threshold: Score >= threshold counts as "correct" (default 70.0)

        Returns:
            Updated BKTState
        """
        return self.update(state, correct=(score >= threshold))

    def bulk_update(self, state: BKTState, observations: list[bool]) -> BKTState:
        """Process multiple observations sequentially.

        Args:
            state: Current BKT state
            observations: List of correct/incorrect outcomes

        Returns:
            BKTState after processing all observations
        """
        for correct in observations:
            state = self.update(state, correct)
        return state

    def predict_correct(self, state: BKTState) -> float:
        """Predict probability of answering correctly on next attempt.

        P(correct) = P(L) * (1 - P(S)) + (1 - P(L)) * P(G)

        Args:
            state: Current BKT state

        Returns:
            Predicted probability of correct response
        """
        p_l = state.p_mastery
        return p_l * (1 - state.params.p_s) + (1 - p_l) * state.params.p_g

    def expected_attempts_to_mastery(self, state: BKTState, max_iter: int = 100) -> int:
        """Estimate number of correct attempts needed to reach mastery.

        Simulates the BKT update assuming all-correct responses until
        P(L) >= mastery_threshold.

        Args:
            state: Current BKT state
            max_iter: Maximum iterations (safety limit)

        Returns:
            0 if already mastered, otherwise estimated number of correct attempts,
            or max_iter if not reachable
        """
        if state.is_mastered:
            return 0

        sim_state = BKTState(
            p_mastery=state.p_mastery,
            observations=state.observations,
            correct_count=state.correct_count,
            params=state.params,
            mastery_threshold=state.mastery_threshold,
        )
        for i in range(1, max_iter + 1):
            sim_state = self.update(sim_state, correct=True)
            if sim_state.is_mastered:
                return i
        return max_iter
