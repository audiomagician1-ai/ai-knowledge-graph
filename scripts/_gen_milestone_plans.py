"""Generate search plans focusing on milestone concepts across priority domains."""
import json, sys
from pathlib import Path

SEED_ROOT = Path("data/seed")
QUALITY_DETAIL = Path("data/quality_report_detail.json")
DRAFTS_DIR = Path("data/rewrite_drafts")

with open(QUALITY_DETAIL, "r", encoding="utf-8") as f:
    details = json.load(f)

# Priority domains for precise science
priority_domains = ["biology", "mathematics", "economics", "finance", "physics", "philosophy", "psychology", "english", "writing"]

# Collect all milestones needing rewrite
candidates = []
for d in details:
    if d.get("domain") not in priority_domains:
        continue
    if d.get("generation_method") in ("research-rewrite-v2", "ai-rewrite-v1", "hand-crafted"):
        continue
    if d.get("quality_score", 100) >= 80:
        continue
    candidates.append(d)

# Sort: milestones first, then low score
candidates.sort(key=lambda x: (not x.get("is_milestone", False), x.get("quality_score", 0)))

print(f"Total candidates: {len(candidates)}")
ms_count = sum(1 for c in candidates if c.get("is_milestone"))
print(f"  Milestones: {ms_count}")
print(f"  Non-milestones: {len(candidates) - ms_count}")

# Take top 20
top = candidates[:20]

# Load seed data to get concept info
all_seeds = {}
for dom_dir in SEED_ROOT.iterdir():
    if not dom_dir.is_dir():
        continue
    sp = dom_dir / "seed_graph.json"
    if not sp.is_file():
        continue
    with open(sp, "r", encoding="utf-8") as f:
        sg = json.load(f)
    
    d_info = sg.get("domain", {})
    domain_name = d_info.get("name", dom_dir.name) if isinstance(d_info, dict) else dom_dir.name
    
    sd_names = {}
    for sd in sg.get("subdomains", []):
        sd_names[sd["id"]] = sd.get("name", sd["id"])
    
    edges = sg.get("edges", [])
    prereqs = {}
    nexts = {}
    for e in edges:
        src = e.get("source_id", e.get("source", e.get("from", "")))
        tgt = e.get("target_id", e.get("target", e.get("to", "")))
        if src and tgt:
            prereqs.setdefault(tgt, []).append(src)
            nexts.setdefault(src, []).append(tgt)
    
    for c in sg.get("concepts", []):
        cid = c["id"]
        all_seeds[f"{dom_dir.name}/{cid}"] = {
            "id": cid,
            "name": c.get("name", cid),
            "description": c.get("description", ""),
            "domain": dom_dir.name,
            "domain_name": domain_name,
            "subdomain": c.get("subdomain", ""),
            "subdomain_name": sd_names.get(c.get("subdomain", ""), ""),
            "difficulty": c.get("difficulty", 1),
            "is_milestone": c.get("is_milestone", False),
            "prerequisites": prereqs.get(cid, []),
            "next_concepts": nexts.get(cid, []),
        }

# Generate plans
plans = []
for item in top:
    cid = Path(item["file"]).stem
    key = f"{item['domain']}/{cid}"
    ci = all_seeds.get(key)
    if not ci:
        print(f"  SKIP {key}: not found in seed")
        continue
    
    en_name = cid.replace("-", " ").title()
    plan = {
        "concept_id": cid,
        "concept_name": ci["name"],
        "domain": ci["domain"],
        "subdomain": ci["subdomain"],
        "description": ci["description"],
        "difficulty": ci["difficulty"],
        "is_milestone": ci.get("is_milestone", False),
        "prerequisites": ci["prerequisites"][:3],
        "next_concepts": ci["next_concepts"][:3],
        "current_score": item.get("quality_score", 0),
        "search_queries": [
            f"{en_name} Wikipedia definition key concepts",
            f"{en_name} textbook explanation Khan Academy",
            f"{ci['name']} 定义 原理 核心知识点",
            f"{ci['name']} {ci['description']} 教学 要点"
        ]
    }
    plans.append(plan)

# Save
DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
out = DRAFTS_DIR / "priority_milestone_plans.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(plans, f, ensure_ascii=False, indent=2)

print(f"\nGenerated {len(plans)} priority plans -> {out}")
for p in plans:
    ms_tag = " [MILESTONE]" if p["is_milestone"] else ""
    print(f"  {p['domain']}/{p['concept_id']}: {p['concept_name']} (score={p['current_score']:.1f}){ms_tag}")
