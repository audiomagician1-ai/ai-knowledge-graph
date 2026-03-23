#!/usr/bin/env python3
"""Analyze Tier-B docs to understand what's holding them back."""
import json
from pathlib import Path
from statistics import mean

detail = json.load(open(Path(__file__).parent.parent / "data" / "quality_report_detail.json", encoding="utf-8"))
b_docs = [d for d in detail if d["quality_tier"] == "B"]
b_docs.sort(key=lambda x: x["quality_score"])

print(f"=== Worst 5 Tier-B ===")
for d in b_docs[:5]:
    print(f"  {d['quality_score']:5.1f}  {d['file']}")
    print(f"         dim1={d['dim1_specificity']} dim2={d['dim2_density']} dim3={d['dim3_sources']} dim4={d['dim4_structure']} dim5={d['dim5_teaching']}")
print()
print(f"=== Best 5 Tier-B ===")
for d in b_docs[-5:]:
    print(f"  {d['quality_score']:5.1f}  {d['file']}")
    print(f"         dim1={d['dim1_specificity']} dim2={d['dim2_density']} dim3={d['dim3_sources']} dim4={d['dim4_structure']} dim5={d['dim5_teaching']}")
print()

print(f"=== Tier-B Average Dims (n={len(b_docs)}) ===")
for dim in ["dim1_specificity","dim2_density","dim3_sources","dim4_structure","dim5_teaching"]:
    vals = [d[dim] for d in b_docs]
    print(f"  {dim}: avg={mean(vals):.1f}  min={min(vals)}  max={max(vals)}")
print()

# How many would become A-tier if dim3 went from 0 to 40?
would_a_40 = sum(1 for d in b_docs if d["quality_score"] + 0.20 * max(0, 40 - d["dim3_sources"]) >= 60)
print(f"Would become A-tier if dim3(sources) went to 40: {would_a_40}/{len(b_docs)}")
would_a_40_33 = sum(1 for d in b_docs if d["quality_score"] + 0.20 * max(0, 40 - d["dim3_sources"]) + 0.10 * max(0, 33 - d["dim5_teaching"]) >= 60)
print(f"Would become A-tier if dim3=40 AND dim5+33: {would_a_40_33}/{len(b_docs)}")
would_a_80 = sum(1 for d in b_docs if d["quality_score"] + 0.20 * max(0, 80 - d["dim3_sources"]) >= 60)
print(f"Would become A-tier if dim3(sources) went to 80: {would_a_80}/{len(b_docs)}")

# Check generation_method distribution
gen_methods = {}
for d in b_docs:
    gm = d.get("generation_method", "unknown")
    gen_methods[gm] = gen_methods.get(gm, 0) + 1
print(f"\n=== Tier-B Generation Methods ===")
for gm, count in sorted(gen_methods.items(), key=lambda x: -x[1]):
    print(f"  {gm}: {count}")
