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
