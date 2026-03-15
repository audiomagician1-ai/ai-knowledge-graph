"""Redis 缓存客户端"""

import asyncio
import time

import redis.asyncio as redis
from config import settings


class RedisClient:
    def __init__(self):
        self._client: redis.Redis | None = None
        self._reconnect_lock = asyncio.Lock()
        self._last_reconnect: float = 0

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
        """Attempt lazy reconnection with lock + cooldown (max once per 60s)."""
        now = time.time()
        if now - self._last_reconnect < 60:
            return False
        async with self._reconnect_lock:
            # Double-check after acquiring lock
            if time.time() - self._last_reconnect < 60:
                return self._client is not None
            self._last_reconnect = time.time()
            try:
                old_client = self._client
                self._client = redis.from_url(settings.redis_url, decode_responses=True)
                await self._client.ping()
                if old_client:
                    try:
                        await old_client.close()
                    except Exception:
                        pass
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
