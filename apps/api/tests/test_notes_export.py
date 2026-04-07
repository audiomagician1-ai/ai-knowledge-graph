"""Tests for V2.1 notes export endpoints (markdown + JSON)."""

import pytest
from httpx import AsyncClient, ASGITransport

from main import app


@pytest.mark.asyncio
async def test_export_markdown_structure():
    """Export should return proper markdown structure."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/notes/export/markdown")
        assert response.status_code == 200
        data = response.json()
        assert data["format"] == "markdown"
        # Content should be a string containing markdown
        assert isinstance(data["content"], str)
        assert "count" in data


@pytest.mark.asyncio
async def test_export_markdown_with_notes():
    """Export should include all notes in markdown format."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create some notes
        await client.post("/api/notes", json={
            "concept_id": "variables",
            "content": "Variables store data in memory."
        })
        await client.post("/api/notes", json={
            "concept_id": "loops",
            "content": "Loops repeat code blocks."
        })

        response = await client.get("/api/notes/export/markdown")
        data = response.json()
        assert data["format"] == "markdown"
        assert data["count"] >= 2
        assert "Variables" in data["content"]
        assert "Loops" in data["content"]
        assert "filename" in data
        assert data["filename"].endswith(".md")


@pytest.mark.asyncio
async def test_export_json_structure():
    """JSON export should have proper structure."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Ensure at least one note exists
        await client.post("/api/notes", json={
            "concept_id": "test-export-json",
            "content": "Test note for JSON export."
        })

        response = await client.get("/api/notes/export/json")
        assert response.status_code == 200
        data = response.json()
        assert data["format"] == "json"
        assert data["version"] == "1.0"
        assert "exported_at" in data
        assert "count" in data
        assert "notes" in data
        assert isinstance(data["notes"], list)
        assert data["count"] == len(data["notes"])


@pytest.mark.asyncio
async def test_export_json_roundtrip():
    """Notes exported as JSON should be importable back via bulk sync."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create notes
        await client.post("/api/notes", json={"concept_id": "roundtrip-1", "content": "Note 1"})
        await client.post("/api/notes", json={"concept_id": "roundtrip-2", "content": "Note 2"})

        # Export
        export_res = await client.get("/api/notes/export/json")
        exported = export_res.json()
        assert exported["count"] >= 2

        # Simulate re-import via bulk sync
        bulk_data = {n["concept_id"]: n["content"] for n in exported["notes"]}
        import_res = await client.post("/api/notes/bulk", json=bulk_data)
        assert import_res.status_code == 200
        assert import_res.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_export_markdown_sorted():
    """Markdown export should have notes sorted by concept ID."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post("/api/notes", json={"concept_id": "zzz-last", "content": "Last"})
        await client.post("/api/notes", json={"concept_id": "aaa-first", "content": "First"})

        response = await client.get("/api/notes/export/markdown")
        content = response.json()["content"]
        # aaa-first should appear before zzz-last
        assert content.index("Aaa") < content.index("Zzz")
