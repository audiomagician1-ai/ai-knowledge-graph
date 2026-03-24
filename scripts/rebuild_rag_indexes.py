#!/usr/bin/env python3
"""Rebuild all _index.json files from current .md files in data/rag/."""
import json, os, re, sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAG_ROOT = PROJECT_ROOT / "data" / "rag"
SEED_ROOT = PROJECT_ROOT / "data" / "seed"

def parse_yaml_frontmatter(content):
    meta = {}
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return meta
    for line in match.group(1).split("\n"):
        line = line.strip()
        if ":" in line and not line.startswith("#") and not line.startswith("-"):
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            meta[key] = val
    return meta

def strip_frontmatter(content):
    return re.sub(r"^---\s*\n.*?\n---\s*\n?", "", content, count=1, flags=re.DOTALL)

def load_seed_concepts(domain_name):
    """Load concept metadata from seed_graph.json."""
    seed_path = SEED_ROOT / domain_name / "seed_graph.json"
    if not seed_path.exists():
        return {}
    with open(seed_path, "r", encoding="utf-8") as f:
        sg = json.load(f)
    concepts = {}
    subdomain_names = {}
    milestone_ids = set()
    for sd in sg.get("subdomains", []):
        subdomain_names[sd["id"]] = sd.get("name", sd["id"])
    for m in sg.get("milestones", []):
        mid = m if isinstance(m, str) else m.get("id", m.get("concept_id", ""))
        milestone_ids.add(mid)
    for c in sg.get("concepts", []):
        cid = c["id"]
        concepts[cid] = {
            "name": c.get("name", cid),
            "domain_id": c.get("domain_id", domain_name),
            "subdomain_id": c.get("subdomain_id", ""),
            "subdomain_name": subdomain_names.get(c.get("subdomain_id", ""), ""),
            "difficulty": c.get("difficulty", 1),
            "is_milestone": cid in milestone_ids or c.get("is_milestone", False),
            "tags": c.get("tags", []),
        }
    return concepts

def build_index_for_domain(domain_dir):
    domain_name = domain_dir.name
    seed_concepts = load_seed_concepts(domain_name)
    
    documents = []
    total_chars = 0
    
    for md_file in sorted(domain_dir.rglob("*.md")):
        if md_file.name.startswith("_"):
            continue
        content = md_file.read_text(encoding="utf-8", errors="replace")
        meta = parse_yaml_frontmatter(content)
        body = strip_frontmatter(content)
        plain = re.sub(r'[#\s\-\*\>\|\`\n]', '', body)
        char_count = len(plain)
        
        concept_id = md_file.stem
        rel_path = str(md_file.relative_to(RAG_ROOT)).replace("\\", "/")
        
        # Get seed metadata if available
        seed = seed_concepts.get(concept_id, {})
        
        doc = {
            "id": concept_id,
            "name": meta.get("concept", meta.get("name", seed.get("name", concept_id))),
            "domain_id": meta.get("domain", domain_name),
            "subdomain_id": meta.get("subdomain", seed.get("subdomain_id", "")),
            "subdomain_name": meta.get("subdomain_name", seed.get("subdomain_name", "")),
            "difficulty": int(meta.get("difficulty", seed.get("difficulty", 1)) or 1),
            "is_milestone": str(meta.get("is_milestone", seed.get("is_milestone", False))).lower() == "true",
            "tags": seed.get("tags", []),
            "file": rel_path,
            "exists": True,
            "char_count": char_count,
        }
        documents.append(doc)
        total_chars += char_count
    
    # Sort by subdomain then name
    documents.sort(key=lambda d: (d["subdomain_id"], d["name"]))
    
    index = {
        "documents": documents,
        "stats": {
            "total": len(documents),
            "total_chars": total_chars,
            "avg_chars": total_chars // max(len(documents), 1),
            "domain": domain_name,
        }
    }
    return index

def main():
    total_docs = 0
    total_domains = 0
    
    for domain_dir in sorted(RAG_ROOT.iterdir()):
        if not domain_dir.is_dir() or domain_dir.name.startswith("_"):
            continue
        
        index = build_index_for_domain(domain_dir)
        
        index_path = domain_dir / "_index.json"
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
        
        n = len(index["documents"])
        avg = index["stats"]["avg_chars"]
        total_docs += n
        total_domains += 1
        print(f"  {domain_dir.name:<30} {n:>4} docs, avg {avg:>5} chars")
    
    # Also build the root _index.json (aggregate)
    all_docs = []
    for domain_dir in sorted(RAG_ROOT.iterdir()):
        if not domain_dir.is_dir() or domain_dir.name.startswith("_"):
            continue
        idx_path = domain_dir / "_index.json"
        if idx_path.exists():
            with open(idx_path, "r", encoding="utf-8") as f:
                idx = json.load(f)
            all_docs.extend(idx["documents"])
    
    root_index = {
        "documents": all_docs,
        "stats": {
            "total": len(all_docs),
            "total_domains": total_domains,
        }
    }
    with open(RAG_ROOT / "_index.json", "w", encoding="utf-8") as f:
        json.dump(root_index, f, ensure_ascii=False, indent=2)
    
    print(f"\n  TOTAL: {total_domains} domains, {total_docs} docs")
    print(f"  Root _index.json: {len(all_docs)} entries")
    print("  Done!")

if __name__ == "__main__":
    main()
