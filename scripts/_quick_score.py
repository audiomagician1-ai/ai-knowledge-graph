import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from pathlib import Path
from quality_scorer import score_doc

BASE = Path(r'D:\EchoAgent\projects\ai-knowledge-graph')
files = [
    'data/rag/game-engine/rendering-pipeline/render-pipeline-intro.md',
    'data/rag/writing/creative-writing/creative-overview.md',
]

for f in files:
    r = score_doc(BASE / f)
    name = f.split('/')[-1]
    print(f"=== {name} ===")
    print(f"  Keys: {list(r.keys())}")
    total = r.get('total', r.get('score', r.get('quality_score', 'N/A')))
    tier = r.get('tier', r.get('quality_tier', 'N/A'))
    print(f"  Total: {total}  Tier: {tier}")
    for k, v in sorted(r.items()):
        if k.startswith('dim'):
            print(f"  {k}: {v}")
    print(f"  unique_content_ratio: {r.get('unique_content_ratio', 'N/A')}")
    print()
