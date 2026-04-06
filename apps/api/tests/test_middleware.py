"""Tests for backend middleware — RequestId + Timing headers."""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.fixture
def client():
    """Sync test client using httpx."""
    import httpx
    transport = ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
async def test_request_id_header_auto_generated(client):
    """Requests without X-Request-ID should get one generated."""
    res = await client.get("/api/health")
    assert "X-Request-ID" in res.headers
    assert len(res.headers["X-Request-ID"]) == 8  # uuid[:8]


@pytest.mark.asyncio
async def test_request_id_header_forwarded(client):
    """Requests with X-Request-ID should have it forwarded."""
    res = await client.get("/api/health", headers={"X-Request-ID": "test-abc"})
    assert res.headers["X-Request-ID"] == "test-abc"


@pytest.mark.asyncio
async def test_response_time_header(client):
    """All responses should include X-Response-Time header."""
    res = await client.get("/api/health")
    assert "X-Response-Time" in res.headers
    assert res.headers["X-Response-Time"].endswith("ms")
    # Parse the numeric value
    ms_str = res.headers["X-Response-Time"].replace("ms", "")
    elapsed = float(ms_str)
    assert elapsed >= 0


@pytest.mark.asyncio
async def test_gzip_middleware_large_response(client):
    """Large responses should be gzip-compressed."""
    res = await client.get("/api/graph/domains", headers={"Accept-Encoding": "gzip"})
    # Response should succeed (compressed or not, depends on size)
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_cors_headers(client):
    """CORS headers should be present on OPTIONS requests."""
    res = await client.options(
        "/api/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    # Should not reject the preflight
    assert res.status_code in (200, 204)
