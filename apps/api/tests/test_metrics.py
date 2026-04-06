"""Tests for the metrics collector."""
import pytest
from utils.metrics import MetricsCollector


class TestMetricsCollector:
    def setup_method(self):
        self.mc = MetricsCollector()

    def test_record_and_summary(self):
        self.mc.record("/api/health", 200, 5.0)
        self.mc.record("/api/health", 200, 10.0)
        summary = self.mc.get_summary()
        assert summary["total_requests"] == 2
        assert summary["total_errors"] == 0
        assert "/api/health" in summary["endpoints"]
        ep = summary["endpoints"]["/api/health"]
        assert ep["requests"] == 2
        assert ep["avg_ms"] == 7.5

    def test_error_recording(self):
        self.mc.record("/api/graph/data", 200, 5.0)
        self.mc.record("/api/graph/data", 500, 10.0)
        self.mc.record("/api/graph/data", 404, 3.0)
        summary = self.mc.get_summary()
        assert summary["total_errors"] == 2  # 500 + 404
        ep = summary["endpoints"]["/api/graph/data"]
        assert ep["errors"] == 2
        assert ep["error_rate"] == "66.7%"

    def test_min_max_time(self):
        self.mc.record("/api/test", 200, 1.0)
        self.mc.record("/api/test", 200, 100.0)
        self.mc.record("/api/test", 200, 50.0)
        ep = self.mc.get_summary()["endpoints"]["/api/test"]
        assert ep["min_ms"] == 1.0
        assert ep["max_ms"] == 100.0

    def test_reset(self):
        self.mc.record("/api/test", 200, 5.0)
        self.mc.reset()
        summary = self.mc.get_summary()
        assert summary["total_requests"] == 0
        assert len(summary["endpoints"]) == 0

    def test_uptime(self):
        import time
        time.sleep(0.1)
        summary = self.mc.get_summary()
        assert summary["uptime_seconds"] >= 0

    def test_empty_summary(self):
        summary = self.mc.get_summary()
        assert summary["total_requests"] == 0
        assert summary["global_error_rate"] == "0%"

    def test_multiple_endpoints(self):
        self.mc.record("/api/graph/domains", 200, 5.0)
        self.mc.record("/api/learning/progress", 200, 10.0)
        self.mc.record("/api/graph/domains", 200, 3.0)
        summary = self.mc.get_summary()
        assert len(summary["endpoints"]) == 2
        assert summary["endpoints"]["/api/graph/domains"]["requests"] == 2
        assert summary["endpoints"]["/api/learning/progress"]["requests"] == 1

    def test_status_code_tracking(self):
        self.mc.record("/api/test", 200, 5.0)
        self.mc.record("/api/test", 200, 5.0)
        self.mc.record("/api/test", 429, 1.0)
        ep = self.mc._endpoints["/api/test"]
        assert ep.status_codes[200] == 2
        assert ep.status_codes[429] == 1
