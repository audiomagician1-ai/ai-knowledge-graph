#!/usr/bin/env python3
"""Phase 37: Cross-sphere link audit + gap analysis."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def load_seed(domain):
    p = ROOT / "data" / "seed" / domain / "seed_graph.json"
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def load_links():
    p = ROOT / "data" / "seed" / "cross_sphere_links.json"
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def get_concept_ids(domain):
    data = load_seed(domain)
    return {c["id"]: c for c in data.get("concepts", [])}

def main():
    domains_to_check = [
        "game-qa", "software-engineering", "physics",
        "computer-graphics", "ai-engineering", "game-design", "technical-art"
    ]
    
    for domain in domains_to_check:
        concepts = get_concept_ids(domain)
        milestones = {cid: c for cid, c in concepts.items() if c.get("is_milestone")}
        print(f"\n=== {domain} ({len(concepts)} concepts, {len(milestones)} milestones) ===")
        for cid, c in list(milestones.items())[:15]:
            print(f'  * {cid}: {c["name"]} (d={c.get("difficulty","?")})')

    # Validate existing links
    print("\n\n=== VALIDATION ===")
    link_data = load_links()
    links = link_data["links"]
    
    # Load ALL domain concept IDs
    domains_path = ROOT / "data" / "seed" / "domains.json"
    with open(domains_path, "r", encoding="utf-8") as f:
        all_domains = json.load(f)
    
    all_concept_ids = {}
    if isinstance(all_domains, dict):
        all_domains = all_domains.get("domains", [])
    for d in all_domains:
        did = d["id"] if isinstance(d, dict) else d
        try:
            concepts = get_concept_ids(did)
            all_concept_ids[did] = set(concepts.keys())
        except Exception as e:
            print(f"  WARN: Cannot load {did}: {e}")
    
    broken = []
    for i, link in enumerate(links):
        sd = link["source_domain"]
        td = link["target_domain"]
        sid = link["source_id"]
        tid = link["target_id"]
        
        src_ok = sd in all_concept_ids and sid in all_concept_ids[sd]
        tgt_ok = td in all_concept_ids and tid in all_concept_ids[td]
        
        if not src_ok or not tgt_ok:
            broken.append((i, link, src_ok, tgt_ok))
    
    print(f"Total links: {len(links)}")
    print(f"Broken links: {len(broken)}")
    for idx, link, src_ok, tgt_ok in broken:
        issues = []
        if not src_ok:
            issues.append(f"source {link['source_id']}@{link['source_domain']} NOT FOUND")
        if not tgt_ok:
            issues.append(f"target {link['target_id']}@{link['target_domain']} NOT FOUND")
        print(f"  [{idx}] {' | '.join(issues)}")

if __name__ == "__main__":
    main()
