#!/usr/bin/env python3
"""Check Tier-B upgrade progress."""
import json
from pathlib import Path

pf = Path("data/tier_b_upgrade_progress.json")
if not pf.exists():
    print("No progress file found")
else:
    p = json.load(open(pf))
    print(f"Completed: {len(p.get('completed', []))}")
    print(f"Errors: {len(p.get('errors', []))}")
    print(f"Started: {p.get('started_at', '?')}")
    print(f"Last updated: {p.get('last_updated', '?')}")
    if p.get('completed'):
        print(f"Last 5 completed: {p['completed'][-5:]}")
