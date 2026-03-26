"""Fix RAG frontmatter domain/subdomain mismatches."""
import re, json
from pathlib import Path
from datetime import datetime

RAG_ROOT = Path("data/rag")
SEED_ROOT = Path("data/seed")
today = datetime.now().strftime("%Y-%m-%d")

# Load seed metadata
seed_concepts = {}
subdomain_name_map = {}
for domain_dir in sorted(SEED_ROOT.iterdir()):
    if not domain_dir.is_dir():
        continue
    sg_path = domain_dir / "seed_graph.json"
    if not sg_path.exists():
        continue
    sg = json.load(open(sg_path, encoding="utf-8"))
    domain_info = sg.get("domain", {})
    domain_id = domain_info.get("id", domain_dir.name) if isinstance(domain_info, dict) else domain_dir.name
    for sd in sg.get("subdomains", []):
        subdomain_name_map[(domain_id, sd["id"])] = sd.get("name", sd["id"])
    for c in sg.get("concepts", []):
        seed_concepts[(c["id"], domain_id)] = {
            "subdomain_id": c.get("subdomain_id", ""),
            "domain_id": domain_id,
        }


def set_field(fm, key, value):
    pattern = re.compile(rf'^{key}:.*$', re.MULTILINE)
    if pattern.search(fm):
        return pattern.sub(f'{key}: {value}', fm)
    return fm + f'\n{key}: {value}'


fixed = 0
for domain_dir in sorted(RAG_ROOT.iterdir()):
    if not domain_dir.is_dir() or domain_dir.name.startswith("_"):
        continue
    for md_file in domain_dir.rglob("*.md"):
        content = open(md_file, "r", encoding="utf-8").read()
        fm_match = re.match(r"^(---\s*\n)(.*?)(\n---)(.*)", content, re.DOTALL)
        if not fm_match:
            continue

        fm_body = fm_match.group(2)
        concept_id = md_file.stem
        rel = md_file.relative_to(RAG_ROOT)
        dir_domain = rel.parts[0]

        # Extract current domain from frontmatter
        domain_val = re.search(r'^domain:\s*["\']?([^"\'\n]+)', fm_body, re.MULTILINE)
        if not domain_val:
            continue
        fm_domain = domain_val.group(1).strip().strip('"').strip("'")

        # Find expected domain from seed
        expected_domain = None
        expected_subdomain = None
        for (cid, dom), meta in seed_concepts.items():
            if cid == concept_id:
                if dom == dir_domain or meta["subdomain_id"] == dir_domain:
                    expected_domain = dom
                    expected_subdomain = meta["subdomain_id"]
                    break

        if not expected_domain or fm_domain == expected_domain:
            continue

        # Fix frontmatter
        new_fm = set_field(fm_body, "domain", f'"{expected_domain}"')
        new_fm = set_field(new_fm, "subdomain", f'"{expected_subdomain}"')
        sd_name = subdomain_name_map.get((expected_domain, expected_subdomain), expected_subdomain)
        new_fm = set_field(new_fm, "subdomain_name", f'"{sd_name}"')
        new_fm = set_field(new_fm, "updated_at", f'"{today}"')

        new_content = fm_match.group(1) + new_fm + fm_match.group(3) + fm_match.group(4)
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(new_content)

        fixed += 1
        print(f"FIXED {rel}: {fm_domain} -> {expected_domain}/{expected_subdomain}")

print(f"\nTotal fixed: {fixed}")
