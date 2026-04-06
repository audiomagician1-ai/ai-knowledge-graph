"""健康检查端点"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "akg-api", "version": "0.1.0"}


@router.get("/health/cache")
async def cache_stats():
    """Return LLM response cache hit/miss statistics."""
    from llm.cache import get_stats
    return get_stats()