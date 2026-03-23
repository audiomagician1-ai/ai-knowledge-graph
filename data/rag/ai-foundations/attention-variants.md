---
id: "attention-variants"
concept: "注意力机制变体"
domain: "ai-engineering"
subdomain: "ai-foundations"
subdomain_name: "AI基础"
difficulty: 5
is_milestone: false
tags: ["attention", "multi-head", "flash-attention"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 46.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.433
last_scored: "2026-03-23"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 注意力机制变体

## 概述

注意力机制变体是在原始Scaled Dot-Product Attention（2017年Vaswani等人提出）基础上发展出的一系列改进方案，每种变体针对原始机制的特定缺陷——计算复杂度O(n²)、跨序列信息融合、稀疏激活效率——设计了不同的结构解法。理解这些变体的差异，本质上是理解如何在表达能力、计算效率和适用场景之间做出工程权衡。

原始注意力公式为 `Attention(Q,K,V) = softmax(QKᵀ/√dₖ)V`，其中√dₖ是缩放因子（dₖ为key的维度），用于防止点积过大导致梯度消失。Multi-Head Attention在2017年"Attention is All You Need"论文中同步提出；Cross Attention伴随编码器-解码器架构出现；而Sparse Attention（2019年）和FlashAttention（2022年）则是为解决序列长度扩展问题而生的工程性创新。这四种变体目前覆盖了90%以上的实际Transformer应用场景。

## 核心原理

### Multi-Head Attention（多头注意力）

Multi-Head Attention的核心思想是将Q、K、V分别线性投影到h个子空间，每个头独立计算注意力后拼接输出，再经过一次线性变换。公式为：

```
MultiHead(Q,K,V) = Concat(head₁,...,headₕ)Wᴼ
headᵢ = Attention(QWᵢQ, KWᵢK, VWᵢV)
```

使用h=8个头时，每个头的维度是dₘₒdₑₗ/h（GPT-3中dₘₒdₑₗ=12288，h=96，每头维度128）。多头机制允许模型在不同表示子空间同时捕捉不同类型的依赖关系——例如句法关系、语义共指、位置邻近性——这是单头注意力无法做到的。参数量代价是4个投影矩阵：WQ、WK、WV（每个形状为dₘₒdₑₗ×dₖ）和Wᴼ（dᵥ×dₘₒdₑₗ）。

### Cross Attention（交叉注意力）

Cross Attention与Self-Attention的根本区别在于Q和K/V来自不同序列。具体地：Q来自解码器的当前状态，K和V来自编码器的输出（固定）。这使得解码器的每个位置都能"查询"完整的编码器上下文，公式结构与标准注意力相同，但Q矩阵维度为`[target_len, dₘₒdₑₗ]`，而K/V维度为`[source_len, dₘₒdₑₗ]`。

Cross Attention是机器翻译、图像描述生成（如BLIP模型）和扩散模型中文本-图像对齐的核心机制。在Stable Diffusion中，Cross Attention将文本token的K/V注入U-Net的各个分辨率层，实现文本条件对图像生成的控制，这一过程与语言翻译中的解码器对编码器的注意力机制完全同构。

### Sparse Attention（稀疏注意力）

标准注意力对长度n的序列计算复杂度为O(n²)，当n=4096时注意力矩阵需要存储4096×4096=16M个float16值（约32MB）。Sparse Attention（OpenAI 2019年提出于Sparse Transformer）通过限制每个token只关注其邻域内的固定模式将复杂度降至O(n√n)。

稀疏模式主要有三类：
- **局部窗口**：每个token只关注前后w个token（BigBird中w=3）
- **跨步模式（strided）**：每隔k步选一个token，捕捉全局结构
- **全局token**：少数特殊token（如[CLS]）关注所有位置

Longformer将局部窗口（大小512）和全局token结合，在处理16384 token序列时，内存占用仅为标准注意力的约1/32。

### FlashAttention（快速注意力）

FlashAttention（Tri Dao等，2022年，NeurIPS）不改变注意力的数学定义，而是通过**分块计算（tiling）**重新设计GPU内存访问模式。标准注意力需要将n×n的注意力矩阵写入HBM（高带宽内存），FlashAttention将Q/K/V分块加载到SRAM（片上内存，带宽约19TB/s，而A100 HBM仅2TB/s），在不完整写出注意力矩阵的情况下利用数值稳定的online softmax算法完成计算。

FlashAttention v2（2023年）在A100上实现了约73%的理论FLOPs利用率，比标准PyTorch实现快2-4倍，且内存复杂度从O(n²)降至O(n)。关键公式是将softmax分块计算的数值稳定技巧：维护局部最大值mᵢ和归一化项lᵢ，逐块更新全局softmax而无需重新访问历史块。

## 实际应用

**BERT/GPT类预训练模型**使用Multi-Head Self-Attention，GPT-4据估计使用96-128个注意力头，每层参数约占模型总参数的1/3。在推理优化中，Multi-Head KV Cache机制会缓存所有头的K/V矩阵，导致批量推理时显存占用与序列长度线性增长。

**文档级长文本处理**（如法律文件、基因序列分析）依赖Sparse Attention变体。BigBird通过随机+局部+全局的组合稀疏模式，将BERT的512 token限制扩展到4096 token，在长文档QA任务（如TriviaQA）上获得显著提升。

**LLM训练加速**中FlashAttention已成为标配：LLaMA-2、Mistral 7B、Falcon等主流开源模型训练均使用FlashAttention，其2倍以上的速度提升直接降低了训练成本。Multi-Query Attention（MQA）是FlashAttention之外另一个关键推理优化：所有head共享同一组K/V矩阵，KV Cache降低至原来的1/h，Gemini和PaLM-2均采用此方案。

**扩散模型**中的Cross Attention层是Prompt与图像特征交互的位置，Prompt Attention Map可视化技术（Prompt-to-Prompt, ICCV 2023）通过直接编辑Cross Attention图来实现图像局部编辑，证明了Cross Attention层的语义定位能力。

## 常见误区

**误区一：认为Multi-Head Attention的多个头会自动学到"互补"的信息**。实验（Michel et al., 2019 "Are Sixteen Heads Really Better than One?"）表明，BERT中修剪掉大多数注意力头对性能影响极小，部分层仅保留1个头仍能维持接近原始性能。多头并不总是互补——它提供了学习多样化特征的**潜力**，但不保证利用率。

**误区二：认为FlashAttention改变了注意力机制的表达能力或近似结果**。FlashAttention是一个精确算法（exact attention），数学上与标准注意力完全等价，仅是I/O复杂度优化。相比之下，Sparse Attention和线性注意力（如Performer用核函数近似softmax）才是以近似换效率的方案，二者不可混淆。

**误区三：Sparse Attention在所有任务上都优于密集注意力**。在序列长度较短（如512以内）时，Sparse Attention的索引开销和不规则内存访问模式实际上比密集注意力**更慢**。Sparse Attention的优势只在序列长度超过某个阈值（通常1024-2048以上）时才开始显现，对短序列任务强行使用稀疏注意力是常见的过度优化错误。

## 知识关联

掌握注意力机制变体需要以**Scaled Dot-Product Attention**的原始公式和梯度特性为前提，理解为何√dₖ缩放是必要的（防止高维空间中向量点积的方差随dₖ线性增长）。同时需要具备**Transformer编码器-解码器架构**的结构知识，才能理解Cross Attention中Q/K/V分属不同序列的设计动机。

在工程实践中，这四种变体并非互斥选择：LLaMA-2同时使用了Multi-Head Attention（表达能力）、RoPE位置编码（位置感知）、FlashAttention（训练效率）和GQA（Grouped-Query Attention，推理效率），体现了多种变体在同一系统中的协同部署。未来方向包括线性注意力（Mamba的SSM架构可视为其极端情形）和稀疏-密集混合架构（Mixture of Experts与稀疏注意力的结合），这些方向均以本文四种变体为基础进行扩展。
