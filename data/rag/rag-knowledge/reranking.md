---
id: "reranking"
name: "Reranking"
subdomain: "rag-knowledge"
subdomain_name: "RAG与知识库"
difficulty: 6
tags: ["RAG", "Retrieval", "Cross-Encoder"]
generated_at: "2026-03-19T12:00:00"
---

# Reranking

## 概述

Reranking（重排序）是 RAG 管线中位于初始检索之后的精排阶段，难度等级 6/9。初始检索（如向量相似度搜索或 BM25）速度快但精度有限，Reranking 使用更强的模型（通常是 Cross-Encoder）对候选文档重新打分排序，显著提升最终送入 LLM 的上下文质量。这是一种"先粗筛、后精排"的两阶段检索策略。

本概念建立在相似度搜索和 RAG Pipeline 基础之上，与 HyDE Retrieval、混合检索等技术互补配合。

## 核心原理

### 两阶段检索架构

```
┌──────────── 阶段1: 粗排（Retrieval）──────────────┐
│                                                    │
│  查询 → Bi-Encoder 向量化 → 近似最近邻搜索        │
│         (独立编码 query 和 doc)                     │
│                   ↓                                │
│         候选文档集 top-100（速度快, 精度中等）       │
│                                                    │
└────────────────────────────────────────────────────┘
                    ↓
┌──────────── 阶段2: 精排（Reranking）──────────────┐
│                                                    │
│  (query, doc) → Cross-Encoder → 相关性分数         │
│  (联合编码 query 和 doc, 注意力交叉)               │
│                   ↓                                │
│         重排序后 top-5（精度高, 速度较慢）          │
│                                                    │
└────────────────────────────────────────────────────┘
                    ↓
              送入 LLM 生成回答
```

### Bi-Encoder vs Cross-Encoder

```
Bi-Encoder (粗排用):
  query  → Encoder → query_vec  ─┐
                                  ├→ cosine_similarity(q, d)
  doc    → Encoder → doc_vec   ─┘
  
  ✅ 优点: doc可以预计算向量, 检索极快 (毫秒级)
  ❌ 缺点: query和doc独立编码, 交互信息弱

Cross-Encoder (精排用):
  [query, doc] → Encoder → relevance_score
  
  ✅ 优点: query和doc联合编码, 深层语义交互, 精度高
  ❌ 缺点: 每对(query, doc)都需要前向传播, 不能预计算, 速度慢
```

**关键区别**：Bi-Encoder 把 query 和 doc 分别编码为独立向量再做相似度计算，而 Cross-Encoder 将 query 和 doc 拼接后一起输入模型，让 Transformer 的 attention 机制在两者之间进行深度交互。

### 为什么不直接用 Cross-Encoder？

```
假设文档库有 100 万篇文档:

Bi-Encoder: 
  预计算 100万 doc向量 (一次性)
  查询时: 1次 query编码 + ANN搜索 → ~10ms

Cross-Encoder: 
  查询时: 100万次 (query, doc) 前向传播 → 数小时 ❌

两阶段策略:
  Bi-Encoder 粗排 top-100 → ~10ms
  Cross-Encoder 精排 100篇  → ~100ms
  总计: ~110ms ✅
```

## 代码示例

```python
# 使用 sentence-transformers 实现 Reranking（Python）
from sentence_transformers import CrossEncoder

# 加载 Cross-Encoder 模型
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

# 假设已通过粗排获得候选文档
query = "如何防止 SQL 注入攻击？"
candidate_docs = [
    "SQL注入是一种常见的Web安全漏洞...",
    "参数化查询是防止SQL注入的最佳实践...",
    "数据库索引可以提升查询性能...",
    "使用ORM框架可以自动处理SQL转义...",
]

# Cross-Encoder 对 (query, doc) 对打分
pairs = [(query, doc) for doc in candidate_docs]
scores = reranker.predict(pairs)

# 按分数降序排列
ranked = sorted(zip(scores, candidate_docs), reverse=True)
for score, doc in ranked:
    print(f"  [{score:.3f}] {doc[:50]}...")

# 输出 (示意):
#   [0.95] 参数化查询是防止SQL注入的最佳实践...
#   [0.87] SQL注入是一种常见的Web安全漏洞...
#   [0.72] 使用ORM框架可以自动处理SQL转义...
#   [0.12] 数据库索引可以提升查询性能...     ← 被正确降权
```

### 在 RAG 管线中集成 Reranking

```python
# RAG + Reranking 集成示例（Python 伪代码）
def rag_with_reranking(query: str, top_k_retrieve: int = 20, top_k_rerank: int = 5):
    # 阶段1: 粗排 — 向量检索 top-k 候选
    candidates = vector_store.similarity_search(query, top_k=top_k_retrieve)

    # 阶段2: 精排 — Cross-Encoder 重排序
    pairs = [(query, doc.content) for doc in candidates]
    scores = reranker.predict(pairs)

    # 取重排后的 top-k
    ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    top_docs = [candidates[i] for i in ranked_indices[:top_k_rerank]]

    # 阶段3: 用精排后的文档生成回答
    context = "\n".join([doc.content for doc in top_docs])
    answer = llm.generate(query=query, context=context)
    return answer
```

## 常用 Reranking 模型

| 模型 | 来源 | 特点 |
|:---|:---|:---|
| ms-marco-MiniLM | sentence-transformers | 轻量级，适合低延迟场景 |
| bge-reranker-v2 | BAAI | 中英双语表现优异 |
| Cohere Rerank | Cohere API | 闭源API，开箱即用 |
| jina-reranker-v2 | Jina AI | 多语言长文档支持 |
| RankGPT | 学术 | 用 LLM 做 listwise reranking |

## Reranking 的不同策略

1. **Pointwise**：对每个 (query, doc) 独立打分（Cross-Encoder，最常用）
2. **Pairwise**：比较两个文档哪个更相关
3. **Listwise**：一次考虑整个候选列表排序（如 RankGPT，用 LLM 直接排序）

## 关联知识

- **前置知识**：相似度搜索（Similarity Search）、RAG Pipeline
- **相关概念**：HyDE Retrieval（可先 HyDE 再 Rerank）、混合检索（Hybrid Search）
- **进阶方向**：Graph RAG、Agentic RAG

## 常见误区

1. **误区：Reranking 只是简单的重新排序** → Cross-Encoder 使用深层语义交互，不仅仅是换个排序标准，而是完全不同的相关性建模方式
2. **误区：粗排检索数量越多越好** → 候选过多会增加 Reranking 延迟，通常 20-100 篇是合理范围
3. **误区：Reranking 可以弥补糟糕的粗排** → 如果粗排完全没有检索到相关文档，Reranking 也无能为力（"garbage in, garbage out"）
4. **误区：所有 Reranking 模型都是 Cross-Encoder** → Listwise 方法（如 RankGPT）使用 LLM 排序，不是传统 Cross-Encoder

## 学习建议

1. 先理解 Bi-Encoder 和 Cross-Encoder 的区别及各自的适用场景
2. 使用 sentence-transformers 库动手实验 Cross-Encoder 打分
3. 在一个 RAG 管线中对比"有 Reranking"和"无 Reranking"的回答质量
4. 尝试不同的 top-k 粗排数量，观察对精排结果的影响
5. 了解 Cohere Rerank API 等商业方案的使用方式
