---
id: "evaluation-benchmarks"
concept: "LLM评估基准"
domain: "ai-engineering"
subdomain: "prompt-engineering"
subdomain_name: "Prompt工程"
difficulty: 4
is_milestone: false
tags: ["benchmark", "evaluation", "mmlu"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.8
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.433
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# LLM评估基准

## 概述

LLM评估基准（Benchmark）是用于系统性测量大型语言模型在特定能力维度上表现的标准化测试集。与传统软件测试不同，LLM基准需要覆盖语言理解、推理、代码生成、事实知识、多轮对话等异质性能力，因此单一基准无法全面刻画模型能力，实践中通常需要组合使用多个基准。

MMLU（Massive Multitask Language Understanding）由Dan Hendrycks等人于2020年发布，包含57个学科领域的14,042道选择题，涵盖从基础数学到医学伦理的广泛知识。HumanEval则由OpenAI于2021年发布，包含164道Python编程题，以pass@k指标（k次尝试中至少通过一次的概率）衡量代码生成能力。MT-Bench由LMSYS团队于2023年提出，专注于多轮对话质量，使用GPT-4作为裁判模型对回答进行1-10分评分。

了解这些基准对Prompt工程师至关重要：在使用DSPy进行提示词自动优化时，优化目标的选取直接依赖对评估基准的理解；在通过OpenAI/Claude API进行模型选型时，基准分数是重要的参考依据，但需要清楚每个基准实际测量的是什么能力。

## 核心原理

### MMLU的测量逻辑与局限

MMLU采用zero-shot或few-shot（通常5-shot）提示格式，要求模型从A/B/C/D四个选项中选择正确答案。其57个学科按难度分为Elementary、High School、College、Professional四个层级。GPT-4在MMLU上的得分约为86.4%，而人类专家平均约为89.8%。

MMLU的核心局限在于它测量的是**记忆性知识的再现**，而非推理能力。一个模型可以通过训练数据中的记忆在MMLU上得高分，却在需要组合推理的任务上表现糟糕。此外，由于MMLU题目已被大量公开，很多模型的训练数据中可能包含原题，导致"基准污染"（benchmark contamination）问题，使得分数虚高。

### HumanEval与pass@k指标

HumanEval每道题包含函数签名、文档字符串和单元测试。pass@k的计算公式为：

$$\text{pass@}k = 1 - \frac{\binom{n-c}{k}}{\binom{n}{k}}$$

其中 $n$ 为总采样次数，$c$ 为通过测试的样本数，$k$ 为允许尝试次数。实践中通常报告pass@1（单次生成通过率）和pass@10。GPT-4的pass@1约为67%，Claude 3.5 Sonnet约为73%。

HumanEval的164道题目整体偏向算法类基础题，对涉及外部库调用、错误处理、复杂数据结构的实际工程代码覆盖不足。因此衍生出了HumanEval+（增加了更严格的测试用例）和MBPP（主要测试基础Python编程问题，包含500道题）。

### MT-Bench的LLM-as-Judge方法

MT-Bench包含80个精选的多轮对话问题，分为Writing、Roleplay、Reasoning、Math、Coding、Extraction、STEM、Humanities八类。每个对话包含两轮，第二轮故意设计为需要利用第一轮上下文的追问。

其核心机制是**LLM-as-Judge**：使用GPT-4对模型输出打分，并附加评分理由。这一方法与人类评估的相关性达到80%以上，远高于传统自动化指标（如BLEU、ROUGE）。但这也意味着评估结果受GPT-4本身偏见影响——研究发现GPT-4作为裁判时倾向于给较长回答和自身风格相近的输出更高分，即"位置偏见"和"自我强化偏见"。

### 其他重要基准

**GSM8K**：8,500道小学数学应用题，测量多步数学推理能力，是评估Chain-of-Thought提示效果的标准测试集。GPT-4在GSM8K上得分约92%，而GPT-3.5约57%，两者差距显著体现了推理能力的代际跳跃。

**HellaSwag**：测量常识推理，要求模型从四个候选句中选出最合理的活动描述续写。其难点在于干扰选项经过专门设计以欺骗语言模型但对人类显而易见，人类准确率约95%，而早期模型仅约40%。

**HELM（Holistic Evaluation of Language Models）**：斯坦福大学提出的综合评估框架，不只报告准确率，还系统测量校准度（Calibration）、鲁棒性、公平性和效率，是目前最全面的多维度基准体系。

## 实际应用

**模型选型决策**：在使用OpenAI API时，如果业务场景主要是生成Python数据处理脚本，应重点参考HumanEval/MBPP分数而非MMLU；如果是构建法律问答系统，则应查看MMLU中Law相关子集的具体得分。不能仅凭综合排名选择模型。

**DSPy优化目标设定**：使用DSPy的`BootstrapFewShot`优化器时，需要定义评估指标（metric）。如果任务是代码生成，可以直接复用HumanEval的unit test执行方式作为metric；如果任务是问答，可以参考MT-Bench的LLM-as-Judge方法构建自定义评分器。评估指标的质量直接决定了DSPy优化结果的可靠性。

**识别基准污染**：当某模型在MMLU某子领域得分异常高（如超过人类专家均值5个百分点以上），应怀疑训练数据污染。可通过对题目进行轻微改写后重新测试来检验，若分数骤降则说明模型依赖了记忆而非真实理解。

## 常见误区

**误区一：基准排名高等于实际任务表现好**。MMLU排名靠前的模型在具体的Prompt工程任务中未必表现最佳。MMLU测量的是静态知识，而实际应用中的指令跟随能力、格式控制能力、拒绝不合理请求的能力，在MMLU中完全无法体现。应该根据目标任务类型选择对应基准分数作参考。

**误区二：pass@1高意味着代码能力强**。HumanEval的164道题目样本量极小，且题目风格单一（主要是字符串处理、数学计算等算法题）。一个模型可能在HumanEval上pass@1=70%，但在实际项目中生成的API调用代码、配置文件解析代码却频繁出错。SWE-Bench（包含真实GitHub Issue修复任务）才是测量实际软件工程能力的更好基准。

**误区三：MT-Bench分数客观反映对话质量**。由于MT-Bench使用GPT-4打分，如果要评估的模型恰好与GPT-4输出风格相似（如同为OpenAI系列），可能获得系统性加分。对话质量的评估还应该结合人工评估或使用不同的裁判模型（如Claude）进行交叉验证。

## 知识关联

本文档建立在**LLM API调用（OpenAI/Claude）**的基础上——理解API调用中temperature、top_p等参数对采样的影响，有助于理解为何pass@k需要多次采样（temperature>0时每次结果不同），以及为何zero-shot评估与few-shot评估会产生显著差异。

在**提示词自动优化（DSPy）**中，基准的选择直接影响优化器的搜索方向。DSPy的`Evaluate`模块需要传入devset（开发集）和metric函数，这两者的设计本质上就是构建一个小型专用基准。理解MMLU的few-shot构造方式，可以帮助正确设计DSPy中的demonstration示例格式；理解HumanEval的执行式评估（而非模型打分），可以启发构建更可靠的代码生成评估流水线。