#!/usr/bin/env python3
"""Quick data integrity check."""
import json, glob, os
total_concepts = 0
total_edges = 0
all_ids = set()
dup_ids = []
broken_edges = []
for f in sorted(glob.glob('data/seed/*/seed_graph.json')):
    with open(f, 'r', encoding='utf-8') as fh:
        d = json.load(fh)
    domain = d.get('domain', '')
    if isinstance(domain, dict):
        domain = domain.get('id', '')
    concepts = d.get('concepts', [])
    edges = d.get('edges', [])
    ids = {c['id'] for c in concepts}
    for cid in ids:
        if cid in all_ids:
            dup_ids.append(cid)
    all_ids |= ids
    for e in edges:
        src = e.get('source_id') or e.get('source', '')
        tgt = e.get('target_id') or e.get('target', '')
        if src not in ids or tgt not in ids:
            broken_edges.append((domain, e['source_id'], e['target_id']))
    total_concepts += len(concepts)
    total_edges += len(edges)
with open('data/seed/cross_sphere_links.json', 'r', encoding='utf-8') as f:
    cl = json.load(f)
domains = len(glob.glob('data/seed/*/seed_graph.json'))
print(f'Domains: {domains}')
print(f'Total concepts: {total_concepts}')
print(f'Total edges: {total_edges}')
print(f'Duplicate IDs: {len(dup_ids)}')
print(f'Broken edges: {len(broken_edges)}')
print(f'Cross-links: {len(cl["links"])}')
if dup_ids:
    print(f'  Duplicates: {dup_ids[:5]}')
if broken_edges:
    print(f'  Broken: {broken_edges[:5]}')
