#!/usr/bin/env python3
"""Analyze rescore results and produce rewrite priority plan."""
import json
from collections import defaultdict
from pathlib import Path

REPORT = Path(__file__).resolve().parent.parent / "data" / "quality_report.json"
DETAIL = Path(__file__).resolve().parent.parent / "data" / "quality_report_detail.json"

report = json.loads(REPORT.read_text(encoding="utf-8"))
details = json.loads(DETAIL.read_text(encoding="utf-8"))

# Group by domain and tier
domain_tiers = defaultdict(lambda: {"S": [], "A": [], "B": [], "C": []})
for d in details:
    domain_tiers[d["domain"]][d["quality_tier"]].append(d)

print("=" * 70)
print("  REWRITE PRIORITY ANALYSIS")
print("=" * 70)

# Priority 1: Tier C domains (worst first)
print("\n--- PRIORITY 1: Tier-C docs (752 total) ---")
print("  These have the lowest quality and should be rewritten first.\n")
c_by_domain = []
for domain, tiers in domain_tiers.items():
    if tiers["C"]:
        c_by_domain.append((domain, len(tiers["C"]), len(tiers["C"]) + len(tiers["B"]) + len(tiers["A"]) + len(tiers["S"])))
c_by_domain.sort(key=lambda x: -x[1])

print(f"  {'Domain':<25} {'Tier-C':>7} {'Total':>7} {'C%':>6}")
print(f"  {'-'*25} {'-'*7} {'-'*7} {'-'*6}")
for domain, c_count, total in c_by_domain:
    print(f"  {domain:<25} {c_count:>7} {total:>7} {c_count/total*100:>5.1f}%")

# Priority 2: High-impact domains (core curriculum)
print("\n--- PRIORITY 2: High-impact domain analysis ---")
print("  Core curriculum domains that learners need most.\n")
core_domains = [
    "mathematics", "physics", "biology", "llm-core",
    "algorithms", "data-structures", "cs-fundamentals",
    "software-engineering", "game-design", "game-engine",
]
for d in core_domains:
    if d in domain_tiers:
        tiers = domain_tiers[d]
        total = sum(len(v) for v in tiers.values())
        avg = sum(doc["quality_score"] for t in tiers.values() for doc in t) / total
        print(f"  {d:<25} docs={total:>4} avg={avg:>5.1f}  S={len(tiers['S'])} A={len(tiers['A'])} B={len(tiers['B'])} C={len(tiers['C'])}")

# Summary stats
print("\n--- EFFORT ESTIMATE ---")
total_c = sum(1 for d in details if d["quality_tier"] == "C")
total_b = sum(1 for d in details if d["quality_tier"] == "B")
print(f"  Tier-C (need full rewrite):    {total_c:>5}")
print(f"  Tier-B (need enhancement):     {total_b:>5}")
print(f"  Tier-A (minor polish):         {sum(1 for d in details if d['quality_tier'] == 'A'):>5}")
print(f"  Tier-S (done):                 {sum(1 for d in details if d['quality_tier'] == 'S'):>5}")
print(f"\n  Total rewrite effort: {total_c + total_b} docs")
print(f"  Suggested batch size: 20 docs/batch")
print(f"  Estimated batches: {(total_c + total_b + 19) // 20}")

# Suggested first batch: worst 20 from core domains
print("\n--- SUGGESTED FIRST BATCH (20 worst from core domains) ---")
core_docs = [d for d in details if d["domain"] in core_domains]
core_docs.sort(key=lambda x: x["quality_score"])
for d in core_docs[:20]:
    print(f"  {d['quality_score']:>5.1f} [{d['quality_tier']}] {d['domain']}/{d['concept']}")

print()
