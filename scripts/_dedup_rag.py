#!/usr/bin/env python3
"""
Deduplicate RAG files: for each duplicate slug, keep the LARGEST file, delete smaller copies.

Simple strategy: the largest file has the best content (most recently upgraded).
"""
import sys
from pathlib import Path
from collections import defaultdict

RAG_ROOT = Path("data/rag")
DRY_RUN = "--dry-run" in sys.argv

# Find duplicates
slug_files = defaultdict(list)
for md in RAG_ROOT.rglob("*.md"):
    if md.name.startswith("_"):
        continue
    slug_files[md.stem].append(md)

dupes = {k: v for k, v in slug_files.items() if len(v) > 1}
print(f"Found {len(dupes)} duplicate slugs")

deleted = 0
for slug, files in sorted(dupes.items()):
    # Sort by size descending
    files_sorted = sorted(files, key=lambda f: f.stat().st_size, reverse=True)
    keep = files_sorted[0]
    to_delete = files_sorted[1:]
    
    keep_domain = keep.relative_to(RAG_ROOT).parts[0]
    keep_size = keep.stat().st_size
    
    for f in to_delete:
        del_domain = f.relative_to(RAG_ROOT).parts[0]
        del_size = f.stat().st_size
        rel = f.relative_to(RAG_ROOT)
        if not DRY_RUN:
            f.unlink()
        print(f"  DELETE {rel} ({del_size}B)  [keep {keep_domain}/{slug} ({keep_size}B)]")
        deleted += 1

action = "Would delete" if DRY_RUN else "Deleted"
print(f"\n{action}: {deleted} duplicate files")

