import json, os
root = os.path.join(os.path.dirname(__file__), "..")

# AI-Engineering IDs
with open(os.path.join(root, "ai-engineering", "seed_graph.json"), "r", encoding="utf-8") as f:
    d = json.load(f)
ai_ids = sorted(c["id"] for c in d["concepts"])
print("=== AI-Engineering relevant concepts ===")
for cid in ai_ids:
    if any(kw in cid for kw in ["entropy", "loss", "cross", "neural", "gpu", "computing", "quantum", "ml-", "machine", "deep", "statistical", "probability", "info"]):
        print(f"  {cid}")

# English IDs  
with open(os.path.join(root, "english", "seed_graph.json"), "r", encoding="utf-8") as f:
    e = json.load(f)
en_ids = sorted(c["id"] for c in e["concepts"])
print("\n=== English relevant concepts ===")
for cid in en_ids:
    if any(kw in cid for kw in ["phon", "sound", "listen", "speak", "pronun"]):
        print(f"  {cid}")
