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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 多Agent协作系统

## 概述

多Agent协作系统（Multi-Agent System，MAS）是指由两个或两个以上具备独立推理和行动能力的AI Agent组成的协同架构，其中每个Agent承担特定角色或专业职责，通过结构化的消息传递机制共同完成单个Agent无法高效完成的复杂任务。与单Agent系统相比，MAS的核心优势在于**并行分工**与**专业化**——不同Agent可以同时处理任务的不同子问题，也可以互相审查彼此输出以减少幻觉错误。

多Agent协作的理论根源可追溯至1980年代分布式人工智能（Distributed AI）领域，研究者Victor Lesser等人提出的"合同网协议"（Contract Net Protocol，1980）定义了Agent之间任务招标与投标的通信模型。进入大语言模型时代后，2023年微软研究院发布的AutoGen框架和Anthropic关于多Agent协作的研究报告重新激活了这一领域，使基于LLM的多Agent系统在工程实践中变得可行。

多Agent架构之所以在AI工程中受到重视，是因为它直接解决了单Agent的两个结构性瓶颈：上下文窗口容量限制导致的长任务退化，以及单一角色无法同时扮演"执行者"和"批评者"的角色冲突。实验数据显示，在HumanEval编程基准测试中，引入代码审查Agent后，多Agent系统的通过率比单Agent提升了约15-20个百分点。

---

## 核心原理

### 角色分工与专业化Agent设计

多Agent系统的首要设计决策是**角色定义**（Role Definition）。常见角色类型包括：Orchestrator（编排者，负责任务分解与调度）、Worker（执行者，负责具体工具调用或内容生成）、Critic（批评者，负责输出质量审查）、以及Memory Manager（记忆管理者，负责跨轮次信息汇总）。每个Agent通过独立的System Prompt被赋予角色约束，这意味着同一个底层LLM可以在不同Agent实例中表现出截然不同的行为模式。角色设计的质量直接决定了Agent之间是否会产生**职责重叠**（导致冗余计算）或**职责空白**（导致任务遗漏）。

### Agent间通信协议

Agent之间的交互通过**消息传递（Message Passing）**实现，而非共享内存，这是MAS区别于传统软件模块的关键特征。消息结构通常包含以下字段：`sender`（发送方标识）、`receiver`（接收方标识或广播标记）、`content`（消息正文）、`message_type`（指令/结果/查询之一）。拓扑结构上，MAS支持三种主要通信模式：

- **星型拓扑（Hub-and-Spoke）**：所有Worker向中心Orchestrator汇报，Orchestrator统一调度，适合任务依赖关系复杂的场景。
- **链式拓扑（Pipeline）**：Agent A的输出直接成为Agent B的输入，形成流水线，适合有严格顺序依赖的任务（如：草稿撰写→事实核查→格式排版）。
- **全连接拓扑（Fully Connected）**：任意Agent可与任意Agent通信，灵活性最高但协调成本也最高，通常需要额外的终止条件控制防止无限循环。

### 终止条件与共识机制

多Agent系统必须明确定义**终止条件**，否则Agent之间的对话可能形成无法收敛的循环。工程上常用的终止策略有三种：（1）**轮次上限**，如设置`max_turns=10`强制停止；（2）**关键词触发**，当某个Agent输出包含预定义的完成标记（如`TERMINATE`字符串）时停止；（3）**共识检测**，Critic Agent对结果打分，当分数超过阈值（如0.85/1.0）时系统停止并输出结果。缺少明确终止条件是生产环境中MAS最常见的故障模式之一，可能导致API费用失控或任务永不交付。

### 状态管理与共享上下文

单Agent靠单一对话历史维护状态，而多Agent系统需要处理**分布式状态一致性**问题。常用方案是引入**共享黑板（Shared Blackboard）**，即一个所有Agent均可读写的结构化状态对象（通常是JSON或Python字典），其中记录任务进度、中间产物和已验证结论。每个Agent在执行前读取黑板状态，执行后将结果写回黑板，避免了不同Agent因上下文不同而产生矛盾输出的问题。

---

## 实际应用

**软件开发自动化**是多Agent系统最成熟的应用场景。典型的软件开发MAS包含四个Agent：需求分析Agent（将用户需求转化为技术规格）、代码生成Agent（调用工具编写代码）、测试Agent（生成并执行单元测试）、代码审查Agent（检查安全漏洞和代码规范）。这四个Agent按照链式拓扑依次处理，测试Agent发现的Bug会以消息形式反馈给代码生成Agent触发修复循环。DeepMind的AlphaCode 2和GitHub Copilot Workspace均采用了类似的多Agent流水线架构。

**企业级研究报告生成**是另一个典型应用。以金融分析为例：Search Agent负责从SEC数据库检索公司财报，Data Analysis Agent执行Python代码计算财务比率（如市盈率P/E、债务权益比D/E），Writing Agent将数据分析结果转化为专业报告文本，最后Fact-Check Agent对报告中的每一个数字引用进行交叉验证。这种架构将原本需要人类分析师3-5天的工作压缩至30分钟以内，并且每个分析步骤都有独立Agent的操作日志可追溯。

**多Agent辩论（Multi-Agent Debate）**是一种专门用于提升推理准确性的MAS模式：多个Agent（通常3-5个）独立回答同一问题，然后互相阅读对方的答案并更新自己的立场，经过2-3轮迭代后达到收敛。MIT的研究（2023）显示，这种辩论机制在算术推理任务上将GPT-3.5的准确率从53%提升至77%。

---

## 常见误区

**误区一：Agent越多系统越强**。增加Agent数量会引入更多的通信开销、更长的总执行延迟以及更复杂的错误传播路径。一个设计精良的双Agent系统（如Orchestrator + Worker）通常比一个设计草率的六Agent系统表现更优。工程原则是：只有当某项职责在角色上与现有Agent存在根本冲突（如执行者无法同时客观评估自己的输出）时，才引入新Agent。

**误区二：多Agent系统天然具备容错能力**。新手常认为"有Critic Agent就能自动纠错"，但Critic Agent自身也可能产生幻觉，而且如果Critic使用与Worker相同的底层模型，它们会倾向于犯相同类型的错误（相关误差）。真正的鲁棒性需要通过以下手段实现：使用不同参数量或不同提供商的模型作为不同Agent的后端、为Critic Agent提供外部工具（如代码执行器）以进行实际验证，而非仅依赖语言判断。

**误区三：将多Agent系统等同于并行API调用**。简单的并行调用只是将同一个任务提交给多个相同Agent取平均，而真正的MAS要求Agent之间存在**角色差异**、**消息交互**和**动态任务分配**。只有包含这三个要素才算是多Agent协作，否则只是批量推理（Batch Inference）。

---

## 知识关联

**前置知识依赖**：理解多Agent系统需要先掌握**Agent循环（感知-推理-行动）**，因为MAS中的每个Agent本质上是一个独立运行的单Agent循环；同时需要熟悉**Agent规划与分解**（如ReAct和Tree-of-Thought方法），因为Orchestrator Agent的核心功能正是将复杂任务拆解为可分派给Worker Agent的子任务，没有规划能力的Orchestrator会导致任务分配混乱。

**后续概念延伸**：掌握MAS基础后，可以进入**AutoGen框架**学习微软如何通过`ConversableAgent`和`GroupChat`类将上述原理工程化，或进入**CrewAI框架**了解基于角色的Agent编排如何用声明式API实现。**Agent编排与工作流**则在MAS基础上引入有向无环图（DAG）来精确控制Agent的执行顺序和条件分支，是将实验性MAS升级为生产级系统的关键步骤。**自主Agent前沿**中的Voyager（Minecraft环境）和SWE-Agent（软件工程环境）则展示了当MAS与长期记忆和自我进化能力结合时系统能力的边界。