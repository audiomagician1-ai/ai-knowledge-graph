#!/usr/bin/env python3
"""Generate RAG docs for software-engineering domain (280 concepts across 14 subdomains).

Run:  python data/scripts/generate_se_rag.py
Output: data/rag/software-engineering/
"""
import json
import pathlib
from datetime import date


def main():
    base = pathlib.Path(__file__).resolve().parent.parent
    seed_path = base / "seed" / "software-engineering" / "seed_graph.json"
    rag_base = base / "rag" / "software-engineering"

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
                "本概念是软件工程知识体系中的关键节点，"
                "掌握它将解锁更多高级工程实践的学习路径。"
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
            f"- 理解{name}的核心定义与在软件工程中的作用\n"
            f"- 掌握其适用场景与限制条件\n"
            f"- 了解在不同规模项目(个人/团队/大型)中的实践差异\n\n"
            f"### 工程实践\n"
            f"- 权衡分析：了解{name}方案的优缺点及替代方案\n"
            f"- 工具链：掌握相关开发工具和自动化支持\n"
            f"- 游戏行业：理解在游戏项目中的特殊约束与最佳实践\n\n"
            f"## 常见误区\n\n"
            f"1. **过度设计**: 在不需要的场景中引入复杂架构或模式，增加维护成本\n"
            f"2. **忽视权衡**: 只看到方案优势而忽略其代价和适用条件\n"
            f"3. **脱离实践**: 停留在理论知识而不在真实项目中应用和验证\n"
            f"{ms_section}\n"
            f"## 学习建议\n\n"
            f"- 在实际项目中应用{name}，通过代码实践加深理解\n"
            f"- 对比不同方案的利弊，培养工程权衡思维\n"
            f"- 阅读经典书籍和开源项目中的实际案例\n"
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
