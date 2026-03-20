"""Validate cross-sphere links."""
import json, os
base = os.path.join(os.path.dirname(__file__), "..")
gd = json.load(open(os.path.join(base, "seed/game-design/seed_graph.json"), encoding="utf-8"))
ld = json.load(open(os.path.join(base, "seed/level-design/seed_graph.json"), encoding="utf-8"))
links = json.load(open(os.path.join(base, "seed/cross_sphere_links.json"), encoding="utf-8"))

all_ids = {
    "game-design": {c["id"] for c in gd["concepts"]},
    "level-design": {c["id"] for c in ld["concepts"]},
}
errors = []
for i, link in enumerate(links["links"]):
    sd, si = link["source_domain"], link["source_id"]
    td, ti = link["target_domain"], link["target_id"]
    if sd in all_ids and si not in all_ids[sd]:
        errors.append(f"Link {i}: source {sd}/{si} not found")
    if td in all_ids and ti not in all_ids[td]:
        errors.append(f"Link {i}: target {td}/{ti} not found")

if errors:
    for e in errors: print(f"ERROR: {e}")
else:
    print(f"All {len(links['links'])} cross-sphere links validated OK")
