---
id: "multi-agent"
concept: "多Agent协作系统"
domain: "ai-engineering"
subdomain: "agent-systems"
subdomain_name: "Agent系统"
difficulty: 8
is_milestone: false
tags: ["Agent"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.7
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.382
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 多Agent协作系统

## 概述

多Agent协作系统（Multi-Agent System，MAS）是指由两个或两个以上具备独立感知、推理与行动能力的AI Agent组成的协调架构，各Agent通过消息传递、共享内存或工具调用机制共同完成单一Agent难以独立解决的复杂任务。与单Agent循环不同，MAS的核心价值在于**分工并行**：不同Agent可同时执行互不依赖的子任务，将串行流程压缩为并行流程，理论上可将大型任务的完成时间缩短至O(log n)量级。

多Agent系统的理论根源可追溯至1980年代的分布式人工智能（DAI）研究，Marvin Minsky在1986年的《心智社会》（The Society of Mind）中提出"心智是由大量简单Agent相互作用构成的"这一思想，直接启发了后来的Agent协作架构设计。进入大语言模型时代后，2023年MetaGPT、AutoGen等框架相继发布，使基于LLM的多Agent协作从学术概念迅速转变为工程实践。

在AI工程场景中，多Agent协作之所以必要，是因为单个LLM Agent受限于上下文窗口长度（通常为8k~128k tokens）、单次推理的认知负荷上限，以及角色专业性不足等问题。将代码生成、测试验证、文档撰写分配给三个专职Agent，比让一个全能Agent串行完成所有工作，在准确率和可维护性上均有显著提升。

---

## 核心原理

### 协作拓扑结构

多Agent系统的通信方式决定了协作的基本形态，主要分为三种拓扑：

- **中心化（Centralized）**：存在一个Orchestrator Agent（编排者），其余Agent作为Worker接受指令。MetaGPT中的ProductManager→Architect→Engineer流水线即属此类，编排者持有全局任务状态，Worker仅处理分配的子任务。
- **去中心化（Decentralized）**：所有Agent地位对等，通过点对点消息广播协调行为。适合无固定流程的探索型任务，但容易产生通信冗余。
- **分层混合（Hierarchical）**：多级编排，如AutoGen中Manager Agent管理若干Group，Group内部再自组织。此结构可处理需要多层级分解的超大型任务。

### Agent间通信协议

Agent之间传递的不是原始文本，而是结构化消息对象。一条典型的Agent消息包含以下字段：

```
{sender: "Planner", receiver: "Coder", 
 message_type: "task_assignment",
 content: {...}, 
 conversation_id: "uuid-xxx",
 timestamp: 1700000000}
```

消息类型通常包括：`task_assignment`（任务分配）、`result_report`（结果汇报）、`clarification_request`（澄清请求）和`termination_signal`（终止信号）。消息协议的规范程度直接影响系统的可调试性——未规范化的自由文本通信是MAS调试困难的主要根源之一。

### 角色专业化与上下文隔离

每个Agent持有独立的System Prompt，通过角色定义（Role Definition）实现专业化。例如在代码审查场景中，`SecurityReviewer` Agent的System Prompt仅包含安全漏洞检测规则，而`PerformanceReviewer`仅关注时间复杂度分析。这种上下文隔离确保每个Agent的推理不被无关信息干扰，同时避免单个Agent的上下文窗口被多重职责撑爆。

角色专业化还带来**认知角色分离**效果：让一个Agent专门扮演"批评者"（Critic）角色，对另一个Agent的输出进行质疑和验证，可有效减少LLM自我确认偏差（Self-confirmation Bias），这正是AutoGen的`AssistantAgent` + `UserProxyAgent`双Agent模式的设计初衷。

### 共享状态与记忆管理

MAS中的Agent可通过三种方式共享信息：
1. **共享消息历史（Shared Message History）**：所有Agent可读取完整对话记录，适合需要全局上下文的任务，但随轮次增加上下文膨胀风险高。
2. **黑板系统（Blackboard System）**：Agent将中间结果写入共享内存区（如向量数据库或键值存储），按需读取。CrewAI的`Memory`模块采用此架构。
3. **消息摘要传递（Summarized Handoff）**：每个Agent仅接收前置Agent输出的摘要，保持上下文精简，但存在信息损失风险。

---

## 实际应用

**软件开发流水线**是MAS最成熟的应用场景。MetaGPT定义了Boss→ProductManager→Architect→ProjectManager→Engineer→QAEngineer的六角色流水线，在SWE-bench基准测试中，这种多角色架构相比单Agent方案将代码生成的文件级正确率提升约15%。

**多角色研究报告生成**：一个典型配置为：`SearchAgent`负责调用搜索API收集原始资料，`SummaryAgent`对每份资料提炼摘要，`AnalystAgent`综合多份摘要提炼洞察，`WriterAgent`最终生成报告，`CriticAgent`审阅并提出修改意见。整个流程可将研究人员手动处理40+页资料压缩为10分钟内的自动化输出。

**辩论式推理（Debate-based Reasoning）**：Google DeepMind的研究（2023）表明，让两个LLM Agent互相辩论同一问题，比单个LLM自我反思的答案准确率在数学推理任务上高出约11个百分点。这种模式在医疗诊断辅助、法律风险分析等高精度要求场景有实际落地价值。

---

## 常见误区

**误区一：Agent越多越好**

增加Agent数量会线性增加通信开销，并引入更多协调失败点。当任务可以被单Agent在一次规划中完成时，强行引入多Agent只会增加延迟和token消耗。经验法则是：只有当任务存在**真实可并行的子任务**，或需要**专业化角色分离**时，才值得引入多Agent架构。三个高质量专职Agent通常优于十个泛化Agent。

**误区二：将多Agent协作等同于多轮对话**

多轮对话（Multi-turn Conversation）是单一Agent与用户的迭代交互；多Agent协作是Agent之间的自主任务传递与协商。前者的对话历史由用户驱动，后者的消息流由Agent自主生成和路由。混淆两者会导致架构设计时错误地将用户代理（User Proxy）的职责分配给多个Agent。

**误区三：忽略终止条件设计**

MAS中若没有明确的任务完成检测逻辑，Agent之间可能形成无限循环——`AgentA`认为需要`AgentB`补充信息，`AgentB`又将问题回传给`AgentA`。AutoGen框架专门提供`max_consecutive_auto_reply`参数（默认值为10）来强制终止，工程实践中必须结合业务逻辑自定义`is_termination_msg`函数，而非依赖默认轮次上限。

---

## 知识关联

理解多Agent协作系统需要先掌握**Agent循环（感知-推理-行动）**：每个子Agent内部依然运行独立的感知-推理-行动循环，MAS本质上是将这些循环通过通信协议连接起来的上层架构。**Agent规划与分解**能力决定了Orchestrator Agent能否将复杂任务正确切分为可分配给各Worker Agent的原子子任务，错误的任务分解是MAS失败的最主要原因。

向上，本概念直接支撑**AutoGen框架**和**CrewAI框架**的使用——两个框架均提供了MAS通信协议、角色定义和消息路由的具体工程实现。**Agent编排与工作流**进一步将MAS的动态协作模式固化为可重复执行的有向无环图（DAG）流程，而**Agent工作流编排**则关注如何在生产环境中监控、重试和版本管理这些多Agent流程。**自主Agent前沿**方向中的自演化Agent（Self-evolving Agent）研究，本质上也是探索MAS中Agent如何动态调整自身角色和协作策略。
