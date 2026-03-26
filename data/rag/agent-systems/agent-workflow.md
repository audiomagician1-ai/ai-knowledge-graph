---
id: "agent-workflow"
concept: "Agent工作流编排"
domain: "ai-engineering"
subdomain: "agent-systems"
subdomain_name: "Agent系统"
difficulty: 7
is_milestone: false
tags: ["Agent", "架构"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 48.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.394
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# Agent工作流编排

## 概述

Agent工作流编排是指将多个LLM调用、工具执行和Agent节点组织成结构化执行图的工程方法。与单次LLM调用不同，工作流编排将复杂任务拆解为可独立执行的节点，并通过有向无环图（DAG，Directed Acyclic Graph）定义节点间的数据依赖关系与控制流顺序。LangGraph、LlamaIndex Workflows、Prefect等框架均以DAG或状态机为底层抽象，将Agent的"思考-行动"循环建模为图上的节点遍历。

该领域的工程化实践在2023年前后随着GPT-4的商用普及迅速成熟。早期的ReAct（Reasoning + Acting）模式是线性链式结构，无法表达并行分支；而现代工作流编排系统引入了条件边（Conditional Edge）和并行扇出（Fan-out）机制，使得需要同时调用多个工具或并发查询多个数据源的场景成为可能。

工作流编排的实用价值在于其**确定性与可观测性**：通过显式定义执行图，工程师可以在节点级别插入日志、重试策略和超时控制，而不是依赖LLM自由选择下一步行动。这解决了纯ReAct循环中"不知道Agent下一步会干什么"的核心工程难题。

---

## 核心原理

### DAG结构与节点类型

工作流DAG由节点（Node）和有向边（Edge）构成。节点类型通常包含三类：**LLM节点**（调用语言模型生成文本或决策）、**工具节点**（执行Python函数、API调用或数据库查询）和**路由节点**（根据上游输出决定激活哪条边）。边只能从上游指向下游，不允许回环，这保证了拓扑排序的存在性，使得调度器可以通过Kahn算法或DFS确定节点执行顺序。

在LangGraph框架中，每个节点接受一个共享的`State`字典并返回对该字典的局部更新，例如：

```
def research_node(state: AgentState) -> dict:
    result = llm.invoke(state["messages"])
    return {"messages": state["messages"] + [result]}
```

这种**不可变状态累积**模式避免了节点间的隐式副作用，使得工作流在调试时可以从任意节点的历史快照重放。

### 条件分支（Conditional Edge）

条件分支允许工作流根据运行时数据动态选择下一个执行节点，而非在编译期固定路径。典型实现是定义一个路由函数，检查当前State中的某个字段（如工具调用结果的置信度分数、用户意图分类标签），返回目标节点名称字符串。LangGraph的`add_conditional_edges`接受路由函数和目标节点映射表，在运行时动态解析边。

条件分支的一个关键工程决策是**分支条件的信息来源**：是让LLM输出结构化JSON来决策（如`{"next": "search_agent"}`），还是用规则代码检查某个阈值？前者灵活但不确定，后者确定但需要显式建模所有分支条件。生产系统中常见的做法是让LLM输出受限于枚举值的决策字段，再由代码路由函数消费该字段。

### 并行执行（Fan-out / Fan-in）

并行执行通过"扇出-扇入"（Fan-out / Fan-in）模式实现：一个上游节点完成后，其多个下游节点可以**同时**调度执行，最后由一个聚合节点等待所有并行分支完成并合并结果。这对于需要同时查询多个数据源（如同时调用天气API、新闻API和本地知识库）的场景，可以将串行等待时间从各节点延迟之和压缩至最慢节点的单次延迟。

以Python的`asyncio`为例，并行扇出的实现形态如下：

```python
results = await asyncio.gather(
    web_search_node(state),
    database_query_node(state),
    calculator_node(state)
)
merged_state = fan_in_node(results)
```

并行执行引入了**写冲突**问题：多个节点同时更新同一个State字段时需要合并策略。LangGraph通过在State字段上定义`Reducer`函数（如`operator.add`用于列表追加）解决此问题，而非使用默认的后写覆盖语义。

### 循环与条件终止

尽管DAG本身不允许环，但Agent工作流常需要"反复尝试直到成功"的迭代语义。工程上的解决方案是**将循环展开为条件跳转回入口节点**，配合循环计数器或终止条件检查。LangGraph中通过`END`特殊节点标记终止，路由函数可以在满足条件时返回`END`，否则返回某个上游节点名称实现循环。必须在State中维护`iteration_count`字段并设置硬上限（通常为10至25次），以防止无限循环消耗Token配额。

---

## 实际应用

**代码生成与自动修复工作流**是工作流编排的典型场景。该工作流包含：代码生成节点 → 代码执行节点 → 条件路由（成功/失败）→ 错误分析节点 → 代码修复节点 → 循环回执行节点。GitHub Copilot Workspace和Devin的核心执行引擎均采用类似的循环修复图结构，其中循环上限通常设置为5至8次以平衡修复成功率与成本。

**多源信息聚合报告生成**使用Fan-out模式：一个意图解析节点产出查询关键词后，并行触发网络搜索Agent、内部文档检索Agent和结构化数据查询Agent，三条支路的结果汇入聚合节点，由LLM综合撰写报告。与串行执行相比，并行模式可将平均延迟从约12秒降至约4秒（假设每个工具节点耗时约4秒）。

**客服意图分流系统**使用条件分支：用户输入经意图分类节点后，根据分类标签（账单查询/技术支持/投诉/其他）路由至不同的专业Agent子图，每个子图内部又有独立的工具集和系统提示。这种"主图+子图"的分层编排使得各业务线的Agent逻辑可以独立迭代而不影响整体路由逻辑。

---

## 常见误区

**误区一：将所有逻辑压入单个LLM节点**。初学者常见做法是在一个超长System Prompt中让LLM自行决定所有步骤和工具调用，导致工作流中只有一个巨大的ReAct循环节点。这种做法丢失了DAG编排的可观测性优势：失败时无法定位是哪个子步骤出错，重试必须从头开始而无法从断点续跑。正确做法是将独立的信息检索、决策、生成步骤拆分为独立节点，每节点负责单一职责。

**误区二：混淆DAG编排与提示链的适用边界**。提示链（Prompt Chaining）适用于线性、无分支的固定步骤序列；一旦出现"如果A则走路径X，否则走路径Y"或"步骤B和C可以同时执行"，就必须升级为DAG编排。错误地用提示链处理需要并行的场景会导致不必要的串行等待，而用完整DAG框架处理三步线性流程则引入了不必要的复杂度。

**误区三：忽视State的大小膨胀问题**。在工作流执行过程中，每个节点的输出都会追加到共享State中。如果State中包含完整的消息历史，随着节点数量增加，传入后续LLM节点的上下文长度会线性增长，在节点数超过15至20个的复杂工作流中可能突破模型的128K上下文窗口上限。解决方案是在关键节点后插入**State压缩节点**，调用LLM将历史消息摘要为简短的中间结论，再清空详细历史。

---

## 知识关联

**前置概念的衔接**：Agent规划与分解（Task Decomposition）提供了将复杂目标拆解为子任务的认知框架，但只描述"拆成什么"而不规定"如何编排执行顺序"——工作流编排正是将分解结果转化为可执行DAG的工程层。多Agent协作系统中的Orchestrator-Subagent模式对应工作流中的路由节点和子图概念：Orchestrator的决策逻辑可以被实现为条件边上的路由函数，每个Subagent对应DAG中的一个子图。提示链是工作流编排的特例：当DAG退化为无分支的线性链时，工作流编排与提示链等价。

**横向扩展**：工作流编排在工程实现上与流式处理框架（如Apache Airflow的DAG调度）共享"有向无环图+拓扑排序调度"的核心思想，区别在于Agent工作流的节点执行时间从毫秒到分钟不等且高度不确定，对动态调度和超时处理有更强的要求。掌握工作流编排后，可以进一步研究**状态机编排**（State Machine Orchestration）——它是DAG的超集，允许环形转移，适用于需要长期运行的Agent任务（如持续监控场景）。