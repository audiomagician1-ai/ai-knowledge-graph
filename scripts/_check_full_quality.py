import json
with open(r'D:\EchoAgent\projects\ai-knowledge-graph\data\quality_report_detail.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print(f'Total scored: {len(data)}')
tiers = {}
domains_c = {}
for d in data:
    t = d.get('quality_tier', '?')
    tiers[t] = tiers.get(t, 0) + 1
    if t == 'C':
        dom = d.get('domain', '?')
        domains_c[dom] = domains_c.get(dom, 0) + 1
print(f'\nTier distribution: {tiers}')
print(f'\nTier-C by domain ({sum(domains_c.values())} total):')
for d, c in sorted(domains_c.items(), key=lambda x:-x[1]):
    print(f'  {d}: {c}')
