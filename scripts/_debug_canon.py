#!/usr/bin/env python3
import json, sys
from pathlib import Path

target = sys.argv[1] if len(sys.argv) > 1 else "storytelling-oral"
SEED_ROOT = Path("data/seed")
canonical_domain = {}

for domain_dir in sorted(SEED_ROOT.iterdir()):
    if not domain_dir.is_dir():
        continue
    seed_path = domain_dir / "seed_graph.json"
    if not seed_path.exists():
        continue
    sg = json.load(open(seed_path, encoding="utf-8"))
    d_info = sg.get("domain", {})
    domain_id = d_info.get("id", domain_dir.name) if isinstance(d_info, dict) else domain_dir.name
    for c in sg.get("concepts", []):
        cid = c["id"]
        if cid not in canonical_domain:
            canonical_domain[cid] = domain_id
        if cid == target:
            print(f"Found in dir={domain_dir.name} domain_id={domain_id}")

print(f"Canonical: {canonical_domain.get(target, 'NOT FOUND')}")

