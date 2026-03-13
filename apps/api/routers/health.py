"""健康检查端点"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "akg-api", "version": "0.1.0"}
