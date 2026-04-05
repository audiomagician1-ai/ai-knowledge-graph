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
updated_at: 2026-03-26
---


# 提示词自动优化（DSPy）

## 概述

DSPy（Declarative Self-improving Language Programs）是由斯坦福大学 NLP 研究组于 2023 年发布的一个 Python 框架，其核心思想是将提示词工程从手工编写字符串转变为可编程、可自动优化的模块化系统。传统 Prompt Engineering 需要工程师反复手动调整指令措辞，而 DSPy 通过将语言模型调用抽象为带有输入/输出签名的模块（Module），使提示词本身成为可以被算法自动优化的参数。

DSPy 由 Omar Khattab 等人主导开发，首篇论文《DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines》描述了其核心机制。框架的命名来源于其声明式（Declarative）与自改进（Self-improving）特性，灵感部分借鉴了 PyTorch 对神经网络参数自动优化的设计哲学——与 PyTorch 中梯度反向传播优化权重类似，DSPy 通过"编译器"（Compiler）优化提示词中的示例和指令。

DSPy 解决了链式提示（Prompt Chaining）系统中一个根本性痛点：当一个 pipeline 包含多个 LLM 调用步骤时，手动协调各步骤的提示词极易产生错误累积，且任何一个步骤的更换（如换用不同基座模型）都需要全流程重写。DSPy 将 pipeline 编写与提示词优化解耦，使同一段代码逻辑在面对 GPT-4、LLaMA-3 或 Claude 3 时可以自动生成各自最优的提示词。

---

## 核心原理

### 签名（Signature）与模块（Module）

DSPy 的最小单元是 **Signature**，它以 `"输入字段 -> 输出字段"` 的字符串形式声明任务意图，例如 `"question -> answer"` 或 `"context, question -> reasoning, answer"`。这个签名不包含任何具体措辞，仅定义字段名称和类型约束。

基于 Signature，DSPy 提供多种内置 **Predictor 模块**：
- `dspy.Predict`：最基础的单次 LLM 调用
- `dspy.ChainOfThought`：自动在签名中注入 `reasoning` 字段，强制模型先生成推理步骤再输出答案（对应思维链机制，但无需手动编写"Let's think step by step"等措辞）
- `dspy.ReAct`：实现 Reason+Act 循环，每轮可调用外部工具
- `dspy.ProgramOfThought`：让模型生成可执行代码而非文字推理

用户通过继承 `dspy.Module` 并在 `forward()` 方法中组合这些 Predictor，构建出完整的 LLM 应用程序，整个过程完全不涉及任何提示词字符串。

### 优化器（Teleprompter / Optimizer）

DSPy 的自动优化由 **Optimizer**（早期版本称 Teleprompter）完成，其工作流程分三步：

1. **候选生成**：根据训练集中的示例，自动筛选、生成 few-shot 示例候选池
2. **评估打分**：对每种提示词配置（由哪些 few-shot 示例组成、指令措辞如何）使用用户定义的 `metric` 函数在开发集上打分
3. **迭代选择**：按打分结果保留最优配置，写回各 Module 的提示词参数

核心优化器包括：
- **`BootstrapFewShot`**：从训练样本中自举（bootstrap）生成 few-shot 示例，最低仅需 **20 个有标注训练样本**即可启动优化
- **`MIPRO`（Multi-prompt Instruction Proposal and Optimization）**：在优化 few-shot 示例的同时，利用 LLM 自动提案并筛选指令文本，属于更彻底的全提示词优化
- **`BayesianSignatureOptimizer`**：使用贝叶斯优化策略在指令空间中搜索，适合调用预算有限的场景

### 编译（Compile）过程

调用 `teleprompter.compile(program, trainset=trainset, metric=metric)` 后，DSPy 进行的实质操作是：遍历 `trainset`，对每条样本运行 `program` 的完整 forward pass，收集中间步骤的输入/输出对，经 `metric` 筛选后将质量达标的 (input, output) 对以 few-shot 示例形式注入各 Predictor 的提示词。编译结束后调用 `program.save("optimized.json")` 可将优化结果持久化，这份 JSON 文件存储的正是各模块最终选定的 few-shot 示例和指令文本。

---

## 实际应用

**多跳问答（Multi-hop QA）**：在 HotPotQA 数据集上，使用 DSPy 的 `MultiHopQA` 程序配合 `BootstrapFewShot` 优化，GPT-3.5-turbo 的 EM（精确匹配）得分相较手写提示词基线提升约 **8-12 个百分点**，且优化仅消耗约 **300 次 LLM 调用**。

**RAG 流水线质量提升**：在 RAG（Retrieval-Augmented Generation）系统中，检索模块的查询改写与生成模块的答案合成分别是两个 DSPy Module，通过 MIPRO 联合优化后，DSPy 能自动发现"生成模块应要求模型明确引用段落编号"这类非直觉的指令，这是人工调试极难发现的优化方向。

**模型迁移场景**：某团队将基于 GPT-4 手写的法律文书分析 pipeline 迁移至 Mistral-7B 本地部署时，原提示词在小模型上 F1 下降约 **35%**；使用 DSPy 重构后对 Mistral-7B 重新编译，F1 仅下降 **9%**，极大降低了模型替换成本。

---

## 常见误区

**误区一：DSPy 等于自动生成提示词字符串的工具**
DSPy 的目标不是"生成更好的提示词字符串"让人复制粘贴使用，而是构建一个**可运行的优化程序**，提示词是该程序的内部状态。直接查看 `compiled_program` 中的提示词并手动复制到其他地方使用，会完全丧失 DSPy 的跨模型适配能力和模块组合特性。

**误区二：不需要任何标注数据**
DSPy 虽然降低了对标注数据的需求，但**并非零标注**。`BootstrapFewShot` 至少需要带有正确输出标注的训练集（哪怕只有最终答案标签）。无标注场景下可使用 `LabeledFewShot` 手动提供示例，但此时的"自动优化"退化为示例选择而非全局搜索，效果有限。误以为只要有无标注文本就能全自动优化是对框架能力的高估。

**误区三：`ChainOfThought` 模块与手写 CoT 提示词等价**
`dspy.ChainOfThought` 在未经编译时确实只是在答案前插入一个 `reasoning` 字段，其效果与简单的"Let's think step by step"类似。但经过 `BootstrapFewShot` 编译后，该模块的 few-shot 示例中包含了**由模型在训练集上自举生成并经 metric 筛选的高质量推理链**，其质量远超人工编写的通用 CoT 示例，两者不可混淆。

---

## 知识关联

**前置概念——思维链（CoT）**：`dspy.ChainOfThought` 是 CoT 的程序化封装，DSPy 的自举过程会自动为 CoT 模块生成任务特定的高质量推理示例，解决了手写 CoT 示例耗时且依赖专家经验的问题。理解 CoT 的推理步骤插入机制有助于理解 DSPy 签名中 `reasoning` 字段的作用。

**后续概念——元提示工程（Meta-Prompt Engineering）**：DSPy 的 MIPRO 优化器本身就是元提示的一种自动化实现——它使用一个"元 LLM"来提案和评估目标 LLM 的指令。学习元提示工程时可将 DSPy 中 MIPRO 的指令提案模板作为具体案例，理解"用 LLM 优化 LLM 提示词"的设计模式。

**后续概念——LLM 评估基准**：DSPy 的 `metric` 函数本质上是一个轻量级任务评估器，其设计逻辑（黄金标签比对、LLM-as-Judge 打分等）与 LLM 评估基准的构建方法高度重合。掌握 DSPy 的 metric 设计后，学习 MMLU、HellaSwag 等基准的评估设计思路时，可以清晰识别各基准的 metric 形式及其局限性。