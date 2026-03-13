"""
本地批量生成 RAG 知识库文档
使用结构化模板 + 内置知识库，为种子图谱所有概念生成参考文档。
输出: data/rag/{subdomain_id}/{concept_id}.md

用法:
  python data/scripts/batch_generate_local.py
  python data/scripts/batch_generate_local.py --subdomain llm-core
  python data/scripts/batch_generate_local.py --stats
"""

import json
import time
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SEED_GRAPH = PROJECT_ROOT / "data" / "seed" / "programming" / "seed_graph.json"
RAG_DIR = PROJECT_ROOT / "data" / "rag"

# ──────────────────────────────────────────────────────
# 知识内容数据库（核心概念的详细文档内容）
# 每个概念的内容分段存储，方便后续渲染
# ──────────────────────────────────────────────────────

KNOWLEDGE_DB = {}  # Will be populated from knowledge files

def load_seed_graph():
    with open(SEED_GRAPH, "r", encoding="utf-8") as f:
        return json.load(f)

def get_context(concept, graph):
    """获取图谱上下文"""
    cid = concept["id"]
    edges = graph["edges"]
    cmap = {c["id"]: c["name"] for c in graph["concepts"]}
    smap = {s["id"]: s["name"] for s in graph["subdomains"]}
    
    prereqs, deps, related = [], [], []
    for e in edges:
        if e["target_id"] == cid and e["relation_type"] == "prerequisite":
            prereqs.append(cmap.get(e["source_id"], ""))
        elif e["source_id"] == cid and e["relation_type"] == "prerequisite":
            deps.append(cmap.get(e["target_id"], ""))
        elif e["relation_type"] == "association":
            if e["source_id"] == cid: related.append(cmap.get(e["target_id"], ""))
            elif e["target_id"] == cid: related.append(cmap.get(e["source_id"], ""))
    
    return {
        "prerequisites": prereqs,
        "dependents": deps,
        "related": related,
        "subdomain_name": smap.get(concept["subdomain_id"], ""),
    }

def make_frontmatter(concept, subdomain_name):
    tags = concept.get("tags", [])
    return f"""---
id: "{concept['id']}"
name: "{concept['name']}"
subdomain: "{concept['subdomain_id']}"
subdomain_name: "{subdomain_name}"
difficulty: {concept['difficulty']}
is_milestone: {str(concept.get('is_milestone', False)).lower()}
tags: {json.dumps(tags, ensure_ascii=False)}
generated_at: "{time.strftime('%Y-%m-%dT%H:%M:%S')}"
---

# {concept['name']}

"""

def generate_doc(concept, graph):
    """为概念生成完整文档内容"""
    ctx = get_context(concept, graph)
    name = concept["name"]
    diff = concept["difficulty"]
    sub_name = ctx["subdomain_name"]
    prereqs = ctx["prerequisites"]
    deps = ctx["dependents"]
    related = ctx["related"]
    is_ms = concept.get("is_milestone", False)
    
    # Check if we have handwritten content in KNOWLEDGE_DB
    if concept["id"] in KNOWLEDGE_DB:
        return KNOWLEDGE_DB[concept["id"]]
    
    # Generate structured template document
    prereq_str = "、".join(prereqs) if prereqs else "无特定先修要求"
    dep_str = "、".join(deps) if deps else "（本概念为当前分支终端节点）"
    related_str = "、".join(related) if related else "无"
    
    milestone_note = "\n\n> 💡 **里程碑节点**：这是知识图谱中的关键节点，掌握它将解锁多个后续学习路径。" if is_ms else ""
    
    doc = f"""## 概述

{name}是{sub_name}领域中的{"核心" if diff >= 6 else "基础" if diff <= 3 else "重要"}概念，难度等级为 {diff}/9。{"它是知识图谱中的里程碑节点，标志着学习者在该领域达到了一个重要的能力阶段。" if is_ms else ""}

在知识体系中，{name}建立在{prereq_str}的基础之上{"，是通向" + dep_str + "等进阶概念的桥梁" if deps else ""}。掌握{name}对于深入理解{sub_name}的核心原理至关重要。{milestone_note}

## 核心概念

### 定义与本质

{name}的核心在于理解其基本定义、设计目标和解决的关键问题。作为{sub_name}领域难度{diff}/9的概念，学习者需要具备扎实的基础知识才能深入理解其内在原理。

### 关键特性

{name}具有以下关键特性，理解这些特性是掌握该概念的核心：

1. **基本原理**：{name}的设计和实现遵循特定的理论基础和工程实践
2. **应用场景**：在实际开发和研究中，{name}有广泛的应用价值
3. **演进趋势**：随着技术发展，{name}的实现方式和最佳实践在持续演进

### 与相关概念的区分

{name}需要与相关概念加以区分。{"它与" + related_str + "存在密切关联，但各有侧重。" if related else "理解其独特性有助于建立清晰的知识框架。"}

## 工作原理

{name}的底层工作原理涉及以下几个关键层面：

1. **理论基础**：基于{sub_name}领域的核心理论框架
2. **实现机制**：通过特定的算法、架构或协议来实现其功能
3. **执行流程**：在实际运行中，遵循特定的处理流程和数据流向

理解{name}的工作原理需要结合理论分析和实践验证。建议在学习过程中，通过动手实验来加深对机制的理解。

## 实际应用

### 应用场景一：工业实践

在实际的软件开发和技术实践中，{name}被广泛应用于解决相关领域的核心问题。

### 应用场景二：项目开发

在项目开发过程中，合理运用{name}可以显著提升代码质量、系统性能或开发效率。

### 工具与框架推荐

学习和实践{name}，推荐使用主流的开发工具和框架，结合官方文档和社区资源进行深入学习。

## 关联知识

- **先修概念**：{prereq_str}
  - 学习{name}之前，建议先掌握以上概念，确保基础扎实
- **后续概念**：{dep_str}
  - 掌握{name}后，可以继续深入学习以上进阶内容
- **相关概念**：{related_str if related else "无直接关联的平行概念"}
  - {"这些概念与" + name + "互为补充，建议并行学习" if related else ""}

## 常见误区

1. **概念混淆**：初学者容易将{name}与相近概念混淆，需要注意它们的本质区别
2. **应用过度简化**：在实际应用中，{name}的使用需要考虑具体场景的约束条件，不能生搬硬套
3. **忽视前置知识**：跳过先修概念直接学习{name}会导致理解不深入，建议按照知识图谱的推荐路径循序渐进

## 学习建议

- **推荐学习路径**：先回顾{prereq_str}相关知识，然后系统学习{name}的理论和实践
- **实践项目**：通过实际项目来巩固对{name}的理解，建议从小型练习开始逐步增加复杂度
- **推荐资源**：查阅{sub_name}领域的权威教材、官方文档和优质在线课程
- **预计学习时间**：根据难度等级（{diff}/9），预计需要 {max(4, diff * 3)}-{max(8, diff * 5)} 小时的深入学习
"""
    return doc


def build_index(graph):
    """构建索引文件"""
    subdomain_map = {s["id"]: s["name"] for s in graph["subdomains"]}
    index = {
        "version": "1.0",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "total_concepts": len(graph["concepts"]),
        "documents": [],
        "stats": {"by_subdomain": {}, "total_docs": 0, "total_chars": 0},
    }

    for concept in graph["concepts"]:
        filepath = RAG_DIR / concept["subdomain_id"] / f"{concept['id']}.md"
        char_count = filepath.stat().st_size if filepath.exists() else 0
        doc_entry = {
            "id": concept["id"],
            "name": concept["name"],
            "subdomain_id": concept["subdomain_id"],
            "subdomain_name": subdomain_map.get(concept["subdomain_id"], ""),
            "difficulty": concept["difficulty"],
            "is_milestone": concept.get("is_milestone", False),
            "tags": concept.get("tags", []),
            "file": f"{concept['subdomain_id']}/{concept['id']}.md",
            "exists": filepath.exists(),
            "char_count": char_count,
        }
        index["documents"].append(doc_entry)

        if filepath.exists():
            sub = concept["subdomain_id"]
            index["stats"]["by_subdomain"][sub] = index["stats"]["by_subdomain"].get(sub, 0) + 1
            index["stats"]["total_docs"] += 1
            index["stats"]["total_chars"] += char_count

    INDEX_FILE = RAG_DIR / "_index.json"
    INDEX_FILE.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n📑 索引已生成: {INDEX_FILE}")
    print(f"   总文档数: {index['stats']['total_docs']}/{index['total_concepts']}")
    print(f"   总字符数: {index['stats']['total_chars']:,}")
    for sub, count in sorted(index['stats']['by_subdomain'].items()):
        print(f"   {sub}: {count} docs")


def main():
    parser = argparse.ArgumentParser(description="本地 RAG 知识库文档批量生成")
    parser.add_argument("--subdomain", default=None, help="只生成指定子领域")
    parser.add_argument("--stats", action="store_true", help="只显示统计信息")
    parser.add_argument("--skip-existing", action="store_true", help="跳过已有的高质量文档")
    args = parser.parse_args()

    graph = load_seed_graph()
    concepts = graph["concepts"]
    subdomain_map = {s["id"]: s["name"] for s in graph["subdomains"]}

    if args.stats:
        build_index(graph)
        return

    if args.subdomain:
        concepts = [c for c in concepts if c["subdomain_id"] == args.subdomain]

    print(f"🚀 本地 RAG 知识库生成器")
    print(f"   待生成: {len(concepts)} 个概念")
    print(f"   输出目录: {RAG_DIR}\n")

    success = 0
    skipped = 0
    start = time.time()

    for i, concept in enumerate(concepts):
        filepath = RAG_DIR / concept["subdomain_id"] / f"{concept['id']}.md"
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Skip existing high-quality docs (>2000 chars)
        if args.skip_existing and filepath.exists() and filepath.stat().st_size > 2000:
            skipped += 1
            continue
        
        content = generate_doc(concept, graph)
        subdomain_name = subdomain_map.get(concept["subdomain_id"], "")
        full = make_frontmatter(concept, subdomain_name) + content
        filepath.write_text(full, encoding="utf-8")
        success += 1
        
        if (i + 1) % 20 == 0 or i == len(concepts) - 1:
            print(f"  📝 [{i+1}/{len(concepts)}] {concept['subdomain_id']}/{concept['name']}")

    elapsed = time.time() - start
    print(f"\n{'='*50}")
    print(f"✅ 完成! 耗时 {elapsed:.1f}s")
    print(f"   生成: {success}, 跳过: {skipped}")

    build_index(graph)


if __name__ == "__main__":
    main()
