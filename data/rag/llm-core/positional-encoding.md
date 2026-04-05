---
id: "positional-encoding"
concept: "位置编码"
domain: "ai-engineering"
subdomain: "llm-core"
subdomain_name: "大模型核心"
difficulty: 7
is_milestone: false
tags: ["Transformer"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "S"
quality_score: 89.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 位置编码

## 概述

位置编码（Positional Encoding）是Transformer架构中用于向模型注入序列顺序信息的机制。由于自注意力机制（Self-Attention）本身对输入序列的排列是置换等变（permutation equivariant）的——即将"我爱你"和"你爱我"打乱后输入，纯注意力层会产生相同的权重分布——模型无法区分第1个token与第3个token的位置差异。位置编码通过在词嵌入之后叠加或融合位置信号，打破这种对称性。

位置编码的概念由Vaswani等人在2017年论文《Attention Is All You Need》中正式提出。原始论文中采用的是正弦余弦函数构造的**绝对位置编码**，公式为：

$$PE_{(pos, 2i)} = \sin\left(\frac{pos}{10000^{2i/d_{model}}}\right), \quad PE_{(pos, 2i+1)} = \cos\left(\frac{pos}{10000^{2i/d_{model}}}\right)$$

其中 $pos$ 是token在序列中的绝对位置，$i$ 是维度索引，$d_{model}$ 是嵌入维度。这种设计让相邻位置的编码差异具有连续性，且能通过线性变换表达相对位移。

位置编码对大语言模型的实际性能影响深远：不同的位置编码方案直接决定了模型的**上下文长度外推能力**。GPT-2使用可学习绝对位置编码，上下文长度硬限制在1024；而RoPE等相对位置编码方案让LLaMA-3支持到128K token的上下文窗口。

---

## 核心原理

### 绝对位置编码（Absolute Positional Encoding）

绝对位置编码为序列中每个位置分配一个固定或可学习的向量，与词嵌入相加后送入后续层。

- **正弦编码（Sinusoidal PE）**：使用上述正弦余弦公式生成，无需训练参数，不同频率的正弦波覆盖不同粒度的位置信息。10000这个底数经过实验选取，保证在序列长度达到数千时不同位置仍有可区分的编码。
- **可学习绝对位置编码（Learned PE）**：BERT和GPT系列采用此方案，为每个位置维护一个可训练的嵌入向量。优点是可适配训练数据中的位置分布；缺点是无法外推到训练时未见过的序列长度（如BERT仅支持512 token）。

两者均通过 $\text{Input} = \text{WordEmbedding} + \text{PE}$ 的加法融合，维度均为 $d_{model}$。

### 相对位置编码（Relative Positional Encoding）

相对位置编码不为每个绝对位置分配固定向量，而是在注意力计算中直接编码两个token之间的**相对距离**。代表方案包括：

- **Shaw et al. (2018) 相对位置编码**：在点积注意力中引入可学习的相对位置偏置矩阵 $r_{i-j}$，注意力得分修改为 $e_{ij} = \frac{(x_i W^Q)(x_j W^K + r_{i-j})^T}{\sqrt{d_k}}$。
- **T5 Bias（2020）**：Google T5模型将相对位置折叠为分桶（bucket）形式，距离超过128的token共享同一位置偏置，显著减少参数量，且具备一定外推能力。
- **ALiBi（2021）**：在注意力得分矩阵上直接加一个与距离成比例的负数偏置 $-m \cdot |i-j|$，其中 $m$ 是预定义的每个注意力头对应的斜率（共8个注意力头时斜率从 $2^{-1}$ 到 $2^{-8}$），完全无需额外参数。

### 外推性（Length Extrapolation）

外推性是衡量位置编码质量的核心指标：模型在训练时使用序列长度 $L_{train}$，推理时能否处理更长的序列 $L_{test} > L_{train}$。

- 正弦编码理论上可外推（编码函数定义在全整数域），但实际因注意力权重分布偏移而性能下降。
- 可学习绝对编码几乎无法外推，超出训练长度后查找表越界。
- ALiBi和RoPE通过对相对距离的显式建模，具备较好外推或内插能力。

---

## 实际应用

**BERT的512 token限制**直接来源于其可学习位置嵌入矩阵的大小为 $512 \times 768$。若将输入序列截断到512以内，性能完整；超出则需要额外的位置插值技巧（如Position Interpolation）才能扩展到更长文本。

**长文档处理中的位置压缩**：对于需要处理数万token的场景，LongFormer（2020）采用局部窗口注意力配合全局token，每个位置仅与窗口内（如512个）相邻token计算位置相关注意力，将复杂度从 $O(n^2)$ 降至 $O(n \cdot w)$，这依赖于相对位置编码的局部化特性。

**代码补全任务中的位置语义**：在StarCoder、CodeLlama等代码模型中，位置编码不仅需要表达行内token顺序，还需在Fill-in-the-Middle（FIM）任务中处理前缀、后缀、中间段的位置关系。这类模型通常采用RoPE以支持较长上下文，并通过特殊token区隔不同代码段。

---

## 常见误区

**误区一：位置编码与词嵌入相乘而非相加**

标准Transformer（含BERT、GPT系列）均使用**加法**融合位置信息：$z = E_{word} + E_{pos}$，维度对齐即可直接叠加。乘法融合在原始论文中并未使用，部分变体（如MAGNETO）虽探索了门控机制，但基础架构仍以加法为主。将两者混淆会导致实现时出现错误的位置信号。

**误区二：正弦位置编码能完美外推到任意长度**

正弦编码函数虽定义在全整数域，但模型的注意力层在训练时仅见过长度 $L_{train}$ 内的位置差组合，超出范围后注意力权重的数值分布会偏离训练分布。实验表明，直接外推到 $2 \times L_{train}$ 时，正弦编码的困惑度（Perplexity）会明显升高，需结合位置插值（Position Interpolation，PI）才能有效扩展。

**误区三：相对位置编码与绝对位置编码不可共存**

部分模型（如DeBERTa）同时使用绝对位置编码和相对位置编码：相对编码处理局部依赖，绝对编码在最后几层提供全局位置意识。DeBERTa-v2在SQuAD 2.0上的F1达到90.7%，其双位置编码设计被认为是关键贡献之一。

---

## 知识关联

**前置知识：Transformer架构**中的多头自注意力机制说明了为何需要位置编码——注意力的点积计算 $QK^T$ 对token顺序不敏感，位置编码正是为补偿这一信息缺失而引入的。理解 $d_{model}$、注意力头数、序列长度等参数含义是掌握位置编码公式的基础。

**后继概念：RoPE（Rotary Position Embedding）**是在绝对与相对位置编码基础上提出的旋转式位置编码，于2021年由苏剑林提出，将位置信息以旋转矩阵形式融入Query和Key向量，公式为 $f(x, m) = x e^{im\theta}$（复数形式）。RoPE同时具备相对位置信息的自然表达和外推能力，已成为LLaMA、Mistral、Qwen等主流开源模型的标配，是学习大模型上下文扩展技术的直接入口。