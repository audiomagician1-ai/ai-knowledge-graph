"""Tests for V2.5 analytics endpoints: session-history + mastery-timeline + study-time-report."""

import pytest
from httpx import AsyncClient, ASGITransport

from main import app


# ── Session History ──────────────────────────────────────


@pytest.mark.asyncio
async def test_session_history_default():
    """Session history should return paginated items and metadata."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/analytics/session-history")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "pagination" in data
        assert "filters" in data
        p = data["pagination"]
        assert p["page"] == 1
        assert p["per_page"] == 20
        assert isinstance(p["total"], int)
        assert isinstance(p["total_pages"], int)
        assert isinstance(p["has_next"], bool)
        assert isinstance(p["has_prev"], bool)


@pytest.mark.asyncio
async def test_session_history_pagination():
    """Page 1 should have has_prev=False."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/analytics/session-history?page=1&per_page=5")
        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["has_prev"] is False
        assert data["pagination"]["per_page"] == 5


@pytest.mark.asyncio
async def test_session_history_filters():
    """Filters should be echoed in response."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/analytics/session-history?action_filter=mastered&concept_filter=test&days=30"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["filters"]["action"] == "mastered"
        assert data["filters"]["concept"] == "test"
        assert data["filters"]["days"] == 30


@pytest.mark.asyncio
async def test_session_history_items_schema():
    """Each item should have the expected fields."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/analytics/session-history")
        data = response.json()
        for item in data["items"]:
            assert "concept_id" in item
            assert "concept_name" in item
            assert "score" in item
            assert "mastered" in item
            assert "action" in item
            assert "timestamp" in item
            assert "date" in item
            assert "time" in item


# ── Mastery Timeline ─────────────────────────────────────


@pytest.mark.asyncio
async def test_mastery_timeline_nonexistent_concept():
    """Mastery timeline for a nonexistent concept should return empty data."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/analytics/mastery-timeline/nonexistent-concept-xyz")
        assert response.status_code == 200
        data = response.json()
        assert data["concept_id"] == "nonexistent-concept-xyz"
        assert data["data_points"] == []
        assert data["total_sessions"] == 0
        assert data["improvement"] == 0.0
        assert data["first_seen"] is None
        assert data["last_seen"] is None


@pytest.mark.asyncio
async def test_mastery_timeline_structure():
    """Mastery timeline response should have expected fields."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/analytics/mastery-timeline/variables")
        assert response.status_code == 200
        data = response.json()
        assert "concept_id" in data
        assert "data_points" in data
        assert "total_sessions" in data
        assert "current" in data
        assert "improvement" in data
        assert isinstance(data["data_points"], list)
        # current should have status/mastery_score/sessions
        c = data["current"]
        assert "status" in c
        assert "mastery_score" in c
        assert "sessions" in c


# ── Study Time Report ────────────────────────────────────


@pytest.mark.asyncio
async def test_study_time_report_default():
    """Study time report should return daily + summary."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/analytics/study-time-report")
        assert response.status_code == 200
        data = response.json()
        assert "daily" in data
        assert "summary" in data
        assert "period_days" in data
        assert data["period_days"] == 30
        assert isinstance(data["daily"], list)
        assert len(data["daily"]) == 30


@pytest.mark.asyncio
async def test_study_time_report_custom_days():
    """Custom days parameter should affect daily array length."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/analytics/study-time-report?days=7")
        assert response.status_code == 200
        data = response.json()
        assert data["period_days"] == 7
        assert len(data["daily"]) == 7


@pytest.mark.asyncio
async def test_study_time_report_summary_fields():
    """Summary should contain all expected metrics."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/analytics/study-time-report")
        data = response.json()
        s = data["summary"]
        assert "total_minutes" in s
        assert "total_hours" in s
        assert "active_days" in s
        assert "avg_daily_minutes" in s
        assert "avg_weekly_minutes" in s
        assert "total_concepts_touched" in s
        assert "minutes_per_concept" in s


@pytest.mark.asyncio
async def test_study_time_daily_schema():
    """Each daily entry should have date/minutes/concepts_touched."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/analytics/study-time-report?days=7")
        data = response.json()
        for entry in data["daily"]:
            assert "date" in entry
            assert "minutes" in entry
            assert "concepts_touched" in entry
            assert isinstance(entry["minutes"], (int, float))
            assert isinstance(entry["concepts_touched"], int)
