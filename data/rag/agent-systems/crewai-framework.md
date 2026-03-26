---
id: "crewai-framework"
concept: "CrewAI框架"
domain: "ai-engineering"
subdomain: "agent-systems"
subdomain_name: "Agent系统"
difficulty: 6
is_milestone: false
tags: ["Agent", "工具"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.452
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# CrewAI框架

## 概述

CrewAI是由João Moura于2023年底发布的开源多Agent协作框架，基于Python构建，专门设计用于协调多个具有明确角色分工的AI Agent共同完成复杂任务。与AutoGen的对话驱动模式不同，CrewAI采用"Crew（团队）"的隐喻，将Agent组织成具有层级结构的工作团队，每个Agent被赋予明确的`role`、`goal`和`backstory`三元组属性，这种设计使Agent的行为更具一致性和可预测性。

CrewAI在GitHub上发布后迅速获得超过20,000颗星，成为2024年增长最快的Agent框架之一。其核心价值在于提供了一套声明式的任务编排接口：开发者无需手工管理Agent之间的消息传递逻辑，而是通过定义`Crew`、`Agent`、`Task`三个核心对象来描述协作结构，框架自身负责调度执行。CrewAI底层默认集成LangChain的工具生态，同时支持直接接入OpenAI、Anthropic等主流LLM提供商。

## 核心原理

### 三层抽象结构

CrewAI的整个执行体系由三个核心类构成：`Agent`、`Task`和`Crew`。

**Agent**定义了一个智能执行单元，其构造参数包括：
- `role`：Agent的职位名称（如"Senior Data Analyst"）
- `goal`：该Agent的工作目标（单句描述）
- `backstory`：注入System Prompt的背景故事，用于塑造Agent的推理风格
- `tools`：该Agent可调用的工具列表
- `llm`：指定底层语言模型，默认使用`gpt-4`

**Task**定义了一个具体的执行任务，包含`description`（任务描述）、`expected_output`（预期输出格式）和`agent`（负责该任务的Agent）三个必填字段。Task支持通过`context`参数声明依赖关系，指定某个Task需要等待另一个Task的输出结果作为上下文。

**Crew**是顶层调度器，接收`agents`列表和`tasks`列表，并通过`process`参数指定执行流程。

### 两种执行流程模式

CrewAI提供两种`Process`模式：

**Sequential（顺序模式）**：任务按`tasks`列表的顺序依次执行，前一个Task的输出自动作为后续Task的上下文。这是最简单的模式，适合流水线型工作流。

**Hierarchical（层级模式）**：Crew会自动创建一个`Manager Agent`，该Manager使用LLM动态决定任务分配给哪个Agent、何时执行，以及是否需要重新分配。使用此模式必须在`Crew`初始化时设置`manager_llm`参数指定Manager使用的模型。层级模式等价于ReAct（Reasoning + Acting）框架在多Agent场景下的扩展。

### 工具集成与记忆机制

CrewAI的工具继承自LangChain的`BaseTool`，但也提供了自己的`@tool`装饰器，一个典型的自定义工具定义如下：

```python
from crewai_tools import tool

@tool("Search Internet")
def search_tool(query: str) -> str:
    """Search the internet for information about a given query."""
    return search_api.run(query)
```

CrewAI支持三种记忆类型：**Short-term Memory**（基于RAG的单次Crew执行内上下文记忆）、**Long-term Memory**（跨多次执行的持久化存储，默认使用SQLite）、**Entity Memory**（专门存储实体信息的结构化记忆）。开启记忆功能只需在`Crew`初始化时设置`memory=True`。

### Agent执行内部循环

每个CrewAI Agent在执行Task时，内部运行一个标准的ReAct循环：`Thought → Action → Observation → Thought...`，直到Agent输出`Final Answer`。CrewAI在此基础上增加了`max_iter`参数（默认值为15次迭代）限制单个Task的最大推理步骤数，以及`max_execution_time`参数控制总执行时间上限，避免Agent陷入无限循环。

## 实际应用

**内容生产流水线**：一个典型的CrewAI内容团队包含三个Agent——`ResearchAgent`（负责联网搜索收集信息）、`WriterAgent`（负责将研究报告改写为文章）、`EditorAgent`（负责校对和优化文章质量）。三个Task通过Sequential流程串联，整个Crew可以在10-15分钟内完成一篇有信源支撑的技术文章草稿。

**代码审查自动化**：使用层级模式，Manager Agent接收一个Pull Request的diff内容，动态将安全漏洞检查分配给`SecurityReviewerAgent`，将代码规范检查分配给`CodeStyleAgent`，将业务逻辑验证分配给`LogicReviewerAgent`，最终汇总各Agent输出生成统一的审查报告。

**市场调研报告生成**：CrewAI在金融和咨询场景中被广泛使用，典型配置是5-7个专业Agent分别负责竞品分析、市场规模估算、SWOT分析等子任务，利用`context`依赖机制确保后续分析能获取前期研究的结论。

## 常见误区

**误区一：认为`backstory`只是装饰性文本**。实际上`backstory`直接注入每次LLM调用的System Prompt，它决定了Agent在模糊情况下的推理倾向。例如，一个`backstory`描述为"你是一个极度谨慎的风控分析师"的Agent，在遇到信息不足时会主动声明不确定性而非猜测，而一个描述为"你是一个创意写手"的Agent则会倾向于补全细节。忽视`backstory`的精心设计会导致Agent行为不稳定。

**误区二：认为层级模式（Hierarchical）一定优于顺序模式（Sequential）**。层级模式的Manager Agent本身也会消耗大量Token进行动态决策，对于步骤固定、流程清晰的任务，Sequential模式的总Token消耗通常比Hierarchical模式低30%-50%，且执行结果更稳定可复现。只有任务流程需要动态调整时才应选择层级模式。

**误区三：将CrewAI的`Task`与AutoGen的对话轮次等同**。AutoGen的多Agent协作以对话消息为基本单元，Agent之间通过消息历史共享上下文；而CrewAI的`Task`是一个完整的工作单元，拥有独立的执行上下文和明确的输出规格。一个CrewAI Task在内部可能包含十多轮LLM调用（ReAct循环），对外表现为单一的结构化输出，这与AutoGen中每条消息都对外可见的设计哲学截然不同。

## 知识关联

CrewAI的角色分工设计直接扩展了多Agent协作系统中的任务分解原则，将抽象的"Agent专业化"概念具体化为`role/goal/backstory`三元组的声明式接口。理解AutoGen的`ConversableAgent`和群聊（GroupChat）机制有助于对比CrewAI中Manager Agent的动态调度与AutoGen的`GroupChatManager`之间的设计差异——前者依赖单一Manager的LLM推理，后者依赖预设的发言顺序规则或`speaker_selection_method`函数。

在学习Agent Frameworks Comparison时，需要重点评估CrewAI与AutoGen、LangGraph的适用场景边界：CrewAI的声明式设计使其在团队协作型任务中代码简洁度最高，但其执行流程的可控性不如LangGraph的有向图模型；AutoGen在需要复杂多轮对话协商的场景下更具优势。CrewAI的`Process.Hierarchical`模式与LangGraph的条件边（conditional edges）本质上都是解决动态任务分配问题，但实现机制完全不同，这是框架比较研究的核心议题之一。