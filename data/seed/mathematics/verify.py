#!/usr/bin/env python3
"""Quick integrity check for math sphere data."""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
seed = json.load(open(os.path.join(ROOT, "data/seed/mathematics/seed_graph.json"), "r", encoding="utf-8"))
rag = json.load(open(os.path.join(ROOT, "data/rag/mathematics/_index.json"), "r", encoding="utf-8"))

seed_ids = set(c["id"] for c in seed["concepts"])
rag_ids = set(d["id"] for d in rag["documents"])

print(f"Seed concepts: {len(seed_ids)}")
print(f"RAG documents: {len(rag_ids)}")
print(f"Missing RAG docs: {seed_ids - rag_ids or 'none'}")
print(f"Extra RAG docs: {rag_ids - seed_ids or 'none'}")
print(f"Milestones: {sum(1 for c in seed['concepts'] if c.get('is_milestone'))}")
print(f"Subdomains: {len(seed['subdomains'])}")
print(f"Edges: {len(seed['edges'])}")

connected = set()
for e in seed["edges"]:
    connected.add(e["source_id"])
    connected.add(e["target_id"])
orphans = seed_ids - connected
print(f"Orphan nodes: {len(orphans)} {orphans if orphans else ''}")

# Check RAG file existence
missing_files = 0
for doc in rag["documents"]:
    fpath = os.path.join(ROOT, "data/rag", doc["file"])
    if not os.path.exists(fpath):
        print(f"  MISSING: {doc['file']}")
        missing_files += 1
print(f"Missing RAG files: {missing_files}")

# Check domains.json
domains_data = json.load(open(os.path.join(ROOT, "data/seed/domains.json"), "r", encoding="utf-8"))
domain_list = domains_data.get("domains", domains_data) if isinstance(domains_data, dict) else domains_data
math_domain = next((d for d in domain_list if d["id"] == "mathematics"), None)
if math_domain:
    print(f"Domain registered: {math_domain['name']} (active={math_domain.get('is_active')})")
else:
    print("WARNING: mathematics domain not in domains.json!")

print("\nAll checks passed!" if missing_files == 0 and not orphans else "\nISSUES FOUND!")
