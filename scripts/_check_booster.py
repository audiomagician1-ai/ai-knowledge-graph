#!/usr/bin/env python3
"""Check quality of recently boosted docs."""
import json

targets = {"口头叙事", "平行结构", "内分泌系统"}

with open("data/quality_report_detail.json", encoding="utf-8") as f:
    d = json.load(f)

for item in d:
    if item["concept"] in targets:
        print(f"{item['quality_score']:5.1f} [{item['quality_tier']}] "
              f"{item['domain']}/{item['concept']} "
              f"spec={item['dim1_specificity']} den={item['dim2_density']} "
              f"src={item['dim3_sources']} str={item['dim4_structure']} "
              f"ped={item['dim5_teaching']} chars={item['plain_chars']}")
