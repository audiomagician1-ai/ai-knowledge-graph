"""
AI Knowledge Graph — Backend API
图谱引擎 + 对话引擎 + 学习引擎
"""

import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import graph, dialogue, learning, health

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理 — DB connections are optional (graceful degradation)"""
    # Startup: try connecting DBs but don't crash if unavailable
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "X-LLM-Provider",
        "X-LLM-API-Key",
        "X-LLM-Model",
    ],
)

# 路由注册
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(graph.router, prefix="/api/graph", tags=["graph"])
app.include_router(dialogue.router, prefix="/api/dialogue", tags=["dialogue"])
app.include_router(learning.router, prefix="/api/learning", tags=["learning"])
