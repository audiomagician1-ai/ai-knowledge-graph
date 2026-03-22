#!/usr/bin/env python3
import json
d = json.load(open("data/quality_report_detail.json", encoding="utf-8"))
c_docs = [x for x in d if x["quality_tier"] == "C"]
c_docs.sort(key=lambda x: x["quality_score"])
core = ["mathematics","physics","biology","game-design","software-engineering",
        "game-engine","llm-core","algorithms","cs-fundamentals"]
core_c = [x for x in c_docs if x["domain"] in core]
print(f"Total Tier-C: {len(c_docs)}")
print(f"Core domain Tier-C: {len(core_c)}")
print()
print("Top 20 worst (core domains):")
for i, x in enumerate(core_c[:20]):
    print(f"  {i+1:>2}. {x['quality_score']:>5.1f} [{x['quality_tier']}] {x['domain']}/{x['concept']}  ({x['file']})")
