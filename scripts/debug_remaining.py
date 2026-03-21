"""Debug remaining template-v1 files."""
import re
from pathlib import Path

RAG = Path(__file__).resolve().parent.parent / "data" / "rag"

remaining = []
for md in RAG.rglob("*.md"):
    c = md.read_text(encoding="utf-8", errors="replace")
    m = re.search(r'generation_method:\s*"?(\S+?)"?\s*$', c, re.MULTILINE)
    method = m.group(1) if m else "unknown"
    if method == "template-v1":
        remaining.append(str(md.relative_to(RAG)))

print(f"template-v1 remaining: {len(remaining)}")
for f in sorted(remaining):
    print(f"  {f}")