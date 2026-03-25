#!/usr/bin/env python3
"""Find duplicate RAG files and determine which to delete."""
import json
from pathlib import Path
from collections import defaultdict

RAG_ROOT = Path("data/rag")
SEED_ROOT = Path("data/seed")

# Load seed data to determine canonical domain for each concept
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

# Find duplicates
slug_files = defaultdict(list)
for md in RAG_ROOT.rglob("*.md"):
    if md.name.startswith("_"):
        continue
    slug_files[md.stem].append(md)

dupes = {k: v for k, v in slug_files.items() if len(v) > 1}
print(f"Found {len(dupes)} duplicate slugs")

to_delete = []
ambiguous = []

for slug, files in sorted(dupes.items()):
    canon = canonical_domain.get(slug)
    if not canon:
        ambiguous.append((slug, files))
        continue
    for f in files:
        domain = f.relative_to(RAG_ROOT).parts[0]
        if domain != canon:
            to_delete.append(f)
            print(f"DELETE: {f.relative_to(RAG_ROOT)}  (canonical={canon})")

print(f"\nTotal to delete: {len(to_delete)}")
if ambiguous:
    print(f"Ambiguous (no seed data): {len(ambiguous)}")
    for slug, files in ambiguous:
        print(f"  {slug}: {[str(f.relative_to(RAG_ROOT)) for f in files]}")

