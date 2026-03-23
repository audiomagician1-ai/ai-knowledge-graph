import json, os, re, sys
sys.path.insert(0, r'D:\EchoAgent\projects\ai-knowledge-graph\scripts')
from quality_scorer import score_file

samples = [
    r'D:\EchoAgent\projects\ai-knowledge-graph\data\rag\physics\astrophysics\stellar-evolution.md',
    r'D:\EchoAgent\projects\ai-knowledge-graph\data\rag\biology\microbiology\virus-biology.md',
    r'D:\EchoAgent\projects\ai-knowledge-graph\data\rag\english\grammar\nouns.md',
    r'D:\EchoAgent\projects\ai-knowledge-graph\data\rag\game-design\numerical-design\numerical-tuning.md',
    r'D:\EchoAgent\projects\ai-knowledge-graph\data\rag\philosophy\ancient-philosophy\confucius.md',
]
for fp in samples:
    if os.path.exists(fp):
        result = score_file(fp)
        name = os.path.basename(fp).replace('.md','')
        print(f'{name}: score={result["quality_score"]:.1f} tier={result["quality_tier"]} spec={result["dim1_specificity"]} dens={result["dim2_density"]} src={result["dim3_sources"]} struct={result["dim4_structure"]} teach={result["dim5_teaching"]}')
    else:
        print(f'NOT FOUND: {fp}')
