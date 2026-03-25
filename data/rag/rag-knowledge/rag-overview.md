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
quality_tier: "B"
quality_score: 44.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.412
last_scored: "2026-03-22"
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

RAG（Retrieval-Augmented Generation，检索增强生成）是一种将**外部知识检索**与**大语言模型生成**相结合的架构范式。其核心思路是：在模型生成回答之前，先从外部知识库中检索出与问题相关的文档片段，将这些片段作为上下文（Context）拼接进提示词，再让语言模型基于这些检索结果生成最终答案。这一设计使得模型无需将所有知识压缩到参数中，也能准确回答特定领域或时效性强的问题。

RAG的概念由Facebook AI Research（现Meta AI）于2020年在论文《Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks》（Lewis等人，发表于NeurIPS 2020）中正式提出。原始论文使用了一个可训练的密集检索器（DPR，Dense Passage Retriever）配合BART生成模型，在开放域问答任务（如Natural Questions和TriviaQA）上取得了比纯参数化模型更优的结果。此后RAG迅速成为大语言模型落地应用的主流工程范式。

RAG解决的根本问题是**知识截止日期（Knowledge Cutoff）**和**幻觉（Hallucination）**两大痛点。GPT-4、Claude等大模型的训练数据均有固定的截止时间，对2023年后发生的事件一无所知；而RAG通过检索实时更新的知识库，允许模型引用原文，使得回答可溯源、可验证，从而大幅降低模型凭空捏造事实的概率。

---

## 核心原理

### 三阶段流水线：索引、检索、生成

RAG系统的运行分为三个明确阶段：

1. **索引阶段（Indexing）**：将原始文档（PDF、网页、数据库记录等）切分为固定大小的文本块（Chunk），通过嵌入模型（Embedding Model）将每个Chunk转化为高维向量，存入向量数据库（如Faiss、Pinecone、Chroma、Weaviate）。此阶段在查询发生前离线完成。

2. **检索阶段（Retrieval）**：用户提交查询（Query）后，系统用同一嵌入模型将Query转化为向量，在向量数据库中计算余弦相似度（Cosine Similarity）或内积，取出Top-K（通常K=3~10）最相关的文本块。

3. **生成阶段（Generation）**：将检索到的K个文本块与用户原始问题拼接为结构化提示词，传入语言模型（如GPT-4、Llama 3、Mistral等），由模型综合上下文生成最终回答。

整体公式可表达为：

$$P(y \mid x) = \sum_{z \in \text{Top-K}(p(z|x))} P(z \mid x) \cdot P(y \mid x, z)$$

其中 $x$ 为用户查询，$z$ 为检索到的文档片段，$y$ 为生成的答案。

### 稀疏检索 vs 密集检索

RAG系统中有两类主要检索方法，选择直接影响检索质量：

- **稀疏检索（Sparse Retrieval）**：基于词频统计，代表算法为BM25（Best Match 25）。BM25通过计算词项频率（TF）与逆文档频率（IDF）的加权得分匹配文档，速度极快，对精确词语匹配效果好，但无法理解语义同义词。
- **密集检索（Dense Retrieval）**：基于向量相似度，使用如`text-embedding-ada-002`（OpenAI）、`bge-large-zh`（北京智源）等嵌入模型生成语义向量。能捕捉"汽车"与"轿车"的语义关联，但计算成本高于BM25。
- **混合检索（Hybrid Retrieval）**：将BM25结果与向量检索结果通过RRF（Reciprocal Rank Fusion）算法融合，取两者之长，是当前生产环境的推荐方案。

### 上下文窗口与Chunk大小的关系

RAG的实际效果与Chunk大小紧密相关。若Chunk过小（如50 tokens），单个片段语义不完整，模型难以理解；若Chunk过大（如2000 tokens），一次检索能放入上下文的片段数量减少，且相关信息被大量噪声稀释。实践中常用512 tokens或256 tokens作为Chunk的基准大小，并使用约10%~20%的重叠（Overlap）避免语义在边界处断裂。GPT-4的128K上下文窗口虽然可容纳大量文本，但研究表明（"Lost in the Middle"，Liu等人，2023）模型对位于上下文**中间部分**的信息提取能力显著弱于头部和尾部，因此即使上下文窗口很大，RAG的精准检索仍有不可替代的价值。

---

## 实际应用

**企业知识库问答（Enterprise QA）**：将公司内部的产品手册、合规文件、会议记录等上传至RAG系统。员工提问"Q3季度的退货政策是什么？"时，系统从文档中检索出对应条款，模型生成带引用来源的精确回答，而非依赖模型训练时可能学到的过时信息。

**代码库智能助手**：将代码仓库中的函数注释、README和API文档向量化后，开发者询问"如何调用订单处理模块的退款接口？"，RAG系统可检索出具体函数签名和使用示例，比直接让LLM生成代码更准确可靠。

**医疗与法律领域问答**：在需要高精度引用来源的场景中，RAG允许模型回答"根据《药典》第×版第×条……"，输出结果附有原文溯源，满足合规审计需求。这种可溯源性是纯生成模型无法原生提供的能力。

**实时数据增强**：将新闻API、股票数据、天气服务的返回值作为临时"文档"注入RAG流水线，使模型具备回答"今天上证指数涨跌幅"等实时问题的能力，突破训练数据截止限制。

---

## 常见误区

**误区一：RAG只是把文档粘贴进提示词**

许多初学者认为RAG就是将全部文档塞入系统提示（System Prompt），这是"长上下文填充"而非RAG。真正的RAG核心在于**语义检索步骤**——只有与当前查询最相关的片段才被选入上下文，而非全量文档。缺少检索步骤的方案无法扩展到超过模型上下文窗口的知识库规模（企业文档库动辄数百万tokens），也无法保证相关性。

**误区二：向量相似度高就等于检索结果正确**

余弦相似度度量的是语义接近程度，而非事实正确性。查询"苹果公司的CEO是谁？"可能检索到一篇高度相似但描述苹果公司历史的文章，其中包含过时信息（如"乔布斯是CEO"）。向量相似度≥0.9不代表该片段能正确回答问题，还需要通过**重排序（Reranking）**模型（如Cohere Rerank、BGE-Reranker）对检索结果做二次精排。

**误区三：RAG可以完全消除LLM幻觉**

RAG显著降低但无法消灭幻觉。当检索结果本身存在错误、相互矛盾，或模型在生成时未能忠实引用上下文（而是混入训练知识）时，幻觉依然会发生。2023年的多项评测（如RAGAS框架的Faithfulness指标）显示，即使在RAG场景下，GPT-4的上下文忠实度也并非100%，需要额外的答案验证机制。

---

## 知识关联

**前置知识衔接**：RAG的生成阶段直接依赖**GPT与解码器模型**的自回归生成机制——理解Transformer解码器如何按token逐步生成文本，有助于理解为何检索到的上下文必须被格式化为提示词而非以其他方式传入。**提示词基础**则决定了如何将检索结果与用户问题拼接为有效指令（如使用"基于以下资料回答问题……"的结构化模板），提示词的质量直接影响模型能否正确引用检索内容。

**后续深化方向**：学完本概述后，**文本嵌入（Embedding）**将详述不同嵌入模型的维度、训练方式及选型标准，这是RAG检索质量的底层基础；**文档分块策略**聚焦Chunk大小、重叠率、递归分割等具体工程决策；**文档解析（PDF/HTML/OCR）**解决原始文档的格式化提取问题；**LangChain基础**和**LlamaIndex基础**则提供了将上述所有组件组装为完整RAG流水线的工程框架。