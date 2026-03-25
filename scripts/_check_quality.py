"""Quick quality report reader."""
import json
import os

report_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'quality_report.json')
r = json.load(open(report_path, 'r', encoding='utf-8'))

print("Total:", r['total_docs'])
print("Avg:", r['avg_score'])
print("Tiers:", r['tier_distribution'])

# Domain summary
ds = r.get('domain_summary', {})
items = sorted(ds.items(), key=lambda x: x[1].get('avg_score', 0))
print("\nDomains by avg score (worst first):")
for k, v in items[:25]:
    t = v.get('tiers', {})
    print(f"  {k}: avg={v.get('avg_score',0):.1f} total={v.get('count',0)} S={t.get('S',0)} A={t.get('A',0)} B={t.get('B',0)} C={t.get('C',0)}")

print("\nTotal Tier-B:", r['tier_distribution'].get('B', 0))
b_total = sum(v.get('tiers',{}).get('B',0) for v in ds.values())
print("Tier-B sum from domains:", b_total)
