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
quality_tier: "S"
quality_score: 82.9
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


# LangChain基础

## 概述

LangChain是由Harrison Chase于2022年10月在GitHub上首次发布的开源框架，专为构建基于大型语言模型（LLM）的应用程序而设计。其核心设计理念是"链式组合"（Chaining）——将LLM调用、数据检索、工具执行等独立步骤串联成可复用的流水线，从而解决单次LLM调用无法完成复杂任务的根本问题。

LangChain的架构由六个主要模块构成：模型I/O（Model I/O）、数据连接（Data Connection）、链（Chains）、代理（Agents）、记忆（Memory）和回调（Callbacks）。区别于直接调用OpenAI API的方式，LangChain提供了统一的抽象层，使开发者可以用相同代码切换GPT-4、Claude、Llama等不同底层模型，而无需重写业务逻辑。

在RAG系统开发领域，LangChain的`RetrievalQA`链和`ConversationalRetrievalChain`成为业界最广泛采用的快速原型工具。从v0.1到v0.2版本（2024年发布），LangChain引入了LangChain Expression Language（LCEL）作为新的链式构建标准，将原有的顺序链重构为基于`Runnable`接口的管道操作符`|`连接方式，大幅简化了异步流式处理的实现复杂度。

---

## 核心原理

### 提示词模板（PromptTemplate）

LangChain的`PromptTemplate`类将原始字符串模板转化为结构化的提示词对象，支持通过`input_variables`参数声明变量占位符。例如，一个RAG场景的提示模板通常包含`{context}`和`{question}`两个变量，分别接收检索到的文档块和用户原始问题。`ChatPromptTemplate`进一步支持多角色消息结构，可分别为`SystemMessage`、`HumanMessage`、`AIMessage`设置不同的模板内容，这对于需要严格控制模型角色行为的知识库问答系统至关重要。

### 文档加载与文本分割

LangChain提供超过100种`DocumentLoader`实现，包括`PyPDFLoader`、`WebBaseLoader`、`CSVLoader`等，统一输出`Document`对象（包含`page_content`和`metadata`两个字段）。文本分割器`RecursiveCharacterTextSplitter`是RAG预处理阶段最常用的组件，其分割逻辑按`["\n\n", "\n", " ", ""]`的优先级顺序递归切分文本，典型配置为`chunk_size=1000`、`chunk_overlap=200`字符。`chunk_overlap`参数的存在是为了防止语义上连续的内容在块边界处被硬性截断，确保检索片段的完整性。

### 向量存储与检索器（Retriever）

LangChain通过`VectorStore`抽象类统一封装了Chroma、FAISS、Pinecone、Weaviate等向量数据库的操作接口，核心方法包括`add_documents()`和`similarity_search(k=4)`。将`VectorStore`转换为`Retriever`对象后，可通过`search_type`参数选择`"similarity"`（余弦相似度）、`"mmr"`（最大边际相关性，用于减少检索结果冗余）或`"similarity_score_threshold"`（设置相似度阈值过滤）三种检索策略。MMR算法在检索时同时最大化相关性和最小化结果间的相似性，公式为：`MMR = argmax[λ·Sim(q,d) - (1-λ)·max Sim(d,dj)]`，其中λ默认值为0.5。

### LCEL链式表达式

LangChain Expression Language（LCEL）的核心是`Runnable`协议，所有实现该协议的组件均支持`|`管道操作符组合。一个标准RAG链的LCEL写法为：

```python
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
```

该写法支持原生的`.stream()`流式输出和`.batch()`批量处理，相比旧版`LLMChain`减少了约40%的样板代码量。

---

## 实际应用

**构建企业知识库问答系统**：使用`ConversationalRetrievalChain`时，需同时传入`retriever`和`memory`参数。`ConversationBufferWindowMemory(k=5)`保留最近5轮对话历史，系统会自动将历史问题与当前问题合并后进行向量检索，解决多轮对话中指代消解（如"它是什么意思"）的语境丢失问题。

**自定义Agent工具链**：在需要调用外部API或执行数据库查询的RAG增强场景中，可通过`@tool`装饰器将Python函数注册为Agent可调用工具。结合`AgentType.OPENAI_FUNCTIONS`类型，Agent会利用OpenAI的函数调用特性精确选择工具，避免ReAct模式下因提示词格式错误导致的解析失败问题。

**文档摘要索引**：对于超长文档（如数百页PDF），`RefineDocumentsChain`采用迭代精炼策略，先对第一个文档块生成初始摘要，再逐步将后续块的信息合并进来，最终输出全文摘要，比`MapReduceDocumentsChain`更适合需要保持叙事连贯性的场景。

---

## 常见误区

**误区一：混淆`Chain`与`Runnable`的适用场景**  
许多初学者在新项目中仍使用`LLMChain`或`SequentialChain`等旧版链类，而LangChain官方自v0.2起已将这些类标记为"Legacy"并建议迁移至LCEL。旧版`LLMChain`不支持原生流式输出，必须额外包装`StreamingStdOutCallbackHandler`才能实现token级别的流式返回，而LCEL管道天然支持`.stream()`方法。

**误区二：错误配置`chunk_overlap`导致检索质量下降**  
部分开发者将`chunk_overlap`设置为0以节省存储空间，这会导致同一句话被分割到两个块中时，无论检索哪个块都只能获得半句话的语义。正确做法是将`chunk_overlap`设置为`chunk_size`的10%至20%，即对于`chunk_size=1000`的配置，`chunk_overlap`应在100至200之间。同时，`chunk_size`的度量单位是**字符数**而非token数，中文场景下1000字符约对应500-700个token，需注意上下文窗口限制。

**误区三：认为LangChain的Agent可以自主规划复杂多步骤任务**  
LangChain的标准Agent（包括ReAct Agent）本质上是单层决策循环，每次只能基于当前观察选择一个工具执行，缺乏跨步骤的状态规划能力。对于需要并行执行多个子任务或动态调整计划的复杂工作流，应使用LangGraph（LangChain的图形化工作流扩展库）而非普通Agent。

---

## 知识关联

LangChain建立在RAG检索增强生成的理论基础之上：RAG中"检索"和"生成"两个阶段在LangChain中分别对应`Retriever`模块和`LLM`模块的具体实现，`RetrievalQA`链正是将这两个阶段编排为可执行流水线的标准化封装。掌握了LangChain中`VectorStore`的索引构建方式和`PromptTemplate`的变量注入机制，才能理解为什么不同的文本分割策略会直接影响最终问答的准确率。

后续学习LlamaIndex时，会发现两者在设计哲学上存在明显差异：LangChain以"链式流程编排"为核心，而LlamaIndex以"数据索引结构"为核心，提供了树形索引、关键词索引、知识图谱索引等LangChain默认不具备的高级索引类型。LlamaIndex的`QueryEngine`在处理结构化数据检索和多文档跨索引查询方面比LangChain的`Retriever`更具表达能力，两者在实际工程中也常被结合使用——以LlamaIndex构建高质量索引，再通过LangChain的Agent框架进行多工具协调。