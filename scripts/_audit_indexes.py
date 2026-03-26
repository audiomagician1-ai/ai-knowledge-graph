"""Audit _index.json files: check if they list all .md files in their domain directory."""
import json
from pathlib import Path

RAG_ROOT = Path("data/rag")

total_missing = 0
total_extra = 0

for domain_dir in sorted(RAG_ROOT.iterdir()):
    if not domain_dir.is_dir() or domain_dir.name.startswith("_"):
        continue
    index_path = domain_dir / "_index.json"

    # Get actual .md files
    actual_files = set()
    for md in domain_dir.rglob("*.md"):
        actual_files.add(md.stem)

    if not index_path.exists():
        if actual_files:
            print(f"MISSING INDEX: {domain_dir.name}/ ({len(actual_files)} .md files)")
        continue

    idx = json.load(open(index_path, encoding="utf-8"))

    # Index format varies — check common formats
    indexed_ids = set()
    if isinstance(idx, list):
        for item in idx:
            if isinstance(item, str):
                indexed_ids.add(item)
            elif isinstance(item, dict):
                indexed_ids.add(item.get("id", item.get("slug", item.get("concept_id", ""))))
    elif isinstance(idx, dict):
        if "concepts" in idx:
            for item in idx["concepts"]:
                if isinstance(item, str):
                    indexed_ids.add(item)
                elif isinstance(item, dict):
                    indexed_ids.add(item.get("id", item.get("slug", "")))
        elif "files" in idx:
            for item in idx["files"]:
                indexed_ids.add(item.get("id", item.get("slug", "")))

    missing = actual_files - indexed_ids
    extra = indexed_ids - actual_files

    if missing or extra:
        print(f"\n{domain_dir.name}/: {len(actual_files)} files, {len(indexed_ids)} indexed")
        if missing:
            total_missing += len(missing)
            for m in sorted(missing)[:5]:
                print(f"  MISSING from index: {m}")
            if len(missing) > 5:
                print(f"  ... and {len(missing)-5} more")
        if extra:
            total_extra += len(extra)
            for e in sorted(extra)[:5]:
                print(f"  EXTRA in index (no file): {e}")
            if len(extra) > 5:
                print(f"  ... and {len(extra)-5} more")

print(f"\nTotal: {total_missing} missing from indexes, {total_extra} extra in indexes")
