"""
RAG 知识库文档批量生成器
用途：为种子图谱中的每个概念生成高质量参考文档（Markdown + YAML frontmatter）
特性：
  - 断点续传：已生成的文件自动跳过
  - 并发控制：可配置并发数，避免 API 限流
  - 质量保证：结构化 prompt + 后验检查
  - 进度追踪：实时显示进度和预估剩余时间

用法：
  python data/scripts/generate_rag_docs.py --provider deepseek --api-key sk-xxx
  python data/scripts/generate_rag_docs.py --provider openai --api-key sk-xxx --model gpt-4o
  python data/scripts/generate_rag_docs.py --provider openrouter --api-key sk-xxx
  python data/scripts/generate_rag_docs.py --resume  # 断点续传（跳过已有文件）
"""

import argparse
import asyncio
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Optional

try:
    import httpx
except ImportError:
    print("需要安装 httpx: pip install httpx")
    sys.exit(1)

# ── 路径 ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SEED_GRAPH = PROJECT_ROOT / "data" / "seed" / "programming" / "seed_graph.json"
RAG_DIR = PROJECT_ROOT / "data" / "rag"
INDEX_FILE = RAG_DIR / "_index.json"

# ── Provider 配置 ──────────────────────────────────────
PROVIDERS = {
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1",
        "default_model": "deepseek-chat",
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o-mini",
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "default_model": "deepseek/deepseek-chat",
    },
}

# ── 文档生成 Prompt ──────────────────────────────────────
SYSTEM_PROMPT = """你是一个资深技术教育内容专家。你的任务是为一个 AI 学习平台的 RAG（检索增强生成）知识库编写高质量的参考文档。

## 写作标准

### 目标读者
- 有一定编程基础，正在系统学习计算机科学和 AI 的开发者
- 需要从"是什么"到"怎么用"的完整认知链路

### 质量要求
1. **准确性**: 技术细节必须准确，引用权威来源（论文/官方文档/经典教材）
2. **深度适中**: 超越入门科普但不深入到论文级别，目标是"让人真正理解"
3. **实用性**: 包含真实场景、代码片段（如适用）、最佳实践
4. **时效性**: 涉及 AI/LLM 领域时，反映 2024-2025 年最新进展
5. **关联性**: 明确说明与先修/后续概念的关系

### 格式规范（严格遵守）
输出**纯 Markdown 正文**（不要输出 YAML frontmatter，系统会自动添加）。

文档结构（每个 h2 标题为一个知识块）：

## 概述
简明定义 + 为什么重要 + 在知识体系中的位置（2-3段）

## 核心概念
分点讲解核心要素，每个要点 2-4 句话。使用 ### 三级标题分组

## 工作原理
底层机制 / 算法流程 / 架构设计（视概念性质而定）。可用流程描述、伪代码、公式

## 实际应用
- 2-3个真实应用场景
- 代码示例（如适用，用 ```语言 包裹）
- 框架/工具推荐

## 关联知识
- **先修概念**: 学这个之前需要掌握什么
- **后续概念**: 学完这个可以继续学什么
- **易混淆概念**: 与哪些概念容易混淆，区别是什么

## 常见误区
列出 2-3 个学习者常犯的错误或误解

## 学习建议
- 推荐的学习路径和资源
- 练手项目建议
- 预计学习时间

### 字数要求
- 总字数：1500-3000 字（中文）
- 不要水字数，每句话都要有信息量
"""

USER_PROMPT_TEMPLATE = """请为以下概念编写 RAG 知识库文档：

**概念名称**: {name}
**所属领域**: {domain} > {subdomain}
**难度等级**: {difficulty}/9（1=入门，9=专家）
**是否里程碑节点**: {is_milestone}

**图谱上下文**:
- 先修概念: {prerequisites}
- 后续概念: {dependents}
- 关联概念: {related}

请严格按照系统提示的格式输出。"""


def load_seed_graph():
    """加载种子图谱"""
    with open(SEED_GRAPH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_concept_context(concept, graph):
    """获取概念的图谱上下文（先修、后续、关联）"""
    cid = concept["id"]
    edges = graph["edges"]
    concepts_map = {c["id"]: c["name"] for c in graph["concepts"]}
    subdomain_map = {s["id"]: s["name"] for s in graph["subdomains"]}

    prerequisites = []
    dependents = []
    related = []

    for e in edges:
        if e["target"] == cid and e["type"] == "prerequisite":
            prerequisites.append(concepts_map.get(e["source"], e["source"]))
        elif e["source"] == cid and e["type"] == "prerequisite":
            dependents.append(concepts_map.get(e["target"], e["target"]))
        elif e["type"] == "association":
            if e["source"] == cid:
                related.append(concepts_map.get(e["target"], e["target"]))
            elif e["target"] == cid:
                related.append(concepts_map.get(e["source"], e["source"]))

    subdomain_name = subdomain_map.get(concept["subdomain_id"], concept["subdomain_id"])

    return {
        "name": concept["name"],
        "domain": graph["domain"]["name"],
        "subdomain": subdomain_name,
        "difficulty": concept["difficulty"],
        "is_milestone": "是 ⭐" if concept.get("is_milestone") else "否",
        "prerequisites": "、".join(prerequisites) if prerequisites else "无",
        "dependents": "、".join(dependents) if dependents else "无",
        "related": "、".join(related) if related else "无",
    }


def concept_to_filename(concept):
    """概念名转文件名"""
    name = concept["id"]  # id 已经是 kebab-case
    subdomain = concept["subdomain_id"]
    return f"{subdomain}/{name}.md"


def make_frontmatter(concept, subdomain_name):
    """生成 YAML frontmatter"""
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


async def generate_doc(
    client: httpx.AsyncClient,
    concept: dict,
    graph: dict,
    provider_config: dict,
    model: str,
    api_key: str,
    semaphore: asyncio.Semaphore,
) -> tuple[str, Optional[str], Optional[str]]:
    """生成单个概念的文档，返回 (concept_id, content, error)"""
    ctx = get_concept_context(concept, graph)
    user_prompt = USER_PROMPT_TEMPLATE.format(**ctx)

    async with semaphore:
        for attempt in range(3):
            try:
                resp = await client.post(
                    f"{provider_config['base_url']}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": user_prompt},
                        ],
                        "temperature": 0.3,
                        "max_tokens": 4096,
                    },
                    timeout=120.0,
                )
                resp.raise_for_status()
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                return (concept["id"], content, None)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    wait = (attempt + 1) * 10
                    print(f"  ⚠ 429 Rate limit on {concept['name']}, wait {wait}s...")
                    await asyncio.sleep(wait)
                else:
                    return (concept["id"], None, f"HTTP {e.response.status_code}: {e.response.text[:200]}")
            except (httpx.ConnectError, httpx.ReadTimeout) as e:
                wait = (attempt + 1) * 5
                print(f"  ⚠ Network error on {concept['name']}: {e}, retry in {wait}s...")
                await asyncio.sleep(wait)
            except Exception as e:
                return (concept["id"], None, f"{type(e).__name__}: {str(e)[:200]}")

        return (concept["id"], None, "Max retries exceeded")


def validate_doc(content: str) -> list[str]:
    """验证文档质量，返回问题列表"""
    issues = []
    if len(content) < 500:
        issues.append(f"内容过短: {len(content)} 字")
    if "## 概述" not in content and "## 核心概念" not in content:
        issues.append("缺少标准章节结构")
    if content.count("##") < 3:
        issues.append(f"章节数不足: 仅 {content.count('##')} 个")
    return issues


async def main():
    parser = argparse.ArgumentParser(description="RAG 知识库文档批量生成器")
    parser.add_argument("--provider", default="deepseek", choices=PROVIDERS.keys())
    parser.add_argument("--api-key", required=True, help="LLM API Key")
    parser.add_argument("--model", default=None, help="Override model name")
    parser.add_argument("--concurrency", type=int, default=5, help="并发数 (default: 5)")
    parser.add_argument("--resume", action="store_true", help="跳过已生成的文件")
    parser.add_argument("--subdomain", default=None, help="只生成指定子领域")
    parser.add_argument("--dry-run", action="store_true", help="只显示计划，不实际生成")

    args = parser.parse_args()
    provider_config = PROVIDERS[args.provider]
    model = args.model or provider_config["default_model"]

    print(f"🚀 RAG 知识库生成器")
    print(f"   Provider: {args.provider} | Model: {model}")
    print(f"   并发数: {args.concurrency}")
    print(f"   输出目录: {RAG_DIR}")
    print()

    # 加载种子图谱
    graph = load_seed_graph()
    concepts = graph["concepts"]
    subdomain_map = {s["id"]: s["name"] for s in graph["subdomains"]}

    if args.subdomain:
        concepts = [c for c in concepts if c["subdomain_id"] == args.subdomain]
        print(f"   过滤子领域: {args.subdomain} → {len(concepts)} 个概念")

    # 断点续传：检查已有文件
    to_generate = []
    skipped = 0
    for c in concepts:
        filepath = RAG_DIR / concept_to_filename(c)
        if args.resume and filepath.exists() and filepath.stat().st_size > 100:
            skipped += 1
        else:
            to_generate.append(c)

    print(f"📊 总计 {len(concepts)} 个概念，跳过 {skipped} 个已有，待生成 {len(to_generate)} 个")
    print()

    if args.dry_run:
        for c in to_generate:
            print(f"  📝 {c['subdomain_id']}/{c['name']} (难度 {c['difficulty']})")
        print(f"\n  共 {len(to_generate)} 个文件待生成")
        return

    if not to_generate:
        print("✅ 所有文档已生成！")
        return

    # 创建子目录
    for sub_id in set(c["subdomain_id"] for c in to_generate):
        (RAG_DIR / sub_id).mkdir(parents=True, exist_ok=True)

    # 批量生成
    semaphore = asyncio.Semaphore(args.concurrency)
    success_count = 0
    error_count = 0
    errors = []
    start_time = time.time()

    async with httpx.AsyncClient() as client:
        tasks = [
            generate_doc(client, c, graph, provider_config, model, args.api_key, semaphore)
            for c in to_generate
        ]

        for i, coro in enumerate(asyncio.as_completed(tasks)):
            concept_id, content, error = await coro
            concept = next(c for c in to_generate if c["id"] == concept_id)
            filepath = RAG_DIR / concept_to_filename(concept)

            elapsed = time.time() - start_time
            rate = (i + 1) / elapsed if elapsed > 0 else 0
            remaining = (len(to_generate) - i - 1) / rate if rate > 0 else 0

            if error:
                error_count += 1
                errors.append((concept["name"], error))
                print(f"  ❌ [{i+1}/{len(to_generate)}] {concept['name']}: {error}")
            else:
                # 验证
                issues = validate_doc(content)
                if issues:
                    print(f"  ⚠️ [{i+1}/{len(to_generate)}] {concept['name']}: {', '.join(issues)}")

                # 添加 frontmatter 并写入
                subdomain_name = subdomain_map.get(concept["subdomain_id"], "")
                full_content = make_frontmatter(concept, subdomain_name) + content
                filepath.write_text(full_content, encoding="utf-8")
                success_count += 1
                print(f"  ✅ [{i+1}/{len(to_generate)}] {concept['name']} ({len(content)} 字) [ETA: {remaining:.0f}s]")

    # 生成索引
    print("\n📑 生成索引文件...")
    build_index(graph)

    elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"🏁 完成！耗时 {elapsed:.0f}s")
    print(f"   ✅ 成功: {success_count}")
    print(f"   ❌ 失败: {error_count}")
    if errors:
        print(f"\n失败列表:")
        for name, err in errors:
            print(f"   - {name}: {err}")


def build_index(graph=None):
    """构建 RAG 文档索引"""
    if graph is None:
        graph = load_seed_graph()

    subdomain_map = {s["id"]: s["name"] for s in graph["subdomains"]}
    index = {
        "version": "1.0",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "total_concepts": len(graph["concepts"]),
        "documents": [],
        "stats": {"by_subdomain": {}, "total_docs": 0, "total_chars": 0},
    }

    for concept in graph["concepts"]:
        filepath = RAG_DIR / concept_to_filename(concept)
        doc_entry = {
            "id": concept["id"],
            "name": concept["name"],
            "subdomain_id": concept["subdomain_id"],
            "subdomain_name": subdomain_map.get(concept["subdomain_id"], ""),
            "difficulty": concept["difficulty"],
            "is_milestone": concept.get("is_milestone", False),
            "tags": concept.get("tags", []),
            "file": concept_to_filename(concept),
            "exists": filepath.exists(),
            "char_count": filepath.stat().st_size if filepath.exists() else 0,
        }
        index["documents"].append(doc_entry)

        if filepath.exists():
            sub = concept["subdomain_id"]
            index["stats"]["by_subdomain"][sub] = index["stats"]["by_subdomain"].get(sub, 0) + 1
            index["stats"]["total_docs"] += 1
            index["stats"]["total_chars"] += doc_entry["char_count"]

    INDEX_FILE.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"   索引已写入: {INDEX_FILE}")
    print(f"   文档数: {index['stats']['total_docs']}/{index['total_concepts']}")


if __name__ == "__main__":
    asyncio.run(main())
