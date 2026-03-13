"""
AI Knowledge Graph — Backend API
图谱引擎 + 对话引擎 + 学习引擎
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import graph, dialogue, learning, health
from db.neo4j_client import neo4j_client
from db.redis_client import redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # Startup
    await neo4j_client.connect()
    await redis_client.connect()
    yield
    # Shutdown
    await neo4j_client.close()
    await redis_client.close()


app = FastAPI(
    title="AI Knowledge Graph API",
    description="费曼对话 + 知识图谱 + 技能树点亮",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由注册
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(graph.router, prefix="/api/graph", tags=["graph"])
app.include_router(dialogue.router, prefix="/api/dialogue", tags=["dialogue"])
app.include_router(learning.router, prefix="/api/learning", tags=["learning"])
