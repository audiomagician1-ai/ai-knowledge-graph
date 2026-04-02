"""Merge remaining Sprint 6 items into Sprint 6.5 queue."""
import json

S6 = r"D:\EchoAgent\projects\AI-Knowledge-Graph\data\tier_b_upgrade_progress_s6.json"
S65 = r"D:\EchoAgent\projects\AI-Knowledge-Graph\data\sprint6_5_progress.json"

s6 = json.load(open(S6, "r", encoding="utf-8"))
s65 = json.load(open(S65, "r", encoding="utf-8"))

# Get Sprint 6 remaining (in queue but not completed)
s6_completed = set(s6.get("completed", []))
s6_remaining = [s for s in s6.get("queue", []) if s not in s6_completed]

# Get Sprint 6.5 current queue and completed
s65_completed = set(s65.get("completed", []))
s65_queue = s65.get("queue", [])
s65_queue_set = set(s65_queue)

# Add S6 remaining to S6.5 queue (avoid duplicates)
added = 0
for slug in s6_remaining:
    if slug not in s65_queue_set and slug not in s65_completed:
        s65_queue.append(slug)
        s65_queue_set.add(slug)
        added += 1

s65["queue"] = s65_queue
s65["total"] = len(s65_queue)

json.dump(s65, open(S65, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"Added {added} Sprint 6 remainders to Sprint 6.5 queue")
print(f"Sprint 6.5 queue now: {len(s65_queue)} total, {len(s65_completed)} completed, {len(s65_queue) - len(s65_completed)} remaining")
