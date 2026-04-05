---
id: "rag-overview"
concept: "RAG检索增强生成概述"
domain: "ai-engineering"
subdomain: "rag-knowledge"
subdomain_name: "RAG与知识库"
difficulty: 5
is_milestone: false
tags: ["RAG"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 95.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---



# RAG检索增强生成概述

## 概述

RAG（Retrieval-Augmented Generation，检索增强生成）是一种将信息检索系统与大型语言模型生成能力结合的AI架构范式。其核心机制是：在语言模型生成回答之前，先从外部知识库中检索出与用户问题相关的文档片段，再将这些片段拼接到提示词中，让模型基于检索到的上下文进行回答。这与纯粹依赖模型参数内存的"闭卷问答"方式形成根本区别。

RAG架构最早由Facebook AI Research（现Meta AI）的Lewis等人于2020年在论文《Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks》中正式提出。该论文将检索器（DPR，Dense Passage Retrieval）与生成器（BART）组合，在开放域问答任务上超越了纯参数化模型的表现。其背后的关键洞察是：大型语言模型的参数量虽然巨大（如GPT-3的1750亿参数），但其知识存储在训练截止日期之前，对于动态变化的专有领域知识存在结构性缺陷。

RAG的工程价值体现在三个可量化维度：一是减少模型幻觉，因为答案有明确的文档来源可以引用；二是无需微调即可更新知识，只需更新向量数据库中的文档；三是降低部署成本，相比为每个垂直领域微调一个模型，维护一个共享的检索索引更经济。

## 核心原理

### 检索-生成双阶段架构

RAG系统的基本流程由两个串联阶段构成。**检索阶段**：用户查询（Query）经过嵌入模型（如`text-embedding-ada-002`）转换为高维向量，在向量数据库（如FAISS、Pinecone）中通过近似最近邻搜索（ANN）找到语义最接近的Top-K文档片段，通常K取3到10之间。**生成阶段**：将检索到的文档片段以结构化格式插入提示词模板，例如：

```
上下文信息：
{retrieved_chunk_1}
{retrieved_chunk_2}

根据以上信息，回答问题：{user_query}
```

模型读取拼接后的完整提示词，生成基于证据的回答。这个"上下文窗口注入"机制是RAG区别于其他知识增强方法的核心操作。

### 朴素RAG与高级RAG的差异

最基础的朴素RAG（Naive RAG）仅包含索引→检索→生成三步，存在明显的召回率和精度问题。高级RAG（Advanced RAG）在此基础上引入查询改写（Query Rewriting）、混合检索（Hybrid Search = 稠密向量检索 + BM25稀疏检索）、重排序（Reranking，使用cross-encoder模型对初步检索结果重新打分）等模块。模块化RAG（Modular RAG）进一步将各阶段抽象为可替换组件，允许根据任务动态选择检索策略。这三代架构的演进路径直接对应了企业级RAG系统的工程复杂度。

### 上下文窗口与知识密度的权衡

RAG系统的一个核心参数约束是大语言模型的上下文窗口长度。GPT-4 Turbo支持128K tokens，但将所有相关文档直接塞入并不是最优策略——研究表明，当相关信息位于超长上下文的中间位置时，模型的提取能力显著下降（"lost in the middle"问题，Liu et al., 2023）。因此，实践中通常将单次检索注入的上下文控制在1500到4000 tokens之间，这直接决定了文档分块大小的选择策略：chunk_size通常设为256到1024个token，且需要50到150 token的重叠（overlap）以避免跨块信息丢失。

### 相似度度量与检索质量

检索阶段的相似度计算通常使用余弦相似度（Cosine Similarity）而非欧氏距离，公式为：

$$\text{sim}(q, d) = \frac{\vec{q} \cdot \vec{d}}{|\vec{q}||\vec{d}|}$$

其中 $\vec{q}$ 是查询向量，$\vec{d}$ 是文档片段向量。余弦相似度的取值范围为[-1, 1]，对向量的绝对长度不敏感，更适合文本嵌入场景。检索质量通常用Recall@K（K个返回结果中包含正确答案的比例）和MRR（Mean Reciprocal Rank）来评估，这两个指标独立于生成质量，方便分模块调试。

## 实际应用

**企业知识库问答**是RAG最典型的落地场景。某金融机构将数千份内部合规文件（PDF格式）解析后存入向量数据库，员工提问"2024年版反洗钱操作规程第三章的要求"时，系统检索出对应文档片段，模型生成带有页码引用的结构化回答，同时支持审计追踪。这类场景要求RAG系统必须处理PDF解析噪声、表格理解等工程问题。

**代码库智能搜索**是另一高价值场景。GitHub Copilot的部分功能使用了RAG思路：将代码仓库的函数签名和注释向量化，用户描述需求时检索最相关的代码片段作为上下文，引导模型生成符合项目风格的代码。此场景中chunk的边界通常与代码的函数或类结构对齐，而非固定token数截断。

**医疗领域**中，RAG被用于将最新的临床指南（如2024年WHO诊疗规范）接入通用模型，避免模型使用过时的医学知识。由于该场景对幻觉零容忍，通常要求系统在回答中附加原文引用，并设置置信度阈值，低于阈值时拒绝回答。

## 常见误区

**误区一：RAG等同于"把文档喂给ChatGPT"。** 直接将整篇文档粘贴到提示词与RAG系统有本质区别。RAG通过向量索引实现亚秒级的语义检索，支持百万量级的文档库；而直接粘贴受限于单次上下文窗口（最多数十万tokens），且无法跨多个会话复用知识库。RAG的索引构建阶段（包括文档解析、分块、向量化）是独立于推理阶段的离线工程流程。

**误区二：更大的K值（检索数量）总是更好。** 增大K值确实提高了召回率，但同时引入了更多噪声文档，导致模型在生成时被无关信息干扰，实测中K=10往往比K=20的端到端答案质量更高。研究显示，最优K值与问题类型强相关：事实性问题（factoid QA）K=3~5已足够，而需要综合多源信息的分析型问题可能需要K=8~15。

**误区三：RAG可以完全替代模型微调。** RAG解决的是知识外挂问题，但无法改变模型的推理风格、输出格式偏好和领域术语理解。对于需要模型持续以特定行业语气、特定JSON格式输出的场景，RAG+LoRA微调的组合方案比单独使用RAG的效果提升约15~30%（基于多个垂直领域基准测试的经验数据）。

## 知识关联

RAG系统的检索阶段依赖**文本嵌入（Embedding）**技术将文本转化为向量，嵌入模型的质量直接决定检索的语义准确性，这是RAG工程的第一个深入方向。**文档分块策略**决定了向量数据库中的最小检索单元，chunk的大小和边界选择对RAG效果的影响通常超过模型本身的差异。在数据接入层，**文档解析（PDF/HTML/OCR）**解决的是将非结构化原始文件转化为可索引文本的工程问题，是RAG系统中最容易积累技术债的环节。在框架层，**LangChain**提供了`RetrievalQA`和`ConversationalRetrievalChain`等封装好的RAG链式组件，**LlamaIndex**则以`VectorStoreIndex`为核心提供了更细粒度的文档索引控制接口，两个框架都将本文描述的RAG架构抽象为可配置的流水线，是工程实践的主要入口。