---
id: "function-calling"
concept: "Function Calling"
domain: "ai-engineering"
subdomain: "llm-core"
subdomain_name: "大模型核心"
difficulty: 6
is_milestone: false
tags: ["LLM"]

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


# 函数调用（Function Calling）

## 概述

函数调用（Function Calling）是大语言模型的一种能力扩展机制，允许模型在推理过程中识别用户意图并生成结构化的函数调用请求，而非直接返回自然语言答案。这一机制由 OpenAI 于 2023 年 6 月随 `gpt-3.5-turbo-0613` 和 `gpt-4-0613` 版本正式推出，标志着大模型从单纯的文本生成器向可编程工具执行代理的转变。

Function Calling 的本质是模型学会了在特定上下文中输出符合预定义 JSON Schema 的结构化参数，而不是模型真正"调用"了某个函数。实际的函数执行发生在调用方（客户端代码）一侧，模型只负责决定调用哪个函数、传入什么参数。这种设计将模型的语义理解能力与外部系统的执行能力解耦，使得 LLM 可以操控数据库查询、API 请求、计算工具等任意外部能力。

该机制的重要性在于它解决了 LLM 的两个固有缺陷：知识截止日期限制与无法执行副作用操作。通过 Function Calling，模型可以在运行时获取实时天气、查询企业内部数据库、发送邮件，将静态的语言推理能力转变为动态的任务执行能力。

## 核心原理

### 工具定义与 JSON Schema 描述

在请求阶段，开发者需要向模型提供工具列表（`tools` 参数），每个工具以 JSON Schema 格式描述其名称、用途和参数结构。例如定义一个查询天气的函数：

```json
{
  "type": "function",
  "function": {
    "name": "get_current_weather",
    "description": "获取指定城市的实时天气信息",
    "parameters": {
      "type": "object",
      "properties": {
        "location": {"type": "string", "description": "城市名称，如北京"},
        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
      },
      "required": ["location"]
    }
  }
}
```

模型通过 `description` 字段理解何时应调用此函数，因此描述的质量直接影响模型的判断准确率。参数中的 `required` 字段告知模型哪些参数是必填的，`enum` 约束合法取值范围，这些 Schema 约束在模型的解码阶段通过受限采样（Constrained Decoding）强制执行。

### 模型响应格式与 finish_reason

当模型判断需要调用函数时，API 响应中的 `finish_reason` 字段值为 `"tool_calls"` 而非普通的 `"stop"`，消息内容结构如下：

```json
{
  "role": "assistant",
  "content": null,
  "tool_calls": [{
    "id": "call_abc123",
    "type": "function",
    "function": {
      "name": "get_current_weather",
      "arguments": "{\"location\": \"北京\", \"unit\": \"celsius\"}"
    }
  }]
}
```

注意 `arguments` 字段是一个 JSON 字符串而非对象，需要二次解析。每个 `tool_call` 有唯一的 `id`，后续返回执行结果时必须通过此 `id` 对应，防止多函数并行调用时的结果错乱。

### 多轮对话与结果回传机制

Function Calling 的完整流程是一个多轮交互过程，包含至少 4 个步骤：

1. **用户提问** → 携带 `tools` 定义发送至模型
2. **模型返回** `tool_calls` 请求（`finish_reason = "tool_calls"`）
3. **客户端执行**函数并获取真实结果
4. **将结果以 `role: "tool"` 消息追加**到对话历史，再次请求模型

第 4 步中，`tool` 角色的消息必须包含 `tool_call_id` 字段与步骤 2 中的 `id` 匹配。模型在收到工具执行结果后，才会生成最终自然语言回复。若跳过此回传步骤直接终止对话，模型无法完成从函数结果到用户答案的语义整合。

### 并行函数调用与 tool_choice 控制

自 `gpt-4-turbo` 起，模型支持在单次响应中返回多个 `tool_calls`，实现并行函数执行，将串行等待时间降低至单次最长任务的耗时。开发者可通过 `tool_choice` 参数控制模型行为：设为 `"auto"` 时模型自主决策，设为 `"required"` 时强制必须调用某个函数，设为具体函数名时强制调用指定函数（适用于需要确定性提取的场景）。

## 实际应用

**企业知识库问答**：将向量数据库的检索接口封装为函数 `search_knowledge_base(query: str, top_k: int)`，模型根据用户问题自动生成语义查询词并调用检索，再基于返回结果生成回答。这比直接在 prompt 中塞入全部文档更节省 token，且支持动态检索。

**结构化数据提取**：利用 `tool_choice: "required"` 强制模型以函数调用形式输出，将非结构化合同文本解析为 `extract_contract_info(party_a, party_b, amount, deadline)` 的参数，相比纯 JSON Mode 可以通过 `description` 字段为每个字段提供提取指引，准确率更高。

**智能体（Agent）任务规划**：在 ReAct 框架中，将计算器、代码执行器、网络搜索等能力注册为工具，模型在解决复杂问题时通过多轮 Function Calling 循环完成"思考-行动-观察"的推理链，最终汇总各步骤结果给出答案。

## 常见误区

**误区一：认为 `arguments` 输出总是合法 JSON**。实际上，在高温度采样或模型能力较弱时，`arguments` 字符串可能出现格式错误或字段幻觉（编造 Schema 中不存在的字段）。生产环境必须对 `arguments` 做 try/except 解析防护，并用 Pydantic 等工具对参数内容做二次校验，而不能假设模型的 Schema 遵从率为 100%。

**误区二：将 Function Calling 等同于工具调用（Tool Use）**。Function Calling 特指 OpenAI API 的具体接口实现（`tools` + `tool_calls` 字段），而 Anthropic Claude 使用 `tool_use` 消息块，Google Gemini 使用 `functionCall` / `functionResponse`。这些实现细节不同，但背后的机制相似。使用 LangChain 或 LlamaIndex 等框架可以抽象这些差异，但理解底层差异有助于排查跨平台兼容问题。

**误区三：认为 Function Calling 不消耗额外 token**。工具定义的 JSON Schema 会被注入到模型的系统 prompt 中，每个工具定义通常消耗 50-200 个 token。注册大量工具（超过 20 个）不仅增加 token 成本，还会导致模型在工具选择准确率上下降，此时应考虑动态工具注册（根据上下文只传入相关工具子集）。

## 知识关联

**前置概念关联**：GPT 与解码器模型的自回归生成机制是理解 Function Calling 工作方式的基础——模型通过 next-token prediction 逐词生成 `arguments` JSON，受限采样技术（Constrained Decoding）在词表层面过滤非法 token，保证输出符合 Schema 语法。结构化输出（JSON Mode）是 Function Calling 的轻量替代方案：JSON Mode 只保证输出是合法 JSON，不提供 Schema 校验和函数路由能力；Function Calling 在此基础上增加了多函数选择、参数语义对齐和对话状态管理，适用于需要与外部系统交互的场景。

**横向关联**：Function Calling 是构建 LLM Agent 的核心机制，ReAct、Plan-and-Execute 等 Agent 架构均依赖多轮 Function Calling 实现工具使用循环。RAG（检索增强生成）系统中，检索步骤可以通过 Function Calling 实现动态触发，相比静态检索更灵活。MCP（Model Context Protocol）是 2024 年 Anthropic 提出的工具调用标准化协议，旨在统一不同模型和工具之间的 Function Calling 接口规范，是该机制在工程标准化方向上的重要演进。