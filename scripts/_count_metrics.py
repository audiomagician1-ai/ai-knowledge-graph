"""Count project metrics: domains, concepts, edges, RAG docs."""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

domains = json.load(open(os.path.join(ROOT, "data/seed/domains.json")))["domains"]
active = [d for d in domains if d.get("is_active", True)]
total_concepts = 0
total_edges = 0
total_rag = 0

for d in active:
    did = d["id"]
    sp = os.path.join(ROOT, "data/seed", did, "seed_graph.json")
    if os.path.exists(sp):
        seed = json.load(open(sp))
        total_concepts += len(seed.get("concepts", []))
        total_edges += len(seed.get("edges", []))
    ip = os.path.join(ROOT, "data/rag", did, "_index.json")
    if os.path.exists(ip):
        idx = json.load(open(ip))
        total_rag += idx.get("total_docs", 0)

# Count cross-sphere links
cl_path = os.path.join(ROOT, "data/seed/cross_sphere_links.json")
cross_links = 0
if os.path.exists(cl_path):
    cl = json.load(open(cl_path))
    cross_links = len(cl) if isinstance(cl, list) else len(cl.get("links", []))

print(f"Domains: {len(active)}")
print(f"Concepts: {total_concepts}")
print(f"Edges: {total_edges}")
print(f"Cross-sphere links: {cross_links}")
print(f"RAG docs: {total_rag}")
print(f"RAG coverage: {total_rag}/{total_concepts} ({total_rag/total_concepts*100:.1f}%)")
