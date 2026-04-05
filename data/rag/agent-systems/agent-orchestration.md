---
id: "agent-orchestration"
concept: "Agent编排与工作流"
domain: "ai-engineering"
subdomain: "agent-systems"
subdomain_name: "Agent系统"
difficulty: 8
is_milestone: false
tags: ["Agent", "架构"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# Agent编排与工作流

## 概述

Agent编排（Agent Orchestration）是指通过结构化控制逻辑，协调一个或多个AI Agent的执行顺序、数据流转与状态管理，使其完成单个Agent无法独立完成的复杂任务。与简单的Agent调用不同，编排层负责决定"谁在何时做什么"，并处理分支判断、循环迭代、并行执行以及失败重试等控制流问题。

工作流（Workflow）在Agent系统中特指将任务拆解为有向无环图（DAG）或有状态机（State Machine）表示的执行路径，每个节点对应一次Agent行动或工具调用，边代表条件跳转或数据依赖。LangGraph于2024年初将状态机模型引入LLM工作流领域，使循环、人工干预（Human-in-the-loop）等非DAG结构首次在主流框架中得到一等公民支持，这标志着Agent工作流从"流水线模式"向"动态控制流模式"的范式转变。

Agent编排的核心价值在于可靠性与可观测性：通过显式定义节点边界与状态转移，系统在任意步骤崩溃后可从上一个检查点（Checkpoint）恢复，而非从头重跑整个任务链。这对于需要调用外部API、耗时数分钟的生产级Agent任务至关重要。

## 核心原理

### 编排模式：集中式 vs 去中心化

集中式编排（Centralized Orchestration）使用单一的Orchestrator Agent作为指挥者，它持有全局任务状态，将子任务分发给专用Worker Agent，并汇总结果。典型实现如AutoGen的`GroupChatManager`，它在每轮对话后重新评估下一步由哪个Agent发言。其优势是全局状态一致，缺点是Orchestrator成为单点瓶颈。

去中心化编排（Decentralized / Choreography模式）中，各Agent通过消息总线（如Redis Stream或Kafka Topic）监听事件并自主触发，无需中心节点协调。LangChain的`AgentExecutor`每次工具调用后由LLM自身决定是否继续循环，本质上是单Agent的去中心化自编排。去中心化适合松耦合场景，但全局状态追踪困难。

### 状态管理与检查点机制

Agent工作流的状态通常以`State`对象贯穿整个执行图。以LangGraph为例，`StateGraph`要求开发者定义一个`TypedDict`作为全局状态模式，每个节点函数接收当前状态并返回状态的增量更新（partial update），框架负责合并。这种设计确保任意节点均可无副作用地重入。

检查点（Checkpoint）将每次状态转移后的快照持久化到存储后端（如SQLite、PostgreSQL）。关键公式为：

> **可恢复执行 = 状态快照 + 执行图定义 + 线程ID（Thread ID）**

只要这三者不变，工作流可在任意节点中断后，通过传入相同`thread_id`无缝续跑。LangGraph的`MemorySaver`和`SqliteSaver`分别对应内存与磁盘两种检查点后端。

### 控制流结构：条件边与并行分支

**条件边（Conditional Edge）**：`add_conditional_edges(node, routing_function, mapping)`将节点的输出传入路由函数，根据返回值跳转到不同后继节点，实现动态分支。例如，路由函数检查`state["error_count"] > 3`则跳转到`fallback_node`，否则进入`retry_node`。

**并行分支（Fan-out / Fan-in）**：通过将多个节点连接到同一前驱节点实现并行，LangGraph在内部使用Python的`asyncio`并发执行这些分支，并在所有分支完成后通过`fan-in`节点合并结果。在实测中，将3个独立的RAG检索Agent并行化可将总延迟从串行的约9秒降低至约3.5秒。

### 人工干预（Human-in-the-loop）集成

HITL通过`interrupt_before`或`interrupt_after`参数实现：在指定节点执行前/后暂停工作流，将控制权交还给外部系统。典型场景是Agent生成SQL后暂停，等待人工审核确认后再执行数据库操作。此模式下，`thread_id`作为会话标识符，外部系统通过`graph.update_state(thread_id, new_state)`注入人工修改后恢复执行。

## 实际应用

**代码审查自动化流水线**：工作流依次调用`CodeAnalysisAgent`（静态分析）→`SecurityScanAgent`（OWASP漏洞检测）→`ReviewSummaryAgent`（生成审查报告），三者串行但每步结果写入共享State，最终节点根据`state["security_issues"] > 0`条件触发人工审核中断。

**多源信息聚合报告**：Orchestrator将用户查询分解为3个并行子任务：`WebSearchAgent`、`DatabaseQueryAgent`、`DocumentRetrievalAgent`同时执行（Fan-out），完成后`SynthesisAgent`读取三者输出进行跨源信息融合（Fan-in），生成统一报告。整体端到端延迟比串行方式减少约60%。

**自适应客服系统**：使用状态机模式，工作流从`intent_classification`节点出发，根据分类结果条件跳转至`billing_agent`、`technical_support_agent`或`escalation_agent`，每个子Agent完成后统一汇入`response_validation`节点，不满足置信度阈值（< 0.75）则循环回`clarification_agent`请求用户澄清，最多重试2次后强制转人工。

## 常见误区

**误区一：将编排等同于链式调用（Chain）**。LangChain早期的`SequentialChain`是静态的线性流水线，无法处理循环、条件分支或中途状态修改。真正的Agent工作流编排必须支持有状态的迭代执行（例如ReAct循环的Thought→Action→Observation→Thought可重复N次），两者在能力上存在本质差距，不可混用概念。

**误区二：状态对象越大越好**。将所有中间产物（包括每次工具调用的原始响应）都堆入State会导致检查点序列化开销爆炸式增长，并加剧后续节点的上下文窗口压力。最佳实践是State仅存储**跨节点必需的摘要信息**，原始响应写入外部存储（如向量数据库）并在State中保留索引键。

**误区三：认为并行执行一定更快**。并行分支的实际加速比受制于LLM API的速率限制（Rate Limit）：若并行调用5个Agent同时触发GPT-4o，在OpenAI的TPM（Tokens Per Minute）限额下，各请求会相互竞争配额，导致部分请求排队，并行优势大幅收窄甚至消失。应预先评估Token消耗总量与API配额的比值，决定并行度上限。

## 知识关联

本概念建立在**多Agent协作系统**基础上：多Agent协作解决了"哪些专用Agent存在及其职责边界"的问题，而Agent编排与工作流解决的是"这些Agent如何被结构化地驱动执行"的问题——前者定义角色，后者定义剧本。没有清晰的Agent角色划分，编排图的节点设计将缺乏依据。

掌握Agent编排后，**Agent部署与监控**是自然的下一步：工作流中的每个节点执行、状态转移和检查点写入都是需要被监控的可观测单元，部署时需要考虑工作流引擎的持久化后端选型（内存/数据库）、异步执行环境（FastAPI + asyncio）以及分布式追踪集成（LangSmith、OpenTelemetry）。同时，**AI应用架构设计**将把本文的工作流模式（DAG、状态机）提升到系统架构层面，讨论编排层与业务逻辑层、数据层的解耦策略及微服务化方案。