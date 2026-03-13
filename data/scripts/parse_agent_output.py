"""
解析子 Agent 输出的文档内容，拆分并保存为独立的 Markdown 文件。
"""
import json
import re
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SEED_GRAPH = PROJECT_ROOT / "data" / "seed" / "programming" / "seed_graph.json"
RAG_DIR = PROJECT_ROOT / "data" / "rag"

def load_seed_graph():
    with open(SEED_GRAPH, "r", encoding="utf-8") as f:
        return json.load(f)

def make_frontmatter(concept, subdomain_name):
    tags = concept.get("tags", [])
    return f"""---
id: "{concept['id']}"
name: "{concept['name']}"
subdomain: "{concept['subdomain_id']}"
subdomain_name: "{subdomain_name}"
difficulty: {concept['difficulty']}
is_milestone: {str(concept.get('is_milestone', False)).lower()}
tags: {json.dumps(tags, ensure_ascii=False)}
generated_at: "{time.strftime('%Y-%m-%dT%H:%M:%S')}"
---

# {concept['name']}

"""

def parse_and_save(raw_text: str, subdomain_id: str):
    """Parse ===FILE: xxx.md=== separated content and save to files"""
    graph = load_seed_graph()
    concept_map = {c['id']: c for c in graph['concepts']}
    subdomain_map = {s['id']: s['name'] for s in graph['subdomains']}
    
    # Split by ===FILE: xxx.md===
    parts = re.split(r'===FILE:\s*([^=]+\.md)\s*===', raw_text)
    
    saved = 0
    # parts[0] is preamble, then alternating: filename, content
    for i in range(1, len(parts), 2):
        filename = parts[i].strip()
        content = parts[i + 1].strip() if i + 1 < len(parts) else ""
        
        if not content or len(content) < 100:
            print(f"  ⚠ Skip {filename}: too short ({len(content)} chars)")
            continue
        
        # Extract concept_id from filename (remove .md)
        concept_id = filename.replace('.md', '')
        concept = concept_map.get(concept_id)
        
        if not concept:
            print(f"  ⚠ Skip {filename}: concept '{concept_id}' not found in graph")
            continue
        
        # Build output path
        out_dir = RAG_DIR / subdomain_id
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / filename
        
        # Add frontmatter
        subdomain_name = subdomain_map.get(subdomain_id, subdomain_id)
        full_content = make_frontmatter(concept, subdomain_name) + content
        
        out_path.write_text(full_content, encoding='utf-8')
        saved += 1
        print(f"  ✅ {subdomain_id}/{filename} ({len(content)} chars)")
    
    print(f"\n  Saved {saved} files to {RAG_DIR / subdomain_id}")
    return saved


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python parse_agent_output.py <subdomain_id> <input_file>")
        sys.exit(1)
    
    subdomain_id = sys.argv[1]
    input_file = sys.argv[2]
    
    with open(input_file, 'r', encoding='utf-8') as f:
        raw = f.read()
    
    parse_and_save(raw, subdomain_id)
