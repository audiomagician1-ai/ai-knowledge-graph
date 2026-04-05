import pathlib, re
rag = pathlib.Path("data/rag")
for f in rag.rglob("*.md"):
    txt = f.read_text(encoding="utf-8", errors="ignore")[:600]
    m = re.search(r'quality_tier:\s*"?([^"\n]+)', txt)
    if m:
        t = m.group(1).strip().strip('"')
        if t == "B":
            ms = re.search(r"quality_score:\s*([\d.]+)", txt)
            score = ms.group(1) if ms else "N/A"
            print(f"Tier-B: {f.relative_to(rag)} (score: {score})")
