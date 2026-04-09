"""Shared analytics utilities — seed data loading helpers.

Used by analytics_insights, analytics_social, and analytics_search routers.
"""

import os
import sys


def _get_data_root() -> str:
    """Get the seed data root directory."""
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, "seed_data")
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        "data", "seed",
    )


def load_seed_metadata() -> tuple[dict[str, str], dict[str, dict], dict[str, dict]]:
    """Load domain/concept metadata from seed files.

    Returns (concept_domain_map, concept_info, domain_map).
    """
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

    return concept_domain_map, concept_info, domain_map
