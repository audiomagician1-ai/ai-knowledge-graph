---
id: "self-attention"
concept: "自注意力与多头注意力"
domain: "ai-engineering"
subdomain: "llm-core"
subdomain_name: "大模型核心"
difficulty: 8
is_milestone: false
tags: ["Transformer"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 49.5
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.424
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 自注意力与多头注意力

## 概述

自注意力（Self-Attention）是一种让序列中每个位置的表示都能直接"看到"并融合序列内所有其他位置信息的机制。与传统的循环神经网络（RNN）不同，自注意力不依赖时间步递推，而是在单次前向计算中通过相似度加权求和实现全局上下文建模。2017年，Vaswani等人在论文《Attention is All You Need》中将自注意力作为Transformer的核心计算单元，彻底替代了LSTM在序列建模中的主导地位。

多头注意力（Multi-Head Attention）是对自注意力的扩展：将输入投影到 $h$ 个独立子空间中分别计算注意力，再将所有头的输出拼接后线性变换回原始维度。原始Transformer使用 $h=8$ 个头，模型维度 $d_{model}=512$，每个头的维度 $d_k=d_v=64$。多头设计的价值在于让模型同时捕捉不同类型的依赖关系——例如一个头专注于句法依存，另一个头专注于语义共指，这种专业化分工已被大量可视化分析实验证实。

## 核心原理

### 缩放点积注意力公式

自注意力的数学核心是**缩放点积注意力**（Scaled Dot-Product Attention）：

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

其中：
- $Q$（Query）、$K$（Key）、$V$（Value）均由同一输入序列 $X$ 线性投影得到，即 $Q=XW^Q$、$K=XW^K$、$V=XW^V$，这正是"自"注意力名称的来源——三者来自同一来源。
- $d_k$ 是 Key 向量的维度。除以 $\sqrt{d_k}$ 是为了防止当 $d_k$ 较大时点积结果进入 softmax 的饱和区，导致梯度消失。若 $d_k=64$，则缩放因子为 $1/8$。
- 点积 $QK^T$ 得到形状为 $[seq\_len \times seq\_len]$ 的**注意力得分矩阵**，每行经 softmax 归一化后成为对 $V$ 加权求和的系数。

### 多头注意力的拼接机制

多头注意力的计算步骤为：

$$\text{MultiHead}(Q,K,V) = \text{Concat}(\text{head}_1, \ldots, \text{head}_h)W^O$$

$$\text{head}_i = \text{Attention}(QW_i^Q, KW_i^K, VW_i^V)$$

其中每个头拥有独立的投影矩阵 $W_i^Q \in \mathbb{R}^{d_{model} \times d_k}$、$W_i^K \in \mathbb{R}^{d_{model} \times d_k}$、$W_i^V \in \mathbb{R}^{d_{model} \times d_v}$，以及最终的输出投影 $W^O \in \mathbb{R}^{hd_v \times d_{model}}$。以原始Transformer为例，8个头每头64维，拼接后得到512维，再通过 $W^O$ 映射回512维。整个多头注意力层的参数量为 $4 \times d_{model}^2$（分别来自 $W^Q, W^K, W^V, W^O$ 四个矩阵）。

### 计算复杂度与全局依赖

自注意力的计算复杂度为 $O(n^2 \cdot d)$，其中 $n$ 是序列长度，$d$ 是模型维度。这一平方复杂度来源于 $QK^T$ 矩阵乘法，是自注意力在长序列场景下（如处理8K以上token时）面临的核心瓶颈，直接驱动了FlashAttention和稀疏注意力等优化方案的诞生。与此同时，自注意力中任意两个位置之间的最大路径长度为1（与序列长度无关），而RNN中这一路径长度为 $O(n)$，这解释了Transformer在捕捉长距离依赖上的优势。

## 实际应用

**GPT系列的因果自注意力（Causal Self-Attention）**：在自回归语言模型中，自注意力矩阵会施加一个下三角掩码（causal mask），将注意力得分矩阵上三角部分置为 $-\infty$，经softmax后归零，确保位置 $i$ 只能看到位置 $\leq i$ 的信息。GPT-3使用96个注意力头、$d_{model}=12288$，每头维度为128。

**BERT的双向自注意力**：BERT不使用因果掩码，每个token可以同时关注前后文，配合MLM预训练目标，BERT-base设置12头、$d_{model}=768$，BERT-large设置16头、$d_{model}=1024$。这种双向注意力设计使BERT在分类、问答等理解任务上表现优秀，但无法直接用于生成。

**多头注意力的头专业化现象**：在BERT的可解释性研究（Vig & Belinkov, 2019）中，研究者发现不同注意力头呈现出分工，例如某些头专门关注直接宾语关系，某些头关注的是句子末尾的句号。这一发现表明多头设计并非冗余，而是产生了有意义的功能分化。

## 常见误区

**误区一：认为Q、K、V是三个不同来源的输入**。在普通的交叉注意力（Cross-Attention）中，Q来自解码器、K和V来自编码器，确实有两个不同来源。但自注意力的关键特征是Q、K、V均从**同一输入序列**通过不同的线性投影得到。混淆这一点会导致对Encoder-only和Decoder-only模型机制的误解。

**误区二：认为增加注意力头数总能提升性能**。注意力头数 $h$ 受模型维度 $d_{model}$ 约束，$d_k = d_{model}/h$。若 $h$ 过大，每头的子空间维度 $d_k$ 会过小，限制每个头表达复杂模式的能力。研究表明，在固定参数量下，并非头数越多越好——Llama 2的7B版本使用32头，而将头数翻倍但缩小 $d_k$ 并不总能带来收益。

**误区三：认为注意力权重直接等于词语的"重要性"**。softmax产生的注意力分布会受到数值初始化、残差连接和LayerNorm的影响，某些研究（Jain & Wallace, 2019）指出注意力权重与特征归因方法（如梯度×输入）的结论经常不一致。直接用注意力权重做模型可解释性分析需要谨慎。

## 知识关联

理解自注意力需要先掌握**注意力机制**的基础概念——特别是Bahdanau在2015年提出的加性注意力，它定义了Query-Key-Value三元组的雏形；以及**Transformer架构**中的位置编码（Positional Encoding），因为自注意力本身对序列位置是排列不变的（permutation invariant），必须显式注入位置信息才能区分"猫追狗"和"狗追猫"。

自注意力中 $QK^T$ 产生的 $[n \times n]$ 注意力矩阵和缓存机制直接引出下一个核心概念**KV Cache**：在自回归推理时，每个新token只需计算其自身的Q，而历史token的K和V可以缓存复用，将推理时的注意力计算从 $O(n^2)$ 降低为每步 $O(n)$，这是大模型推理加速的基础技术。而 $O(n^2)$ 的显存占用和数值精度问题则引出**FlashAttention**——它通过分块（tiling）计算和在线softmax技术，在不改变数学等价性的前提下将显存复杂度从 $O(n^2)$ 降至 $O(n)$，使得长上下文训练成为可能。