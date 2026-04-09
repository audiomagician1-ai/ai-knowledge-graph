"""学习引擎 API — FSRS 间隔重复 + 成就系统
从 learning.py (793L) 拆分: V3.5 Code Health"""

import time

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from utils.logger import get_logger

from db.sqlite_client import (
    get_unlocked_keys, get_unlocked_map, unlock_achievement,
    mark_achievements_seen, get_unseen_achievements,
)

logger = get_logger(__name__)

router = APIRouter()


# ════════════════════════════════════════════
# FSRS Spaced Repetition Endpoints
# ════════════════════════════════════════════

class ReviewRequest(BaseModel):
    """Submit a review rating for a concept."""
    concept_id: str = Field(..., max_length=200)
    rating: int = Field(..., ge=1, le=4, description="1=Again, 2=Hard, 3=Good, 4=Easy")


@router.get("/due")
async def get_due_reviews(
    limit: int = Query(20, ge=1, le=100),
    domain: str = Query("", max_length=100),
):
    """Get concepts due for spaced repetition review.

    Returns concepts that have been reviewed at least once and are past their
    scheduled review date. Sorted by most overdue first.
    """
    from db.sqlite_client import get_due_concepts

    now = time.time()
    due_items = get_due_concepts(before=now, limit=limit)

    # Optionally filter by domain
    if domain:
        from routers.graph import _load_seed
        try:
            seed = _load_seed(domain)
            domain_concept_ids = {c["id"] for c in seed["concepts"]}
            due_items = [d for d in due_items if d["concept_id"] in domain_concept_ids]
        except Exception:
            pass  # If domain not found, return all due items

    results = []
    for item in due_items:
        overdue_days = max(0, (now - item["fsrs_due"]) / 86400) if item["fsrs_due"] > 0 else 0
        results.append({
            "concept_id": item["concept_id"],
            "status": item["status"],
            "mastery_score": item["mastery_score"],
            "fsrs_state": item["fsrs_state"],
            "fsrs_stability": round(item["fsrs_stability"], 2),
            "fsrs_difficulty": round(item["fsrs_difficulty"], 2),
            "fsrs_due": item["fsrs_due"],
            "fsrs_reps": item["fsrs_reps"],
            "fsrs_lapses": item["fsrs_lapses"],
            "overdue_days": round(overdue_days, 1),
        })

    return {
        "due_count": len(results),
        "items": results,
    }


@router.post("/review")
async def submit_review(req: ReviewRequest):
    """Submit a review rating and update FSRS scheduling state.

    Rating scale:
    - 1 (Again): Complete failure to recall
    - 2 (Hard): Recalled with significant difficulty
    - 3 (Good): Recalled correctly with some effort
    - 4 (Easy): Recalled effortlessly

    Returns the updated card state including next review date.
    """
    from engines.learning.fsrs_scheduler import FSRSScheduler, Card, Rating
    from db.sqlite_client import get_fsrs_card, update_fsrs_card, update_streak

    scheduler = FSRSScheduler()
    now = time.time()

    # Load existing card state or create new
    card_data = get_fsrs_card(req.concept_id)
    if card_data:
        card = Card(
            due=card_data['due'],
            stability=card_data['stability'],
            difficulty=card_data['difficulty'],
            elapsed_days=card_data['elapsed_days'],
            scheduled_days=card_data['scheduled_days'],
            reps=card_data['reps'],
            lapses=card_data['lapses'],
            state=card_data['state'],
            last_review=card_data['last_review'],
        )
    else:
        card = Card()

    # Process the review
    result = scheduler.review(card, Rating(req.rating), now=now)
    updated = result.card

    # Persist updated card state
    update_fsrs_card(req.concept_id, {
        'stability': updated.stability,
        'difficulty': updated.difficulty,
        'due': updated.due,
        'elapsed_days': updated.elapsed_days,
        'scheduled_days': updated.scheduled_days,
        'reps': updated.reps,
        'lapses': updated.lapses,
        'state': updated.state,
        'last_review': updated.last_review,
    })

    # Also update streak (learning activity)
    update_streak()

    # Calculate retrievability for response
    retrievability = scheduler.forgetting_curve(updated.elapsed_days, updated.stability)

    return {
        "success": True,
        "concept_id": req.concept_id,
        "rating": req.rating,
        "card": {
            "state": updated.state,
            "stability": round(updated.stability, 3),
            "difficulty": round(updated.difficulty, 3),
            "due": updated.due,
            "scheduled_days": updated.scheduled_days,
            "reps": updated.reps,
            "lapses": updated.lapses,
            "retrievability": round(retrievability, 4),
        },
        "review_log": {
            "rating": result.review_log.rating,
            "previous_state": result.review_log.state,
            "previous_stability": round(result.review_log.stability, 3),
            "previous_difficulty": round(result.review_log.difficulty, 3),
        },
        "achievements_unlocked": check_and_unlock_achievements(),
    }


# ════════════════════════════════════════════
# Achievement System
# ════════════════════════════════════════════

class MarkSeenRequest(BaseModel):
    """Request to mark achievements as seen."""
    keys: list[str] = Field(..., max_length=50)


def check_and_unlock_achievements() -> list[dict]:
    """Check all achievement conditions and unlock any newly earned ones.

    Called after learning events (assess, review, etc.).
    Returns list of newly unlocked achievement dicts.
    """
    from engines.learning.achievements import AchievementEngine, ACHIEVEMENT_MAP

    engine = AchievementEngine()
    try:
        stats = engine.collect_stats_from_db()
    except Exception as e:
        logger.warning("Achievement stats collection failed: %s", e)
        return []  # Graceful degradation if stats collection fails

    already_unlocked = get_unlocked_keys()
    newly = engine.check_all(stats, already_unlocked)

    unlocked_list = []
    for ach in newly:
        was_new = unlock_achievement(ach['key'], progress=ach['progress'])
        if was_new:
            # Enrich with full definition
            defn = ACHIEVEMENT_MAP.get(ach['key'])
            if defn:
                unlocked_list.append({
                    'key': ach['key'],
                    'name': defn.name,
                    'description': defn.description,
                    'icon': defn.icon,
                    'tier': defn.tier,
                })
    return unlocked_list


@router.get("/achievements")
async def get_achievements():
    """Get all achievements with current unlock status and progress.

    Returns the complete achievement catalog with:
    - Which achievements are unlocked
    - Current progress towards locked achievements
    - Total unlocked count and categorized breakdown
    """
    from engines.learning.achievements import AchievementEngine, ACHIEVEMENTS

    engine = AchievementEngine()
    try:
        stats = engine.collect_stats_from_db()
    except Exception as e:
        logger.warning("Achievement catalog stats collection failed: %s", e)
        stats = {
            'mastered_count': 0, 'learning_count': 0, 'total_concepts': 0,
            'current_streak': 0, 'longest_streak': 0, 'total_assessments': 0,
            'highest_score': 0, 'high_scores_90': 0, 'perfect_scores': 0,
            'total_reviews': 0, 'domains_started': 0, 'domains_mastered_5': 0,
            'domains_mastered_10': 0, 'mastered_today': 0, 'mastered_milestones': 0,
            'total_study_time_sec': 0,
        }

    unlocked_map = get_unlocked_map()
    all_achievements = engine.get_all_with_status(stats, unlocked_map)

    # Category breakdown
    categories = {}
    for ach in all_achievements:
        cat = ach['category']
        if cat not in categories:
            categories[cat] = {'total': 0, 'unlocked': 0}
        categories[cat]['total'] += 1
        if ach['unlocked']:
            categories[cat]['unlocked'] += 1

    return {
        "total": len(ACHIEVEMENTS),
        "unlocked_count": len(unlocked_map),
        "categories": categories,
        "achievements": all_achievements,
    }


@router.get("/achievements/recent")
async def get_recent_achievements():
    """Get recently unlocked achievements that haven't been seen yet.

    Designed for toast/popup notifications in the frontend.
    """
    from engines.learning.achievements import ACHIEVEMENT_MAP

    unseen = get_unseen_achievements()
    results = []
    for row in unseen:
        defn = ACHIEVEMENT_MAP.get(row['achievement_key'])
        if defn:
            results.append({
                'key': row['achievement_key'],
                'name': defn.name,
                'description': defn.description,
                'icon': defn.icon,
                'tier': defn.tier,
                'unlocked_at': row['unlocked_at'],
            })
    return {"unseen_count": len(results), "achievements": results}


@router.post("/achievements/seen")
async def mark_seen(req: MarkSeenRequest):
    """Mark achievements as seen (dismiss notifications)."""
    count = mark_achievements_seen(req.keys)
    return {"success": True, "marked_count": count}
