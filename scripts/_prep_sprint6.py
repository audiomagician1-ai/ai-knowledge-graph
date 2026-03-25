"""Prepare Sprint 6 batch: all remaining Tier-B docs not yet upgraded."""
import json, os
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

d = json.load(open('data/quality_report_detail.json', 'r', encoding='utf-8'))
already_done = set()
for pf in ['data/tier_b_upgrade_progress.json', 'data/tier_b_upgrade_progress_p2.json']:
    p = json.load(open(pf, 'r', encoding='utf-8'))
    already_done.update(p.get('completed', []))

remaining = []
for x in d:
    fname = os.path.basename(x['file']).replace('.md', '')
    if x['quality_tier'] == 'B' and fname not in already_done:
        remaining.append({'slug': fname, 'domain': x['domain'], 'score': x['quality_score']})

remaining.sort(key=lambda x: x['score'])

config = {
    'total': len(remaining),
    'done': 0,
    'errors': [],
    'error_slugs': [],
    'completed': [],
    'queue': [r['slug'] for r in remaining]
}
with open('data/tier_b_upgrade_progress_s6.json', 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)

print(f'Sprint 6 queue: {len(remaining)} docs')
print(f'Score range: {remaining[0]["score"]:.1f} - {remaining[-1]["score"]:.1f}')

dc = Counter(r['domain'] for r in remaining)
for dom, cnt in dc.most_common(10):
    print(f'  {dom:30s} {cnt}')
