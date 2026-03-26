---
id: "llamaindex-basics"
concept: "LlamaIndex基础"
domain: "ai-engineering"
subdomain: "rag-knowledge"
subdomain_name: "RAG与知识库"
difficulty: 5
is_milestone: false
tags: ["工具"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.433
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# LlamaIndex基础

## 概述

LlamaIndex（原名GPT Index）是一个专为大语言模型（LLM）应用构建的数据框架，由Jerry Liu于2022年11月首次发布在GitHub上。它的核心设计哲学是将外部私有数据与LLM能力连接起来，特别针对RAG（检索增强生成）场景提供了高度封装的抽象层，使开发者无需从零实现文档解析、向量化、检索等繁琐流程。

与LangChain的宽泛定位不同，LlamaIndex专注于"数据索引与查询"这一垂直领域。它提供了一套完整的数据摄取（Ingestion）→索引（Indexing）→查询（Querying）三阶段流水线，每个阶段都有对应的模块化组件。截至2024年，LlamaIndex已发布0.10.x稳定版本，将核心库拆分为`llama-index-core`与各类集成包，支持超过160种数据源连接器（Data Connector）。

LlamaIndex的重要性体现在它大幅降低了企业知识库类应用的开发门槛。通过内置的`SimpleDirectoryReader`，5行Python代码就能完成从本地文档到可查询索引的全部流程。它还内置了对话历史管理、引用溯源（Source Attribution）、混合检索等生产级功能，这些在手工实现RAG时需要数百行代码才能完成。

---

## 核心原理

### 文档与节点（Document & Node）模型

LlamaIndex的数据基本单元是`Document`和`Node`。`Document`对应原始数据文件，`Node`是Document经过分块（Chunking）后的最小可检索单元。每个Node包含：
- `text`：分块后的文本内容
- `metadata`：键值对形式的元数据（文件名、页码、日期等）
- `relationships`：指向父节点、子节点、前一节点、后一节点的引用链接

这种设计使LlamaIndex支持**层次化节点图（Hierarchical Node Graph）**——一个PDF可以分解为章节Node（父），再分解为段落Node（子），检索时可在不同粒度间切换。默认分块大小（`chunk_size`）为1024 tokens，`chunk_overlap`默认为200 tokens。

### 索引类型

LlamaIndex提供多种内置索引类型，每种对应不同的数据组织方式：

**VectorStoreIndex**：最常用，将每个Node的文本通过Embedding模型转化为稠密向量，存入向量数据库。查询时计算查询向量与所有Node向量的余弦相似度，返回Top-K结果。默认Top-K值为2。

**SummaryIndex**（旧称ListIndex）：将所有Node串联后整体送入LLM生成答案，适合需要全局汇总的场景，但token消耗随文档量线性增长，不适合大规模语料。

**KeywordTableIndex**：为每个Node提取关键词，建立关键词→Node的倒排映射表，查询时通过关键词匹配检索，速度快但依赖准确的关键词提取。

**KnowledgeGraphIndex**：自动从文本中抽取（主语，谓语，宾语）三元组，构建知识图谱，适合实体关系密集的场景。

### 查询引擎（Query Engine）与检索器（Retriever）

`QueryEngine`是LlamaIndex对外的统一查询接口，内部由`Retriever`+`ResponseSynthesizer`两部分组成。`Retriever`负责从索引中召回相关Node，`ResponseSynthesizer`负责将召回内容组织成Prompt后调用LLM生成回答。

`ResponseSynthesizer`支持多种合成策略（`response_mode`）：
- `compact`：将多个Node文本压缩拼接后一次性发给LLM（默认模式）
- `refine`：先用第一个Node生成初始答案，再依次用后续Node迭代精炼
- `tree_summarize`：递归地对Node进行两两合并摘要，适合超长文档
- `no_text`：只返回检索到的Node，不调用LLM

### 服务上下文（ServiceContext / Settings）

在0.10.x版本中，LlamaIndex使用全局`Settings`对象统一管理LLM、Embedding模型、分块参数等配置。例如：
```python
from llama_index.core import Settings
Settings.llm = OpenAI(model="gpt-4o", temperature=0.1)
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
Settings.chunk_size = 512
Settings.chunk_overlap = 50
```
旧版本使用的`ServiceContext`在0.10.0之后被废弃，这是迁移时的常见障碍。

---

## 实际应用

**企业内部知识库问答**：将公司PDF手册、Word文档放入同一目录，用`SimpleDirectoryReader`自动识别文件类型并加载，`VectorStoreIndex`建立索引后通过`as_query_engine()`暴露查询接口。通过`node_postprocessors`添加`MetadataReplacementPostProcessor`可在返回答案时自动附上文档来源页码，满足合规追溯需求。

**多文档对比分析**：使用`SubQuestionQueryEngine`，它能将用户的复杂问题自动分解为针对不同文档的子问题并行查询，最终合并各子答案。例如查询"比较2022年和2023年财报中的营收变化"，系统会自动生成两个分别针对不同财报的子查询。

**结构化数据查询**：`PandasQueryEngine`允许直接对Pandas DataFrame进行自然语言查询，LlamaIndex内部会将自然语言转换为Pandas代码执行，适合CSV/Excel格式的结构化知识库场景。

**流式输出（Streaming）**：调用`query_engine.query()`时添加`streaming=True`参数，结合`response.print_response_stream()`可实现逐token输出，改善用户等待体验。

---

## 常见误区

**误区一：将`chunk_size`设置越大越好**
很多初学者认为更大的分块保留了更完整的上下文，实则不然。`chunk_size=4096`时单个Node的语义噪声增加，向量化后的检索精度会下降，因为Embedding模型对超长文本的表示能力有限（如`text-embedding-3-small`的最优输入长度约为512 tokens）。实践中应根据文档类型调整：技术文档适合512-1024，对话记录适合256-512。

**误区二：`VectorStoreIndex`默认将向量存储在内存中，重启后丢失**
默认情况下，`VectorStoreIndex.from_documents()`将向量存储在内存的`SimpleVectorStore`中，进程结束后数据消失。生产环境必须通过`StorageContext`指定持久化存储，或集成Chroma、Pinecone、Weaviate等外部向量数据库。未做持久化导致每次启动重新建索引，消耗大量Embedding API费用是新手最常见的成本浪费。

**误区三：混淆`QueryEngine`与`ChatEngine`的适用场景**
`QueryEngine`是无状态的单轮问答接口，每次查询独立处理，不保留对话历史。`ChatEngine`（如`CondenseQuestionChatEngine`）会将历史对话压缩为上下文，支持追问和指代消解。对于需要"接上文说的那个方案"之类指代解析的场景，错误使用`QueryEngine`会导致LLM无法理解指代关系。

---

## 知识关联

**与RAG概述的关系**：LlamaIndex是RAG流程的具体实现框架。RAG概述中讲解的"文档分块→向量化→检索→增强生成"四步骤，分别对应LlamaIndex中的`NodeParser`、`EmbedModel`、`Retriever`、`ResponseSynthesizer`四个组件。理解RAG的理论流程后，LlamaIndex的抽象设计逻辑会更容易掌握。

**与LangChain的差异与互补**：LangChain的`RetrievalQA`链也能实现RAG，但LlamaIndex在索引多样性（KG索引、层次索引）和查询策略（SubQuestion、树状摘要）上提供了更丰富的开箱即用选项，而LangChain在Agent工具调用、多链编排上更成熟。实际项目中两者可通过`LlamaIndexToolSpec`互相集成——将LlamaIndex的`QueryEngine`封装为LangChain的`Tool`，在LangChain Agent中调用。