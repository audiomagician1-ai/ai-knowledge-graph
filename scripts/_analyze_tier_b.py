#!/usr/bin/env python3
"""Analyze Tier-B documents to understand what needs upgrading."""
import json
from collections import Counter

with open("data/quality_report_detail.json", encoding="utf-8") as f:
    data = json.load(f)

tier_b = [d for d in data if d.get("quality_tier") == "B"]
print(f"Total Tier-B: {len(tier_b)}")

# Generation methods
methods = Counter(d.get("generation_method", "unknown") for d in tier_b)
print("\nGeneration methods:")
for m, c in methods.most_common():
    docs = [d for d in tier_b if d.get("generation_method", "unknown") == m]
    avg = sum(d["quality_score"] for d in docs) / len(docs)
    lo = min(d["quality_score"] for d in docs)
    hi = max(d["quality_score"] for d in docs)
    print(f"  {m}: count={c}, avg={avg:.1f}, range={lo:.1f}-{hi:.1f}")

# Score distribution within Tier-B
print("\nScore distribution within Tier-B:")
brackets = [(40, 45, 0), (45, 50, 0), (50, 55, 0), (55, 60, 0)]
for lo, hi, _ in brackets:
    count = sum(1 for d in tier_b if lo <= d["quality_score"] < hi)
    print(f"  [{lo}-{hi}): {count}")

# Bottom 10 domains by average B-tier score
print("\nDomain avg scores (Tier-B only):")
domain_scores = {}
for d in tier_b:
    dom = d["file"].split("/")[0] if "/" in d["file"] else d["file"].split("\\")[0]
    domain_scores.setdefault(dom, []).append(d["quality_score"])
for dom, scores in sorted(domain_scores.items(), key=lambda x: sum(x[1])/len(x[1])):
    avg = sum(scores) / len(scores)
    print(f"  {dom}: {len(scores)} docs, avg={avg:.1f}")

# Check dimension breakdown for sample Tier-B docs
print("\nSample Tier-B dimension scores (first 5):")
for d in tier_b[:5]:
    dims = d.get("dimension_scores", {})
    print(f"  {d['file']}: score={d['quality_score']:.1f}, dims={dims}")
