"""Community API — User-contributed concept suggestions, feedback, and graph modifications.

MVP: All suggestions are stored in-memory (later → Supabase table with moderation workflow).
Supports: concept suggestion, link suggestion, content feedback.
"""

import time
import uuid
from enum import Enum
from typing import Optional

from fastapi import APIRouter, HTTPException
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


# In-memory store (Supabase-ready: will map to `community_suggestions` table)
_suggestions: dict[str, dict] = {}


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
    }
