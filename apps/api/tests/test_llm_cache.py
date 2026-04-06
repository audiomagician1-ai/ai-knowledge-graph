"""llm/cache.py tests — cache key generation, get/set, stats, graceful degradation"""

import pytest
from unittest.mock import AsyncMock, patch


class TestBuildCacheKey:
    """Test deterministic cache key generation"""

    def test_same_input_same_key(self):
        from llm.cache import build_cache_key
        msgs = [{"role": "user", "content": "hello"}]
        k1 = build_cache_key("gpt-4", msgs, 0.7, 2048)
        k2 = build_cache_key("gpt-4", msgs, 0.7, 2048)
        assert k1 == k2

    def test_different_model_different_key(self):
        from llm.cache import build_cache_key
        msgs = [{"role": "user", "content": "hello"}]
        k1 = build_cache_key("gpt-4", msgs, 0.7, 2048)
        k2 = build_cache_key("gpt-3.5", msgs, 0.7, 2048)
        assert k1 != k2

    def test_different_messages_different_key(self):
        from llm.cache import build_cache_key
        k1 = build_cache_key("gpt-4", [{"role": "user", "content": "a"}], 0.7, 2048)
        k2 = build_cache_key("gpt-4", [{"role": "user", "content": "b"}], 0.7, 2048)
        assert k1 != k2

    def test_different_temperature_different_key(self):
        from llm.cache import build_cache_key
        msgs = [{"role": "user", "content": "hello"}]
        k1 = build_cache_key("gpt-4", msgs, 0.7, 2048)
        k2 = build_cache_key("gpt-4", msgs, 0.2, 2048)
        assert k1 != k2

    def test_key_has_prefix(self):
        from llm.cache import build_cache_key, PREFIX
        msgs = [{"role": "user", "content": "hello"}]
        key = build_cache_key("gpt-4", msgs, 0.7, 2048)
        assert key.startswith(PREFIX)

    def test_key_length_consistent(self):
        from llm.cache import build_cache_key, PREFIX
        msgs = [{"role": "user", "content": "hello world " * 100}]
        key = build_cache_key("gpt-4", msgs, 0.7, 2048)
        # PREFIX + 16 hex chars
        assert len(key) == len(PREFIX) + 16


class TestGetCachedResponse:
    """Test cache retrieval with graceful degradation"""

    @pytest.mark.asyncio
    async def test_cache_hit(self):
        from llm.cache import get_cached_response
        with patch("llm.cache.redis_client") as mock_rc:
            mock_rc.get_cached = AsyncMock(return_value="cached response")
            result = await get_cached_response("llm:v1:abc123")
            assert result == "cached response"

    @pytest.mark.asyncio
    async def test_cache_miss(self):
        from llm.cache import get_cached_response
        with patch("llm.cache.redis_client") as mock_rc:
            mock_rc.get_cached = AsyncMock(return_value=None)
            result = await get_cached_response("llm:v1:abc123")
            assert result is None

    @pytest.mark.asyncio
    async def test_cache_error_returns_none(self):
        from llm.cache import get_cached_response
        with patch("llm.cache.redis_client") as mock_rc:
            mock_rc.get_cached = AsyncMock(side_effect=Exception("redis down"))
            result = await get_cached_response("llm:v1:abc123")
            assert result is None


class TestSetCachedResponse:
    """Test cache storage"""

    @pytest.mark.asyncio
    async def test_set_with_ttl(self):
        from llm.cache import set_cached_response
        with patch("llm.cache.redis_client") as mock_rc:
            mock_rc.set_cached = AsyncMock()
            await set_cached_response("llm:v1:abc", "response", ttl=3600)
            mock_rc.set_cached.assert_awaited_once_with("llm:v1:abc", "response", ttl=3600)

    @pytest.mark.asyncio
    async def test_set_default_ttl(self):
        from llm.cache import set_cached_response, DEFAULT_TTL
        with patch("llm.cache.redis_client") as mock_rc:
            mock_rc.set_cached = AsyncMock()
            await set_cached_response("llm:v1:abc", "response")
            mock_rc.set_cached.assert_awaited_once_with("llm:v1:abc", "response", ttl=DEFAULT_TTL)

    @pytest.mark.asyncio
    async def test_set_error_no_raise(self):
        from llm.cache import set_cached_response
        with patch("llm.cache.redis_client") as mock_rc:
            mock_rc.set_cached = AsyncMock(side_effect=Exception("redis down"))
            await set_cached_response("llm:v1:abc", "response")  # Should not raise


class TestInvalidate:
    """Test cache invalidation"""

    @pytest.mark.asyncio
    async def test_invalidate_existing(self):
        from llm.cache import invalidate
        with patch("llm.cache.redis_client") as mock_rc:
            mock_rc.delete_cached = AsyncMock(return_value=True)
            result = await invalidate("llm:v1:abc")
            assert result is True

    @pytest.mark.asyncio
    async def test_invalidate_missing(self):
        from llm.cache import invalidate
        with patch("llm.cache.redis_client") as mock_rc:
            mock_rc.delete_cached = AsyncMock(return_value=False)
            result = await invalidate("llm:v1:abc")
            assert result is False


class TestGetStats:
    """Test stats reporting"""

    def test_stats_structure(self):
        from llm.cache import get_stats
        stats = get_stats()
        assert "hits" in stats
        assert "misses" in stats
        assert "errors" in stats
        assert "total" in stats
        assert "hit_rate_pct" in stats