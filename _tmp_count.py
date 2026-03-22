from pathlib import Path; import re; root=Path("data/rag"); tiers={"S":0,"A":0,"B":0,"C":0}; total=0
for f in root.rglob("*.md"):
    text=f.read_text(encoding="utf-8",errors="ignore")
    m=re.search(r"""quality_tier:\s*["\x27](\w+)["\x27]""",text)
    if m:
        t=m.group(1)
        if t in tiers: tiers[t]+=1
        total+=1
print(f"Total: {total}")
for t in ["S","A","B","C"]: print(f"  Tier-{t}: {tiers[t]} ({tiers[t]/total*100:.1f}%)")
