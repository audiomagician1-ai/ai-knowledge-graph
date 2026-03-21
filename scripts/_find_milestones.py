"""Find milestone concepts across all domains that need rewriting."""
import json
from pathlib import Path

SEED_ROOT = Path("data/seed")
QUALITY_DETAIL = Path("data/quality_report_detail.json")

with open(QUALITY_DETAIL, "r", encoding="utf-8") as f:
    details = json.load(f)

# Find all entries where is_milestone=true and not yet rewritten
milestones = [d for d in details 
              if d.get("is_milestone") 
              and d.get("generation_method") != "research-rewrite-v2"
              and d.get("quality_score", 100) < 80]

milestones.sort(key=lambda x: x.get("quality_score", 0))

print(f"Total milestone concepts needing rewrite: {len(milestones)}")
print()

# Group by domain
domain_groups = {}
for m in milestones:
    dom = m.get("domain", "?")
    if dom not in domain_groups:
        domain_groups[dom] = []
    domain_groups[dom].append(m)

for dom in sorted(domain_groups.keys()):
    items = domain_groups[dom]
    print(f"\n{dom} ({len(items)} milestones):")
    for item in items[:5]:
        cid = Path(item["file"]).stem
        print(f"  {cid}: score={item['quality_score']:.1f} [{item['quality_tier']}] gen={item.get('generation_method','?')}")
    if len(items) > 5:
        print(f"  ... and {len(items)-5} more")
