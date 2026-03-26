import json

d = json.load(open("data/quality_report_detail.json", encoding="utf-8"))
score_45 = [x for x in d if abs(x["quality_score"] - 45.0) < 0.1]

dims = ["dim1_specificity", "dim2_density", "dim3_sources", "dim4_structure", "dim5_teaching"]
for dim in dims:
    avg = sum(x[dim] for x in score_45) / len(score_45)
    print(f"{dim}: {avg:.1f}")

avg_chars = sum(x["plain_chars"] for x in score_45) / len(score_45)
print(f"\navg plain_chars: {avg_chars:.0f}")
print(f"has_formula: {sum(1 for x in score_45 if x.get('has_formula'))}/{len(score_45)}")
print(f"has_code: {sum(1 for x in score_45 if x.get('has_code'))}/{len(score_45)}")
print(f"has_example: {sum(1 for x in score_45 if x.get('has_example'))}/{len(score_45)}")
print(f"has_sources: {sum(1 for x in score_45 if x.get('has_sources'))}/{len(score_45)}")

# Check generation method
from collections import Counter
methods = Counter()
for x in score_45:
    # Read front matter from file to get method
    methods[x.get("generation_method", "unknown")] += 1

# Check one sample file's content size vs higher-scoring ones
tier_a = [x for x in d if x["quality_tier"] == "A"]
a_chars = sum(x["plain_chars"] for x in tier_a) / len(tier_a)
print(f"\nTier-A avg chars: {a_chars:.0f}")
print(f"Score-45 avg chars: {avg_chars:.0f}")
print(f"Gap: {a_chars - avg_chars:.0f} chars")
