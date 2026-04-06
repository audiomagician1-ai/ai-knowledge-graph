#!/usr/bin/env python3
"""Legacy RAG Quality Booster — processes from the TAIL end of the target list (200→101).
Run in parallel with _batch_legacy_boost.py which starts from 1→100."""

import json, os, re, sys, time
from pathlib import Path
import httpx

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
TARGETS_FILE = PROJECT_ROOT / "data" / "legacy_upgrade_targets.json"
PROGRESS_FILE = PROJECT_ROOT / "data" / "legacy_boost_progress_tail.json"

API_BASE = "https://llm-open-ai.mihoyo.com/v1"
API_KEY = "a12488be-58bb-4f52-93d0-26fee71d5507"
MODEL = "mihoyo.claude-4-6-sonnet"
MAX_TOKENS = 4000
RATE_LIMIT_DELAY = 1.5
RETRY_DELAY = 10
MAX_RETRIES = 3
SAVE_EVERY = 5

SYSTEM_PROMPT = """You are an expert educational content writer. Your task is to ENHANCE an existing teaching document to score higher on quality metrics.

The document already has decent content but needs improvement in these dimensions:

1. SPECIFICITY (30%): Replace generic sentences with concept-specific info. Add dates, names, numbers.
2. DENSITY (25%): Expand to 2500+ Chinese characters of substantive content.
3. SOURCES (20%): Add at least 2 real citations (Author, Year).
4. STRUCTURE (15%): Ensure 6+ substantive sections (##/###).
5. TEACHING (10%): Must include formula ($...$), example (例如), question (？).

OUTPUT: The complete improved document. Start with the existing # title. NO markdown fences."""


def call_llm(system, user, retries=MAX_RETRIES):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {"model": MODEL, "max_tokens": MAX_TOKENS, "messages": [
        {"role": "system", "content": system}, {"role": "user", "content": user}]}
    for attempt in range(retries):
        try:
            with httpx.Client(timeout=120.0) as client:
                resp = client.post(f"{API_BASE}/chat/completions", json=payload, headers=headers)
                resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
            else:
                raise


def load_progress():
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
    return {"completed": [], "errors": []}


def save_progress(progress):
    PROGRESS_FILE.write_text(json.dumps(progress, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    targets = json.loads(TARGETS_FILE.read_text(encoding="utf-8"))
    # Also check the head-end progress to avoid duplicates
    head_progress_file = PROJECT_ROOT / "data" / "legacy_boost_progress.json"
    head_done = set()
    if head_progress_file.exists():
        head_done = set(json.loads(head_progress_file.read_text(encoding="utf-8")).get("completed", []))

    progress = load_progress()
    completed = set(progress["completed"]) | head_done

    # Process from index 100→199 (tail half)
    todo = [t for t in targets[100:] if t not in completed]
    total = len(todo)

    print("=" * 60)
    print(f"  Legacy RAG Booster (TAIL: 101-200)")
    print(f"  Targets: {len(targets[100:])} | Already done: {len(completed)} | This run: {total}")
    print("=" * 60)

    success = errors = 0
    start = time.time()

    for i, filepath in enumerate(todo):
        fp = Path(filepath)
        if not fp.exists():
            continue
        content = fp.read_text(encoding="utf-8")
        title_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
        concept_name = title_match.group(1) if title_match else fp.stem
        parts = filepath.replace("\\", "/").split("/")
        domain_idx = parts.index("rag") + 1 if "rag" in parts else -1
        domain = parts[domain_idx] if domain_idx > 0 else "unknown"

        user_prompt = (
            f"Enhance this teaching document. Keep and improve ALL existing content.\n\n"
            f"Domain: {domain}\nConcept: {concept_name}\nCurrent: {len(content)} chars\n"
            f"Target: 3500+ chars, 6+ sections, citations, formula, example, question\n\n"
            f"---CURRENT---\n{content}\n---END---\n\nOutput improved version in Chinese."
        )

        print(f"\n[{i+1}/{total}] {domain}/{concept_name}...", end=" ", flush=True)
        try:
            result = call_llm(SYSTEM_PROMPT, user_prompt).strip()
            if result.startswith("```"):
                result = re.sub(r'^```\w*\n?', '', result)
                result = re.sub(r'\n?```$', '', result)
            fp.write_text(result, encoding="utf-8")
            progress["completed"].append(filepath)
            success += 1
            print(f"✅ {len(result)} chars", flush=True)
        except Exception as e:
            progress["errors"].append({"path": filepath, "error": str(e)})
            errors += 1
            print(f"❌ {e}", flush=True)

        if (i + 1) % SAVE_EVERY == 0:
            save_progress(progress)
        time.sleep(RATE_LIMIT_DELAY)

    save_progress(progress)
    print(f"\n{'='*60}")
    print(f"  DONE: {success} success, {errors} errors, {time.time()-start:.0f}s")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
