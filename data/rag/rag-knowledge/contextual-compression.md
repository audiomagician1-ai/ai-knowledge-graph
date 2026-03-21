---
id: "contextual-compression"
concept: "上下文压缩"
domain: "ai-engineering"
subdomain: "rag-knowledge"
subdomain_name: "RAG与知识库"
difficulty: 6
is_milestone: false
tags: ["RAG"]

# Quality Metadata (Schema v2)
content_version: 1
quality_tier: "A"
quality_score: 60.3
generation_method: "ai-batch-v1"
unique_content_ratio: 1.0
last_scored: "2026-03-21"
sources: []
---
# 上下文压缩

## 核心概念

上下文压缩（Contextual Compression）是在RAG检索后、送入LLM前，对检索到的文档片段进行精炼和压缩的技术。目的是去除与查询无关的信息，保留最相关的内容，从而提高LLM回答质量并减少token消耗。

## 为什么需要压缩

传统RAG检索返回固定大小的文档块，存在问题：
1. **信噪比低**: 检索的chunk中包含大量与查询无关的内容
2. **上下文窗口有限**: LLM能处理的token数有上限
3. **注意力稀释**: 无关内容分散LLM的注意力
4. **成本浪费**: 多余token增加API调用费用

## 压缩方法

### 1. 提取式压缩（Extractive）
从原文中提取相关句子/段落：
- 使用嵌入模型计算句子与查询的相似度
- 保留相似度高于阈值的句子
- 保持原文表述，不改变语义

### 2. 生成式压缩（Abstractive）
使用LLM对原文进行摘要/改写：
- 针对查询生成定向摘要
- 可以综合多个文档片段
- 更灵活但可能引入幻觉

### 3. 过滤式压缩（Filtering）
直接丢弃不相关的文档：
- 使用交叉编码器（Cross-Encoder）评估相关性
- 低于阈值的整个chunk被过滤
- 最简单但粒度最粗

### 4. 重排序+截断（Rerank + Truncate）
对检索结果重新排序后只保留top-K：
- 使用Reranker模型精确排序
- 截取前N个最相关的片段
- 兼顾质量和效率

## LangChain中的实现

LangChain提供了`ContextualCompressionRetriever`：
- 包装任意基础检索器
- 可配置不同的压缩器（LLM压缩器/嵌入过滤器/交叉编码器过滤器）
- 在检索和生成之间插入压缩步骤

## 压缩的权衡

| 方面 | 轻度压缩 | 重度压缩 |
|------|---------|---------|
| 信息保留 | 高 | 低 |
| Token节省 | 少 | 多 |
| 延迟增加 | 少 | 多（需要额外LLM调用） |
| 幻觉风险 | 低 | 高（生成式） |

## 与Chunking Strategies的关系

上下文压缩是分块策略（Chunking）的下游优化。分块决定了初始检索的粒度，压缩则在检索后进一步精炼内容。二者配合使用效果最佳。
