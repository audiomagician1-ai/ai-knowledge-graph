"""Tests for the in-memory sliding-window rate limiter."""

import time
from unittest.mock import MagicMock, patch
import pytest

from rate_limiter import RateLimiter, get_client_ip, check_rate_limit, WINDOW_SECONDS


# ─── RateLimiter core logic ───

class TestRateLimiter:
    def setup_method(self):
        self.rl = RateLimiter()

    def test_allows_request_under_limit(self):
        allowed, info = self.rl.check("test-ip", limit=5)
        assert allowed is True
        assert info["remaining"] == 4
        assert info["limit"] == 5

    def test_allows_up_to_limit(self):
        for i in range(5):
            allowed, info = self.rl.check("test-ip", limit=5)
            assert allowed is True
            assert info["remaining"] == 5 - (i + 1)

    def test_blocks_over_limit(self):
        for _ in range(5):
            self.rl.check("test-ip", limit=5)
        allowed, info = self.rl.check("test-ip", limit=5)
        assert allowed is False
        assert info["remaining"] == 0
        assert info["reset_after"] > 0
        assert info["limit"] == 5

    def test_separate_keys_independent(self):
        """Different IPs should have independent rate limits."""
        for _ in range(5):
            self.rl.check("ip-1", limit=5)
        # ip-1 exhausted
        allowed1, _ = self.rl.check("ip-1", limit=5)
        assert allowed1 is False
        # ip-2 should still be allowed
        allowed2, info2 = self.rl.check("ip-2", limit=5)
        assert allowed2 is True
        assert info2["remaining"] == 4

    def test_window_expiry_allows_new_requests(self):
        """After window expires, requests should be allowed again."""
        # Fill up the bucket
        for _ in range(3):
            self.rl.check("test-ip", limit=3)
        # Verify blocked
        allowed, _ = self.rl.check("test-ip", limit=3)
        assert allowed is False

        # Simulate time passing beyond the window
        now = time.time()
        self.rl._buckets["test-ip"] = [now - WINDOW_SECONDS - 10] * 3  # All expired
        allowed, info = self.rl.check("test-ip", limit=3)
        assert allowed is True
        assert info["remaining"] == 2

    def test_sliding_window_partial_expiry(self):
        """Old requests expire while recent ones count."""
        now = time.time()
        # 2 old (expired) + 1 recent
        self.rl._buckets["test-ip"] = [
            now - WINDOW_SECONDS - 100,  # expired
            now - WINDOW_SECONDS - 50,   # expired
            now - 10,                      # recent
        ]
        allowed, info = self.rl.check("test-ip", limit=3)
        assert allowed is True
        # 1 recent + 1 new = 2 total, limit 3, remaining 1
        assert info["remaining"] == 1

    def test_prune_removes_stale_keys(self):
        """_prune_stale_keys should remove keys with no recent activity."""
        now = time.time()
        self.rl._buckets["active-ip"] = [now - 10]
        self.rl._buckets["stale-ip"] = [now - WINDOW_SECONDS - 100]
        self.rl._last_prune = 0  # Force prune to run

        self.rl._prune_stale_keys(now)
        assert "active-ip" in self.rl._buckets
        assert "stale-ip" not in self.rl._buckets

    def test_prune_skips_within_interval(self):
        """Pruning should not run if within the prune interval."""
        now = time.time()
        self.rl._buckets["stale-ip"] = [now - WINDOW_SECONDS - 100]
        self.rl._last_prune = now - 10  # Recent prune, within 5-min interval

        self.rl._prune_stale_keys(now)
        assert "stale-ip" in self.rl._buckets  # Not pruned

    def test_reset_after_positive(self):
        """reset_after should always be a positive integer."""
        for _ in range(3):
            self.rl.check("test-ip", limit=3)
        _, info = self.rl.check("test-ip", limit=3)
        assert info["reset_after"] > 0
        assert isinstance(info["reset_after"], int)


# ─── get_client_ip ───

class TestGetClientIp:
    def test_x_forwarded_for_single(self):
        req = MagicMock()
        req.headers = {"x-forwarded-for": "203.0.113.50"}
        assert get_client_ip(req) == "203.0.113.50"

    def test_x_forwarded_for_multiple(self):
        req = MagicMock()
        req.headers = {"x-forwarded-for": "203.0.113.50, 70.41.3.18, 150.172.238.178"}
        assert get_client_ip(req) == "203.0.113.50"

    def test_x_forwarded_for_with_spaces(self):
        req = MagicMock()
        req.headers = {"x-forwarded-for": "  10.0.0.1  , 192.168.1.1  "}
        assert get_client_ip(req) == "10.0.0.1"

    def test_fallback_to_client_host(self):
        req = MagicMock()
        req.headers = {}
        req.client.host = "127.0.0.1"
        assert get_client_ip(req) == "127.0.0.1"

    def test_no_client_returns_unknown(self):
        req = MagicMock()
        req.headers = {}
        req.client = None
        assert get_client_ip(req) == "unknown"


# ─── check_rate_limit integration ───

class TestCheckRateLimit:
    def test_byok_user_always_allowed(self):
        """Users with their own API key should never be rate-limited."""
        req = MagicMock()
        req.headers = {}
        req.client.host = "1.2.3.4"
        for _ in range(100):
            allowed, info = check_rate_limit(req, has_user_key=True)
            assert allowed is True
            assert info["remaining"] == -1  # -1 means unlimited

    def test_anon_user_rate_limited(self):
        """Anonymous (free LLM) users should be rate-limited."""
        req = MagicMock()
        req.headers = {}
        req.client.host = "198.51.100.1"

        # Patch ANON_LIMIT to a small number for testing
        with patch("rate_limiter.ANON_LIMIT", 3):
            from rate_limiter import rate_limiter as rl
            # Clear any existing state
            rl._buckets.clear()

            for _ in range(3):
                allowed, _ = check_rate_limit(req, has_user_key=False)
                assert allowed is True

            allowed, info = check_rate_limit(req, has_user_key=False)
            assert allowed is False
            assert info["remaining"] == 0

    def test_different_ips_independent(self):
        """Different IPs should have independent limits."""
        with patch("rate_limiter.ANON_LIMIT", 2):
            from rate_limiter import rate_limiter as rl
            rl._buckets.clear()

            req1 = MagicMock()
            req1.headers = {}
            req1.client.host = "10.0.0.1"

            req2 = MagicMock()
            req2.headers = {}
            req2.client.host = "10.0.0.2"

            # Exhaust req1
            for _ in range(2):
                check_rate_limit(req1, has_user_key=False)
            allowed1, _ = check_rate_limit(req1, has_user_key=False)
            assert allowed1 is False

            # req2 should still have quota
            allowed2, _ = check_rate_limit(req2, has_user_key=False)
            assert allowed2 is True
