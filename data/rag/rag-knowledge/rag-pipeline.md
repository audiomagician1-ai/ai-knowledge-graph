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
quality_tier: "pending-rescore"
quality_score: 41.7
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.382
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# RAG管道架构

## 概述

RAG（检索增强生成，Retrieval-Augmented Generation）管道架构是一种将外部知识检索与大型语言模型生成能力相结合的系统工程框架。与纯粹依赖模型参数中内嵌知识的方式不同，RAG管道通过实时查询向量数据库或文档存储，将检索到的上下文片段注入到LLM的提示词中，使模型能够回答训练数据截止日期之后的问题或处理私有知识库内容。

RAG的概念由Meta AI研究团队在2020年的论文《Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks》（Lewis等人）中正式提出，原始实验在Open-Domain QA任务上将准确率提升了约11个百分点。从那时起，RAG管道从简单的"检索-生成"二元结构演化为包含预处理、多路检索、重排、融合和生成五个独立阶段的复杂系统。

RAG管道架构的价值在于它解决了LLM的两个根本性缺陷：知识静态性（模型权重一旦训练完成便固定）和幻觉问题（模型在无关联证据时仍会生成看似合理的错误内容）。通过将可溯源的文档片段绑定到每次生成请求，RAG使得答案可审计、可更新、可追溯到具体来源。

---

## 核心原理

### 1. 管道的五阶段串行结构

标准RAG管道由以下五个阶段顺序执行：

**索引阶段（Indexing）**：离线完成，将原始文档经过分块策略（如递归字符分块，chunk size通常设置为256~1024 tokens）转换为向量嵌入，存储至向量数据库（如Chroma、Weaviate、Pinecone）。每个向量同时附带原始文本和元数据（文档来源、章节、时间戳）。

**查询处理阶段（Query Processing）**：在线阶段的起点。用户查询经过同一嵌入模型（必须与索引时使用的模型一致，否则向量空间不对齐）转为查询向量。此阶段可选加入查询扩展（Query Expansion）或HyDE（Hypothetical Document Embeddings）技术，通过让LLM先生成一个假设性答案来改善稀疏查询的检索效果。

**检索阶段（Retrieval）**：向量数据库执行近似最近邻（ANN）搜索，返回top-k个文档片段（k通常为5~20）。现代RAG管道多采用混合检索，将密集向量检索（如cosine相似度）与稀疏关键词检索（BM25算法，公式：`Score(D,Q) = Σ IDF(qi) · (f(qi,D)·(k1+1)) / (f(qi,D)+k1·(1-b+b·|D|/avgdl))`）通过RRF（Reciprocal Rank Fusion）算法合并排名。

**重排阶段（Reranking）**：使用Cross-Encoder模型（如`cross-encoder/ms-marco-MiniLM-L-6-v2`）对检索到的候选片段与查询进行细粒度相关性打分，将top-k结果精简为top-3或top-5后传入生成阶段。Cross-Encoder比Bi-Encoder精度更高但计算更慢，因此只用于重排而非初始检索。

**生成阶段（Generation）**：将重排后的文档片段拼接到提示词模板中，构造包含系统指令、检索上下文和用户问题的完整提示，发送至LLM生成最终回答。提示模板通常包含"仅基于以下上下文回答"的约束指令，以减少模型引入参数知识导致的幻觉。

### 2. 上下文窗口的物理约束与管理

RAG管道的生成阶段受到LLM上下文窗口的硬性限制。以GPT-4 Turbo的128K token窗口为例，若每个文档片段平均400 tokens，理论上可容纳约320个片段，但实验表明"迷失在中间"（Lost in the Middle）现象会导致模型忽略位于上下文中部的信息——2023年刘等人的研究显示，将关键文档放在上下文首部或尾部时，准确率比放置中部高出约20%。因此，RAG管道在组装上下文时需要对文档片段排序，将最相关片段放置在提示首部。

### 3. 朴素RAG与高级RAG的架构差异

朴素RAG（Naive RAG）仅执行"单轮检索-单次生成"，适合简单问答场景，端到端延迟通常在500ms~2s之间。高级RAG（Advanced RAG）引入迭代检索机制：当生成阶段识别到"证据不足"信号时，触发第二轮甚至第三轮检索，此模式延迟可达5~15s但显著提升复杂推理问题的准确率。模块化RAG（Modular RAG）则将各阶段解耦为可插拔组件，允许针对特定场景替换检索器或重排器，是目前生产系统中最主流的架构形式。

---

## 实际应用

**企业知识库问答系统**：某金融机构将内部合规文档（约50万页PDF）构建为RAG管道，使用`text-embedding-ada-002`（1536维）嵌入模型索引，BM25+向量混合检索配合Cohere Rerank重排器，将合规查询的答案准确率从GPT-4直接生成的61%提升至87%，同时使每次回答可溯源到具体条款编号。

**代码助手场景**：GitHub Copilot的知识库增强版本中，RAG管道针对代码仓库构建了双索引：一个基于代码语义嵌入（使用专用代码嵌入模型如`code-search-babbage`），另一个基于函数签名的精确匹配索引。两路检索结果通过加权融合（语义检索权重0.7，精确匹配权重0.3）后进入生成阶段，使代码补全对私有API的引用准确率提升约35%。

**医疗问答系统**：在临床决策支持场景中，RAG管道通常配置chunk overlap为20%（即相邻片段重叠约50~100 tokens），以防止关键诊断信息被分块边界截断。检索阶段还增加元数据过滤层，限制仅检索特定疾病分类或特定年份的临床指南，从而降低过时医疗信息进入上下文的风险。

---

## 常见误区

**误区一：嵌入模型可以任意更换而无需重建索引**
许多工程师误以为向量索引可以独立于嵌入模型存在。实际上，向量空间与生成它的嵌入模型深度绑定——`text-embedding-ada-002`生成的1536维向量与`bge-large-en-v1.5`生成的1024维向量位于完全不同的几何空间中，用不同模型生成的查询向量去搜索原模型建立的索引，cosine相似度计算结果无任何语义意义。更换嵌入模型必须删除并重建全量索引。

**误区二：检索到的片段越多，生成质量越高**
增大top-k值并非总能改善答案质量。当k从5增大到20时，检索召回率提升，但同时引入了更多噪声片段。噪声片段会稀释核心证据在上下文中的占比，导致LLM产生"证据混淆"现象，实验中常观察到k=20时的答案F1分数低于k=5的情况。最优k值需通过具体数据集上的评估实验确定，而非凭直觉设置越大越好。

**误区三：RAG管道可以完全消除幻觉**
RAG减少了知识性幻觉（factual hallucination），但无法消除推理性幻觉（reasoning hallucination）。当检索到的片段包含矛盾信息，或问题需要跨多个片段进行多步推理时，LLM仍会生成错误结论。2023年的RAGAS评估框架研究显示，即使在检索精度达90%的系统中，生成阶段的忠实度（Faithfulness）得分平均仍只有0.76，说明约24%的生成内容包含与检索上下文不完全一致的表述。

---

## 知识关联

RAG管道架构建立在**文档分块策略**之上：索引阶段的分块决策（固定大小分块、递归分块、语义分块）直接决定了进入检索阶段的信息单元粒度，粒度过粗导致检索片段包含冗余信息，粒度过细导致单个片段语义不完整。同时，**相似度搜索与重排**是RAG管道检索阶段和重排阶段的技术基础，向量空间距离度量和Cross-Encoder的工作机制在RAG管道中被具体实例化为完整的数据流。

在RAG管道架构掌握之后，**RAG评估（Ragas）**框架提供了针对管道各阶段的量化指标体系，包括Context Precision、Context Recall、Faithfulness和Answer Relevancy四项核心指标，用于诊断管道中的具体瓶颈。**知识图谱+RAG**在管道的检索阶段引入图结构遍历，解决实体关系推理场景下纯向量检索的局限性。**多模态RAG**将管道的索引和检索阶段扩展至图像、音频等非文本模态。**Agentic RAG**则将RAG管道中的检索步骤转变为由Agent动态
