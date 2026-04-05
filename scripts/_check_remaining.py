"""Check remaining docs below threshold that haven't been boosted."""
import json, os, re

p = json.load(open('data/tier_s_booster_progress.json', encoding='utf-8'))
completed = set(p.get('completed', []))
print(f'Total completed in progress: {len(completed)}')

count = 0
remaining = []
for root, dirs, files in os.walk('data/rag'):
    for f in files:
        if f.endswith('.md'):
            path = os.path.join(root, f)
            with open(path, encoding='utf-8') as fh:
                content = fh.read(600)
                m = re.search(r'quality_score:\s*([\d.]+)', content)
                if m:
                    score = float(m.group(1))
                    if score < 73.1:
                        nm = re.search(r'title:\s*["\']?(.+?)["\']?\s*$', content, re.M)
                        name = nm.group(1).strip('"\'') if nm else f
                        if name not in completed:
                            remaining.append((name, score, path))
                            count += 1

print(f'Remaining below 73.1 (not yet boosted): {count}')
for name, score, path in sorted(remaining, key=lambda x: x[1]):
    print(f'  {score:.1f} - {name} ({path})')
