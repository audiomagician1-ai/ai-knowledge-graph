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
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---


# Graph RAG

## 概述

Graph RAG（图检索增强生成）是微软研究院于2024年提出的一种将知识图谱与RAG技术深度融合的架构，其核心论文《From Local to Global: A Graph RAG Approach to Query-Focused Summarization》发表后迅速引发业界广泛关注。与传统向量检索RAG不同，Graph RAG不是在文本块向量空间中搜索相似片段，而是先从原始语料中自动抽取实体与关系，构建知识图谱，再通过图社区算法对节点进行层级聚类，生成多粒度的社区摘要，最终利用这些摘要回答查询。

Graph RAG的设计动机来自于传统RAG在"全局性问题"上的根本性缺陷。当用户提问"这份企业年报中最主要的风险主题是什么？"时，答案散布于整个文档的每一处，没有任何单一文本块能单独回答它。Graph RAG通过社区摘要将整个语料库的宏观结构压缩进可检索的层级摘要，使得大规模语料的全局推理成为可能，这是其区别于Naive RAG和HyDE等方案的根本所在。

## 核心原理

### 索引阶段：从文本到图谱

Graph RAG的索引管道分为五个明确步骤。第一步，使用LLM对切分后的文本块逐一进行实体与关系抽取，每个文本块默认调用`gleanings`机制（最多执行N次追问）以降低LLM漏提实体的概率，微软官方实现中默认`gleanings=1`。第二步，对跨文本块提及同一实体的节点执行合并（entity resolution），通过余弦相似度或LLM判断决定是否将"苹果公司"与"Apple Inc."合并为同一节点。第三步，为每个节点生成自然语言描述摘要，将该节点出现的所有上下文浓缩为一段文字，存储于图节点属性中。

### 社区检测：Leiden算法的使用

Graph RAG选择Leiden算法（而非简单的Louvain算法）对知识图谱进行社区划分，原因在于Leiden算法能保证每个社区内部的强连通性，避免Louvain算法产生"断裂社区"的问题。算法执行后产生多个层级（Level 0最细粒度、Level N最粗粒度），每个层级的社区都会被单独送入LLM生成社区摘要（Community Report），摘要包含该社区的关键实体、关键关系、潜在主题与重要发现。一个典型的中等规模语料库（约百万词级别）在Level 1层级可能产生数百个社区报告。

### 查询阶段：Local与Global两种模式

Graph RAG提供两种截然不同的查询模式，对应不同的应用场景：

**Global Search模式**：用于回答需要理解整个语料库的宏观问题。系统将所有相关层级的社区报告进行Map-Reduce式处理——先让LLM对每份社区报告独立打分并提取与查询相关的要点（Map阶段），再将所有要点汇总让LLM综合生成最终答案（Reduce阶段）。该模式的token消耗远高于传统RAG，成本是其主要限制。

**Local Search模式**：用于回答针对特定实体或关系的具体问题。系统从向量数据库中检索与查询最相关的实体节点，然后沿图的邻居关系扩展上下文，同时混入相关的文本块、实体摘要与社区报告，最终拼接成增强提示词。这一过程结合了向量检索与图遍历两种机制。

### 存储结构

Graph RAG的存储层需要同时维护四类数据：（1）原始文本块及其向量嵌入（向量数据库）；（2）实体节点及其摘要（图数据库或Parquet文件）；（3）关系边及权重（图数据库）；（4）社区报告及其层级归属（结构化存储）。微软官方实现`graphrag`库默认使用本地Parquet文件存储图结构，可配置为Azure AI Search或Neo4j。

## 实际应用

**学术文献分析**：将数百篇医学论文导入Graph RAG后，系统可自动构建"疾病-药物-靶点-副作用"知识图谱，社区检测会自然将"心血管疾病研究社区"与"肿瘤免疫疗法社区"分离，研究者可直接查询"当前治疗耐药性的主流机制是什么"这类全局问题，这在传统分块检索中几乎不可能获得高质量答案。

**企业知识管理**：将公司内部文档（合同、会议纪要、技术文档）构建为知识图谱后，Graph RAG的Local Search模式可以在回答"张总和李工在Q3项目中有哪些决策分歧"时，自动将两个人名节点的邻居（相关会议纪要片段、项目决策节点）一并纳入上下文，比单纯关键词检索精准得多。

**法律合规审查**：针对监管文件库，Global Search模式能够跨越数百个文件生成"当前法规对数据跨境传输的整体要求"的综合性摘要，而非仅返回某几条法规条文。

## 常见误区

**误区一：Graph RAG等于"用图数据库替换向量数据库"**。事实上Graph RAG的图并非用来做向量检索的替代品，其图结构的核心价值在于支撑社区检测与多跳关系推理。即使在官方实现中，Local Search模式依然保留了向量检索步骤来定位种子实体，图与向量是互补而非替代关系。

**误区二：Graph RAG在所有场景下都优于传统RAG**。微软原论文的评测数据显示，Global Search在"comprehensiveness"（全面性）和"diversity"（多样性）两个维度上显著优于Naive RAG，但在单点事实查询（如"某条约的签署日期"）上，传统向量RAG的延迟更低、成本更小，效果相当。Graph RAG的优势域是全局摘要型查询，而非所有查询类型。

**误区三：索引阶段只需运行一次即可永久使用**。当源文档频繁更新时，图中实体合并与社区检测需要增量重建，实体描述摘要也需要重新生成，这涉及大量LLM调用。微软官方文档明确指出增量索引（incremental indexing）在2024年版本中仍属实验性功能，不建议在高频更新场景下直接使用。

## 知识关联

Graph RAG以**知识图谱+RAG**为直接前置基础——学习者需要已经理解实体关系抽取、图嵌入与传统向量RAG的管道结构，才能理解Graph RAG索引阶段为何需要两个独立存储层。**RAG管道架构**中的分块策略、检索召回率与上下文窗口管理等概念在Graph RAG中均有对应的演化版本：传统RAG的文本块在Graph RAG中升级为携带图结构上下文的增强块，检索步骤从单一向量检索变为向量检索+图遍历的混合策略。

Leiden社区检测算法是Graph RAG架构中的关键图算法组件，其参数`resolution`控制社区粒度（值越大社区越小越细），直接决定社区报告的数量与覆盖深度，调整这一参数是Graph RAG工程落地中最重要的超参数调优步骤之一。理解这一算法的收敛机制有助于解释为什么同一语料在不同`resolution`设置下会产生截然不同的问答表现。