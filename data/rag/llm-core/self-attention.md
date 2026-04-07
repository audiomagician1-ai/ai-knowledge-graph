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
quality_tier: "A"
quality_score: 78.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.966
last_scored: "2026-04-07"
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

自注意力（Self-Attention）是一种让序列中每个位置的表示都能直接参考序列内所有其他位置的机制，区别于传统注意力机制中"编码器-解码器"跨序列查询的模式。在自注意力中，Query、Key、Value三组向量均来自**同一输入序列**的线性变换，这意味着一个词的最终表示会动态融合整句话中所有词的信息，而不依赖任何递归或卷积操作。

自注意力由Vaswani等人于2017年在论文《Attention Is All You Need》中系统化提出，随即成为Transformer架构的基石。在此之前，LSTM和GRU通过时序递推来建立长距离依赖，信息在传递过程中会逐步衰减；而自注意力的任意两个位置之间路径长度恒为O(1)，彻底消除了长距离依赖的衰减问题。

多头注意力（Multi-Head Attention）在自注意力基础上并行运行h个独立的注意力头，每个头学习不同的线性投影子空间，捕捉不同语义维度的依赖关系。GPT-3使用96个注意力头，每头维度为128，这种设计使模型能同时建模句法依赖、指代关系、语义相似性等异构模式。

---

## 核心原理

### 缩放点积注意力公式

自注意力的核心计算由以下公式定义：

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

其中：
- **Q**（Query矩阵）= 输入矩阵 × W_Q，形状为 [seq_len, d_k]
- **K**（Key矩阵）= 输入矩阵 × W_K，形状为 [seq_len, d_k]
- **V**（Value矩阵）= 输入矩阵 × W_V，形状为 [seq_len, d_v]
- **√d_k** 是缩放因子，防止点积结果过大导致softmax梯度消失

缩放因子的必要性可以量化说明：当 d_k = 512 时，未缩放的点积方差为512，softmax输入值可达数十甚至上百，梯度接近于零；除以√512 ≈ 22.6后，方差恢复为1，训练稳定性大幅提升。

### 三矩阵投影的本质

Q、K、V并非直接等于输入，而是通过三组独立的可学习权重矩阵 W_Q、W_K、W_V 投影得到。这种分离设计的关键意义在于：Q与K控制"哪些位置对当前位置重要"（即注意力权重分布），V控制"重要位置贡献什么内容"（即输出的实际信息）。将相关性计算与内容读取解耦，使模型可以独立优化这两个目标。以BERT-base为例，d_model=768，d_k=d_v=64，每层有12个头，W_Q/W_K/W_V各自形状均为 [768, 64]。

### 多头注意力的并行投影机制

多头注意力将h个注意力头的输出拼接后再线性变换：

$$\text{MultiHead}(Q,K,V) = \text{Concat}(\text{head}_1, \ldots, \text{head}_h) \cdot W_O$$

$$\text{head}_i = \text{Attention}(QW_i^Q,\ KW_i^K,\ VW_i^V)$$

每个头有独立的投影矩阵 W_i^Q、W_i^K、W_i^V（维度为 [d_model, d_k]）和共享的输出矩阵 W_O（维度为 [h·d_v, d_model]）。为保持参数量可控，通常令 d_k = d_v = d_model/h，这使得多头注意力总参数量与单头注意力相同，但表达能力显著增强。实验表明，不同注意力头自发学习了不同语言结构：某些头专注于直接宾语关系，某些头追踪指代链，某些头捕捉邻近词的局部依赖。

### 掩码自注意力（Masked Self-Attention）

在自回归语言模型（如GPT系列）的解码阶段，需要防止当前位置"看见"未来位置的token，通过在softmax之前将未来位置的注意力分数设为 -∞ 来实现因果掩码：

$$\text{score}_{ij} = \begin{cases} \frac{q_i \cdot k_j}{\sqrt{d_k}} & j \leq i \\ -\infty & j > i \end{cases}$$

经过softmax后，-∞ 对应的权重变为0，保证自回归生成的因果一致性。

---

## 实际应用

**BERT的双向自注意力**：BERT使用完整（非掩码）自注意力，序列中每个位置均可关注所有其他位置，这是其做完形填空预训练（MLM）的前提。BERT-Large的每层24个注意力头共同处理512个token的序列，生成上下文感知的词向量，直接推动了NLP任务的大规模迁移学习。

**GPT系列的因果自注意力**：GPT-2（1.5B参数）使用48层Transformer，每层16个注意力头，采用因果掩码自注意力保证自回归生成。生成"Paris is the capital of"时，注意力权重可视化显示"capital"位置的注意力头会强烈关注"Paris"，而忽略后续padding位置。

**多查询注意力（MQA）与分组查询注意力（GQA）**：为解决推理时K/V矩阵的内存带宽瓶颈，Llama 2的34B和70B版本采用GQA，将32个Query头分为8组，每组共享1组K/V头，将KV Cache大小压缩为标准多头注意力的1/4，推理吞吐量提升约2倍，同时精度损失极小。

---

## 常见误区

**误区一：认为注意力权重直接等于语义相关性**
注意力权重是经softmax归一化的概率分布，每个位置的权重之和为1，这是一种强约束。实际上，一个头可能在某位置将99%的权重集中于某个标点符号，并非因为该符号语义重要，而是模型学到了该位置"无需关注其他内容"的特殊模式。直接解读注意力权重为语义相关性是不准确的，Jain & Wallace（2019年）的研究已证明注意力权重与特征重要性之间无必然对应关系。

**误区二：混淆自注意力与交叉注意力的Q/K/V来源**
自注意力中Q、K、V全部来自同一序列，而Transformer编解码架构中解码器的交叉注意力层Q来自解码器隐状态、K和V来自编码器输出。混淆两者会导致对seq2seq模型数据流的严重误解。在实现时，判断依据很简单：如果三个线性层的输入张量相同，则为自注意力；如果Q输入与K/V输入不同，则为交叉注意力。

**误区三：认为增加注意力头数总能提升性能**
多头注意力中，头数h与每头维度 d_k=d_model/h 成反比。过多的头（过小的 d_k）会使每个子空间表达能力严重受限。论文《Are Sixteen Heads Really Better than One?》（Michel等，2019年）实验发现，BERT中约70%的注意力头在测试时可以直接剪除而性能损失不超过1%，盲目增加头数无益于模型质量。

---

## 知识关联

**前置概念连接**：理解注意力机制中Bahdanau（2015年）提出的加性注意力有助于对比：加性注意力用MLP计算相关性，计算复杂度高；自注意力改用点积并增加缩放，使计算可以表达为矩阵乘法，从而充分利用GPU并行算力。Transformer架构中的位置编码（Positional Encoding）是自注意力的必要补充，因为自注意力本身对输入顺序完全无感，需要外部注入位置信息。

**后续概念延伸**：KV Cache技术直接针对多头注意力中Key、Value矩阵的重复计算问题而设计——自回归生成时每新增一个token只需计算该token的K/V并追加到缓存，而非重算整个序列，将生成延迟从O(n²)降低为O(n)。FlashAttention则针对标准自注意力实现中 QK^T 中间矩阵必须写入HBM（高带宽内存）的I/O瓶颈，通过分块计算（Tiling）将注意力计算的内存访问复杂度从O(n²)降至O(n)，在A100 GPU上实现了相比标准实现2-4倍的速度提升。