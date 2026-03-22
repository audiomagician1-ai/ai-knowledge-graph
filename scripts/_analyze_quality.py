"""Analyze RAG doc quality: generation_method distribution + source coverage."""
import os, re
from collections import Counter

rag_root = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "rag")
methods = Counter()
sources_stats = Counter()
low_score_docs = []
total = 0

for dirpath, dirs, files in os.walk(rag_root):
    for f in sorted(files):
        if not f.endswith(".md"):
            continue
        total += 1
        fpath = os.path.join(dirpath, f)
        rel = os.path.relpath(fpath, rag_root)
        with open(fpath, "r", encoding="utf-8") as fh:
            content = fh.read()

        # generation_method
        m = re.search(r'generation_method:\s*"?([\w-]+)"?', content)
        methods[m.group(1) if m else "(none)"] += 1

        # sources field
        has_sources = bool(re.search(r"sources:\s*\n\s+-\s+type:", content))
        has_wiki = "wikipedia" in content.lower()
        has_textbook = "textbook" in content.lower() or bool(re.search(r"et al\.|edition|ISBN", content, re.I))
        has_paper = bool(re.search(r"arXiv|doi:|IEEE|ACM", content, re.I))
        if has_sources:
            sources_stats["has_sources"] += 1
        if has_wiki:
            sources_stats["has_wikipedia"] += 1
        if has_textbook:
            sources_stats["has_textbook"] += 1
        if has_paper:
            sources_stats["has_paper"] += 1

        # quality_score from YAML
        m2 = re.search(r"quality_score:\s*(\d+\.?\d*)", content)
        if m2:
            score = float(m2.group(1))
            if score < 83:
                low_score_docs.append((score, rel.replace("\\", "/")))

print(f"Total documents: {total}\n")
print("=== Generation Method Distribution ===")
for method, count in methods.most_common():
    print(f"  {method:30s} {count:5d} ({count/total*100:.1f}%)")

pct = lambda k: f"{sources_stats[k]:5d} ({sources_stats[k]/total*100:.1f}%)"
print(f"\n=== Source Coverage ===")
print(f"  Has sources field:  {pct('has_sources')}")
print(f"  Has Wikipedia ref:  {pct('has_wikipedia')}")
print(f"  Has textbook ref:   {pct('has_textbook')}")
print(f"  Has paper ref:      {pct('has_paper')}")

print(f"\n=== Bottom Docs (score < 83) — {len(low_score_docs)} docs ===")
low_score_docs.sort()
for score, rel in low_score_docs[:40]:
    print(f"  {score:5.1f}  {rel}")
