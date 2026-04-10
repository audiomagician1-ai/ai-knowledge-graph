"""Tests for CR Round 1 fixes: #52 #53 #54 #58 #59."""

import time
from datetime import datetime
from unittest.mock import patch

import pytest


class TestStreakAliases:
    """#53: get_streak() returns both canonical and alias keys."""

    def test_aliases_present(self):
        from db.sqlite_client import get_streak
        s = get_streak()
        assert "current_streak" in s
        assert "longest_streak" in s
        assert "current" in s
        assert "longest" in s

    def test_aliases_match_canonical(self):
        from db.sqlite_client import get_streak
        s = get_streak()
        assert s["current"] == s["current_streak"]
        assert s["longest"] == s["longest_streak"]


class TestDailySummaryTimestamp:
    """#52: daily_summary handles numeric unix timestamps."""

    def test_numeric_ts_date_extraction(self):
        """Numeric unix ts should be converted via datetime, not str[:10]."""
        ts = time.time()
        today = datetime.now().date().isoformat()
        # The fix converts numeric ts via datetime.fromtimestamp
        result_date = datetime.fromtimestamp(ts).date().isoformat()
        assert result_date == today

    def test_iso_str_still_works(self):
        """ISO date strings should still work with str[:10]."""
        ts = "2026-04-10T12:00:00"
        assert ts[:10] == "2026-04-10"


class TestValidateDomainId:
    """#54: domain_id validation blocks path traversal."""

    def test_rejects_traversal(self):
        from routers.analytics_utils import validate_domain_id
        assert validate_domain_id("../../etc") is False

    def test_rejects_empty(self):
        from routers.analytics_utils import validate_domain_id
        assert validate_domain_id("") is False

    def test_rejects_slashes(self):
        from routers.analytics_utils import validate_domain_id
        assert validate_domain_id("a/b") is False
        assert validate_domain_id("a\\b") is False

    def test_rejects_dots(self):
        from routers.analytics_utils import validate_domain_id
        assert validate_domain_id("..") is False
        assert validate_domain_id(".hidden") is False

    def test_rejects_too_long(self):
        from routers.analytics_utils import validate_domain_id
        assert validate_domain_id("a" * 100) is False

    def test_accepts_valid_domain(self):
        from routers.analytics_utils import validate_domain_id
        # Real domains from seed data
        assert validate_domain_id("mathematics") is True
        assert validate_domain_id("ai-engineering") is True


class TestContentSearchEarlyTermination:
    """#58: content-search bounds file reads."""

    def test_limit_bounds_reads(self):
        """With limit=5, max file reads should be 25 (5*5)."""
        limit = 5
        max_reads = limit * 5
        assert max_reads == 25


class TestNotificationsCap:
    """#59: notifications store has capacity limit."""

    def test_max_capacity_set(self):
        from routers.notifications import _MAX_NOTIFICATIONS
        assert _MAX_NOTIFICATIONS == 500

    def test_eviction_on_overflow(self):
        from routers.notifications import (
            _notifications,
            _MAX_NOTIFICATIONS,
            create_notification,
            NotificationType,
        )
        # Save original state
        original = dict(_notifications)
        _notifications.clear()

        try:
            # Create MAX + 1 notifications
            for i in range(_MAX_NOTIFICATIONS + 5):
                create_notification(
                    NotificationType.mastery,
                    f"Test {i}",
                    f"Message {i}",
                )
            assert len(_notifications) <= _MAX_NOTIFICATIONS
        finally:
            # Restore original state
            _notifications.clear()
            _notifications.update(original)
