#!/usr/bin/env python3
"""
RAG Schema v2 升级脚本

读取 seed_graph.json + quality_report_detail.json，为每篇 RAG 文档
补全/升级 YAML frontmatter 到 Schema v2 标准。

操作:
  1. 无 frontmatter → 从 seed_graph 恢复并添加 v2 字段
  2. 旧 frontmatter → 保留原字段 + 追加 v2 字段
  3. 已有 v2 → 只更新 quality_score/quality_tier

用法:
    python scripts/upgrade_schema.py                  # 全量升级
    python scripts/upgrade_schema.py --domain biology  # 单域
    python scripts/upgrade_schema.py --dry-run         # 只预览不写入
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


def load_seed_graphs() -> dict:
    """加载所有 seed_graph.json，返回 {concept_id: {...}} 全局字典"""
    concept_map = {}
    subdomain_map = {}

    for domain_dir in sorted(SEED_ROOT.iterdir()):
        seed_path = domain_dir / "seed_graph.json"
        if not seed_path.is_file():
            continue
        with open(seed_path, "r", encoding="utf-8") as f:
            sg = json.load(f)

        domain_id = sg.get("domain", {}).get("id", domain_dir.name) if isinstance(sg.get("domain"), dict) else domain_dir.name

        # 子域映射
        for sd in sg.get("subdomains", []):
            subdomain_map[sd["id"]] = sd.get("name", sd["id"])

        # 里程碑集合（三种格式: {id:...}, {concept_id:...}, 纯字符串）
        milestone_ids = set()
        for m in sg.get("milestones", []):
            if isinstance(m, str):
                milestone_ids.add(m)
            elif isinstance(m, dict):
                milestone_ids.add(m.get("id", m.get("concept_id", "")))

        for c in sg.get("concepts", []):
            cid = c["id"]
            concept_map[cid] = {
                "id": cid,
                "name": c.get("name", cid),
                "description": c.get("description", ""),
                "domain": c.get("domain_id", domain_id),
                "subdomain_id": c.get("subdomain_id", ""),
                "subdomain_name": subdomain_map.get(c.get("subdomain_id", ""), ""),
                "difficulty": c.get("difficulty", 1),
                "is_milestone": cid in milestone_ids,
                "tags": c.get("tags", []),
            }

    return concept_map


def load_quality_scores() -> dict:
    """加载评分详情，返回 {file_relative_path: {quality_score, quality_tier, ...}}"""
    if not QUALITY_DETAIL.is_file():
        print(f"  WARNING: {QUALITY_DETAIL} not found, scores will be 0")
        return {}
    with open(QUALITY_DETAIL, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {d["file"]: d for d in data}


def parse_existing_frontmatter(content: str) -> tuple:
    """返回 (meta_dict, body_without_frontmatter, has_frontmatter)"""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", content, re.DOTALL)
    if not match:
        return {}, content, False

    meta = {}
    for line in match.group(1).split("\n"):
        line = line.strip()
        if ":" in line and not line.startswith("#"):
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if val.startswith("[") and val.endswith("]"):
                try:
                    val = json.loads(val.replace("'", '"'))
                except Exception:
                    pass
            meta[key] = val

    body = content[match.end():]
    return meta, body, True


def build_v2_frontmatter(concept_info: dict, quality_info: dict, old_meta: dict) -> str:
    """构建 Schema v2 YAML frontmatter 字符串"""
    ci = concept_info
    qi = quality_info

    # 合并: 优先用 seed_graph 的权威数据，保留旧 meta 中独有字段
    cid = ci.get("id", old_meta.get("id", ""))
    name = ci.get("name", old_meta.get("concept", old_meta.get("name", "")))
    domain = ci.get("domain", old_meta.get("domain", "unknown"))
    subdomain_id = ci.get("subdomain_id", old_meta.get("subdomain", ""))
    subdomain_name = ci.get("subdomain_name", old_meta.get("subdomain_name", ""))
    difficulty = ci.get("difficulty", int(old_meta.get("difficulty", 1) or 1))
    is_milestone = ci.get("is_milestone", str(old_meta.get("is_milestone", "false")).lower() == "true")
    tags = ci.get("tags", old_meta.get("tags", []))
    if isinstance(tags, str):
        try:
            tags = json.loads(tags.replace("'", '"'))
        except Exception:
            tags = [tags]

    # v2 质量字段
    content_version = int(old_meta.get("content_version", 1))
    quality_score = round(qi.get("quality_score", 0), 1)
    quality_tier = qi.get("quality_tier", "C")
    gen_method = old_meta.get("generation_method", "")
    if not gen_method:
        if quality_tier == "S":
            gen_method = "hand-crafted"
        elif quality_score >= 40:
            gen_method = "ai-batch-v1"
        else:
            gen_method = "template-v1"

    unique_ratio = qi.get("unique_content_ratio", 0)

    tags_str = json.dumps(tags, ensure_ascii=False) if tags else "[]"

    lines = [
        "---",
        f'id: "{cid}"',
        f'concept: "{name}"',
        f'domain: "{domain}"',
        f'subdomain: "{subdomain_id}"',
        f'subdomain_name: "{subdomain_name}"',
        f"difficulty: {difficulty}",
        f"is_milestone: {'true' if is_milestone else 'false'}",
        f"tags: {tags_str}",
        f"",
        f"# Quality Metadata (Schema v2)",
        f"content_version: {content_version}",
        f'quality_tier: "{quality_tier}"',
        f"quality_score: {quality_score}",
        f'generation_method: "{gen_method}"',
        f"unique_content_ratio: {unique_ratio}",
        f'last_scored: "{datetime.now().strftime("%Y-%m-%d")}"',
        "sources: []",
        "---",
    ]
    return "\n".join(lines)


def upgrade_domain(domain_name: str, concept_map: dict, quality_map: dict, dry_run: bool) -> dict:
    """升级单个域，返回统计"""
    domain_dir = RAG_ROOT / domain_name
    if not domain_dir.is_dir():
        return {"error": f"not found: {domain_dir}"}

    stats = {"total": 0, "created_fm": 0, "upgraded_fm": 0, "already_v2": 0, "no_seed": 0}

    # 收集所有md（含子目录）
    md_files = list(domain_dir.rglob("*.md"))
    md_files = [f for f in md_files if not f.name.startswith("_")]

    for md_path in md_files:
        stats["total"] += 1
        rel = str(md_path.relative_to(RAG_ROOT)).replace("\\", "/")
        concept_id = md_path.stem

        content = md_path.read_text(encoding="utf-8", errors="replace")
        old_meta, body, has_fm = parse_existing_frontmatter(content)

        # 从 seed_graph 查找概念信息
        ci = concept_map.get(concept_id, {})
        if not ci:
            # 尝试 domain 前缀匹配
            for k, v in concept_map.items():
                if v.get("domain") == domain_name and v.get("name", "") == old_meta.get("concept", "~"):
                    ci = v
                    break
        if not ci:
            stats["no_seed"] += 1
            ci = {"id": concept_id, "domain": domain_name}

        # 质量评分
        # quality_map 的 key 用 backslash (Windows), 也试 forward slash
        qi = quality_map.get(rel, quality_map.get(rel.replace("/", "\\"), {}))

        # 检查是否已有 v2
        if old_meta.get("content_version"):
            stats["already_v2"] += 1
            # 只更新评分
            if qi and not dry_run:
                new_score_line = f"quality_score: {round(qi.get('quality_score', 0), 1)}"
                new_tier_line = f'quality_tier: "{qi.get("quality_tier", "C")}"'
                if "quality_score:" in content:
                    content = re.sub(r"quality_score:.*", new_score_line, content)
                    content = re.sub(r'quality_tier:.*', new_tier_line, content)
                    md_path.write_text(content, encoding="utf-8")
            continue

        # 构建新 frontmatter
        new_fm = build_v2_frontmatter(ci, qi, old_meta)

        if has_fm:
            stats["upgraded_fm"] += 1
        else:
            stats["created_fm"] += 1

        if not dry_run:
            new_content = new_fm + "\n" + body.lstrip("\n")
            md_path.write_text(new_content, encoding="utf-8")

    return stats


def main():
    parser = argparse.ArgumentParser(description="Upgrade RAG docs to Schema v2")
    parser.add_argument("--domain", type=str, help="Single domain to upgrade")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    args = parser.parse_args()

    print("RAG Schema v2 Upgrade")
    print(f"  RAG Root: {RAG_ROOT}")
    print(f"  Dry run: {args.dry_run}")
    print()

    print("  Loading seed graphs...", end="", flush=True)
    concept_map = load_seed_graphs()
    print(f" {len(concept_map)} concepts")

    print("  Loading quality scores...", end="", flush=True)
    quality_map = load_quality_scores()
    print(f" {len(quality_map)} scores")
    print()

    domains = [args.domain] if args.domain else sorted(
        d.name for d in RAG_ROOT.iterdir() if d.is_dir()
    )

    grand = {"total": 0, "created_fm": 0, "upgraded_fm": 0, "already_v2": 0, "no_seed": 0}

    for domain_name in domains:
        stats = upgrade_domain(domain_name, concept_map, quality_map, args.dry_run)
        if "error" in stats:
            print(f"  {domain_name}: {stats['error']}")
            continue
        print(f"  {domain_name:<25} total={stats['total']:>4}  "
              f"created={stats['created_fm']:>4}  upgraded={stats['upgraded_fm']:>4}  "
              f"v2={stats['already_v2']:>4}  no_seed={stats['no_seed']:>4}")
        for k in grand:
            grand[k] += stats.get(k, 0)

    print(f"\n  {'TOTAL':<25} total={grand['total']:>4}  "
          f"created={grand['created_fm']:>4}  upgraded={grand['upgraded_fm']:>4}  "
          f"v2={grand['already_v2']:>4}  no_seed={grand['no_seed']:>4}")

    if args.dry_run:
        print("\n  [DRY RUN] No files modified. Remove --dry-run to apply.")


if __name__ == "__main__":
    main()
