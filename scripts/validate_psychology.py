"""Validate psychology knowledge sphere data integrity."""
import json
import os

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 1. Validate seed graph
with open(os.path.join(root, 'data/seed/psychology/seed_graph.json'), encoding='utf-8') as f:
    data = json.load(f)

concepts = data['concepts']
edges = data['edges']
meta = data['meta']
ids = set(c['id'] for c in concepts)

print(f"=== Psychology Seed Graph ===")
print(f"Concepts: {len(concepts)} (unique IDs: {len(ids)})")
print(f"Edges: {len(edges)}")
stats = meta.get('stats', meta)
print(f"Subdomains: {stats.get('total_subdomains', 'N/A')}")
print(f"Milestones: {sum(1 for c in concepts if c.get('is_milestone'))}")

# Meta consistency
tc = stats.get('total_concepts', meta.get('total_concepts'))
te = stats.get('total_edges', meta.get('total_edges'))
assert tc == len(concepts), f"Meta mismatch: {tc} vs {len(concepts)}"
assert te == len(edges), f"Meta mismatch: {te} vs {len(edges)}"
print("Meta consistent: OK")

# Invalid edges
sk, tk = ('source_id', 'target_id') if 'source_id' in edges[0] else ('source', 'target')
bad = [e for e in edges if e[sk] not in ids or e[tk] not in ids]
assert len(bad) == 0, f"Invalid edges: {bad}"
print(f"Invalid edges: 0")

# Orphan nodes
connected = set()
for e in edges:
    connected.add(e[sk])
    connected.add(e[tk])
orphans = ids - connected
assert len(orphans) == 0, f"Orphan nodes: {orphans}"
print(f"Orphan nodes: 0")

# 2. Validate RAG docs
rag_dir = os.path.join(root, 'data/rag/psychology')
rag_count = 0
for sd in os.listdir(rag_dir):
    sd_path = os.path.join(rag_dir, sd)
    if os.path.isdir(sd_path):
        for f in os.listdir(sd_path):
            if f.endswith('.md'):
                rag_count += 1

print(f"\n=== RAG Documents ===")
print(f"RAG docs: {rag_count}")
print(f"Seed concepts: {len(concepts)}")
print(f"Coverage: {rag_count}/{len(concepts)} = {'100%' if rag_count >= len(concepts) else f'{rag_count*100//len(concepts)}%'}")

# 3. Validate cross-sphere links
with open(os.path.join(root, 'data/seed/cross_sphere_links.json'), encoding='utf-8') as f:
    links_data = json.load(f)

all_links = links_data['links']
psych_links = [l for l in all_links if 'psychology' in l.get('from_domain', '') or 'psychology' in l.get('to_domain', '')]
print(f"\n=== Cross-Sphere Links ===")
print(f"Total links: {len(all_links)}")
print(f"Psychology-related: {len(psych_links)}")

# 4. Validate domains.json
with open(os.path.join(root, 'data/seed/domains.json'), encoding='utf-8') as f:
    domains = json.load(f)
psych_domain = [d for d in domains['domains'] if d['id'] == 'psychology']
assert len(psych_domain) == 1, "Psychology domain not found in domains.json"
print(f"\n=== Domain Registry ===")
print(f"Psychology registered: OK (is_active={psych_domain[0].get('is_active')})")

print("\n=== ALL CHECKS PASSED ===")
