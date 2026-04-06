"""
LLM Response Cache — Redis-backed caching for LLM responses.
Reduces duplicate API calls for identical prompts (e.g., concept openings).

Cache key = hash(model + messages + temperature + max_tokens)
Default TTL: 24 hours (knowledge content changes infrequently)
Graceful degradation: cache miss/error → normal LLM call
"""

import hashlib
import json
from typing import Optional

from db.redis_client import redis_client
from utils.logger import get_logger

logger = get_logger(__name__)

# Default TTL: 24 hours
DEFAULT_TTL = 86400
# Cache key prefix
PREFIX = "llm:v1:"

# Stats counters (in-memory, reset on restart)
_stats = {"hits": 0, "misses": 0, "errors": 0}


def build_cache_key(
    model: str,
    messages: list[dict],
    temperature: float,
    max_tokens: int,
) -> str:
    """Build a deterministic cache key from LLM request params."""
    payload = json.dumps(
        {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
        sort_keys=True,
        ensure_ascii=False,
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    return f"{PREFIX}{digest}"


async def get_cached_response(cache_key: str) -> Optional[str]:
    """Try to get a cached LLM response. Returns None on miss."""
    try:
        cached = await redis_client.get_cached(cache_key)
        if cached is not None:
            _stats["hits"] += 1
            logger.debug("LLM cache HIT: %s", cache_key)
            return cached
        _stats["misses"] += 1
        return None
    except Exception:
        _stats["errors"] += 1
        return None


async def set_cached_response(
    cache_key: str, response: str, ttl: int = DEFAULT_TTL
) -> None:
    """Cache an LLM response."""
    try:
        await redis_client.set_cached(cache_key, response, ttl=ttl)
        logger.debug("LLM cache SET: %s (ttl=%ds)", cache_key, ttl)
    except Exception:
        _stats["errors"] += 1


async def invalidate(cache_key: str) -> bool:
    """Invalidate a specific cache entry."""
    return await redis_client.delete_cached(cache_key)


def get_stats() -> dict:
    """Return cache hit/miss/error stats."""
    total = _stats["hits"] + _stats["misses"]
    hit_rate = (_stats["hits"] / total * 100) if total > 0 else 0.0
    return {**_stats, "total": total, "hit_rate_pct": round(hit_rate, 1)}