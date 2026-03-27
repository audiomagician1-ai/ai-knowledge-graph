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

模型合并（Model Merging）是一种无需额外训练、直接在参数空间中将多个独立微调模型的权重合并为单一模型的技术。其核心假设来自2022年前后的研究发现：在同一基础模型（如LLaMA-2-7B）上经过不同任务微调的模型，其权重仍位于同一高维参数空间中，且任务向量（Task Vector）可以进行线性叠加。这意味着两个分别擅长代码和数学的模型，合并后可能同时具备两种能力。

模型合并的早期理论基础来自Ilharco等人2022年发表的论文《Editing Models with Task Arithmetic》，该文将微调权重与基础模型权重之差定义为任务向量，并证明这些向量可被加减组合。2023年起，Hugging Face社区的合并实践爆炸式增长，MergeKit工具库的出现使普通研究者无需GPU即可在CPU上完成7B乃至70B规模的模型合并。在开源LLM竞赛榜单（如Open LLM Leaderboard）上，长期排名靠前的模型相当一部分是合并模型而非从头微调的模型。

模型合并之所以重要，在于它提供了一条极低成本获得多能力模型的路径。与多任务联合训练相比，合并不需要同时持有所有任务的数据；与RAG或Agent框架相比，合并后的能力被内化为模型权重本身而非外挂系统。对资源受限的研究者而言，这是将社区现有微调成果最大化复用的关键手段。

## 核心原理

### SLERP：球面线性插值

SLERP（Spherical Linear Interpolation，球面线性插值）最初用于3D图形中的四元数旋转插值，被引入模型合并后用于在两个模型的权重张量之间进行插值。与简单的线性插值（LERP）不同，SLERP沿高维球面上的测地线进行插值，公式为：

**SLERP(θ, v₀, v₁) = sin((1−θ)·Ω)/sin(Ω) · v₀ + sin(θ·Ω)/sin(Ω) · v₁**

其中Ω是两个权重向量之间的夹角（cos(Ω) = v₀·v₁ / (‖v₀‖·‖v₁‖)），θ∈[0,1]是插值比例。SLERP的优势在于，它保持了插值路径上权重向量的"范数"相对稳定，避免了线性插值在权重量级差异较大时产生的幅度衰减问题。SLERP的主要局限是仅支持**两个**模型之间的合并，对超过两个模型的场景需要层叠调用。

### TIES：解决参数冲突

TIES（Trim, Elect Sign, Disjoint Merge）由2023年的论文《TIES-Merging: Resolving Interference When Merging Models》提出，专门解决多模型合并时任务向量之间的**符号冲突**问题。其流程分三步：

1. **Trim（剪裁）**：对每个模型的任务向量（Δθ = θ_ft − θ_base），只保留绝对值最大的Top-K%参数（通常K=20），其余置零。这一步去除了微调中产生的低信号噪声扰动。
2. **Elect Sign（选举符号）**：对每个参数位置，统计所有模型在该位置任务向量的符号（正/负），以绝对值加权多数投票决定最终符号方向。
3. **Disjoint Merge（非重叠合并）**：只对与选定符号一致的任务向量参数取均值，符号相反的参数不参与该位置的合并。

TIES能有效缓解多个模型在同一参数位置"相互抵消"的问题，在3个以上模型合并时比简单均值合并的基准测试性能平均提升约2-5个百分点。

### DARE：稀疏化降低干扰

DARE（Drop And REscale）2023年提出，其核心思路是：微调模型相对基础模型的大量参数变化是冗余的，可以随机丢弃而不显著损害性能。具体做法是以概率p（通常p=0.9，即丢弃90%的任务向量参数）随机将任务向量中的元素置零，然后将保留的参数乘以缩放因子1/(1−p)以补偿期望值。

DARE通常与TIES结合使用（称为DARE-TIES），先用DARE对每个模型的任务向量进行稀疏化，再送入TIES流程合并。这种组合在合并4个以上的LoRA微调模型时尤其有效，因为LoRA模型的任务向量本身已相当稀疏，DARE能进一步减少合并时的参数干扰密度。实验表明，在合并8个专业领域模型时，DARE-TIES比单纯TIES减少了约15%的性能下降。

### 线性任务算术与权重缩放

最基础的合并方式是线性任务算术（Task Arithmetic）：θ_merged = θ_base + λ₁·Δθ₁ + λ₂·Δθ₂ + ...，其中λ为各任务向量的缩放系数。当λ<1时相当于部分合并，当λ为负数时可实现**任务消除**（Task Negation），例如将"有毒内容生成"能力从模型中减去。MergeKit中的`linear`和`task_arithmetic`方法均基于此原理，并允许逐层设置不同的λ值（Layer-wise scaling），因为模型浅层权重的合并往往比深层权重更敏感。

## 实际应用

**Mistral社区合并实践**：在Hugging Face上，基于Mistral-7B-v0.1的合并模型（如OpenHermes-2.5、NeuralHermes、Dolphin-2.2-mistral-7b的各种合并变体）常年占据7B量级Open LLM Leaderboard的前列。典型做法是将一个指令遵循模型与一个代码专精模型通过SLERP以θ=0.5进行合并，得到指令+代码双能力模型。

**MergeKit工具的配置方式**：用户通过YAML配置文件指定合并方法、参与模型路径及各层权重，全程在CPU上运行，合并一个7B模型通常耗时5-15分钟，无需任何GPU。这使得个人研究者可以在笔记本电脑上完成对比实验。

**Frankenmerge（层堆叠合并）**：这是MergeKit支持的一种特殊方法，直接拼接不同模型的Transformer层（而非插值权重），例如将模型A的第0-16层与模型B的第17-32层拼接，创造出参数量为原始模型1.5倍甚至2倍的"Frankenstein"模型。Solar-10.7B（由韩国AI公司Upstage基于LLaMA-2-13B和Mistral-7B层拼接）就是此类方法的成功案例，其在2023年底以10.7B参数超越了多个13B量级模型的性能。

**LoRA合并回主干**：模型合并也包括将训练好的LoRA适配器权重（ΔW = BA）直接加回基础模型权重（W' = W + α/r·BA），转换为全量参数模型。这是部署优化的标准做法，MergeKit和PEFT库均内置此功能。

## 常见误区

**误区一：合并总是优于单一微调模型**。模型合并的效果高度依赖参与合并的模型是否基于同一基础模型，且基础模型版本必须完全相同（精确到同一checkpoint）。将基于LLaMA-2-7B和LLaMA-2-7B-Chat的两个模型合并，因两者已在参数空间上产生较大偏移，合并后性能可能大幅下降而非提升。不同架构模型之间的直接合并（如LLaMA与Mistral）通常会产生退化输出。

**误区二：合并系数可以任意设置**。在任务算术合并中，λ的选择并非越大越好。过大的λ会使合并模型偏离基础模型过远，导致语言建模的基础能力（困惑度/perplexity）显著恶化。实验发现，对于大多数7B规模模型，λ>0.7时合并效果开始不稳定；TIES论文的实验中，λ=0.3-0.5是较为稳健的区间。

**误区三：模型合并等价于知识蒸馏**。知识蒸馏（Knowledge Distillation）通过让学生模型拟合教师模型的输出分布来传递知识，需要训练过程和数据。模型合并完全不涉及前向传播和梯度计算，是纯粹的参数空间算术操作。两者在目标（压缩vs.能力聚合）、成本（需要训练vs.无需训练）和适用场景上均有本质差异，不可混淆。

## 知识关联

模型合并是SFT/RLHF微调工作流的延伸——只有理解微调产生了什么（即相对基础模型的参数偏移，即任务向量）才能理解合并的操作对象。LoRA微调与模型合并的关系尤为紧密：LoRA产生的低秩增量矩阵需要先合并回全量权重才能参与SLERP/TIES等操作，而DARE的稀疏化思想也与LoRA将更新限制在低秩子空间的动机同源——