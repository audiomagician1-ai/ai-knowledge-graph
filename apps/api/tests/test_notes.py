"""Tests for Notes API — CRUD + bulk sync + stats."""

import pytest
from httpx import ASGITransport, AsyncClient

from main import app


def _clear_store():
    from routers.notes import _notes_store
    _notes_store.clear()


# ── Create / Upsert ──

@pytest.mark.asyncio
async def test_create_note():
    """POST /api/notes should create a new note."""
    _clear_store()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/notes", json={
            "concept_id": "python-basics",
            "content": "Variables, types, control flow"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["concept_id"] == "python-basics"
        assert data["content"] == "Variables, types, control flow"
        assert data["created_at"] > 0
        assert data["updated_at"] >= data["created_at"]


@pytest.mark.asyncio
async def test_upsert_note_updates_content():
    """POST with same concept_id should update content, keep created_at."""
    _clear_store()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r1 = await client.post("/api/notes", json={
            "concept_id": "loops",
            "content": "for, while loops"
        })
        created_at = r1.json()["created_at"]

        r2 = await client.post("/api/notes", json={
            "concept_id": "loops",
            "content": "for, while, do-while loops"
        })
        data = r2.json()
        assert data["content"] == "for, while, do-while loops"
        assert data["created_at"] == created_at
        assert data["updated_at"] >= created_at


@pytest.mark.asyncio
async def test_create_note_max_length_validation():
    """Content exceeding max_length should be rejected."""
    _clear_store()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/notes", json={
            "concept_id": "test",
            "content": "x" * 10001
        })
        assert resp.status_code == 422


# ── Read ──

@pytest.mark.asyncio
async def test_get_note():
    """GET /api/notes/{concept_id} should return the note."""
    _clear_store()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post("/api/notes", json={
            "concept_id": "recursion",
            "content": "A function that calls itself"
        })
        resp = await client.get("/api/notes/recursion")
        assert resp.status_code == 200
        assert resp.json()["concept_id"] == "recursion"


@pytest.mark.asyncio
async def test_get_note_not_found():
    """GET non-existent note should return 404."""
    _clear_store()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/notes/nonexistent")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_notes_empty():
    """GET /api/notes should return empty list initially."""
    _clear_store()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/notes")
        assert resp.status_code == 200
        assert resp.json() == []


@pytest.mark.asyncio
async def test_list_notes_with_data():
    """GET /api/notes should return all notes sorted by updated_at desc."""
    _clear_store()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post("/api/notes", json={"concept_id": "a", "content": "first"})
        await client.post("/api/notes", json={"concept_id": "b", "content": "second"})
        resp = await client.get("/api/notes")
        data = resp.json()
        assert len(data) == 2
        assert data[0]["concept_id"] == "b"


@pytest.mark.asyncio
async def test_list_notes_search():
    """GET /api/notes?search=... should filter by concept_id or content."""
    _clear_store()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post("/api/notes", json={"concept_id": "python-basics", "content": "vars"})
        await client.post("/api/notes", json={"concept_id": "js-basics", "content": "let const"})

        resp = await client.get("/api/notes?search=python")
        data = resp.json()
        assert len(data) == 1
        assert data[0]["concept_id"] == "python-basics"

        resp2 = await client.get("/api/notes?search=const")
        assert len(resp2.json()) == 1


@pytest.mark.asyncio
async def test_list_notes_pagination():
    """GET /api/notes with limit/offset should paginate."""
    _clear_store()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for i in range(5):
            await client.post("/api/notes", json={"concept_id": f"c-{i}", "content": f"note {i}"})

        resp = await client.get("/api/notes?limit=2&offset=0")
        assert len(resp.json()) == 2

        resp2 = await client.get("/api/notes?limit=2&offset=3")
        assert len(resp2.json()) == 2


# ── Delete ──

@pytest.mark.asyncio
async def test_delete_note():
    """DELETE /api/notes/{concept_id} should remove the note."""
    _clear_store()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post("/api/notes", json={"concept_id": "to-delete", "content": "bye"})
        resp = await client.delete("/api/notes/to-delete")
        assert resp.status_code == 200
        assert resp.json()["status"] == "deleted"

        resp2 = await client.get("/api/notes/to-delete")
        assert resp2.status_code == 404


@pytest.mark.asyncio
async def test_delete_note_not_found():
    """DELETE non-existent note should return 404."""
    _clear_store()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.delete("/api/notes/nonexistent")
        assert resp.status_code == 404


# ── Bulk Sync ──

@pytest.mark.asyncio
async def test_bulk_sync():
    """POST /api/notes/bulk should upsert multiple notes."""
    _clear_store()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/notes/bulk", json={
            "algo-sort": "QuickSort, MergeSort",
            "algo-search": "BFS, DFS, Binary Search",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["synced"] == 2
        assert data["total"] == 2

        r = await client.get("/api/notes/algo-sort")
        assert r.status_code == 200
        assert "QuickSort" in r.json()["content"]


@pytest.mark.asyncio
async def test_bulk_sync_skips_empty():
    """Bulk sync should skip empty content."""
    _clear_store()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/notes/bulk", json={
            "valid": "some content",
            "empty": "",
            "whitespace": "   ",
        })
        data = resp.json()
        assert data["synced"] == 1


# ── Stats ──

@pytest.mark.asyncio
async def test_stats_empty():
    """Stats should return zeros when no notes exist."""
    _clear_store()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/notes/stats/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_notes"] == 0
        assert data["total_characters"] == 0
        assert data["avg_length"] == 0


@pytest.mark.asyncio
async def test_stats_with_data():
    """Stats should reflect note count and character totals."""
    _clear_store()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post("/api/notes", json={"concept_id": "a", "content": "hello"})
        await client.post("/api/notes", json={"concept_id": "b", "content": "world!"})

        resp = await client.get("/api/notes/stats/summary")
        data = resp.json()
        assert data["total_notes"] == 2
        assert data["total_characters"] == 11
        assert data["avg_length"] == 5
