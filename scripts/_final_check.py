import json
with open(r'D:\EchoAgent\projects\ai-knowledge-graph\data\quality_report_detail.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
tc = [d for d in data if d.get('quality_tier') == 'C']
print(f'Tier-C count: {len(tc)}')
for d in tc:
    print(f'  {d["file"]} score={d["quality_score"]:.1f} chars={d.get("plain_chars",0)} spec={d.get("dim1_specificity",0)} dens={d.get("dim2_density",0)}')
