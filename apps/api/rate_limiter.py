"""
In-memory sliding-window rate limiter for free (server-side) LLM requests.

Design:
- Applies ONLY when using the server-side free LLM (no user API key provided).
- Uses client IP as the rate-limit key for anonymous users.
- Sliding window: counts requests within the last `window_seconds`.
- Configurable via environment variables.
- Thread-safe in asyncio context (single event loop — no concurrent dict mutation).
- Auto-prunes expired entries every check to prevent memory leak.

Limits (configurable via env):
  RATE_LIMIT_ANON_PER_HOUR=30     — anonymous users: 30 LLM calls/hour
  RATE_LIMIT_AUTH_PER_HOUR=100    — authenticated users: 100 LLM calls/hour (future)

BYOK (bring-your-own-key) users are NOT rate-limited — they use their own quotas.
"""

import os
import time
from collections import defaultdict, deque

from utils.logger import get_logger

logger = get_logger(__name__)

# Configuration from environment
ANON_LIMIT = int(os.getenv("RATE_LIMIT_ANON_PER_HOUR", "30"))
AUTH_LIMIT = int(os.getenv("RATE_LIMIT_AUTH_PER_HOUR", "100"))
WINDOW_SECONDS = 3600  # 1 hour sliding window


class RateLimiter:
    """Sliding-window rate limiter keyed by client identifier (IP or user ID)."""

    def __init__(self) -> None:
        # key -> deque of timestamps (deque.popleft is O(1) vs list.pop(0) O(n))
        self._buckets: dict[str, deque[float]] = defaultdict(deque)
        self._last_prune: float = 0.0
        self._PRUNE_INTERVAL = 300  # Prune stale keys every 5 minutes

    def _prune_stale_keys(self, now: float) -> None:
        """Remove keys with no recent activity to prevent unbounded memory growth."""
        if now - self._last_prune < self._PRUNE_INTERVAL:
            return
        self._last_prune = now
        cutoff = now - WINDOW_SECONDS
        stale_keys = [k for k, ts_list in self._buckets.items() if not ts_list or ts_list[-1] < cutoff]
        for k in stale_keys:
            del self._buckets[k]

    def check(self, key: str, limit: int) -> tuple[bool, dict]:
        """Check if the request is allowed under the rate limit.

        Returns:
            (allowed, info) where info contains:
                - remaining: number of remaining requests in the window
                - reset_after: seconds until the oldest request expires
                - limit: the configured limit
        """
        now = time.time()
        self._prune_stale_keys(now)

        # Sliding window: remove timestamps older than the window
        cutoff = now - WINDOW_SECONDS
        bucket = self._buckets[key]
        # Remove expired entries (bucket is append-only so entries are sorted)
        while bucket and bucket[0] < cutoff:
            bucket.popleft()

        count = len(bucket)
        if count >= limit:
            # Rate limit exceeded
            reset_after = bucket[0] + WINDOW_SECONDS - now if bucket else WINDOW_SECONDS
            return False, {
                "remaining": 0,
                "reset_after": int(reset_after) + 1,
                "limit": limit,
            }

        # Allowed — record this request
        bucket.append(now)
        remaining = limit - len(bucket)
        return True, {
            "remaining": remaining,
            "reset_after": int(WINDOW_SECONDS - (now - bucket[0])) + 1 if bucket else WINDOW_SECONDS,
            "limit": limit,
        }


# Global singleton
rate_limiter = RateLimiter()


def get_client_ip(request) -> str:
    """Extract client IP from request, respecting X-Forwarded-For for proxied environments."""
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        # X-Forwarded-For: client, proxy1, proxy2 — use leftmost (original client)
        return forwarded.split(",")[0].strip()
    if hasattr(request, "client") and request.client:
        return request.client.host
    return "unknown"


def check_rate_limit(request, has_user_key: bool) -> tuple[bool, dict]:
    """Check rate limit for a request. Returns (allowed, info).

    Args:
        request: FastAPI Request object
        has_user_key: True if the user provided their own LLM API key (BYOK — not rate-limited)

    Returns:
        (allowed, info) — info contains remaining/reset_after/limit for response headers
    """
    if has_user_key:
        # BYOK users are not rate-limited
        return True, {"remaining": -1, "reset_after": 0, "limit": 0}

    client_ip = get_client_ip(request)
    key = f"anon:{client_ip}"
    limit = ANON_LIMIT

    # Future: if authenticated user, use user_id as key and AUTH_LIMIT
    # auth_user_id = request.state.get("user_id")  # from Supabase JWT middleware
    # if auth_user_id:
    #     key = f"auth:{auth_user_id}"
    #     limit = AUTH_LIMIT

    allowed, info = rate_limiter.check(key, limit)
    if not allowed:
        logger.info(
            "Rate limit exceeded for %s (%s): %d/%d in window",
            key, client_ip, limit, limit,
        )
    return allowed, info
