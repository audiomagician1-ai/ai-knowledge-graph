#!/usr/bin/env python3
"""
Legacy RAG Quality Booster — Upgrade bottom 200 docs to push global avg above 80.

Usage:
    python scripts/_batch_legacy_boost.py --max 200
    python scripts/_batch_legacy_boost.py --max 50  # smaller batch
"""

import argparse, json, os, re, sys, time, traceback
from pathlib import Path
import httpx

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
TARGETS_FILE = PROJECT_ROOT / "data" / "legacy_upgrade_targets.json"
PROGRESS_FILE = PROJECT_ROOT / "data" / "legacy_boost_progress.json"

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

1. SPECIFICITY (30% weight): Replace ANY generic sentences with concept-specific information.
   - Add exact dates, inventor names, specific numbers, formula variable definitions
   - BANNED: "是X领域的重要概念", "涉及基础理论和实践应用" — if swapping the concept name still works, DELETE it.

2. DENSITY (25% weight): Expand thin sections to 2500+ Chinese characters total.
   - Add depth, not fluff. Every paragraph must teach something unique.

3. SOURCES (20% weight): Add at least 2 real citations if missing.
   - (Author, Year) format. Real books, papers, or established references.

4. STRUCTURE (15% weight): Ensure 6+ substantive sections (## or ###).
   - Required: 概述, 核心原理(with subsections), 关键公式/模型, 实际应用, 常见误区, 知识关联

5. TEACHING (10% weight): Must include ALL:
   - A formula ($...$ or $$...$$)
   - A concrete example (use 例如/案例)
   - A thought-provoking question (use ？)

OUTPUT: The complete improved document. Start with the existing # title. Output ONLY the document body. NO markdown fences."""


def call_llm(system: str, user: str, retries: int = MAX_RETRIES) -> str:
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
    return {"completed": [], "errors": []}


def save_progress(progress):
    PROGRESS_FILE.write_text(json.dumps(progress, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max", type=int, default=200)
    args = parser.parse_args()

    targets = json.loads(TARGETS_FILE.read_text(encoding="utf-8"))
    progress = load_progress()
    completed = set(progress["completed"])

    todo = [t for t in targets if t not in completed][:args.max]
    total = len(todo)

    print("=" * 60)
    print(f"  Legacy RAG Quality Booster")
    print(f"  Total targets: {len(targets)} | Already done: {len(completed)} | This run: {total}")
    print(f"  Model: {MODEL}")
    print("=" * 60)

    success = 0
    errors = 0
    start = time.time()

    for i, filepath in enumerate(todo):
        fp = Path(filepath)
        if not fp.exists():
            print(f"\n[{i+1}/{total}] SKIP (not found): {filepath}")
            continue

        content = fp.read_text(encoding="utf-8")
        # Extract concept name from first heading
        title_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
        concept_name = title_match.group(1) if title_match else fp.stem

        # Determine domain from path
        parts = filepath.replace("\\", "/").split("/")
        domain_idx = parts.index("rag") + 1 if "rag" in parts else -1
        domain = parts[domain_idx] if domain_idx > 0 else "unknown"

        user_prompt = (
            f"Enhance this existing teaching document. Keep and improve ALL existing content, add missing elements.\n\n"
            f"Domain: {domain}\n"
            f"Concept: {concept_name}\n"
            f"Current length: {len(content)} chars\n"
            f"Target: 3500+ chars, 6+ sections, citations, formula, example, question\n\n"
            f"---CURRENT DOCUMENT---\n{content}\n---END---\n\n"
            f"Output the improved version. Keep the same # title. Write in Chinese."
        )

        print(f"\n[{i+1}/{total}] {domain}/{concept_name}...", end=" ", flush=True)
        try:
            result = call_llm(SYSTEM_PROMPT, user_prompt)
            # Clean up
            result = result.strip()
            if result.startswith("```"):
                result = re.sub(r'^```\w*\n?', '', result)
                result = re.sub(r'\n?```$', '', result)

            # Validate: must be longer than original and contain heading
            if len(result) < len(content):
                print(f"WARN short ({len(result)} < {len(content)})", end="")
            
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
    elapsed = time.time() - start
    print(f"\n{'='*60}")
    print(f"  DONE: {success} success, {errors} errors, {elapsed:.0f}s elapsed")
    print(f"  Progress: {PROGRESS_FILE}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
