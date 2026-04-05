import pathlib, re
from collections import Counter

rag = pathlib.Path("data/rag")
tiers = Counter()
for f in rag.rglob("*.md"):
    txt = f.read_text(encoding="utf-8", errors="ignore")[:600]
    m = re.search(r'quality_tier:\s*"?([^"\n]+)', txt)
    if m:
        tiers[m.group(1).strip().strip('"')] += 1
    else:
        tiers["no-tier"] += 1

for k, v in tiers.most_common():
    print(f"{k}: {v}")
print(f"---\nTotal: {sum(tiers.values())}")
