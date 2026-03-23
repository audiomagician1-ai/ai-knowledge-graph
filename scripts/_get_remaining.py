import json
with open(r'D:\EchoAgent\projects\ai-knowledge-graph\data\quality_report_detail.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
tier_c = [d for d in data if d.get('quality_tier') == 'C']
# Group by domain
by_domain = {}
for d in tier_c:
    dom = d.get('domain','?')
    cid = d['file'].replace('\\','/').split('/')[-1].replace('.md','')
    by_domain.setdefault(dom, []).append(cid)
for dom, ids in by_domain.items():
    print(f'{dom}:{",".join(ids)}')
