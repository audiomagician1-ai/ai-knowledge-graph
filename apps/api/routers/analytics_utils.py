"""Shared analytics utilities — seed data loading helpers.

Used by analytics_insights, analytics_social, and analytics_search routers.
Includes in-memory cache (TTL 300s) to avoid re-reading 36 seed JSON files per request.
"""

import os
import re
import sys
import time
from typing import Optional

# ---------------------------------------------------------------------------
# Module-level cache — seed data is static, safe to cache for 5 minutes.
# ---------------------------------------------------------------------------
_CACHE_TTL = 300  # seconds
_cache_data: Optional[tuple[dict[str, str], dict[str, dict], dict[str, dict]]] = None
_cache_ts: float = 0.0


def _get_data_root() -> str:
    """Get the seed data root directory."""
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, "seed_data")
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        "data", "seed",
    )


def invalidate_seed_cache() -> None:
    """Force cache invalidation (useful after seed data updates)."""
    global _cache_data, _cache_ts
    _cache_data = None
    _cache_ts = 0.0


def load_seed_metadata() -> tuple[dict[str, str], dict[str, dict], dict[str, dict]]:
    """Load domain/concept metadata from seed files (cached, TTL 300s).

    Returns (concept_domain_map, concept_info, domain_map).
    """
    global _cache_data, _cache_ts

    now = time.monotonic()
    if _cache_data is not None and (now - _cache_ts) < _CACHE_TTL:
        return _cache_data

    import json as _json

    data_root = _get_data_root()

    concept_domain_map: dict[str, str] = {}
    concept_info: dict[str, dict] = {}
    domain_map: dict[str, dict] = {}

    domains_path = os.path.join(data_root, "domains.json")
    if os.path.isfile(domains_path):
        with open(domains_path, "r", encoding="utf-8") as f:
            raw = _json.load(f)
        domain_list = raw.get("domains", raw) if isinstance(raw, dict) else raw
        domain_map = {d["id"]: d for d in domain_list}
        for d in domain_list:
            did = d["id"]
            seed_path = os.path.join(data_root, did, "seed_graph.json")
            if os.path.isfile(seed_path):
                with open(seed_path, "r", encoding="utf-8") as f:
                    seed = _json.load(f)
                for c in seed.get("concepts", []):
                    concept_domain_map[c["id"]] = did
                    concept_info[c["id"]] = {
                        "name": c.get("name", c["id"]),
                        "difficulty": c.get("difficulty", 5),
                        "subdomain": c.get("subdomain_id", ""),
                        "tags": c.get("tags", []),
                    }

    result = (concept_domain_map, concept_info, domain_map)
    _cache_data = result
    _cache_ts = now
    return result


# ---------------------------------------------------------------------------
# Domain ID validation — prevents path traversal (#54)
# ---------------------------------------------------------------------------
_DOMAIN_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")


def validate_domain_id(domain_id: str) -> bool:
    """Check that domain_id is safe for filesystem path construction.

    Returns True if the domain_id matches allowed pattern AND exists in
    the seed domains.json whitelist.  Returns False otherwise.
    """
    if not domain_id or not _DOMAIN_ID_RE.match(domain_id):
        return False
    # Check against whitelist (uses cached seed data)
    _, _, domain_map = load_seed_metadata()
    return domain_id in domain_map


def get_data_root() -> str:
    """Public accessor for seed data root directory."""
    return _get_data_root()
