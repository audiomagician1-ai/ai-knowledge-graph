#!/usr/bin/env python3
"""Generate RAG docs for computer-graphics domain (250 concepts across 12 subdomains).

Run:  python data/scripts/generate_cg_rag.py
Output: data/rag/computer-graphics/
"""
import json
import pathlib
from datetime import date


def main():
    base = pathlib.Path(__file__).resolve().parent.parent
    seed_path = base / "seed" / "computer-graphics" / "seed_graph.json"
    rag_base = base / "rag" / "computer-graphics"

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
                "本概念是计算机图形学知识体系中的关键节点，"
                "掌握它将解锁更多高级渲染技术的学习路径。"
                "建议深入理解数学原理和GPU实现后再继续。\n"
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
            f"### 数学基础\n"
            f"- 理解{name}背后的数学原理（线性代数/微积分/概率论等）\n"
            f"- 掌握从数学公式到GPU实现的转化思路\n"
            f"- 了解数值精度和性能之间的权衡\n\n"
            f"### 渲染技术\n"
            f"- {name}在实时渲染管线中的位置与作用\n"
            f"- 相关Shader实现要点与优化技巧\n"
            f"- 在游戏引擎(UE5/Unity)中的实际应用案例\n\n"
            f"## 常见误区\n\n"
            f"1. **忽视硬件限制**: 脱离GPU架构特性设计算法，导致性能瓶颈\n"
            f"2. **过度追求物理正确**: 在实时渲染中不加取舍地使用离线渲染算法\n"
            f"3. **孤立学习**: 不理解{name}与渲染管线其他环节的协同关系\n"
            f"{ms_section}\n"
            f"## 学习建议\n\n"
            f"- 使用ShaderToy或RenderDoc等工具动手实验{name}效果\n"
            f"- 阅读GPU Gems/Real-Time Rendering等经典参考资料\n"
            f"- 在游戏引擎中观察和修改{name}的实际实现\n"
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
