---
id: "model-merging"
concept: "模型合并"
domain: "ai-engineering"
subdomain: "llm-core"
subdomain_name: "大模型核心"
difficulty: 8
is_milestone: false
tags: ["LLM", "高级"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 50.4
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.452
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 模型合并

## 概述

模型合并（Model Merging）是指在**不进行额外训练**的前提下，将两个或多个独立微调的神经网络权重直接融合为一个新模型的技术。与蒸馏或集成学习不同，模型合并操作完全在参数空间（weight space）中进行，合并后的模型与原始模型具有完全相同的架构和参数量，推理成本不会增加。这一特性使其成为开源LLM社区在2023-2024年间爆炸式增长的热门技术，Hugging Face上出现了数百个通过合并产生的高分模型。

模型合并的理论基础可以追溯到2022年Mitchell等人的论文《Model Soups》，该论文首次系统性地证明：在同一预训练基础上微调的多个模型，其权重在损失景观（loss landscape）中处于同一低损失盆地（basin），因此直接对权重求均值不会导致性能崩溃。这一洞见催生了后续一系列更精细的合并算法。在实践中，模型合并的意义在于：可以将针对数学、代码、指令跟随等不同能力分别微调的专家模型融合为一个通用能力更强的模型，同时节省大量GPU训练资源。

## 核心原理

### 线性插值与球面线性插值（SLERP）

最简单的模型合并是**线性插值（LERP）**，公式为：
$$\theta_{merge} = (1-t)\cdot\theta_A + t\cdot\theta_B, \quad t \in [0,1]$$

其中 $\theta_A$、$\theta_B$ 分别为两个模型的权重向量，$t$ 是插值系数。然而，当权重向量高维度且模长差异较大时，线性插值会导致合并模型的权重范数（norm）在中间点处显著小于两端，产生所谓"范数塌陷"问题，表现为模型输出过于保守或困惑度上升。

**SLERP（Spherical Linear Interpolation，球面线性插值）** 通过将插值路径限制在超球面上解决这一问题，公式为：
$$\theta_{merge} = \frac{\sin((1-t)\Omega)}{\sin\Omega}\theta_A + \frac{\sin(t\Omega)}{\sin\Omega}\theta_B$$
其中 $\Omega = \arccos\left(\frac{\theta_A \cdot \theta_B}{|\theta_A||\theta_B|}\right)$ 是两权重向量的夹角。SLERP保证了合并路径上每个点的权重范数恒定，在两模型能力差异较大（夹角较大）时效果尤为显著。mergekit工具库中SLERP是最常用的双模型合并方法。

### TIES合并：处理干扰参数

**TIES（Trim, Elect Sign & Merge）** 由2023年Yadav等人提出，专门解决多模型合并（3个以上）时的参数干扰（interference）问题。其核心思路分三步：

1. **Trim（修剪）**：对每个模型相对于基础模型的增量权重 $\Delta\theta_i = \theta_i - \theta_{base}$，按绝对值大小保留Top-k%（通常k=20），将其余参数归零。这一步消除了微调中产生的大量噪声小扰动。
2. **Elect Sign（选举符号）**：对每个参数位置，统计所有模型增量中正值与负值的总量之和，选择绝对值更大的方向作为该位置的"主方向"，舍弃反方向的模型贡献。
3. **Merge（合并）**：仅对符号一致的参数取均值，叠加回基础模型权重。

TIES的核心贡献在于用符号投票机制避免了不同能力方向上的相互抵消，在合并3-7个模型时相比简单均值平均有约2-4%的基准测试提升。

### DARE：大规模随机丢弃

**DARE（Drop And REscale）** 由2023年Yu等人提出，其核心思想是：在将微调增量 $\Delta\theta$ 叠加回基础模型之前，以概率 $p$（通常p=0.9，即90%的参数被丢弃）随机将增量置零，并对保留的参数乘以 $\frac{1}{1-p}$ 进行重新缩放以保持期望值不变：
$$\Delta\theta_{DARE} = \frac{m \odot \Delta\theta}{1-p}$$
其中 $m$ 是伯努利随机掩码。DARE基于一个反直觉的发现：大模型（7B参数以上）的微调增量中绝大多数参数对模型性能贡献极小，丢弃90%的增量参数后性能损失不足0.5%。DARE通常与TIES结合使用（DARE-TIES），先通过DARE稀疏化各模型的增量，再用TIES进行合并，实现了比单独使用任一方法更好的效果。

### 任务向量与负合并

**任务向量（Task Vector）** 概念由Ilharco等人在2023年正式提出，定义为 $\tau = \theta_{fine-tuned} - \theta_{pre-trained}$。任务向量最重要的性质是支持**算术运算**：两个任务向量相加对应能力叠加，任务向量取反（乘以-1）后叠加回基础模型可以实现能力"遗忘"（例如遗忘有害内容生成能力）。这一机制使得模型合并不仅是能力增强工具，也成为对齐研究的手段之一。

## 实际应用

**开源社区合并实践**：以mergekit为代表的开源工具极大降低了模型合并的门槛，用户只需编写YAML配置文件即可在单张消费级GPU（甚至CPU）上完成70亿参数模型的合并。2024年初在Open LLM Leaderboard排行榜前10的模型中，超过60%是通过合并而非独立训练产生的。典型案例包括将Mistral-7B-v0.1为基础、合并数学能力（WizardMath）与代码能力（CodeLlama-7B-Instruct）微调版本产生综合能力更强的通用模型。

**Frankenmerge（层级混合）**：这是mergekit支持的特殊合并方式，将不同模型的Transformer层直接拼接，例如将模型A的第0-16层与模型B的第17-32层组合。由于这种方式会增加模型参数量（从7B变为13B），严格来说属于模型拼接而非权重合并，但在社区实践中被广泛归入合并范畴，代表作是Goliath-120B（由两个Llama-2-70B拼接而成）。

**进化合并（Evolutionary Merging）**：Sakana AI在2024年3月提出的方法，使用进化算法自动搜索各层最优的合并系数，无需人工设定 $t$ 值，在日语LLM合并任务上实现了超过人工调参的效果。

## 常见误区

**误区一：模型合并等同于参数均值**。许多初学者认为合并就是 $(\theta_A + \theta_B)/2$，实际上简单均值只在两模型基于相同基础模型且微调数据分布相近时有效。当两模型的任务向量夹角超过90度时，简单均值的性能往往低于任意单一模型，必须使用TIES或DARE等方法处理参数干扰问题。

**误区二：任意两个模型都可以合并**。模型合并有严格的前提条件：**两模型必须具有相同的架构和词表**，且通常要求基于同一个预训练模型（或其直接后代）进行微调。将Llama-3-8B微调版本与Mistral-7B微调版本直接合并不会得到有意义的结果，因为两者的权重空间并不对齐（处于不同的loss basin中）。跨架构合并（如Llama与Qwen）在理论和实践上均不可行。

**误区三：合并系数 $t=0.5$ 总是最优的**。在SLERP合并中，最优的 $t$ 值高度依赖于具体评测基准。当目标是增强数学推理能力时，可能 $t=0.7$（偏向数学模型）才能使GSM8K分数最高，而此时代码能力基准可能会下降。实践中需要在多个基准上做参数扫描（t从0.1到0.9以0.1为步长测试），而非固定使用0.5。

## 知识关联

模型合并在技术上深度依赖**LoRA与参数高效微调**的概念：mergekit支持直接合并LoRA适配器（在合并前先将LoRA权重合并回基础模型），而LoRA的增量矩阵 $\Delta W = BA$ 本质上就是一种低秩任务向量，DARE的稀疏化思路与LoRA的低秩假设（大多数参数更新是冗余的）共享同一理论直觉。同时，理解**SFT/RLHF微调**对于判断哪些模型适合合并至关重要：经过RLHF对齐的模型（如Llama-2-Chat）与仅做SFT的模型（如Llama-2-Base）在权重空间中差异极大，直接合并往往会破坏RLHF带来的安全对齐特性，这是实践中需要特别注意的风险点。