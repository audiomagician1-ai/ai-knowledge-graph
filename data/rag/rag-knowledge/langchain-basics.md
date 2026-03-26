---
id: "langchain-basics"
concept: "LangChain基础"
domain: "ai-engineering"
subdomain: "rag-knowledge"
subdomain_name: "RAG与知识库"
difficulty: 5
is_milestone: false
tags: ["工具"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 47.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.467
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# LangChain基础

## 概述

LangChain是由Harrison Chase于2022年10月首次发布的开源框架，专为构建基于大型语言模型（LLM）的应用程序而设计。其核心设计理念是"链式组合"（Chaining）——将LLM调用与外部数据源、工具、记忆模块通过标准化接口串联起来，使开发者无需从零搭建复杂的LLM管线。截至2024年，LangChain在GitHub上已积累超过85,000颗星，成为AI工程领域最广泛采用的LLM应用框架之一。

LangChain在RAG（检索增强生成）工程实践中扮演重要角色。它通过`DocumentLoader`、`TextSplitter`、`VectorStore`和`Retriever`四大组件，为构建知识库问答系统提供了完整的端到端工具链。相比手工调用OpenAI API再拼接检索结果，LangChain将这些步骤抽象为可复用的模块，显著降低了RAG系统的开发复杂度。

框架分为两个主要包：`langchain-core`定义基础抽象接口，`langchain`提供具体实现和集成。2024年发布的LangChain v0.2版本进一步将第三方集成拆分为独立包（如`langchain-openai`、`langchain-community`），避免依赖膨胀。理解这一包结构，有助于在实际项目中按需安装，而不是引入整个生态的所有依赖。

---

## 核心原理

### 1. LCEL：LangChain表达式语言

LangChain Expression Language（LCEL）是2023年引入的核心语法，使用管道符`|`连接各组件，实现声明式链式调用：

```python
chain = prompt | llm | output_parser
result = chain.invoke({"question": "什么是RAG？"})
```

LCEL背后实现了`Runnable`协议——每个组件都必须实现`invoke`、`batch`、`stream`三个方法。`batch`支持并发处理多个输入，`stream`支持流式输出token。通过`RunnableParallel`可以并行执行多个子链，通过`RunnablePassthrough`可以透传输入数据不做修改。这一协议设计使得任意符合`Runnable`接口的对象都可以插入链中，极大提升了组件的可替换性。

### 2. Prompt模板系统

LangChain提供三种Prompt类：`PromptTemplate`（纯文本）、`ChatPromptTemplate`（多轮对话消息列表）和`FewShotPromptTemplate`（含示例的少样本提示）。`ChatPromptTemplate`将消息拆分为`SystemMessage`、`HumanMessage`和`AIMessage`三类，与OpenAI Chat API的角色划分直接对应：

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个知识库助手，仅根据以下上下文回答：\n{context}"),
    ("human", "{question}")
])
```

在RAG场景中，`{context}`占位符接收检索到的文档片段，`{question}`接收用户查询——这是LangChain RAG链最基础的Prompt结构。

### 3. 文档处理管线：Loader → Splitter → Embedder

LangChain的RAG数据准备分三步：

**DocumentLoader**：支持40+种数据源，包括`PyPDFLoader`、`WebBaseLoader`、`CSVLoader`等，统一输出`Document`对象（含`page_content`字符串和`metadata`字典）。

**TextSplitter**：最常用的是`RecursiveCharacterTextSplitter`，按`["\n\n", "\n", " ", ""]`顺序递归分割，优先在段落边界断开。关键参数：`chunk_size`（每块最大字符数，常设512或1000）和`chunk_overlap`（相邻块重叠字符数，常设50-200，防止语义截断）。

**Embeddings + VectorStore**：`OpenAIEmbeddings`默认使用`text-embedding-ada-002`模型（1536维向量）。`Chroma`、`FAISS`、`Pinecone`等VectorStore封装了向量存储和相似度搜索，调用`similarity_search(query, k=4)`返回最相关的k个`Document`对象。

### 4. RetrievalQA与LCEL RAG链

LangChain有两种构建RAG链的方式：旧版`RetrievalQA`链和新版LCEL写法。推荐的LCEL RAG链结构如下：

```python
from langchain_core.runnables import RunnablePassthrough

rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
```

此处`retriever`实现了`Runnable`接口，自动将问题字符串转换为检索结果并格式化为上下文字符串。整条链的数据流：用户问题 → 并行执行（检索器获取context + PassThrough传递question）→ 注入Prompt → LLM生成 → 解析输出。

---

## 实际应用

**企业知识库问答系统**：将公司内部PDF文档用`PyPDFLoader`加载，`RecursiveCharacterTextSplitter`按`chunk_size=500, chunk_overlap=100`切割，存入本地`Chroma`向量库。查询时通过`MMR`（最大边际相关性）检索策略（`search_type="mmr"`）获取多样性结果，避免返回重复内容。

**对话式RAG**：使用`ConversationBufferMemory`或`ChatMessageHistory`保存历史对话，配合`create_history_aware_retriever`将多轮问题压缩为独立查询，解决"它是什么意思"这类指代不明的问题。

**工具调用Agent**：通过`create_react_agent`创建ReAct模式的Agent，传入`TavilySearchResults`（网络搜索）和自定义的向量库检索工具，让LLM自主决策何时检索内部知识库、何时联网搜索。

---

## 常见误区

**误区1：认为`chunk_size`越大越好**
增大`chunk_size`会提升单块语义完整性，但也导致注入Prompt的上下文过长、超出模型context window，且检索精度下降（大块中无关内容稀释相关信息）。实践中应根据具体模型的context limit（如GPT-3.5的4096 tokens）和文档类型调整，技术文档通常用512-800，叙述性文档可用1000-1500。

**误区2：混淆`similarity_search`和`as_retriever`的默认行为差异**
直接调用`vectorstore.similarity_search(query, k=4)`返回`Document`列表；而`vectorstore.as_retriever(search_kwargs={"k": 4})`返回`Retriever`对象，可接入LCEL链。两者检索结果相同，但后者才能正确插入`|`管道。误用前者会导致链无法正确处理输入输出类型，抛出`TypeError`。

**误区3：将LangChain版本混用**
LangChain在v0.1至v0.2期间经历了大规模API重构，许多旧版接口（如`LLMChain`、`load_chain`）已被废弃。在同一项目中混用`from langchain.chains import LLMChain`（旧）和`langchain_core`（新）会导致行为不一致。应统一使用`langchain>=0.2`的LCEL写法，通过`LangChainDeprecationWarning`排查遗留代码。

---

## 知识关联

**前置知识衔接**：RAG检索增强生成的概念奠定了"检索+生成"两阶段架构的认知基础，LangChain将这一架构具体实现为`Retriever → Prompt → LLM`的LCEL链，每个RAG概念在LangChain中都有对应的具体类和方法。

**向量数据库**：LangChain的`VectorStore`抽象层统一封装了Chroma、FAISS、Pinecone等向量库的操作接口，学习LangChain后理解各向量库的选型差异（本地vs云端、内存vs持久化）将更具实践指导意义。

**下一步：LlamaIndex**：LlamaIndex（原GPT Index）与LangChain定位有所不同——LlamaIndex更专注于数据索引和查询引擎，提供了`SentenceWindowNodeParser`、`HierarchicalNodeParser`等更精细的文档切分策略，以及`QueryEngine`和`SubQuestionQueryEngine`等高级查询分解机制。学习LlamaIndex时，可以将LangChain的`TextSplitter`与LlamaIndex的`NodeParser`对比理解：前者以字符数为主要切分依据，后者支持基于语义单元（句子、段落）的结构化切分。