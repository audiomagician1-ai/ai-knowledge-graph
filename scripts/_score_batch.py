import sys
sys.path.insert(0, '.')
from quality_scorer import score_doc
from pathlib import Path

ROOT = Path(r'D:\EchoAgent\projects\ai-knowledge-graph')
files = [
    'data/rag/programming-basics/recursion.md',
    'data/rag/game-design/player-psychology/player-motivation.md',
    'data/rag/level-design/guidance-design/guidance-intro.md',
    'data/rag/game-design/difficulty-curve/difficulty-overview.md',
    'data/rag/game-engine/physics-engine/physics-engine-intro.md',
    'data/rag/game-engine/animation-system/skeleton-system.md',
    'data/rag/3d-art/3da-prop-intro.md',
    'data/rag/english/writing-en/essay-structure.md',
    'data/rag/computer-graphics/anti-aliasing/cg-taa.md',
    'data/rag/mathematics/statistics/linear-regression.md',
]

for f in files:
    p = ROOT / f
    r = score_doc(p)
    print(f'{p.name}: Score={r["quality_score"]:.1f} Tier={r["quality_tier"]}  dim1={r["dim1_specificity"]} dim2={r["dim2_density"]} dim3={r["dim3_sources"]} dim4={r["dim4_structure"]} dim5={r["dim5_teaching"]} unique={r["unique_content_ratio"]:.2f}')
