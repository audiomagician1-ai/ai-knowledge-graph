#!/usr/bin/env python3
"""Analyze stubborn Tier-B docs and compare with high-quality examples."""
import json, sys

with open("data/quality_report_detail.json", encoding="utf-8") as f:
    d = json.load(f)

mode = sys.argv[1] if len(sys.argv) > 1 else "stubborn"

if mode == "high":
    high = [i for i in d if i["quality_score"] >= 85]
    high.sort(key=lambda x: -x["quality_score"])
    print(f"High quality docs (>=85): {len(high)}")
    for h in high[:20]:
        print(f"  {h['quality_score']:5.1f}  {h['domain']}/{h['concept']}")
        print(f"         spec={h['dim1_specificity']} den={h['dim2_density']} src={h['dim3_sources']} str={h['dim4_structure']} ped={h['dim5_teaching']}")
        print(f"         chars={h['plain_chars']} formula={h['has_formula']} code={h['has_code']} example={h['has_example']}")
elif mode == "compare":
    # Compare average dimensions of stubborn vs high-quality
    stub = [i for i in d if i["quality_score"] < 46]
    high = [i for i in d if i["quality_score"] >= 80]
    for label, group in [("Stubborn <46", stub), ("High >=80", high)]:
        n = len(group)
        avg = lambda k: sum(i[k] for i in group)/n if n else 0
        print(f"\n{label} ({n} docs):")
        print(f"  Specificity: {avg('dim1_specificity'):.1f}")
        print(f"  Density:     {avg('dim2_density'):.1f}")
        print(f"  Sources:     {avg('dim3_sources'):.1f}")
        print(f"  Structure:   {avg('dim4_structure'):.1f}")
        print(f"  Teaching:    {avg('dim5_teaching'):.1f}")
        print(f"  Chars:       {avg('plain_chars'):.0f}")
        print(f"  Has formula: {sum(1 for i in group if i['has_formula'])/n*100:.0f}%")
        print(f"  Has code:    {sum(1 for i in group if i['has_code'])/n*100:.0f}%")
        print(f"  Has example: {sum(1 for i in group if i['has_example'])/n*100:.0f}%")
else:
    stubborn = [(i["quality_score"], i["domain"], i["concept"],
                 i["dim1_specificity"], i["dim2_density"],
                 i["dim4_structure"], i["dim5_teaching"],
                 i["plain_chars"]) for i in d if i["quality_score"] < 46]
    stubborn.sort()
    print(f"Stubborn Tier-B docs (score < 46): {len(stubborn)}")
    for s, domain, concept, spec, den, stru, ped, chars in stubborn[:30]:
        print(f"{s:6.1f}  {domain:<20} {concept:<35} spec={spec:4.0f} den={den:4.0f} str={stru:4.0f} ped={ped:4.0f} ch={chars}")

