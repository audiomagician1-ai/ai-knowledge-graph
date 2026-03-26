"""Audit RAG frontmatter: find files where domain/subdomain in YAML doesn't match the directory path."""
import re, json
from pathlib import Path
from collections import defaultdict

RAG_ROOT = Path("data/rag")
SEED_ROOT = Path("data/seed")

# Load seed metadata for reference
seed_concepts = {}  # (concept_id, domain) -> {subdomain_id, ...}
for domain_dir in sorted(SEED_ROOT.iterdir()):
    if not domain_dir.is_dir():
        continue
    sg_path = domain_dir / "seed_graph.json"
    if not sg_path.exists():
        continue
    sg = json.load(open(sg_path, encoding="utf-8"))
    domain_info = sg.get("domain", {})
    domain_id = domain_info.get("id", domain_dir.name) if isinstance(domain_info, dict) else domain_dir.name
    subdomain_names = {sd["id"]: sd.get("name", sd["id"]) for sd in sg.get("subdomains", [])}
    for c in sg.get("concepts", []):
        seed_concepts[(c["id"], domain_id)] = {
            "subdomain_id": c.get("subdomain_id", ""),
            "subdomain_name": subdomain_names.get(c.get("subdomain_id", ""), ""),
            "domain_id": domain_id,
        }

mismatches = []
missing_seed = []
total = 0

for domain_dir in sorted(RAG_ROOT.iterdir()):
    if not domain_dir.is_dir() or domain_dir.name.startswith("_"):
        continue
    for md_file in domain_dir.rglob("*.md"):
        total += 1
        content = open(md_file, "r", encoding="utf-8").read()
        fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if not fm_match:
            continue

        fm = fm_match.group(1)
        # Extract fields
        domain_val = re.search(r'^domain:\s*["\']?([^"\'\n]+)', fm, re.MULTILINE)
        subdomain_val = re.search(r'^subdomain:\s*["\']?([^"\'\n]+)', fm, re.MULTILINE)
        concept_id = md_file.stem

        if not domain_val:
            continue

        fm_domain = domain_val.group(1).strip().strip('"').strip("'")
        fm_subdomain = subdomain_val.group(1).strip().strip('"').strip("'") if subdomain_val else ""

        # Determine expected domain from directory
        rel = md_file.relative_to(RAG_ROOT)
        dir_domain = rel.parts[0]

        # Check seed for the correct metadata
        # The RAG directory might be a subdomain name for ai-engineering
        expected_domain = None
        for (cid, dom), meta in seed_concepts.items():
            if cid == concept_id:
                # Check if this file belongs to this domain
                if dom == dir_domain or meta["subdomain_id"] == dir_domain:
                    expected_domain = dom
                    expected_subdomain = meta["subdomain_id"]
                    break

        if expected_domain and fm_domain != expected_domain:
            mismatches.append({
                "file": str(rel),
                "concept": concept_id,
                "fm_domain": fm_domain,
                "expected_domain": expected_domain,
                "fm_subdomain": fm_subdomain,
                "expected_subdomain": expected_subdomain,
            })

print(f"Total files scanned: {total}")
print(f"Domain mismatches: {len(mismatches)}")
for m in mismatches[:30]:
    print(f"  {m['file']}: fm={m['fm_domain']}/{m['fm_subdomain']} expected={m['expected_domain']}/{m['expected_subdomain']}")
