---
id: "graph-rag"
concept: "Graph RAG"
domain: "ai-engineering"
subdomain: "rag-knowledge"
subdomain_name: "RAG与知识库"
difficulty: 7
is_milestone: false
tags: ["RAG"]

# Quality Metadata (Schema v2)
content_version: 1
quality_tier: "S"
quality_score: 99.9
generation_method: "hand-crafted"
unique_content_ratio: 1.0
last_scored: "2026-03-21"
sources: []
---
# Graph RAG

## 概述

Graph RAG 是一种将知识图谱结构与检索增强生成（RAG）相结合的高级架构，难度等级 7/9。与传统 RAG 仅依赖向量相似度检索不同，Graph RAG 利用实体之间的图结构关系和社区摘要来提供更全面、更连贯的回答，特别擅长处理需要跨多个文档片段综合推理的全局性问题。

本概念建立在 RAG Pipeline 和知识图谱基础之上，与 HyDE Retrieval、Reranking 等高级检索技术密切相关。

## 核心原理

### 传统 RAG 的局限

```
用户问题: "这个数据集中的主要主题是什么？"

传统 RAG 流程:
  问题 → 向量化 → 检索 top-k 片段 → 生成回答
                     ↑
            仅能找到局部相关片段
            无法回答需要全局视角的问题
```

传统 RAG 的核心问题：
1. **局部性**：向量检索只能找到与查询最相似的局部片段
2. **缺乏全局视角**：无法回答"总结整个数据集"类型的全局问题
3. **关系缺失**：平坦的文本片段丢失了实体之间的结构化关系

### Graph RAG 架构

```
┌─────────── 索引阶段 ───────────┐    ┌────── 查询阶段 ──────┐
│                                │    │                      │
│  文档 → 文本切片               │    │  用户问题             │
│    ↓                           │    │    ↓                  │
│  LLM 实体/关系抽取             │    │  判断: 局部 or 全局?  │
│    ↓                           │    │    ↓           ↓      │
│  构建知识图谱                  │    │  局部搜索    全局搜索  │
│    ↓                           │    │  (实体+邻居)  (社区摘要)│
│  社区检测(Leiden算法)          │    │    ↓           ↓      │
│    ↓                           │    │  Map-Reduce生成回答   │
│  每个社区生成摘要              │    │                      │
└────────────────────────────────┘    └──────────────────────┘
```

### 关键步骤详解

**1. 实体与关系抽取**

使用 LLM 从文本中自动提取实体和关系：

```python
# 示例：LLM 实体抽取的提示模板（伪代码）
prompt = """
从以下文本中提取所有实体和关系。
每个实体包含：名称、类型、描述
每个关系包含：源实体、目标实体、关系描述

文本: {text_chunk}
"""
# LLM 输出结构化的实体和关系 → 构建图谱
```

**2. 社区检测（Community Detection）**

使用 Leiden 算法将图谱中的节点聚类为"社区"：

```
完整知识图谱:
  A ── B ── C        D ── E
  │    │              │
  F ── G              H

Leiden 社区检测后:
  社区1: {A, B, C, F, G}  ← 紧密连接的实体群
  社区2: {D, E, H}        ← 另一组紧密连接的实体
```

Leiden 算法的优势：层次化社区（可配置不同粒度层级），每个层级对应不同的抽象程度。

**3. 社区摘要生成**

对每个社区用 LLM 生成描述性摘要：

```python
# 每个社区 → 一段自然语言摘要
community_summary = llm.summarize(
    entities=community.entities,
    relationships=community.relationships,
    # 摘要包含：主要实体、关键关系、总体主题
)
```

**4. 查询处理（Map-Reduce）**

```
全局查询流程:
  1. Map: 将问题发送给所有社区摘要 → 每个社区生成部分回答
  2. Reduce: 汇总所有部分回答 → 生成最终综合回答

局部查询流程:
  1. 识别问题相关的实体
  2. 检索这些实体的邻居节点和关系
  3. 结合上下文生成回答
```

## 与相关技术的对比

| 方法 | 检索方式 | 全局问题 | 结构化推理 | 索引成本 |
|:---|:---|:---|:---|:---|
| 传统 RAG | 向量相似度 | ❌ 弱 | ❌ | 低 |
| Knowledge Graph RAG | 图遍历 | ⚠️ 有限 | ✅ | 中 |
| **Graph RAG** | 社区摘要+图遍历 | ✅ 强 | ✅ | 高 |
| HyDE + RAG | 假设文档+向量 | ❌ | ❌ | 低 |

## 实际应用

### 典型场景

1. **文档集全局分析**：分析大型文档集的核心主题和趋势
2. **跨文档推理**：需要综合多个文档信息才能回答的复杂问题
3. **实体关系查询**：例如 "X 和 Y 之间有什么关系？"

### 使用 Microsoft GraphRAG 库

```python
# Microsoft GraphRAG 工具链（Python，概念示例）
# pip install graphrag

# 1. 准备输入文档
# input/  ← 放置文本文件

# 2. 初始化项目
# python -m graphrag.index --init --root .

# 3. 构建索引（实体抽取+社区检测+摘要生成）
# python -m graphrag.index --root .

# 4. 查询
# python -m graphrag.query --root . --method global \
#     --query "What are the main themes?"
```

注意：索引阶段会大量调用 LLM，成本较高（与文档量成正比）。

## 关联知识

- **前置知识**：RAG Pipeline（基础检索增强流程）、知识图谱（图结构基础）
- **相关概念**：HyDE Retrieval（另一种高级检索策略）、Reranking（后检索重排序）
- **进阶方向**：Agentic RAG（基于 Agent 的动态检索）、Multimodal RAG

## 常见误区

1. **误区：Graph RAG 适合所有场景** → 实际上对于简单的事实查询，传统 RAG 足够且成本更低
2. **误区：Graph RAG 只是把知识图谱和 RAG 拼在一起** → 核心创新是社区摘要机制和 Map-Reduce 全局查询策略
3. **误区：Graph RAG 不需要 LLM 就能工作** → 实体抽取、社区摘要、最终生成都依赖 LLM

## 学习建议

1. 先掌握传统 RAG Pipeline 的工作流程
2. 理解图论中社区检测的基本概念（不需要深入算法细节）
3. 阅读 Microsoft Graph RAG 论文了解设计动机
4. 动手运行 Microsoft graphrag 库的示例，观察索引产物
5. 比较传统 RAG 和 Graph RAG 在全局问题上的回答质量差异
