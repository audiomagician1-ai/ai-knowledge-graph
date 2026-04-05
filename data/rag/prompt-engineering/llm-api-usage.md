---
id: "llm-api-usage"
concept: "LLM API调用(OpenAI/Claude)"
domain: "ai-engineering"
subdomain: "prompt-engineering"
subdomain_name: "Prompt工程"
difficulty: 4
is_milestone: false
tags: ["API"]

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


# LLM API调用（OpenAI/Claude）

## 概述

LLM API调用是通过HTTP请求与大语言模型服务交互的标准化接口方式，开发者无需自行部署模型即可获得GPT-4、Claude 3等模型的推理能力。OpenAI于2020年6月随GPT-3发布了首个商业化LLM API，随后Anthropic在2023年推出Claude API，两者共同确立了当前LLM API的基本范式——以JSON格式传递对话历史，接收流式或完整的文本响应。

OpenAI API与Claude API在接口设计上存在明显差异，但都遵循RESTful原则。OpenAI采用`/v1/chat/completions`端点，消息结构使用`role`（system/user/assistant）和`content`字段；Claude API使用`/v1/messages`端点，且将系统提示词从消息列表中独立为顶层`system`参数，这一设计差异直接影响提示词工程的实现方式。掌握两者的API调用不仅是构建AI应用的基础操作，更是理解模型行为、控制生成质量、管理成本的关键技能。

## 核心原理

### 请求结构与认证机制

两个API均通过HTTP Header传递API密钥进行身份验证。OpenAI使用`Authorization: Bearer sk-...`格式，Claude使用`x-api-key: sk-ant-...`加上`anthropic-version: 2023-06-01`版本头（此版本头为必填项，缺失会导致400错误）。请求体的核心参数包括：`model`（指定模型版本如`gpt-4o`或`claude-3-5-sonnet-20241022`）、`messages`（对话历史数组）、`max_tokens`（最大输出token数）。

OpenAI的最小可运行请求示例：
```json
{
  "model": "gpt-4o",
  "messages": [
    {"role": "system", "content": "你是助手"},
    {"role": "user", "content": "你好"}
  ],
  "max_tokens": 100
}
```

Claude的等效请求需将系统提示词提取到顶层：
```json
{
  "model": "claude-3-5-sonnet-20241022",
  "system": "你是助手",
  "messages": [{"role": "user", "content": "你好"}],
  "max_tokens": 100
}
```

### 响应格式与流式输出

两个API的响应结构不同，处理时需分别解析。OpenAI返回的文本位于`response.choices[0].message.content`，token用量在`response.usage`中包含`prompt_tokens`、`completion_tokens`、`total_tokens`三个字段。Claude的响应文本位于`response.content[0].text`，token统计字段名为`input_tokens`和`output_tokens`（注意字段命名与OpenAI不同）。

流式输出（Streaming）通过设置`"stream": true`启用，服务端返回`text/event-stream`格式的Server-Sent Events。OpenAI每个事件的增量文本在`delta.content`中，Claude在`delta.text`中，且Claude的流式事件类型更丰富，包括`content_block_start`、`content_block_delta`、`message_delta`等五种事件类型，需逐一处理以正确拼接完整响应。

### 多轮对话的状态管理

LLM API本身是**无状态的**——每次调用必须将完整的对话历史包含在`messages`数组中，服务端不保存任何会话状态。这意味着实现10轮对话时，第10次请求需携带前9轮的全部消息。对话历史累积会导致`prompt_tokens`线性增长，当总token数超过模型上下文窗口（GPT-4o为128K tokens，Claude 3.5 Sonnet为200K tokens）时，API会返回`context_length_exceeded`错误。

管理多轮对话的常见策略是维护一个消息列表，每次用户输入后追加`{"role": "user", "content": ...}`，收到响应后追加`{"role": "assistant", "content": ...}`。Python的`openai`官方库（1.0.0+版本，2023年11月重构了客户端API）和`anthropic`库都封装了这一逻辑，但底层仍是每次发送完整历史。

### 错误处理与重试策略

两个API都存在速率限制（Rate Limit），OpenAI按`TPM`（每分钟token数）和`RPM`（每分钟请求数）双维度限制，超限返回HTTP 429状态码。推荐的重试策略是指数退避（Exponential Backoff）：首次重试等待1秒，第二次2秒，第三次4秒，最多重试3次。网络超时建议将`timeout`设置为30-60秒，因为大型模型的首个token延迟（TTFT，Time To First Token）可达数秒。

## 实际应用

**构建客服问答系统**：将产品文档作为`system`提示词注入，用户问题作为`user`消息，通过维护`messages`列表实现多轮追问。使用Claude API时，可将长篇产品手册（最多约150,000词）放入`system`字段，利用其200K上下文窗口优势，避免RAG（检索增强生成）的额外复杂性。

**批量文本处理**：对于需要处理1000条文本分类任务的场景，可利用OpenAI的Batch API（2024年4月上线），以`/v1/batches`端点提交JSONL文件，成本降低50%，但需接受最长24小时的异步处理延迟。同步API适合实时场景，Batch API适合离线处理。

**函数调用（Function Calling）**：OpenAI的`tools`参数和Claude的`tools`参数支持结构化输出，通过JSON Schema定义函数签名，模型可输出结构化的函数调用请求而非自由文本，这是构建Agent工具调用链的核心机制。

## 常见误区

**误区一：认为设置相同参数两个API行为完全一致**。`temperature=1.0`在OpenAI和Claude中的实际采样行为不同，因为两者底层的温度缩放公式应用于不同阶段。Claude的`temperature`默认值为1.0，而GPT-4系列默认为1.0，但两者在`temperature=0`时的确定性程度也存在微小差异，不能假设跨平台结果可互换。

**误区二：将API密钥硬编码在代码中**。API密钥一旦提交至公开代码仓库，通常在30秒内就会被自动扫描工具（如GitHub Secret Scanning）检测，OpenAI和Anthropic均会自动撤销泄露的密钥。正确做法是通过环境变量（`os.environ.get("OPENAI_API_KEY")`）或`.env`文件（配合`python-dotenv`库）传递密钥。

**误区三：忽略`max_tokens`参数会导致响应被截断**。OpenAI的`max_tokens`限制仅针对**输出**tokens，而Claude的`max_tokens`是**必填参数**（不设置直接报错），且Claude 3系列的默认最大输出为4096 tokens，若任务需要更长输出（最高支持8192 tokens for Claude 3.5）必须显式设置。

## 知识关联

本文涉及的`temperature`参数仅作了基本介绍，**Temperature与采样策略**这一后续主题将深入分析`top_p`、`top_k`（Claude独有）以及`frequency_penalty`等参数对输出分布的精确影响。`prompt_tokens`计费逻辑引出**Token经济与成本优化**，需要理解如何用tiktoken库（OpenAI）或Claude的token计数API精确预估成本。Function Calling机制是**AI Agent概述**的直接前置技术，Agent的工具调用循环本质上是多次API调用的编排。而掌握两个主流API的标准化调用方式，也是进行**LLM评估基准**测试的技术基础——评估框架（如EleutherAI的lm-evaluation-harness）正是通过标准化API接口对模型进行批量推理测评的。