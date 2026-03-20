#!/usr/bin/env python3
"""Generate RAG docs for level-design domain (200 concepts across 10 subdomains)."""
import json
import pathlib
from datetime import date


def main():
    base = pathlib.Path(__file__).resolve().parent.parent
    seed_path = base / "seed" / "level-design" / "seed_graph.json"
    rag_base = base / "rag" / "level-design"

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
                "\n## \u91cc\u7a0b\u7891\u610f\u4e49\n\n"
                "\u672c\u6982\u5ff5\u662f\u5173\u5361\u8bbe\u8ba1\u77e5\u8bc6\u4f53\u7cfb\u4e2d\u7684\u5173\u952e\u8282\u70b9\uff0c"
                "\u638c\u63e1\u5b83\u5c06\u89e3\u9501\u66f4\u591a\u9ad8\u7ea7\u8bbe\u8ba1\u6982\u5ff5\u7684\u5b66\u4e60\u8def\u5f84\u3002"
                "\u5efa\u8bae\u6df1\u5165\u7406\u89e3\u540e\u518d\u7ee7\u7eed\u3002\n"
            )

        content = (
            f"---\n"
            f"concept: {name}\n"
            f"subdomain: {sub_name}\n"
            f"domain: {domain_id}\n"
            f"difficulty: {diff}\n"
            f"---\n\n"
            f"# {name}\n\n"
            f"## \u6838\u5fc3\u5185\u5bb9\n\n"
            f"{desc}\n\n"
            f"## \u5173\u952e\u8981\u70b9\n\n"
            f"### \u57fa\u672c\u539f\u7406\n"
            f"- \u7406\u89e3{name}\u7684\u6838\u5fc3\u5b9a\u4e49\u4e0e\u5728\u5173\u5361\u8bbe\u8ba1\u4e2d\u7684\u4f5c\u7528\n"
            f"- \u638c\u63e1\u5176\u4e0e\u5176\u4ed6\u5173\u5361\u8bbe\u8ba1\u5b50\u7cfb\u7edf\u7684\u5173\u8054\u5173\u7cfb\n"
            f"- \u4e86\u89e3\u5b9e\u9645\u9879\u76ee\u4e2d\u7684\u5e94\u7528\u573a\u666f\u4e0e\u9650\u5236\u6761\u4ef6\n\n"
            f"### \u8bbe\u8ba1\u539f\u5219\n"
            f"- \u670d\u52a1\u4e8e\u73a9\u5bb6\u4f53\u9a8c\uff1a\u5173\u5361\u8bbe\u8ba1\u7684\u6bcf\u4e2a\u51b3\u7b56\u90fd\u5e94\u589e\u5f3a\u6c89\u6d78\u611f\u4e0e\u53ef\u73a9\u6027\n"
            f"- \u7a7a\u95f4\u53ef\u8bfb\u6027\uff1a\u73a9\u5bb6\u80fd\u76f4\u89c9\u7406\u89e3\u7a7a\u95f4\u5e03\u5c40\u4e0e\u5f15\u5bfc\u610f\u56fe\n"
            f"- \u53ef\u8fed\u4ee3\uff1a\u4fdd\u6301\u7070\u76d2\u9636\u6bb5\u7684\u5feb\u901f\u9a8c\u8bc1\u80fd\u529b\uff0c\u4fbf\u4e8e\u53cd\u9988\u9a71\u52a8\u4f18\u5316\n\n"
            f"## \u5e38\u89c1\u8bef\u533a\n\n"
            f"1. **\u8fc7\u5ea6\u590d\u6742\u5316**: \u5806\u780c\u7ec6\u8282\u4e0d\u7b49\u4e8e\u4f18\u8d28\u5173\u5361\uff0c\u6e05\u6670\u7684\u7a7a\u95f4\u8bed\u8a00\u6bd4\u534e\u4e3d\u88c5\u9970\u66f4\u91cd\u8981\n"
            f"2. **\u5ffd\u89c6\u5ea6\u91cf\u6807\u51c6**: \u4e0d\u53c2\u8003\u89d2\u8272\u79fb\u52a8\u53c2\u6570\u8fdb\u884c\u7a7a\u95f4\u8bbe\u8ba1\uff0c\u5bfc\u81f4\u5c3a\u5ea6\u5931\u771f\n"
            f"3. **\u8131\u79bb\u6574\u4f53\u8282\u594f**: \u5355\u72ec\u6253\u78e8\u5c40\u90e8\u533a\u57df\u800c\u5ffd\u7565\u6574\u4f53\u8282\u594f\u66f2\u7ebf\u7684\u5e73\u8861\n"
            f"{ms_section}\n"
            f"## \u5b66\u4e60\u5efa\u8bae\n\n"
            f"- \u5728\u5df2\u6709\u6e38\u620f\u4e2d\u5206\u6790{name}\u7684\u5177\u4f53\u5b9e\u73b0\u4e0e\u6548\u679c\n"
            f"- \u5c1d\u8bd5\u7528\u7b80\u77ed\u8bed\u8a00\u5411\u975e\u4ece\u4e1a\u8005\u89e3\u91ca{name}\u7684\u4ef7\u503c\n"
            f"- \u5728\u5f15\u64ce\u4e2d\u642d\u5efa\u7b80\u5355\u539f\u578b\u9a8c\u8bc1\u4f60\u5bf9{name}\u7684\u7406\u89e3\n"
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
