---
id: "hyde-retrieval"
name: "HyDE Retrieval"
subdomain: "rag-knowledge"
subdomain_name: "RAG与知识库"
difficulty: 6
tags: ["RAG", "Retrieval", "Hypothetical Document"]
generated_at: "2026-03-19T12:00:00"
---

# HyDE Retrieval

## 概述

HyDE（Hypothetical Document Embeddings）是一种创新的检索增强策略，难度等级 6/9。其核心思想是：先让 LLM 根据用户问题生成一个"假设性回答文档"，然后用这个假设文档（而非原始问题）去做向量检索。这种方法利用了 LLM 的世界知识来弥合"问题语义空间"与"文档语义空间"之间的鸿沟。

本概念建立在文本嵌入和相似度搜索基础之上，与 Reranking、混合检索等高级 RAG 技术密切相关。

## 核心原理

### 为什么需要 HyDE？

```
传统检索的语义鸿沟:

  用户问题: "如何防止 SQL 注入？"
  ↓ 嵌入
  问题向量 → 搜索 → 可能匹配到: "SQL注入是一种常见的安全漏洞..."
                     但可能漏掉: "使用参数化查询可以有效防御..."

问题:
  - 问题的语义空间 ≠ 答案/文档的语义空间
  - 短问题的向量信息量远小于长文档
  - 关键词不匹配时检索效果下降
```

### HyDE 的工作流程

```
┌─────────────────────────────────────────────┐
│                 HyDE 流程                    │
│                                             │
│  1. 用户问题                                 │
│     "如何防止 SQL 注入？"                     │
│           ↓                                  │
│  2. LLM 生成假设文档                          │
│     "防止SQL注入的最佳实践包括：              │
│      使用参数化查询、输入验证、ORM框架..."     │
│           ↓                                  │
│  3. 对假设文档做向量嵌入                      │
│     hypothetical_doc → embedding             │
│           ↓                                  │
│  4. 用假设文档的向量检索真实文档库             │
│     embedding → vector_search → top_k docs   │
│           ↓                                  │
│  5. 用真实文档 + 原始问题生成最终回答         │
│     (question, real_docs) → LLM → answer     │
│                                             │
└─────────────────────────────────────────────┘
```

### 关键直觉

**假设文档的作用不是给出正确答案，而是生成一个与真实答案在语义空间中更接近的"锚点"。**

```
语义空间示意:

  [问题向量]        ............  [真实文档A]
       ↓                              ↑
  与文档距离较远           ←──→  距离很近
       ↓                              ↑
  [假设文档向量]  ←───── 距离较近 ─────→  [真实文档B]
```

即使假设文档包含事实错误，只要它在语义结构上与真实答案文档相似（使用相似的术语、句式、概念），就能提升检索效果。

## 代码示例

```python
# HyDE 检索的核心实现逻辑（Python 伪代码）
from openai import OpenAI

client = OpenAI()

def hyde_retrieve(question: str, vector_store, top_k: int = 5):
    """HyDE 检索流程"""

    # Step 1: 生成假设文档
    hypothesis = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": f"请写一段详细的文章来回答以下问题。"
                       f"不需要完全准确，重点是覆盖相关概念和术语。\n\n"
                       f"问题: {question}"
        }],
        max_tokens=300
    ).choices[0].message.content

    # Step 2: 用假设文档做嵌入
    hyp_embedding = get_embedding(hypothesis)

    # Step 3: 用假设文档的嵌入检索真实文档
    real_docs = vector_store.similarity_search(
        query_vector=hyp_embedding,
        top_k=top_k
    )

    # Step 4: 用真实文档生成最终回答
    context = "\n".join([doc.content for doc in real_docs])
    answer = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"根据以下资料回答问题:\n{context}"},
            {"role": "user", "content": question}
        ]
    ).choices[0].message.content

    return answer
```

## 与传统检索的对比

| 维度 | 传统向量检索 | HyDE | 说明 |
|:---|:---|:---|:---|
| 查询输入 | 原始问题 | LLM假设文档 | HyDE 输入更长、信息更丰富 |
| 语义匹配 | 问题↔文档 | 答案↔文档 | HyDE 缩小了语义鸿沟 |
| LLM 调用 | 仅生成阶段 | 检索+生成 | HyDE 多一次 LLM 调用 |
| 延迟 | 较低 | 较高（+生成假设文档耗时） | 可通过流式或缓存优化 |
| 短查询表现 | 弱 | 强 | HyDE 对简短模糊问题提升明显 |
| 精确关键词查询 | 强 | 可能弱 | LLM 可能"过度泛化"具体查询 |

## 适用与不适用场景

**适用：**
- 用户问题简短或模糊（如"怎么优化性能？"）
- 问题与文档之间存在词汇鸿沟（同一概念不同表述）
- 需要回答"如何做"类型的问题（答案文档风格与问题不同）

**不适用：**
- 精确关键词查询（如"Python 3.12 release notes"）
- 实时性要求极高的场景（额外 LLM 调用增加延迟）
- 文档库与问题领域高度匹配时（传统方法已足够好）

## 关联知识

- **前置知识**：文本嵌入（Text Embedding）、相似度搜索（Similarity Search）
- **相关概念**：Reranking（可与 HyDE 组合使用）、混合检索（Hybrid Search）
- **进阶方向**：Multi-Query RAG（生成多个查询变体）、Graph RAG

## 常见误区

1. **误区：假设文档必须准确** → 实际上 HyDE 要求的是语义相似而非事实准确，LLM 的"幻觉"在这里反而可能有帮助
2. **误区：HyDE 总是比传统检索好** → 对于精确匹配和特定查询，传统方法可能更优
3. **误区：HyDE 需要很强的 LLM** → 较小的模型也能生成有效的假设文档，关键是覆盖相关术语

## 学习建议

1. 先理解文本嵌入和向量检索的基本原理
2. 动手实现一个最简单的 HyDE 管线，比较它与传统检索的结果差异
3. 尝试不同的假设文档生成 prompt，观察检索结果变化
4. 在一个真实文档库上量化比较 recall 和 precision 指标
5. 思考 HyDE 与 Reranking 组合使用的可能性
