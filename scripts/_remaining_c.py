import json
with open(r'D:\EchoAgent\projects\ai-knowledge-graph\data\quality_report_detail.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
tier_c = [d for d in data if d.get('quality_tier') == 'C']
print(f'Remaining Tier-C: {len(tier_c)}')
by_domain = {}
for d in tier_c:
    dom = d.get('domain','?')
    by_domain.setdefault(dom, []).append(d)
for dom, docs in sorted(by_domain.items(), key=lambda x: -len(x[1])):
    print(f'\n  {dom} ({len(docs)}):')
    for d in sorted(docs, key=lambda x: x.get('quality_score',0)):
        print(f'    {d["file"].split(chr(92))[-1].replace(".md","")} score={d["quality_score"]:.1f}')
