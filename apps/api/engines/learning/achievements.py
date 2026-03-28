"""
Achievement System — 成就系统
Gamification engine for AI Knowledge Graph learning platform.

Achievement categories:
  - learning:    Mastering N concepts (milestone thresholds)
  - streak:      Consecutive study days
  - domain:      Domain-specific mastery depth
  - assessment:  Score-based achievements
  - review:      FSRS spaced repetition milestones
  - special:     Rare / hidden achievements

Each achievement is defined as a dict with:
  key:          Unique identifier (e.g. "first_light")
  category:     One of the categories above
  name:         Display name
  description:  How to unlock
  icon:         Emoji icon
  tier:         bronze / silver / gold / platinum
  check:        Function(stats) → (unlocked: bool, progress: float 0-100)

Stats dict passed to check functions contains:
  mastered_count, learning_count, total_concepts,
  current_streak, longest_streak,
  total_assessments, perfect_scores, assessment_accuracy,
  total_reviews, review_streak,
  domains_started, domains_mastered_5, domains_mastered_10,
  first_mastered_at, total_study_time_sec,
  highest_score, mastered_milestones
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AchievementDef:
    """Achievement definition — immutable blueprint."""
    key: str
    category: str
    name: str
    description: str
    icon: str
    tier: str  # bronze / silver / gold / platinum
    check: Callable[[dict], tuple[bool, float]]  # (unlocked, progress%)

    def to_dict(self) -> dict:
        return {
            'key': self.key,
            'category': self.category,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'tier': self.tier,
        }


# ═══════════════════════════════════════════════
# Achievement Definitions
# ═══════════════════════════════════════════════

def _pct(current: float, target: float) -> float:
    """Calculate progress percentage, clamped to [0, 100]."""
    if target <= 0:
        return 100.0
    return min(100.0, max(0.0, (current / target) * 100.0))


# ── Learning Milestones ──

ACHIEVEMENTS: list[AchievementDef] = [
    AchievementDef(
        key="first_light",
        category="learning",
        name="🌟 第一道光",
        description="掌握第一个知识概念",
        icon="🌟",
        tier="bronze",
        check=lambda s: (s['mastered_count'] >= 1, _pct(s['mastered_count'], 1)),
    ),
    AchievementDef(
        key="explorer_10",
        category="learning",
        name="🧭 探索者",
        description="掌握10个知识概念",
        icon="🧭",
        tier="bronze",
        check=lambda s: (s['mastered_count'] >= 10, _pct(s['mastered_count'], 10)),
    ),
    AchievementDef(
        key="scholar_50",
        category="learning",
        name="📚 学者",
        description="掌握50个知识概念",
        icon="📚",
        tier="silver",
        check=lambda s: (s['mastered_count'] >= 50, _pct(s['mastered_count'], 50)),
    ),
    AchievementDef(
        key="master_100",
        category="learning",
        name="🎓 大师",
        description="掌握100个知识概念",
        icon="🎓",
        tier="gold",
        check=lambda s: (s['mastered_count'] >= 100, _pct(s['mastered_count'], 100)),
    ),
    AchievementDef(
        key="sage_200",
        category="learning",
        name="🏛️ 智者",
        description="掌握200个知识概念",
        icon="🏛️",
        tier="platinum",
        check=lambda s: (s['mastered_count'] >= 200, _pct(s['mastered_count'], 200)),
    ),

    # ── Streak Achievements ──

    AchievementDef(
        key="streak_3",
        category="streak",
        name="🔥 三日连燃",
        description="连续学习3天",
        icon="🔥",
        tier="bronze",
        check=lambda s: (s['longest_streak'] >= 3, _pct(s['longest_streak'], 3)),
    ),
    AchievementDef(
        key="streak_7",
        category="streak",
        name="⚡ 一周不断",
        description="连续学习7天",
        icon="⚡",
        tier="silver",
        check=lambda s: (s['longest_streak'] >= 7, _pct(s['longest_streak'], 7)),
    ),
    AchievementDef(
        key="streak_14",
        category="streak",
        name="💪 两周坚持",
        description="连续学习14天",
        icon="💪",
        tier="gold",
        check=lambda s: (s['longest_streak'] >= 14, _pct(s['longest_streak'], 14)),
    ),
    AchievementDef(
        key="streak_30",
        category="streak",
        name="🏆 月度传奇",
        description="连续学习30天",
        icon="🏆",
        tier="platinum",
        check=lambda s: (s['longest_streak'] >= 30, _pct(s['longest_streak'], 30)),
    ),

    # ── Domain Mastery ──

    AchievementDef(
        key="domain_explorer",
        category="domain",
        name="🌐 跨域探索者",
        description="在3个不同领域开始学习",
        icon="🌐",
        tier="bronze",
        check=lambda s: (s['domains_started'] >= 3, _pct(s['domains_started'], 3)),
    ),
    AchievementDef(
        key="domain_deep_5",
        category="domain",
        name="🔬 深度研究者",
        description="在一个领域掌握5个概念",
        icon="🔬",
        tier="silver",
        check=lambda s: (s['domains_mastered_5'] >= 1, _pct(s['domains_mastered_5'], 1)),
    ),
    AchievementDef(
        key="domain_deep_10",
        category="domain",
        name="🧬 领域专家",
        description="在一个领域掌握10个概念",
        icon="🧬",
        tier="gold",
        check=lambda s: (s['domains_mastered_10'] >= 1, _pct(s['domains_mastered_10'], 1)),
    ),

    # ── Assessment Achievements ──

    AchievementDef(
        key="perfect_score",
        category="assessment",
        name="💯 满分达人",
        description="在评估中获得100分",
        icon="💯",
        tier="silver",
        check=lambda s: (s['highest_score'] >= 100, _pct(s['highest_score'], 100)),
    ),
    AchievementDef(
        key="high_achiever",
        category="assessment",
        name="🎯 高分射手",
        description="累计获得10次90分以上的评估",
        icon="🎯",
        tier="gold",
        check=lambda s: (s.get('high_scores_90', 0) >= 10, _pct(s.get('high_scores_90', 0), 10)),
    ),
    AchievementDef(
        key="first_assessment",
        category="assessment",
        name="📝 初次挑战",
        description="完成第一次评估",
        icon="📝",
        tier="bronze",
        check=lambda s: (s['total_assessments'] >= 1, _pct(s['total_assessments'], 1)),
    ),

    # ── Review (FSRS) Achievements ──

    AchievementDef(
        key="first_review",
        category="review",
        name="🔄 温故知新",
        description="完成第一次间隔复习",
        icon="🔄",
        tier="bronze",
        check=lambda s: (s['total_reviews'] >= 1, _pct(s['total_reviews'], 1)),
    ),
    AchievementDef(
        key="review_10",
        category="review",
        name="📖 复习达人",
        description="完成10次间隔复习",
        icon="📖",
        tier="silver",
        check=lambda s: (s['total_reviews'] >= 10, _pct(s['total_reviews'], 10)),
    ),
    AchievementDef(
        key="review_50",
        category="review",
        name="🧠 记忆大师",
        description="完成50次间隔复习",
        icon="🧠",
        tier="gold",
        check=lambda s: (s['total_reviews'] >= 50, _pct(s['total_reviews'], 50)),
    ),

    # ── Special / Hidden ──

    AchievementDef(
        key="milestone_master",
        category="special",
        name="⭐ 里程碑征服者",
        description="掌握5个里程碑节点",
        icon="⭐",
        tier="gold",
        check=lambda s: (s.get('mastered_milestones', 0) >= 5, _pct(s.get('mastered_milestones', 0), 5)),
    ),
    AchievementDef(
        key="speed_learner",
        category="special",
        name="⚡ 快速学习者",
        description="一天内掌握5个概念",
        icon="⚡",
        tier="silver",
        check=lambda s: (s.get('mastered_today', 0) >= 5, _pct(s.get('mastered_today', 0), 5)),
    ),
]

# Lookup map
ACHIEVEMENT_MAP: dict[str, AchievementDef] = {a.key: a for a in ACHIEVEMENTS}


# ═══════════════════════════════════════════════
# Achievement Check Engine
# ═══════════════════════════════════════════════

class AchievementEngine:
    """Evaluates achievements against current learning stats.

    Usage:
        engine = AchievementEngine()
        stats = engine.collect_stats()  # from DB
        newly_unlocked = engine.check_all(stats, already_unlocked_keys)
    """

    def check_all(self, stats: dict, already_unlocked: set[str]) -> list[dict]:
        """Check all achievements and return newly unlocked ones.

        Args:
            stats: Learning statistics dict (see module docstring)
            already_unlocked: Set of achievement keys already unlocked

        Returns:
            List of {key, name, icon, tier, progress} for newly unlocked achievements
        """
        newly = []
        for ach in ACHIEVEMENTS:
            if ach.key in already_unlocked:
                continue
            unlocked, progress = ach.check(stats)
            if unlocked:
                newly.append({
                    'key': ach.key,
                    'name': ach.name,
                    'icon': ach.icon,
                    'tier': ach.tier,
                    'progress': round(progress, 1),
                })
        if newly:
            logger.info("Achievements unlocked", extra={"count": len(newly), "keys": [a['key'] for a in newly]})
        return newly

    def get_all_with_status(self, stats: dict, unlocked_map: dict[str, dict]) -> list[dict]:
        """Get all achievements with current unlock status and progress.

        Args:
            stats: Learning statistics dict
            unlocked_map: {key: {unlocked_at, seen}} for unlocked achievements

        Returns:
            List of achievement dicts with status info
        """
        result = []
        for ach in ACHIEVEMENTS:
            unlocked_info = unlocked_map.get(ach.key)
            is_unlocked = unlocked_info is not None
            _, progress = ach.check(stats)

            entry = {
                **ach.to_dict(),
                'unlocked': is_unlocked,
                'progress': round(progress, 1),
            }
            if is_unlocked:
                entry['unlocked_at'] = unlocked_info.get('unlocked_at', 0)
                entry['seen'] = unlocked_info.get('seen', False)
            result.append(entry)
        return result

    @staticmethod
    def collect_stats_from_db() -> dict:
        """Collect all stats needed for achievement checks from the database.

        Returns a dict with all the fields that achievement check functions expect.
        """
        from db.sqlite_client import (
            get_all_progress, get_streak, get_history, refresh_streak
        )
        import time
        from datetime import datetime, timedelta

        progress_list = get_all_progress()
        streak = refresh_streak()
        history = get_history(limit=10000)  # Get all history for stats

        mastered = [p for p in progress_list if p['status'] == 'mastered']
        mastered_count = len(mastered)
        learning_count = sum(1 for p in progress_list if p['status'] == 'learning')

        # Domain stats: count unique domains from concept_id prefixes or subdomain patterns
        # We'll check which domain each mastered concept belongs to using seed data
        domain_mastered_counts = _count_domain_mastery(mastered)

        # Assessment stats from history
        total_assessments = len(history)
        scores = [h['score'] for h in history]
        highest_score = max(scores) if scores else 0
        high_scores_90 = sum(1 for s in scores if s >= 90)
        perfect_scores = sum(1 for s in scores if s >= 100)

        # Review stats (FSRS reviews = entries with fsrs_reps > 0)
        total_reviews = sum(1 for p in progress_list if p.get('fsrs_reps', 0) > 0)

        # Mastered today
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
        mastered_today = sum(
            1 for p in mastered
            if p.get('mastered_at') and p['mastered_at'] >= today_start
        )

        # Milestone mastery count (requires seed data check)
        mastered_milestones = _count_mastered_milestones(mastered)

        return {
            'mastered_count': mastered_count,
            'learning_count': learning_count,
            'total_concepts': len(progress_list),
            'current_streak': streak.get('current_streak', 0),
            'longest_streak': streak.get('longest_streak', 0),
            'total_assessments': total_assessments,
            'highest_score': highest_score,
            'high_scores_90': high_scores_90,
            'perfect_scores': perfect_scores,
            'total_reviews': total_reviews,
            'domains_started': len(domain_mastered_counts),
            'domains_mastered_5': sum(1 for c in domain_mastered_counts.values() if c >= 5),
            'domains_mastered_10': sum(1 for c in domain_mastered_counts.values() if c >= 10),
            'mastered_today': mastered_today,
            'mastered_milestones': mastered_milestones,
            'total_study_time_sec': sum(p.get('total_time_sec', 0) for p in progress_list),
        }


def _count_domain_mastery(mastered_progress: list[dict]) -> dict[str, int]:
    """Count mastered concepts per domain by checking seed data.

    Returns: {domain_id: count}
    """
    import json
    import os

    if not mastered_progress:
        return {}

    mastered_ids = {p['concept_id'] for p in mastered_progress}
    domain_counts: dict[str, int] = {}

    # Load domains list
    seed_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'data', 'seed')
    domains_path = os.path.join(seed_dir, 'domains.json')

    try:
        with open(domains_path, 'r', encoding='utf-8') as f:
            domains_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

    for domain in domains_data.get('domains', []):
        if not domain.get('is_active'):
            continue
        domain_id = domain['id']
        seed_path = os.path.join(seed_dir, domain_id, 'seed_graph.json')
        try:
            with open(seed_path, 'r', encoding='utf-8') as f:
                seed = json.load(f)
            domain_concept_ids = {c['id'] for c in seed.get('concepts', [])}
            count = len(mastered_ids & domain_concept_ids)
            if count > 0:
                domain_counts[domain_id] = count
        except (FileNotFoundError, json.JSONDecodeError):
            continue

    return domain_counts


def _count_mastered_milestones(mastered_progress: list[dict]) -> int:
    """Count how many mastered concepts are milestone nodes."""
    import json
    import os

    if not mastered_progress:
        return 0

    mastered_ids = {p['concept_id'] for p in mastered_progress}
    milestone_count = 0

    seed_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'data', 'seed')
    domains_path = os.path.join(seed_dir, 'domains.json')

    try:
        with open(domains_path, 'r', encoding='utf-8') as f:
            domains_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0

    for domain in domains_data.get('domains', []):
        if not domain.get('is_active'):
            continue
        seed_path = os.path.join(seed_dir, domain['id'], 'seed_graph.json')
        try:
            with open(seed_path, 'r', encoding='utf-8') as f:
                seed = json.load(f)
            for c in seed.get('concepts', []):
                if c.get('is_milestone') and c['id'] in mastered_ids:
                    milestone_count += 1
        except (FileNotFoundError, json.JSONDecodeError):
            continue

    return milestone_count