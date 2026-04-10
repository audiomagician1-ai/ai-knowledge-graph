"""Community Discussions API — Concept-level Q&A and social learning threads.

V2.8: Concept discussions with voting, replies, and resolution tracking.
Split from community.py (V2.12) to maintain module size limits.
"""

import time
import uuid
from enum import Enum
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


class DiscussionType(str, Enum):
    question = "question"       # Ask a question about a concept
    insight = "insight"         # Share a learning insight
    resource = "resource"       # Share a helpful resource
    explanation = "explanation"  # Alternative explanation


class DiscussionCreate(BaseModel):
    concept_id: str = Field(..., min_length=1, max_length=200)
    domain_id: Optional[str] = Field(None, max_length=100)
    type: DiscussionType = DiscussionType.question
    title: str = Field(..., min_length=3, max_length=300)
    content: str = Field(..., min_length=5, max_length=5000)


class ReplyCreate(BaseModel):
    content: str = Field(..., min_length=2, max_length=3000)


# In-memory discussion store (Supabase-ready)
_discussions: dict[str, dict] = {}
_replies: dict[str, list[dict]] = {}  # discussion_id -> [replies]
_vote_tracking: dict[str, set] = {}  # discussion_id -> set of voter tokens (#60)


@router.post("/community/discussions")
async def create_discussion(req: DiscussionCreate):
    """Create a new concept discussion thread.

    Allows users to ask questions, share insights, suggest resources,
    or provide alternative explanations for concepts.
    """
    disc_id = f"disc_{uuid.uuid4().hex[:12]}"
    now = time.time()

    discussion = {
        "id": disc_id,
        "concept_id": req.concept_id,
        "domain_id": req.domain_id,
        "type": req.type,
        "title": req.title,
        "content": req.content,
        "created_at": now,
        "updated_at": now,
        "votes": 0,
        "reply_count": 0,
        "resolved": False,
    }

    _discussions[disc_id] = discussion
    _replies[disc_id] = []
    logger.info("Discussion created", extra={"id": disc_id, "concept_id": req.concept_id, "type": req.type})
    return discussion


@router.get("/community/discussions")
async def list_discussions(
    concept_id: Optional[str] = None,
    domain_id: Optional[str] = None,
    type: Optional[DiscussionType] = None,
    sort: str = Query("recent", description="Sort: recent | popular | active"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = 0,
):
    """List discussions with optional filters.

    Sort options:
    - recent: newest first
    - popular: most votes first
    - active: most replies first
    """
    items = list(_discussions.values())

    if concept_id:
        items = [d for d in items if d["concept_id"] == concept_id]
    if domain_id:
        items = [d for d in items if d.get("domain_id") == domain_id]
    if type:
        items = [d for d in items if d["type"] == type]

    if sort == "popular":
        items.sort(key=lambda d: (-d["votes"], -d["created_at"]))
    elif sort == "active":
        items.sort(key=lambda d: (-d["reply_count"], -d["updated_at"]))
    else:  # recent
        items.sort(key=lambda d: -d["created_at"])

    return {
        "discussions": items[offset:offset + limit],
        "total": len(items),
        "offset": offset,
    }


@router.get("/community/discussions/{discussion_id}")
async def get_discussion(discussion_id: str):
    """Get a discussion thread with its replies."""
    if discussion_id not in _discussions:
        raise HTTPException(status_code=404, detail="Discussion not found")

    disc = _discussions[discussion_id]
    replies = _replies.get(discussion_id, [])

    return {
        **disc,
        "replies": sorted(replies, key=lambda r: r["created_at"]),
    }


@router.post("/community/discussions/{discussion_id}/reply")
async def reply_to_discussion(discussion_id: str, req: ReplyCreate):
    """Add a reply to a discussion thread."""
    if discussion_id not in _discussions:
        raise HTTPException(status_code=404, detail="Discussion not found")

    reply_id = f"reply_{uuid.uuid4().hex[:12]}"
    now = time.time()

    reply = {
        "id": reply_id,
        "discussion_id": discussion_id,
        "content": req.content,
        "created_at": now,
        "votes": 0,
        "is_accepted": False,
    }

    _replies.setdefault(discussion_id, []).append(reply)
    _discussions[discussion_id]["reply_count"] += 1
    _discussions[discussion_id]["updated_at"] = now

    logger.info("Reply added", extra={"discussion_id": discussion_id, "reply_id": reply_id})
    return reply


@router.post("/community/discussions/{discussion_id}/vote")
async def vote_discussion(discussion_id: str, voter_token: str = Query("anon", max_length=100)):
    """Upvote a discussion (+1). Deduplicates by voter_token (#60)."""
    if discussion_id not in _discussions:
        raise HTTPException(status_code=404, detail="Discussion not found")
    voters = _vote_tracking.setdefault(discussion_id, set())
    if voter_token in voters:
        return {"id": discussion_id, "votes": _discussions[discussion_id]["votes"], "already_voted": True}
    voters.add(voter_token)
    _discussions[discussion_id]["votes"] += 1
    return {"id": discussion_id, "votes": _discussions[discussion_id]["votes"], "already_voted": False}


@router.patch("/community/discussions/{discussion_id}/resolve")
async def resolve_discussion(discussion_id: str):
    """Mark a discussion as resolved (question answered)."""
    if discussion_id not in _discussions:
        raise HTTPException(status_code=404, detail="Discussion not found")
    _discussions[discussion_id]["resolved"] = True
    _discussions[discussion_id]["updated_at"] = time.time()
    return _discussions[discussion_id]


@router.get("/community/discussions/concept-activity/{concept_id}")
async def concept_discussion_activity(concept_id: str):
    """Get discussion activity summary for a concept.

    Useful for showing discussion badges/counts on concept cards.
    """
    related = [d for d in _discussions.values() if d["concept_id"] == concept_id]

    return {
        "concept_id": concept_id,
        "total_discussions": len(related),
        "questions": sum(1 for d in related if d["type"] == "question"),
        "insights": sum(1 for d in related if d["type"] == "insight"),
        "resources": sum(1 for d in related if d["type"] == "resource"),
        "explanations": sum(1 for d in related if d["type"] == "explanation"),
        "total_replies": sum(d["reply_count"] for d in related),
        "unresolved_questions": sum(1 for d in related if d["type"] == "question" and not d["resolved"]),
        "recent": sorted(related, key=lambda d: -d["created_at"])[:3],
    }
