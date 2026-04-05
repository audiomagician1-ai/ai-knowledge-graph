---
id: "agent-loop"
concept: "Agent循环(感知-推理-行动)"
domain: "ai-engineering"
subdomain: "agent-systems"
subdomain_name: "Agent系统"
difficulty: 6
is_milestone: false
tags: ["Agent"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---


# Agent循环（感知-推理-行动）

## 概述

Agent循环（Perception-Reasoning-Action Loop，简称PRA循环）是自主AI Agent持续运行的基本执行单元，描述Agent如何从外部环境获取信息、内部处理后生成决策、再将决策转化为可执行动作的完整一次迭代过程。与单次调用LLM不同，这一循环可以无限次重复，每一轮的输出会改变环境状态，从而影响下一轮的输入，形成真正意义上的闭环控制系统。

PRA循环的思想来源于控制论（Cybernetics）中Norbert Wiener在1948年提出的反馈回路理论，后经认知科学中的"感知-行动循环"（Perception-Action Cycle）演化而来。现代AI Agent框架（如LangChain的AgentExecutor、AutoGPT、OpenAI的Assistants API）均将这一循环作为运行时的核心调度机制。

该循环之所以关键，在于它解决了LLM"无状态、单轮输出"的根本局限——通过循环迭代，Agent能够处理跨步骤依赖的复杂任务，动态响应工具调用结果，并在中途根据新信息修正执行路径。一个需要调用搜索API、再汇总结果、再生成报告的任务，最少需要3次完整的PRA循环才能完成。

---

## 核心原理

### 感知阶段（Perception）：构建上下文窗口

感知阶段的本质是将Agent所处的"世界状态"序列化为LLM可消费的Token序列。这一阶段的输入来源通常包括四类：**用户消息**（原始指令）、**工具返回结果**（ToolMessage）、**历史对话记录**（Memory）、以及**系统提示词**（System Prompt）。

以OpenAI的消息格式为例，感知阶段的输出是一个结构化的消息列表：

```
[
  {role: "system", content: "You are a helpful assistant..."},
  {role: "user", content: "查询北京今天的天气"},
  {role: "assistant", content: null, tool_calls: [{id: "call_abc", function: "get_weather"}]},
  {role: "tool", tool_call_id: "call_abc", content: "晴，25°C"}
]
```

感知阶段的关键挑战是**上下文窗口溢出**：当循环轮次增加，历史消息累积，总Token数可能超过模型的上下文限制（如GPT-4o的128K Token上限）。因此感知阶段需要实施消息压缩或滑动窗口策略，这直接关联到Agent记忆系统的设计。

### 推理阶段（Reasoning）：LLM的决策生成

推理阶段是将感知阶段构建的上下文输入LLM，由模型输出下一步行动计划的过程。LLM的输出有且只有两种形式：**生成文本响应**（任务已完成，直接回答用户）或**生成工具调用指令**（task未完成，需要调用外部工具）。

ReAct框架（Reasoning + Acting）在这一阶段引入了显式的"思考链"（Thought），强制LLM在生成动作前输出推理过程，格式为：

```
Thought: 用户需要北京的天气，我需要调用天气API
Action: get_weather(city="Beijing")
```

这种显式推理将LLM的中间推断过程暴露出来，使得调试和可观测性成为可能。推理阶段的核心参数是**temperature**：生产环境中Agent的temperature通常设为0或0.1，以保证决策的确定性，避免因采样随机性导致循环行为不稳定。

### 行动阶段（Action）：执行与环境反馈

行动阶段由**Agent Runtime**（非LLM本身）执行推理阶段生成的指令。Runtime负责解析LLM输出中的工具调用请求、路由到对应的工具函数、执行并捕获返回值或异常，最后将执行结果封装为新的感知输入，**触发下一轮循环**。

行动阶段存在一个关键的**循环终止判断**：Runtime需要检测LLM的输出是否包含工具调用。若无工具调用，则判定本次任务完成，将最终文本响应返回用户，循环终止。若有工具调用，则执行工具后将结果注入消息列表，进入下一次PRA迭代。为防止无限循环，生产系统通常设置`max_iterations`参数（LangChain默认值为15次），超过阈值则强制终止并返回错误。

### 循环的时序与状态传递

一次完整的PRA循环可以用如下伪代码表达：

```python
messages = [system_prompt, user_message]
for step in range(max_iterations):
    response = llm.invoke(messages)          # 推理
    if not response.tool_calls:
        return response.content              # 循环终止
    messages.append(response)               # 保存Assistant消息
    for tool_call in response.tool_calls:
        result = execute_tool(tool_call)     # 行动
        messages.append(tool_result(result)) # 感知：注入结果
```

状态在循环轮次之间完全通过`messages`列表传递，这意味着Agent的"记忆"在默认情况下完全存储在上下文窗口中，这是In-Context Memory的典型实现。

---

## 实际应用

**数据分析Agent场景**：用户请求"分析上个季度销售数据并生成报告"。第1轮循环：感知到用户指令，推理决定调用`query_database(sql="SELECT...")`, 行动执行SQL返回5000行数据。第2轮：感知到数据库结果，推理决定调用`calculate_statistics(data=...)`，行动返回统计摘要。第3轮：感知到统计结果，推理判断信息足够，直接生成自然语言报告，循环终止。整个任务经历3次完整的PRA循环。

**错误恢复场景**：当行动阶段的工具调用返回异常（如API超时返回`{"error": "timeout"}`），这个错误信息会作为ToolMessage注入感知阶段。LLM在下一轮推理时可以"看到"这个错误，从而决定重试、切换备用工具或向用户报告失败。这种**错误信息的显式可见性**是PRA循环相比传统编排系统的核心优势，LLM不需要特殊的错误处理代码，仅凭感知到的错误文本即可生成恢复策略。

---

## 常见误区

**误区1：认为每轮循环都必须调用外部工具**。实际上，推理阶段的LLM完全可以在不调用任何工具的情况下完成任务——当模型判断已有信息足够回答问题时，会直接生成文本响应并终止循环。将"必须有工具调用"误认为循环继续的条件，会导致错误的循环逻辑设计。

**误区2：认为感知阶段只包含最新的用户消息**。许多初学者在手动实现Agent时只将最新用户消息传给LLM，而忽略了历史ToolMessage。这会导致LLM在推理时无法获知前几轮工具调用的结果，产生重复调用同一工具或逻辑矛盾的行为。完整的感知输入必须包含从系统提示到最新ToolMessage的**完整消息历史**。

**误区3：将PRA循环中的"推理"等同于Chain-of-Thought**。推理阶段的核心输出是"下一个动作决策"，CoT是提升推理质量的技术手段之一，但不是必须的。没有显式CoT的LLM调用（如直接输出Function Call JSON而不附带Thought文本）同样是合法的推理阶段，这在追求低延迟的生产环境中更为常见。

---

## 知识关联

**前置概念的延伸**：AI Agent概述中介绍的"自主性"在PRA循环中得到了具体化——自主性的实现机制正是循环内的迭代决策。ReAct框架直接对应推理阶段的显式Thought设计，理解ReAct的Thought-Action-Observation三元组后，能直接映射到PRA循环的三个阶段。

**后续概念的基础**：工具调用（Function Calling）是行动阶段的具体实现协议，规定了LLM如何以结构化JSON格式输出工具调用请求。Agent记忆系统解决感知阶段上下文窗口溢出问题，引入外部存储（向量数据库、摘要记忆）扩展PRA循环中消息列表的容量上限。Agent规划与分解在推理阶段引入多步任务分解，使单次推理能生成多轮循环的执行计划。多Agent协作系统将单个Agent的行动阶段扩展为"调用另一个Agent"，形成Agent嵌套的PRA循环结构。Agent可观测性（Debugging and Observability）直接作用于PRA循环的每个阶段边界，通过记录每轮的输入输出实现全链路追踪（如LangSmith对每次LLM调用和工具调用的span记录）。