import json
with open(r'D:\EchoAgent\projects\ai-knowledge-graph\data\quality_report_detail.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
phys = [d for d in data if 'physics' in d.get('file','').lower() or 'physics' in d.get('domain','').lower()]
print(f'Physics entries: {len(phys)}')
if phys:
    for d in phys[:5]:
        print(f"  file={d.get('file','?')} score={d.get('score','?')} tier={d.get('tier','?')}")
tiers = {}
for d in data:
    t = d.get('tier', '?')
    tiers[t] = tiers.get(t, 0) + 1
print(f'Overall tier distribution: {tiers}')
# Also check keys in first entry
if data:
    print(f'\nFirst entry keys: {list(data[0].keys())}')
    print(f'First entry: {data[0]}')
