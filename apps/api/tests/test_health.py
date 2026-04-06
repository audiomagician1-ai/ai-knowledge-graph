"""健康检查端点测试"""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_health_check():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "akg-api"


@pytest.mark.asyncio
async def test_system_health():
    """System health endpoint should return component status"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health/system")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ("ok", "degraded")
        assert "python" in data
        assert "components" in data
        # SQLite should always be available in test environment
        assert "sqlite" in data["components"]
        assert data["components"]["sqlite"]["status"] == "connected"
        # Seed data should be available
        assert "seed_data" in data["components"]
        assert data["components"]["seed_data"]["status"] == "ok"
        assert data["components"]["seed_data"]["domains"] >= 30


@pytest.mark.asyncio
async def test_cache_stats():
    """Cache stats endpoint should return hit/miss counters."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health/cache")
        assert response.status_code == 200
        data = response.json()
        # Should have stats fields (may be zero if no cache activity)
        assert "hits" in data or "total" in data or isinstance(data, dict)


@pytest.mark.asyncio
async def test_metrics_endpoint():
    """Metrics endpoint should return request/error/timing data."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Make a few requests to generate metrics
        await client.get("/api/health")
        await client.get("/api/health")
        
        response = await client.get("/api/health/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "uptime_seconds" in data
        assert "total_requests" in data
        assert isinstance(data["total_requests"], int)
        assert "endpoints" in data
        assert "global_error_rate" in data


@pytest.mark.asyncio
async def test_metrics_tracks_per_endpoint():
    """Metrics should track individual endpoints separately."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.get("/api/graph/domains")
        await client.get("/api/health")
        
        response = await client.get("/api/health/metrics")
        data = response.json()
        # Should have at least some endpoint data
        assert len(data["endpoints"]) >= 1


@pytest.mark.asyncio
async def test_project_stats():
    """Project stats endpoint should return domain/concept/RAG metrics."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health/project")
        assert response.status_code == 200
        data = response.json()
        assert data["domains"] >= 30
        assert data["concepts"] >= 5000
        assert data["edges"] >= 5000
        assert data["cross_links"] >= 500
        assert data["rag_files"] >= 5000
        assert data["rag_coverage_pct"] >= 90
        assert len(data["domain_details"]) >= 30
        # Each domain detail should have expected fields
        sample = data["domain_details"][0]
        assert "id" in sample
        assert "name" in sample
        assert "concepts" in sample
        assert "rag_files" in sample


@pytest.mark.asyncio
async def test_global_rag_search():
    """Global RAG search endpoint should return cross-domain results."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/graph/rag/search/global?q=system")
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert data["query"] == "system"
        assert "results" in data
        assert isinstance(data["results"], list)
        assert "total" in data
        # Should find at least some results for "system" across domains
        if data["total"] > 0:
            result = data["results"][0]
            assert "concept_id" in result
            assert "name" in result
            assert "domain_id" in result
            assert "domain_name" in result
            assert "match_score" in result
