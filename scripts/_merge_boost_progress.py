#!/usr/bin/env python3
"""Merge head + tail boost progress files into a single progress file."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "data"
p1_file = ROOT / "legacy_boost_progress.json"
p2_file = ROOT / "legacy_boost_progress_tail.json"
targets_file = ROOT / "legacy_upgrade_targets.json"

p1 = json.loads(p1_file.read_text(encoding="utf-8")) if p1_file.exists() else {"completed": [], "errors": []}
p2 = json.loads(p2_file.read_text(encoding="utf-8")) if p2_file.exists() else {"completed": [], "errors": []}

merged = {
    "completed": list(set(p1.get("completed", []) + p2.get("completed", []))),
    "errors": p1.get("errors", []) + p2.get("errors", [])
}

p1_file.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")

targets = json.loads(targets_file.read_text(encoding="utf-8"))
done = set(merged["completed"])
remaining = [t for t in targets if t not in done]

print(f"Merged: {len(merged['completed'])} completed, {len(merged['errors'])} errors")
print(f"Total targets: {len(targets)}")
print(f"Remaining: {len(remaining)}")
