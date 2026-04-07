#!/usr/bin/env python3
"""
Sprint 10: Final Push — Rewrite bottom ~80 docs to push global RAG avg from 79.89 to 80.0+

Strategy: Target docs scoring <= 76.3 in the official scorer (bottom tier).
Expected gain: +11 pts/doc average → 80 * 11 = 880 > 717 gap.

Usage:
    python scripts/_batch_sprint10_final.py
    python scripts/_batch_sprint10_final.py --max 40   # limit batch size
    python scripts/_batch_sprint10_final.py --dry-run   # preview only
"""

import argparse, json, os, re, sys, time, traceback
from datetime import datetime
from pathlib import Path
import subprocess
import httpx

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
RAG_ROOT = PROJECT_ROOT / "data" / "rag"
SEED_ROOT = PROJECT_ROOT / "data" / "seed"
PROGRESS_FILE = PROJECT_ROOT / "data" / "sprint10_progress.json"

API_BASE = "https://llm-open-ai.mihoyo.com/v1"
API_KEY = "a12488be-58bb-4f52-93d0-26fee71d5507"
MODEL = "mihoyo.claude-4-6-sonnet"
MAX_TOKENS = 4000
RATE_LIMIT_DELAY = 1.5
RETRY_DELAY = 10
MAX_RETRIES = 3

# ─── Official scorer integration ───
def run_official_scorer():
    """Run quality_scorer.py and parse the quality_report.json output."""
    report_path = PROJECT_ROOT / "data" / "quality_report.json"
    # Run scorer to generate report
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "quality_scorer.py")],
        capture_output=True, text=True, encoding="utf-8",
        cwd=str(PROJECT_ROOT)
    )
    if report_path.exists():
        return json.loads(report_path.read_text(encoding="utf-8"))
    return None

def find_bottom_docs_from_report(report, threshold=76.5, max_docs=80):
    """Extract docs with score <= threshold from quality report."""
    bottom = []
    if not report or "domains" not in report:
        return bottom
    for domain_name, domain_data in report["domains"].items():
        if "files" not in domain_data:
            continue
        for file_info in domain_data["files"]:
            score = file_info.get("score", 100)
            if score <= threshold:
                bottom.append({
                    "score": score,
                    "path": file_info.get("path", ""),
                    "name": file_info.get("name", ""),
                    "domain": domain_name,
                })
    bottom.sort(key=lambda x: x["score"])
    return bottom[:max_docs]

def find_bottom_docs_manual(threshold=76.5, max_docs=80):
    """Scan all RAG docs and find those scoring below threshold using our scorer logic."""
    # Import scorer logic
    sys.path.insert(0, str(SCRIPT_DIR))
    
    bottom = []
    for domain_dir in sorted(RAG_ROOT.iterdir()):
        if not domain_dir.is_dir():
            continue
        domain = domain_dir.name
        for md_file in domain_dir.rglob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
                score = quick_score(content)
                if score <= threshold:
                    rel = str(md_file.relative_to(RAG_ROOT)).replace("\\", "/")
                    name = md_file.stem
                    bottom.append({
                        "score": score,
                        "path": rel,
                        "name": name,
                        "domain": domain,
                        "abs_path": str(md_file),
                    })
            except Exception:
                pass
    
    bottom.sort(key=lambda x: x["score"])
    return bottom[:max_docs]

def quick_score(content):
    """Lightweight scoring matching the official scorer's dimensions."""
    if not content or len(content) < 50:
        return 0
    
    lines = content.split("\n")
    s = 0
    
    # 1. Specificity (30) - check for template/generic content
    from collections import Counter
    TEMPLATE_PHRASES = [
        "服务于核心体验", "玩家可感知", "可迭代", "过度设计",
        "忽视玩家感受", "照搬其他游戏", "明确设计目标和约束条件",
        "参考成功案例建立初始方案", "快速制作原型或纸面模拟",
        "组织测试并收集反馈", "基于数据迭代改进",
        "电子表格(Excel/Google Sheets)用于数值模拟",
        "的核心在于理解其基本定义", "学习者需要具备扎实的基础知识",
        "初学者容易忽视", "在第1天、第3天、第7天分别回顾",
        "学完后不看笔记复述", "将所学应用于实际项目",
    ]
    template_count = sum(1 for p in TEMPLATE_PHRASES if p in content)
    non_template_ratio = max(0, 1 - template_count * 0.15)
    s += 30 * non_template_ratio
    
    # 2. Density (25) - effective character count
    clean = re.sub(r'[#\-*`\s\n]', '', content)
    char_count = len(clean)
    if char_count >= 2500: s += 25
    elif char_count >= 2000: s += 22
    elif char_count >= 1500: s += 18
    elif char_count >= 1000: s += 14
    elif char_count >= 500: s += 8
    else: s += 3
    
    # 3. Sources (20) - citations and references
    citations = re.findall(r'\([\w\s&]+,?\s*\d{4}[a-z]?\)', content)
    book_refs = re.findall(r'《.+?》', content)
    source_score = min(20, len(citations) * 5 + len(book_refs) * 4)
    s += source_score
    
    # 4. Structure (15) - sections
    h2_count = len([l for l in lines if l.startswith("## ")])
    h3_count = len([l for l in lines if l.startswith("### ")])
    struct = min(15, h2_count * 2.5 + h3_count * 1.5)
    s += struct
    
    # 5. Teaching (10) - formulas, examples, questions
    has_math = bool(re.search(r'\$[^$]+\$', content))
    has_example = bool(re.search(r'(例如|案例|实例|比如|e\.g\.)', content))
    has_question = content.count('？') >= 1
    teaching = 0
    if has_math: teaching += 4
    if has_example: teaching += 3
    if has_question: teaching += 3
    s += teaching
    
    return min(100, round(s, 1))

# ─── LLM Rewrite ───
SYSTEM_PROMPT = """You are an expert educational content writer. Write in Chinese (Simplified).

Your task: REWRITE and SIGNIFICANTLY UPGRADE this document for a knowledge graph RAG system. The current version scores LOW on our quality metrics. You must produce a document scoring 85+.

SCORING DIMENSIONS (you MUST optimize ALL):

1. SPECIFICITY (30% weight): Every sentence must contain information UNIQUE to this concept.
   - Include specific numbers, dates, inventor names, formula definitions
   - ZERO generic sentences. If you can swap the concept name and the sentence still works, DELETE IT.
   - BANNED phrases (instant penalty):
     "服务于核心体验", "玩家可感知", "可迭代", "过度设计",
     "参考成功案例建立初始方案", "快速制作原型",
     "明确设计目标和约束条件", "基于数据迭代改进",
     "的核心在于理解其基本定义", "初学者容易忽视"
     Any sentence that works for ANY concept by swapping the name

2. DENSITY (25% weight): Must have 2500+ Chinese characters of substantive content.
   - Add depth. No thin sections. Every paragraph teaches something concrete.

3. SOURCES (20% weight): Include at least TWO real citations.
   - Use real authors and years: (Author, Year)
   - Reference real books, papers, or seminal works
   - Cite specific theorems, equations, or experimental results

4. STRUCTURE (15% weight): Must have 6+ sections (## or ###).
   - Required: ## 概述, ## 核心原理 (with subsections), ## 关键方法/公式,
     ## 实际应用, ## 常见误区, ## 知识关联

5. TEACHING (10% weight): Must include ALL of these:
   - A formula (use LaTeX: $...$) if applicable to domain
   - A concrete example (use 例如/案例)
   - A thought-provoking question (use ？)

OUTPUT FORMAT:
- Output ONLY the document body. NO YAML frontmatter. NO ```markdown``` fences.
- Start with: # [Concept Name in Chinese]
- Minimum 2500 Chinese characters of substantive, concept-specific content."""

def build_user_prompt(doc_info, current_content):
    """Build the user prompt for rewriting a doc."""
    # Try to find seed data for context
    domain = doc_info["domain"]
    name = doc_info["name"]
    
    # Get concept info from seed graph if available
    context = ""
    seed_file = SEED_ROOT / domain / "seed_graph.json"
    if seed_file.exists():
        try:
            seed = json.loads(seed_file.read_text(encoding="utf-8"))
            for c in seed.get("concepts", []):
                if c["id"] == name or c.get("name", "") == name:
                    context = f"\nConcept ID: {c['id']}\nConcept Name: {c['name']}\nDescription: {c.get('description', '')}\nDifficulty: {c.get('difficulty', 5)}/9\n"
                    break
        except Exception:
            pass
    
    content_preview = current_content[:2000] if len(current_content) > 2000 else current_content
    
    return (
        f"REWRITE this document to score 85+ on our quality metrics.\n\n"
        f"Domain: {domain}\n"
        f"Document: {name}\n"
        f"Current score: {doc_info['score']:.1f} (needs 85+)\n"
        f"{context}\n"
        f"Current content (LOW QUALITY — rewrite completely):\n"
        f"---\n{content_preview}\n---\n\n"
        f"IMPORTANT:\n"
        f"- Replace ALL generic/template content with concept-specific knowledge\n"
        f"- Add real citations (Author, Year) and references\n"
        f"- Include mathematical formulas if applicable ($...$)\n"
        f"- Every paragraph must teach something UNIQUE to '{name}'\n"
        f"- Target: 2500+ Chinese characters of substantive content\n"
        f"- Do NOT include any of the banned generic phrases listed in system prompt"
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

def validate_output(content, concept_name):
    if not content or len(content) < 800:
        return False, "Too short"
    # Strip markdown fences if present
    content = re.sub(r"^```(?:markdown)?\s*\n?", "", content)
    content = re.sub(r"\n?```\s*$", "", content)
    # Check for banned stub phrases
    banned = ["服务于核心体验", "参考成功案例建立初始方案", "的核心在于理解其基本定义"]
    for phrase in banned:
        if phrase in content:
            return False, f"Contains banned phrase: {phrase}"
    return True, content

def load_progress():
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
    return {"completed": [], "errors": [], "stats": {"total": 0, "success": 0, "error": 0, "skipped": 0}}

def save_progress(progress):
    PROGRESS_FILE.write_text(json.dumps(progress, ensure_ascii=False, indent=2), encoding="utf-8")

def main():
    parser = argparse.ArgumentParser(description="Sprint 10: Final push to avg 80.0+")
    parser.add_argument("--max", type=int, default=80, help="Max docs to process")
    parser.add_argument("--threshold", type=float, default=76.5, help="Score threshold")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    args = parser.parse_args()

    print(f"Sprint 10: RAG Quality Final Push")
    print(f"Target: global avg 80.0+ (current 79.89)")
    print(f"Threshold: rewrite docs scoring <= {args.threshold}")
    print(f"Max docs: {args.max}")
    print()

    # Find bottom docs
    print("Scanning all RAG docs...")
    bottom = find_bottom_docs_manual(threshold=args.threshold, max_docs=args.max)
    print(f"Found {len(bottom)} docs below threshold {args.threshold}")
    
    if not bottom:
        print("No docs below threshold. Mission accomplished!")
        return
    
    if args.dry_run:
        for d in bottom:
            print(f"  {d['score']:5.1f}  {d['path']}")
        return

    # Load progress
    progress = load_progress()
    completed_set = set(progress["completed"])
    
    total = len(bottom)
    processed = 0
    
    for i, doc in enumerate(bottom):
        path_key = doc["path"]
        if path_key in completed_set:
            print(f"[{i+1}/{total}] {path_key} — already done, skip")
            continue
        
        abs_path = RAG_ROOT / doc["path"]
        if not abs_path.exists():
            print(f"[{i+1}/{total}] {path_key} — file not found, skip")
            progress["stats"]["skipped"] += 1
            continue
        
        current_content = abs_path.read_text(encoding="utf-8")
        print(f"[{i+1}/{total}] {doc['domain']}/{doc['name']} (score={doc['score']:.1f})...", end=" ", flush=True)
        
        try:
            user_prompt = build_user_prompt(doc, current_content)
            new_content = call_llm(SYSTEM_PROMPT, user_prompt)
            
            valid, result = validate_output(new_content, doc["name"])
            if not valid:
                print(f"❌ validation failed: {result}")
                progress["errors"].append({"path": path_key, "error": result})
                progress["stats"]["error"] += 1
                continue
            
            # Write upgraded content
            abs_path.write_text(result, encoding="utf-8")
            new_score = quick_score(result)
            print(f"✅ {len(result)} chars (score {doc['score']:.1f} → ~{new_score:.1f})")
            
            progress["completed"].append(path_key)
            completed_set.add(path_key)
            progress["stats"]["success"] += 1
            progress["stats"]["total"] += 1
            processed += 1
            
            # Save progress every 5 docs
            if processed % 5 == 0:
                save_progress(progress)
                print(f"  [checkpoint: {processed}/{total} done]")
            
            time.sleep(RATE_LIMIT_DELAY)
            
        except Exception as e:
            print(f"❌ {e}")
            progress["errors"].append({"path": path_key, "error": str(e)})
            progress["stats"]["error"] += 1
            traceback.print_exc()
    
    save_progress(progress)
    print(f"\n{'='*60}")
    print(f"Sprint 10 Complete!")
    print(f"  Processed: {processed}")
    print(f"  Success: {progress['stats']['success']}")
    print(f"  Errors: {progress['stats']['error']}")
    print(f"  Skipped: {progress['stats']['skipped']}")

if __name__ == "__main__":
    main()
