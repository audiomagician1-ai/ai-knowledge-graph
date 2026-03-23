#!/usr/bin/env python3
"""Score specific docs to check quality after rewrite."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from quality_scorer import score_doc, RAG_ROOT

targets = sys.argv[1:] if len(sys.argv) > 1 else [
    "ai-engineering/supervised-learning.md",
    "economics/structural-transformation.md",  
    "ai-engineering/hash-table.md",
]

for t in targets:
    # Try direct, then search
    p = RAG_ROOT / t.replace("/", "\\")
    if not p.exists():
        # Search recursively
        parts = t.split("/")
        domain = parts[0]
        fname = parts[-1] if parts[-1].endswith(".md") else parts[-1] + ".md"
        found = list((RAG_ROOT / domain).rglob(fname))
        if found:
            p = found[0]
        else:
            print(f"NOT FOUND: {t}")
            continue
    
    r = score_doc(p)
    print(f"{r['quality_score']:5.1f} [{r['quality_tier']}] {t}")
    print(f"  dim1(specificity)={r['dim1_specificity']}  dim2(density)={r['dim2_density']}  "
          f"dim3(sources)={r['dim3_sources']}  dim4(structure)={r['dim4_structure']}  dim5(teaching)={r['dim5_teaching']}")
    print(f"  unique_ratio={r['unique_content_ratio']:.3f}  plain_chars={r['plain_chars']}  "
          f"has_citation={r.get('has_citation',False)}  has_textbook={r.get('has_textbook',False)}")
    print()
