#!/usr/bin/env python3
"""
Fix remaining non-S tier RAG docs.

Sprint 3.1: Targeted rewrite of 52 docs still below Tier-S after Sprint 2.
These docs were missed because they reside in cross-domain directories
(e.g., a finance concept stored in economics/ folder), so the batch rewrite
couldn't match them by domain.

Strategy:
1. Load quality_report_detail.json to identify all non-S docs
2. Match each to its seed graph concept by ID (domain-agnostic)
3. Apply ai-rewrite-v1 content generation
4. Re-score to verify improvement

Usage:
    python scripts/fix_remaining_non_s.py              # Fix all non-S
    python scripts/fix_remaining_non_s.py --dry-run    # Preview only
    python scripts/fix_remaining_non_s.py --tier C     # Fix only Tier-C
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
RAG_ROOT = PROJECT_ROOT / "data" / "rag"
SEED_ROOT = PROJECT_ROOT / "data" / "seed"
LOG_FILE = PROJECT_ROOT / "data" / "ai_rewrite_log.json"

# Import generate_content and related functions from batch_ai_rewrite
sys.path.insert(0, str(SCRIPT_DIR))
from batch_ai_rewrite import (
    DOMAIN_CONTEXT,
    load_seed_data,
    generate_content,
    parse_frontmatter,
    update_frontmatter,
)


def load_non_s_docs(tier_filter=None):
    """Load non-S docs from quality report."""
    report_path = PROJECT_ROOT / "data" / "quality_report_detail.json"
    if not report_path.exists():
        print("ERROR: quality_report_detail.json not found. Run quality_scorer.py first.")
        sys.exit(1)

    data = json.load(open(report_path, "r", encoding="utf-8"))
    non_s = [x for x in data if x["quality_tier"] != "S"]

    if tier_filter:
        non_s = [x for x in non_s if x["quality_tier"] == tier_filter]

    non_s.sort(key=lambda x: x["quality_score"])
    return non_s


def find_concept_in_seed(concept_id, concept_map):
    """Find a concept in the seed graph by ID, regardless of domain."""
    # Direct match
    if concept_id in concept_map:
        return concept_map[concept_id]

    # Try extracting ID from file path
    return None


def extract_concept_id_from_file(filepath):
    """Extract concept ID from a RAG file path like 'economics/behavioral-econ/behavioral-finance.md'."""
    p = Path(filepath)
    return p.stem  # e.g., 'behavioral-finance'


def process_doc(doc, concept_map, dry_run=False):
    """Process a single non-S document."""
    filepath = doc["file"]
    rag_path = RAG_ROOT / filepath

    if not rag_path.exists():
        return {"ok": False, "file": filepath, "error": "File not found"}

    # Extract concept ID from filename
    concept_id = extract_concept_id_from_file(filepath)

    # Find concept in seed graph
    concept = find_concept_in_seed(concept_id, concept_map)
    if not concept:
        return {"ok": False, "file": filepath, "error": f"Concept '{concept_id}' not in seed graph"}

    # Read current content
    content = rag_path.read_text(encoding="utf-8", errors="replace")
    fm_str, old_body, meta = parse_frontmatter(content)

    old_score = doc["quality_score"]
    old_gen = meta.get("generation_method", "unknown")

    # Generate new content using seed graph metadata
    new_body = generate_content(concept)

    # Update frontmatter
    new_fm = update_frontmatter(fm_str, method="ai-rewrite-v1")

    # Combine
    new_content = new_fm + "\n" + new_body.strip() + "\n"

    if dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "file": filepath,
            "concept": concept_id,
            "domain": concept["domain"],
            "old_score": old_score,
            "old_gen": old_gen,
            "old_size": len(content),
            "new_size": len(new_content),
        }

    # Write back
    rag_path.write_text(new_content, encoding="utf-8")

    return {
        "ok": True,
        "file": filepath,
        "concept": concept_id,
        "domain": concept["domain"],
        "old_score": old_score,
        "old_gen": old_gen,
        "old_size": len(content),
        "new_size": len(new_content),
    }


def main():
    parser = argparse.ArgumentParser(description="Fix remaining non-S tier RAG docs")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--tier", type=str, help="Filter by tier (C, B, A)")
    args = parser.parse_args()

    print("=" * 60)
    print("Sprint 3.1 — Fix Remaining Non-S Tier RAG Docs")
    print("=" * 60)

    # Load all seed data (all domains)
    concept_map = load_seed_data()
    print(f"Loaded {len(concept_map)} concepts from seed graphs")

    # Load non-S docs
    non_s = load_non_s_docs(tier_filter=args.tier)
    print(f"Found {len(non_s)} non-S docs to fix")

    if not non_s:
        print("All docs are Tier-S! Nothing to do.")
        return

    # Process each doc
    results = {"success": 0, "skipped": 0, "failed": 0, "details": []}

    for i, doc in enumerate(non_s):
        result = process_doc(doc, concept_map, dry_run=args.dry_run)
        results["details"].append(result)

        if result["ok"]:
            results["success"] += 1
            status = "DRY" if args.dry_run else "OK"
            print(
                f"  [{i+1}/{len(non_s)}] {status} [{doc['quality_tier']}→rewrite] "
                f"{doc['domain']}/{result['concept']} "
                f"(score={result['old_score']:.1f}, gen={result['old_gen']}, "
                f"{result['old_size']}→{result['new_size']}B)"
            )
        else:
            results["failed"] += 1
            print(f"  [{i+1}/{len(non_s)}] FAIL {doc['file']}: {result.get('error')}")

    # Summary
    print(f"\n{'='*60}")
    print(f"Results: {results['success']} rewritten, {results['failed']} failed")

    if not args.dry_run and results["success"] > 0:
        # Append to log
        log_entries = []
        if LOG_FILE.is_file():
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                log_entries = json.load(f)

        for r in results["details"]:
            if r["ok"] and not r.get("dry_run"):
                log_entries.append({
                    "concept_id": r["concept"],
                    "domain": r["domain"],
                    "filepath": r["file"],
                    "timestamp": datetime.now().isoformat(),
                    "method": "ai-rewrite-v1-fix",
                    "old_size": r["old_size"],
                    "new_size": r["new_size"],
                    "old_score": r["old_score"],
                })

        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(log_entries, f, ensure_ascii=False, indent=2)
        print(f"Log appended to {LOG_FILE}")
        print(f"\nNext: Run 'python scripts/quality_scorer.py' to verify scores.")


if __name__ == "__main__":
    main()
