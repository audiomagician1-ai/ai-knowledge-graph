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
content_version: 1
quality_tier: "A"
quality_score: 76.6
generation_method: "ai-batch-v1"
unique_content_ratio: 1.0
last_scored: "2026-03-21"
sources: []
---
# Function Calling

## 概述

Function Calling（函数调用）是 LLM 的一种结构化输出能力，允许模型根据用户意图生成符合预定义 JSON Schema 的函数调用请求，难度等级 6/9。它是 LLM 从"文本生成器"进化为"行动执行者"的关键桥梁，也是 Agent 系统实现 Tool Use 的底层机制。

本概念建立在 LLM 推理能力之上，与 Agent 系统、Tool Use、Prompt 工程密切关联。

## 核心原理

### 工作流程

```
用户: "北京今天天气怎么样？"

                ┌──────────────────┐
                │      LLM         │
                │                  │
  System Prompt │  可用函数:        │
  + 函数定义 ──→│  1. get_weather   │
  + 用户消息    │  2. search_web    │
                │  3. send_email    │
                │                  │
                │  分析意图...      │
                │  选择函数...      │
                │  生成参数...      │
                └────────┬─────────┘
                         │
                         ▼
            {
              "function": "get_weather",
              "arguments": {
                "city": "北京",
                "date": "today"
              }
            }
                         │
                         ▼
              应用层执行真实 API 调用
                         │
                         ▼
              将结果返回 LLM 生成自然语言回复
```

### 函数定义（OpenAI 格式）

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定城市的天气信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称，如'北京'、'上海'"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "温度单位"
                    }
                },
                "required": ["city"]
            }
        }
    }
]
```

### 多轮函数调用

```
Turn 1: User → LLM
  "帮我查一下北京和上海的天气，然后对比一下"

Turn 2: LLM → App (并行调用)
  [
    {"function": "get_weather", "args": {"city": "北京"}},
    {"function": "get_weather", "args": {"city": "上海"}}
  ]

Turn 3: App → LLM (返回结果)
  [
    {"role": "tool", "content": "北京: 晴, 12°C"},
    {"role": "tool", "content": "上海: 多云, 18°C"}
  ]

Turn 4: LLM → User
  "北京今天晴天 12°C，上海多云 18°C。上海比北京暖和 6 度..."
```

## 关键技术

### 训练方法

模型的 Function Calling 能力通过 Supervised Fine-Tuning 获得：

1. **数据构造**: 大量 (用户意图, 函数定义, 正确调用) 三元组
2. **格式训练**: 模型学会在特定 token 后输出 JSON 格式
3. **参数提取**: 模型学会从自然语言中提取参数值并正确填充类型

### tool_choice 控制

```python
# 自动决定是否调用函数（默认）
response = client.chat.completions.create(
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

# 强制调用某个函数
tool_choice={"type": "function", "function": {"name": "get_weather"}}

# 禁止调用函数
tool_choice="none"

# 强制调用任意一个函数
tool_choice="required"
```

### Structured Output (JSON Mode)

Function Calling 的泛化形式——强制输出符合特定 JSON Schema 的结构化数据：

```python
# OpenAI Structured Output
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "分析这篇文章的情感"}],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "sentiment_analysis",
            "schema": {
                "type": "object",
                "properties": {
                    "sentiment": {"enum": ["positive", "negative", "neutral"]},
                    "confidence": {"type": "number"},
                    "keywords": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["sentiment", "confidence"]
            }
        }
    }
)
```

## 实际应用

### 典型使用场景

| 场景 | 函数示例 | 说明 |
|:---|:---|:---|
| 数据查询 | `query_database(sql)` | 自然语言转数据库查询 |
| API 集成 | `send_email(to, subject, body)` | 操作外部服务 |
| 代码执行 | `run_python(code)` | 数学计算、数据处理 |
| 多步推理 | 链式调用多个函数 | Agent 任务分解 |

### 安全注意事项

```
⚠️ 关键安全原则:
1. 永远不要直接执行模型生成的代码/SQL — 必须沙箱化
2. 函数调用结果必须经过验证 — 模型可能幻觉参数
3. 敏感操作(删除/支付)必须人工确认
4. 限制可用函数范围 — 最小权限原则
5. 防范 Prompt 注入 — 用户输入可能操纵函数选择
```

## 常见误区

1. **认为 LLM 真的"调用"了函数**: LLM 只是生成 JSON 描述，真正的执行在应用层
2. **函数描述不够精确**: 描述模糊导致模型选错函数或参数错误
3. **忽略错误处理**: 函数执行失败时未将错误信息反馈给模型
4. **过多函数定义**: 函数太多会消耗 context window 并降低选择准确率（建议 <20）

## 与相邻概念关联

- **前置**: LLM 推理、Prompt 工程 — 理解模型如何理解指令
- **下游**: Agent Loop — Function Calling 是 Agent 执行动作的核心机制
- **下游**: Tool Use — Function Calling 的 Agent 层面抽象
- **互补**: Structured Output — Function Calling 的泛化，适用于任意 JSON 输出
- **进阶**: MCP Protocol — 标准化的 Tool 注册与调用协议
