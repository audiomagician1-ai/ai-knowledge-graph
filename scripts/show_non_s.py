import json
data = json.load(open('data/quality_report_detail.json', 'r', encoding='utf-8'))
non_s = [d for d in data if d.get('quality_tier') in ('C', 'B', 'A')]
non_s.sort(key=lambda x: x.get('quality_score', 0))
print(f"Total non-S: {len(non_s)}")
print(f"  C: {len([d for d in non_s if d['quality_tier'] == 'C'])}")
print(f"  B: {len([d for d in non_s if d['quality_tier'] == 'B'])}")
print(f"  A: {len([d for d in non_s if d['quality_tier'] == 'A'])}")
print()
for d in non_s:
    print(f"  {d['quality_score']:5.1f} [{d['quality_tier']}] {d['domain']}/{d['concept']} ({d['file']})")
    print(f"         dim1={d['dim1_specificity']} dim2={d['dim2_density']} dim3={d['dim3_sources']} dim4={d['dim4_structure']} dim5={d['dim5_teaching']}")
