import pathlib, re

root = pathlib.Path(r"D:\EchoAgent\projects\ai-knowledge-graph\data\rag")
tiers = {"S": 0, "A": 0, "B": 0, "C": 0, "other": 0}
total = 0

for f in root.rglob("*.md"):
    total += 1
    text = f.read_text(encoding="utf-8", errors="replace")[:500]
    m = re.search(r'quality_tier:\s*"?(\w+)', text)
    if m:
        t = m.group(1)
        if t in tiers:
            tiers[t] += 1
        else:
            tiers["other"] += 1
    else:
        tiers["other"] += 1

print("=== Global Quality Statistics ===")
print("Total docs: {}".format(total))
for t in ["S", "A", "B", "C", "other"]:
    c = tiers[t]
    pct = c / total * 100
    print("  Tier-{}: {} ({:.1f}%)".format(t, c, pct))
print("\nTier-C remaining: {}".format(tiers["C"]))
print("Tier-S total: {}".format(tiers["S"]))
