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

LlamaIndex（原名GPT Index）是由Jerry Liu于2022年11月发布的专为检索增强生成（RAG）场景设计的Python框架。与通用型AI应用框架不同，LlamaIndex从设计之初就专注于解决"如何将大规模私有数据高效接入大语言模型"这一具体问题，其核心数据结构围绕**索引（Index）**而非链（Chain）或代理（Agent）构建。

LlamaIndex的架构特色在于抽象出了一套完整的数据摄取→索引→查询流水线（Pipeline）。在0.10版本的重大重构后，框架正式拆分为`llama-index-core`核心包与数百个集成子包，安装时使用`pip install llama-index`获取完整套件。其核心价值在于：默认提供针对RAG任务优化的分块策略、嵌入管理和检索后处理机制，而不需要开发者从零拼接这些组件。

相比LangChain的通用链式调用设计，LlamaIndex的抽象粒度更接近"文档问答"这一具体任务。这意味着开发者使用更少的代码即可完成功能完整的RAG系统，但同时也需要理解LlamaIndex特有的Index类型、Node语义和查询引擎接口才能充分发挥其能力。

---

## 核心原理

### 数据加载与Node体系

LlamaIndex通过`SimpleDirectoryReader`、`PDFReader`等数百种`Reader`类将原始文件转换为`Document`对象。`Document`进一步被`NodeParser`切分为`TextNode`——这是LlamaIndex中最小的可检索信息单元。每个`TextNode`携带：

- `text`：实际文本内容
- `metadata`：来源文件名、页码、创建时间等键值对
- `relationships`：与父节点、前后节点的引用关系（`NodeRelationship`枚举类型）

默认的`SentenceSplitter`按`chunk_size=1024` tokens、`chunk_overlap=200` tokens分块。这两个参数对最终检索质量影响显著：chunk_size过大导致噪声增多，过小则丢失上下文完整性。

### Index类型与存储机制

LlamaIndex提供多种索引类型，各有明确的适用场景：

| Index类型 | 存储结构 | 适用场景 |
|-----------|----------|----------|
| `VectorStoreIndex` | 向量数据库 | 语义相似度检索（最常用） |
| `SummaryIndex` | 顺序节点列表 | 需要遍历全文摘要的问题 |
| `KeywordTableIndex` | 倒排关键词表 | 精确关键词匹配场景 |
| `KnowledgeGraphIndex` | 三元组图结构 | 实体关系推理 |

`VectorStoreIndex`构建时，每个TextNode会调用嵌入模型（默认为`text-embedding-ada-002`，1536维）生成向量并存入向量存储。通过`StorageContext`可将索引持久化到本地磁盘或Pinecone、Weaviate等外部向量数据库。

### 查询引擎与检索流程

查询流程遵循**检索→后处理→合成**三阶段：

1. **检索（Retrieval）**：`VectorIndexRetriever`默认返回`similarity_top_k=2`个最相似节点，可调整为混合检索（BM25 + 向量）
2. **后处理（Postprocessing）**：`SimilarityPostprocessor`过滤相似度低于阈值的节点；`KeywordNodePostprocessor`按关键词过滤；`LLMRerank`用LLM对候选节点重排序
3. **合成（Synthesis）**：`ResponseSynthesizer`将检索到的节点与原始问题组合成Prompt送入LLM，支持`compact`（压缩合并）、`refine`（迭代精炼）、`tree_summarize`（树状摘要）等响应模式

完整查询引擎创建示例：
```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.postprocessor import LLMRerank

documents = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine(
    similarity_top_k=5,
    node_postprocessors=[LLMRerank(top_n=3)]
)
response = query_engine.query("量子计算的基本原理是什么？")
```

### ServiceContext与Settings全局配置

在0.10版本后，原有的`ServiceContext`被全局`Settings`对象替代。通过`Settings.llm`、`Settings.embed_model`、`Settings.chunk_size`可一次性配置整个Pipeline使用的模型和参数，避免在每个组件处重复传参。

---

## 实际应用

**企业知识库问答**：将公司内部PDF文档、Confluence页面通过对应Reader导入，构建`VectorStoreIndex`并持久化到Pinecone。前端调用`query_engine.query()`接口，LlamaIndex自动完成向量检索、Rerank和答案合成，开发周期可缩短至2天以内。

**多文档对比分析**：使用`SubQuestionQueryEngine`将一个复杂问题分解为针对不同文档的子问题，分别检索后合并答案。例如询问"A产品和B产品的性能差异"时，框架会自动生成两个子查询并汇总对比结果。

**结构化数据查询**：`PandasQueryEngine`允许对DataFrame直接进行自然语言查询，LlamaIndex将自然语言转换为Pandas代码执行后返回结果，适合混合了文本和表格数据的报告分析场景。

---

## 常见误区

**误区1：认为`VectorStoreIndex`是唯一选择**
许多初学者默认所有场景都使用向量索引。但当问题需要综合整篇文档（如"请总结这份报告的所有风险"）时，`SummaryIndex`配合`tree_summarize`响应模式效果更佳，因为它不做向量截断，会处理全部节点。

**误区2：忽视chunk_overlap的作用**
`chunk_overlap=0`看似节省存储空间，实则会导致语义跨越chunk边界时检索失败。例如一个完整的技术定义若被切割在两个chunk的衔接处，单独检索任一chunk都无法获得完整答案。推荐保持默认的200 token重叠量。

**误区3：混淆`retriever`和`query_engine`的层次**
`retriever`只负责返回原始Node列表，不调用LLM；`query_engine`封装了检索+合成的完整流程。如果只需要做向量搜索而不生成答案（如推荐系统），应直接使用`index.as_retriever()`而非`as_query_engine()`，以节省LLM调用成本。

---

## 知识关联

**前置概念衔接**：RAG检索增强生成概述中建立的"检索-增强-生成"三段式思维，直接对应LlamaIndex的Retriever→Postprocessor→Synthesizer三层架构。LangChain基础中接触过的嵌入模型、向量存储概念在LlamaIndex中同样适用，但LlamaIndex通过`VectorStoreIndex.from_documents()`将这些步骤进一步封装，调用层次更高。

**横向对比LangChain**：LangChain的`RetrievalQA`链与LlamaIndex的`VectorStoreIndex.as_query_engine()`功能等价，但LlamaIndex额外提供了Node关系管理、多种Index类型选择和内置Rerank后处理，在纯RAG场景下配置更简洁。若项目同时需要复杂工具调用和RAG，两者可通过`LlamaIndexToolSpec`进行集成互操作。