#!/usr/bin/env python3
"""
Batch Tier-B Upgrade — Rewrites lowest-scoring Tier-B docs using MiHoYo intranet API.

Runs in batches with progress tracking. Designed for long-running execution.

Usage:
    python scripts/_batch_tier_b_upgrade.py --max 200
    python scripts/_batch_tier_b_upgrade.py --max 200 --domain mathematics
    python scripts/_batch_tier_b_upgrade.py --max 200 --resume
"""

import argparse, json, os, re, sys, time, traceback
from datetime import datetime
from pathlib import Path
import httpx

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
RAG_ROOT = PROJECT_ROOT / "data" / "rag"
SEED_ROOT = PROJECT_ROOT / "data" / "seed"
QUALITY_DETAIL = PROJECT_ROOT / "data" / "quality_report_detail.json"
LOG_FILE = PROJECT_ROOT / "data" / "tier_b_upgrade_log.json"
PROGRESS_FILE = PROJECT_ROOT / "data" / "tier_b_upgrade_progress.json"

API_BASE = "https://llm-open-ai.mihoyo.com/v1"
API_KEY = "a12488be-58bb-4f52-93d0-26fee71d5507"
MODEL = "mihoyo.claude-4-6-sonnet"
MAX_TOKENS = 3000
RATE_LIMIT_DELAY = 1.5
RETRY_DELAY = 10
MAX_RETRIES = 3

SYSTEM_PROMPT = (
    "You are an expert educational content writer. Write in Chinese (Simplified).\n\n"
    "Your task: Write a focused, concept-specific teaching document for a knowledge graph RAG system.\n\n"
    "CRITICAL RULES - VIOLATIONS WILL BE REJECTED:\n\n"
    "1. EVERY paragraph must contain information SPECIFIC to this concept. No generic filler.\n"
    "2. BANNED PHRASES (using any = instant failure):\n"
    '   - "是X的核心组成部分之一"\n'
    '   - "在X的实践中，Y决定了系统行为的关键特征"\n'
    '   - "当X参数或条件发生变化时，整体表现会产生显著差异"\n'
    '   - "深入理解X需要结合Y的基本原理进行分析"\n'
    '   - "明确X的边界和适用条件，区分它与相近概念的差异"\n'
    '   - "理解X内部各要素的相互作用方式"\n'
    '   - "将X的原理映射到Y的实际场景中"\n'
    '   - "真正掌握X的标志是能在具体场景中灵活运用"\n'
    '   - "起到承上启下的作用，连接基础概念与高级应用"\n'
    '   - "提供了必要的概念基础"\n'
    '   - "在X基础上进一步拓展"\n'
    "   - Any sentence that could apply to ANY concept by swapping the name\n\n"
    "3. REQUIRED content quality:\n"
    "   - Include at least ONE specific number, date, name, or formula unique to this concept\n"
    "   - Each section must teach something a student couldn't learn from any other concept's page\n"
    "   - If a formula exists, include it with variable definitions\n\n"
    "4. Structure (output ONLY the body, NO YAML frontmatter):\n"
    "   # [Concept Name in Chinese]\n"
    "   ## 概述 (2-3 paragraphs: definition, history/origin, why it matters)\n"
    "   ## 核心原理 (3+ subsections with SPECIFIC details)\n"
    "   ## 实际应用 (concrete examples from the domain)\n"
    "   ## 常见误区 (2-3 concept-specific misconceptions)\n"
    "   ## 知识关联 (how it connects to prerequisites and next topics)\n\n"
    "5. Length: 1200-2000 Chinese characters of substantive content."
)


def build_user_prompt(concept):
    prereqs = ", ".join(concept.get("prerequisites", [])) or "none"
    nexts = ", ".join(concept.get("next_concepts", [])) or "none"
    return (
        f"Write a teaching document for:\n\n"
        f"Concept: {concept['name']}\n"
        f"Domain: {concept['domain_name']} > {concept['subdomain_name']}\n"
        f"Description: {concept['description']}\n"
        f"Difficulty: {concept['difficulty']}/9\n"
        f"Prerequisites: {prereqs}\n"
        f"Next concepts: {nexts}\n\n"
        f'Remember: EVERY sentence must be specific to "{concept["name"]}". Generic filler = rejection.'
    )


def call_llm(system, user, retries=MAX_RETRIES):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": MODEL, "max_tokens": MAX_TOKENS,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
    }
    for attempt in range(retries):
        try:
            with httpx.Client(timeout=120.0) as client:
                resp = client.post(f"{API_BASE}/chat/completions", json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            if attempt < retries - 1:
                wait = RETRY_DELAY * (attempt + 1)
                print(f" RETRY({attempt+1}) in {wait}s: {e}", end="", flush=True)
                time.sleep(wait)
            else:
                raise


def load_seed_data(domain_filter=None):
    concept_map, subdomain_names, domain_names, edges_map = {}, {}, {}, {}
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
        domain_id = d_info.get("id", domain_dir.name) if isinstance(d_info, dict) else domain_dir.name
        domain_name = d_info.get("name", domain_dir.name) if isinstance(d_info, dict) else domain_dir.name
        domain_names[domain_id] = domain_name
        for sd in sg.get("subdomains", []):
            subdomain_names[sd["id"]] = sd.get("name", sd["id"])
        milestone_ids = set()
        for m in sg.get("milestones", []):
            milestone_ids.add(m if isinstance(m, str) else m.get("id", m.get("concept_id", "")))
        for e in sg.get("edges", []):
            src = e.get("source_id", e.get("source", e.get("from", "")))
            tgt = e.get("target_id", e.get("target", e.get("to", "")))
            if src and tgt:
                edges_map.setdefault(tgt, {"prereqs": [], "next": []})["prereqs"].append(src)
                edges_map.setdefault(src, {"prereqs": [], "next": []})["next"].append(tgt)
        for c in sg.get("concepts", []):
            cid = c["id"]
            concept_map[cid] = {
                "id": cid, "name": c.get("name", cid),
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
        info["prerequisites"] = [concept_map[p]["name"] for p in e["prereqs"][:5] if p in concept_map]
        info["next_concepts"] = [concept_map[n]["name"] for n in e["next"][:5] if n in concept_map]
    return concept_map


def find_rag_file(concept_id, domain):
    domain_dir = RAG_ROOT / domain
    if domain_dir.exists():
        for md_file in domain_dir.rglob(f"{concept_id}.md"):
            return md_file
    for subdir in RAG_ROOT.iterdir():
        if subdir.is_dir():
            check = subdir / f"{concept_id}.md"
            if check.exists():
                return check
    return None


def update_frontmatter(content, method="intranet-llm-rewrite-v2"):
    fm_match = re.match(r"^(---\s*\n)(.*?)(\n---)", content, re.DOTALL)
    if not fm_match:
        return content
    fm_body = fm_match.group(2)
    today = datetime.now().strftime("%Y-%m-%d")

    def set_field(fm, key, value):
        pat = re.compile(rf'^({re.escape(key)}\s*:).*$', re.MULTILINE)
        return pat.sub(f'{key}: {value}', fm) if pat.search(fm) else fm.rstrip() + f'\n{key}: {value}'

    ver_match = re.search(r'content_version:\s*(\d+)', fm_body)
    new_ver = int(ver_match.group(1)) + 1 if ver_match else 3
    fm_body = set_field(fm_body, "content_version", str(new_ver))
    fm_body = set_field(fm_body, "generation_method", f'"{method}"')
    fm_body = set_field(fm_body, "quality_tier", '"pending-rescore"')
    fm_body = set_field(fm_body, "last_scored", f'"{today}"')
    src_pat = re.compile(r'sources:.*?(?=\n\w|\n---|\Z)', re.DOTALL)
    new_src = f'sources:\n  - type: "ai-generated"\n    model: "{MODEL}"\n    prompt_version: "{method}"'
    if src_pat.search(fm_body):
        fm_body = src_pat.sub(new_src, fm_body)
    return fm_match.group(1) + fm_body + fm_match.group(3) + content[fm_match.end():]


def load_quality_scores():
    if not QUALITY_DETAIL.exists():
        return {}
    with open(QUALITY_DETAIL, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Handle both list format and dict format (with all_scores key)
    if isinstance(data, list):
        return {d["file"]: d for d in data}
    elif isinstance(data, dict) and "all_scores" in data:
        return {d["file"]: d for d in data["all_scores"]}
    else:
        return {}


def load_progress():
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"completed": [], "errors": [], "total_upgraded": 0, "started_at": datetime.now().isoformat()}


def save_progress(progress):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Batch Tier-B Upgrade")
    parser.add_argument("--domain", type=str, help="Filter by domain")
    parser.add_argument("--max", type=int, default=200, help="Max concepts to rewrite")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--resume", action="store_true", help="Skip already completed concepts")
    parser.add_argument("--min-score", type=float, default=0, help="Min score to include")
    parser.add_argument("--max-score", type=float, default=60, help="Max score to include")
    args = parser.parse_args()

    print("=" * 70)
    print(f"Tier-B Batch Upgrade — {MODEL}")
    print(f"Target: domain={args.domain or 'all'}, max={args.max}, score=[{args.min_score},{args.max_score})")
    print("=" * 70)

    concept_map = load_seed_data(domain_filter=args.domain)
    quality_map = load_quality_scores()
    progress = load_progress() if args.resume else {"completed": [], "errors": [], "total_upgraded": 0, "started_at": datetime.now().isoformat()}
    completed_set = set(progress.get("completed", []))

    print(f"Loaded {len(concept_map)} concepts, {len(quality_map)} quality scores")
    if args.resume:
        print(f"Resuming: {len(completed_set)} already completed")

    # Find Tier-B candidates sorted by score (worst first)
    scored = []
    for cid, info in concept_map.items():
        if cid in completed_set:
            continue
        rag_path = find_rag_file(cid, info["domain"])
        if not rag_path:
            continue
        rel = str(rag_path.relative_to(RAG_ROOT))
        q = quality_map.get(rel, {})
        score = q.get("quality_score", 999)
        tier = q.get("quality_tier", "?")
        if tier != "B":
            continue
        if not (args.min_score <= score < args.max_score):
            continue
        # Skip already upgraded by intranet or research methods
        gen = str(q.get("generation_method", ""))
        if any(k in gen for k in ["intranet-llm-rewrite-v2", "research-rewrite"]):
            continue
        scored.append((score, info))
    scored.sort(key=lambda x: x[0])
    candidates = [s[1] for s in scored[:args.max]]
    print(f"Selected {len(candidates)} candidates (worst-scoring Tier-B)")

    if not candidates:
        print("No candidates found!")
        return

    # Process
    ok_count, err_count = 0, 0
    start_time = time.time()

    for i, concept in enumerate(candidates):
        cid, domain = concept["id"], concept["domain"]
        rag_path = find_rag_file(cid, domain)
        if not rag_path:
            continue

        elapsed = time.time() - start_time
        rate = (ok_count + err_count) / elapsed * 3600 if elapsed > 0 else 0
        eta = (len(candidates) - i) / (rate / 3600) if rate > 0 else 0

        print(f"  [{i+1}/{len(candidates)}] {domain}/{cid} ({concept['name']}) "
              f"[{ok_count} ok, {err_count} err, {rate:.0f}/hr, ETA {eta/60:.0f}m]...", end="", flush=True)

        if args.dry_run:
            print(" DRY RUN")
            continue

        try:
            new_body = call_llm(SYSTEM_PROMPT, build_user_prompt(concept))
            time.sleep(RATE_LIMIT_DELAY)
        except Exception as e:
            print(f" ERROR: {e}")
            err_count += 1
            progress["errors"].append({"concept": cid, "error": str(e), "time": datetime.now().isoformat()})
            save_progress(progress)
            time.sleep(RETRY_DELAY)
            continue

        content = rag_path.read_text(encoding="utf-8", errors="replace")
        updated = update_frontmatter(content)
        fm_match = re.match(r"^(---\s*\n.*?\n---)\s*\n?", updated, re.DOTALL)
        new_content = (fm_match.group(1) + "\n" + new_body.strip() + "\n") if fm_match else (new_body.strip() + "\n")
        rag_path.write_text(new_content, encoding="utf-8")
        print(f" OK ({len(new_body)}ch)")
        ok_count += 1
        progress["completed"].append(cid)
        progress["total_upgraded"] = len(progress["completed"])
        progress["last_updated"] = datetime.now().isoformat()

        # Save progress every 10 docs
        if ok_count % 10 == 0:
            save_progress(progress)
            print(f"    --- Progress saved: {ok_count} upgraded ---")

    # Final save
    save_progress(progress)

    elapsed = time.time() - start_time
    print(f"\n{'='*70}")
    print(f"DONE: {ok_count} upgraded, {err_count} errors in {elapsed/60:.1f} minutes")
    print(f"Total upgraded (all runs): {len(progress['completed'])}")
    print(f"Progress saved: {PROGRESS_FILE}")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
