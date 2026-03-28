import json, os

SEED_DIR = os.path.dirname(os.path.abspath(__file__))
domains_path = os.path.join(SEED_DIR, "domains.json")

with open(domains_path, "r", encoding="utf-8") as f:
    domains_data = json.load(f)
print(f'[OK] domains.json valid, {len(domains_data["domains"])} domains total')

new_domains = ["systems-theory", "cybernetics", "information-theory",
               "dissipative-structures", "synergetics", "catastrophe-theory"]

for d_id in new_domains:
    found = [d for d in domains_data["domains"] if d["id"] == d_id]
    assert len(found) == 1, f"Domain {d_id} not found or duplicate!"

print("[OK] All 6 new domains registered in domains.json")

total_concepts = 0
total_edges = 0
for d_id in new_domains:
    path = os.path.join(SEED_DIR, d_id, "seed_graph.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "domain" in data and "subdomains" in data
    assert "concepts" in data and "edges" in data
    if isinstance(data["domain"], dict):
        assert data["domain"]["id"] == d_id
    concept_ids = set()
    subdomain_ids = {s["id"] for s in data["subdomains"]}
    for cc in data["concepts"]:
        for field in ["id", "name", "description", "domain_id", "subdomain_id", "difficulty", "tags"]:
            assert field in cc, f"{d_id}: concept {cc.get('id','?')} missing {field}"
        assert cc["id"] not in concept_ids, f"{d_id}: dup id {cc['id']}"
        concept_ids.add(cc["id"])
        assert cc["domain_id"] == d_id
        assert cc["subdomain_id"] in subdomain_ids, f"{d_id}: bad subdomain {cc['subdomain_id']}"
    for edge in data["edges"]:
        assert edge["source_id"] in concept_ids, f"{d_id}: bad source {edge['source_id']}"
        assert edge["target_id"] in concept_ids, f"{d_id}: bad target {edge['target_id']}"
    n_c = len(data["concepts"])
    n_e = len(data["edges"])
    n_s = len(data["subdomains"])
    total_concepts += n_c
    total_edges += n_e
    print(f"[OK] {d_id}: {n_s} subdomains, {n_c} concepts, {n_e} edges")

print(f"\n=== TOTAL: 6 domains, {total_concepts} concepts, {total_edges} edges ===")
print("All validations passed!")