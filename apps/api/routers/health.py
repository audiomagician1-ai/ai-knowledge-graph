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


@router.get("/health/project")
async def project_stats():
    """Return project-level statistics — domains, concepts, edges, RAG coverage, cross-links."""
    import json

    data_root = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data")
    seed_root = os.path.join(data_root, "seed")
    rag_root = os.path.join(data_root, "rag")

    stats = {
        "domains": 0,
        "concepts": 0,
        "edges": 0,
        "cross_links": 0,
        "rag_files": 0,
        "rag_coverage_pct": 0,
        "domain_details": [],
    }

    # Count domains + concepts + edges
    try:
        domains_json = os.path.join(seed_root, "domains.json")
        if os.path.isfile(domains_json):
            with open(domains_json, "r", encoding="utf-8") as f:
                raw = json.load(f)
            domain_list = raw.get("domains", raw) if isinstance(raw, dict) else raw
            stats["domains"] = len(domain_list)

            for d in domain_list:
                domain_id = d.get("id", "")
                seed_file = os.path.join(seed_root, domain_id, "seed_graph.json")
                c_count, e_count = 0, 0
                if os.path.isfile(seed_file):
                    with open(seed_file, "r", encoding="utf-8") as f:
                        sg = json.load(f)
                    c_count = len(sg.get("concepts", []))
                    e_count = len(sg.get("edges", []))
                stats["concepts"] += c_count
                stats["edges"] += e_count

                # Count RAG files per domain
                rag_dir = os.path.join(rag_root, domain_id)
                rag_count = 0
                if os.path.isdir(rag_dir):
                    for root, _dirs, files in os.walk(rag_dir):
                        rag_count += sum(1 for f in files if f.endswith(".md"))
                stats["rag_files"] += rag_count

                stats["domain_details"].append({
                    "id": domain_id,
                    "name": d.get("name", ""),
                    "concepts": c_count,
                    "edges": e_count,
                    "rag_files": rag_count,
                })
    except Exception:
        pass

    # Cross-links
    try:
        cross_file = os.path.join(seed_root, "cross_sphere_links.json")
        if os.path.isfile(cross_file):
            with open(cross_file, "r", encoding="utf-8") as f:
                raw = json.load(f)
            # Support both {"links": [...]} and plain [...]
            links = raw.get("links", raw) if isinstance(raw, dict) else raw
            stats["cross_links"] = len(links) if isinstance(links, list) else 0
    except Exception:
        pass

    # RAG coverage
    if stats["concepts"] > 0:
        stats["rag_coverage_pct"] = round(stats["rag_files"] / stats["concepts"] * 100, 1)

    return stats


@router.get("/health/api-catalog")
async def api_catalog():
    """Enumerate all registered API endpoints with metadata.

    Returns a list of all routes, organized by tag/module, with method, path,
    summary, and module source. Useful for API documentation and monitoring.
    """
    from fastapi import Request
    from main import app as _app

    routes_by_tag: dict[str, list[dict]] = {}
    total = 0

    for route in _app.routes:
        if not hasattr(route, "methods") or not hasattr(route, "path"):
            continue
        path = route.path
        # Skip internal/docs routes
        if path in ("/openapi.json", "/docs", "/redoc", "/docs/oauth2-redirect"):
            continue
        methods = sorted(route.methods - {"HEAD", "OPTIONS"}) if route.methods else []
        if not methods:
            continue

        summary = getattr(route, "summary", "") or ""
        name = getattr(route, "name", "") or ""
        tags = list(getattr(route, "tags", []) or [])
        tag = tags[0] if tags else "other"

        for method in methods:
            entry = {
                "method": method,
                "path": path,
                "name": name,
                "summary": summary,
            }
            routes_by_tag.setdefault(tag, []).append(entry)
            total += 1

    # Sort within each tag
    for tag in routes_by_tag:
        routes_by_tag[tag].sort(key=lambda r: (r["path"], r["method"]))

    return {
        "total_endpoints": total,
        "total_tags": len(routes_by_tag),
        "tags": {tag: {"count": len(routes), "endpoints": routes}
                 for tag, routes in sorted(routes_by_tag.items())},
    }


@router.get("/health/latency-report")
async def latency_report():
    """Aggregated API latency and error report from in-memory metrics.

    Returns per-endpoint performance data sorted by avg latency (slowest first),
    plus global summary and endpoints with high error rates.
    """
    from utils.metrics import metrics as mc

    summary = mc.get_summary()
    endpoints = summary.get("endpoints", {})

    # Build latency-sorted list
    latency_list = []
    high_error = []
    for path, data in endpoints.items():
        entry = {"path": path, **data}
        latency_list.append(entry)
        err_pct = float(data.get("error_rate", "0%").rstrip("%"))
        if err_pct > 5 and data["requests"] >= 3:
            high_error.append(entry)

    latency_list.sort(key=lambda x: x["avg_ms"], reverse=True)
    high_error.sort(key=lambda x: float(x["error_rate"].rstrip("%")), reverse=True)

    # Compute global aggregates
    total_req = summary.get("total_requests", 0)
    all_avg = [e["avg_ms"] for e in latency_list if e["requests"] > 0]

    return {
        "uptime_seconds": summary.get("uptime_seconds", 0),
        "total_requests": total_req,
        "global_error_rate": summary.get("global_error_rate", "0%"),
        "global_avg_ms": round(sum(all_avg) / max(1, len(all_avg)), 1) if all_avg else 0,
        "slowest_endpoints": latency_list[:10],
        "high_error_endpoints": high_error[:5],
        "total_tracked": len(latency_list),
    }