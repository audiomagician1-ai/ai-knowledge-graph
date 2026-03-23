import json
with open(r'D:\EchoAgent\projects\ai-knowledge-graph\data\quality_report_detail.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Group Tier-B docs by domain, sorted by avg score (worst first)
tier_b = [d for d in data if d.get('quality_tier') == 'B']
print(f'Total Tier-B: {len(tier_b)}')

by_domain = {}
for d in tier_b:
    dom = d.get('domain','?')
    by_domain.setdefault(dom, []).append(d['quality_score'])

print(f'\nTier-B domains by avg score (worst first):')
for dom, scores in sorted(by_domain.items(), key=lambda x: sum(x[1])/len(x[1])):
    avg = sum(scores)/len(scores)
    print(f'  {dom}: {len(scores)} docs, avg={avg:.1f}, min={min(scores):.1f}, max={max(scores):.1f}')

# How many could be upgraded to A with rewrite?
low_b = [d for d in tier_b if d['quality_score'] < 45]
print(f'\nLow Tier-B (<45): {len(low_b)} docs (priority targets)')
