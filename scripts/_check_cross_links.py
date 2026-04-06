"""Check cross-sphere links for new domains."""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data = json.load(open(os.path.join(ROOT, "data/seed/cross_sphere_links.json")))
links = data["links"]

new_domains = {"systems-theory","cybernetics","information-theory","dissipative-structures","synergetics","catastrophe-theory"}
hits = [l for l in links if l.get("source_domain") in new_domains or l.get("target_domain") in new_domains]
print(f"Cross-links involving new domains: {len(hits)}/{len(links)}")
for h in hits[:5]:
    print(f"  {h['source_domain']}/{h['source_id']} -> {h['target_domain']}/{h['target_id']}")
