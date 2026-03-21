import json
for domain in ['biology', 'mathematics', 'economics', 'finance']:
    with open(f'data/rewrite_drafts/search_plans_{domain}.json', 'r', encoding='utf-8') as f:
        plans = json.load(f)
    print(f'\n=== {domain} ({len(plans)} concepts) ===')
    for p in plans:
        print(f'  {p["concept_id"]}: {p["name"]}')
        for q in p.get('queries', [])[:2]:
            print(f'    Q: {q}')
