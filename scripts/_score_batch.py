import sys
sys.path.insert(0, '.')
from quality_scorer import score_doc
from pathlib import Path

ROOT = Path(r'D:\EchoAgent\projects\ai-knowledge-graph')
files = [
    'data/rag/game-design/feedback-systems/feedback-intro.md',
    'data/rag/level-design/lighting-narrative/lighting-intro.md',
    'data/rag/game-design/social-systems/social-design-intro.md',
    'data/rag/writing/revision-craft/revision-overview.md',
    'data/rag/level-design/terrain-design/terrain-intro.md',
    'data/rag/game-design/design-docs/design-doc-intro.md',
    'data/rag/writing/academic-writing/academic-overview.md',
    'data/rag/game-engine/resource-management/resource-mgmt-intro.md',
]

for f in files:
    p = ROOT / f
    r = score_doc(p)
    print(f'{p.name}: Score={r["quality_score"]:.1f} Tier={r["quality_tier"]}  dim1={r["dim1_specificity"]} dim2={r["dim2_density"]} dim3={r["dim3_sources"]} dim4={r["dim4_structure"]} dim5={r["dim5_teaching"]} unique={r["unique_content_ratio"]:.2f}')
