---
id: "prompt-optimization"
concept: "提示词自动优化(DSPy)"
domain: "ai-engineering"
subdomain: "prompt-engineering"
subdomain_name: "Prompt工程"
difficulty: 7
is_milestone: false
tags: ["Prompt"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 46.6
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

# 提示词自动优化（DSPy）

## 概述

DSPy（Declarative Self-improving Language Programs）是由斯坦福大学 Omar Khattab 等人于2023年提出的框架，其核心创新在于**将提示词工程从手工编写转变为可编译的程序**。传统提示词工程要求人工反复调试 prompt 措辞，而 DSPy 将语言模型调用抽象为带有输入/输出签名的模块，由优化器（Optimizer）自动搜索最优的提示词或少样本示例。

DSPy 的设计哲学源于机器学习编译器的思想：开发者只需描述"做什么"（声明式），框架负责"怎么做"（优化策略）。用户定义一个 `Signature`（如 `question -> answer`）和评估指标（如答案准确率），DSPy 的 `Teleprompter`（即优化器）会在给定训练集上迭代生成候选提示词，并基于指标选择最优方案。这一过程类似于神经网络的反向传播，但作用对象是自然语言指令而非模型权重。

该框架的重要性在于它解决了**提示词脆弱性**问题：当底层 LLM 版本升级（如从 GPT-3.5 切换到 GPT-4o）或任务分布变化时，手工提示词往往大幅失效，而 DSPy 可自动重新编译以适应新模型，无需人工重写。

---

## 核心原理

### Signature：输入/输出声明式契约

DSPy 中的 `Signature` 是程序与 LLM 之间的接口定义，形如：

```python
class GenerateAnswer(dspy.Signature):
    """根据上下文回答问题"""
    context: str = dspy.InputField()
    question: str = dspy.InputField()
    answer: str = dspy.OutputField(desc="通常为1-5个词")
```

每个字段可附带 `desc` 描述，DSPy 编译器会将这些描述转化为 prompt 中的指令说明。Signature 本身不包含任何具体措辞，优化前后的 prompt 文本由编译过程决定，而非开发者手写。

### 内置模块：Predict、ChainOfThought、ReAct

DSPy 提供多种预置模块，每种模块对应不同的推理范式：

- **`dspy.Predict`**：直接从 Signature 生成输出，对应零样本调用。
- **`dspy.ChainOfThought`**：在 Signature 基础上自动插入 `rationale` 字段，强制模型先生成推理链再给出答案，这正是思维链（CoT）的自动化版本，但 CoT 的具体措辞由优化器而非人工决定。
- **`dspy.ReAct`**：实现 Reason+Act 循环，内置工具调用逻辑，参数 `max_iters` 控制最大循环次数。

模块可嵌套组合，构成有向无环图（DAG）式的推理流水线，DSPy 的优化器能同时优化图中所有节点的提示词。

### Teleprompter（优化器）工作机制

DSPy 的优化器统称 `Teleprompter`，目前主要包括以下几种：

1. **`BootstrapFewShot`**：使用教师模型（可以是同一 LLM）在训练集上生成带标注的示例轨迹，从中筛选出满足评估指标的轨迹作为少样本示例注入 prompt。筛选标准由用户提供的 `metric` 函数决定，例如 `lambda pred, gold: pred.answer == gold.answer`。

2. **`MIPRO`（Multi-prompt Instruction PRoposal Optimizer）**：通过贝叶斯优化在离散指令空间中搜索，每次迭代生成新的指令候选，并在验证集上评分，最终选出帕累托最优的指令组合。MIPRO 的搜索预算通过 `num_candidates` 和 `num_trials` 两个参数控制。

3. **`BootstrapFinetune`**：将优化过程延伸至模型权重层面，把 DSPy 生成的高质量轨迹转化为微调数据集，对较小的本地模型（如 LLaMA-3 8B）进行 SFT（监督微调），实现从提示词优化到模型优化的统一流程。

优化过程中需要一个可微分的**评估指标**（metric），该指标不一定是可微函数，因为 DSPy 使用的是基于采样的黑盒优化，而非梯度下降，因此整数准确率、F1 分数等离散指标均可使用。

---

## 实际应用

### 多跳问答（Multi-hop QA）

在 HotPotQA 数据集上，使用 DSPy 构建的多跳检索增强问答系统，经过 `BootstrapFewShot` 优化后，相较于手工编写的 CoT 提示词，答案精确匹配率（EM）提升约 **10-15 个百分点**（具体数值取决于基础模型）。系统由两个串联模块组成：第一个 `dspy.ChainOfThought` 模块分解子问题，第二个模块基于检索结果综合答案，优化器同时调整两个模块的少样本示例。

### 代码生成流水线的自动提示词调整

在切换基础模型时（如从 `gpt-4-turbo` 切换至 `claude-3-sonnet`），已有 DSPy 程序只需在新模型上重新调用 `compile()` 方法，即可在无需人工干预的情况下为新模型生成适配的提示词。这对于需要同时维护多个 LLM 后端的企业应用尤为关键。

### 结合断言（Assertion）实施硬约束

DSPy 支持在模块中嵌入 `dspy.Assert` 语句，例如：

```python
dspy.Assert(len(pred.answer.split()) <= 5, "答案不得超过5个词")
```

若断言失败，DSPy 会自动将错误反馈注入上下文并重试（最多重试次数由 `max_backtracks` 参数控制，默认为 3），实现类似运行时约束的自我修正。

---

## 常见误区

### 误区一：DSPy 等同于自动提示词生成工具

DSPy 不仅生成提示词文本，而是构建**可编译的程序图**。单个 `dspy.Predict` 模块确实会输出优化后的 prompt，但 DSPy 的真正能力在于协同优化多模块流水线中所有节点的提示词及少样本示例，并在评估指标上进行全局优化，而非逐条提示词地独立调整。将其视为"ChatGPT prompt 生成器"是对框架能力的严重低估。

### 误区二：DSPy 优化无需训练数据

许多初学者误认为 DSPy 是"零标注"工具。事实上，`BootstrapFewShot` 最少需要 **10-50 条带标签的训练样本**，`MIPRO` 则建议提供 100 条以上，且需要一个独立的验证集来评估指令候选。如果缺乏任何标注数据，DSPy 优化器无法运行，只能使用未优化的 `dspy.Predict` 基线。

### 误区三：ChainOfThought 模块直接复用了手工 CoT 技巧

`dspy.ChainOfThought` 并非简单地在 prompt 末尾追加"让我们一步步思考"。它在 Signature 中插入一个 `rationale` 输出字段，由优化器决定该字段的具体提示措辞和少样本示例中的推理格式。优化后的推理指令可能与人工 CoT 措辞截然不同，且通常针对特定任务和模型的组合进行了专项适配。

---

## 知识关联

**与思维链（CoT）的关系**：CoT 是 `dspy.ChainOfThought` 模块的概念基础，手工 CoT 要求人工设计推理步骤的提示措辞，而 DSPy 将这一工作交给优化器。学习 DSPy 之前，理解 CoT 中"中间推理步骤能提升多步推理准确率"的机制，有助于理解为何 `ChainOfThought` 模块在 DSPy 流水线中能持续带来增益。

**通向元提示工程（Meta-Prompting）**：DSPy 的优化器本质上使用 LLM 生成候选提示词（即 LLM 写 prompt），这与元提示工程的思路高度重叠。学习 DSPy 后，元提示工程中"指令生成模型与任务执行模型分离"的设计模式将更容易理解，因为 DSPy 的 `MIPRO` 优化器正是这一模式的工程实现。

**通向 LLM 评估基准**：DSPy 的优化过程强依赖评估指标的设计质量——指标选择不当（如仅用字符串精确匹配评估开放域问答）会导致优化器学到错误信号。这直接引出 LLM 评估基准领域的核心问题：如何构建可靠、无污染且与真实性能相关的自动化评估指标。