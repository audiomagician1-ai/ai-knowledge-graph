"""Generate cross-sphere links for the 6 new systems-theory family domains."""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NEW_DOMAINS = ["systems-theory","cybernetics","information-theory","dissipative-structures","synergetics","catastrophe-theory"]

# Load existing links
cl_path = os.path.join(ROOT, "data/seed/cross_sphere_links.json")
data = json.load(open(cl_path))
existing = set()
for l in data["links"]:
    existing.add((l["source_domain"], l["source_id"], l["target_domain"], l["target_id"]))

# Load all domain concepts for matching
all_concepts = {}  # {domain: {concept_id: concept_name}}
domains = json.load(open(os.path.join(ROOT, "data/seed/domains.json")))["domains"]
for d in domains:
    if not d.get("is_active", True):
        continue
    sp = os.path.join(ROOT, "data/seed", d["id"], "seed_graph.json")
    if os.path.exists(sp):
        seed = json.load(open(sp))
        all_concepts[d["id"]] = {c["id"]: c.get("name","") for c in seed["concepts"]}

# Define meaningful cross-links based on conceptual overlap
LINKS = [
    # systems-theory <-> ai-engineering
    ("systems-theory", "feedback-loop", "cybernetics", "negative-feedback", "shared_concept", 0.9),
    ("systems-theory", "feedback-loop", "cybernetics", "positive-feedback", "shared_concept", 0.9),
    ("systems-theory", "self-organization", "synergetics", "self-org-synergetics", "shared_concept", 0.95),
    ("systems-theory", "emergence", "synergetics", "order-parameter-def", "enables", 0.8),
    ("systems-theory", "system-stability", "cybernetics", "stability-analysis", "shared_concept", 0.85),
    ("systems-theory", "complex-adaptive-system", "cybernetics", "adaptive-control", "shared_concept", 0.7),
    ("systems-theory", "system-evolution", "dissipative-structures", "far-from-equilibrium", "enables", 0.7),
    ("systems-theory", "edge-of-chaos", "catastrophe-theory", "catastrophe-overview", "shared_concept", 0.75),
    ("systems-theory", "scale-free-network", "information-theory", "network-info-theory", "shared_concept", 0.7),
    ("systems-theory", "resilience", "cybernetics", "robust-control", "shared_concept", 0.7),

    # cybernetics <-> other domains
    ("cybernetics", "cybernetics-overview", "systems-theory", "system-definition", "shared_concept", 0.85),
    ("cybernetics", "homeostasis", "systems-theory", "system-stability", "shared_concept", 0.8),
    ("cybernetics", "fuzzy-control", "ai-engineering", "fuzzy-logic", "shared_concept", 0.8) if "fuzzy-logic" in all_concepts.get("ai-engineering", {}) else None,
    ("cybernetics", "neural-network-control", "ai-engineering", "neural-networks", "shared_concept", 0.8) if "neural-networks" in all_concepts.get("ai-engineering", {}) else None,
    ("cybernetics", "reinforcement-learning-ctrl", "ai-engineering", "reinforcement-learning", "shared_concept", 0.9) if "reinforcement-learning" in all_concepts.get("ai-engineering", {}) else None,
    ("cybernetics", "feedback-delay", "systems-theory", "system-adaptation", "enables", 0.65),
    ("cybernetics", "pid-control", "mathematics", "differential-equations", "requires", 0.7) if "differential-equations" in all_concepts.get("mathematics", {}) else None,

    # information-theory <-> ai-engineering
    ("information-theory", "shannon-entropy", "ai-engineering", "information-theory-ml", "shared_concept", 0.85) if "information-theory-ml" in all_concepts.get("ai-engineering", {}) else None,
    ("information-theory", "mutual-information", "ai-engineering", "feature-selection", "enables", 0.7) if "feature-selection" in all_concepts.get("ai-engineering", {}) else None,
    ("information-theory", "relative-entropy", "ai-engineering", "loss-functions", "enables", 0.75) if "loss-functions" in all_concepts.get("ai-engineering", {}) else None,
    ("information-theory", "huffman-coding", "ai-engineering", "data-compression", "shared_concept", 0.8) if "data-compression" in all_concepts.get("ai-engineering", {}) else None,
    ("information-theory", "information-definition", "cybernetics", "signal-types", "shared_concept", 0.7),
    ("information-theory", "channel-capacity", "cybernetics", "open-closed-loop", "enables", 0.6),
    ("information-theory", "entropy-rate", "systems-theory", "system-evolution", "shared_concept", 0.65),

    # dissipative-structures <-> other
    ("dissipative-structures", "dissipative-structure-def", "systems-theory", "self-organization", "shared_concept", 0.85),
    ("dissipative-structures", "entropy-production", "information-theory", "shannon-entropy", "shared_concept", 0.7),
    ("dissipative-structures", "bifurcation-theory-ds", "catastrophe-theory", "critical-point-catastrophe", "shared_concept", 0.85),
    ("dissipative-structures", "far-from-equilibrium", "systems-theory", "edge-of-chaos", "shared_concept", 0.8),
    ("dissipative-structures", "turing-pattern", "biology", "pattern-formation", "shared_concept", 0.75) if "pattern-formation" in all_concepts.get("biology", {}) else None,
    ("dissipative-structures", "chemical-oscillation", "biology", "biological-rhythms", "shared_concept", 0.7) if "biological-rhythms" in all_concepts.get("biology", {}) else None,
    ("dissipative-structures", "order-through-fluctuation", "synergetics", "order-parameter-def", "shared_concept", 0.85),

    # synergetics <-> other
    ("synergetics", "synergetics-overview", "systems-theory", "emergence", "shared_concept", 0.85),
    ("synergetics", "slaving-principle-def", "systems-theory", "system-hierarchy", "shared_concept", 0.75),
    ("synergetics", "phase-transition-concept", "dissipative-structures", "instability-mechanism", "shared_concept", 0.8),
    ("synergetics", "symmetry-breaking-syn", "catastrophe-theory", "fold-catastrophe", "shared_concept", 0.75),
    ("synergetics", "laser-synergetics", "physics", "laser-physics", "shared_concept", 0.8) if "laser-physics" in all_concepts.get("physics", {}) else None,
    ("synergetics", "competition-cooperation", "economics", "game-theory-intro", "shared_concept", 0.65) if "game-theory-intro" in all_concepts.get("economics", {}) else None,
    ("synergetics", "critical-slowing-down", "catastrophe-theory", "catastrophe-flags", "shared_concept", 0.8),

    # catastrophe-theory <-> other
    ("catastrophe-theory", "catastrophe-overview", "systems-theory", "system-stability", "shared_concept", 0.8),
    ("catastrophe-theory", "cusp-catastrophe", "dissipative-structures", "bifurcation-theory-ds", "shared_concept", 0.85),
    ("catastrophe-theory", "potential-function", "mathematics", "optimization", "shared_concept", 0.7) if "optimization" in all_concepts.get("mathematics", {}) else None,
    ("catastrophe-theory", "hysteresis-ct", "cybernetics", "feedback-delay", "shared_concept", 0.65),
    ("catastrophe-theory", "structural-stability-ct", "systems-theory", "resilience", "shared_concept", 0.75),
    ("catastrophe-theory", "catastrophe-in-biology", "biology", "evolution", "shared_concept", 0.6) if "evolution" in all_concepts.get("biology", {}) else None,
    ("catastrophe-theory", "catastrophe-in-economics", "economics", "market-equilibrium", "shared_concept", 0.65) if "market-equilibrium" in all_concepts.get("economics", {}) else None,
    ("catastrophe-theory", "catastrophe-in-psychology", "psychology", "cognitive-dissonance", "shared_concept", 0.6) if "cognitive-dissonance" in all_concepts.get("psychology", {}) else None,

    # Within new family: inter-domain links
    ("cybernetics", "second-order-cybernetics", "systems-theory", "mental-models", "shared_concept", 0.7),
    ("information-theory", "communication-model", "cybernetics", "signal-types", "shared_concept", 0.8),
    ("dissipative-structures", "fluctuation-amplification", "synergetics", "order-param-dynamics", "shared_concept", 0.8),
    ("synergetics", "adiabatic-elimination", "dissipative-structures", "dissipative-conditions", "shared_concept", 0.7),
    ("catastrophe-theory", "bimodality", "synergetics", "phase-transition-concept", "shared_concept", 0.75),
]

# Filter out None entries and validate
new_links = []
for link in LINKS:
    if link is None:
        continue
    src_d, src_id, tgt_d, tgt_id, rel, strength = link
    # Validate concept exists
    if src_id not in all_concepts.get(src_d, {}) or tgt_id not in all_concepts.get(tgt_d, {}):
        print(f"  SKIP (concept missing): {src_d}/{src_id} -> {tgt_d}/{tgt_id}")
        continue
    # Skip duplicates
    if (src_d, src_id, tgt_d, tgt_id) in existing:
        print(f"  SKIP (duplicate): {src_d}/{src_id} -> {tgt_d}/{tgt_id}")
        continue
    new_links.append({
        "source_domain": src_d,
        "source_id": src_id,
        "target_domain": tgt_d,
        "target_id": tgt_id,
        "relation": rel,
        "strength": strength,
        "description": f"{all_concepts[src_d].get(src_id, src_id)} ({src_d}) 与 {all_concepts[tgt_d].get(tgt_id, tgt_id)} ({tgt_d}) 之间的跨域关联",
    })

print(f"\nAdding {len(new_links)} new cross-sphere links")
data["links"].extend(new_links)
data["_version"] = "1.4"

with open(cl_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"Total cross-links: {len(data['links'])}")
