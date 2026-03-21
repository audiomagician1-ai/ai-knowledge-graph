"""Show non-S tier docs with their generation method."""
import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAG_ROOT = PROJECT_ROOT / "data" / "rag"

data = json.load(open(PROJECT_ROOT / 'data' / 'quality_report_detail.json', 'r', encoding='utf-8'))
non_s = [x for x in data if x['quality_tier'] != 'S']
non_s.sort(key=lambda x: x['quality_score'])
print(f"Total non-S: {len(non_s)}")
print(f"  C: {len([x for x in non_s if x['quality_tier'] == 'C'])}")
print(f"  B: {len([x for x in non_s if x['quality_tier'] == 'B'])}")
print(f"  A: {len([x for x in non_s if x['quality_tier'] == 'A'])}")
print()

for x in non_s:
    fp = RAG_ROOT / x['file']
    gen_method = "?"
    if fp.exists():
        content = fp.read_text(encoding='utf-8', errors='replace')
        m = re.search(r'generation_method:\s*"?([^"\n]+)', content)
        if m:
            gen_method = m.group(1).strip()
    print(f"  {x['quality_score']:5.1f} [{x['quality_tier']}] {x['domain']}/{x['concept']}")
    print(f"         file={x['file']}  gen={gen_method}")
    print(f"         dims: spec={x['dim1_specificity']} dens={x['dim2_density']} src={x['dim3_sources']} struct={x['dim4_structure']} teach={x['dim5_teaching']}")
