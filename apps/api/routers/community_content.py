"""Community Content Feedback API — Content quality reporting and health monitoring.

V2.11: Content quality feedback with categories, resolution tracking, and health dashboard.
Split from community.py (V2.12) to maintain module size limits.
"""

import os
import time
import uuid
from enum import Enum
from typing import Optional

from fastapi import APIRouter, HTTPException, Header, Query
from pydantic import BaseModel, Field
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Admin token for moderation (env var or fallback for testing)
_ADMIN_TOKEN = os.environ.get("COMMUNITY_ADMIN_TOKEN", "akg-admin-2026")


def _check_admin(token: Optional[str]):
    """Validate admin bearer token. Raises 403 if invalid."""
    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization header")
    actual = token.replace("Bearer ", "").strip()
    if actual != _ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Insufficient permissions")


class ContentFeedbackCategory(str, Enum):
    inaccurate = "inaccurate"       # Factually wrong information
    outdated = "outdated"           # Information is out of date
    unclear = "unclear"             # Hard to understand
    incomplete = "incomplete"       # Missing important information
    excellent = "excellent"         # Particularly good content (positive)


class ContentFeedbackCreate(BaseModel):
    concept_id: str = Field(..., min_length=1, max_length=200)
    domain_id: Optional[str] = Field(None, max_length=100)
    category: ContentFeedbackCategory
    comment: Optional[str] = Field(None, max_length=2000)
    rag_doc_path: Optional[str] = Field(None, max_length=500, description="Path to the RAG document")


# In-memory content feedback store
_content_feedback: dict[str, dict] = {}


@router.post("/community/content-feedback")
async def submit_content_feedback(req: ContentFeedbackCreate):
    """Submit quality feedback for RAG content.

    Users can report inaccurate, outdated, unclear, or incomplete content,
    or flag particularly excellent content. Used to build a content health map.
    """
    fb_id = f"cfb_{uuid.uuid4().hex[:12]}"
    now = time.time()

    feedback = {
        "id": fb_id,
        "concept_id": req.concept_id,
        "domain_id": req.domain_id,
        "category": req.category,
        "comment": req.comment,
        "rag_doc_path": req.rag_doc_path,
        "created_at": now,
        "resolved": False,
        "resolved_at": None,
    }

    _content_feedback[fb_id] = feedback
    logger.info("Content feedback submitted", extra={"id": fb_id, "concept_id": req.concept_id, "category": req.category})

    # Trigger notification if notifications module is available
    try:
        from routers.notifications import create_notification, NotificationType
        create_notification(
            NotificationType.content_feedback,
            "内容反馈已收到",
            f"你对 '{req.concept_id}' 的{req.category}反馈已记录，感谢贡献!",
            f"/domain/{req.domain_id}/{req.concept_id}" if req.domain_id else None,
            {"concept_id": req.concept_id, "feedback_id": fb_id},
        )
    except Exception:
        pass  # Notifications are optional

    return feedback


@router.get("/community/content-feedback")
async def list_content_feedback(
    concept_id: Optional[str] = None,
    domain_id: Optional[str] = None,
    category: Optional[ContentFeedbackCategory] = None,
    unresolved_only: bool = False,
    limit: int = Query(50, ge=1, le=200),
    offset: int = 0,
):
    """List content feedback with optional filters."""
    items = list(_content_feedback.values())

    if concept_id:
        items = [f for f in items if f["concept_id"] == concept_id]
    if domain_id:
        items = [f for f in items if f.get("domain_id") == domain_id]
    if category:
        items = [f for f in items if f["category"] == category]
    if unresolved_only:
        items = [f for f in items if not f["resolved"]]

    items.sort(key=lambda f: -f["created_at"])
    return {
        "feedback": items[offset:offset + limit],
        "total": len(items),
        "offset": offset,
    }


@router.patch("/community/content-feedback/{feedback_id}/resolve")
async def resolve_content_feedback(
    feedback_id: str,
    authorization: Optional[str] = Header(None),
):
    """Admin: Mark content feedback as resolved."""
    _check_admin(authorization)

    if feedback_id not in _content_feedback:
        raise HTTPException(status_code=404, detail="Content feedback not found")

    _content_feedback[feedback_id]["resolved"] = True
    _content_feedback[feedback_id]["resolved_at"] = time.time()
    return _content_feedback[feedback_id]


@router.get("/community/content-health")
async def content_health_dashboard(
    domain_id: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
):
    """Content health overview — aggregated feedback per concept.

    Shows which concepts have the most quality issues, helping prioritize
    RAG content improvements. Concepts are ranked by issue severity.
    """
    # Aggregate feedback by concept
    concept_stats: dict[str, dict] = {}

    for fb in _content_feedback.values():
        if domain_id and fb.get("domain_id") != domain_id:
            continue

        cid = fb["concept_id"]
        if cid not in concept_stats:
            concept_stats[cid] = {
                "concept_id": cid,
                "domain_id": fb.get("domain_id"),
                "total_feedback": 0,
                "issues": 0,
                "positive": 0,
                "unresolved": 0,
                "categories": {},
            }

        stats = concept_stats[cid]
        stats["total_feedback"] += 1
        cat = fb["category"]
        stats["categories"][cat] = stats["categories"].get(cat, 0) + 1

        if cat == "excellent":
            stats["positive"] += 1
        else:
            stats["issues"] += 1
            if not fb["resolved"]:
                stats["unresolved"] += 1

    # Score: higher = more urgent (issues - positive, weighted by unresolved)
    for stats in concept_stats.values():
        stats["health_score"] = max(0, 100 - stats["issues"] * 15 + stats["positive"] * 5)
        stats["urgency"] = stats["unresolved"] * 2 + stats["issues"]

    # Sort by urgency descending
    ranked = sorted(concept_stats.values(), key=lambda s: -s["urgency"])[:limit]

    # Global summary
    total_feedback = len(_content_feedback) if not domain_id else sum(
        1 for f in _content_feedback.values() if f.get("domain_id") == domain_id
    )
    total_issues = sum(1 for f in _content_feedback.values()
                       if f["category"] != "excellent"
                       and (not domain_id or f.get("domain_id") == domain_id))
    total_unresolved = sum(1 for f in _content_feedback.values()
                          if not f["resolved"] and f["category"] != "excellent"
                          and (not domain_id or f.get("domain_id") == domain_id))

    return {
        "summary": {
            "total_feedback": total_feedback,
            "total_issues": total_issues,
            "total_unresolved": total_unresolved,
            "concepts_with_issues": len([s for s in concept_stats.values() if s["issues"] > 0]),
        },
        "concepts": ranked,
    }
