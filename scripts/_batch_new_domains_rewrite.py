#!/usr/bin/env python3
"""
New Domains RAG Rewrite — Upgrade 144 stub documents across 6 systems-theory family domains.

Targets: systems-theory, cybernetics, information-theory, dissipative-structures, synergetics, catastrophe-theory

Usage:
    python scripts/_batch_new_domains_rewrite.py --max 200
    python scripts/_batch_new_domains_rewrite.py --domain systems-theory --max 30
"""

import argparse, json, os, re, sys, time, traceback
from datetime import datetime
from pathlib import Path
import httpx

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
RAG_ROOT = PROJECT_ROOT / "data" / "rag"
SEED_ROOT = PROJECT_ROOT / "data" / "seed"
PROGRESS_FILE = PROJECT_ROOT / "data" / "new_domains_rewrite_progress.json"

API_BASE = "https://llm-open-ai.mihoyo.com/v1"
API_KEY = "a12488be-58bb-4f52-93d0-26fee71d5507"
MODEL = "mihoyo.claude-4-6-sonnet"
MAX_TOKENS = 4000
RATE_LIMIT_DELAY = 1.5
RETRY_DELAY = 10
MAX_RETRIES = 3
SAVE_EVERY = 5

TARGET_DOMAINS = [
    "systems-theory", "cybernetics", "information-theory",
    "dissipative-structures", "synergetics", "catastrophe-theory"
]

SYSTEM_PROMPT = """You are an expert educational content writer specializing in systems science, cybernetics, and complexity theory. Write in Chinese (Simplified).

Your task: Write a HIGH-QUALITY teaching document for a knowledge graph RAG system. The current document is a placeholder stub — you are writing from scratch.

SCORING DIMENSIONS (you MUST optimize ALL):

1. SPECIFICITY (30% weight): Every sentence must contain information UNIQUE to this concept.
   - Include specific numbers, dates, inventor/discoverer names, formula variable definitions
   - ZERO generic sentences. If you can swap the concept name and the sentence still works, DELETE IT.
   - BANNED phrases (instant score = 0):
     "是X领域的重要概念", "涉及该领域的基础理论和实践应用",
     "的核心原理和机制", "在实际问题中的应用",
     "与相关概念的联系", "掌握其在实际场景中的应用方法",
     "了解与其他知识点的关联关系", "理解X的定义和核心思想",
     Any sentence that works for ANY concept by swapping the name

2. DENSITY (25% weight): Must have 2000+ Chinese characters of substantive content.
   - Current stubs are ~300 chars (score≈0). Target: 2500+ chars (score=100).
   - Add depth to EVERY section. No thin sections.

3. SOURCES (20% weight): Include at least TWO real citations.
   - Use real authors and years: (von Bertalanffy, 1968), (Wiener, 1948), (Shannon, 1948), (Prigogine, 1977), (Haken, 1977), (Thom, 1972), etc.
   - Reference real books: 《一般系统论》, 《控制论》, 《信息论》, 《从存在到演化》, 《协同学》, etc.
   - Cite specific theorems, equations, or experimental results with proper attribution.

4. STRUCTURE (15% weight): Must have 6+ substantive sections (## or ###).
   - Required: ## 概述, ## 核心原理 (with 2-3 ### subsections), ## 关键公式/模型,
     ## 实际应用, ## 常见误区, ## 知识关联
   - Each section must have 100+ chars of non-generic content.

5. TEACHING (10% weight): Must include ALL of these:
   - A formula (use LaTeX: $...$ or $$...$$) — these domains are rich in math!
   - A concrete example (use 例如/案例/实例)
   - A thought-provoking question (use ？) to stimulate deeper thinking

OUTPUT FORMAT:
- Output ONLY the document body. NO YAML frontmatter. NO ```markdown``` fences.
- Start with: # [Concept Name in Chinese]
- Minimum 2000 Chinese characters of substantive content.
- Include at least one $formula$ block.
- For systems-theory family concepts, leverage the rich mathematical and historical foundations."""


def build_user_prompt(concept, domain_info, edges):
    prereqs = []
    nexts = []
    for e in edges:
        if e.get("target_id") == concept["id"]:
            prereqs.append(e["source_id"])
        if e.get("source_id") == concept["id"]:
            nexts.append(e["target_id"])
    prereqs_str = ", ".join(prereqs) or "none (entry point)"
    nexts_str = ", ".join(nexts) or "none (terminal)"
    
    return (
        f"Write a comprehensive teaching document for this concept:\n\n"
        f"Concept ID: {concept['id']}\n"
        f"Concept Name: {concept['name']}\n"
        f"Domain: {domain_info['name']} ({domain_info['id']})\n"
        f"Subdomain: {concept['subdomain_id']}\n"
        f"Description: {concept['description']}\n"
        f"Difficulty: {concept['difficulty']}/9\n"
        f"Prerequisites: {prereqs_str}\n"
        f"Leads to: {nexts_str}\n"
        f"Content type: {concept.get('content_type', 'theory')}\n"
        f"Tags: {', '.join(concept.get('tags', []))}\n\n"
        f"IMPORTANT:\n"
        f"- This is a {domain_info['name']} concept. Use domain-specific terminology.\n"
        f"- Include real historical context (founders, key papers, dates).\n"
        f"- Include at least one mathematical formula relevant to this specific concept.\n"
        f"- Every paragraph must teach something UNIQUE to '{concept['name']}'.\n"
        f"- Target: 2500+ Chinese characters of substantive, concept-specific content."
    )


def call_llm(system, user, retries=MAX_RETRIES):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
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


def load_progress():
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
    return {"completed": [], "errors": [], "stats": {"total": 0, "success": 0, "error": 0}}


def save_progress(progress):
    PROGRESS_FILE.write_text(json.dumps(progress, ensure_ascii=False, indent=2), encoding="utf-8")


def find_rag_file(domain_id, subdomain_id, concept_id):
    """Find the RAG markdown file for a concept."""
    domain_dir = RAG_ROOT / domain_id
    if not domain_dir.exists():
        return None
    # Search recursively for the concept file
    for md_file in domain_dir.rglob(f"{concept_id}.md"):
        return md_file
    # Try subdomain path
    sub_dir = domain_dir / subdomain_id
    if sub_dir.exists():
        target = sub_dir / f"{concept_id}.md"
        if target.exists():
            return target
    return None


def validate_output(content, concept_name):
    """Basic validation of LLM output."""
    if not content or len(content) < 500:
        return False, "Too short"
    if "```markdown" in content:
        # Strip markdown fences
        content = re.sub(r"```markdown\s*\n?", "", content)
        content = re.sub(r"\n?```\s*$", "", content)
    # Check for banned stub phrases
    banned = ["涉及该领域的基础理论和实践应用", "的核心原理和机制", "在实际问题中的应用"]
    for phrase in banned:
        if phrase in content:
            return False, f"Contains banned phrase: {phrase}"
    return True, content


def main():
    parser = argparse.ArgumentParser(description="Rewrite RAG stubs for 6 new domains")
    parser.add_argument("--max", type=int, default=200, help="Max concepts to process")
    parser.add_argument("--domain", type=str, default=None, help="Process single domain only")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without calling LLM")
    args = parser.parse_args()

    domains_to_process = [args.domain] if args.domain else TARGET_DOMAINS
    progress = load_progress()
    completed_set = set(progress["completed"])

    # Collect all concepts
    all_tasks = []
    for domain_id in domains_to_process:
        seed_file = SEED_ROOT / domain_id / "seed_graph.json"
        if not seed_file.exists():
            print(f"⚠️  No seed file for {domain_id}, skipping")
            continue
        seed = json.loads(seed_file.read_text(encoding="utf-8"))
        domain_info = seed["domain"]
        edges = seed.get("edges", [])
        
        for concept in seed["concepts"]:
            key = f"{domain_id}/{concept['id']}"
            if key in completed_set:
                continue
            rag_file = find_rag_file(domain_id, concept["subdomain_id"], concept["id"])
            if rag_file is None:
                print(f"⚠️  No RAG file for {key}, skipping")
                continue
            all_tasks.append({
                "key": key,
                "concept": concept,
                "domain_info": domain_info,
                "edges": edges,
                "rag_file": rag_file,
            })

    total = len(all_tasks)
    limit = min(args.max, total)
    print(f"\n{'='*60}")
    print(f"  New Domains RAG Rewrite")
    print(f"  Domains: {', '.join(domains_to_process)}")
    print(f"  Total stubs: {total} | Already done: {len(completed_set)} | This run: {limit}")
    print(f"  Model: {MODEL}")
    print(f"{'='*60}\n")

    if args.dry_run:
        for t in all_tasks[:limit]:
            print(f"  Would rewrite: {t['key']} → {t['rag_file']}")
        return

    success = 0
    errors = 0
    start_time = time.time()

    for i, task in enumerate(all_tasks[:limit]):
        key = task["key"]
        concept = task["concept"]
        rag_file = task["rag_file"]
        
        print(f"[{i+1}/{limit}] {key} ({concept['name']})...", end="", flush=True)
        
        try:
            user_prompt = build_user_prompt(concept, task["domain_info"], task["edges"])
            raw = call_llm(SYSTEM_PROMPT, user_prompt)
            
            # Validate
            ok, result = validate_output(raw, concept["name"])
            if not ok:
                print(f" ❌ {result}")
                progress["errors"].append({"key": key, "error": result, "time": datetime.now().isoformat()})
                errors += 1
                time.sleep(RATE_LIMIT_DELAY)
                continue
            
            # Clean output
            content = result.strip()
            if content.startswith("```"):
                content = re.sub(r"^```\w*\n?", "", content)
                content = re.sub(r"\n?```\s*$", "", content)
            
            # Write to file
            rag_file.write_text(content, encoding="utf-8")
            
            progress["completed"].append(key)
            completed_set.add(key)
            success += 1
            
            char_count = len(content)
            print(f" ✅ {char_count} chars")
            
        except Exception as e:
            print(f" ❌ {e}")
            progress["errors"].append({"key": key, "error": str(e), "time": datetime.now().isoformat()})
            errors += 1
        
        # Save progress periodically
        if (i + 1) % SAVE_EVERY == 0:
            progress["stats"] = {"total": total, "success": success, "error": errors}
            save_progress(progress)
        
        time.sleep(RATE_LIMIT_DELAY)

    # Final save
    elapsed = time.time() - start_time
    progress["stats"] = {
        "total": total,
        "success": success,
        "error": errors,
        "elapsed_seconds": round(elapsed),
        "last_run": datetime.now().isoformat(),
    }
    save_progress(progress)

    print(f"\n{'='*60}")
    print(f"  DONE: {success} success, {errors} errors, {elapsed:.0f}s elapsed")
    print(f"  Remaining: {total - len(completed_set)} stubs")
    print(f"  Progress: {PROGRESS_FILE}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
