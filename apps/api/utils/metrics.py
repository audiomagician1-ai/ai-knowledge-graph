"""
Simple in-memory metrics collector for API observability.

Tracks:
- Request counts per endpoint
- Error counts per status code
- Average response times per endpoint

Thread-safe for asyncio context. Metrics reset on server restart.
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class EndpointMetrics:
    """Metrics for a single endpoint."""
    request_count: int = 0
    error_count: int = 0
    total_time_ms: float = 0.0
    min_time_ms: float = float('inf')
    max_time_ms: float = 0.0
    status_codes: dict[int, int] = field(default_factory=lambda: defaultdict(int))

    @property
    def avg_time_ms(self) -> float:
        return round(self.total_time_ms / self.request_count, 1) if self.request_count else 0.0

    @property
    def error_rate(self) -> float:
        return round(self.error_count / self.request_count * 100, 1) if self.request_count else 0.0


class MetricsCollector:
    """Global metrics collector singleton."""

    def __init__(self):
        self._endpoints: dict[str, EndpointMetrics] = defaultdict(EndpointMetrics)
        self._start_time = time.time()

    def record(self, path: str, status_code: int, elapsed_ms: float) -> None:
        """Record a completed request."""
        m = self._endpoints[path]
        m.request_count += 1
        m.total_time_ms += elapsed_ms
        m.min_time_ms = min(m.min_time_ms, elapsed_ms)
        m.max_time_ms = max(m.max_time_ms, elapsed_ms)
        m.status_codes[status_code] += 1
        if status_code >= 400:
            m.error_count += 1

    def get_summary(self) -> dict:
        """Get a summary of all metrics."""
        uptime = time.time() - self._start_time
        total_requests = sum(m.request_count for m in self._endpoints.values())
        total_errors = sum(m.error_count for m in self._endpoints.values())

        endpoints = {}
        for path, m in sorted(self._endpoints.items(), key=lambda x: -x[1].request_count):
            endpoints[path] = {
                "requests": m.request_count,
                "errors": m.error_count,
                "error_rate": f"{m.error_rate}%",
                "avg_ms": m.avg_time_ms,
                "min_ms": round(m.min_time_ms, 1) if m.min_time_ms != float('inf') else 0,
                "max_ms": round(m.max_time_ms, 1),
            }

        return {
            "uptime_seconds": int(uptime),
            "total_requests": total_requests,
            "total_errors": total_errors,
            "global_error_rate": f"{round(total_errors / total_requests * 100, 1) if total_requests else 0}%",
            "endpoints": endpoints,
        }

    def reset(self) -> None:
        """Reset all metrics."""
        self._endpoints.clear()
        self._start_time = time.time()


# Global singleton
metrics = MetricsCollector()
