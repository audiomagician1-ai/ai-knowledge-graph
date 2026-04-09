"""Community API — User-contributed concept suggestions, feedback, and graph modifications.

MVP: All suggestions are stored in-memory (later → Supabase table with moderation workflow).
Supports: concept suggestion, link suggestion, content feedback, admin moderation.
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


class SuggestionType(str, Enum):
    concept = "concept"           # New concept suggestion
    link = "link"                 # New cross-link suggestion
    correction = "correction"     # Factual correction to existing content
    feedback = "feedback"         # General feedback


class SuggestionStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class SuggestionCreate(BaseModel):
    type: SuggestionType
    domain_id: Optional[str] = Field(None, max_length=100)
    concept_id: Optional[str] = Field(None, max_length=200)
    title: str = Field(..., min_length=3, max_length=300)
    description: str = Field(..., min_length=10, max_length=5000)
    source_concept: Optional[str] = Field(None, max_length=200, description="For link suggestions: source concept")
    target_concept: Optional[str] = Field(None, max_length=200, description="For link suggestions: target concept")


class ModerationAction(BaseModel):
    action: SuggestionStatus = Field(..., description="approve or reject")
    reason: Optional[str] = Field(None, max_length=1000, description="Moderation reason")


class SuggestionResponse(BaseModel):
    id: str
    type: SuggestionType
    status: SuggestionStatus
    domain_id: Optional[str]
    concept_id: Optional[str]
    title: str
    description: str
    source_concept: Optional[str]
    target_concept: Optional[str]
    created_at: float
    votes: int
    moderated_at: Optional[float] = None
    moderation_reason: Optional[str] = None


# In-memory store (Supabase-ready: will map to `community_suggestions` table)
_suggestions: dict[str, dict] = {}

# Admin token for moderation (env var or fallback for testing)
_ADMIN_TOKEN = os.environ.get("COMMUNITY_ADMIN_TOKEN", "akg-admin-2026")


def _check_admin(token: Optional[str]):
    """Validate admin bearer token. Raises 403 if invalid."""
    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization header")
    actual = token.replace("Bearer ", "").strip()
    if actual != _ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Insufficient permissions")


@router.get("/community/suggestions")
async def list_suggestions(
    type: Optional[SuggestionType] = None,
    domain_id: Optional[str] = None,
    status: Optional[SuggestionStatus] = None,
    limit: int = 50,
    offset: int = 0,
):
    """List community suggestions with optional filters."""
    items = list(_suggestions.values())

    if type:
        items = [s for s in items if s["type"] == type]
    if domain_id:
        items = [s for s in items if s.get("domain_id") == domain_id]
    if status:
        items = [s for s in items if s["status"] == status]

    # Sort by votes desc, then created_at desc
    items.sort(key=lambda s: (-s["votes"], -s["created_at"]))
    return items[offset:offset + limit]


@router.post("/community/suggestions", response_model=SuggestionResponse)
async def create_suggestion(req: SuggestionCreate):
    """Submit a new community suggestion."""
    suggestion_id = f"sug_{uuid.uuid4().hex[:12]}"
    now = time.time()

    suggestion = {
        "id": suggestion_id,
        "type": req.type,
        "status": SuggestionStatus.pending,
        "domain_id": req.domain_id,
        "concept_id": req.concept_id,
        "title": req.title,
        "description": req.description,
        "source_concept": req.source_concept,
        "target_concept": req.target_concept,
        "created_at": now,
        "votes": 0,
    }

    _suggestions[suggestion_id] = suggestion
    logger.info("New suggestion", extra={"id": suggestion_id, "type": req.type, "title": req.title})
    return suggestion


@router.get("/community/suggestions/{suggestion_id}", response_model=SuggestionResponse)
async def get_suggestion(suggestion_id: str):
    """Get a specific suggestion by ID."""
    if suggestion_id not in _suggestions:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    return _suggestions[suggestion_id]


@router.post("/community/suggestions/{suggestion_id}/vote")
async def vote_suggestion(suggestion_id: str):
    """Upvote a suggestion (+1)."""
    if suggestion_id not in _suggestions:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    _suggestions[suggestion_id]["votes"] += 1
    return {"id": suggestion_id, "votes": _suggestions[suggestion_id]["votes"]}


@router.patch("/community/suggestions/{suggestion_id}/moderate")
async def moderate_suggestion(
    suggestion_id: str,
    req: ModerationAction,
    authorization: Optional[str] = Header(None),
):
    """Admin: approve or reject a suggestion."""
    _check_admin(authorization)

    if suggestion_id not in _suggestions:
        raise HTTPException(status_code=404, detail="Suggestion not found")

    if req.action not in (SuggestionStatus.approved, SuggestionStatus.rejected):
        raise HTTPException(status_code=400, detail="Action must be 'approved' or 'rejected'")

    s = _suggestions[suggestion_id]
    s["status"] = req.action
    s["moderated_at"] = time.time()
    s["moderation_reason"] = req.reason

    logger.info(
        "Suggestion moderated",
        extra={"id": suggestion_id, "action": req.action, "reason": req.reason},
    )
    return s


@router.get("/community/moderation/queue")
async def moderation_queue(
    authorization: Optional[str] = Header(None),
    limit: int = 50,
):
    """Admin: list pending suggestions for review."""
    _check_admin(authorization)

    pending = [
        s for s in _suggestions.values()
        if s["status"] == SuggestionStatus.pending
    ]
    # Highest votes first (community pre-filter)
    pending.sort(key=lambda s: (-s["votes"], s["created_at"]))
    return pending[:limit]


@router.delete("/community/suggestions/{suggestion_id}")
async def delete_suggestion(
    suggestion_id: str,
    authorization: Optional[str] = Header(None),
):
    """Admin: permanently delete a suggestion."""
    _check_admin(authorization)

    if suggestion_id not in _suggestions:
        raise HTTPException(status_code=404, detail="Suggestion not found")

    del _suggestions[suggestion_id]
    logger.info("Suggestion deleted", extra={"id": suggestion_id})
    return {"deleted": suggestion_id}


@router.get("/community/stats")
async def community_stats():
    """Get community activity statistics."""
    total = len(_suggestions)
    by_type = {}
    by_status = {}
    total_votes = 0

    for s in _suggestions.values():
        by_type[s["type"]] = by_type.get(s["type"], 0) + 1
        by_status[s["status"]] = by_status.get(s["status"], 0) + 1
        total_votes += s["votes"]

    return {
        "total_suggestions": total,
        "by_type": by_type,
        "by_status": by_status,
        "total_votes": total_votes,
        "pending_count": by_status.get(SuggestionStatus.pending, 0),
    }


@router.post("/community/suggestions/{suggestion_id}/auto-moderate")
async def auto_moderate_suggestion(
    suggestion_id: str,
    authorization: Optional[str] = Header(None),
):
    """AI-assisted auto-moderation: score a suggestion for quality and relevance.

    Returns a quality_score (0-100) and recommendation (approve/reject/review).
    Uses heuristic rules (no LLM call needed for MVP):
    - Title length and clarity
    - Description depth
    - Spam/duplicate detection
    - Vote count as community signal
    """
    _check_admin(authorization)

    if suggestion_id not in _suggestions:
        raise HTTPException(status_code=404, detail="Suggestion not found")

    s = _suggestions[suggestion_id]
    score = 50  # Base score
    reasons = []

    # Title quality (3-300 chars, longer is better up to a point)
    title_len = len(s.get("title", ""))
    if title_len >= 10:
        score += 10
        reasons.append("descriptive_title")
    elif title_len < 5:
        score -= 15
        reasons.append("title_too_short")

    # Description quality
    desc_len = len(s.get("description", ""))
    if desc_len >= 100:
        score += 15
        reasons.append("detailed_description")
    elif desc_len >= 50:
        score += 8
        reasons.append("adequate_description")
    elif desc_len < 20:
        score -= 10
        reasons.append("description_too_short")

    # Has domain/concept context
    if s.get("domain_id"):
        score += 5
        reasons.append("has_domain_context")
    if s.get("concept_id"):
        score += 5
        reasons.append("has_concept_context")

    # Community signal (votes)
    votes = s.get("votes", 0)
    if votes >= 5:
        score += 15
        reasons.append("strong_community_support")
    elif votes >= 2:
        score += 8
        reasons.append("some_community_support")

    # Spam detection (very basic)
    title_lower = s.get("title", "").lower()
    spam_keywords = ["buy", "sell", "click here", "free money", "http://", "www.", "casino"]
    if any(kw in title_lower for kw in spam_keywords):
        score -= 40
        reasons.append("potential_spam")

    # Type-specific bonuses
    if s.get("type") == "link" and s.get("source_concept") and s.get("target_concept"):
        score += 10
        reasons.append("complete_link_suggestion")
    elif s.get("type") == "correction":
        score += 5  # Corrections are high value
        reasons.append("correction_type_bonus")

    # Clamp score
    score = max(0, min(100, score))

    # Recommendation
    if score >= 70:
        recommendation = "approve"
    elif score >= 40:
        recommendation = "review"  # Needs human review
    else:
        recommendation = "reject"

    result = {
        "suggestion_id": suggestion_id,
        "quality_score": score,
        "recommendation": recommendation,
        "signals": reasons,
        "auto_moderated_at": time.time(),
    }

    logger.info(
        "Auto-moderation complete",
        extra={"id": suggestion_id, "score": score, "recommendation": recommendation},
    )
    return result


@router.post("/community/suggestions/batch-auto-moderate")
async def batch_auto_moderate(
    authorization: Optional[str] = Header(None),
    limit: int = 20,
):
    """Auto-moderate all pending suggestions in batch.

    Returns scored results sorted by quality (best first).
    """
    _check_admin(authorization)

    pending = [
        s for s in _suggestions.values()
        if s["status"] == SuggestionStatus.pending
    ][:limit]

    results = []
    for s in pending:
        # Inline scoring (same logic as single auto-moderate)
        score = 50
        reasons = []

        title_len = len(s.get("title", ""))
        if title_len >= 10:
            score += 10
            reasons.append("descriptive_title")
        elif title_len < 5:
            score -= 15

        desc_len = len(s.get("description", ""))
        if desc_len >= 100:
            score += 15
        elif desc_len >= 50:
            score += 8
        elif desc_len < 20:
            score -= 10

        if s.get("domain_id"):
            score += 5
        if s.get("concept_id"):
            score += 5

        votes = s.get("votes", 0)
        if votes >= 5:
            score += 15
        elif votes >= 2:
            score += 8

        title_lower = s.get("title", "").lower()
        spam_keywords = ["buy", "sell", "click here", "free money", "http://", "www.", "casino"]
        if any(kw in title_lower for kw in spam_keywords):
            score -= 40

        if s.get("type") == "link" and s.get("source_concept") and s.get("target_concept"):
            score += 10
        elif s.get("type") == "correction":
            score += 5

        score = max(0, min(100, score))
        recommendation = "approve" if score >= 70 else ("review" if score >= 40 else "reject")

        results.append({
            "suggestion_id": s["id"],
            "title": s["title"],
            "type": s["type"],
            "quality_score": score,
            "recommendation": recommendation,
            "votes": votes,
        })

    # Sort by quality score descending
    results.sort(key=lambda r: -r["quality_score"])

    return {
        "total_pending": len(pending),
        "results": results,
        "auto_approve_count": sum(1 for r in results if r["recommendation"] == "approve"),
        "review_count": sum(1 for r in results if r["recommendation"] == "review"),
        "reject_count": sum(1 for r in results if r["recommendation"] == "reject"),
    }


@router.get("/community/feedback/{concept_id}")
async def concept_feedback(concept_id: str):
    """Get aggregated feedback for a specific concept."""
    related = [
        s for s in _suggestions.values()
        if s.get("concept_id") == concept_id
    ]

    positive = sum(1 for s in related if "👍" in s.get("title", ""))
    negative = sum(1 for s in related if s["type"] in ("correction", "feedback") and "👍" not in s.get("title", ""))

    return {
        "concept_id": concept_id,
        "total_feedback": len(related),
        "positive": positive,
        "negative": negative,
        "suggestions": [
            {"id": s["id"], "type": s["type"], "title": s["title"], "votes": s["votes"], "status": s["status"]}
            for s in sorted(related, key=lambda x: -x["votes"])[:10]
        ],
    }


# ── V2.8: Concept Discussions (Social Learning) ─────────

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
async def vote_discussion(discussion_id: str):
    """Upvote a discussion (+1)."""
    if discussion_id not in _discussions:
        raise HTTPException(status_code=404, detail="Discussion not found")
    _discussions[discussion_id]["votes"] += 1
    return {"id": discussion_id, "votes": _discussions[discussion_id]["votes"]}


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
