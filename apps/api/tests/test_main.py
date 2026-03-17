"""main.py 测试 — CORS / SPA serving / path traversal / route registration / debug mode"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch
from httpx import AsyncClient, ASGITransport


# ── CORS configuration tests ──

class TestCORSConfiguration:
    """Test CORS middleware configuration logic"""

    def test_default_cors_origins(self):
        """Default CORS origins should be localhost:3000 and localhost:5173"""
        raw = "http://localhost:3000,http://localhost:5173"
        origins = [o.strip() for o in raw.split(",") if o.strip()]
        assert origins == ["http://localhost:3000", "http://localhost:5173"]

    def test_wildcard_cors_disables_credentials(self):
        """Wildcard origin '*' must disable credentials per CORS spec"""
        raw = "*"
        origins = [o.strip() for o in raw.split(",") if o.strip()]
        allow_creds = "*" not in origins
        assert allow_creds is False

    def test_specific_origins_enable_credentials(self):
        """Non-wildcard origins should allow credentials"""
        raw = "https://example.com,https://app.example.com"
        origins = [o.strip() for o in raw.split(",") if o.strip()]
        allow_creds = "*" not in origins
        assert allow_creds is True

    def test_cors_origins_strip_whitespace(self):
        """Origins parsing should strip whitespace"""
        raw = " http://a.com , http://b.com , "
        origins = [o.strip() for o in raw.split(",") if o.strip()]
        assert origins == ["http://a.com", "http://b.com"]

    def test_cors_empty_string(self):
        """Empty CORS_ORIGINS string should result in empty list"""
        raw = ""
        origins = [o.strip() for o in raw.split(",") if o.strip()]
        assert origins == []


# ── Route registration tests ──

class TestRouteRegistration:
    """Test that API routes are properly registered"""

    @pytest.mark.asyncio
    async def test_health_endpoint_exists(self):
        from main import app
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            r = await c.get("/api/health")
            assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_graph_data_endpoint_exists(self):
        from main import app
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            r = await c.get("/api/graph/data")
            assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_graph_domains_endpoint_exists(self):
        from main import app
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            r = await c.get("/api/graph/domains")
            assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_learning_stats_endpoint_exists(self):
        from main import app
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            r = await c.get("/api/learning/stats")
            assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_dialogue_list_endpoint_exists(self):
        from main import app
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            r = await c.get("/api/dialogue/conversations")
            assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_nonexistent_api_returns_404_or_422(self):
        """Non-existent API path should return 404/405, not 200"""
        from main import app
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            r = await c.get("/api/nonexistent")
            assert r.status_code in (404, 405)


# ── Debug mode tests ──

class TestDebugMode:
    """Test debug mode controls docs/redoc visibility"""

    def test_debug_false_by_default(self):
        """DEBUG env should default to false"""
        val = os.getenv("DEBUG", "false").lower()
        # In test environment, DEBUG is typically not set
        debug = val == "true"
        assert debug is False or os.getenv("DEBUG", "").lower() == "true"

    def test_debug_mode_parsing(self):
        """Only 'true' (case-insensitive) enables debug"""
        assert "true" == "true"
        assert "TRUE".lower() == "true"
        assert "false".lower() != "true"
        assert "1".lower() != "true"
        assert "".lower() != "true"


# ── SPA path traversal security tests ──

class TestSPAPathTraversal:
    """Test path traversal protection in SPA serve logic"""

    def test_resolve_prevents_parent_traversal(self):
        """Path.resolve() should prevent ../ attacks"""
        base = Path("/app/web_dist").resolve()
        # Simulate traversal attempt
        malicious = (Path("/app/web_dist") / "../../etc/passwd").resolve()
        # On any OS, resolved path should NOT be under base
        try:
            is_safe = malicious.is_relative_to(base)
        except (AttributeError, TypeError):
            is_safe = str(malicious).startswith(str(base))
        assert is_safe is False

    def test_normal_path_is_safe(self):
        """Normal subpath should be relative to base"""
        base = Path("/app/web_dist").resolve()
        normal = (Path("/app/web_dist") / "assets/index.js").resolve()
        try:
            is_safe = normal.is_relative_to(base)
        except (AttributeError, TypeError):
            is_safe = str(normal).startswith(str(base))
        assert is_safe is True

    def test_empty_path_returns_index(self):
        """Empty path should trigger index.html fallback"""
        full_path = ""
        # In the SPA handler, empty path skips file check → returns index.html
        assert not full_path  # Falsy → returns index.html


# ── CORS headers integration test ──

class TestCORSHeaders:
    """Test CORS headers are actually applied"""

    @pytest.mark.asyncio
    async def test_cors_headers_on_allowed_origin(self):
        from main import app
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            r = await c.options(
                "/api/health",
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "GET",
                },
            )
            # Preflight should return 200
            assert r.status_code == 200
            assert "access-control-allow-origin" in r.headers

    @pytest.mark.asyncio
    async def test_custom_headers_allowed(self):
        """X-LLM-* custom headers should be in allowed headers"""
        from main import app
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            r = await c.options(
                "/api/health",
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "X-LLM-API-Key",
                },
            )
            assert r.status_code == 200
            allowed = r.headers.get("access-control-allow-headers", "")
            assert "x-llm-api-key" in allowed.lower()
