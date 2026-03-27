"""Check for RAG files not marked v2 that are also not in Sprint 6 queue."""
import json, os

PROJECT = r"D:\EchoAgent\projects\AI-Knowledge-Graph"
RAG_ROOT = os.path.join(PROJECT, "data", "rag")
PROGRESS = os.path.join(PROJECT, "data", "tier_b_upgrade_progress_s6.json")

# Load Sprint 6 queue + completed
with open(PROGRESS, "r", encoding="utf-8") as f:
    prog = json.load(f)
in_s6 = set(prog.get("queue", []) + prog.get("completed", []))

# Scan all RAG files
not_v2_not_queued = []
not_v2_total = 0
total = 0

for root, dirs, files in os.walk(RAG_ROOT):
    for fname in files:
        if not fname.endswith(".md"):
            continue
        total += 1
        slug = fname[:-3]  # remove .md
        path = os.path.join(root, fname)
        with open(path, "r", encoding="utf-8") as fh:
            head = fh.read(600)
        if "quality_method: intranet-llm-rewrite-v2" in head:
            continue  # Already v2
        not_v2_total += 1
        if slug not in in_s6:
            domain = os.path.basename(os.path.dirname(root)) if os.path.basename(root) != os.path.basename(RAG_ROOT) else os.path.basename(root)
            # Get relative path from RAG_ROOT
            rel = os.path.relpath(path, RAG_ROOT)
            not_v2_not_queued.append((rel, slug))

print(f"Total RAG files: {total}")
print(f"Not v2: {not_v2_total}")
print(f"Not v2 AND not in S6 queue: {len(not_v2_not_queued)}")
if not_v2_not_queued:
    print(f"\nOrphan files (not covered by Sprint 6):")
    for rel, slug in sorted(not_v2_not_queued)[:50]:
        print(f"  {rel}")
    if len(not_v2_not_queued) > 50:
        print(f"  ... and {len(not_v2_not_queued) - 50} more")
