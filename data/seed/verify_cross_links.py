"""Verify cross-sphere links: all concept IDs must exist in their respective domains."""
import json
import os
import sys

root = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(root, "cross_sphere_links.json"), "r", encoding="utf-8") as f:
    links = json.load(f)["links"]

domain_concepts = {}
for d in ["ai-engineering", "mathematics", "english"]:
    path = os.path.join(root, d, "seed_graph.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        domain_concepts[d] = set(c["id"] for c in data["concepts"])

errors = []
for i, link in enumerate(links):
    src_ok = link["source_id"] in domain_concepts.get(link["source_domain"], set())
    tgt_ok = link["target_id"] in domain_concepts.get(link["target_domain"], set())
    if not src_ok:
        errors.append(f"Link {i}: MISSING SOURCE {link['source_domain']}:{link['source_id']}")
    if not tgt_ok:
        errors.append(f"Link {i}: MISSING TARGET {link['target_domain']}:{link['target_id']}")

if errors:
    print("ERRORS FOUND:")
    for e in errors:
        print(f"  {e}")
    sys.exit(1)
else:
    print(f"All {len(links)} cross-sphere links verified OK")