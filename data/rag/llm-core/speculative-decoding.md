---
id: "speculative-decoding"
concept: "Speculative Decoding"
domain: "ai-engineering"
subdomain: "llm-core"
subdomain_name: "大模型核心"
difficulty: 8
is_milestone: false
tags: ["LLM"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 66.2
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.581
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 推测解码（Speculative Decoding）

## 概述

推测解码是一种无损加速大语言模型自回归推理的技术，由Google DeepMind在2023年的论文《Speculative Decoding》（Leviathan et al., 2023）和《Fast Inference from Transformers via Speculative Decoding》中正式提出。其核心思想是：用一个小型"草稿模型"（draft model）快速生成若干候选token，再用目标大模型并行验证这些候选token的接受与否，从而在单次大模型前向传播中完成多个token的生成。

这一技术的根本动机来自LLM推理的硬件瓶颈分析：大模型推理受内存带宽（memory bandwidth）而非计算能力（FLOPS）限制，属于"memory-bound"操作。在A100 GPU上，单次解码一个token需要将数百GB的权重从HBM加载到SRAM，但实际矩阵运算量极少。推测解码通过批量验证多个token来提升算术强度（arithmetic intensity），将原本浪费的计算资源转化为吞吐量提升，在不改变输出分布的前提下实现2x–3x的速度提升。

与投机性并行（speculative parallelism）或提前退出（early exit）等有损加速方法不同，推测解码保证了输出与原始大模型精确等价——数学上可以证明，接受-拒绝采样机制使最终输出的token分布与目标模型独立生成时完全相同。

## 核心原理

### 草稿-验证循环（Draft-then-Verify Loop）

推测解码的完整流程分为两个阶段：
1. **草稿阶段**：小模型（draft model，参数量通常为目标模型的1/10至1/7）自回归生成γ个候选token（通常γ=4至8）。
2. **验证阶段**：将当前上下文加上γ个草稿token一次性送入目标大模型，通过一次并行前向传播同时获得γ+1个位置的概率分布（最后一个位置是目标模型对第γ+1个token的预测）。

关键在于，目标模型在验证γ个草稿token时的计算代价，与仅生成1个新token的代价几乎相同（因为Transformer的矩阵运算可以完全并行化）。这是整个方法能够奏效的根本原因。

### 接受-拒绝采样的数学保证

对于第i个草稿token $\tilde{x}_i$，目标模型给出概率 $p(\tilde{x}_i)$，草稿模型给出概率 $q(\tilde{x}_i)$，接受概率为：

$$\alpha_i = \min\left(1, \frac{p(\tilde{x}_i)}{q(\tilde{x}_i)}\right)$$

若被拒绝，则从调整后的分布 $p'(x) = \text{norm}(\max(0, p(x) - q(x)))$ 中重新采样。可以严格证明，此机制下最终接受的token序列分布恰好等于 $p(x)$，即目标模型的分布。这是推测解码"无损"特性的数学根基，不同于其他近似加速方法。

### 平均接受长度与加速比

实际加速比由**平均接受token数** $\bar{n}$ 决定，其理论上界为 $\gamma + 1$（所有草稿均被接受且额外获得一个新token）。加速比近似为：

$$\text{Speedup} \approx \frac{\bar{n}}{c + 1}$$

其中 $c$ 为草稿模型相对于目标模型单次前向传播的时间比例。若草稿模型选用目标模型的小版本（如LLaMA-70B + LLaMA-7B），$c \approx 0.1$，$\bar{n} \approx 3$，则加速比约为2.7x。提高草稿模型与目标模型的**token分布对齐程度**（alignment）是提升 $\bar{n}$ 的核心。

### 草稿模型的选择策略

草稿模型并非只有独立小模型一种选择。**Self-speculative decoding**（如Medusa方法，2023）在目标模型的最后隐层上增加多个并行预测头（每个head独立预测未来第k个token），完全消除了草稿模型的额外权重加载开销。另一种方案是**Lookahead Decoding**，完全不依赖草稿模型，而是从上下文n-gram中提取候选序列，适合资源受限的部署场景。

## 实际应用

**代码补全场景**：代码生成任务中草稿模型接受率显著高于自然语言任务，因为代码包含大量重复性语法结构（如括号、缩进、API调用模式），使得草稿模型更容易正确预测。在HumanEval基准上，推测解码对CodeLlama-34B的实测加速比可达3.0x，而通用文本生成任务通常仅为1.7x–2.3x。

**生产级部署（vLLM集成）**：vLLM从0.2.0版本起集成了推测解码支持，通过`speculative_model`参数指定草稿模型。在batch size=1的在线服务场景（高延迟敏感、低吞吐）中效益最大，因为此时单序列的内存带宽瓶颈最为突出。当batch size增大时，目标模型的计算利用率本身提高，推测解码的相对收益会下降。

**Medusa在LLaMA-2上的应用**：在LLaMA-2-13B上，Medusa-1（无需调整基础模型权重，仅微调预测头）实测可达1.8x–2.3x加速；Medusa-2（联合微调预测头与基础模型）可达2.5x–3.6x，但需要额外的微调成本。

## 常见误区

**误区一：推测解码在高batch size下同样有效**。实际上，当batch size增大时，目标模型的每次前向传播已经处理多个序列，GPU的计算利用率上升，内存带宽不再是瓶颈，推测解码的并行验证优势被削弱。在batch size=32以上的吞吐优先场景中，推测解码几乎没有速度收益，甚至可能因草稿生成的额外开销而变慢。

**误区二：可以用任意小模型作为草稿模型**。草稿模型必须与目标模型共享相同的词表（vocabulary）和tokenizer，否则无法进行逐token的概率比较。更重要的是，草稿模型的输出分布需要与目标模型高度对齐——一个与目标模型架构完全不同的小模型（如用GPT-2草稿Llama-3-70B）会导致接受率极低（可能低于0.3），实际速度可能不如直接推理。

**误区三：推测解码改变了模型输出的概率分布**。这是最关键的错误认知。通过上文所述的接受-拒绝采样机制，推测解码在数学上严格保证输出分布与目标模型完全一致，与量化、剪枝等有损压缩方法有根本区别。在使用温度参数（temperature）和Top-p采样时，只需对草稿和验证阶段同样应用这些参数，分布等价性仍然成立。

## 知识关联

**前置知识**：理解推测解码需要掌握Transformer自回归解码的KV Cache机制——验证阶段的并行前向传播需要正确处理草稿token对应的KV Cache写入与回滚（rollback）；以及LLM推理优化中内存带宽瓶颈的roofline模型分析，这直接解释了为何批量验证比逐步生成更高效。

**后续延伸**：推测解码是学习LLM Serving系统（vLLM、TensorRT-LLM、TGI）的重要基础，上述系统在工程实现中均需处理推测解码与PagedAttention、Continuous Batching的协同设计。例如，vLLM中推测解码与Continuous Batching的结合需要特殊的"bonus token"逻辑来处理不同序列接受长度不一致的问题。推测解码的草稿树（draft tree）思想也延伸到了Multi-Candidate Speculative Decoding（SpecTr）和Tree Attention等更高级的采样方法中。