"""Notifications API — In-app notification center for learning events.

Generates notifications for: mastery achievements, streak milestones,
new discussion replies, content feedback responses, weekly report availability.
In-memory store (Supabase-ready: will map to `notifications` table).
"""

import time
import uuid
from enum import Enum
from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


class NotificationType(str, Enum):
    mastery = "mastery"              # Concept mastered
    streak = "streak"                # Streak milestone (7/14/30/60/90/180/365)
    review_due = "review_due"        # FSRS reviews available
    discussion_reply = "discussion_reply"  # Someone replied to your discussion
    content_feedback = "content_feedback"  # Response to your content feedback
    weekly_report = "weekly_report"  # Weekly learning report ready
    milestone = "milestone"          # Domain milestone (25%/50%/75%/100%)
    recommendation = "recommendation"  # New domain/concept recommendation


class NotificationCreate(BaseModel):
    type: NotificationType
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=1000)
    link: Optional[str] = Field(None, max_length=500, description="Deep-link URL path")
    metadata: Optional[dict] = Field(None, description="Extra data (concept_id, domain_id, etc.)")


# In-memory notification store (keyed by notification ID)
_notifications: dict[str, dict] = {}
_MAX_NOTIFICATIONS = 500  # FIFO eviction when exceeded (#59)


def create_notification(
    ntype: NotificationType,
    title: str,
    message: str,
    link: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> dict:
    """Programmatic helper to create a notification (callable from other routers)."""
    nid = f"notif_{uuid.uuid4().hex[:12]}"
    now = time.time()
    notif = {
        "id": nid,
        "type": ntype,
        "title": title,
        "message": message,
        "link": link,
        "metadata": metadata or {},
        "created_at": now,
        "read": False,
        "read_at": None,
    }
    _notifications[nid] = notif
    # Evict oldest if over capacity (#59)
    if len(_notifications) > _MAX_NOTIFICATIONS:
        oldest_id = min(_notifications, key=lambda k: _notifications[k]["created_at"])
        del _notifications[oldest_id]
    logger.info("Notification created", extra={"id": nid, "type": ntype, "title": title})
    return notif


@router.get("/notifications")
async def list_notifications(
    unread_only: bool = Query(False, description="Only return unread notifications"),
    type: Optional[NotificationType] = None,
    limit: int = Query(30, ge=1, le=100),
    offset: int = 0,
):
    """List notifications with optional filters.

    Returns newest-first sorted notifications with unread count.
    """
    items = list(_notifications.values())

    if unread_only:
        items = [n for n in items if not n["read"]]
    if type:
        items = [n for n in items if n["type"] == type]

    items.sort(key=lambda n: -n["created_at"])
    total = len(items)
    unread_count = sum(1 for n in _notifications.values() if not n["read"])

    return {
        "notifications": items[offset:offset + limit],
        "total": total,
        "unread_count": unread_count,
        "offset": offset,
    }


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str):
    """Mark a single notification as read."""
    if notification_id not in _notifications:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Notification not found")

    _notifications[notification_id]["read"] = True
    _notifications[notification_id]["read_at"] = time.time()
    return _notifications[notification_id]


@router.post("/notifications/read-all")
async def mark_all_read():
    """Mark all notifications as read."""
    now = time.time()
    count = 0
    for n in _notifications.values():
        if not n["read"]:
            n["read"] = True
            n["read_at"] = now
            count += 1
    return {"marked_read": count}


@router.delete("/notifications/{notification_id}")
async def dismiss_notification(notification_id: str):
    """Dismiss (delete) a notification."""
    if notification_id not in _notifications:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Notification not found")

    del _notifications[notification_id]
    return {"dismissed": notification_id}


@router.get("/notifications/summary")
async def notification_summary():
    """Get notification counts by type + unread total.

    Useful for displaying badge counts on navigation icons.
    """
    by_type: dict[str, int] = {}
    unread_by_type: dict[str, int] = {}
    total_unread = 0

    for n in _notifications.values():
        ntype = n["type"]
        by_type[ntype] = by_type.get(ntype, 0) + 1
        if not n["read"]:
            total_unread += 1
            unread_by_type[ntype] = unread_by_type.get(ntype, 0) + 1

    return {
        "total": len(_notifications),
        "unread": total_unread,
        "by_type": by_type,
        "unread_by_type": unread_by_type,
    }


@router.post("/notifications/generate")
async def generate_notifications():
    """Generate sample notifications for testing/demo.

    Creates one notification of each type to populate the notification center.
    """
    samples = [
        (NotificationType.mastery, "概念已掌握!", "你已掌握 'Binary Search' — 继续保持!", "/domain/algorithms/binary-search", {"concept_id": "binary-search", "domain_id": "algorithms"}),
        (NotificationType.streak, "连续学习 7 天!", "太棒了! 你已经连续学习 7 天。继续保持这个势头!", "/dashboard", {"streak_days": 7}),
        (NotificationType.review_due, "有复习任务", "你有 5 个概念需要复习，保持记忆效果。", "/review", {"review_count": 5}),
        (NotificationType.milestone, "领域里程碑!", "恭喜! 你已完成 'Algorithms' 领域 50% 的内容。", "/domain/algorithms", {"domain_id": "algorithms", "percentage": 50}),
        (NotificationType.weekly_report, "周报已生成", "查看你本周的学习成果和进步趋势。", "/report", {}),
        (NotificationType.recommendation, "新领域推荐", "基于你的学习历史，推荐探索 'Data Science' 领域。", "/domain/data-science", {"domain_id": "data-science"}),
    ]

    created = []
    for ntype, title, message, link, meta in samples:
        notif = create_notification(ntype, title, message, link, meta)
        created.append(notif)

    return {"generated": len(created), "notifications": created}
