#!/usr/bin/env python3
"""Find the lowest-scoring legacy RAG documents for targeted upgrade."""
import os, re, json
from collections import Counter

RAG_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "rag")
NEW_DOMAINS = {'systems-theory','cybernetics','information-theory','dissipative-structures','synergetics','catastrophe-theory'}

docs = []
for domain in sorted(os.listdir(RAG_ROOT)):
    dp = os.path.join(RAG_ROOT, domain)
    if not os.path.isdir(dp) or domain in NEW_DOMAINS:
        continue
    for root, _, files in os.walk(dp):
        for f in files:
            if not f.endswith('.md'):
                continue
            fp = os.path.join(root, f)
            with open(fp, 'r', encoding='utf-8') as fh:
                content = fh.read()
            chars = len(content)
            sections = len(re.findall(r'^#{2,3}\s', content, re.MULTILINE))
            has_formula = 1 if re.search(r'\$[^$]+\$', content) else 0
            has_citation = 1 if re.search(r'\(.*?\d{4}.*?\)', content) else 0
            has_question = 1 if re.search(r'\uff1f', content) else 0
            has_example = 1 if re.search(r'(例如|案例|实例|比如)', content) else 0
            
            # Approximate scorer
            sp = min(30, (chars/50)*0.5) if chars > 500 else 5
            dn = min(25, (chars/100)) if chars > 500 else 5
            sr = min(20, 10*(has_citation + has_formula))
            st = min(15, sections * 2.5)
            tc = min(10, 2.5*(has_formula + has_example + has_question + (1 if sections >= 6 else 0)))
            score = sp + dn + sr + st + tc
            
            docs.append({
                'path': fp.replace(os.sep, '/'),
                'domain': domain,
                'file': f,
                'score': round(score, 1),
                'chars': chars,
            })

docs.sort(key=lambda x: x['score'])
targets = docs[:200]

print(f"Total legacy docs: {len(docs)}")
print(f"Bottom 200 score range: {targets[0]['score']:.1f} - {targets[-1]['score']:.1f}")
print(f"\nDomains covered:")
dc = Counter(d['domain'] for d in targets)
for dom, cnt in dc.most_common(15):
    print(f"  {dom}: {cnt}")

# Save
out_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "legacy_upgrade_targets.json")
with open(out_path, 'w', encoding='utf-8') as fh:
    json.dump([d['path'] for d in targets], fh, indent=2)
print(f"\nSaved {len(targets)} targets to {out_path}")
