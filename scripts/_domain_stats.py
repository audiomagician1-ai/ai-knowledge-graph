import json

detail = json.load(open('data/quality_report_detail.json','r',encoding='utf-8'))
progress = json.load(open('data/tier_b_upgrade_progress.json','r',encoding='utf-8'))
completed = set(progress['completed'])

domain_counts = {}
for d in detail:
    if d['quality_tier'] == 'B':
        slug = d['file'].replace('.md','').split('\\')[-1]
        if slug not in completed:
            dom = d['domain']
            domain_counts[dom] = domain_counts.get(dom, 0) + 1

for dom, cnt in sorted(domain_counts.items(), key=lambda x: -x[1]):
    print(f'  {dom:<25} {cnt:>5} Tier-B remaining')
print(f'  {"TOTAL":<25} {sum(domain_counts.values()):>5}')
