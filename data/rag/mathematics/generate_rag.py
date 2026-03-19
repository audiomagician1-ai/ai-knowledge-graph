#!/usr/bin/env python3
"""
Generate math RAG documents (Phase 8.3).
Reads seed_graph.json, generates one .md per concept + _index.json.
Usage: python data/rag/mathematics/generate_rag.py
"""
import json, os, sys
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
SEED_PATH = os.path.join(PROJECT_ROOT, "data", "seed", "mathematics", "seed_graph.json")
TEMPLATES_PATH = os.path.join(SCRIPT_DIR, "_templates.json")
RAG_DIR = SCRIPT_DIR
INDEX_PATH = os.path.join(RAG_DIR, "_index.json")


def load_seed():
    with open(SEED_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_templates():
    if os.path.exists(TEMPLATES_PATH):
        with open(TEMPLATES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def build_edge_map(seed):
    cmap = {c["id"]: c["name"] for c in seed["concepts"]}
    prereqs, postreqs = {}, {}
    for e in seed["edges"]:
        s, t = e["source_id"], e["target_id"]
        prereqs.setdefault(t, []).append(cmap.get(s, s))
        postreqs.setdefault(s, []).append(cmap.get(t, t))
    return prereqs, postreqs


def generic_content(c):
    name, desc, diff = c["name"], c["description"], c["difficulty"]
    labels = {1:"入门",2:"基础",3:"基础进阶",4:"中级",5:"中级进阶",
              6:"中高级",7:"高级",8:"高级进阶",9:"研究级"}
    dl = labels.get(diff, "中级")
    core = (
        f"{name}({desc})是数学知识体系中的重要概念，难度为 {diff}/9({dl})。\n\n"
        f"### 定义与核心思想\n\n"
        f"{name}的核心在于{desc.rstrip(chr(12290))}。"
        f"理解{name}需要把握其基本定义和关键性质，并通过具体例题加深理解。\n\n"
        f"### 关键公式与性质\n\n"
        f"{name}涉及以下核心要点：\n\n"
        f"1. **基本定义**: {desc}\n"
        f"2. **关键性质**: 掌握{name}的核心性质是深入学习的基础\n"
        f"3. **典型应用**: {name}在数学其他分支和实际问题中都有广泛应用"
    )
    examples = (
        f"**练习建议**: 先从基本概念入手，通过课本例题理解{name}的定义和性质，"
        f"再尝试解决综合问题以提高熟练度。"
    )
    return core, examples


def generate_doc(concept, sub_name, prereqs, postreqs, templates):
    cid = concept["id"]
    name = concept["name"]
    desc = concept["description"]
    sub_id = concept["subdomain_id"]
    diff = concept["difficulty"]
    tags = concept.get("tags", [])
    is_ms = concept.get("is_milestone", False)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")

    # Try template, else generic
    if cid in templates:
        t = templates[cid]
        core, examples = t["core"], t["examples"]
    else:
        core, examples = generic_content(concept)

    prereq_list = prereqs.get(cid, [])
    postreq_list = postreqs.get(cid, [])
    rel = "## 关联知识\n\n"
    if prereq_list:
        joined = "、".join(prereq_list[:5])
        rel += f"- **先修概念**: {joined}\n  - 学习本概念前，建议先掌握以上概念\n"
    if postreq_list:
        joined = "、".join(postreq_list[:5])
        rel += f"- **后续概念**: {joined}\n  - 掌握本概念后，可以继续学习以上进阶内容\n"
    if not prereq_list and not postreq_list:
        rel += "本概念是基础起点概念，可直接开始学习。\n"

    pre_path = ""
    if prereq_list:
        pre_path = f"先回顾先修概念({'、'.join(prereq_list[:3])})，然后"

    hours_lo = max(5, diff * 3)
    hours_hi = max(10, diff * 5)
    ms_label = "里程碑" if is_ms else "重要"

    md = f"""---
id: "{cid}"
name: "{name}"
subdomain: "{sub_id}"
subdomain_name: "{sub_name}"
difficulty: {diff}
is_milestone: {"true" if is_ms else "false"}
tags: {json.dumps(tags, ensure_ascii=False)}
generated_at: "{now}"
---

# {name}

## 概述

{name}是{sub_name}领域中的{ms_label}概念，难度等级为 {diff}/9。

{desc}

## 核心内容

{core}

## 例题与练习

{examples}

{rel}
## 学习建议

- **推荐学习路径**: {pre_path}系统学习{name}的定义、公式和证明
- **实践方法**: 多做练习题，从基础计算到综合应用逐步提高
- **常见误区**: 注意公式的适用条件和推导细节，避免机械套用
- **预计学习时间**: 根据难度({diff}/9)，预计需要 {hours_lo}-{hours_hi} 小时
"""
    return md.strip() + "\n"


def main():
    seed = load_seed()
    templates = load_templates()
    sub_map = {s["id"]: s["name"] for s in seed["subdomains"]}
    prereqs, postreqs = build_edge_map(seed)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    index_docs = []
    total_chars = 0
    by_subdomain = {}

    for concept in seed["concepts"]:
        sub_id = concept["subdomain_id"]
        sub_name = sub_map.get(sub_id, sub_id)
        sub_dir = os.path.join(RAG_DIR, sub_id)
        os.makedirs(sub_dir, exist_ok=True)

        md = generate_doc(concept, sub_name, prereqs, postreqs, templates)
        fname = f"{concept['id']}.md"
        fpath = os.path.join(sub_dir, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(md)

        cc = len(md)
        total_chars += cc
        by_subdomain[sub_id] = by_subdomain.get(sub_id, 0) + 1
        index_docs.append({
            "id": concept["id"],
            "name": concept["name"],
            "domain_id": "mathematics",
            "subdomain_id": sub_id,
            "subdomain_name": sub_name,
            "difficulty": concept["difficulty"],
            "is_milestone": concept.get("is_milestone", False),
            "tags": concept.get("tags", []),
            "file": f"mathematics/{sub_id}/{fname}",
            "exists": True,
            "char_count": cc,
        })

    index_data = {
        "version": "1.0",
        "domain_id": "mathematics",
        "generated_at": now,
        "total_concepts": len(index_docs),
        "documents": index_docs,
        "stats": {
            "by_subdomain": by_subdomain,
            "total_docs": len(index_docs),
            "total_chars": total_chars,
        },
    }
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)

    print(f"Generated {len(index_docs)} RAG documents")
    print(f"Total chars: {total_chars:,}")
    print(f"Subdomains: {len(by_subdomain)}")
    for sid, cnt in sorted(by_subdomain.items()):
        print(f"  {sid}: {cnt}")


if __name__ == "__main__":
    main()
