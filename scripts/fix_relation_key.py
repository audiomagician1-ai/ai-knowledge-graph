#!/usr/bin/env python3
"""Fix relation values in cross_sphere_links.json to use valid types."""
import json
from pathlib import Path

LINKS_PATH = Path(__file__).resolve().parent.parent / "data" / "seed" / "cross_sphere_links.json"

VALID = {"same_concept", "requires", "enables", "applies_to", "applied_in",
         "foundational", "supports", "related", "related_to", "applies",
         "impacts", "prerequisite", "teaches"}

# Map invalid names to valid ones
REMAP = {
    "foundational_theory": "foundational",
    "applies_concept": "applies",
}

with open(LINKS_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

fixed = 0
for link in data["links"]:
    rel = link.get("relation", "")
    if rel not in VALID:
        new_rel = REMAP.get(rel, "related")
        print(f"  Fix: {rel} -> {new_rel} ({link['source_id']} -> {link['target_id']})")
        link["relation"] = new_rel
        fixed += 1

with open(LINKS_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\nFixed {fixed} links")
