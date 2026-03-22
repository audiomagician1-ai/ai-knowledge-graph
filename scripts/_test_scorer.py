#!/usr/bin/env python3
"""Test scorer v2 on sample docs."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from quality_scorer import score_doc, RAG_ROOT
from pathlib import Path

test_files = [
    ("ai-rewrite-v1 (AO-bake)", RAG_ROOT / "3d-art" / "3da-bake-ao.md"),
    ("research-v2 (cell-membrane)", RAG_ROOT / "biology" / "cell-biology" / "cell-membrane.md"),
    ("llm-rewrite-v2 (newtons-1st)", RAG_ROOT / "physics" / "classical-mechanics" / "newtons-first-law.md"),
    ("llm-rewrite-v2 (fractions)", RAG_ROOT / "mathematics" / "arithmetic" / "fractions.md"),
]

for name, fpath in test_files:
    if not fpath.exists():
        print(f"\n=== {name} === NOT FOUND: {fpath}")
        continue
    r = score_doc(fpath)
    print(f"\n=== {name} ===")
    print(f"  Total: {r['quality_score']}  Tier: {r['quality_tier']}")
    print(f"  dim1_specificity: {r['dim1_specificity']}  (unique_ratio: {r['unique_content_ratio']})")
    print(f"  dim2_density:     {r['dim2_density']}")
    print(f"  dim3_sources:     {r['dim3_sources']}  (textbook: {r.get('has_textbook')}, paper: {r.get('has_paper')}, citation: {r.get('has_citation')})")
    print(f"  dim4_structure:   {r['dim4_structure']}  (sections: {r['section_count']})")
    print(f"  dim5_teaching:    {r['dim5_teaching']}  (formula: {r['has_formula']}, code: {r['has_code']}, example: {r['has_example']})")
    print(f"  plain_chars: {r['plain_chars']}")
