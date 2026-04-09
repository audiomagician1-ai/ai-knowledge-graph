"""Tests for V2.1 analytics endpoints: weekly-report + study-patterns."""

import pytest
from httpx import AsyncClient, ASGITransport

from main import app


@pytest.mark.asyncio
async def test_weekly_report_structure():
    """Weekly report should return this_week/last_week/deltas/overall."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/analytics/weekly-report")
        assert response.status_code == 200
        data = response.json()
        assert "period" in data
        assert "this_week" in data
        assert "last_week" in data
        assert "deltas" in data
        assert "overall" in data
        # this_week should have expected fields
        tw = data["this_week"]
        assert "mastered" in tw
        assert "started" in tw
        assert "assessments" in tw
        assert "active_days" in tw


@pytest.mark.asyncio
async def test_weekly_report_deltas_are_numbers():
    """Deltas should be numeric percentages."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/analytics/weekly-report")
        data = response.json()
        for key, val in data["deltas"].items():
            assert isinstance(val, (int, float)), f"Delta {key} should be numeric, got {type(val)}"


@pytest.mark.asyncio
async def test_weekly_report_overall_fields():
    """Overall section should have totals and streak info."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/analytics/weekly-report")
        data = response.json()
        overall = data["overall"]
        assert "total_mastered" in overall
        assert "total_learning" in overall
        assert "streak_current" in overall
        assert isinstance(overall["total_mastered"], int)


@pytest.mark.asyncio
async def test_study_patterns_structure():
    """Study patterns should return hour/weekday distribution + peaks."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/analytics/study-patterns")
        assert response.status_code == 200
        data = response.json()
        assert "hour_distribution" in data
        assert "weekday_distribution" in data
        assert "peak_hour" in data
        assert "peak_day" in data
        assert "consistency_score" in data


@pytest.mark.asyncio
async def test_study_patterns_hour_distribution_length():
    """Hour distribution should have exactly 24 entries."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/analytics/study-patterns")
        data = response.json()
        assert len(data["hour_distribution"]) == 24


@pytest.mark.asyncio
async def test_study_patterns_weekday_distribution():
    """Weekday distribution should have 7 entries (Chinese day names)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/analytics/study-patterns")
        data = response.json()
        wd = data["weekday_distribution"]
        assert len(wd) == 7
        # Check Chinese day names
        assert "周一" in wd
        assert "周日" in wd


@pytest.mark.asyncio
async def test_study_patterns_custom_days():
    """Study patterns should accept custom day range."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/analytics/study-patterns?days=7")
        assert response.status_code == 200
        data = response.json()
        assert data["period_days"] == 7


@pytest.mark.asyncio
async def test_study_patterns_consistency_score_range():
    """Consistency score should be between 0 and 100."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/analytics/study-patterns")
        data = response.json()
        assert 0 <= data["consistency_score"] <= 100


# ─── V2.4 Batch endpoint tests ───


@pytest.mark.asyncio
async def test_dashboard_batch_returns_all_three():
    """Batch endpoint should return weekly_report + study_patterns + learning_velocity."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/analytics/dashboard-batch")
        assert response.status_code == 200
        data = response.json()
        assert "weekly_report" in data
        assert "study_patterns" in data
        assert "learning_velocity" in data


@pytest.mark.asyncio
async def test_dashboard_batch_weekly_report_matches_individual():
    """Batch weekly_report should match the individual endpoint's schema."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        batch = (await client.get("/api/analytics/dashboard-batch")).json()
        individual = (await client.get("/api/analytics/weekly-report")).json()
        wr = batch["weekly_report"]
        assert wr is not None
        # Same top-level keys
        assert set(wr.keys()) == set(individual.keys())


@pytest.mark.asyncio
async def test_dashboard_batch_study_patterns_matches_individual():
    """Batch study_patterns should match the individual endpoint's schema."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        batch = (await client.get("/api/analytics/dashboard-batch")).json()
        individual = (await client.get("/api/analytics/study-patterns")).json()
        sp = batch["study_patterns"]
        assert sp is not None
        assert set(sp.keys()) == set(individual.keys())


@pytest.mark.asyncio
async def test_dashboard_batch_velocity_matches_individual():
    """Batch learning_velocity should match the individual endpoint's schema."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        batch = (await client.get("/api/analytics/dashboard-batch")).json()
        individual = (await client.get("/api/analytics/learning-velocity?days=14")).json()
        lv = batch["learning_velocity"]
        assert lv is not None
        assert set(lv.keys()) == set(individual.keys())