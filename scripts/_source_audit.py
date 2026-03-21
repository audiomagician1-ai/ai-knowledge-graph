"""Full source audit: for each domain, report generation method, source types, quality."""
import json
from pathlib import Path
from collections import defaultdict

QUALITY_DETAIL = Path("data/quality_report_detail.json")
RAG_ROOT = Path("data/rag")
SEED_ROOT = Path("data/seed")

with open(QUALITY_DETAIL, "r", encoding="utf-8") as f:
    details = json.load(f)

# Group by domain
domains = defaultdict(list)
for d in details:
    domains[d.get("domain", "?")].append(d)

# For each domain, analyze generation methods and source presence
print("=" * 100)
print(f"  RAG Knowledge Base Source Audit — {len(details)} documents across {len(domains)} domains")
print("=" * 100)
print()

# Overall generation method stats
gm_total = defaultdict(int)
for d in details:
    gm_total[d.get("generation_method", "unknown")] += 1

print("Overall Generation Method Distribution:")
for gm, cnt in sorted(gm_total.items(), key=lambda x: -x[1]):
    pct = cnt / len(details) * 100
    print(f"  {gm:25s}: {cnt:5d} ({pct:5.1f}%)")
print()

# Overall quality
tiers = defaultdict(int)
for d in details:
    tiers[d.get("quality_tier", "?")] += 1
print("Overall Quality Tier Distribution:")
for t in ["S", "A", "B", "C"]:
    cnt = tiers.get(t, 0)
    pct = cnt / len(details) * 100
    print(f"  Tier {t}: {cnt:5d} ({pct:5.1f}%)")
print()

# Source presence
has_sources = sum(1 for d in details if d.get("has_sources"))
has_textbook = sum(1 for d in details if d.get("has_textbook"))
print(f"Documents with external sources cited: {has_sources} ({has_sources/len(details)*100:.1f}%)")
print(f"Documents with textbook references: {has_textbook} ({has_textbook/len(details)*100:.1f}%)")
print()

# Per-domain breakdown
print("=" * 100)
print(f"  {'Domain':<25s} {'Count':>5s} {'AvgScore':>8s} {'GenMethod':>20s} {'Sources':>7s} {'Tier':>12s}")
print("-" * 100)

for dom in sorted(domains.keys()):
    items = domains[dom]
    count = len(items)
    avg_score = sum(d.get("quality_score", 0) for d in items) / count
    
    # Most common gen method
    gm_counts = defaultdict(int)
    for d in items:
        gm_counts[d.get("generation_method", "unknown")] += 1
    top_gm = max(gm_counts.items(), key=lambda x: x[1])
    gm_str = f"{top_gm[0]}({top_gm[1]})"
    
    # Source count
    src_cnt = sum(1 for d in items if d.get("has_sources"))
    
    # Tier distribution
    tier_d = defaultdict(int)
    for d in items:
        tier_d[d.get("quality_tier", "?")] += 1
    tier_str = f"S{tier_d['S']}/A{tier_d['A']}/B{tier_d['B']}/C{tier_d['C']}"
    
    print(f"  {dom:<25s} {count:>5d} {avg_score:>8.1f} {gm_str:>20s} {src_cnt:>7d} {tier_str:>12s}")

print()
print("=" * 100)
print("  Generation Method Definitions:")
print("  - template-v1:          Python script (generate_rag.py) fills {name}/{description} into subdomain templates")
print("  - ai-batch-v1:          AI batch-generated in conversation, 1KB boilerplate per doc")
print("  - ai-rewrite-v1:        AI rewrite without web research (physics milestones, Sprint 1)")
print("  - hand-crafted:         Written interactively with detailed formulas/code (llm-core)")
print("  - research-rewrite-v2:  Web research enhanced rewrite with external source citations")
print("=" * 100)

# External sources detail: which docs have real external citations
print()
print("Documents with External Source Citations:")
for d in details:
    if d.get("has_sources"):
        print(f"  {d['file']}: score={d['quality_score']:.1f} gen={d.get('generation_method','?')}")
