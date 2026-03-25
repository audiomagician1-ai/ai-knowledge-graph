#!/usr/bin/env python3
"""
Sprint 6 Tier-B Upgrade — Process all remaining 3360 Tier-B docs.
Uses progress file: data/tier_b_upgrade_progress_s6.json

Usage:
    python scripts/_batch_sprint6.py --max 3400
"""

import argparse, json, os, re, sys, time, traceback
from datetime import datetime
from pathlib import Path
import httpx

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
RAG_ROOT = PROJECT_ROOT / "data" / "rag"
SEED_ROOT = PROJECT_ROOT / "data" / "seed"
PROGRESS_FILE = PROJECT_ROOT / "data" / "tier_b_upgrade_progress_s6.json"

API_BASE = "https://llm-open-ai.mihoyo.com/v1"
API_KEY = "a12488be-58bb-4f52-93d0-26fee71d5507"
MODEL = "mihoyo.claude-4-6-sonnet"
MAX_TOKENS = 3000
RATE_LIMIT_DELAY = 1.0
RETRY_DELAY = 10
MAX_RETRIES = 3
SAVE_EVERY = 40

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


def load_seed_data():
    concept_map, subdomain_names, domain_names, edges_map = {}, {}, {}, {}
    for domain_dir in sorted(SEED_ROOT.iterdir()):
        if not domain_dir.is_dir():
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
        pattern = re.compile(rf"^{key}:.*$", re.MULTILINE)
        if pattern.search(fm):
            return pattern.sub(f"{key}: {value}", fm)
        return fm + f"\n{key}: {value}"

    fm_body = set_field(fm_body, "quality_method", method)
    fm_body = set_field(fm_body, "updated_at", today)
    return fm_match.group(1) + fm_body + fm_match.group(3) + content[fm_match.end():]


def load_progress():
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"total": 0, "done": 0, "errors": [], "error_slugs": [], "completed": [], "queue": []}


def save_progress(progress):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max", type=int, default=3400)
    args = parser.parse_args()

    progress = load_progress()
    queue = progress.get("queue", [])
    completed = set(progress.get("completed", []))
    errors = progress.get("error_slugs", [])

    # Filter queue: skip already completed
    queue = [s for s in queue if s not in completed]
    if not queue:
        print("No items in queue!")
        return

    print(f"Sprint 6: {len(queue)} remaining, {len(completed)} done, {len(errors)} errors")
    print(f"Loading seed data...")
    concept_map = load_seed_data()

    total_in_queue = len(queue)
    start_time = time.time()
    ok_count = len(completed)
    err_count = len(errors)

    for i, slug in enumerate(queue[:args.max], 1):
        if slug in completed:
            continue
        concept = concept_map.get(slug)
        if not concept:
            print(f"  [{i}/{total_in_queue}] {slug}: NOT in concept_map, skip")
            continue

        rag_file = find_rag_file(slug, concept["domain"])
        if not rag_file:
            print(f"  [{i}/{total_in_queue}] {slug}: RAG file not found, skip")
            continue

        elapsed = time.time() - start_time
        rate = ok_count / (elapsed / 3600) if elapsed > 60 else 0
        eta = int((total_in_queue - i) / max(rate, 1) * 60) if rate > 0 else 999

        print(f"  [{ok_count+err_count+1}/{total_in_queue}] {concept['domain']}/{slug} ({concept['name']}) "
              f"[{ok_count} ok, {err_count} err, {rate:.0f}/hr, ETA {eta}m]...", end="", flush=True)

        try:
            user_prompt = build_user_prompt(concept)
            new_body = call_llm(SYSTEM_PROMPT, user_prompt)

            old = open(rag_file, "r", encoding="utf-8").read()
            fm_match = re.match(r"^(---\s*\n.*?\n---\s*\n)", old, re.DOTALL)
            if fm_match:
                combined = fm_match.group(1) + "\n" + new_body
                combined = update_frontmatter(combined)
            else:
                combined = new_body

            with open(rag_file, "w", encoding="utf-8") as f:
                f.write(combined)

            ok_count += 1
            completed.add(slug)
            print(f" OK ({len(new_body)}ch)")

        except Exception as e:
            err_count += 1
            errors.append({"concept": slug, "error": str(e), "time": datetime.now().isoformat()})
            print(f" ERR: {e}")

        # Save progress periodically
        if (ok_count + err_count) % SAVE_EVERY == 0:
            progress["done"] = ok_count
            progress["completed"] = list(completed)
            progress["error_slugs"] = errors
            progress["queue"] = [s for s in queue if s not in completed]
            save_progress(progress)
            print(f"    --- S6 Progress saved: {ok_count} upgraded ---")

        time.sleep(RATE_LIMIT_DELAY)

    # Final save
    progress["done"] = ok_count
    progress["completed"] = list(completed)
    progress["error_slugs"] = errors
    progress["queue"] = [s for s in queue if s not in completed]
    save_progress(progress)

    elapsed = time.time() - start_time
    print(f"\n{'='*70}")
    print(f"DONE (S6): {ok_count} upgraded, {err_count} errors in {elapsed/60:.1f} minutes")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
