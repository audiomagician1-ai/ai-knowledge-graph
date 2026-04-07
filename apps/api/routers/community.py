"""Community API — User-contributed concept suggestions, feedback, and graph modifications.

MVP: All suggestions are stored in-memory (later → Supabase table with moderation workflow).
Supports: concept suggestion, link suggestion, content feedback, admin moderation.
"""

import os
import time
import uuid
from enum import Enum
from typing import Optional

from fastapi import APIRouter, HTTPException, Header
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
