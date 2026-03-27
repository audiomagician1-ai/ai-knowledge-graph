import os

base = r'D:\EchoAgent\projects\AI-Knowledge-Graph\data\rag'
counts = {'v2': 0, 'v1': 0, 'ai': 0, 'other': 0}
total = 0

for root, dirs, files in os.walk(base):
    for f in files:
        if not f.endswith('.md'):
            continue
        total += 1
        path = os.path.join(root, f)
        with open(path, 'r', encoding='utf-8') as fh:
            head = fh.read(600)
        if 'quality_method: intranet-llm-rewrite-v2' in head:
            counts['v2'] += 1
        elif 'quality_method: intranet-llm-rewrite-v1' in head:
            counts['v1'] += 1
        elif 'quality_method: ai-rewrite-v1' in head:
            counts['ai'] += 1
        else:
            counts['other'] += 1

print(f"Total RAG files: {total}")
for k, v in counts.items():
    pct = v * 100 / total if total else 0
    print(f"  {k}: {v} ({pct:.1f}%)")
print(f"Remaining to rewrite-v2: {total - counts['v2']}")
