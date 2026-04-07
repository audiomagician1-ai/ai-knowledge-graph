---
id: "transformer-architecture"
concept: "Transformer架构"
domain: "ai-engineering"
subdomain: "llm-core"
subdomain_name: "大模型核心"
difficulty: 8
is_milestone: false
tags: ["DL", "NLP"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 74.2
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.944
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# Transformer架构

## 概述

Transformer架构由Google Brain团队于2017年在论文《Attention Is All You Need》中提出，作者包括Ashish Vaswani等8人。它彻底放弃了RNN和CNN中的序列递归或局部卷积操作，完全依赖注意力机制处理序列数据，从根本上改变了自然语言处理领域的技术路线。原始Transformer模型拥有约6500万参数，在WMT 2014英德翻译任务上以28.4 BLEU分数超越了所有此前最优模型。

Transformer之所以成为现代大模型的基础骨架，原因在于其天然支持并行计算。RNN必须按时间步顺序处理序列，无法在序列维度上并行；而Transformer的自注意力层可以同时计算序列中所有位置对之间的关系，使得在大规模GPU集群上的训练效率得到质的提升。正是这一特性使GPT、BERT、LLaMA等千亿级参数模型的训练成为可能。

Transformer的核心架构包含编码器（Encoder）和解码器（Decoder）两个模块，各由6个相同的层堆叠而成（原始论文设定N=6）。编码器负责将输入序列映射为连续表示，解码器则自回归地生成目标序列。后续模型如BERT仅使用编码器，GPT仅使用解码器，证明这两个模块各自具有独立的应用价值。

## 核心原理

### 整体架构与数据流

原始Transformer的编码器由6层堆叠构成，每层包含两个子层：多头自注意力层和前馈神经网络层（FFN）。解码器同样6层，每层包含三个子层：掩码多头自注意力、编码器-解码器注意力（Cross-Attention）、以及FFN。每个子层都使用残差连接（Residual Connection）和层归一化（Layer Normalization），即输出为 `LayerNorm(x + Sublayer(x))`。模型的隐藏维度 `d_model = 512`，前馈层内部维度 `d_ff = 2048`，恰好是 `d_model` 的4倍，这一比例在后续大多数Transformer变体中被沿用。

### 缩放点积注意力机制

Transformer中注意力的核心计算公式为：

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

其中 $Q$（Query）、$K$（Key）、$V$（Value）分别为查询、键、值矩阵，$d_k$ 为键向量的维度。除以 $\sqrt{d_k}$ 是为了防止点积结果在维度较大时进入softmax的梯度饱和区。原始论文中 $d_k = d_v = 64$，因为模型采用8个注意力头（`h=8`），而 $d_k = d_{model}/h = 512/8 = 64$。解码器中的自注意力还引入了掩码（Mask），将未来位置的注意力分数置为 $-\infty$，确保自回归生成时模型无法"看见"未来的词。

### 多头注意力与前馈网络

多头注意力（Multi-Head Attention）并非单纯地运行一次注意力，而是将 $Q$、$K$、$V$ 分别线性投影到 $h$ 个不同的低维子空间，在每个子空间独立计算注意力后拼接结果，再经一次线性变换输出。公式为 $\text{MultiHead}(Q,K,V) = \text{Concat}(\text{head}_1,...,\text{head}_h)W^O$，其中每个 $\text{head}_i = \text{Attention}(QW_i^Q, KW_i^K, VW_i^V)$。多头机制使模型能同时从不同表示子空间捕获语法、语义、指代等多种类型的依存关系。

前馈网络（FFN）在每个位置独立且相同地应用，结构为两层线性变换加ReLU激活：$\text{FFN}(x) = \max(0, xW_1 + b_1)W_2 + b_2$。FFN的作用是在注意力层完成跨位置信息聚合后，对每个位置的表示进行非线性特征变换，两者功能上形成明确分工。

### 位置编码的必要性

由于自注意力对序列中各位置的处理是置换不变的（permutation-invariant），即打乱输入顺序不影响注意力的计算结构，Transformer必须通过位置编码（Positional Encoding）显式注入位置信息。原始论文使用正弦/余弦函数生成位置编码，维度与词嵌入相同（512维），直接与词嵌入相加后输入模型。这与RNN依靠时序展开隐式编码位置的方式形成本质区别。

## 实际应用

**机器翻译**：Transformer的最初设计场景即机器翻译，完整的编码器-解码器结构负责将源语言序列映射为目标语言序列。谷歌在2017年将Transformer部署到Google翻译，对100多种语言对的翻译质量产生了显著提升。

**大语言模型预训练**：GPT系列（OpenAI）仅使用Transformer解码器堆叠，GPT-3使用了96层解码器、`d_model=12288`，共1750亿参数。BERT使用12层（Base版）或24层（Large版）Transformer编码器，在11项NLP任务上刷新了记录。这两条路线均直接源于原始Transformer的模块化设计。

**多模态场景**：Vision Transformer（ViT）将图像切分为16×16的图像块（patch），每个块展平后线性投影为向量序列，送入标准Transformer编码器处理，在ImageNet上首次证明纯Transformer架构在图像分类领域可匹敌CNN。

## 常见误区

**误区一：认为Transformer的注意力能无限扩展到任意长序列**。实际上，自注意力的时间和空间复杂度均为 $O(n^2)$，其中 $n$ 为序列长度。当序列长度达到8192以上时，标准Transformer的内存消耗会变得极为昂贵。这正是Longformer、FlashAttention等技术试图解决的问题，其中FlashAttention通过IO感知的分块计算将显存占用降低至近似 $O(n)$。

**误区二：认为残差连接只是防止梯度消失的辅助手段**。在Transformer中，残差连接还承担着保留原始位置信息的功能——若无残差，经过6层注意力后，各位置的表示会被多次混合，位置区分度大幅下降。实验表明，去除残差连接后Transformer在训练深度超过4层时性能急剧恶化，而并非仅仅是梯度消失问题。

**误区三：混淆编码器与解码器的注意力掩码策略**。编码器的自注意力不使用因果掩码，每个位置可以看到整个输入序列（双向注意力）；解码器的自注意力使用因果掩码（causal mask），每个位置只能看到它之前的位置。解码器的第二个子层（Cross-Attention）中，Query来自解码器，Key和Value来自编码器输出，这与纯自注意力有本质不同。

## 知识关联

**前置概念**：注意力机制是理解Transformer的直接基础，Transformer中的缩放点积注意力是对Bahdanau注意力（2014年提出）的简化与加速版本，去除了对齐网络，改为直接点积计算。理解Query-Key-Value三元组的含义，是读懂Transformer代码的前提。

**后续分支**：自注意力与多头注意力是Transformer内部机制的深化，位置编码是其并行化带来的特有问题的解决方案，二者都是Transformer的组成部分。在模型方向上，BERT是将Transformer编码器用于预训练的代表，GPT是将解码器用于自回归语言模型的代表，二者分别定义了"理解型"和"生成型"大模型两条主线。此外，分词与Tokenization决定了输入序列 $n$ 的实际长度，直接影响Transformer的计算代价，与架构设计密切耦合。