import json, os
base = r'D:\EchoAgent\projects\ai-knowledge-graph\data\rag'
tier_c = {}
tier_b = {}
total = 0
for root, dirs, files in os.walk(base):
    for f in files:
        if not f.endswith('.md'): continue
        fp = os.path.join(root, f)
        total += 1
        with open(fp, 'r', encoding='utf-8') as fh:
            content = fh.read()
        if '---' not in content: continue
        parts = content.split('---', 2)
        if len(parts) < 3: continue
        fm = parts[1]
        score = None
        domain = None
        for line in fm.split('\n'):
            if line.startswith('quality_score:'):
                try: score = float(line.split(':',1)[1].strip())
                except: pass
            if line.startswith('domain:'):
                domain = line.split(':',1)[1].strip().strip('"')
        if score is not None and domain:
            if score < 40:
                tier_c[domain] = tier_c.get(domain, 0) + 1
            elif score < 60:
                tier_b[domain] = tier_b.get(domain, 0) + 1
print(f'Total docs: {total}')
print(f'\nTier-C (<40) by domain ({sum(tier_c.values())} total):')
for d, c in sorted(tier_c.items(), key=lambda x:-x[1]):
    print(f'  {d}: {c}')
print(f'\nTier-B (40-60) by domain ({sum(tier_b.values())} total):')
for d, c in sorted(tier_b.items(), key=lambda x:-x[1])[:15]:
    print(f'  {d}: {c}')
