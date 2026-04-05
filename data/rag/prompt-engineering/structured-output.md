---
id: "structured-output"
concept: "结构化输出(JSON Mode)"
domain: "ai-engineering"
subdomain: "prompt-engineering"
subdomain_name: "Prompt工程"
difficulty: 4
is_milestone: false
tags: ["Prompt", "API"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 96.6
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


# 结构化输出（JSON Mode）

## 概述

结构化输出（JSON Mode）是一种强制大型语言模型将响应格式化为合法 JSON 字符串的技术手段。与普通文本输出相比，JSON Mode 通过约束模型的解码过程，确保每一个输出 token 序列在语法层面符合 JSON 规范，从而使下游系统可以直接调用 `JSON.parse()` 或等效方法解析结果，而无需额外的正则提取或异常处理。

JSON Mode 最早由 OpenAI 在 2023 年 11 月随 GPT-4 Turbo 的发布正式提出，随后 Anthropic（Claude 系列）、Google（Gemini 系列）以及开源框架 Outlines、Guidance 相继推出各自的实现方案。其技术背景是：早期 LLM 即使在 prompt 中要求输出 JSON，仍会以约 5%–15% 的概率产生格式错误（如末尾多余逗号、缺少引号），导致生产环境中的解析失败率过高，推动了专用 JSON Mode 的工程化落地。

在 AI 工程的 Prompt 工程层面，掌握 JSON Mode 的价值在于它直接打通"模型推理"与"程序逻辑"之间的接口。当输出用于填充数据库字段、驱动前端渲染或触发工具调用时，结构化输出将不确定性从"模型会不会输出合法格式"这一维度完全消除，使系统可靠性从 95% 级别提升至接近 100%。

---

## 核心原理

### 受限解码（Constrained Decoding）

JSON Mode 的底层机制并非简单地在 system prompt 中写"请输出 JSON"，而是在 token 采样阶段对词表施加掩码（logit masking）。在每一个解码步骤中，系统根据当前已生成的 JSON 片段维护一个有限状态自动机（FSM），只有在该状态下合法的下一个 token 才被赋予非负 logit，其余 token 的 logit 被设为 `-inf`。例如，当当前状态为"刚写完一个字符串值的右引号"时，只允许 `,`、`}` 或换行符等合法后继出现。这一方法由 Outlines 库（2023 年由 Brandon T. Willard 等人发表于 arXiv:2307.09702）系统化描述。

### Schema 约束与 Structured Outputs

比普通 JSON Mode 更进一步的是 **Structured Outputs**（OpenAI 于 2024 年 8 月推出）。它允许开发者传入一个 JSON Schema 对象，模型不仅需要输出合法 JSON，还必须严格遵循 schema 中定义的字段名、类型（`string`、`integer`、`array` 等）和 `required` 属性。调用方式如下：

```python
response = client.beta.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=[...],
    response_format=ResearchPaper,  # Pydantic BaseModel 子类
)
```

其中 `ResearchPaper` 是一个 Pydantic 模型，OpenAI SDK 会自动将其转换为 JSON Schema 并注入请求。相比于仅启用 JSON Mode（`response_format={"type": "json_object"}`），Structured Outputs 将字段级别的合规性也纳入约束，消除了"JSON 合法但字段缺失"的边缘情况。

### Prompt 设计对 JSON Mode 的影响

即使启用了受限解码，prompt 的写法仍然决定 JSON 内容的语义质量。关键实践包括：

- **在 system prompt 中明确声明目标 schema**：描述每个字段的含义和取值范围，例如 `"sentiment": "positive | negative | neutral"`，可将分类错误率降低约 30%（根据 OpenAI Cookbook 的内部测试数据）。
- **避免在 user message 中插入大段自由文本干扰**：当 user message 超过 2000 token 时，模型更容易在 JSON 值字段中插入额外的解释性文本，触发 schema 违规。
- **使用 `additionalProperties: false`**：在 JSON Schema 中禁止额外字段，防止模型"发明"未定义的键名。

---

## 实际应用

**信息抽取流水线**：给定一段医学文献摘要，要求模型抽取 `{ "drug_name": str, "trial_phase": int, "primary_endpoint": str, "p_value": float }` 四个字段。启用 Structured Outputs 后，`p_value` 字段会被强制解析为 float 类型，避免模型输出 `"p < 0.05"` 这类无法直接用于统计计算的字符串。

**前端动态表单生成**：电商后台要求模型根据商品描述生成 `{ "title": str, "price": number, "tags": string[], "in_stock": boolean }` 格式的商品卡片数据。JSON Mode 确保 `tags` 始终是数组而非逗号分隔的字符串，前端渲染逻辑无需做防御性类型检查。

**多步骤 Agent 的中间状态传递**：在 LangGraph 或 AutoGen 构建的多智能体系统中，每个节点的输出必须是可被下一个节点直接读取的结构体。使用 JSON Mode 配合固定 schema，可以将节点间的接口错误率从人工提示方案的约 8% 降至可忽略水平。

---

## 常见误区

**误区一：JSON Mode 等同于在 prompt 中说"请输出 JSON"**

两者有本质区别。纯 prompt 指令依赖模型的指令遵循能力，在长对话、高压缩 context 或模型能力较弱时会失效。JSON Mode 通过 logit masking 在解码层强制约束，即使 prompt 中完全不提"JSON"，输出也必然合法。混淆这两者会导致开发者误以为自己已经启用了结构化输出，实际上仍在依赖不可靠的软约束。

**误区二：JSON Mode 保证语义正确性**

JSON Mode 只保证语法合规，不保证值的含义正确。例如，schema 要求 `"rating": integer`，模型可能输出 `"rating": 999`，这是合法 JSON 且符合 integer 类型，但语义上可能超出业务允许的 1–5 分范围。语义校验需要在应用层额外使用 Pydantic 的 `Field(ge=1, le=5)` 等验证器，不能依赖 JSON Mode 本身完成。

**误区三：所有模型的 JSON Mode 行为一致**

不同提供商的实现差异显著。OpenAI 的 JSON Mode（`json_object`）不验证 schema，仅保证合法 JSON；而 Structured Outputs（`json_schema`）才进行 schema 级别约束。Anthropic Claude 的做法是通过 tool use 接口实现结构化输出，并无独立的"JSON Mode"开关。开源模型如 Llama-3 需借助 vLLM 的 `guided_json` 参数或 Outlines 库才能获得等效能力，默认推理不提供此功能。

---

## 知识关联

**前置概念**：学习 JSON Mode 需要理解提示词基础中的 system/user message 分工，因为 schema 描述通常放置于 system prompt，而待处理的输入内容位于 user message，两者混淆会导致模型将 schema 定义误认为待解析内容。

**后续概念——工具调用（Function Calling）**：Function Calling 是 JSON Mode 的自然延伸。在 Function Calling 中，模型不仅要输出符合 schema 的 JSON，还要在多个工具 schema 中选择调用哪一个并填充参数，本质上是在结构化输出之上叠加了"选择"和"路由"逻辑。JSON Mode 是理解 Function Calling 参数填充机制的直接基础——两者共享受限解码技术，区别在于 Function Calling 的 schema 由工具定义动态注入，而非由开发者在每次请求中手工指定。