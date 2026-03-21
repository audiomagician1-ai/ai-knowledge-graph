#!/usr/bin/env python3
"""
RAG 知识库质量评分器 v1.0

对 data/rag/ 下所有 .md 文档自动评分 (0-100)，输出 quality_report.json。

评分维度 (总分100):
  1. 概念特异性 (30%)  — 正文中非模板段落占比
  2. 信息密度   (25%)  — 去除格式后有效字符数
  3. 来源可信度 (20%)  — YAML sources 字段质量
  4. 结构完整度 (15%)  — 核心段落数
  5. 教学适配度 (10%)  — 公式/代码/案例/引导性问题

用法:
    python scripts/quality_scorer.py                     # 全量评分
    python scripts/quality_scorer.py --domain biology     # 单域
    python scripts/quality_scorer.py --report-only        # 只输出统计摘要
"""

import argparse
import json
import os
import re
import sys
import hashlib
from collections import defaultdict
from pathlib import Path
from datetime import datetime

# ─── 项目根路径 ───
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
RAG_ROOT = PROJECT_ROOT / "data" / "rag"

# ─── 已知模板固定段落指纹（用于计算特异性）───
# 这些是 generate_rag.py 和对话批量生成中反复出现的文本
TEMPLATE_FINGERPRINTS = [
    # game-dev Tier-C 通用段落
    "服务于核心体验：每个设计决策都应强化而非分散核心乐趣",
    "玩家可感知：设计效果需要通过反馈让玩家感受到",
    "可迭代：留有调整空间，便于后续平衡和优化",
    "过度设计: 功能复杂不等于体验丰富，简洁的系统往往更优雅",
    "忽视玩家感受: 数据上合理但玩家体验不佳的设计需要调整",
    "照搬其他游戏: 每个游戏有独特的设计语境",
    "明确设计目标和约束条件",
    "参考成功案例建立初始方案",
    "快速制作原型或纸面模拟",
    "组织测试并收集反馈",
    "基于数据迭代改进",
    "电子表格(Excel/Google Sheets)用于数值模拟",
    "白板/Miro用于流程梳理",
    # biology/physics Tier-B 共享段落
    "细胞是生命的基本单位",
    "理解该概念的核心定义和设计目的",
    "掌握其在游戏系统中的作用和位置",
    "了解与其他系统的交互关系",
    # llm-core Tier-B (auto-generated ones)
    "的核心在于理解其基本定义、设计目标和解决的关键问题",
    "学习者需要具备扎实的基础知识才能深入理解其内在原理",
    "的设计和实现遵循特定的理论基础和工程实践",
    # 无frontmatter Tier-C (3d-art, game-engine, etc.) 通用段落
    "初学者容易忽视",
    "过度依赖工具的自动功能而缺乏手动控制能力",
    "阶段的决策会影响后续管线所有环节",
    "需要从全局视角理解",
    "不同项目类型(游戏/影视/移动端)",
    "需要根据项目需求灵活调整",
    "是核心组成部分。技术美术和3D美术师需要深入理解其原理",
    "才能高效地完成高质量资产制作",
    "环节的核心组成部分",
    "需要深入理解其原理",
]


def parse_yaml_frontmatter(content: str) -> dict:
    """提取 YAML frontmatter 字段（简易解析，不依赖 pyyaml）"""
    meta = {}
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return meta
    for line in match.group(1).split("\n"):
        line = line.strip()
        if ":" in line and not line.startswith("#"):
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            meta[key] = val
    return meta


def strip_frontmatter(content: str) -> str:
    """移除 YAML frontmatter 返回正文"""
    return re.sub(r"^---\s*\n.*?\n---\s*\n?", "", content, count=1, flags=re.DOTALL)


def strip_markdown_formatting(text: str) -> str:
    """移除 markdown 标题/格式标记，保留纯文本"""
    text = re.sub(r"^#{1,6}\s+.*$", "", text, flags=re.MULTILINE)  # 标题行
    text = re.sub(r"^\s*[-*]\s+", "", text, flags=re.MULTILINE)    # 列表标记
    text = re.sub(r"\*\*|__|\*|_|`", "", text)                     # 加粗/斜体/code
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)           # 链接
    text = re.sub(r"\n{2,}", "\n", text)                           # 多余空行
    return text.strip()


def score_doc(filepath: Path, subdomain_docs: list[str] = None) -> dict:
    """
    对单篇文档评分，返回评分详情字典。
    subdomain_docs: 同子域其他文档正文列表（用于计算同子域特异性）。
    """
    content = filepath.read_text(encoding="utf-8", errors="replace")
    meta = parse_yaml_frontmatter(content)
    body = strip_frontmatter(content)
    plain = strip_markdown_formatting(body)
    body_lower = body.lower()

    # 从文件路径推断 domain/subdomain（当 YAML 缺失时使用）
    rel = filepath.relative_to(RAG_ROOT)
    parts = rel.parts  # e.g. ('biology', 'cell-biology', 'cell-membrane.md') or ('3d-art', '3da-bake-ao.md')
    path_domain = parts[0] if len(parts) >= 1 else "unknown"
    path_subdomain = parts[1] if len(parts) >= 3 else "_root_"

    result = {
        "file": str(rel),
        "domain": meta.get("domain", path_domain),
        "subdomain": meta.get("subdomain", meta.get("subdomain_name", path_subdomain)),
        "concept": meta.get("concept", meta.get("name", filepath.stem)),
        "difficulty": int(meta.get("difficulty", 0) or 0),
        "is_milestone": meta.get("is_milestone", "false").lower() == "true",
        "content_bytes": len(content.encode("utf-8")),
        "plain_chars": len(plain),
    }

    # ── 维度1: 概念特异性 (30%) ──
    # 方法: 逐行检测，匹配模板指纹的行 → 模板行
    lines = [l.strip() for l in body.split("\n") if len(l.strip()) > 15]
    total_lines = max(len(lines), 1)
    template_lines = 0
    for line in lines:
        for fp in TEMPLATE_FINGERPRINTS:
            if fp in line:
                template_lines += 1
                break
    
    # 同子域相似度补充检测
    if subdomain_docs and len(subdomain_docs) > 0:
        # 取本文档有效行的 hash 集合，与同子域其他文档比对
        my_hashes = set()
        for l in lines:
            if len(l) > 20:
                my_hashes.add(hashlib.md5(l.encode()).hexdigest())
        
        max_overlap = 0
        for other_body in subdomain_docs:
            other_lines = [l.strip() for l in other_body.split("\n") if len(l.strip()) > 20]
            other_hashes = {hashlib.md5(l.encode()).hexdigest() for l in other_lines}
            if my_hashes:
                overlap = len(my_hashes & other_hashes) / len(my_hashes)
                max_overlap = max(max_overlap, overlap)
        
        # 合并: 取模板指纹检测和同子域相似度的较大值
        fingerprint_ratio = template_lines / total_lines
        unique_ratio = 1.0 - max(fingerprint_ratio, max_overlap)
    else:
        unique_ratio = 1.0 - (template_lines / total_lines)

    unique_ratio = max(0.0, min(1.0, unique_ratio))
    
    if unique_ratio < 0.2:
        specificity_score = 0
    elif unique_ratio < 0.6:
        specificity_score = int(50 * (unique_ratio - 0.2) / 0.4)
    else:
        specificity_score = int(50 + 50 * (unique_ratio - 0.6) / 0.4)
    
    result["unique_content_ratio"] = round(unique_ratio, 3)
    result["dim1_specificity"] = min(specificity_score, 100)

    # ── 维度2: 信息密度 (25%) ──
    plain_len = len(plain)
    if plain_len < 300:
        density_score = 0
    elif plain_len < 800:
        density_score = int(50 * (plain_len - 300) / 500)
    elif plain_len < 2000:
        density_score = int(50 + 50 * (plain_len - 800) / 1200)
    else:
        density_score = 100
    
    result["dim2_density"] = density_score

    # ── 维度3: 来源可信度 (20%) ──
    has_sources = "sources:" in content.lower() or "source:" in content.lower()
    has_textbook = bool(re.search(r"(教科书|textbook|et al\.|edition|ISBN)", content, re.I))
    has_wiki = bool(re.search(r"(wikipedia|维基|百科)", content, re.I))
    has_paper = bool(re.search(r"(arXiv|论文|paper|doi:|IEEE|ACM)", content, re.I))
    
    source_score = 0
    if has_textbook or has_paper:
        source_score = 100
    elif has_wiki:
        source_score = 50
    elif has_sources:
        source_score = 30
    # 纯AI无来源 = 0
    
    result["dim3_sources"] = source_score
    result["has_sources"] = has_sources
    result["has_textbook"] = has_textbook

    # ── 维度4: 结构完整度 (15%) ──
    sections = re.findall(r"^##\s+.+", body, re.MULTILINE)
    subsections = re.findall(r"^###\s+.+", body, re.MULTILINE)
    total_sections = len(sections) + len(subsections)
    
    if total_sections <= 2:
        structure_score = 0
    elif total_sections <= 4:
        structure_score = 50
    elif total_sections <= 6:
        structure_score = 75
    else:
        structure_score = 100
    
    result["section_count"] = total_sections
    result["dim4_structure"] = structure_score

    # ── 维度5: 教学适配度 (10%) ──
    has_formula = bool(re.search(r"(\$.*\$|\\frac|\\sum|\\int|softmax|sigmoid)", content))
    has_code = "```" in content
    has_example = bool(re.search(r"(例如|比如|例：|案例|example|e\.g\.|举例)", content, re.I))
    has_question = bool(re.search(r"(？|\?|思考|为什么|如何)", body))
    
    teach_items = sum([has_formula, has_code, has_example, has_question])
    teach_score = min(int(teach_items * 33), 100)
    
    result["has_formula"] = has_formula
    result["has_code"] = has_code
    result["has_example"] = has_example
    result["dim5_teaching"] = teach_score

    # ── 总分 ──
    total = (
        result["dim1_specificity"] * 0.30 +
        result["dim2_density"] * 0.25 +
        result["dim3_sources"] * 0.20 +
        result["dim4_structure"] * 0.15 +
        result["dim5_teaching"] * 0.10
    )
    result["quality_score"] = round(total, 1)

    # ── Tier 分层 ──
    if total >= 80:
        result["quality_tier"] = "S"
    elif total >= 60:
        result["quality_tier"] = "A"
    elif total >= 40:
        result["quality_tier"] = "B"
    else:
        result["quality_tier"] = "C"

    return result


def collect_subdomain_docs(domain_dir: Path) -> dict[str, list]:
    """收集同子域文档正文，用于相似度对比。返回 {subdomain_dir: [body1, body2, ...]}"""
    groups = defaultdict(list)
    for subdir in sorted(domain_dir.iterdir()):
        if subdir.is_dir():
            for md in sorted(subdir.glob("*.md")):
                body = strip_frontmatter(md.read_text(encoding="utf-8", errors="replace"))
                groups[str(subdir)].append((md, body))
        # 也处理直接放在域目录下的 .md（非 _index/generate_rag）
    for md in sorted(domain_dir.glob("*.md")):
        if md.name.startswith("_"):
            continue
        body = strip_frontmatter(md.read_text(encoding="utf-8", errors="replace"))
        groups["_root_"].append((md, body))
    return groups


def run_scoring(target_domain: str = None, max_compare: int = 5) -> dict:
    """
    执行全量/单域评分。
    max_compare: 同子域相似度对比最多取多少篇（节省时间）。
    """
    all_results = []
    domain_dirs = sorted(RAG_ROOT.iterdir())
    
    for domain_dir in domain_dirs:
        if not domain_dir.is_dir():
            continue
        domain_name = domain_dir.name
        if target_domain and domain_name != target_domain:
            continue
        
        print(f"  Scoring domain: {domain_name} ...", end="", flush=True)
        
        # 收集子域分组
        subdomain_groups = collect_subdomain_docs(domain_dir)
        domain_count = 0
        
        for subdir_key, doc_list in subdomain_groups.items():
            for i, (md_path, body) in enumerate(doc_list):
                # 构建同子域其他文档列表（排除自身）
                others = [b for j, (_, b) in enumerate(doc_list) if j != i]
                if len(others) > max_compare:
                    others = others[:max_compare]
                
                result = score_doc(md_path, others)
                all_results.append(result)
                domain_count += 1
        
        print(f" {domain_count} docs")
    
    return all_results


def generate_report(results: list) -> dict:
    """生成统计摘要报告"""
    if not results:
        return {"error": "No documents found"}
    
    # 按域统计
    domain_stats = defaultdict(lambda: {
        "count": 0, "total_score": 0, "tiers": {"S": 0, "A": 0, "B": 0, "C": 0},
        "min_score": 100, "max_score": 0
    })
    
    tier_counts = {"S": 0, "A": 0, "B": 0, "C": 0}
    total_score = 0
    
    for r in results:
        d = r["domain"]
        s = r["quality_score"]
        t = r["quality_tier"]
        
        domain_stats[d]["count"] += 1
        domain_stats[d]["total_score"] += s
        domain_stats[d]["tiers"][t] += 1
        domain_stats[d]["min_score"] = min(domain_stats[d]["min_score"], s)
        domain_stats[d]["max_score"] = max(domain_stats[d]["max_score"], s)
        
        tier_counts[t] += 1
        total_score += s
    
    # 构建摘要
    domain_summary = {}
    for d, st in sorted(domain_stats.items()):
        domain_summary[d] = {
            "count": st["count"],
            "avg_score": round(st["total_score"] / st["count"], 1),
            "min_score": st["min_score"],
            "max_score": st["max_score"],
            "tiers": st["tiers"],
        }
    
    # 最低分 TOP 20（改写优先）
    worst_20 = sorted(results, key=lambda x: x["quality_score"])[:20]
    worst_list = [
        {"file": r["file"], "concept": r["concept"], "score": r["quality_score"],
         "tier": r["quality_tier"], "domain": r["domain"]}
        for r in worst_20
    ]
    
    # 最高分 TOP 10（标杆）
    best_10 = sorted(results, key=lambda x: -x["quality_score"])[:10]
    best_list = [
        {"file": r["file"], "concept": r["concept"], "score": r["quality_score"],
         "tier": r["quality_tier"], "domain": r["domain"]}
        for r in best_10
    ]
    
    report = {
        "_generated": datetime.now().isoformat(),
        "_version": "scorer-v1.0",
        "total_docs": len(results),
        "avg_score": round(total_score / len(results), 1),
        "tier_distribution": tier_counts,
        "domain_summary": domain_summary,
        "top10_best": best_list,
        "top20_worst": worst_list,
        "all_scores": results,
    }
    return report


def print_summary(report: dict):
    """打印终端可读摘要"""
    print("\n" + "=" * 60)
    print(f"  RAG Quality Report — {report['total_docs']} documents")
    print(f"  Average Score: {report['avg_score']}/100")
    print("=" * 60)
    
    td = report["tier_distribution"]
    print(f"\n  Tier Distribution:")
    print(f"    S (80-100): {td['S']:>5} ({td['S']/report['total_docs']*100:.1f}%)")
    print(f"    A (60-79):  {td['A']:>5} ({td['A']/report['total_docs']*100:.1f}%)")
    print(f"    B (40-59):  {td['B']:>5} ({td['B']/report['total_docs']*100:.1f}%)")
    print(f"    C (0-39):   {td['C']:>5} ({td['C']/report['total_docs']*100:.1f}%)")
    
    print(f"\n  Domain Breakdown:")
    print(f"  {'Domain':<25} {'Count':>5} {'Avg':>5} {'Min':>5} {'Max':>5}  S/A/B/C")
    print(f"  {'-'*25} {'-'*5} {'-'*5} {'-'*5} {'-'*5}  {'-'*15}")
    for d, st in sorted(report["domain_summary"].items(), key=lambda x: x[1]["avg_score"]):
        t = st["tiers"]
        print(f"  {d:<25} {st['count']:>5} {st['avg_score']:>5.1f} "
              f"{st['min_score']:>5.1f} {st['max_score']:>5.1f}  "
              f"{t['S']}/{t['A']}/{t['B']}/{t['C']}")
    
    print(f"\n  Top 10 Best:")
    for r in report["top10_best"]:
        print(f"    {r['score']:>5.1f}  [{r['tier']}] {r['domain']}/{r['concept']}")
    
    print(f"\n  Top 20 Worst (rewrite priority):")
    for r in report["top20_worst"]:
        print(f"    {r['score']:>5.1f}  [{r['tier']}] {r['domain']}/{r['concept']}")
    
    print()


def main():
    parser = argparse.ArgumentParser(description="RAG Knowledge Base Quality Scorer")
    parser.add_argument("--domain", type=str, help="Score single domain only")
    parser.add_argument("--report-only", action="store_true", help="Print summary only (skip saving)")
    parser.add_argument("--output", type=str, default=None, help="Output JSON path")
    args = parser.parse_args()
    
    print(f"RAG Quality Scorer v1.0")
    print(f"RAG Root: {RAG_ROOT}")
    print(f"Target: {'all domains' if not args.domain else args.domain}")
    print()
    
    results = run_scoring(target_domain=args.domain)
    
    if not results:
        print("ERROR: No documents found!")
        sys.exit(1)
    
    report = generate_report(results)
    print_summary(report)
    
    if not args.report_only:
        out_path = args.output or str(PROJECT_ROOT / "data" / "quality_report.json")
        # 保存时去掉 all_scores 以减小文件体积，单独保存
        report_lite = {k: v for k, v in report.items() if k != "all_scores"}
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(report_lite, f, ensure_ascii=False, indent=2)
        print(f"  Report saved: {out_path}")
        
        # 全量详情保存
        detail_path = out_path.replace(".json", "_detail.json")
        with open(detail_path, "w", encoding="utf-8") as f:
            json.dump(report["all_scores"], f, ensure_ascii=False, indent=2)
        print(f"  Detail saved: {detail_path}")


if __name__ == "__main__":
    main()
