"""Redis 缓存客户端"""

import redis.asyncio as redis
from config import settings


class RedisClient:
    def __init__(self):
        self._client: redis.Redis | None = None

    async def connect(self):
        try:
            self._client = redis.from_url(settings.redis_url, decode_responses=True)
            await self._client.ping()
            print(f"✅ Redis connected: {settings.redis_url}")
        except Exception as e:
            print(f"⚠️ Redis connection failed (will retry on demand): {e}")
            self._client = None

    async def close(self):
        if self._client:
            await self._client.close()
            self._client = None

    @property
    def client(self) -> redis.Redis | None:
        return self._client

    async def _try_reconnect(self) -> bool:
        """Attempt lazy reconnection with cooldown (max once per 60s)."""
        import time
        now = time.time()
        if hasattr(self, '_last_reconnect') and now - self._last_reconnect < 60:
            return False
        self._last_reconnect = now
        try:
            self._client = redis.from_url(settings.redis_url, decode_responses=True)
            await self._client.ping()
            print("✅ Redis reconnected")
            return True
        except Exception:
            self._client = None
            return False

    async def get_cached(self, key: str) -> str | None:
        if not self._client:
            if not await self._try_reconnect():
                return None
        try:
            return await self._client.get(key)
        except Exception:
            self._client = None
            return None

    async def set_cached(self, key: str, value: str, ttl: int = 3600):
        if not self._client:
            if not await self._try_reconnect():
                return
        try:
            await self._client.set(key, value, ex=ttl)
        except Exception:
            self._client = None


redis_client = RedisClient()
