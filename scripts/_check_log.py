#!/usr/bin/env python3
import json
from pathlib import Path
log = json.load(open(Path(__file__).parent.parent / "data" / "intranet_rewrite_v2_log.json", encoding="utf-8"))
print(f"Total rewritten: {len(log)}")
ok = [r for r in log if r.get("status") == "ok"]
print(f"OK: {len(ok)}")
if ok:
    print(f"Last 5:")
    for r in ok[-5:]:
        print(f"  {r.get('domain','?')}/{r.get('concept','?')} ({r.get('name','?')}) {r.get('body_chars',0)}ch")
    # Domain distribution
    domains = {}
    for r in ok:
        d = r.get("domain", "?")
        domains[d] = domains.get(d, 0) + 1
    print(f"\nDomain distribution:")
    for d, c in sorted(domains.items(), key=lambda x: -x[1]):
        print(f"  {d}: {c}")
