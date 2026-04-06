"""笔记 API — 概念级学习笔记 CRUD
Supabase-ready: 当前用 SQLite，后续可切换到 Supabase RLS 表"""

import time
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

# In-memory storage (will be replaced by SQLite/Supabase)
# Format: { concept_id: { content, created_at, updated_at } }
_notes_store: dict[str, dict] = {}


class NoteCreate(BaseModel):
    concept_id: str = Field(..., max_length=200)
    content: str = Field(..., max_length=10000)


class NoteUpdate(BaseModel):
    content: str = Field(..., max_length=10000)


class NoteResponse(BaseModel):
    concept_id: str
    content: str
    created_at: float
    updated_at: float


@router.get("/notes", response_model=list[NoteResponse])
async def list_notes(
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
):
    """List all notes, optionally filtered by search query."""
    notes = list(_notes_store.values())

    if search:
        search_lower = search.lower()
        notes = [
            n for n in notes
            if search_lower in n["concept_id"].lower()
            or search_lower in n["content"].lower()
        ]

    # Sort by updated_at descending
    notes.sort(key=lambda n: n["updated_at"], reverse=True)

    return notes[offset:offset + limit]


@router.get("/notes/stats/summary")
async def notes_stats():
    """Get summary statistics about notes."""
    total = len(_notes_store)
    total_chars = sum(len(n["content"]) for n in _notes_store.values())
    return {
        "total_notes": total,
        "total_characters": total_chars,
        "avg_length": total_chars // total if total > 0 else 0,
    }


@router.get("/notes/{concept_id}", response_model=NoteResponse)
async def get_note(concept_id: str):
    """Get note for a specific concept."""
    if concept_id not in _notes_store:
        raise HTTPException(status_code=404, detail=f"Note not found: {concept_id}")
    return _notes_store[concept_id]


@router.post("/notes", response_model=NoteResponse)
async def create_or_update_note(req: NoteCreate):
    """Create or update a note for a concept (upsert)."""
    now = time.time()
    existing = _notes_store.get(req.concept_id)

    note = {
        "concept_id": req.concept_id,
        "content": req.content,
        "created_at": existing["created_at"] if existing else now,
        "updated_at": now,
    }
    _notes_store[req.concept_id] = note
    logger.info("Note saved", extra={"concept_id": req.concept_id, "length": len(req.content)})
    return note


@router.delete("/notes/{concept_id}")
async def delete_note(concept_id: str):
    """Delete a note."""
    if concept_id not in _notes_store:
        raise HTTPException(status_code=404, detail=f"Note not found: {concept_id}")
    del _notes_store[concept_id]
    logger.info("Note deleted", extra={"concept_id": concept_id})
    return {"status": "deleted", "concept_id": concept_id}


@router.post("/notes/bulk")
async def bulk_sync_notes(notes: dict[str, str]):
    """Bulk sync notes from frontend → backend.
    Input: { concept_id: content, ... }"""
    now = time.time()
    synced = 0
    for concept_id, content in notes.items():
        if not content or not content.strip():
            continue
        existing = _notes_store.get(concept_id)
        _notes_store[concept_id] = {
            "concept_id": concept_id,
            "content": content.strip(),
            "created_at": existing["created_at"] if existing else now,
            "updated_at": now,
        }
        synced += 1
    logger.info("Bulk notes sync", extra={"synced": synced})
    return {"status": "ok", "synced": synced, "total": len(_notes_store)}
