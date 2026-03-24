"""Analyze quality score bottleneck dimensions for Tier-B docs."""
import json

detail = json.load(open('data/quality_report_detail.json', 'r', encoding='utf-8'))

# Filter Tier-B
tier_b = [d for d in detail if d.get('quality_tier') == 'B']
tier_a = [d for d in detail if d.get('quality_tier') == 'A']
tier_s = [d for d in detail if d.get('quality_tier') == 'S']

dims = ['dim1_specificity', 'dim2_density', 'dim3_sources', 'dim4_structure', 'dim5_teaching']
dim_names = ['Specificity(30%)', 'Density(25%)', 'Sources(20%)', 'Structure(15%)', 'Teaching(10%)']

print("Dimension averages by tier:")
print(f"{'Dimension':<20} {'Tier-B':>8} {'Tier-A':>8} {'Tier-S':>8} {'Gap B->A':>10}")
print("-" * 60)
for dim, name in zip(dims, dim_names):
    b_avg = sum(d[dim] for d in tier_b) / len(tier_b) if tier_b else 0
    a_avg = sum(d[dim] for d in tier_a) / len(tier_a) if tier_a else 0
    s_avg = sum(d[dim] for d in tier_s) / len(tier_s) if tier_s else 0
    gap = a_avg - b_avg
    print(f"{name:<20} {b_avg:>8.1f} {a_avg:>8.1f} {s_avg:>8.1f} {gap:>+10.1f}")

# What's holding Tier-B back the most?
print("\nTier-B: Dimension score distribution (0-100 scale)")
for dim, name in zip(dims, dim_names):
    vals = [d[dim] for d in tier_b]
    zeros = sum(1 for v in vals if v == 0)
    low = sum(1 for v in vals if 0 < v <= 30)
    mid = sum(1 for v in vals if 30 < v <= 60)
    high = sum(1 for v in vals if v > 60)
    print(f"  {name:<20} zero={zeros:>5} low={low:>5} mid={mid:>5} high={high:>5}")

# Check generation methods
methods = {}
for d in tier_b:
    # Read the file to check gen method? No, let's use what we have
    pass

# Check key attributes
has_sources = sum(1 for d in tier_b if d.get('has_sources'))
has_textbook = sum(1 for d in tier_b if d.get('has_textbook'))
has_examples = sum(1 for d in tier_b if d.get('has_example'))
print(f"\nTier-B attributes ({len(tier_b)} docs):")
print(f"  has_sources: {has_sources} ({has_sources/len(tier_b)*100:.0f}%)")
print(f"  has_textbook: {has_textbook} ({has_textbook/len(tier_b)*100:.0f}%)")
print(f"  has_example: {has_examples} ({has_examples/len(tier_b)*100:.0f}%)")
