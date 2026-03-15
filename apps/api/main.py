"""
AI Knowledge Graph — Backend API
图谱引擎 + 对话引擎 + 学习引擎
支持两种运行模式：
  1. 开发模式: uvicorn main:app --reload （前端由 Vite dev server 提供）
  2. 打包模式: PyInstaller exe  （前端 dist 内嵌，由 FastAPI StaticFiles 提供）
"""

import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from routers import graph, dialogue, learning, health

logger = logging.getLogger(__name__)


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


app = FastAPI(
    title="AI Knowledge Graph API",
    description="费曼对话 + 知识图谱 + 技能树点亮",
    version="0.1.0",
    lifespan=lifespan,
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

# 路由注册
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(graph.router, prefix="/api/graph", tags=["graph"])
app.include_router(dialogue.router, prefix="/api/dialogue", tags=["dialogue"])
app.include_router(learning.router, prefix="/api/learning", tags=["learning"])

# ── Frontend SPA serving (for packaged exe mode) ──
_frontend_dist = BASE_DIR / "web_dist"
if _frontend_dist.is_dir():
    _index_html = _frontend_dist / "index.html"

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve frontend SPA — all non-API routes return index.html or static files"""
        if full_path:
            # Security: prevent path traversal
            safe_path = Path(full_path).resolve()
            candidate = (_frontend_dist / full_path).resolve()
            if str(candidate).startswith(str(_frontend_dist.resolve())) and candidate.is_file():
                return FileResponse(str(candidate))
        return FileResponse(str(_index_html))


# ── Entry point for PyInstaller exe ──
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "127.0.0.1")

    print(f"\n{'='*50}")
    print(f"  AI Knowledge Graph v0.1.0")
    print(f"  http://{host}:{port}")
    print(f"{'='*50}\n")

    # Auto-open browser
    import webbrowser
    import threading
    threading.Timer(1.5, lambda: webbrowser.open(f"http://{host}:{port}")).start()

    uvicorn.run(app, host=host, port=port, log_level="info")
