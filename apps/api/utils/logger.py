"""
logger.py — Unified Logging Configuration (Vibe Coding Standard)

Centralized logging setup for the FastAPI backend.
All modules should use: `from utils.logger import get_logger`

Features:
- Structured format with timestamps and module names
- Environment-based level control (LOG_LEVEL env var)
- Consistent format across all modules
- Ring buffer for recent log retrieval (diagnostics)

Usage:
    from utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Server started", extra={"port": 8000})
"""

import logging
import os
from collections import deque
from typing import Optional


# ── Config ─────────────────────────────────────────────────────────

_LOG_FORMAT = "%(asctime)s [%(levelname)-5s] [%(name)s] %(message)s"
_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"
_BUFFER_SIZE = 500
_configured = False

# Ring buffer for diagnostics
_log_buffer: deque = deque(maxlen=_BUFFER_SIZE)


class _BufferHandler(logging.Handler):
    """Captures log records into a ring buffer for diagnostics."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            entry = {
                "ts": self.format(record),
                "level": record.levelname,
                "module": record.name,
                "msg": record.getMessage(),
            }
            _log_buffer.append(entry)
        except Exception:
            self.handleError(record)


def configure_logging(level: Optional[str] = None) -> None:
    """Configure root logger. Call once at app startup (main.py)."""
    global _configured
    if _configured:
        return

    log_level = (level or os.environ.get("LOG_LEVEL", "INFO")).upper()

    root = logging.getLogger()
    root.setLevel(getattr(logging, log_level, logging.INFO))

    # Console handler
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))
    root.addHandler(console)

    # Buffer handler (no format needed, stores structured data)
    buf_handler = _BufferHandler()
    buf_handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))
    root.addHandler(buf_handler)

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Get a named logger. Auto-configures if not yet configured."""
    if not _configured:
        configure_logging()
    return logging.getLogger(name)


def get_log_buffer() -> list[dict]:
    """Return recent log entries for diagnostics."""
    return list(_log_buffer)


def clear_log_buffer() -> None:
    """Clear the ring buffer."""
    _log_buffer.clear()