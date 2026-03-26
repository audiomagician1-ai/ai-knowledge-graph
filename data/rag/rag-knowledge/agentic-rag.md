---
id: "agentic-rag"
concept: "Agentic RAG"
domain: "ai-engineering"
subdomain: "rag-knowledge"
subdomain_name: "RAG与知识库"
difficulty: 8
is_milestone: false
tags: ["RAG", "Agent"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 46.5
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

# Agentic RAG

## 概述

Agentic RAG（智能体增强检索生成）是将大型语言模型的自主决策能力与检索增强生成管道结合的架构范式。与传统RAG的单轮"检索→生成"线性流程不同，Agentic RAG允许系统自主判断何时检索、检索什么、检索几次，以及是否需要对检索结果进行验证或追加查询。这意味着系统不再被动执行固定步骤，而是根据任务的中间结果动态调整行为路径。

该范式在2023年下半年随着LangChain的ReAct Agent和LlamaIndex的Agent框架普及而进入工程主流。其理论基础来自Yao等人于2022年提出的ReAct（Reason + Act）框架——模型在"思考-行动-观察"循环中迭代处理问题，每次行动可以是向量检索、SQL查询、API调用或代码执行。将此循环嵌入RAG管道，即形成Agentic RAG的基本结构。

Agentic RAG的核心价值在于处理单次检索无法解决的复杂问题。例如，用户询问"对比A公司和B公司2023年的财务表现并给出投资建议"，传统RAG只能做一次检索并拼接上下文，而Agentic RAG会分解为：检索A公司财报→检索B公司财报→比较数据→检索行业基准→综合生成建议，每步结果驱动下一步行动。

## 核心原理

### 工具调用与检索决策机制

Agentic RAG的Agent将检索操作建模为"工具"（Tool），与搜索引擎调用、计算器、代码解释器并列。Agent通过函数调用（Function Calling）接口决定调用哪个工具，传入什么查询参数。典型工具定义包含：`tool_name`（如`vector_search`）、`description`（供LLM判断适用场景）、`parameters`（如`query: str, top_k: int, filter: dict`）。LLM根据当前对话状态与工具描述进行匹配，而非机械地在每次回答前执行检索，这使得对于LLM已知的简单事实查询，系统可以跳过检索直接回答，降低延迟。

### 多步检索与自我纠错循环

Agentic RAG的关键能力是多轮迭代检索。在ReAct循环中，每次工具调用的结果（Observation）被追加回上下文，LLM重新评估是否已获得足够信息。若检索结果相关性低（例如向量相似度均低于0.7阈值），Agent可自动改写查询——将原始问题拆解为子问题，或切换检索策略（如从语义检索切换为关键词BM25检索）。LlamaIndex的`SubQuestionQueryEngine`正是实现这一模式的具体组件，它将复杂问题分解为N个子问题并行检索，最后合并答案。

### 规划器-执行器分离架构

在更复杂的Agentic RAG实现中，系统分为**规划器（Planner）**和**执行器（Executor）**两层。规划器（通常是能力更强的模型，如GPT-4o）负责将用户意图拆解为有序检索任务列表；执行器（可以是较小的模型或直接调用嵌入检索API）按序执行每个检索子任务并返回结果。这种分离允许规划层使用思维链（Chain-of-Thought）推理，而执行层专注于高效检索，整体延迟可控制在单纯使用大模型规划的50%以下。典型的任务计划结构如下：

```
Step 1: retrieve(query="A公司2023年营收", source="financial_db")
Step 2: retrieve(query="B公司2023年营收", source="financial_db")  
Step 3: retrieve(query="科技行业2023年平均PE", source="industry_report")
Step 4: synthesize(inputs=[step1, step2, step3])
```

### 记忆与状态管理

Agentic RAG需要在多步推理过程中维护工作记忆（Working Memory）。与标准RAG仅传递检索文档片段不同，Agentic RAG维护一个结构化的**轨迹缓冲区**，记录每步的思考内容、调用的工具、工具入参及返回结果。当轨迹超出LLM上下文窗口限制（如GPT-4 Turbo的128K tokens）时，系统需要对中间结果进行压缩摘要。MemGPT的分页内存机制和LangGraph的状态图（StateGraph）是管理此类长程状态的两种主流方案。

## 实际应用

**企业知识库问答**：某金融机构部署Agentic RAG处理合规查询，系统将复杂监管问题自动分解为：检索相关法规条款→检索内部操作手册→检索历史判例→交叉验证一致性→生成合规建议。相比传统RAG，答案准确率从67%提升至89%（依据RAGAs框架中的Faithfulness指标评估）。

**代码生成辅助**：GitHub Copilot Workspace的原型采用Agentic RAG思路，Agent先检索项目仓库中的相关文件，发现依赖关系后再检索对应库文档，最后检索历史Issue记录，综合生成代码修改方案。这种三轮检索模式比单次检索将代码可用率（pass@1）提升约23个百分点。

**多源异构数据融合**：当知识库包含向量数据库（非结构化文档）、关系数据库（结构化数据）和图数据库（实体关系）时，Agentic RAG的工具抽象层允许Agent根据问题性质路由到不同数据源：事实性问题→向量检索，统计性问题→SQL查询，关系推理问题→图查询，再将结果统一汇入生成上下文。

## 常见误区

**误区一：将所有RAG都"Agent化"**。并非所有检索任务都需要Agentic架构。对于问题类型单一、检索策略固定的场景（如产品FAQ查询），引入Agent决策循环只会增加平均响应延迟200-800ms，且因多次LLM调用使成本上升3-5倍，而收益几乎为零。Agentic RAG适用的判断标准是：问题需要2步以上的信息推导，或答案依赖多个独立知识源的组合。

**误区二：混淆Agentic RAG与多Agent系统**。Agentic RAG指单个具有自主检索决策能力的Agent，其行动空间主要集中在知识检索与信息综合；多Agent系统（如AutoGen的GroupChat）是多个专业化Agent协作分工。前者是知识访问层的智能化，后者是任务执行层的并行化，二者可以组合但概念不同。

**误区三：忽视检索循环的终止条件**。初学者实现Agentic RAG时常遇到无限检索循环：Agent每次检索后认为信息不足，继续发起新检索。必须显式设置最大迭代次数（业界常用max_iterations=10）和停止信号判断（如LLM输出包含`FINAL ANSWER:`标记时终止循环），否则单次查询可能消耗数百次API调用。

## 知识关联

理解Agentic RAG需要扎实掌握RAG管道架构的基础知识——向量嵌入、相似度检索、上下文窗口管理和生成后处理构成了Agentic RAG中每个检索工具调用的内部实现。没有这些基础，无法理解Agent的工具参数设计和检索结果评估逻辑。

Agentic RAG向上直接对接**自主Agent前沿**方向的核心议题：当检索工具扩展为代码执行、浏览器操作、数据库写入时，系统从信息获取型Agent演变为能够修改外部世界状态的自主Agent。Agentic RAG是从被动RAG到完全自主Agent之间的关键过渡形态，ReAct框架、函数调用接口和工具抽象层的工程经验在自主Agent设计中被直接复用和扩展。