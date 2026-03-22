import sys, os
from pathlib import Path
sys.path.insert(0, os.path.dirname(__file__))
from quality_scorer import score_doc

files = [
    'data/rag/physics/classical-mechanics/gravitation.md',
    'data/rag/physics/modern-physics/bohr-model.md',
    'data/rag/physics/classical-mechanics/energy-conservation.md',
    'data/rag/biology/cell-biology/mitochondria.md',
]

base = Path(r'D:\EchoAgent\projects\ai-knowledge-graph')
for f in files:
    path = base / f
    result = score_doc(path)
    name = path.name
    print(f'=== {name} ===')
    print(f'  Total: {result["quality_score"]:.1f}  Tier: {result["quality_tier"]}')
    dims = ['dim1_specificity', 'dim2_density', 'dim3_sources', 'dim4_structure', 'dim5_teaching']
    for d in dims:
        print(f'  {d}: {result[d]}')
    print(f'  unique_content_ratio: {result["unique_content_ratio"]}')
    print()
