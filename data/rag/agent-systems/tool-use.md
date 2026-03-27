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
quality_tier: "B"
quality_score: 51.4
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.4
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 工具调用（Function Calling）

## 概述

工具调用（Function Calling）是一种让大语言模型（LLM）在对话过程中主动声明"我需要调用某个外部函数"的机制，模型本身并不执行该函数，而是以结构化 JSON 格式输出函数名称与参数，由调用方（宿主程序）完成实际执行并将结果回传给模型。这一机制首次以正式 API 形式出现于 2023 年 6 月 OpenAI 对 `gpt-3.5-turbo-0613` 和 `gpt-4-0613` 的更新，标志着 LLM 从纯文本生成向可编程行为代理的关键转变。

Function Calling 的重要性在于它解决了 LLM 两个根本缺陷：知识截止日期导致的信息过时，以及无法执行精确计算或与外部系统交互。通过让模型决定"何时调用什么工具、传入哪些参数"，Agent 系统得以将语言推理能力与确定性程序逻辑结合，实现真正的感知-推理-行动闭环。

---

## 核心原理

### 工具描述的 JSON Schema 定义

开发者在调用 API 时需要传入 `tools` 参数，每个工具是一个符合 JSON Schema 规范的对象，包含三个必填字段：`name`（函数名）、`description`（自然语言描述，模型依赖它判断何时使用该工具）、`parameters`（参数的类型、约束与必填项）。模型在 function calling 的正确性上高度依赖 `description` 的质量——描述含糊会导致模型在不恰当时机触发工具，或传入错误类型的参数。

```json
{
  "type": "function",
  "function": {
    "name": "get_weather",
    "description": "获取指定城市的当前天气，仅支持实时查询，不支持历史数据",
    "parameters": {
      "type": "object",
      "properties": {
        "city": {"type": "string", "description": "城市名，如'北京'"},
        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
      },
      "required": ["city"]
    }
  }
}
```

### 模型输出与执行循环

当模型决定调用工具时，API 响应中的 `finish_reason` 字段值为 `"tool_calls"` 而非 `"stop"`，消息体的 `tool_calls` 数组包含 `id`、`function.name` 和 `function.arguments`（字符串化的 JSON）。宿主程序需将此工具调用结果以 `role: "tool"` 消息连同对应的 `tool_call_id` 追加到对话历史，再次发起请求，模型才能基于工具返回值生成最终回答。整个 **LLM → 工具调用声明 → 外部执行 → 结果回传 → LLM** 的循环，正是 ReAct（Reasoning + Acting）模式的技术实现。

### 并行工具调用与顺序依赖

GPT-4o 及 Claude 3.5 等现代模型支持 **并行工具调用**（Parallel Tool Calls）：单次响应中 `tool_calls` 数组可包含多个条目，宿主程序可并发执行这些函数以减少延迟。但当工具 B 的输入依赖工具 A 的输出时（如先查询用户 ID，再用 ID 查询订单），模型会自动拆分成两轮串行调用。开发者需要在系统设计时区分"可并行"与"有依赖"的工具组合，以避免不必要的串行等待。

### 强制调用与工具选择控制

OpenAI API 的 `tool_choice` 参数提供三种模式：`"auto"`（模型自主决定，默认）、`"none"`（禁止工具调用）、`{"type": "function", "function": {"name": "..."}}` （强制调用指定函数）。强制调用模式常用于数据提取场景——将 JSON Schema 当作输出格式约束，确保模型返回严格符合业务数据结构的内容，这与 JSON Mode 的区别在于 Function Calling 能同时携带参数语义。

---

## 实际应用

**实时信息检索 Agent**：将搜索引擎 API 封装为 `web_search(query: str, max_results: int)` 工具，当用户询问"今天比特币价格"时，模型触发工具调用并将返回的实时数据整合进回答，彻底规避训练数据截止问题。

**结构化数据提取**：在客服工单处理场景中，定义 `extract_order_info(order_id, issue_type, priority)` 函数并将 `tool_choice` 设为强制调用，即可将用户非结构化文字可靠转换为数据库可直接写入的字段，错误率相比提示词 JSON 提取降低约 40%（实测依赖模型版本）。

**多工具协作的差旅预订 Agent**：一次用户请求触发如下工具链：① `search_flights` → ② `check_hotel_availability` → ③ `get_exchange_rate` 并行执行 → ④ `book_itinerary`（依赖前三步结果）串行执行。整个过程模型自主编排，宿主程序仅负责路由与执行，业务逻辑由模型的推理能力驱动。

---

## 常见误区

**误区一：认为 Function Calling 等同于 JSON Mode**。JSON Mode 仅保证模型输出合法 JSON 字符串，但不约束字段名称和结构；而 Function Calling 通过 JSON Schema 强约束输出结构，且对话历史中需要插入 `tool` 角色消息，两者的 token 消耗模式和对话状态管理完全不同，不可互换使用。

**误区二：认为模型"执行"了函数**。模型实际上只是生成了一段描述调用意图的 JSON 文本，函数的真实执行、网络请求、数据库查询等操作全部由宿主程序完成。这意味着工具执行中的任何错误（超时、权限不足、参数校验失败）需要由宿主程序捕获并以包含错误信息的 `tool` 消息回传给模型，让模型自行决定重试或告知用户。

**误区三：工具越多越好**。将超过 20 个工具一次性注入 `tools` 列表会显著增加上下文 token 消耗，且实验表明当工具数量超过 15 个时，`gpt-4-turbo` 出现工具选择错误的概率明显上升。工程实践中推荐采用"工具路由"策略：先由一个分类模型选取与当前任务相关的 3-5 个工具，再传入主模型。

---

## 知识关联

Function Calling 的先决知识是 **结构化输出（JSON Mode）**——理解 JSON Schema 类型系统（`string`、`integer`、`enum`、`array`、`$ref`）是正确定义工具参数的前提；以及 **Agent 循环（感知-推理-行动）**，Function Calling 正是"行动"步骤在 LLM API 层面的具体实现形式，`tool_calls` 消息对应"行动声明"，工具执行结果回传对应"感知更新"。

在此基础上，**MCP（Model Context Protocol）** 将 Function Calling 的工具定义和调用协议标准化为跨模型、跨框架的开放规范，解决多厂商工具描述格式不统一的问题；**AutoGen 框架** 则在 Function Calling 之上构建多 Agent 协作体系，允许多个 LLM 实例通过工具调用相互委托任务；**浏览器 Agent** 和 **代码生成 Agent** 是 Function Calling 的垂直特化方向，前者将浏览器操作（点击、截图、填表）封装为工具集，后者将代码执行环境暴露为 `execute_python(code: str)` 形式的工具接口。