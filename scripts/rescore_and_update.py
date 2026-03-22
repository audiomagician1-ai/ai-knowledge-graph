#!/usr/bin/env python3
"""
Rescore all RAG docs and write quality_score + quality_tier back to YAML frontmatter.
Also saves full report JSON.
"""
import json, re, sys, os
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from quality_scorer import run_scoring, generate_report, print_summary, RAG_ROOT, PROJECT_ROOT


def update_frontmatter_field(content: str, key: str, value: str) -> str:
    """Update or insert a field in YAML frontmatter."""
    fm_match = re.match(r"^(---\s*\n)(.*?)(\n---)", content, re.DOTALL)
    if not fm_match:
        return content  # no frontmatter, skip

    fm_body = fm_match.group(2)
    # Try to replace existing field
    pattern = re.compile(rf'^({re.escape(key)}\s*:).*$', re.MULTILINE)
    if pattern.search(fm_body):
        fm_body = pattern.sub(f'{key}: {value}', fm_body)
    else:
        # Append before end
        fm_body = fm_body.rstrip() + f'\n{key}: {value}'

    return fm_match.group(1) + fm_body + fm_match.group(3) + content[fm_match.end():]


def main():
    print("=== Rescore & Update YAML Frontmatter ===")
    print(f"RAG Root: {RAG_ROOT}")
    print(f"Time: {datetime.now().isoformat()}\n")

    # Run full scoring
    results = run_scoring()
    if not results:
        print("ERROR: No documents found!")
        sys.exit(1)

    report = generate_report(results)
    print_summary(report)

    # Write scores back to files
    updated = 0
    errors = 0
    for r in results:
        fpath = RAG_ROOT / r["file"]
        if not fpath.exists():
            errors += 1
            continue

        content = fpath.read_text(encoding="utf-8", errors="replace")

        # Only update files that have frontmatter
        if not content.startswith("---"):
            continue

        score_val = str(r["quality_score"])
        tier_val = f'"{r["quality_tier"]}"'
        scorer_ver = '"scorer-v2.0"'
        scored_date = f'"{datetime.now().strftime("%Y-%m-%d")}"'
        unique_ratio = str(r["unique_content_ratio"])

        content = update_frontmatter_field(content, "quality_score", score_val)
        content = update_frontmatter_field(content, "quality_tier", tier_val)
        content = update_frontmatter_field(content, "scorer_version", scorer_ver)
        content = update_frontmatter_field(content, "last_scored", scored_date)
        content = update_frontmatter_field(content, "unique_content_ratio", unique_ratio)

        fpath.write_text(content, encoding="utf-8")
        updated += 1

    print(f"\n=== Update Complete ===")
    print(f"  Updated: {updated}")
    print(f"  Errors:  {errors}")

    # Save report
    out_path = PROJECT_ROOT / "data" / "quality_report.json"
    report_lite = {k: v for k, v in report.items() if k != "all_scores"}
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report_lite, f, ensure_ascii=False, indent=2)
    print(f"  Report: {out_path}")

    detail_path = str(out_path).replace(".json", "_detail.json")
    with open(detail_path, "w", encoding="utf-8") as f:
        json.dump(report["all_scores"], f, ensure_ascii=False, indent=2)
    print(f"  Detail: {detail_path}")


if __name__ == "__main__":
    main()
