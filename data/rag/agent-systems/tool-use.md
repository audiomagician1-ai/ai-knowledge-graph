---
id: "tool-use"
concept: "工具调用(Function Calling)"
domain: "ai-engineering"
subdomain: "agent-systems"
subdomain_name: "Agent系统"
difficulty: 6
is_milestone: false
tags: ["Agent", "API"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 82.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---



# 工具调用（Function Calling）

## 概述

工具调用（Function Calling）是大语言模型（LLM）的一种能力扩展机制，允许模型在生成回复过程中识别出需要调用外部函数的时机，输出结构化的函数调用请求（而非直接给出文本答案），再由宿主程序执行该函数并将结果返回给模型，最终由模型综合结果生成最终回复。这一机制将 LLM 从"纯文本问答引擎"升级为"可与外部系统交互的推理核心"。

Function Calling 由 OpenAI 于 2023 年 6 月随 GPT-4 与 GPT-3.5-turbo 的 API 更新正式发布，最初以 `functions` 参数形式提供，2023 年 11 月升级为更灵活的 `tools` 参数格式，支持并行调用多个工具（Parallel Function Calling）。此后 Anthropic（Claude）、Google（Gemini）、Mistral 等主流模型提供商相继跟进，工具调用逐渐成为生产级 Agent 系统的标准基础设施。

Function Calling 的核心价值在于：它给模型提供了一条**确定性的执行通道**。纯文本提示词无法保证模型按固定格式输出函数名和参数；Function Calling 通过在推理阶段对输出进行模式约束，使得函数名、参数名、参数类型均可被程序可靠解析，实现 LLM 与外部 API、数据库、代码解释器的可靠对接。

---

## 核心原理

### 工具描述的 JSON Schema 规范

每个工具在调用前必须以 JSON Schema 格式向模型声明其接口，包含三个必填字段：`name`（函数名）、`description`（自然语言描述，直接影响模型的工具选择决策）、`parameters`（参数的类型、枚举值、是否必填等约束）。以下是一个标准工具定义示例：

```json
{
  "type": "function",
  "function": {
    "name": "get_weather",
    "description": "获取指定城市的实时天气信息",
    "parameters": {
      "type": "object",
      "properties": {
        "city": { "type": "string", "description": "城市名称，如'北京'" },
        "unit": { "type": "string", "enum": ["celsius", "fahrenheit"] }
      },
      "required": ["city"]
    }
  }
}
```

`description` 字段的质量至关重要：模型依赖该描述来判断在何种用户意图下应触发此工具，措辞模糊的描述会导致工具被误触发或漏触发。

### 调用流程与消息角色

Function Calling 的完整交互涉及四种消息角色，按时序排列如下：

1. **user**：用户原始请求
2. **assistant**（含 `tool_calls` 字段）：模型决定调用工具，输出 `tool_call_id`、函数名、参数 JSON，**不输出最终文本**
3. **tool**：宿主程序执行函数后，以 `tool_call_id` 为键将结果注入上下文
4. **assistant**（纯文本）：模型读取工具返回结果，生成面向用户的最终回复

整个流程中，模型共被调用**两次**：第一次产生工具调用请求，第二次综合结果生成回答。若模型选择 `finish_reason: "stop"` 而非 `"tool_calls"`，则表示无需调用任何工具。

### 并行调用与顺序调用

OpenAI 从 `gpt-4-1106-preview` 开始支持在单次响应中输出**多个并行工具调用**（`tool_calls` 数组包含多项），允许宿主程序并发执行多个函数以节省延迟。例如同时查询三个城市天气，模型会在一次 API 调用中返回三个 `tool_call` 对象，宿主程序可并发发起三个 HTTP 请求。相比顺序调用，并行调用可将延迟从 `3T` 降低为接近 `T`（T 为单次工具执行时间）。若工具之间存在数据依赖（如"先查用户 ID，再用 ID 查订单"），则必须顺序执行，此时 Agent 循环会在两轮 LLM 调用之间穿插。

### 模型内部的工具选择机制

模型并非随机选择工具，而是通过微调阶段学习到的**工具路由能力**做决策。开发者可通过 `tool_choice` 参数干预：设为 `"auto"` 时模型自主选择；设为 `"required"` 时强制模型必须调用至少一个工具；设为 `{"type": "function", "function": {"name": "xxx"}}` 时强制指定工具。这一控制能力在构建确定性工作流时非常重要。

---

## 实际应用

**智能客服查单场景**：用户询问"我的订单 ORD-20241103 到哪了？"，Agent 识别到需要查询物流，调用 `query_order_status(order_id="ORD-20241103")`，物流系统返回 JSON 数据，模型将结构化数据转化为自然语言答复。整个过程对用户透明，无需用户了解 API 细节。

**数学计算与代码执行**：LLM 直接做浮点计算容易出错，通过定义 `calculate(expression: str)` 工具并后接 Python 解释器，可将计算精度从模型自身的约 95% 提升至 100%。这是 ChatGPT 的 Code Interpreter（Advanced Data Analysis）功能的底层机制之一。

**多工具 Agent 工作流**：一个财务分析 Agent 可同时注册 `search_web`、`query_database`、`generate_chart`、`send_email` 四个工具，模型根据用户请求自主规划调用顺序，无需开发者编写显式的 if-else 调度逻辑，Agent 循环（感知-推理-行动）中的"行动"层完全由 Function Calling 承载。

---

## 常见误区

**误区一：工具调用等同于让模型"执行"函数**
模型本身**不执行任何函数**，它只负责输出一段 JSON（函数名 + 参数），真正的执行发生在宿主程序中。模型无法访问网络、无法读写文件，所有副作用都由调用方代码负责。混淆这一点会导致开发者错误地认为模型有"主动能力"，从而忽视执行层的安全校验。

**误区二：`description` 不重要，参数定义才是关键**
实验数据显示，将 `description` 从"查天气"改为"获取指定城市当前的温度、湿度和风速"后，模型在相关 Query 上的工具调用准确率可提升 10–20 个百分点。模型在 `tool_calls` 决策阶段重度依赖描述语义，而非仅靠参数结构推断。

**误区三：Function Calling 与 JSON Mode 可以互换**
JSON Mode 只保证输出是合法 JSON，但不约束字段名和结构；Function Calling 则通过 Schema 严格约束输出的字段名、类型和必填项，并触发专属的 `finish_reason: "tool_calls"` 状态。JSON Mode 无法让模型"决定是否调用"，而 Function Calling 本质上是模型具备工具路由推理能力的体现。

---

## 知识关联

**前置概念衔接**：Function Calling 是 Agent 循环（感知-推理-行动）中"行动"步骤的具体实现方式——推理阶段决定调用哪个工具、行动阶段输出 `tool_calls` JSON。结构化输出（JSON Mode）是 Function Calling 的基础能力子集：后者在 Schema 约束上更严格，并额外引入了工具路由决策逻辑。

**后续概念延伸**：MCP（Model Context Protocol）将 Function Calling 的工具注册与发现标准化为跨进程协议，使工具服务可以独立部署和动态注册，解决大规模 Agent 系统中工具管理的碎片化问题。AutoGen 框架在 Function Calling 之上构建了多 Agent 协作层，每个 Agent 持有不同工具集，通过消息传递协同完成复杂任务。浏览器 Agent 和代码生成 Agent 则分别将 `browser_click/type` 系列工具和 `execute_code` 工具作为核心行动接口，Function Calling 是其与 LLM 对接的标准通道。