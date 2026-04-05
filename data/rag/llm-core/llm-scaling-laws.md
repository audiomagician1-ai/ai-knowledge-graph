---
id: "llm-scaling-laws"
concept: "LLM缩放定律"
domain: "ai-engineering"
subdomain: "llm-core"
subdomain_name: "大模型核心"
difficulty: 8
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
updated_at: 2026-03-26
---


# LLM缩放定律

## 概述

LLM缩放定律（Scaling Laws for Neural Language Models）是描述语言模型性能与模型规模、数据量、计算量之间幂律关系的定量理论。2020年，OpenAI研究员Jared Kaplan等人在论文《Scaling Laws for Neural Language Models》中首次系统性地提出这一框架，核心发现是：语言模型的交叉熵损失（cross-entropy loss）与模型参数量N、训练数据量D、计算预算C之间各自呈现出平滑的幂律（power-law）关系，而非饱和或断崖式变化。

Kaplan等人的核心方程为：$L(N) \approx (N_c / N)^{\alpha_N}$，其中$N_c$是拟合常数，指数$\alpha_N \approx 0.076$。类似地，$L(D) \approx (D_c / D)^{\alpha_D}$，$\alpha_D \approx 0.095$。这意味着：将参数量扩大10倍，损失下降约有固定比例，且这种规律在参数量从$10^7$跨越到$10^{10}$以上的范围内保持稳定。这一发现使得研究者可以在小规模实验上预测大规模模型的行为，从而指导数十亿美元的训练决策。

缩放定律的重要性在于它将深度学习从"炼丹术"推向了某种"工程科学"。在此之前，从业者无法系统预测增大模型是否值得；有了缩放定律，可以通过小实验外推大模型的预期性能，合理分配计算预算——这直接影响了GPT-3（1750亿参数）、PaLM（5400亿参数）等模型的设计决策。

## 核心原理

### Kaplan缩放定律的幂律关系

Kaplan 2020论文的核心结论是三条独立的幂律：
- **参数缩放**：$L(N) \propto N^{-0.076}$，固定数据量充足时，增加参数量持续降低损失；
- **数据缩放**：$L(D) \propto D^{-0.095}$，固定模型大小时，增加数据量同样持续降低损失；
- **计算缩放**：$L(C) \propto C^{-0.050}$，在固定FLOPs预算下，存在最优的参数量与数据量分配比例。

特别关键的是：Kaplan等人发现，在固定计算预算C的情况下，最优策略是**优先增大模型参数量**，而数据量可以相对较少。这一结论在2022年被后续研究推翻。

### Chinchilla缩放定律对Kaplan的修正

2022年，DeepMind的Hoffmann等人在论文《Training Compute-Optimal Large Language Models》中提出Chinchilla缩放定律，对Kaplan的结论进行了重要修正。Chinchilla定律的核心结论是：**最优训练时，模型参数量N与训练token数D应保持大致1:20的比例**，即每个参数对应约20个训练token。

具体地，Chinchilla定律给出最优参数量 $N_{opt} \propto C^{0.5}$，最优数据量 $D_{opt} \propto C^{0.5}$，两者应同步扩大。对比之下，Kaplan定律预测 $N_{opt} \propto C^{0.73}$，严重偏向增大模型规模。基于此，Chinchilla（700亿参数，1.4万亿token）在多项基准上超过了参数量是其4倍的Gopher（2800亿参数），直接证明GPT-3等模型是"训练不足"（undertrained）的。

### 计算效率前沿（Compute-Optimal Frontier）

给定计算预算 $C \approx 6ND$（其中6是前向+反向传播的FLOPs近似系数），缩放定律确定了参数量与数据量的最优权衡曲线。这条曲线称为**计算效率前沿**。落在前沿左侧意味着模型过大、数据不足（undertrained）；落在右侧意味着模型过小、数据过多（过度训练但推理高效）。

LLaMA系列模型有意偏离Chinchilla最优点，选择用更小的参数量搭配更大的数据量（例如LLaMA-1的7B模型使用1万亿token，远超Chinchilla建议的约1400亿token），牺牲训练效率换取推理时的低成本，这是一种针对**推理部署场景**而非训练效率的工程权衡。

### 涌现能力与缩放定律的关系

部分能力（如思维链推理、算术运算）不遵循平滑的幂律，而是在某个参数量阈值附近**突然涌现**（emergent abilities）。研究者发现这些涌现能力通常在参数量超过约$10^{10}$时出现，但目前学界对于涌现是真实的非线性现象还是评测指标选择的假象仍有争议（Schaeffer等人2023年的研究指出，换用连续指标后，许多"涌现"现象消失，仍呈幂律）。

## 实际应用

**计算预算分配**：Meta在训练LLaMA-2（700亿参数）时，基于Chinchilla定律将训练数据量设为2万亿token，是Chinchilla建议值的约2.7倍，以平衡训练成本与推理效率的工程需求。

**小实验外推大模型**：OpenAI在GPT-4训练前，据报道使用了一系列从$10^7$到$10^{10}$参数的小模型，通过拟合幂律曲线外推预测GPT-4在MMLU等基准上的预期表现，误差控制在合理范围内，从而决定是否值得进行全规模训练投入。

**MoE架构的参数计数修正**：在混合专家模型（MoE）中，缩放定律需要区分**总参数量**与**激活参数量**，因为每个token只激活部分专家。实验表明，MoE模型的损失与激活参数量的幂律关系更稳定，这直接影响了Mixtral、GPT-4（推测为MoE架构）的设计哲学。

## 常见误区

**误区一：缩放定律保证所有能力随规模线性提升。** 缩放定律描述的是交叉熵损失（perplexity相关）的平均行为，而非每项具体任务的准确率。特定任务（尤其是需要多步推理的任务）可能在小规模时几乎无效，在某个规模阈值后快速跃升，这类涌现行为不符合幂律假设。直接用损失的幂律外推任务准确率会导致错误预测。

**误区二：Kaplan定律已过时，Chinchilla定律才是真理。** Chinchilla定律针对的是**训练计算效率最优**场景。如果目标是**推理部署成本最优**（如在手机或边缘设备上运行），则应选择比Chinchilla建议更小的模型并喂入更多数据，使其充分训练。LLaMA、Mistral系列的成功正是基于这一反向逻辑。选择哪条定律，取决于工程目标是训练效率还是推理效率。

**误区三：增大数据量总能替代增大模型参数量。** 缩放定律中存在数据重复（data repetition）惩罚效应。Muennighoff等人2023年的研究表明，当数据重复超过4个epoch时，损失相对于唯一token量的幂律关系开始偏离，重复数据带来的收益大幅递减，不能简单地以重复数据替代新数据来模拟等效的D增大。

## 知识关联

**与LLM预训练的关系**：缩放定律的所有变量（N、D、C）直接对应预训练的三要素：模型参数量、训练语料大小、训练FLOPs。理解预训练的transformer架构（注意力头数、层数、隐藏维度如何决定N）是正确计算缩放定律中参数量的前提，例如$N \approx 12 \cdot d_{model}^2 \cdot n_{layers}$（忽略词表部分）。

**与MoE混合专家模型的关系**：Chinchilla定律揭示了稠密模型参数量与数据量的最优比，但稠密模型在推理时必须激活所有参数，计算成本随N线性增长。MoE模型通过条件计算（conditional computation）在固定激活参数量下扩大总参数量，相当于在缩放定律的坐标系中同时移动"总参数量"与"激活参数量"两个维度，从而以更低推理FLOPs达到Chinchilla最优损失，这是MoE成为下一代超大规模模型主流架构的理论依据。