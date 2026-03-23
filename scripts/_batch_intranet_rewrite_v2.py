#!/usr/bin/env python3
"""
Batch Intranet LLM Rewrite v2 — Tier-B → Tier-A+ upgrade.

Targets existing Tier-B documents (score 40-59) that were produced by
ai-rewrite-v1 / intranet-llm-rewrite-v1 with template-heavy content.
Uses a completely redesigned prompt that eliminates template patterns
and produces concept-specific, citation-rich content.

Usage:
    python scripts/_batch_intranet_rewrite_v2.py --domain animation --max 20
    python scripts/_batch_intranet_rewrite_v2.py --tier B --max 100
    python scripts/_batch_intranet_rewrite_v2.py --tier B --max 200 --min-score 40 --max-score 50
    python scripts/_batch_intranet_rewrite_v2.py --domain physics --max 20 --dry-run
"""

import argparse, json, os, re, sys, time, traceback
from datetime import datetime
from pathlib import Path
import httpx

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
RAG_ROOT = PROJECT_ROOT / "data" / "rag"
SEED_ROOT = PROJECT_ROOT / "data" / "seed"
QUALITY_DETAIL = PROJECT_ROOT / "data" / "quality_report_detail_detail.json"
LOG_FILE = PROJECT_ROOT / "data" / "intranet_rewrite_v2_log.json"

API_BASE = "https://llm-open-ai.mihoyo.com/v1"
API_KEY = "a12488be-58bb-4f52-93d0-26fee71d5507"
MODEL = "mihoyo.claude-4-6-sonnet"
MAX_TOKENS = 4096
RATE_LIMIT_DELAY = 1.5

# ── v2 Prompt: completely redesigned to eliminate template patterns ──

SYSTEM_PROMPT = """You are an expert educational content writer specializing in creating high-quality RAG teaching documents. Write in Chinese (Simplified).

Your task: Write a UNIQUE, concept-specific teaching document that will score 60+ on our quality rubric.

## SCORING RUBRIC (you MUST optimize for this):

1. **Concept Specificity (30%)** — Every sentence must contain facts UNIQUE to this concept. 
   - Score 0-50: Generic sentences that could apply to any concept
   - Score 80-100: Every paragraph has concept-specific facts, numbers, names, formulas

2. **Information Density (25%)** — After removing headers/formatting, need 1500+ chars of substantive text.
   - Each paragraph must be 100+ chars of real content
   - No padding sentences, no filler

3. **Source Credibility (20%)** — Must include inline citations in body text.
   - Include at least 2 inline citations in format: [Author, Year] or (Author et al., Year)
   - Reference real textbooks, papers, or standards by name
   - Example: "根据Shannon的信息论[Shannon, 1948]..." or "Knuth在《计算机程序设计艺术》中指出..."

4. **Structure Completeness (15%)** — Need 5+ substantive sections with real content.

5. **Teaching Adaptiveness (10%)** — Include formulas ($...$ or LaTeX), code (```), examples, AND questions.

## ABSOLUTE BANS (any match = document rejected):

The following sentence patterns are BANNED. Our automated detector catches them:
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
- "标志着学习者在该领域达到了重要的能力节点"
- "难度等级X/9"
- "学完后不看笔记复述"
- "在第1天、第3天、第7天分别回顾"
- "预计学习时间"
- "相关教科书中关于X的章节可作为"
- "可参考X领域的权威教材"
- Any sentence where swapping the concept name still makes it true

## OUTPUT FORMAT:

Output ONLY the markdown body content (NO YAML frontmatter, NO --- delimiters).

```
# [概念中文名]

## 概述
[2-3 paragraphs: precise definition with origin/history, why it specifically matters, 
 include a date or person who coined/invented it if applicable]

## 核心原理
### [Specific Subtopic 1]
[Detailed explanation with formulas/numbers/specifics]
### [Specific Subtopic 2]  
[More details unique to THIS concept]
### [Specific Subtopic 3]
[Include an inline citation here]

## 实际应用
[2-3 concrete, named real-world examples with specifics]

## 常见误区
[2-3 misconceptions SPECIFIC to this concept, with explanation of why they're wrong]

## 思考题
[2-3 thought-provoking questions that require understanding THIS specific concept]
```

## LENGTH: 1800-2500 Chinese characters of substantive content. Quality over quantity."""


def build_user_prompt(concept, existing_content_summary=""):
    """Build concept-specific user prompt with rich metadata."""
    prereqs = ", ".join(concept.get("prerequisites", [])) or "无"
    nexts = ", ".join(concept.get("next_concepts", [])) or "无"
    
    parts = [
        f"请为以下概念撰写教学文档：\n",
        f"概念名称: {concept['name']}",
        f"英文ID: {concept['id']}",
        f"所属领域: {concept['domain_name']} > {concept['subdomain_name']}",
        f"概念描述: {concept['description']}",
        f"难度: {concept['difficulty']}/9",
        f"先修概念: {prereqs}",
        f"后续概念: {nexts}",
    ]
    
    if concept.get("is_milestone"):
        parts.append("⭐ 这是一个里程碑概念（学习路径上的关键节点）")
    
    parts.append("")
    parts.append("要求：")
    parts.append("1. 每个段落必须包含该概念独有的具体事实、数据或公式")
    parts.append("2. 在正文中至少包含2个内联引用 [Author, Year] 或提及具体著作/标准")
    parts.append("3. 如果该概念涉及公式，用 $...$ 格式写出")
    parts.append("4. 如果该概念涉及代码/算法，用 ``` 代码块写出")
    parts.append(f'5. 禁止任何可以通过替换"{concept["name"]}"仍然成立的泛化句子')
    
    return "\n".join(parts)


def call_llm(system, user, retries=2):
    """Call intranet LLM with retry logic."""
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": MODEL, 
        "max_tokens": MAX_TOKENS,
        "messages": [
            {"role": "system", "content": system}, 
            {"role": "user", "content": user}
        ],
    }
    last_err = None
    for attempt in range(retries + 1):
        try:
            with httpx.Client(timeout=120.0) as client:
                resp = client.post(f"{API_BASE}/chat/completions", json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            last_err = e
            if attempt < retries:
                wait = 3 * (attempt + 1)
                print(f" RETRY({attempt+1}, wait {wait}s)...", end="", flush=True)
                time.sleep(wait)
    raise last_err


def load_seed_data(domain_filter=None):
    """Load concept metadata from seed graphs."""
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
    """Find the RAG markdown file for a concept."""
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
    """Update YAML frontmatter with new version info."""
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
    """Load quality report detail for filtering."""
    if not QUALITY_DETAIL.exists():
        return {}
    with open(QUALITY_DETAIL, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Key by concept file path (relative to RAG_ROOT)
    return {d["file"]: d for d in data}


def validate_output(body, concept_name):
    """Quick validation that output doesn't contain banned template patterns."""
    BANNED = [
        "是.{2,30}的核心组成部分之一",
        "起到承上启下的作用",
        "提供了必要的概念基础",
        "在.{2,30}基础上进一步拓展",
        "标志着学习者在该领域达到了重要的能力节点",
        "难度等级\\d+/9",
        "学完后不看笔记复述",
        "在第1天、第3天、第7天",
        "预计学习时间",
        "相关教科书中关于",
    ]
    issues = []
    for pat in BANNED:
        if re.search(pat, body):
            issues.append(f"Contains banned pattern: {pat}")
    
    # Check minimum length
    plain = re.sub(r"^#{1,6}\s+.*$", "", body, flags=re.MULTILINE)
    plain = re.sub(r"^\s*[-*]\s+", "", plain, flags=re.MULTILINE)
    plain = re.sub(r"\*\*|__|`", "", plain)
    plain = re.sub(r"\n{2,}", "\n", plain).strip()
    if len(plain) < 800:
        issues.append(f"Too short: {len(plain)} chars (need 800+)")
    
    return issues


def main():
    parser = argparse.ArgumentParser(description="Batch Intranet LLM Rewrite v2 (Tier-B → Tier-A+)")
    parser.add_argument("--domain", type=str, help="Filter by domain")
    parser.add_argument("--tier", type=str, default="B", help="Filter by tier (default: B)")
    parser.add_argument("--min-score", type=float, default=0, help="Min quality score")
    parser.add_argument("--max-score", type=float, default=59.9, help="Max quality score")
    parser.add_argument("--max", type=int, default=50, help="Max concepts to rewrite")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--concepts", type=str, help="Comma-separated concept IDs")
    args = parser.parse_args()

    print("=" * 60)
    print(f"Batch Intranet LLM Rewrite v2 — {MODEL}")
    print(f"Target: tier={args.tier}, domain={args.domain or 'all'}, "
          f"score={args.min_score}-{args.max_score}, max={args.max}")
    print("=" * 60)

    concept_map = load_seed_data(domain_filter=args.domain)
    quality_map = load_quality_scores()
    print(f"Loaded {len(concept_map)} concepts, {len(quality_map)} quality scores")

    if args.concepts:
        target_ids = [c.strip() for c in args.concepts.split(",")]
        candidates = [concept_map[cid] for cid in target_ids if cid in concept_map]
    else:
        scored = []
        for cid, info in concept_map.items():
            rag_path = find_rag_file(cid, info["domain"])
            if not rag_path:
                continue
            # Skip files already rewritten by v2 (check actual file content)
            try:
                header = rag_path.read_text(encoding="utf-8", errors="replace")[:500]
                if "intranet-llm-rewrite-v2" in header:
                    continue
            except Exception:
                pass
            rel = str(rag_path.relative_to(RAG_ROOT)).replace("\\", "/")
            # Also try backslash variant for Windows
            rel_bs = str(rag_path.relative_to(RAG_ROOT))
            q = quality_map.get(rel) or quality_map.get(rel_bs, {})
            score = q.get("quality_score", 999)
            tier = q.get("quality_tier", "?")
            if args.tier and tier != args.tier:
                continue
            if score < args.min_score or score > args.max_score:
                continue
            scored.append((score, tier, info))
        scored.sort(key=lambda x: x[0])
        candidates = [s[2] for s in scored[:args.max]]
        print(f"Selected {len(candidates)} candidates (worst-scoring first)")

    if not candidates:
        print("No candidates found!")
        return

    results = []
    ok_count = 0
    err_count = 0
    skip_count = 0
    start_time = time.time()
    
    for i, concept in enumerate(candidates):
        cid, domain = concept["id"], concept["domain"]
        rag_path = find_rag_file(cid, domain)
        if not rag_path:
            print(f"  [{i+1}/{len(candidates)}] SKIP {cid} (no RAG file)")
            skip_count += 1
            continue
        
        elapsed = time.time() - start_time
        rate = ok_count / elapsed * 60 if elapsed > 0 and ok_count > 0 else 0
        print(f"  [{i+1}/{len(candidates)}] {domain}/{cid} ({concept['name']}) "
              f"[{rate:.1f}/min]...", end="", flush=True)
        
        if args.dry_run:
            print(" DRY RUN")
            results.append({"concept": cid, "status": "dry-run"})
            continue
        
        try:
            user_prompt = build_user_prompt(concept)
            new_body = call_llm(SYSTEM_PROMPT, user_prompt)
            time.sleep(RATE_LIMIT_DELAY)
        except Exception as e:
            print(f" ERROR: {e}")
            results.append({"concept": cid, "status": "error", "error": str(e)})
            err_count += 1
            time.sleep(3)  # Extra cooldown on error
            continue
        
        # Validate output
        issues = validate_output(new_body, concept["name"])
        if issues:
            print(f" WARN: {'; '.join(issues[:2])}", end="")
        
        # Strip any YAML frontmatter the LLM might have included
        new_body = re.sub(r"^---\s*\n.*?\n---\s*\n?", "", new_body, count=1, flags=re.DOTALL)
        
        # Read existing file and update frontmatter
        content = rag_path.read_text(encoding="utf-8", errors="replace")
        updated = update_frontmatter(content, method="intranet-llm-rewrite-v2")
        
        # Replace body, keep frontmatter
        fm_match = re.match(r"^(---\s*\n.*?\n---)\s*\n?", updated, re.DOTALL)
        if fm_match:
            new_content = fm_match.group(1) + "\n" + new_body.strip() + "\n"
        else:
            new_content = new_body.strip() + "\n"
        
        rag_path.write_text(new_content, encoding="utf-8")
        body_chars = len(new_body.strip())
        print(f" OK ({body_chars} chars, {len(issues)} warns)")
        ok_count += 1
        results.append({
            "concept": cid, "domain": domain, "name": concept["name"],
            "status": "ok", "body_chars": body_chars, 
            "validation_issues": issues,
            "timestamp": datetime.now().isoformat()
        })

    elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"Done in {elapsed:.0f}s: {ok_count} rewritten, {err_count} errors, {skip_count} skipped")
    if ok_count > 0:
        print(f"Rate: {ok_count/elapsed*60:.1f} docs/min")

    if ok_count > 0 and not args.dry_run:
        log = []
        if LOG_FILE.exists():
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                log = json.load(f)
        log.extend([r for r in results if r["status"] == "ok"])
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(log, f, ensure_ascii=False, indent=2)
        print(f"Log saved: {LOG_FILE}")


if __name__ == "__main__":
    main()
