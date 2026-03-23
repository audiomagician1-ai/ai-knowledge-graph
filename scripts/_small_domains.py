import json
with open(r'D:\EchoAgent\projects\ai-knowledge-graph\data\quality_report_detail.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
# Original Tier-C counts
c_orig = {}
for d in data:
    if d.get('quality_tier') == 'C':
        dom = d.get('domain','?')
        c_orig[dom] = c_orig.get(dom, 0) + 1
for d, c in sorted(c_orig.items(), key=lambda x:x[1]):
    if c <= 15:
        print(f'  {d}: {c} Tier-C docs')
