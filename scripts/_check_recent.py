#!/usr/bin/env python3
"""Check quality of recently upgraded docs."""
import json, os, re, glob

progress = json.load(open('data/tier_b_upgrade_progress.json', 'r', encoding='utf-8'))
completed = progress.get('completed', [])
print(f"Total completed: {len(completed)}")

# Check the last 10 upgraded docs
recent = completed[-10:]
for doc_id in recent:
    slug = doc_id.split('/')[-1]
    # Find the file
    matches = glob.glob(f'data/rag/**/{slug}.md', recursive=True)
    if not matches:
        print(f"  {doc_id}: FILE NOT FOUND")
        continue
    path = matches[0]
    content = open(path, 'r', encoding='utf-8').read()
    # Extract body after frontmatter
    fm_end = content.find('---', content.find('---') + 3)
    body = content[fm_end+3:] if fm_end > 0 else content
    body_clean = re.sub(r'[#\s\-\*\>\|\`\n]', '', body)
    gen_method = 'unknown'
    m = re.search(r'generation_method:\s*"?([^"\n]+)', content)
    if m:
        gen_method = m.group(1).strip()
    print(f"  {doc_id}: {len(content):>5}B body={len(body_clean):>4}ch gen={gen_method}")

# Score distribution of all completed vs uncompleted
detail = json.load(open('data/quality_report_detail.json', 'r', encoding='utf-8'))
# Build map using domain/slug as key
def doc_key(d):
    f = d['file'].replace('\\','/').replace('.md','')
    parts = f.split('/')
    return '/'.join(parts[-2:]) if len(parts) >= 2 else f

detail_map = {doc_key(d): d for d in detail}
completed_set = set(completed)

completed_scores = [detail_map[d]['quality_score'] for d in completed if d in detail_map]
print(f'\nMatched {len(completed_scores)}/{len(completed)} completed docs in report')
uncompleted_scores = [d['quality_score'] for d in detail if doc_key(d) not in completed_set and d.get('quality_tier') == 'B']

if completed_scores:
    print(f"\nCompleted docs ({len(completed_scores)}):")
    print(f"  Avg: {sum(completed_scores)/len(completed_scores):.1f}")
    print(f"  Min: {min(completed_scores):.1f} Max: {max(completed_scores):.1f}")

if uncompleted_scores:
    print(f"\nRemaining Tier-B ({len(uncompleted_scores)}):")
    print(f"  Avg: {sum(uncompleted_scores)/len(uncompleted_scores):.1f}")
    print(f"  Min: {min(uncompleted_scores):.1f} Max: {max(uncompleted_scores):.1f}")
