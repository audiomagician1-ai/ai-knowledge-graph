---
id: "rag-pipeline"
concept: "RAG管道架构"
domain: "ai-engineering"
subdomain: "rag-knowledge"
subdomain_name: "RAG与知识库"
difficulty: 7
is_milestone: false
tags: ["RAG", "架构"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# RAG管道架构

## 概述

RAG（Retrieval-Augmented Generation，检索增强生成）管道架构是一种将外部知识检索与大型语言模型生成能力相结合的系统设计范式。与纯参数化知识的LLM不同，RAG管道通过在推理时动态检索相关文档片段，将其注入到提示词上下文中，使模型能够基于最新、精确的外部信息生成回答。这一架构由Facebook AI Research于2020年在论文《Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks》中首次系统性提出，原始实现使用DPR（Dense Passage Retrieval）作为检索器，BART作为生成器。

RAG管道的工程价值在于它解决了LLM的两个核心局限：知识截止日期（knowledge cutoff）问题和幻觉（hallucination）问题。一个典型的生产级RAG系统将检索延迟控制在100-300ms以内，同时在专业领域问答任务上比纯LLM基线提升20-40%的准确率。区别于微调方案，RAG管道在知识更新时无需重新训练模型，仅需更新向量数据库中的文档索引即可。

## 核心原理

### 管道的四阶段执行流程

标准RAG管道由四个串行阶段构成：**索引（Indexing）→ 检索（Retrieval）→ 增强（Augmentation）→ 生成（Generation）**。索引阶段在离线完成，负责将原始文档经过分块、嵌入编码后存入向量数据库；后三个阶段在每次用户查询时在线执行。这四个阶段的职责严格分离，意味着可以独立优化各阶段而不影响其他模块——例如替换嵌入模型不需要修改生成器的提示词模板。

### 检索器与生成器的接口协议

RAG管道中检索器输出的Top-K文档块（通常K取3-10）通过一个固定格式的**上下文注入模板**传递给生成器。典型的提示词结构为：

```
System: 你是一个专业助手，请基于以下参考文档回答问题。
Context: [检索文档1] \n [检索文档2] \n ... [检索文档K]
Question: {用户问题}
Answer:
```

这个接口的关键约束是**上下文窗口限制**。GPT-4的128K token上下文看似充裕，但实验研究（Lost in the Middle, 2023）表明，当相关信息位于长上下文的中间位置时，模型的利用率会显著下降，呈现U形曲线。因此生产系统通常将每个文档块大小控制在512-1024 tokens，总注入上下文不超过4096 tokens。

### 朴素RAG与高级RAG的架构差异

**朴素RAG（Naive RAG）** 严格遵循单轮检索-生成流程：用户查询→向量检索→上下文拼接→LLM生成。其缺陷在于单次检索可能遗漏多跳推理所需的中间文档，且检索质量完全依赖原始查询的表达质量。

**高级RAG（Advanced RAG）** 在朴素管道基础上引入了三类增强机制：
- **预检索增强**：查询改写（Query Rewriting）、HyDE（假设文档嵌入）、查询分解（Sub-question Generation）
- **检索中增强**：混合检索（BM25稀疏检索+密集向量检索融合）、重排序器（Cross-Encoder Reranker）
- **后检索增强**：上下文压缩（Contextual Compression）、相关性过滤

**模块化RAG（Modular RAG）** 则将管道拆解为可组合的功能模块，支持迭代检索（Iterative Retrieval）和递归检索（Recursive Retrieval），适用于复杂多步推理场景。

### 向量数据库在管道中的角色

向量数据库是RAG管道的核心存储基础设施，承担文档嵌入的持久化存储和ANN（近似最近邻）搜索。主流选择包括Pinecone（托管服务）、Weaviate、Qdrant和Chroma（本地部署）。以Qdrant为例，其HNSW索引结构在百万级向量规模下可将检索延迟控制在10ms以内，召回率保持在0.95以上。管道设计时必须在索引构建时确定向量维度（如text-embedding-3-large为3072维），后续无法动态修改。

## 实际应用

**企业知识库问答系统**是RAG管道最典型的落地场景。以一个基于LangChain构建的法律文档问答系统为例：离线阶段将数千份合同PDF通过PyPDF解析、按512 token分块、使用OpenAI `text-embedding-ada-002`编码后存入Pinecone；在线阶段用户提问经过查询改写后检索Top-5文档块，经BGE-Reranker-v2重排后取Top-3注入GPT-4o生成答案。整个在线链路的P99延迟约2.5秒。

**代码辅助场景**中，RAG管道需要处理结构化代码的检索。GitHub Copilot的内部架构使用了基于代码语义的检索增强，将用户当前文件上下文、项目内相关代码片段一起注入。与文本RAG的差异在于代码分块必须遵循函数/类边界而非固定字符数，代码嵌入模型（如CodeBERT或UniXcoder）也与文本嵌入模型使用不同的预训练目标。

**实时数据增强场景**通过将RAG管道的检索源替换为搜索引擎API（如Bing Search API），可实现知识的实时更新。Perplexity AI的核心架构即是此类设计，其系统在生成最终答案前执行3-5次并行网页检索，每次检索结果经过相关性评分过滤后注入生成器。

## 常见误区

**误区一：将向量相似度等同于语义相关性**。许多工程师默认余弦相似度高的文档块就是最相关的检索结果，忽视了嵌入模型的局限性。实际上，`text-embedding-ada-002`在处理否定语义（如"不包含X"和"包含X"）时往往会给出相近的相似度得分，因为否定词在嵌入空间中的权重不足。解决方案是在向量检索后添加交叉编码器（Cross-Encoder）重排序层，Cross-Encoder直接对查询-文档对进行联合编码打分，相比双塔向量模型对语义细节的捕捉更精确。

**误区二：认为更大的K值必然带来更好的生成质量**。工程实践中有人设置K=20甚至更高，期望通过增加检索量来降低遗漏重要信息的风险。但这会导致两个具体问题：一是超出LLM有效利用的上下文长度引发"Lost in the Middle"问题；二是引入大量噪声文档，导致LLM在矛盾信息中产生混淆。斯坦福大学的研究表明，在大多数单跳问答任务中，K=3到K=5是准确率与噪声之间的帕累托最优点。

**误区三：将RAG管道视为静态的线性流水线**。初学者常将索引阶段视为一次性操作，忽视了生产环境中文档的动态更新需求。实际上，成熟的RAG系统需要设计增量索引机制：当新文档入库时，只对变更部分执行嵌入计算并更新向量数据库，而非全量重建索引。同时，生成阶段的输出也可以反馈到检索阶段（如Corrective RAG中的相关性评估步骤），形成带有反馈环路的非线性架构。

## 知识关联

RAG管道架构直接依赖**文档分块策略**（Chunking Strategy）作为索引阶段的输入准备。分块的粒度和方式（递归字符分割、语义分割或基于文档结构的父子分块）直接决定了检索阶段能够获取的信息完整性——块太小会截断语义，块太大会稀释相关信息的浓度，进而影响向量相似度计算的精度。

**相似度搜索与重排**是RAG管道检索阶段的核心实现，理解ANN算法（HNSW、IVF-Flat）和重排序模型（Cross-Encoder）的工作原理，是优化RAG管道检索质量的前提。这些技术在管道中共同构成检索增强的技术栈。

在掌握基础管道架构后，可以延伸至四个进阶方向：**RAG评估（Ragas）**提供了针对RAG管道各阶段的量化评估指标（Context Precision、Answer Faithfulness等）；**知识图谱+RAG**通过引入实体关系图谱增强结构化知识的检索；**多模态RAG**将管道扩展到图像、表格等非文本数据；**Agentic RAG**则赋予管道动态决策和迭代检索的能力，是当前RAG工程化的前沿方向。