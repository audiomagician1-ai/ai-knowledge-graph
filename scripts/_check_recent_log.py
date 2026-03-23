import json
with open(r'D:\EchoAgent\projects\ai-knowledge-graph\data\intranet_rewrite_log.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
recent = [d for d in data if d.get('timestamp','') > '2026-03-22T17:45']
print(f'Recent entries: {len(recent)}')
for d in recent[:10]:
    print(f"  {d.get('concept_id','?')} domain={d.get('domain','?')} status={d.get('status','?')}")
