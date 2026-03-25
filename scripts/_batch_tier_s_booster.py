#!/usr/bin/env python3
"""
Tier-S Booster — Second-pass rewrite for stubborn Tier-B docs (score < 50).
Targets: Specificity, Density, Teaching dimensions.

Usage:
    python scripts/_batch_tier_s_booster.py --max 200 --threshold 50
"""

import argparse, json, os, re, sys, time, traceback
from datetime import datetime
from pathlib import Path
import httpx

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
RAG_ROOT = PROJECT_ROOT / "data" / "rag"
SEED_ROOT = PROJECT_ROOT / "data" / "seed"
DETAIL_FILE = PROJECT_ROOT / "data" / "quality_report_detail.json"
PROGRESS_FILE = PROJECT_ROOT / "data" / "tier_s_booster_progress.json"

API_BASE = "https://llm-open-ai.mihoyo.com/v1"
API_KEY = "a12488be-58bb-4f52-93d0-26fee71d5507"
MODEL = "mihoyo.claude-4-6-sonnet"
MAX_TOKENS = 4000
RATE_LIMIT_DELAY = 1.5
RETRY_DELAY = 10
MAX_RETRIES = 3
SAVE_EVERY = 20

SYSTEM_PROMPT = """You are an expert educational content writer. Write in Chinese (Simplified).

Your task: REWRITE a teaching document to dramatically improve its quality score.

SCORING DIMENSIONS (you MUST optimize ALL):

1. SPECIFICITY (30% weight): Every sentence must contain information UNIQUE to this concept.
   - Include specific numbers, dates, inventor/discoverer names, formula variable values
   - ZERO generic sentences. If you can swap the concept name and the sentence still works, DELETE IT.
   - BANNED phrases (instant score = 0):
     "是X的核心组成部分之一", "在X的实践中", "当参数或条件发生变化时",
     "深入理解X需要结合Y", "承上启下的作用", "提供了必要的概念基础",
     "初学者容易忽视", "需要从全局视角理解", "需要根据项目需求灵活调整"

2. DENSITY (25% weight): Must have 2000+ Chinese characters of substantive content.
   - Current doc is ~1300 chars (score=40). Target: 2500+ chars (score=100).
   - Add depth to EVERY section. No thin sections.

3. SOURCES (20% weight): Include at least ONE real citation.
   - Format: (Author, Year) or [Author, Year] or mention a real textbook 《书名》出版社
   - Example: "(Shannon, 1948)" or "《信号与系统》(Oppenheim, 2015)"

4. STRUCTURE (15% weight): Must have 6+ substantive sections (## or ###).
   - Required: ## 概述, ## 核心原理 (with 2-3 ### subsections), ## 关键公式/算法,
     ## 实际应用, ## 常见误区, ## 知识关联
   - Each section must have 100+ chars of non-generic content.

5. TEACHING (10% weight): Must include ALL of these:
   - A formula (use $...$ or \\frac etc.) OR a code snippet (use ``` blocks)
   - A concrete example (use 例如/案例)
   - A thought question (use ？)

OUTPUT FORMAT:
- Output ONLY the document body. NO YAML frontmatter.
- Start with: # [Concept Name in Chinese]
- Minimum 2000 Chinese characters of substantive content.
- Include at least one $formula$ or ```code``` block."""
def build_user_prompt(concept, current_content):
    prereqs = ", ".join(concept.get("prerequisites", [])) or "none"
    nexts = ", ".join(concept.get("next_concepts", [])) or "none"
    # Truncate current content to 1500 chars as context
    truncated = current_content[:1500] if len(current_content) > 1500 else current_content
    return (
        f"REWRITE this teaching document to score 80+/100:\n\n"
        f"Concept: {concept['name']}\n"
        f"Domain: {concept['domain_name']} > {concept['subdomain_name']}\n"
        f"Description: {concept['description']}\n"
        f"Difficulty: {concept['difficulty']}/9\n"
        f"Prerequisites: {prereqs}\n"
        f"Next concepts: {nexts}\n\n"
        f"CURRENT CONTENT (score ~44, too generic and short):\n"
        f"---\n{truncated}\n---\n\n"
        f"REQUIREMENTS:\n"
        f"1. 2500+ Chinese characters (current is ~1300, DOUBLE it)\n"
        f"2. Add specific numbers/dates/names/formulas unique to this concept\n"
        f"3. Add a real citation: (Author, Year) or a textbook reference\n"
        f"4. Add a formula or code block\n"
        f"5. 6+ substantive sections with ### subsections\n"
        f"6. ZERO generic filler sentences"
    )


def call_llm(system, user, retries=MAX_RETRIES):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": MODEL, "max_tokens": MAX_TOKENS,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
    }
    for attempt in range(retries):
        try:
            with httpx.Client(timeout=180.0) as client:
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


def update_frontmatter(content, method="tier-s-booster-v1"):
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
    return {"completed": [], "errors": []}


def save_progress(progress):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max", type=int, default=200)
    parser.add_argument("--threshold", type=float, default=50.0,
                        help="Rewrite docs below this score")
    args = parser.parse_args()

    # Load quality report to find targets
    with open(DETAIL_FILE, "r", encoding="utf-8") as f:
        report = json.load(f)

    targets = [(r["quality_score"], r["file"], r["domain"], r["concept"])
               for r in report if r["quality_score"] < args.threshold]
    targets.sort(key=lambda x: x[0])  # lowest first
    print(f"Tier-S Booster: {len(targets)} docs below {args.threshold}")

    progress = load_progress()
    completed = set(progress.get("completed", []))
    errors = progress.get("errors", [])

    # Filter already done
    targets = [(s, f, d, c) for s, f, d, c in targets if c not in completed]
    print(f"After filtering completed: {len(targets)} remaining")

    if not targets:
        print("Nothing to do!")
        return

    print("Loading seed data...")
    concept_map = load_seed_data()

    ok_count = len(completed)
    err_count = len(errors)
    start_time = time.time()
    total = min(len(targets), args.max)

    for i, (score, filepath, domain, concept_name) in enumerate(targets[:args.max], 1):
        # Find concept in seed data by name
        concept = None
        for cid, cdata in concept_map.items():
            if cdata["name"] == concept_name:
                concept = cdata
                break
        if not concept:
            print(f"  [{i}/{total}] {concept_name}: NOT in seed, skip")
            continue

        rag_file = Path(PROJECT_ROOT) / filepath if filepath else find_rag_file(concept["id"], domain)
        if not rag_file or not Path(rag_file).exists():
            rag_file = find_rag_file(concept["id"], domain)
        if not rag_file:
            print(f"  [{i}/{total}] {concept_name}: RAG file not found, skip")
            continue

        elapsed = time.time() - start_time
        rate = (ok_count - len(progress.get("completed", []))) / (elapsed / 3600) if elapsed > 60 else 0

        print(f"  [{i}/{total}] {domain}/{concept_name} (was {score:.1f}) "
              f"[{ok_count} ok, {err_count} err, {rate:.0f}/hr]...", end="", flush=True)

        try:
            current = open(rag_file, "r", encoding="utf-8").read()
            # Strip frontmatter for context
            body = re.sub(r"^---\s*\n.*?\n---\s*\n", "", current, count=1, flags=re.DOTALL)

            user_prompt = build_user_prompt(concept, body)
            new_body = call_llm(SYSTEM_PROMPT, user_prompt)

            # Preserve frontmatter
            fm_match = re.match(r"^(---\s*\n.*?\n---\s*\n)", current, re.DOTALL)
            if fm_match:
                combined = fm_match.group(1) + "\n" + new_body
                combined = update_frontmatter(combined)
            else:
                combined = new_body

            with open(rag_file, "w", encoding="utf-8") as f:
                f.write(combined)

            ok_count += 1
            completed.add(concept_name)
            print(f" OK ({len(new_body)}ch)")

        except Exception as e:
            err_count += 1
            errors.append({"concept": concept_name, "error": str(e),
                          "time": datetime.now().isoformat()})
            print(f" ERR: {e}")

        if (ok_count + err_count) % SAVE_EVERY == 0:
            progress["completed"] = list(completed)
            progress["errors"] = errors
            save_progress(progress)
            print(f"    --- Booster progress saved: {ok_count} upgraded ---")

        time.sleep(RATE_LIMIT_DELAY)

    # Final save
    progress["completed"] = list(completed)
    progress["errors"] = errors
    save_progress(progress)

    elapsed = time.time() - start_time
    print(f"\n{'='*70}")
    print(f"DONE (Booster): {ok_count} upgraded, {err_count} errors in {elapsed/60:.1f}m")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
