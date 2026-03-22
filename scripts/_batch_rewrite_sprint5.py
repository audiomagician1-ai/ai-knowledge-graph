#!/usr/bin/env python3
"""Sprint 5 batch rewrite - writes pre-generated content to files."""
import re, sys
from pathlib import Path
from datetime import datetime

RAG_ROOT = Path(__file__).resolve().parent.parent / "data" / "rag"

def update_frontmatter(content, method="llm-rewrite-v2"):
    fm_match = re.match(r"^(---\s*\n)(.*?)(\n---)", content, re.DOTALL)
    if not fm_match:
        return content
    fm = fm_match.group(2)
    today = datetime.now().strftime("%Y-%m-%d")
    def sf(fm, k, v):
        p = re.compile(rf'^({re.escape(k)}\s*:).*$', re.MULTILINE)
        return p.sub(f'{k}: {v}', fm) if p.search(fm) else fm.rstrip() + f'\n{k}: {v}'
    ver = re.search(r'content_version:\s*(\d+)', fm)
    nv = int(ver.group(1)) + 1 if ver else 3
    fm = sf(fm, "content_version", str(nv))
    fm = sf(fm, "generation_method", f'"{method}"')
    fm = sf(fm, "quality_tier", '"pending-rescore"')
    fm = sf(fm, "last_scored", f'"{today}"')
    src_p = re.compile(r'sources:.*?(?=\n\w|\n---|\Z)', re.DOTALL)
    ns = f'sources:\n  - type: "ai-generated"\n    model: "claude-sonnet-4-20250514"\n    prompt_version: "{method}"'
    fm = src_p.sub(ns, fm) if src_p.search(fm) else fm.rstrip() + '\n' + ns
    return fm_match.group(1) + fm + fm_match.group(3) + content[fm_match.end():]

def rewrite_file(rel_path, new_body, extra_sources=None):
    fpath = RAG_ROOT / rel_path
    if not fpath.exists():
        print(f"  NOT FOUND: {fpath}")
        return False
    content = fpath.read_text(encoding="utf-8", errors="replace")
    updated = update_frontmatter(content)
    # If extra sources, inject into frontmatter
    if extra_sources:
        fm_match = re.match(r"^(---\s*\n)(.*?)(\n---)", updated, re.DOTALL)
        if fm_match:
            fm = fm_match.group(2)
            src_p = re.compile(r'sources:.*?(?=\n\w|\n---|\Z)', re.DOTALL)
            fm = src_p.sub(extra_sources, fm) if src_p.search(fm) else fm
            updated = fm_match.group(1) + fm + fm_match.group(3) + updated[fm_match.end():]
    # Replace body
    fm_match = re.match(r"^(---\s*\n.*?\n---)\s*\n?", updated, re.DOTALL)
    if fm_match:
        new_content = fm_match.group(1) + "\n" + new_body.strip() + "\n"
    else:
        new_content = new_body.strip() + "\n"
    fpath.write_text(new_content, encoding="utf-8")
    print(f"  OK: {rel_path} ({len(new_body)} chars)")
    return True

if __name__ == "__main__":
    # Import content from the content module
    from _sprint5_content import DOCUMENTS
    ok = 0
    for doc in DOCUMENTS:
        src_text = doc.get("sources_yaml", None)
        if rewrite_file(doc["path"], doc["body"], src_text):
            ok += 1
    print(f"\nDone: {ok}/{len(DOCUMENTS)} files rewritten")
