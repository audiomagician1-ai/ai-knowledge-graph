#!/usr/bin/env python3
"""
RAG 改写管线 v1.0

四阶段管线: 评估 → 知识获取 → AI改写 → 验证

用法:
    # 改写单个概念
    python scripts/rewrite_pipeline.py --concept cell-membrane --domain biology

    # 按优先级改写一批(里程碑优先)
    python scripts/rewrite_pipeline.py --batch --max 10 --milestones-first

    # 只评估不改写(生成改写候选列表)
    python scripts/rewrite_pipeline.py --plan --max 50

    # 指定域批量改写
    python scripts/rewrite_pipeline.py --batch --domain physics --max 20
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
RAG_ROOT = PROJECT_ROOT / "data" / "rag"
SEED_ROOT = PROJECT_ROOT / "data" / "seed"
QUALITY_DETAIL = PROJECT_ROOT / "data" / "quality_report_detail.json"
REWRITE_LOG = PROJECT_ROOT / "data" / "rewrite_log.json"

# ─── 改写 Prompt 模板 ───

REWRITE_SYSTEM_PROMPT = """你是一位{domain_name}领域的教学内容专家。你的任务是为学习者撰写高质量的教学参考文档。

要求:
1. 内容必须专门针对该概念，禁止使用通用模板语句
2. 每个段落必须包含该概念特有的知识点
3. 至少包含3个可验证的关键事实(定义/公式/数据/案例)
4. 常见误区必须是该概念特有的，不是通用学习建议
5. 明确说明与先修概念的关系

禁止:
- "理解X需要把握其基本定义和关键性质"这类万金油句子
- 对所有概念使用相同的"设计原则"段落
- 如果不确定某个事实，用 [待验证] 标记"""

REWRITE_USER_TEMPLATE = """请为以下概念撰写教学参考文档。

## 概念信息
- 名称: {name}
- 描述: {description}
- 所属域: {domain_name}
- 所属子域: {subdomain_name}
- 难度: {difficulty}/9
- 先修概念: {prerequisites}
- 后续概念: {next_concepts}

## 外部参考资料
{external_knowledge}

## 输出格式
请直接输出 Markdown 正文(不含 YAML frontmatter)，结构:

# {name}

## 概述
(2-3段，该概念是什么、为什么重要、在知识体系中的位置)

## 核心知识点
(至少3个子标题，每个含具体事实/公式/定义)

## 关键要点
(该概念最重要的3-5条要点，每条有具体内容)

## 常见误区
(2-3个该概念特有的误解，每个要解释为什么是错的)

## 知识衔接
(与先修/后续概念的关系，学完后能解锁什么)

正文1500-2500字。"""


def load_seed_data() -> dict:
    """加载所有 seed_graph，返回 {concept_id: concept_info_with_edges}"""
    concept_map = {}
    subdomain_names = {}
    domain_names = {}
    edges_map = {}  # concept_id -> {prereqs: [], next: []}

    for domain_dir in sorted(SEED_ROOT.iterdir()):
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

        # Build edge map
        for e in sg.get("edges", []):
            src = e.get("source", e.get("from", ""))
            tgt = e.get("target", e.get("to", ""))
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
                "is_milestone": cid in milestone_ids,
            }

    # Merge edges into concepts
    for cid, info in concept_map.items():
        e = edges_map.get(cid, {"prereqs": [], "next": []})
        info["prerequisites"] = [concept_map[p]["name"] for p in e["prereqs"][:5] if p in concept_map]
        info["next_concepts"] = [concept_map[n]["name"] for n in e["next"][:5] if n in concept_map]

    return concept_map


def load_quality_data() -> list:
    """加载评分详情"""
    if not QUALITY_DETAIL.is_file():
        return []
    with open(QUALITY_DETAIL, "r", encoding="utf-8") as f:
        return json.load(f)


def get_rewrite_candidates(quality_data: list, domain: str = None,
                           milestones_first: bool = True, max_count: int = 50) -> list:
    """按改写优先级排序，返回候选列表"""

    def priority_key(doc):
        score = doc.get("quality_score", 0)
        is_ms = doc.get("is_milestone", False)
        diff = doc.get("difficulty", 5)

        # priority = (1 - score/100) * usage_weight * domain_weight
        usage_w = 3.0 if is_ms else (2.0 if diff <= 3 else 1.0)

        # 精确科学域权重
        d = doc.get("domain", "")
        if d in ("physics", "mathematics", "biology", "economics", "finance"):
            domain_w = 2.0
        elif d in ("llm-core", "computer-graphics", "game-engine", "software-engineering"):
            domain_w = 1.5
        else:
            domain_w = 1.0

        return (1.0 - score / 100.0) * usage_w * domain_w

    filtered = quality_data
    if domain:
        filtered = [d for d in filtered if d.get("domain") == domain]

    # 排除已经 Tier-S 的
    filtered = [d for d in filtered if d.get("quality_tier") != "S"]

    # 按优先级降序
    filtered.sort(key=priority_key, reverse=True)

    if milestones_first:
        ms = [d for d in filtered if d.get("is_milestone")]
        non_ms = [d for d in filtered if not d.get("is_milestone")]
        filtered = ms + non_ms

    return filtered[:max_count]


def build_rewrite_prompt(concept_info: dict, external_knowledge: str = "") -> tuple:
    """构建改写 prompt，返回 (system, user)"""
    ci = concept_info
    prereqs = ", ".join(ci.get("prerequisites", [])) or "无"
    nexts = ", ".join(ci.get("next_concepts", [])) or "无"
    ext = external_knowledge or "(暂无外部参考资料，请基于专业知识撰写，不确定的用 [待验证] 标记)"

    system = REWRITE_SYSTEM_PROMPT.format(domain_name=ci.get("domain_name", ci["domain"]))
    user = REWRITE_USER_TEMPLATE.format(
        name=ci["name"],
        description=ci.get("description", ""),
        domain_name=ci.get("domain_name", ci["domain"]),
        subdomain_name=ci.get("subdomain_name", ""),
        difficulty=ci.get("difficulty", 1),
        prerequisites=prereqs,
        next_concepts=nexts,
        external_knowledge=ext,
    )
    return system, user


def call_llm(system: str, user: str) -> str:
    """调用 LLM API 获取改写内容。当前使用占位实现 — 实际执行时由外部脚本或API调用替代。"""
    # TODO: 集成实际 LLM API (Claude/OpenAI)
    # 当前返回占位文本，实际使用时替换
    raise NotImplementedError(
        "LLM API 未配置。请使用 --generate-prompts 模式生成 prompt 文件，"
        "然后手动/批量调用 LLM 获取结果。"
    )


def validate_rewrite(new_body: str, concept_info: dict) -> dict:
    """验证改写结果质量"""
    issues = []
    plain = re.sub(r"[#*`\[\]()-]", "", new_body)

    # 长度检查
    if len(plain) < 800:
        issues.append(f"too_short: {len(plain)} chars (min 800)")
    if len(plain) > 5000:
        issues.append(f"too_long: {len(plain)} chars (max 5000)")

    # 结构检查
    h2_count = len(re.findall(r"^## ", new_body, re.MULTILINE))
    if h2_count < 3:
        issues.append(f"missing_sections: only {h2_count} h2 (min 3)")

    # 概念名出现检查
    name = concept_info.get("name", "")
    if name and name not in new_body:
        issues.append("concept_name_missing")

    # 待验证标记
    unverified = new_body.count("[待验证]")
    if unverified > 3:
        issues.append(f"too_many_unverified: {unverified}")

    # 模板段落检查
    template_phrases = [
        "服务于核心体验",
        "理解其基本定义",
        "需要具备扎实的基础知识",
        "过度依赖工具的自动功能",
    ]
    for tp in template_phrases:
        if tp in new_body:
            issues.append(f"template_detected: '{tp}'")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "char_count": len(plain),
        "h2_count": h2_count,
        "unverified_count": unverified,
    }


def update_rag_doc(filepath: Path, new_body: str, concept_info: dict):
    """回写改写结果到 RAG 文档，保留 frontmatter 并更新版本号"""
    content = filepath.read_text(encoding="utf-8", errors="replace")

    # 提取现有 frontmatter
    match = re.match(r"^(---\s*\n.*?\n---)\s*\n?", content, re.DOTALL)
    if match:
        fm = match.group(1)
        # 更新 content_version
        fm = re.sub(r"content_version:\s*\d+", lambda m: f"content_version: {int(m.group().split(':')[1].strip()) + 1}", fm)
        # 更新 generation_method
        fm = re.sub(r'generation_method:.*', 'generation_method: "ai-rewrite-v1"', fm)
        # 更新 last_scored
        fm = re.sub(r'last_scored:.*', f'last_scored: "{datetime.now().strftime("%Y-%m-%d")}"', fm)
    else:
        fm = "---\n# ERROR: no frontmatter found\n---"

    new_content = fm + "\n" + new_body.strip() + "\n"
    filepath.write_text(new_content, encoding="utf-8")


def generate_prompt_files(candidates: list, concept_map: dict, output_dir: Path):
    """生成 prompt 文件供手动/批量 LLM 调用"""
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest = []
    for doc in candidates:
        concept_id = doc.get("file", "").replace("\\", "/").split("/")[-1].replace(".md", "")
        ci = concept_map.get(concept_id)
        if not ci:
            continue

        system, user = build_rewrite_prompt(ci)

        prompt_file = output_dir / f"{concept_id}.json"
        prompt_data = {
            "concept_id": concept_id,
            "concept_name": ci["name"],
            "domain": ci["domain"],
            "subdomain": ci.get("subdomain_name", ""),
            "difficulty": ci["difficulty"],
            "is_milestone": ci.get("is_milestone", False),
            "current_score": doc.get("quality_score", 0),
            "current_tier": doc.get("quality_tier", "C"),
            "rag_file": doc.get("file", ""),
            "system_prompt": system,
            "user_prompt": user,
        }
        with open(prompt_file, "w", encoding="utf-8") as f:
            json.dump(prompt_data, f, ensure_ascii=False, indent=2)

        manifest.append({
            "concept_id": concept_id,
            "name": ci["name"],
            "domain": ci["domain"],
            "score": doc.get("quality_score", 0),
            "is_milestone": ci.get("is_milestone", False),
            "prompt_file": str(prompt_file.relative_to(PROJECT_ROOT)),
        })

    # 写 manifest
    manifest_path = output_dir / "_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump({"generated": datetime.now().isoformat(), "count": len(manifest),
                    "prompts": manifest}, f, ensure_ascii=False, indent=2)

    return manifest


def main():
    parser = argparse.ArgumentParser(description="RAG Rewrite Pipeline v1.0")
    parser.add_argument("--concept", type=str, help="Rewrite single concept by ID")
    parser.add_argument("--domain", type=str, help="Filter by domain")
    parser.add_argument("--batch", action="store_true", help="Batch rewrite mode")
    parser.add_argument("--max", type=int, default=20, help="Max concepts to process")
    parser.add_argument("--milestones-first", action="store_true", default=True)
    parser.add_argument("--plan", action="store_true", help="Only show rewrite plan")
    parser.add_argument("--generate-prompts", action="store_true",
                        help="Generate prompt files for manual LLM calls")
    args = parser.parse_args()

    print("RAG Rewrite Pipeline v1.0")
    print(f"  Mode: {'plan' if args.plan else 'generate-prompts' if args.generate_prompts else 'batch' if args.batch else 'single'}")
    print()

    concept_map = load_seed_data()
    print(f"  Loaded {len(concept_map)} concepts from seed graphs")

    quality_data = load_quality_data()
    print(f"  Loaded {len(quality_data)} quality scores")

    if args.plan or args.generate_prompts or args.batch:
        candidates = get_rewrite_candidates(
            quality_data, domain=args.domain,
            milestones_first=args.milestones_first, max_count=args.max
        )

        if args.plan:
            print(f"\n  Top {len(candidates)} rewrite candidates:")
            print(f"  {'#':>3} {'Score':>5} {'Tier':>4} {'MS':>3} {'Domain':<22} {'Concept'}")
            print(f"  {'-'*3} {'-'*5} {'-'*4} {'-'*3} {'-'*22} {'-'*30}")
            for i, c in enumerate(candidates):
                ms = "Y" if c.get("is_milestone") else ""
                print(f"  {i+1:>3} {c['quality_score']:>5.1f} {c['quality_tier']:>4} {ms:>3} "
                      f"{c['domain']:<22} {c['concept']}")
            return

        if args.generate_prompts:
            output_dir = PROJECT_ROOT / "data" / "rewrite_prompts"
            manifest = generate_prompt_files(candidates, concept_map, output_dir)
            print(f"\n  Generated {len(manifest)} prompt files in {output_dir}")
            print(f"  Manifest: {output_dir / '_manifest.json'}")
            return

        # batch mode with actual LLM calls
        print(f"\n  Processing {len(candidates)} candidates...")
        print("  ERROR: LLM API not configured. Use --generate-prompts instead.")
        return

    elif args.concept:
        ci = concept_map.get(args.concept)
        if not ci:
            print(f"  ERROR: concept '{args.concept}' not found in seed graphs")
            sys.exit(1)
        system, user = build_rewrite_prompt(ci)
        print(f"\n  Concept: {ci['name']} ({ci['domain']}/{ci.get('subdomain_name', '')})")
        print(f"  Difficulty: {ci['difficulty']}/9  Milestone: {ci.get('is_milestone', False)}")
        print(f"\n--- SYSTEM PROMPT ---\n{system}")
        print(f"\n--- USER PROMPT ---\n{user}")


if __name__ == "__main__":
    main()
