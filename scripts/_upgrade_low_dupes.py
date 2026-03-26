#!/usr/bin/env python3
"""
Upgrade low-scoring duplicate RAG files by copying body content from the
high-scoring sibling, while preserving correct domain/subdomain frontmatter.

This handles the 24 cross-domain duplicate slugs where one copy scored 40-49
and the other scored 73-96. No API calls needed — purely local file operations.
"""

import json
import re
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAG_ROOT = PROJECT_ROOT / "data" / "rag"
SEED_ROOT = PROJECT_ROOT / "data" / "seed"


def load_seed_concept_meta():
    """Load concept metadata from all seed graphs."""
    meta = {}  # (concept_id, domain_id) -> {subdomain_id, subdomain_name, ...}
    for domain_dir in sorted(SEED_ROOT.iterdir()):
        if not domain_dir.is_dir():
            continue
        sg_path = domain_dir / "seed_graph.json"
        if not sg_path.exists():
            continue
        sg = json.load(open(sg_path, encoding="utf-8"))
        domain_info = sg.get("domain", {})
        domain_id = domain_info.get("id", domain_dir.name) if isinstance(domain_info, dict) else domain_dir.name

        subdomain_names = {}
        for sd in sg.get("subdomains", []):
            subdomain_names[sd["id"]] = sd.get("name", sd["id"])

        for c in sg.get("concepts", []):
            cid = c["id"]
            sdid = c.get("subdomain_id", "")
            meta[(cid, domain_id)] = {
                "domain": domain_id,
                "subdomain": sdid,
                "subdomain_name": subdomain_names.get(sdid, sdid),
                "difficulty": c.get("difficulty", 1),
                "is_milestone": c.get("is_milestone", False),
                "name": c.get("name", cid),
                "description": c.get("description", ""),
            }
    return meta


def find_duplicates():
    """Find RAG files with duplicate slugs across domains."""
    slug_map = defaultdict(list)
    for domain_dir in sorted(RAG_ROOT.iterdir()):
        if not domain_dir.is_dir():
            continue
        for md in domain_dir.rglob("*.md"):
            slug_map[md.stem].append(md)
    return {k: v for k, v in slug_map.items() if len(v) > 1}


def parse_frontmatter(content):
    """Split file into frontmatter and body."""
    fm_match = re.match(r"^(---\s*\n)(.*?)(\n---\s*\n)(.*)", content, re.DOTALL)
    if fm_match:
        return fm_match.group(1), fm_match.group(2), fm_match.group(3), fm_match.group(4)
    return None, None, None, content


def build_frontmatter(concept_meta, old_fm_body=""):
    """Build correct frontmatter for a concept in its domain."""
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")

    lines = [
        f'id: "{concept_meta["domain"]}/{concept_meta["subdomain"]}/{concept_meta["domain"]}-{concept_meta["subdomain"]}"',
    ]
    # Actually, let's keep it simple — just fix the domain/subdomain fields
    # and preserve the rest of the old frontmatter structure
    fm = old_fm_body

    def set_field(fm_text, key, value):
        pattern = re.compile(rf'^{key}:.*$', re.MULTILINE)
        if pattern.search(fm_text):
            return pattern.sub(f'{key}: {value}', fm_text)
        return fm_text + f'\n{key}: {value}'

    fm = set_field(fm, "domain", f'"{concept_meta["domain"]}"')
    fm = set_field(fm, "subdomain", f'"{concept_meta["subdomain"]}"')
    fm = set_field(fm, "subdomain_name", f'"{concept_meta["subdomain_name"]}"')
    fm = set_field(fm, "quality_method", '"content-copy-from-sibling"')
    fm = set_field(fm, "updated_at", f'"{today}"')
    fm = set_field(fm, "quality_tier", '"pending-rescore"')

    return fm


def load_quality_scores():
    """Load quality scores from the detail report."""
    detail_path = PROJECT_ROOT / "data" / "quality_report_detail.json"
    if not detail_path.exists():
        return {}
    detail = json.load(open(detail_path, encoding="utf-8"))
    scores = {}
    for item in detail:
        f = item["file"].replace("\\", "/")
        scores[f] = item["quality_score"]
    return scores


def main():
    seed_meta = load_seed_concept_meta()
    dupes = find_duplicates()
    scores = load_quality_scores()

    print(f"Found {len(dupes)} duplicate slugs")
    upgraded = 0
    skipped = 0

    for slug, files in sorted(dupes.items()):
        # Get scores for each copy
        scored_files = []
        for f in files:
            rel = str(f.relative_to(RAG_ROOT)).replace("\\", "/")
            sc = scores.get(rel, -1)
            scored_files.append((f, sc, rel))

        scored_files.sort(key=lambda x: x[1])
        low_file, low_score, low_rel = scored_files[0]
        high_file, high_score, high_rel = scored_files[-1]

        # Only upgrade if there's a significant gap
        if low_score >= 60 or high_score < 60:
            skipped += 1
            continue

        gap = high_score - low_score
        if gap < 15:
            skipped += 1
            continue

        # Determine which domain the low file belongs to
        # Extract domain from file path
        low_domain = low_rel.split("/")[0]
        meta_key = (slug, low_domain)
        concept_meta = seed_meta.get(meta_key)

        if not concept_meta:
            print(f"  SKIP {slug}: no seed meta for ({slug}, {low_domain})")
            skipped += 1
            continue

        # Read both files
        low_content = open(low_file, "r", encoding="utf-8").read()
        high_content = open(high_file, "r", encoding="utf-8").read()

        # Extract body from high-quality file
        _, _, _, high_body = parse_frontmatter(high_content)

        # Extract frontmatter from low-quality file (to preserve structure)
        fm_start, fm_body, fm_end, _ = parse_frontmatter(low_content)

        if not fm_body:
            print(f"  SKIP {slug}: no frontmatter in {low_rel}")
            skipped += 1
            continue

        # Fix frontmatter with correct domain metadata
        new_fm = build_frontmatter(concept_meta, fm_body)

        # Combine corrected frontmatter + high-quality body
        new_content = fm_start + new_fm + fm_end + high_body

        # Write
        with open(low_file, "w", encoding="utf-8") as f:
            f.write(new_content)

        upgraded += 1
        print(f"  UPGRADED {slug}: {low_rel} ({low_score:.0f} -> ~{high_score:.0f})")
        print(f"    Source: {high_rel} ({high_score:.0f})")
        print(f"    Fixed domain: {concept_meta['domain']}/{concept_meta['subdomain']}")

    print(f"\nDone: {upgraded} upgraded, {skipped} skipped")


if __name__ == "__main__":
    main()
