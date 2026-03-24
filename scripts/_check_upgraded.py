import json
progress = json.load(open('data/tier_b_upgrade_progress.json','r',encoding='utf-8'))
completed = set(progress['completed'])
detail = json.load(open('data/quality_report_detail.json','r',encoding='utf-8'))

still_b = []
upgraded = []
for d in detail:
    slug = d['file'].replace('.md','').split('\\')[-1]
    if slug in completed:
        if d['quality_tier'] == 'B':
            still_b.append(d)
        else:
            upgraded.append(d)

print(f'Completed docs: {len(completed)}')
print(f'  Upgraded to A/S: {len(upgraded)}')
print(f'  Still Tier-B: {len(still_b)}')
if still_b:
    print('Still-B examples:')
    for d in still_b[:10]:
        print(f'  {d["file"]}: score={d["quality_score"]:.1f} spec={d["dim1_specificity"]} dens={d["dim2_density"]}')
if upgraded:
    scores = [d['quality_score'] for d in upgraded]
    print(f'Upgraded avg: {sum(scores)/len(scores):.1f} min={min(scores):.1f} max={max(scores):.1f}')
    tiers = {}
    for d in upgraded:
        t = d['quality_tier']
        tiers[t] = tiers.get(t,0)+1
    print(f'Tier dist: {dict(sorted(tiers.items()))}')
