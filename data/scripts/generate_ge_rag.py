#!/usr/bin/env python3
"""Generate RAG docs for game-engine domain (300 concepts across 15 subdomains)."""
import json
import pathlib
from datetime import date


def main():
    base = pathlib.Path(__file__).resolve().parent.parent
    seed_path = base / "seed" / "game-engine" / "seed_graph.json"
    rag_base = base / "rag" / "game-engine"

    with open(seed_path, "r", encoding="utf-8") as f:
        seed = json.load(f)

    concepts = seed["concepts"]
    subdomains = {s["id"]: s["name"] for s in seed["subdomains"]}
    domain_id = seed["domain"]["id"]
    domain_name = seed["domain"]["name"]

    # Create subdomain dirs
    for sid in subdomains:
        (rag_base / sid).mkdir(parents=True, exist_ok=True)

    docs_index = []
    stats_by_sub = {}

    for c in concepts:
        sid = c["subdomain_id"]
        sub_name = subdomains[sid]
        is_ms = c.get("is_milestone", False)
        diff = c["difficulty"]
        name = c["name"]
        desc = c["description"]
        tags = c.get("tags", [])

        ms_section = ""
        if is_ms:
            ms_section = (
                "\n## 里程碑意义\n\n"
                "本概念是游戏引擎知识体系中的关键节点，"
                "掌握它将解锁更多高级引擎技术的学习路径。"
                "建议深入理解后再继续。\n"
            )

        content = (
            f"---\n"
            f"concept: {name}\n"
            f"subdomain: {sub_name}\n"
            f"domain: {domain_id}\n"
            f"difficulty: {diff}\n"
            f"---\n\n"
            f"# {name}\n\n"
            f"## 核心内容\n\n"
            f"{desc}\n\n"
            f"## 关键要点\n\n"
            f"### 基本原理\n"
            f"- 理解{name}的核心定义与在游戏引擎中的作用\n"
            f"- 掌握其与其他引擎子系统的关联关系\n"
            f"- 了解UE5和Unity中的具体实现差异与设计取舍\n\n"
            f"### 工程实践\n"
            f"- 性能影响：了解{name}的CPU/GPU/内存开销及优化策略\n"
            f"- 调试方法：掌握引擎Profiler和调试工具的使用\n"
            f"- 版本兼容：注意不同引擎版本中的API变化\n\n"
            f"## 常见误区\n\n"
            f"1. **只会调API不懂原理**: 仅停留在蓝图/编辑器层面，不理解底层算法与数据结构\n"
            f"2. **忽视性能代价**: 添加功能时不评估帧时间影响，导致运行时性能问题\n"
            f"3. **孤立看待子系统**: 不考虑与其他子系统的数据流和依赖关系\n"
            f"{ms_section}\n"
            f"## 学习建议\n\n"
            f"- 在引擎中动手实践{name}的核心功能并用Profiler验证性能影响\n"
            f"- 对比UE5和Unity对{name}的不同实现，理解设计取舍\n"
            f"- 阅读引擎源码或官方文档，深入理解{name}的底层机制\n"
        )

        file_rel = f"{domain_id}/{sid}/{c['id']}.md"
        file_path = rag_base / sid / f"{c['id']}.md"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        char_count = len(content)

        if sid not in stats_by_sub:
            stats_by_sub[sid] = {"count": 0, "chars": 0}
        stats_by_sub[sid]["count"] += 1
        stats_by_sub[sid]["chars"] += char_count

        docs_index.append(
            {
                "id": c["id"],
                "name": name,
                "domain_id": domain_id,
                "subdomain_id": sid,
                "subdomain_name": sub_name,
                "difficulty": diff,
                "is_milestone": is_ms,
                "tags": tags,
                "file": file_rel,
                "exists": True,
                "char_count": char_count,
            }
        )

    total_chars = sum(s["chars"] for s in stats_by_sub.values())
    total_docs = sum(s["count"] for s in stats_by_sub.values())

    index = {
        "version": "1.0.0",
        "domain": domain_id,
        "domain_name": domain_name,
        "generated_at": str(date.today()),
        "total_concepts": total_docs,
        "stats": {
            "total_docs": total_docs,
            "total_chars": total_chars,
            "by_subdomain": stats_by_sub,
        },
        "documents": docs_index,
    }

    with open(rag_base / "_index.json", "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f"Generated {total_docs} docs, {total_chars} total chars")
    print(f"Subdomains: {len(stats_by_sub)}")
    for sid, st in sorted(stats_by_sub.items()):
        print(f"  {sid}: {st['count']} docs, {st['chars']} chars")


if __name__ == "__main__":
    main()
