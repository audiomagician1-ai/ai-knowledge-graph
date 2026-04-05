---
id: "llm-benchmarks"
concept: "LLM Benchmarks (MMLU/HumanEval)"
domain: "ai-engineering"
subdomain: "llm-core"
subdomain_name: "大模型核心"
difficulty: 6
is_milestone: false
tags: ["LLM"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# LLM 基准测试：MMLU 与 HumanEval

## 概述

MMLU（Massive Multitask Language Understanding）和 HumanEval 是当前评估大语言模型能力最广泛使用的两个基准测试，分别针对知识推理和代码生成能力设计。MMLU 由 Dan Hendrycks 等人于 2020 年发布，包含来自 57 个学科领域的 15,908 道四选一选择题，涵盖 STEM、人文、社科和专业领域（如医学、法律）。HumanEval 则由 OpenAI 于 2021 年发布，包含 164 个 Python 编程题，通过 pass@k 指标衡量模型生成可执行、正确代码的能力。

这两个基准的重要性体现在：几乎所有主流大模型发布报告（GPT-4、Claude、Llama 等）都会公布这两项分数，使其成为横向比较模型能力的通用语言。MMLU 的平均准确率已从 GPT-3 时代的约 43.9% 提升到 GPT-4 的 86.4%，而人类专家水平约为 89.8%，这一数字清晰地标定了当前模型能力与人类之间的差距。

理解这两个基准的方法论设计与局限性，对于工程师在选型、训练和评估大模型时做出正确判断至关重要——盲目相信榜单分数而不了解其测量边界，会导致选错模型或错误解读能力进展。

## 核心原理

### MMLU 的题目构成与评分机制

MMLU 的 57 个学科涵盖范围极广，包括大学物理、临床知识、道德推理、美国历史、计量经济学等。每道题提供 A/B/C/D 四个选项，通过 few-shot prompting（通常为 5-shot）引导模型输出答案。最终分数是所有学科准确率的宏平均（macro-average），意味着每个学科权重相同，不论题量多少。

MMLU 的关键设计假设是：广泛的知识覆盖面可以代理模型的"智识广度"。但其题目大多来源于人类资格考试和教材，格式固定为选择题，这使得模型可以通过识别选项模式而非真正推理来获得分数——例如，某些模型会利用选项长度或特定关键词偏差（"以上都对"倾向于正确）来提升准确率。

### HumanEval 的 pass@k 指标

HumanEval 的核心评估指标 pass@k 定义为：给模型 n 次生成机会，至少有 k 次通过所有单元测试的概率。实际计算中为避免高方差，使用无偏估计公式：

$$\text{pass@k} = 1 - \frac{\binom{n-c}{k}}{\binom{n}{k}}$$

其中 n 为总生成次数（通常取 200），c 为通过测试的生成次数，k 为目标次数（常用 pass@1 和 pass@10）。这一指标直接测量代码功能正确性，而非代码风格或效率，因为"正确"的唯一标准是通过预设的单元测试集。

HumanEval 中的题目具有明确的函数签名（docstring + 输入输出说明），要求模型补全函数体。题目难度分布不均匀：简单题如字符串反转，难题涉及动态规划或复杂数据结构操作。GPT-4 的 pass@1 约为 67%，而 Claude 3.5 Sonnet 超过 90%，但这一差距需结合题目难度分布来解读，而非简单地理解为"好 30%"。

### 两个基准的方法论差异

MMLU 测量**知识检索与多步推理的结合**，答案已预设在选项中，模型无需生成开放式文本。HumanEval 测量**从自然语言需求到可执行代码的转换**，输出空间几乎无限。这一根本差异导致两个分数捕捉的能力维度不同：一个模型在 MMLU 上表现优异但在 HumanEval 上落后，通常意味着其预训练数据中代码比例偏低，而非"更笨"。

此外，MMLU 存在严重的数据污染风险（data contamination）：由于其题目公开且固定，模型在预训练语料中可能直接见过题目与答案。OpenAI 在 GPT-4 技术报告中承认无法完全排除这种可能性，并通过 n-gram 重叠检测估计污染程度，但这一估计方法本身也不完备。

## 实际应用

**模型选型决策**：在选择代码助手工具时，工程师应优先参考 HumanEval pass@1 分数，并结合 HumanEval+ （由 EvalPlus 团队扩展至 164→1800+ 测试用例）的结果，因为后者能更有效地识别通过数量少但覆盖边界条件的代码生成能力差异。

**训练阶段监控**：在对预训练模型进行指令微调（instruction tuning）时，MMLU 分数常被用作"知识遗忘"的监控指标。若微调后 MMLU 下降超过 2 个百分点，通常提示指令数据集中的知识覆盖不足或学习率设置过高，导致原有知识被覆写。

**排行榜解读实践**：HuggingFace Open LLM Leaderboard 曾长期使用 MMLU 作为核心指标，但 2023 年底发现多个"刷榜"模型：开发者针对 MMLU 的题目格式进行专项微调，导致分数虚高但实际能力未提升。这促使社区转向使用 MMLU-Pro（选项从 4 个扩展到 10 个，更难被猜测）作为替代。

## 常见误区

**误区一：MMLU 高分等于模型"更聪明"**
MMLU 测量的是在 57 个特定学科的四选一准确率，不能直接推广为通用智能的代理指标。一个专门在教材问答数据上微调的模型可以在 MMLU 上拿到 75% 以上，但在开放式推理任务上完全失效。GPT-4 和某些专项微调的 7B 模型在 MMLU 上分数相近，但两者的实际推理差距却极为显著。

**误区二：HumanEval 的通过率代表真实编程能力**
HumanEval 的 164 道题全部为 Python，且单元测试用例数量有限（平均每题约 7.7 个测试用例），容易出现"偶然通过"——模型可以生成一个仅适用于给定测试输入、不具通用性的硬编码实现。EvalPlus 团队在 2023 年将测试用例从约 7 个/题扩展到 100+ 个/题后，多个模型的 pass@1 平均下降了约 15–20 个百分点，说明原始 HumanEval 存在明显高估问题。

**误区三：两个基准分数都高则模型全面均衡**
MMLU 和 HumanEval 仅覆盖了知识问答与 Python 代码两个维度，不测量对话连贯性、长上下文理解、数学推理（需 GSM8K 或 MATH 基准）、多语言能力或指令遵循精度。仅凭这两个数字判断模型"全面均衡"会忽略其在未测维度上的潜在弱点。

## 知识关联

学习 MMLU 和 HumanEval 需要已具备 LLM 评估方法的基础知识，特别是对 few-shot prompting 机制、token 生成概率与采样策略的理解——因为 MMLU 的 5-shot 格式与 HumanEval 的温度参数设置都直接影响最终分数，而非仅反映模型本身的能力。理解 pass@k 的无偏估计公式需要基本的组合数学背景。

在更广泛的评估生态中，MMLU 和 HumanEval 属于**自动化静态基准**这一类别，与 LMSYS Chatbot Arena 的人类偏好排名、BIG-Bench 的动态任务扩展形成对照。随着主流模型在这两个基准上逼近天花板（MMLU 接近人类专家水平，HumanEval 已被多个模型超越 90%），社区正在将注意力迁移至 MMLU-Pro、LiveCodeBench（使用竞赛平台实时更新的题目避免污染）和 SWE-bench（测量真实 GitHub issue 修复能力）等下一代基准。