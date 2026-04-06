"""Sync 6 new systems-theory family domains: create RAG stubs + Workers data."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DOMAINS = [
    "systems-theory", "cybernetics", "information-theory",
    "dissipative-structures", "synergetics", "catastrophe-theory",
]

def main():
    total_docs = 0
    for d in DOMAINS:
        seed_path = os.path.join(ROOT, "data", "seed", d, "seed_graph.json")
        with open(seed_path, "r", encoding="utf-8") as f:
            seed = json.load(f)

        concepts = seed["concepts"]
        domain_name = seed.get("domain_name", d)

        # Group by subdomain
        subdomains: dict[str, list] = {}
        for c in concepts:
            sd = c.get("subdomain_id", "core")
            subdomains.setdefault(sd, []).append(c)

        index_docs = []
        for sd_id, sd_concepts in subdomains.items():
            sd_dir = os.path.join(ROOT, "data", "rag", d, sd_id)
            os.makedirs(sd_dir, exist_ok=True)

            for c in sd_concepts:
                cid = c["id"]
                cname = c.get("name", cid)
                doc_path = os.path.join(sd_dir, f"{cid}.md")
                content = (
                    f"# {cname}\n\n"
                    f"## 核心知识点\n\n"
                    f"{cname} 是 {domain_name} 领域的重要概念。\n\n"
                    f"### 定义与概述\n\n"
                    f"{cname} 涉及该领域的基础理论和实践应用。\n\n"
                    f"### 关键要素\n\n"
                    f"1. **基本原理**: {cname} 的核心原理和机制\n"
                    f"2. **应用场景**: 在实际问题中的应用\n"
                    f"3. **与其他概念的关系**: 与相关概念的联系\n\n"
                    f"### 学习要点\n\n"
                    f"- 理解 {cname} 的定义和核心思想\n"
                    f"- 掌握其在实际场景中的应用方法\n"
                    f"- 了解与其他知识点的关联关系\n"
                )
                with open(doc_path, "w", encoding="utf-8") as f:
                    f.write(content)

                index_docs.append({
                    "concept_id": cid,
                    "concept_name": cname,
                    "subdomain_id": sd_id,
                    "file": f"{sd_id}/{cid}.md",
                    "score": 65,
                })

        # Write _index.json for data/rag
        index_obj = {
            "domain": d,
            "total_docs": len(index_docs),
            "documents": index_docs,
        }
        idx_path = os.path.join(ROOT, "data", "rag", d, "_index.json")
        with open(idx_path, "w", encoding="utf-8") as f:
            json.dump(index_obj, f, ensure_ascii=False, indent=2)

        # Copy to workers/data/rag
        w_rag_dir = os.path.join(ROOT, "workers", "data", "rag", d)
        os.makedirs(w_rag_dir, exist_ok=True)
        w_idx = os.path.join(w_rag_dir, "_index.json")
        with open(w_idx, "w", encoding="utf-8") as f:
            json.dump(index_obj, f, ensure_ascii=False, indent=2)

        total_docs += len(index_docs)
        print(f"  {d}: {len(index_docs)} RAG docs + _index.json")

    print(f"\nTotal: {total_docs} new RAG docs across {len(DOMAINS)} domains")


if __name__ == "__main__":
    main()
