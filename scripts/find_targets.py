"""Find valid target concept IDs for cross-sphere links"""
import json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
seed_dir = os.path.join(BASE, "data", "seed")

# Build index: domain -> {id: name}
domain_concepts = {}
for d in os.listdir(seed_dir):
    sg = os.path.join(seed_dir, d, "seed_graph.json")
    if os.path.isfile(sg):
        data = json.load(open(sg, "r", encoding="utf-8"))
        key = "concepts" if "concepts" in data else "nodes"
        domain_concepts[d] = {n["id"]: n["name"] for n in data[key]}

# Search for keywords in each domain
searches = {
    "game-audio-music": ["reverb", "wwise", "fmod", "mix", "adaptive"],
    "game-engine": ["audio", "sound"],
    "animation": ["notify", "blend", "facial"],
    "vfx": ["screen", "shake", "emitter", "particle"],
    "game-design": ["feedback", "juice", "feel"],
    "game-ui-ux": ["click", "feedback", "screen", "accessibility"],
    "narrative-design": ["environment", "dialogue", "storytell"],
    "technical-art": ["python", "tool", "plugin"],
    "level-design": ["spatial", "hierarchy", "zone"],
    "software-engineering": ["git", "version", "test"],
    "psychology": ["percep", "emotion", "cognit"],
    "physics": ["wave", "sound", "oscillat"],
    "multiplayer-network": ["voice", "chat"],
}

for domain, keywords in searches.items():
    if domain not in domain_concepts:
        print(f"\n--- {domain}: NOT FOUND ---")
        continue
    concepts = domain_concepts[domain]
    print(f"\n--- {domain} ({len(concepts)} concepts) ---")
    for kw in keywords:
        matches = [(cid, name) for cid, name in concepts.items() if kw.lower() in cid.lower() or kw.lower() in name.lower()]
        if matches:
            for cid, name in matches[:3]:
                print(f"  [{kw}] {cid} = {name}")
        else:
            print(f"  [{kw}] no match")
