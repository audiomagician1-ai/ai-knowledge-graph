"""健康检查端点"""

import os
import sys
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


@router.get("/health/system")
async def system_health():
    """Comprehensive system health — DB connectivity, config status, resource stats."""
    result = {
        "status": "ok",
        "python": sys.version.split()[0],
        "components": {},
    }

    # SQLite
    try:
        from db.sqlite_client import get_db, DB_PATH
        with get_db() as conn:
            count = conn.execute("SELECT COUNT(*) FROM concept_progress").fetchone()[0]
        result["components"]["sqlite"] = {
            "status": "connected",
            "db_path": str(DB_PATH),
            "progress_rows": count,
        }
    except Exception as e:
        result["components"]["sqlite"] = {"status": "error", "error": str(e)}

    # Neo4j
    try:
        from db.neo4j_client import neo4j_client
        if neo4j_client._driver:
            result["components"]["neo4j"] = {"status": "connected"}
        else:
            result["components"]["neo4j"] = {"status": "disconnected"}
    except Exception:
        result["components"]["neo4j"] = {"status": "unavailable"}

    # Redis
    try:
        from db.redis_client import redis_client
        if redis_client._client:
            result["components"]["redis"] = {"status": "connected"}
        else:
            result["components"]["redis"] = {"status": "disconnected"}
    except Exception:
        result["components"]["redis"] = {"status": "unavailable"}

    # Seed data
    try:
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data", "seed")
        if os.path.isdir(data_dir):
            domains = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
            result["components"]["seed_data"] = {
                "status": "ok",
                "domains": len(domains),
            }
        else:
            result["components"]["seed_data"] = {"status": "missing"}
    except Exception as e:
        result["components"]["seed_data"] = {"status": "error", "error": str(e)}

    # LLM cache stats
    try:
        from llm.cache import get_stats
        cache = get_stats()
        result["components"]["llm_cache"] = {
            "status": "ok",
            **cache,
        }
    except Exception:
        result["components"]["llm_cache"] = {"status": "unavailable"}

    # Check if any component has errors
    for comp in result["components"].values():
        if comp.get("status") == "error":
            result["status"] = "degraded"
            break

    return result


@router.get("/health/metrics")
async def api_metrics():
    """Return API request metrics — counts, error rates, response times per endpoint."""
    from utils.metrics import metrics
    return metrics.get_summary()