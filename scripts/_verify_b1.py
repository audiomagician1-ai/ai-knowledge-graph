import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from quality_scorer import score_doc

ROOT = pathlib.Path(r"D:\EchoAgent\projects\ai-knowledge-graph")

files = [
    "data/rag/mathematics/statistics/hypothesis-testing.md",
    "data/rag/product-design/product-management/product-roadmap.md",
    "data/rag/writing/writing-fundamentals/sentence-structure.md",
    "data/rag/data-structures/binary-tree.md",
    "data/rag/biology/molecular-biology/gene-regulation.md",
    "data/rag/english/tenses/simple-past.md",
    "data/rag/game-design/systems-design/resource-systems.md",
]

for f in files:
    r = score_doc(ROOT / f)
    name = f.split("/")[-1]
    print("{:45s} | Score: {:5.1f} | Tier: {} | d1={} d2={} d3={} d4={} d5={}".format(
        name, r["quality_score"], r["quality_tier"],
        r["dim1_specificity"], r["dim2_density"], r["dim3_sources"],
        r["dim4_structure"], r["dim5_teaching"]
    ))
