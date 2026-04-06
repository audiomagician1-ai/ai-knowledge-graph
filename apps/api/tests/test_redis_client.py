"""redis_client.py 测试 — RedisClient connection, caching, reconnect, graceful degradation"""

import asyncio
import time
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestRedisClientInit:
    """Test RedisClient initialization"""

    def test_initial_state(self):
        from db.redis_client import RedisClient
        rc = RedisClient()
        assert rc._client is None
        assert rc._last_reconnect == 0
        assert rc.client is None

    def test_client_property_returns_none_before_connect(self):
        from db.redis_client import RedisClient
        rc = RedisClient()
        assert rc.client is None


class TestRedisClientConnect:
    """Test connect/close lifecycle"""

    @pytest.mark.asyncio
    async def test_connect_success(self):
        from db.redis_client import RedisClient
        rc = RedisClient()
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(return_value=True)
        with patch("db.redis_client.redis.from_url", return_value=mock_redis):
            await rc.connect()
            assert rc.client is mock_redis
            mock_redis.ping.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_connect_failure_sets_client_none(self):
        from db.redis_client import RedisClient
        rc = RedisClient()
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(side_effect=ConnectionError("refused"))
        with patch("db.redis_client.redis.from_url", return_value=mock_redis):
            await rc.connect()
            assert rc.client is None

    @pytest.mark.asyncio
    async def test_close_clears_client(self):
        from db.redis_client import RedisClient
        rc = RedisClient()
        mock_redis = AsyncMock()
        rc._client = mock_redis
        await rc.close()
        assert rc.client is None
        mock_redis.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_close_noop_when_no_client(self):
        from db.redis_client import RedisClient
        rc = RedisClient()
        await rc.close()  # Should not raise
        assert rc.client is None


class TestRedisClientCaching:
    """Test get_cached / set_cached with graceful degradation"""

    @pytest.mark.asyncio
    async def test_get_cached_returns_value(self):
        from db.redis_client import RedisClient
        rc = RedisClient()
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value="cached_data")
        rc._client = mock_redis
        result = await rc.get_cached("test_key")
        assert result == "cached_data"
        mock_redis.get.assert_awaited_once_with("test_key")

    @pytest.mark.asyncio
    async def test_get_cached_returns_none_on_miss(self):
        from db.redis_client import RedisClient
        rc = RedisClient()
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=None)
        rc._client = mock_redis
        result = await rc.get_cached("missing_key")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_cached_returns_none_when_no_client(self):
        """When Redis is down, get_cached should return None (graceful degradation)"""
        from db.redis_client import RedisClient
        rc = RedisClient()
        rc._last_reconnect = time.time()  # Prevent reconnect attempt
        result = await rc.get_cached("any_key")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_cached_clears_client_on_error(self):
        """On Redis error, client should be set to None for next reconnect"""
        from db.redis_client import RedisClient
        rc = RedisClient()
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(side_effect=ConnectionError("broken pipe"))
        rc._client = mock_redis
        result = await rc.get_cached("test_key")
        assert result is None
        assert rc._client is None  # Cleared for reconnect

    @pytest.mark.asyncio
    async def test_set_cached_with_ttl(self):
        from db.redis_client import RedisClient
        rc = RedisClient()
        mock_redis = AsyncMock()
        rc._client = mock_redis
        await rc.set_cached("key", "value", ttl=300)
        mock_redis.set.assert_awaited_once_with("key", "value", ex=300)

    @pytest.mark.asyncio
    async def test_set_cached_default_ttl(self):
        from db.redis_client import RedisClient
        rc = RedisClient()
        mock_redis = AsyncMock()
        rc._client = mock_redis
        await rc.set_cached("key", "value")
        mock_redis.set.assert_awaited_once_with("key", "value", ex=3600)

    @pytest.mark.asyncio
    async def test_set_cached_noop_when_no_client(self):
        """When Redis is down, set_cached should silently no-op"""
        from db.redis_client import RedisClient
        rc = RedisClient()
        rc._last_reconnect = time.time()  # Prevent reconnect
        await rc.set_cached("key", "value")  # Should not raise

    @pytest.mark.asyncio
    async def test_set_cached_clears_client_on_error(self):
        from db.redis_client import RedisClient
        rc = RedisClient()
        mock_redis = AsyncMock()
        mock_redis.set = AsyncMock(side_effect=ConnectionError("broken"))
        rc._client = mock_redis
        await rc.set_cached("key", "value")
        assert rc._client is None


class TestRedisClientDeleteCached:
    """Test delete_cached method"""

    @pytest.mark.asyncio
    async def test_delete_existing_key(self):
        from db.redis_client import RedisClient
        rc = RedisClient()
        mock_redis = AsyncMock()
        mock_redis.delete = AsyncMock(return_value=1)
        rc._client = mock_redis
        result = await rc.delete_cached("key")
        assert result is True
        mock_redis.delete.assert_awaited_once_with("key")

    @pytest.mark.asyncio
    async def test_delete_missing_key(self):
        from db.redis_client import RedisClient
        rc = RedisClient()
        mock_redis = AsyncMock()
        mock_redis.delete = AsyncMock(return_value=0)
        rc._client = mock_redis
        result = await rc.delete_cached("missing")
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_no_client(self):
        from db.redis_client import RedisClient
        rc = RedisClient()
        rc._last_reconnect = time.time()
        result = await rc.delete_cached("key")
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_error_clears_client(self):
        from db.redis_client import RedisClient
        rc = RedisClient()
        mock_redis = AsyncMock()
        mock_redis.delete = AsyncMock(side_effect=ConnectionError("broken"))
        rc._client = mock_redis
        result = await rc.delete_cached("key")
        assert result is False
        assert rc._client is None


class TestRedisClientReconnect:
    """Test lazy reconnection with cooldown"""

    @pytest.mark.asyncio
    async def test_reconnect_succeeds(self):
        from db.redis_client import RedisClient
        rc = RedisClient()
        rc._last_reconnect = 0  # Long ago — allow reconnect
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(return_value=True)
        with patch("db.redis_client.redis.from_url", return_value=mock_redis):
            result = await rc._try_reconnect()
            assert result is True
            assert rc.client is mock_redis

    @pytest.mark.asyncio
    async def test_reconnect_cooldown_60s(self):
        """Should not attempt reconnect within 60s of last attempt"""
        from db.redis_client import RedisClient
        rc = RedisClient()
        rc._last_reconnect = time.time()  # Just now
        result = await rc._try_reconnect()
        assert result is False

    @pytest.mark.asyncio
    async def test_reconnect_failure_clears_client(self):
        from db.redis_client import RedisClient
        rc = RedisClient()
        rc._last_reconnect = 0
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(side_effect=ConnectionError("refused"))
        with patch("db.redis_client.redis.from_url", return_value=mock_redis):
            result = await rc._try_reconnect()
            assert result is False
            assert rc._client is None

    @pytest.mark.asyncio
    async def test_reconnect_closes_old_client(self):
        """On successful reconnect, old client should be closed"""
        from db.redis_client import RedisClient
        rc = RedisClient()
        rc._last_reconnect = 0
        old_mock = AsyncMock()
        rc._client = old_mock
        new_mock = AsyncMock()
        new_mock.ping = AsyncMock(return_value=True)
        with patch("db.redis_client.redis.from_url", return_value=new_mock):
            result = await rc._try_reconnect()
            assert result is True
            old_mock.close.assert_awaited_once()
            assert rc.client is new_mock

    @pytest.mark.asyncio
    async def test_get_cached_triggers_reconnect(self):
        """get_cached should trigger reconnect when client is None"""
        from db.redis_client import RedisClient
        rc = RedisClient()
        rc._last_reconnect = 0
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(return_value=True)
        mock_redis.get = AsyncMock(return_value="reconnected_value")
        with patch("db.redis_client.redis.from_url", return_value=mock_redis):
            result = await rc.get_cached("key")
            assert result == "reconnected_value"
