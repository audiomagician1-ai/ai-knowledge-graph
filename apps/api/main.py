"""
AI Knowledge Graph — Backend API
图谱引擎 + 对话引擎 + 学习引擎
支持两种运行模式：
  1. 开发模式: uvicorn main:app --reload （前端由 Vite dev server 提供）
  2. 打包模式: PyInstaller exe  （前端 dist 内嵌，由 FastAPI StaticFiles 提供）
"""

import os
import sys
import uuid
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse
from starlette.middleware.base import BaseHTTPMiddleware

from routers import graph, graph_advanced, graph_topology, dialogue, learning, learning_extended, learning_intelligence, learning_review, health, notes, community, community_discussions, community_content, notifications, analytics, analytics_experience, analytics_profile, analytics_planning, analytics_advanced, analytics_insights, analytics_forecast, analytics_social, analytics_search, onboarding
from utils.logger import configure_logging, get_logger

# Initialize unified logging before anything else
configure_logging()
logger = get_logger(__name__)


def _get_base_dir() -> Path:
    """Get the base directory — works both in dev and PyInstaller frozen mode"""
    if getattr(sys, 'frozen', False):
        # PyInstaller: _MEIPASS is the temp dir for bundled data
        return Path(sys._MEIPASS)
    return Path(__file__).parent


BASE_DIR = _get_base_dir()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理 — DB connections are optional (graceful degradation)"""
    # Startup: initialize SQLite (always available, zero-config)
    try:
        from db.sqlite_client import init_db, DB_PATH
        init_db()
        logger.info("SQLite initialized: %s", DB_PATH)
    except Exception as e:
        logger.error("SQLite init failed: %s", e)

    # Optional: try connecting external DBs but don't crash if unavailable
    try:
        from db.neo4j_client import neo4j_client
        await neo4j_client.connect()
    except Exception as e:
        logger.warning("Neo4j unavailable, using JSON fallback: %s", e)

    try:
        from db.redis_client import redis_client
        await redis_client.connect()
    except Exception as e:
        logger.warning("Redis unavailable, using in-memory sessions: %s", e)

    yield

    # Shutdown
    try:
        from db.neo4j_client import neo4j_client
        await neo4j_client.close()
    except Exception:
        pass
    try:
        from db.redis_client import redis_client
        await redis_client.close()
    except Exception:
        pass
    try:
        from llm.router import llm_router
        await llm_router.close()
    except Exception:
        pass


_debug = os.getenv("DEBUG", "false").lower() == "true"

app = FastAPI(
    title="AI Knowledge Graph API",
    description="费曼对话 + 知识图谱 + 技能树点亮",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if _debug else None,
    redoc_url="/redoc" if _debug else None,
)

# CORS — allow origins from env or default to local dev
_cors_origins_raw = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173")
_cors_origins = [o.strip() for o in _cors_origins_raw.split(",") if o.strip()]
# Wildcard origin + credentials is invalid per CORS spec — disable credentials if "*" present
_allow_credentials = "*" not in _cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=_allow_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "X-LLM-Provider",
        "X-LLM-API-Key",
        "X-LLM-Model",
        "X-LLM-Base-URL",
    ],
)

# GZip compression — reduce response sizes for graph data / RAG documents
# minimum_size=500 avoids compressing tiny health-check responses
app.add_middleware(GZipMiddleware, minimum_size=500)


# ── Request ID + Timing Middleware ──
class RequestIdMiddleware(BaseHTTPMiddleware):
    """Add X-Request-ID header and log request timing for observability."""

    async def dispatch(self, request: Request, call_next):
        from utils.metrics import metrics as api_metrics

        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
        start = time.monotonic()
        response = await call_next(request)
        elapsed_ms = round((time.monotonic() - start) * 1000, 1)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{elapsed_ms}ms"

        # Record metrics for API endpoints
        path = request.url.path
        if path.startswith("/api/"):
            api_metrics.record(path, response.status_code, elapsed_ms)

        # Log slow requests (>500ms)
        if elapsed_ms > 500:
            logger.warning("Slow request: %s %s %sms [%s]",
                           request.method, request.url.path, elapsed_ms, request_id)
        return response


app.add_middleware(RequestIdMiddleware)

# 路由注册
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(graph.router, prefix="/api/graph", tags=["graph"])
app.include_router(graph_advanced.router, prefix="/api/graph", tags=["graph-advanced"])
app.include_router(graph_topology.router, prefix="/api/graph", tags=["graph-topology"])
app.include_router(dialogue.router, prefix="/api/dialogue", tags=["dialogue"])
app.include_router(learning.router, prefix="/api/learning", tags=["learning"])
app.include_router(learning_extended.router, prefix="/api/learning", tags=["learning-extended"])
app.include_router(learning_intelligence.router, prefix="/api/learning", tags=["learning-intelligence"])
app.include_router(learning_review.router, prefix="/api/learning", tags=["learning-review"])
app.include_router(notes.router, prefix="/api", tags=["notes"])
app.include_router(community.router, prefix="/api", tags=["community"])
app.include_router(community_discussions.router, prefix="/api", tags=["community-discussions"])
app.include_router(community_content.router, prefix="/api", tags=["community-content"])
app.include_router(analytics.router, prefix="/api", tags=["analytics"])
app.include_router(analytics_experience.router, prefix="/api", tags=["analytics-experience"])
app.include_router(analytics_profile.router, prefix="/api", tags=["analytics-profile"])
app.include_router(analytics_planning.router, prefix="/api", tags=["analytics-planning"])
app.include_router(analytics_advanced.router, prefix="/api", tags=["analytics-advanced"])
app.include_router(analytics_insights.router, prefix="/api", tags=["analytics-insights"])
app.include_router(analytics_forecast.router, prefix="/api", tags=["analytics-forecast"])
app.include_router(analytics_social.router, prefix="/api", tags=["analytics-social"])
app.include_router(analytics_search.router, prefix="/api", tags=["analytics-search"])
app.include_router(notifications.router, prefix="/api", tags=["notifications"])
app.include_router(onboarding.router, prefix="/api", tags=["onboarding"])

# ── Frontend SPA serving (for packaged exe mode) ──
_frontend_dist = BASE_DIR / "web_dist"
if _frontend_dist.is_dir():
    _index_html = _frontend_dist / "index.html"
    if not _index_html.is_file():
        logger.warning("Frontend dist exists but index.html is missing: %s", _frontend_dist)
    else:
        @app.get("/{full_path:path}")
        async def serve_spa(full_path: str):
            """Serve frontend SPA — all non-API routes return index.html or static files"""
            if full_path:
                # Security: prevent path traversal
                candidate = (_frontend_dist / full_path).resolve()
                if candidate.is_relative_to(_frontend_dist.resolve()) and candidate.is_file():
                    return FileResponse(str(candidate))
            return FileResponse(str(_index_html))


# ── Entry point for PyInstaller exe ──
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "127.0.0.1")

    logger.info("AI Knowledge Graph v0.1.0 starting on http://%s:%s", host, port)

    # Auto-open browser (m-14: gracefully handle headless/SSH environments)
    import webbrowser
    import threading
    def _try_open_browser():
        try:
            webbrowser.open(f"http://{host}:{port}")
        except Exception:
            pass  # Headless server or no display — silently skip
    threading.Timer(1.5, _try_open_browser).start()

    uvicorn.run(app, host=host, port=port, log_level="info")
