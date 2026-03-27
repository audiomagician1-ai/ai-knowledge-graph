#!/usr/bin/env python3
"""Retry the 3 Sprint 6 timeout errors."""
import json, re, time, sys
from pathlib import Path
from datetime import datetime
import httpx

PROJECT_ROOT = Path(r"D:\EchoAgent\projects\AI-Knowledge-Graph")
RAG_ROOT = PROJECT_ROOT / "data" / "rag"
SEED_ROOT = PROJECT_ROOT / "data" / "seed"

API_BASE = "https://llm-open-ai.mihoyo.com/v1"
API_KEY = "a12488be-58bb-4f52-93d0-26fee71d5507"
MODEL = "mihoyo.claude-4-6-sonnet"

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
    '   - Any sentence that could apply to ANY concept by swapping the name\n\n'
    "3. REQUIRED content quality:\n"
    "   - Include at least ONE specific number, date, name, or formula unique to this concept\n"
    "   - Each section must teach something a student couldn't learn from any other concept's page\n"
    "   - If a formula exists, include it with variable definitions\n\n"
    "4. Structure (output ONLY the body, NO YAML frontmatter):\n"
    "   # [Concept Name in Chinese]\n"
    "   ## 概述 (2-3 paragraphs)\n"
    "   ## 核心原理 (3+ subsections)\n"
    "   ## 实际应用 (concrete examples)\n"
    "   ## 常见误区 (2-3 misconceptions)\n"
    "   ## 知识关联 (prerequisites and next topics)\n\n"
    "5. Length: 1200-2000 Chinese characters of substantive content."
)

TARGETS = [
    {
        "slug": "analogical-reasoning",
        "name": "类比推理",
        "domain": "philosophy",
        "subdomain": "逻辑与推理",
        "description": "通过两个领域之间的结构相似性进行推理的方法",
        "difficulty": 5,
        "prereqs": ["归纳推理", "演绎推理"],
        "nexts": ["科学方法论"],
    },
    {
        "slug": "chinese-metaphysics",
        "name": "中国形而上学",
        "domain": "philosophy",
        "subdomain": "形而上学",
        "description": "中国哲学传统中关于存在本质、道、气等形而上学思想",
        "difficulty": 6,
        "prereqs": ["形而上学导论"],
        "nexts": ["比较哲学"],
    },
    {
        "slug": "feminist-philosophy",
        "name": "女性主义哲学",
        "domain": "philosophy",
        "subdomain": "现代哲学",
        "description": "从性别视角审视知识、伦理、政治等哲学问题的思想传统",
        "difficulty": 6,
        "prereqs": ["后现代主义"],
        "nexts": ["当代伦理争议"],
    },
]

FILE_MAP = {
    "analogical-reasoning": RAG_ROOT / "philosophy" / "logic-reasoning" / "analogical-reasoning.md",
    "chinese-metaphysics": RAG_ROOT / "philosophy" / "metaphysics" / "chinese-metaphysics.md",
    "feminist-philosophy": RAG_ROOT / "philosophy" / "modern-philosophy" / "feminist-philosophy.md",
}


def call_llm(system, user):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": MODEL, "max_tokens": 3000,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
    }
    for attempt in range(3):
        try:
            with httpx.Client(timeout=180.0) as client:
                resp = client.post(f"{API_BASE}/chat/completions", json=payload, headers=headers)
                resp.raise_for_status()
                return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            if attempt < 2:
                wait = 15 * (attempt + 1)
                print(f"  RETRY({attempt+1}) in {wait}s: {e}")
                time.sleep(wait)
            else:
                raise


def update_frontmatter(content):
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

    fm_body = set_field(fm_body, "quality_method", "intranet-llm-rewrite-v2")
    fm_body = set_field(fm_body, "updated_at", today)
    return fm_match.group(1) + fm_body + fm_match.group(3) + content[fm_match.end():]


def main():
    for t in TARGETS:
        slug = t["slug"]
        path = FILE_MAP[slug]
        prereqs = ", ".join(t["prereqs"]) or "none"
        nexts = ", ".join(t["nexts"]) or "none"
        user_prompt = (
            f"Write a teaching document for:\n\n"
            f"Concept: {t['name']}\n"
            f"Domain: {t['domain']} > {t['subdomain']}\n"
            f"Description: {t['description']}\n"
            f"Difficulty: {t['difficulty']}/9\n"
            f"Prerequisites: {prereqs}\n"
            f"Next concepts: {nexts}\n\n"
            f'Remember: EVERY sentence must be specific to "{t["name"]}". Generic filler = rejection.'
        )

        print(f"Rewriting {slug} ({t['name']})...", end="", flush=True)
        try:
            new_body = call_llm(SYSTEM_PROMPT, user_prompt)
            old = open(path, "r", encoding="utf-8").read()
            fm_match = re.match(r"^(---\s*\n.*?\n---\s*\n)", old, re.DOTALL)
            if fm_match:
                combined = fm_match.group(1) + "\n" + new_body
                combined = update_frontmatter(combined)
            else:
                combined = new_body
            with open(path, "w", encoding="utf-8") as f:
                f.write(combined)
            print(f" OK ({len(new_body)}ch)")
        except Exception as e:
            print(f" FAILED: {e}")

    # Update progress file to move these from error_slugs to completed
    progress_file = PROJECT_ROOT / "data" / "tier_b_upgrade_progress_s6.json"
    if progress_file.exists():
        progress = json.load(open(progress_file, "r", encoding="utf-8"))
        completed = set(progress.get("completed", []))
        for t in TARGETS:
            completed.add(t["slug"])
        progress["completed"] = list(completed)
        progress["done"] = len(completed)
        # Remove from error_slugs
        progress["error_slugs"] = [
            e for e in progress.get("error_slugs", [])
            if e.get("concept") not in {t["slug"] for t in TARGETS}
        ]
        json.dump(progress, open(progress_file, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"Progress updated: {len(completed)} completed, {len(progress['error_slugs'])} errors")

    print("Done!")


if __name__ == "__main__":
    main()
