"""Debug why batch-search-plan generates 0 plans."""
import json
from pathlib import Path

SEED_ROOT = Path("data/seed")
QUALITY_DETAIL = Path("data/quality_report_detail.json")

domain = "biology"
seed_path = SEED_ROOT / domain / "seed_graph.json"

with open(seed_path, "r", encoding="utf-8") as f:
    seed = json.load(f)

concept_map = {}
for c in seed.get("concepts", []):
    cid = c.get("id", "")
    concept_map[cid] = c

print(f"concept_map size: {len(concept_map)}")
print(f"concept_map keys sample: {list(concept_map.keys())[:5]}")

with open(QUALITY_DETAIL, "r", encoding="utf-8") as f:
    qd = json.load(f)

qd_bio = [d for d in qd if d.get("domain") == domain]
print(f"biology entries: {len(qd_bio)}")

qd_bio = [d for d in qd_bio if d.get("generation_method") != "research-rewrite-v2"]
print(f"after filter: {len(qd_bio)}")

qd_bio.sort(key=lambda x: (not x.get("is_milestone", False), x.get("quality_score", 0)))
candidates = qd_bio[:10]

print(f"candidates: {len(candidates)}")
for c in candidates[:5]:
    file_val = c.get("file", "")
    # The script uses split("/") but on Windows paths might use backslash
    cid_slash = file_val.split("/")[-1].replace(".md", "")
    cid_bslash = file_val.split("\\")[-1].replace(".md", "")
    print(f"  file: {file_val}")
    print(f"    cid(slash): {cid_slash} -> in map: {cid_slash in concept_map}")
    print(f"    cid(bslash): {cid_bslash} -> in map: {cid_bslash in concept_map}")
