"""Verify cross-sphere link targets exist"""
import json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
seed_dir = os.path.join(BASE, "data", "seed")

all_ids = set()
for d in os.listdir(seed_dir):
    sg = os.path.join(seed_dir, d, "seed_graph.json")
    if os.path.isfile(sg):
        data = json.load(open(sg, "r", encoding="utf-8"))
        key = "concepts" if "concepts" in data else "nodes"
        for n in data[key]:
            all_ids.add(n["id"])

cl = json.load(open(os.path.join(BASE, "data", "seed", "cross_sphere_links.json"), "r", encoding="utf-8"))
broken = []
for l in cl["links"]:
    if l["source_id"] not in all_ids:
        broken.append(("source", l["source_id"], l["source_domain"]))
    if l["target_id"] not in all_ids:
        broken.append(("target", l["target_id"], l["target_domain"]))

if broken:
    for side, cid, dom in broken:
        print(f"BROKEN {side}: {cid} ({dom})")
else:
    print(f"All {len(cl['links'])} links valid. {len(all_ids)} total concept IDs.")
