#!/usr/bin/env python3
"""Find concepts for cross-sphere linking."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def load_seed(domain):
    p = ROOT / "data" / "seed" / domain / "seed_graph.json"
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def search_concepts(domain, keywords, limit=20):
    data = load_seed(domain)
    results = []
    for c in data["concepts"]:
        name = c["name"].lower()
        desc = c.get("description", "").lower()
        cid = c["id"].lower()
        text = f"{name} {desc} {cid}"
        if any(kw.lower() in text for kw in keywords):
            results.append(c)
    return results[:limit]

print("=== physics concepts related to optics/mechanics/waves ===")
for c in search_concepts("physics", ["光", "optic", "refraction", "reflect", "wave", "lens",
                                       "力学", "motion", "velocity", "collision", "acceleration",
                                       "geometric", "snell", "diffraction", "interference"]):
    print(f"  {c['id']}: {c['name']} (d={c.get('difficulty','?')})")

print("\n=== computer-graphics concepts related to physics/optics/simulation ===")
for c in search_concepts("computer-graphics", ["ray", "光", "refract", "reflect", "physics",
                                                  "光追", "optic", "trace", "brdf", "散射",
                                                  "rendering-equation", "collision", "simulate",
                                                  "fresnel", "snell", "subsurface"]):
    print(f"  {c['id']}: {c['name']} (d={c.get('difficulty','?')})")

print("\n=== ai-engineering concepts related to game/AI agents/procedural ===")
for c in search_concepts("ai-engineering", ["neural", "deep", "reinforcement", "agent",
                                              "procedural", "generate", "nlp", "classify",
                                              "decision", "tree", "search", "pathfind",
                                              "A*", "minimax", "recommend", "diffusion"]):
    print(f"  {c['id']}: {c['name']} (d={c.get('difficulty','?')})")

print("\n=== game-design concepts related to AI/procedural ===")
for c in search_concepts("game-design", ["AI", "procedur", "generat", "NPC", "behavior",
                                           "agent", "random", "probability", "algorithm"]):
    print(f"  {c['id']}: {c['name']} (d={c.get('difficulty','?')})")

print("\n=== technical-art concepts related to AI/ML ===")
for c in search_concepts("technical-art", ["AI", "ML", "machine", "neural", "procedur",
                                             "compute", "shader", "automat", "script"]):
    print(f"  {c['id']}: {c['name']} (d={c.get('difficulty','?')})")
