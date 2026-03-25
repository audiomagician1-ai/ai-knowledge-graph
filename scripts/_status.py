#!/usr/bin/env python3
"""Quick status check for background processes."""
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent

# Sprint 6 progress
s6 = root / "data" / "tier_b_upgrade_progress_s6.json"
if s6.exists():
    p = json.load(open(s6, encoding="utf-8"))
    print(f"Sprint 6: {len(p.get('completed', []))} done, {len(p.get('errors', []))} errors")

# Sprint 7 booster progress
s7 = root / "data" / "tier_s_booster_progress.json"
if s7.exists():
    p = json.load(open(s7, encoding="utf-8"))
    print(f"Sprint 7 Booster: {len(p.get('completed', []))} done, {len(p.get('errors', []))} errors")
