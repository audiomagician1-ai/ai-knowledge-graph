"""Check remaining concepts that need ai-rewrite-v1."""
import re
from pathlib import Path
from collections import Counter

RAG_ROOT = Path(__file__).resolve().parent.parent / "data" / "rag"

already = 0
remaining = []

for md in RAG_ROOT.rglob("*.md"):
    content = md.read_text(encoding="utf-8", errors="replace")
    m = re.search(r'generation_method:\s*"?(\S+?)"?\s*$', content, re.MULTILINE)
    method = m.group(1) if m else "unknown"
    if method in ("ai-rewrite-v1", "research-rewrite-v2", "human-curated"):
        already += 1
    else:
        remaining.append((str(md.relative_to(RAG_ROOT)), method))

print(f"Already rewritten: {already}")
print(f"Remaining: {len(remaining)}")
print()
for f, m in sorted(remaining):
    print(f"  {m:20s} {f}")