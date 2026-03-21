#!/usr/bin/env python3
"""
Research-Enhanced RAG Rewrite Pipeline v2.0

与 v1.0 的关键差异：每个概念精写前，先通过 WebResearch 获取外部知识，
编译为结构化的 external_knowledge 注入到改写 prompt 中。

工作流:
  1. 从 seed_graph 提取概念元数据 (name, description, prerequisites, next_concepts)
  2. 生成搜索查询策略 (中英文各 2 条, 共 4 条)
  3. WebSearch 搜索 + 读取 top 来源页面 (Wikipedia, 教科书在线版, Khan Academy 等)
  4. 编译外部知识为结构化文本 (含来源 URL + 关键事实)
  5. 注入 external_knowledge 到精写 prompt
  6. AI 生成精写内容 (要求引用来源中的事实)
  7. 验证 + 回写到 RAG 文档

搜索查询策略模板:
  - 英文精确查询:  "{concept_en} {key_terms} site:wikipedia.org OR site:khanacademy.org"
  - 英文学术查询:  "{concept_en} {domain_en} definition principles"
  - 中文科普查询:  "{concept_zh} {key_terms_zh} 原理 结构"
  - 中文教科书查询: "{concept_zh} {domain_zh} 教科书 知识点"

外部知识编译格式:
  ```
  ### 来源 1: {title} ({url})
  - 关键事实 1: ...
  - 关键事实 2: ...
  - 关键数据: ...

  ### 来源 2: {title} ({url})
  ...
  ```

用法:
    # 对单个概念执行完整 research + rewrite (由 Agent 调用)
    # Agent 负责: WebSearch → 编译知识 → 调用此脚本写入

    python scripts/research_rewrite.py --write-back \\
        --concept cell-membrane \\
        --domain biology \\
        --body-file data/rewrite_drafts/cell-membrane.md \\
        --sources-json data/rewrite_drafts/cell-membrane_sources.json

    # 生成搜索查询计划 (Agent 据此执行搜索)
    python scripts/research_rewrite.py --search-plan \\
        --concept cell-membrane --domain biology

    # 批量生成搜索计划
    python scripts/research_rewrite.py --batch-search-plan \\
        --domain biology --max 10
"""

import argparse
import json
import re
import sys
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
RAG_ROOT = PROJECT_ROOT / "data" / "rag"
SEED_ROOT = PROJECT_ROOT / "data" / "seed"
DRAFTS_DIR = PROJECT_ROOT / "data" / "rewrite_drafts"
QUALITY_DETAIL = PROJECT_ROOT / "data" / "quality_report_detail.json"
RESEARCH_LOG = PROJECT_ROOT / "data" / "research_rewrite_log.json"

# ─── 增强版 Prompt ───

REWRITE_SYSTEM_PROMPT_V2 = """你是一位{domain_name}领域的教学内容专家。你的任务是基于提供的外部参考资料，为学习者撰写高质量的教学参考文档。

核心原则:
1. 所有关键事实必须来自提供的参考资料，不可凭空编造
2. 每个核心知识点段落至少引用 1 条来源中的具体事实/数据
3. 公式、数值、年份等可验证信息必须与参考资料一致
4. 无法从参考资料确认的信息用 [待验证] 标记
5. 内容必须专门针对该概念，禁止使用通用模板语句

质量标准:
- 概述段包含: 概念定义 + 提出者/年代 + 在知识体系中的位置
- 核心知识点: ≥3 个子标题，每个含具体事实/公式/数据
- 关键要点: 3-5 条，每条有可验证的具体内容
- 常见误区: 2-3 个该概念特有的误解，解释为什么是错的
- 知识衔接: 基于 seed_graph 的先修/后续关系

禁止:
- "理解X需要把握其基本定义和关键性质"等万金油句子
- 未在参考资料中出现的数据或公式(除非标记[待验证])
- 使用相同的"设计原则"段落套用所有概念"""

REWRITE_USER_TEMPLATE_V2 = """请基于以下概念信息和外部参考资料，撰写教学参考文档。

## 概念信息
- 名称: {name}
- 描述: {description}
- 所属域: {domain_name}
- 所属子域: {subdomain_name}
- 难度: {difficulty}/9
- 先修概念: {prerequisites}
- 后续概念: {next_concepts}

## 外部参考资料 (已通过 Web Research 获取)
{external_knowledge}

## 输出格式
请直接输出 Markdown 正文(不含 YAML frontmatter)，结构:

# {name}

## 概述
(2-3段，基于参考资料的定义、历史、重要性)

## 核心知识点
(至少3个子标题，每个含来自参考资料的具体事实/公式/数据)

## 关键要点
(3-5条，每条引用参考资料中的具体内容)

## 常见误区
(2-3个该概念特有的误解，基于教学经验)

## 知识衔接
(与先修/后续概念的关系)

## 参考来源
(列出使用的参考资料，格式: - [来源名称](URL))

正文1500-2500字。"""


# ─── 搜索策略生成 ───

# 域名中英文映射
DOMAIN_NAME_MAP = {
    "biology": ("生物学", "Biology"),
    "physics": ("物理学", "Physics"),
    "mathematics": ("数学", "Mathematics"),
    "economics": ("经济学", "Economics"),
    "english": ("英语", "English Language"),
    "finance": ("金融学", "Finance"),
    "philosophy": ("哲学", "Philosophy"),
    "psychology": ("心理学", "Psychology"),
    "writing": ("写作", "Writing"),
    "product-design": ("产品设计", "Product Design"),
    "game-design": ("游戏设计", "Game Design"),
    "game-engine": ("游戏引擎", "Game Engine"),
    "level-design": ("关卡设计", "Level Design"),
    "narrative-design": ("叙事设计", "Narrative Design"),
    "game-audio-music": ("游戏音乐", "Game Music"),
    "game-audio-sfx": ("游戏音效", "Game Audio SFX"),
    "computer-graphics": ("计算机图形学", "Computer Graphics"),
    "3d-art": ("3D美术", "3D Art"),
    "animation": ("动画", "Animation"),
    "concept-design": ("概念设计", "Concept Design"),
    "technical-art": ("技术美术", "Technical Art"),
    "vfx": ("视觉特效", "Visual Effects"),
    "software-engineering": ("软件工程", "Software Engineering"),
    "ai-engineering": ("AI工程", "AI Engineering"),
    "llm-core": ("大语言模型", "Large Language Models"),
    "game-ui-ux": ("游戏UI/UX", "Game UI/UX"),
    "game-live-ops": ("游戏运营", "Game Live Operations"),
    "game-publishing": ("游戏发行", "Game Publishing"),
    "game-qa": ("游戏QA", "Game QA Testing"),
    "multiplayer-network": ("多人联网", "Multiplayer Networking"),
}


def load_seed_data(domain_filter=None):
    """加载 seed_graph 数据"""
    concept_map = {}
    subdomain_names = {}
    domain_names = {}
    edges_map = {}

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

        for e in sg.get("edges", []):
            src = e.get("source_id", e.get("source", e.get("from", "")))
            tgt = e.get("target_id", e.get("target", e.get("to", "")))
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

    for cid, info in concept_map.items():
        e = edges_map.get(cid, {"prereqs": [], "next": []})
        info["prerequisites"] = [concept_map[p]["name"] for p in e["prereqs"][:5] if p in concept_map]
        info["next_concepts"] = [concept_map[n]["name"] for n in e["next"][:5] if n in concept_map]

    return concept_map


def generate_search_queries(concept_info: dict) -> list:
    """为一个概念生成 4 条搜索查询"""
    name_zh = concept_info["name"]
    desc = concept_info["description"]
    domain_id = concept_info["domain"]
    domain_zh, domain_en = DOMAIN_NAME_MAP.get(domain_id, (domain_id, domain_id))

    # 从 description 提取英文关键词（如果有）或用概念 ID
    concept_id = concept_info["id"]
    # 将 kebab-case 转为 title case 作为英文名
    name_en = concept_id.replace("-", " ").title()

    # 提取 description 中的关键术语
    key_terms = desc.replace("、", " ").replace("与", " ").replace("和", " ")

    queries = [
        # Q1: 英文 Wikipedia/教育站点
        f"{name_en} {domain_en} Wikipedia definition structure",
        # Q2: 英文学术/教科书
        f"{name_en} {domain_en} principles key concepts textbook",
        # Q3: 中文科普
        f"{name_zh} {key_terms} 原理 定义",
        # Q4: 中文知识点
        f"{name_zh} {domain_zh} 核心知识点 教学",
    ]
    return queries


def generate_search_plan(concept_info: dict) -> dict:
    """生成一个概念的完整搜索计划"""
    queries = generate_search_queries(concept_info)

    # 推荐阅读的优先来源类型
    priority_sources = [
        "Wikipedia (en/zh)",
        "Khan Academy",
        "LibreTexts / OpenStax",
        "NCBI Bookshelf (Alberts, etc.)",
        "知乎专栏 (高质量回答)",
        "百度百科 (交叉验证)",
    ]

    return {
        "concept_id": concept_info["id"],
        "concept_name": concept_info["name"],
        "domain": concept_info["domain"],
        "description": concept_info["description"],
        "difficulty": concept_info["difficulty"],
        "is_milestone": concept_info.get("is_milestone", False),
        "search_queries": queries,
        "priority_sources": priority_sources,
        "min_sources_to_read": 3,
        "target_facts_per_source": 5,
        "instructions": (
            "1. 执行 4 条搜索查询\n"
            "2. 从结果中选择 3-5 个高质量来源页面阅读\n"
            "3. 优先选择: Wikipedia > 教科书在线版 > Khan Academy > 知乎\n"
            "4. 从每个来源提取 3-8 条关键事实\n"
            "5. 编译为 external_knowledge 格式\n"
            "6. 注入精写 prompt 并生成内容"
        ),
    }


def find_rag_file(concept_id: str, domain: str) -> Path:
    """查找概念对应的 RAG 文档路径"""
    domain_dir = RAG_ROOT / domain

    # 搜索所有子目录
    for md_file in domain_dir.rglob(f"{concept_id}.md"):
        return md_file

    # 直接在域目录下
    direct = domain_dir / f"{concept_id}.md"
    if direct.exists():
        return direct

    return None


def write_back_rewrite(concept_id: str, domain: str, new_body: str,
                       sources: list, dry_run: bool = False) -> dict:
    """将精写内容回写到 RAG 文档"""
    filepath = find_rag_file(concept_id, domain)
    if not filepath:
        return {"ok": False, "error": f"RAG file not found for {concept_id} in {domain}"}

    content = filepath.read_text(encoding="utf-8", errors="replace")

    # 提取 frontmatter
    match = re.match(r"^(---\s*\n.*?\n---)\s*\n?", content, re.DOTALL)
    if not match:
        return {"ok": False, "error": f"No frontmatter in {filepath}"}

    fm = match.group(1)

    # 更新 frontmatter 字段
    fm = re.sub(r"content_version:\s*\d+",
                lambda m: f"content_version: {int(m.group().split(':')[1].strip()) + 1}", fm)
    fm = re.sub(r'generation_method:.*', 'generation_method: "research-rewrite-v2"', fm)
    fm = re.sub(r'quality_tier:.*', 'quality_tier: "pending-rescore"', fm)
    fm = re.sub(r'last_scored:.*',
                f'last_scored: "{datetime.now().strftime("%Y-%m-%d")}"', fm)

    # 更新 sources
    if sources:
        # 移除旧的 sources 行
        fm = re.sub(r'\nsources:.*?(?=\n[a-zA-Z#-]|\n---)', '\n', fm, flags=re.DOTALL)
        # 在 --- 前插入新 sources
        sources_yaml = "sources:"
        for s in sources:
            s_type = s.get("type", "web")
            s_ref = s.get("ref", s.get("url", ""))
            s_url = s.get("url", "")
            sources_yaml += f'\n  - type: "{s_type}"'
            sources_yaml += f'\n    ref: "{s_ref}"'
            if s_url:
                sources_yaml += f'\n    url: "{s_url}"'
        fm = fm.rstrip().rstrip("-")
        if fm.endswith("\n"):
            fm += sources_yaml + "\n---"
        else:
            fm += "\n" + sources_yaml + "\n---"

    new_content = fm + "\n" + new_body.strip() + "\n"

    if dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "filepath": str(filepath),
            "new_size": len(new_content),
            "sources_count": len(sources),
        }

    filepath.write_text(new_content, encoding="utf-8")

    # 记录日志
    log_entry = {
        "concept_id": concept_id,
        "domain": domain,
        "filepath": str(filepath.relative_to(PROJECT_ROOT)),
        "timestamp": datetime.now().isoformat(),
        "method": "research-rewrite-v2",
        "sources_count": len(sources),
        "body_chars": len(new_body),
        "sources": sources,
    }
    append_to_log(log_entry)

    return {
        "ok": True,
        "filepath": str(filepath),
        "new_size": len(new_content),
        "sources_count": len(sources),
    }


def append_to_log(entry: dict):
    """追加到研究改写日志"""
    log = []
    if RESEARCH_LOG.is_file():
        with open(RESEARCH_LOG, "r", encoding="utf-8") as f:
            log = json.load(f)
    log.append(entry)
    with open(RESEARCH_LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Research-Enhanced RAG Rewrite Pipeline v2.0")
    parser.add_argument("--concept", type=str, help="Concept ID")
    parser.add_argument("--domain", type=str, help="Domain ID")
    parser.add_argument("--search-plan", action="store_true", help="Generate search plan for a concept")
    parser.add_argument("--batch-search-plan", action="store_true", help="Batch generate search plans")
    parser.add_argument("--write-back", action="store_true", help="Write rewritten body back to RAG file")
    parser.add_argument("--body-file", type=str, help="Path to rewritten body markdown file")
    parser.add_argument("--sources-json", type=str, help="Path to sources JSON file")
    parser.add_argument("--max", type=int, default=10, help="Max concepts for batch mode")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()

    concept_map = load_seed_data(domain_filter=args.domain)
    print(f"Research Rewrite Pipeline v2.0")
    print(f"  Loaded {len(concept_map)} concepts")

    if args.search_plan:
        if not args.concept:
            print("ERROR: --concept required with --search-plan")
            sys.exit(1)
        ci = concept_map.get(args.concept)
        if not ci:
            print(f"ERROR: concept '{args.concept}' not found")
            sys.exit(1)
        plan = generate_search_plan(ci)
        print(json.dumps(plan, ensure_ascii=False, indent=2))

    elif args.batch_search_plan:
        # 加载 quality detail 并按优先级排序
        if QUALITY_DETAIL.is_file():
            with open(QUALITY_DETAIL, "r", encoding="utf-8") as f:
                qd = json.load(f)
            # 过滤域
            if args.domain:
                qd = [d for d in qd if d.get("domain") == args.domain]
            # 排除已精写的
            qd = [d for d in qd if d.get("generation_method") != "research-rewrite-v2"]
            # 里程碑优先 + 低分优先
            qd.sort(key=lambda x: (not x.get("is_milestone", False), x.get("quality_score", 0)))
            candidates = qd[:args.max]
        else:
            candidates = []

        plans = []
        for doc in candidates:
            cid = doc.get("file", "").split("/")[-1].replace(".md", "")
            ci = concept_map.get(cid)
            if ci:
                plans.append(generate_search_plan(ci))

        DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
        output_path = DRAFTS_DIR / f"search_plans_{args.domain or 'all'}.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(plans, f, ensure_ascii=False, indent=2)
        print(f"  Generated {len(plans)} search plans → {output_path}")

    elif args.write_back:
        if not all([args.concept, args.domain, args.body_file]):
            print("ERROR: --concept, --domain, --body-file required with --write-back")
            sys.exit(1)

        body_path = Path(args.body_file)
        if not body_path.is_file():
            print(f"ERROR: body file not found: {body_path}")
            sys.exit(1)

        new_body = body_path.read_text(encoding="utf-8")

        sources = []
        if args.sources_json:
            sources_path = Path(args.sources_json)
            if sources_path.is_file():
                with open(sources_path, "r", encoding="utf-8") as f:
                    sources = json.load(f)

        result = write_back_rewrite(args.concept, args.domain, new_body,
                                     sources, dry_run=args.dry_run)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print("  Use --search-plan, --batch-search-plan, or --write-back")
        print("  Example: python scripts/research_rewrite.py --search-plan --concept cell-membrane --domain biology")


if __name__ == "__main__":
    main()
