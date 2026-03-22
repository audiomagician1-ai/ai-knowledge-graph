#!/usr/bin/env python3
"""
Batch LLM Rewrite v2 — True AI-powered RAG quality improvement.

Unlike ai-rewrite-v1 (template string concat), this script actually calls
an LLM API to generate concept-specific educational content.

Strategy:
  - Uses Anthropic Claude API via httpx
  - Prompt designed to produce unique, concept-specific content
  - Explicitly bans all template patterns detected by quality_scorer v2
  - Targets quality_score 55-75 (Tier-B+/A) without web research
  - Rate-limited to respect API limits

Usage:
    python scripts/batch_llm_rewrite.py --domain mathematics --max 5
    python scripts/batch_llm_rewrite.py --domain physics --max 10 --dry-run
    python scripts/batch_llm_rewrite.py --tier C --max 20
    python scripts/batch_llm_rewrite.py --concepts "newtons-first-law,cell-membrane"
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import httpx

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
RAG_ROOT = PROJECT_ROOT / "data" / "rag"
SEED_ROOT = PROJECT_ROOT / "data" / "seed"
QUALITY_DETAIL = PROJECT_ROOT / "data" / "quality_report_detail.json"
LOG_FILE = PROJECT_ROOT / "data" / "llm_rewrite_log.json"

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 3000
RATE_LIMIT_DELAY = 2.0  # seconds between API calls

# ─── Anti-template system prompt ───

SYSTEM_PROMPT = """You are an expert educational content writer. Write in Chinese (Simplified).

Your task: Write a focused, concept-specific teaching document for a knowledge graph RAG system.

CRITICAL RULES - VIOLATIONS WILL BE REJECTED:

1. EVERY paragraph must contain information SPECIFIC to this concept. No generic filler.
2. BANNED PHRASES (using any of these = instant failure):
   - "是X的核心组成部分之一"
   - "在X的实践中，Y决定了系统行为的关键特征"
   - "当X参数或条件发生变化时，整体表现会产生显著差异"
   - "深入理解X需要结合Y的基本原理进行分析"
   - "明确X的边界和适用条件，区分它与相近概念的差异"
   - "理解X内部各要素的相互作用方式"
   - "将X的原理映射到Y的实际场景中"
   - "真正掌握X的标志是能在具体场景中灵活运用"
   - "起到承上启下的作用，连接基础概念与高级应用"
   - "提供了必要的概念基础"
   - "在X基础上进一步拓展"
   - "如何判断X的应用是否超出了其理论适用范围"
   - "标志着学习者在该领域达到了重要的能力节点"
   - Any sentence that could apply to ANY concept by swapping the name

3. REQUIRED content quality:
   - Include at least ONE specific number, date, name, or formula unique to this concept
   - Each section must teach something a student couldn't learn from any other concept's page
   - Common misconceptions must be SPECIFIC to this concept (not generic "don't confuse X with Y")
   - If a formula exists for this concept, include it with variable definitions

4. Structure (output ONLY the body, NO YAML frontmatter):
   # [Concept Name]
   ## 概述 (2-3 paragraphs: definition, history/origin, why it matters)
   ## 核心原理 (3+ subsections with SPECIFIC details)
   ## 实际应用 (concrete examples from the domain)
   ## 常见误区 (2-3 concept-specific misconceptions)
   ## 知识关联 (how it connects to prerequisites and next topics)

5. Length: 1200-2000 Chinese characters of substantive content."""


def build_user_prompt(concept: dict) -> str:
    """Build the user prompt from concept metadata."""
    prereqs = ", ".join(concept.get("prerequisites", [])) or "none"
    nexts = ", ".join(concept.get("next_concepts", [])) or "none"

    return f"""Write a teaching document for:

Concept: {concept['name']}
Domain: {concept['domain_name']} > {concept['subdomain_name']}
Description: {concept['description']}
Difficulty: {concept['difficulty']}/9
Prerequisites: {prereqs}
Next concepts: {nexts}

Remember: EVERY sentence must be specific to "{concept['name']}". Generic filler = rejection."""


def call_llm(system: str, user: str) -> str:
    """Call Anthropic Claude API."""
    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "system": system,
        "messages": [{"role": "user", "content": user}],
    }

    with httpx.Client(timeout=60.0) as client:
        resp = client.post(API_URL, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    # Extract text from response
    content_blocks = data.get("content", [])
    text_parts = [b["text"] for b in content_blocks if b.get("type") == "text"]
    return "\n".join(text_parts)


def load_seed_data(domain_filter=None):
    """Load seed graph data (reused from batch_ai_rewrite.py logic)."""
    concept_map = {}
    subdomain_names = {}
    domain_names = {}
    edges_map = {}

    for domain_dir in sorted(SEED_ROOT.iterdir()):
        if not domain_dir.is_dir():
            continue
        if domain_filter and domain_dir.name != domain_filter:
            continue

        seed_path = domain_dir / "seed_graph.json"
        if not seed_path.is_file():
            continue

        with open(seed_path, "r", encoding="utf-8") as f:
            sg = json.load(f)

        d_info = sg.get("domain", {})
        if isinstance(d_info, dict):
            domain_id = d_info.get("id", domain_dir.name)
            domain_name = d_info.get("name", domain_dir.name)
        else:
            domain_id = domain_dir.name
            domain_name = domain_dir.name
        domain_names[domain_id] = domain_name

        for sd in sg.get("subdomains", []):
            subdomain_names[sd["id"]] = sd.get("name", sd["id"])

        milestone_ids = set()
        for m in sg.get("milestones", []):
            if isinstance(m, str):
                milestone_ids.add(m)
            elif isinstance(m, dict):
                milestone_ids.add(m.get("id", m.get("concept_id", "")))

        for e in sg.get("edges", []):
            src = e.get("source_id", e.get("source", e.get("from", "")))
            tgt = e.get("target_id", e.get("target", e.get("to", "")))
            if src and tgt:
                edges_map.setdefault(tgt, {"prereqs": [], "next": []})
                edges_map[tgt]["prereqs"].append(src)
                edges_map.setdefault(src, {"prereqs": [], "next": []})
                edges_map[src]["next"].append(tgt)

        for c in sg.get("concepts", []):
            cid = c["id"]
            concept_map[cid] = {
                "id": cid,
                "name": c.get("name", cid),
                "description": c.get("description", ""),
                "domain": c.get("domain_id", domain_id),
                "domain_name": domain_names.get(c.get("domain_id", domain_id), domain_id),
                "subdomain_id": c.get("subdomain_id", ""),
                "subdomain_name": subdomain_names.get(c.get("subdomain_id", ""), ""),
                "difficulty": c.get("difficulty", 1),
                "is_milestone": cid in milestone_ids or c.get("is_milestone", False),
            }

    for cid, info in concept_map.items():
        e = edges_map.get(cid, {"prereqs": [], "next": []})
        info["prerequisites"] = [
            concept_map[p]["name"] for p in e["prereqs"][:5] if p in concept_map
        ]
        info["next_concepts"] = [
            concept_map[n]["name"] for n in e["next"][:5] if n in concept_map
        ]

    return concept_map


def find_rag_file(concept_id: str, domain: str) -> Path:
    """Find the RAG .md file for a concept."""
    domain_dir = RAG_ROOT / domain
    if domain_dir.exists():
        for md_file in domain_dir.rglob(f"{concept_id}.md"):
            return md_file
    # Check ai-engineering subdomain dirs
    for subdir in RAG_ROOT.iterdir():
        if subdir.is_dir():
            check = subdir / f"{concept_id}.md"
            if check.exists():
                return check
    return None


def update_frontmatter(content: str, method: str = "llm-rewrite-v2") -> str:
    """Update YAML frontmatter with new metadata."""
    fm_match = re.match(r"^(---\s*\n)(.*?)(\n---)", content, re.DOTALL)
    if not fm_match:
        return content

    fm_body = fm_match.group(2)
    today = datetime.now().strftime("%Y-%m-%d")

    def set_field(fm: str, key: str, value: str) -> str:
        pattern = re.compile(rf'^({re.escape(key)}\s*:).*$', re.MULTILINE)
        if pattern.search(fm):
            return pattern.sub(f'{key}: {value}', fm)
        return fm.rstrip() + f'\n{key}: {value}'

    # Increment content_version
    ver_match = re.search(r'content_version:\s*(\d+)', fm_body)
    new_ver = int(ver_match.group(1)) + 1 if ver_match else 3

    fm_body = set_field(fm_body, "content_version", str(new_ver))
    fm_body = set_field(fm_body, "generation_method", f'"{method}"')
    fm_body = set_field(fm_body, "quality_tier", '"pending-rescore"')
    fm_body = set_field(fm_body, "last_scored", f'"{today}"')

    # Update sources
    src_pattern = re.compile(r'sources:.*?(?=\n\w|\n---|\Z)', re.DOTALL)
    new_sources = f'sources:\n  - type: "ai-generated"\n    model: "{MODEL}"\n    prompt_version: "{method}"'
    if src_pattern.search(fm_body):
        fm_body = src_pattern.sub(new_sources, fm_body)

    return fm_match.group(1) + fm_body + fm_match.group(3) + content[fm_match.end():]


def load_quality_scores() -> dict:
    """Load quality detail report to find lowest-scoring docs."""
    if not QUALITY_DETAIL.exists():
        return {}
    with open(QUALITY_DETAIL, "r", encoding="utf-8") as f:
        details = json.load(f)
    return {d["file"]: d for d in details}


def main():
    parser = argparse.ArgumentParser(description="Batch LLM Rewrite v2")
    parser.add_argument("--domain", type=str, help="Filter by domain")
    parser.add_argument("--tier", type=str, help="Filter by tier (C, B, A)")
    parser.add_argument("--concepts", type=str, help="Comma-separated concept IDs")
    parser.add_argument("--max", type=int, default=5, help="Max concepts to rewrite")
    parser.add_argument("--dry-run", action="store_true", help="Show prompts without calling API")
    args = parser.parse_args()

    if not API_KEY and not args.dry_run:
        print("ERROR: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    print("=" * 60)
    print(f"Batch LLM Rewrite v2 — {MODEL}")
    print("=" * 60)

    # Load data
    concept_map = load_seed_data(domain_filter=args.domain)
    quality_map = load_quality_scores()
    print(f"Loaded {len(concept_map)} concepts, {len(quality_map)} quality scores")

    # Select candidates
    if args.concepts:
        target_ids = [c.strip() for c in args.concepts.split(",")]
        candidates = [concept_map[cid] for cid in target_ids if cid in concept_map]
    else:
        # Match concepts to their quality scores and sort by score (worst first)
        scored = []
        for cid, info in concept_map.items():
            rag_path = find_rag_file(cid, info["domain"])
            if not rag_path:
                continue
            rel = str(rag_path.relative_to(RAG_ROOT)).replace("\\", "/")
            q = quality_map.get(rel, {})
            score = q.get("quality_score", 999)
            tier = q.get("quality_tier", "?")

            if args.tier and tier != args.tier:
                continue

            # Skip already-rewritten docs
            gen_method = q.get("generation_method", "")
            if "llm-rewrite" in str(gen_method) or "research-rewrite" in str(gen_method):
                continue

            scored.append((score, tier, info))

        scored.sort(key=lambda x: x[0])
        candidates = [s[2] for s in scored[:args.max]]
        print(f"Selected {len(candidates)} worst-scoring candidates")

    if not candidates:
        print("No candidates found!")
        sys.exit(0)

    # Process
    results = []
    for i, concept in enumerate(candidates):
        cid = concept["id"]
        domain = concept["domain"]
        rag_path = find_rag_file(cid, domain)

        if not rag_path:
            print(f"  [{i+1}/{len(candidates)}] SKIP {cid} - no RAG file")
            continue

        print(f"  [{i+1}/{len(candidates)}] Processing {domain}/{cid}...", end="", flush=True)

        user_prompt = build_user_prompt(concept)

        if args.dry_run:
            print(f" DRY RUN")
            print(f"    Prompt preview: {user_prompt[:200]}...")
            results.append({"concept": cid, "status": "dry-run"})
            continue

        try:
            new_body = call_llm(SYSTEM_PROMPT, user_prompt)
            time.sleep(RATE_LIMIT_DELAY)
        except Exception as e:
            print(f" ERROR: {e}")
            results.append({"concept": cid, "status": "error", "error": str(e)})
            continue

        # Read original, update frontmatter, replace body
        content = rag_path.read_text(encoding="utf-8", errors="replace")
        updated_content = update_frontmatter(content, method="llm-rewrite-v2")

        # Extract frontmatter
        fm_match = re.match(r"^(---\s*\n.*?\n---)\s*\n?", updated_content, re.DOTALL)
        if fm_match:
            new_content = fm_match.group(1) + "\n" + new_body.strip() + "\n"
        else:
            new_content = new_body.strip() + "\n"

        rag_path.write_text(new_content, encoding="utf-8")
        print(f" OK ({len(new_body)} chars)")

        results.append({
            "concept": cid,
            "domain": domain,
            "status": "ok",
            "body_chars": len(new_body),
            "timestamp": datetime.now().isoformat(),
        })

    # Summary
    ok = sum(1 for r in results if r["status"] == "ok")
    err = sum(1 for r in results if r["status"] == "error")
    print(f"\nDone: {ok} rewritten, {err} errors")

    # Save log
    if ok > 0 and not args.dry_run:
        log = []
        if LOG_FILE.exists():
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                log = json.load(f)
        log.extend([r for r in results if r["status"] == "ok"])
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(log, f, ensure_ascii=False, indent=2)
        print(f"Log: {LOG_FILE}")


if __name__ == "__main__":
    main()
