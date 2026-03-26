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
quality_tier: "B"
quality_score: 47.7
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.382
last_scored: "2026-03-22"
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

Transformer架构由Google Brain团队于2017年在论文《Attention Is All You Need》中提出，作者包括Ashish Vaswani等8人。与当时主流的RNN、LSTM序列模型不同，Transformer**完全摒弃了循环结构**，仅依靠注意力机制处理序列数据，这使得训练过程可以充分并行化，从根本上改变了大规模语言模型的可行性。

原始Transformer设计用于机器翻译任务（英德、英法翻译），采用编码器-解码器（Encoder-Decoder）对称结构。编码器将输入序列映射为连续表示，解码器逐步生成目标序列。论文中使用8个注意力头、6层堆叠、512维模型维度的配置，在WMT 2014英德翻译任务上达到28.4 BLEU分，超越了所有已有的集成模型。

Transformer之所以重要，在于它将序列建模的时间复杂度从RNN的O(n)串行步骤改为O(1)层级的并行计算，代价是自注意力的O(n²)空间复杂度。这一权衡在GPU并行硬件上极为有利，直接催生了BERT、GPT系列等现代大模型。

---

## 核心原理

### 编码器-解码器整体结构

原始Transformer由N=6个编码器层和N=6个解码器层堆叠构成。每个**编码器层**包含两个子层：多头自注意力（Multi-Head Self-Attention）和前馈网络（Feed-Forward Network，FFN）。每个**解码器层**则包含三个子层：掩码多头自注意力（Masked Multi-Head Self-Attention）、编码器-解码器交叉注意力（Cross-Attention）、以及FFN。每个子层外均包裹残差连接（Residual Connection）和层归一化（Layer Normalization），即：

$$\text{output} = \text{LayerNorm}(x + \text{Sublayer}(x))$$

其中 $x$ 为子层的输入向量，$\text{Sublayer}(x)$ 为该子层的变换函数。残差连接确保了梯度在深层堆叠中有效流动。

### 前馈网络（FFN）的具体形态

Transformer中每个FFN是一个两层全连接网络，结构为：

$$\text{FFN}(x) = \max(0, xW_1 + b_1)W_2 + b_2$$

在原始论文配置中，输入/输出维度 $d_{model} = 512$，中间层维度 $d_{ff} = 2048$（扩展比例为4倍）。FFN对序列中每个位置**独立且相同**地应用，不跨位置共享计算，这与注意力层的全局交互形成互补——注意力负责位置间信息聚合，FFN负责每个位置的特征变换。

### 解码器的掩码机制与自回归生成

解码器的第一个注意力子层使用**因果掩码（Causal Mask）**，将注意力矩阵的上三角部分设为 $-\infty$（softmax后趋近于0），确保位置 $i$ 只能关注位置 $\leq i$ 的词，防止训练时看到未来词。这一设计使得解码器在训练阶段可以并行计算所有位置的损失，而在推理阶段仍以自回归方式逐词生成，兼顾了训练效率与生成正确性。

### 缩放点积注意力与多头机制

Transformer的注意力公式为：

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

其中 $\sqrt{d_k}$ 是缩放因子，防止点积结果进入softmax的饱和区。原始论文中 $d_k = d_v = 64$，共8个注意力头，每头独立计算后拼接再投影，总输出维度仍为512。多头机制让模型在不同的表示子空间中并行捕捉不同类型的依赖关系。

---

## 实际应用

**机器翻译**是Transformer的原生任务：编码器处理源语言句子，解码器利用交叉注意力从编码器输出中提取对齐信息，生成目标语言。交叉注意力中，Q来自解码器，K和V来自编码器，这是Encoder-Decoder架构独有的信息通道。

**纯编码器变体**（如BERT）去掉解码器，仅用6或12层编码器，配合掩码语言模型（MLM）预训练，适合文本分类、命名实体识别、问答等需要理解全局上下文的任务。BERT-Base使用12层、768维、12头，参数量约1.1亿。

**纯解码器变体**（如GPT系列）去掉编码器和交叉注意力，仅保留带因果掩码的解码器层，适合文本生成任务。GPT-2使用12至48层不等的解码器，全部依赖上文预测下文。这种变体在推理时存在KV Cache优化空间，工程实现中通过缓存每层的K、V矩阵避免重复计算。

**视觉Transformer（ViT）**将图片切分为16×16像素的patch作为"词元"，输入原始Transformer编码器，证明了该架构跨模态的通用性。

---

## 常见误区

**误区一：认为Transformer的并行化是推理阶段的并行化。**
实际上，Transformer的并行优势主要体现在**训练阶段**。编码器对整个输入序列可以完全并行计算。但解码器在推理时仍是自回归串行生成，每生成一个词需要一次前向传播，序列长度n对应n次串行步骤，这是当前大模型推理延迟的主要瓶颈，也是投机采样（Speculative Decoding）等技术的动机所在。

**误区二：认为层归一化的位置是固定的。**
原始论文使用Post-LN（残差加法之后做归一化），但后续研究发现Pre-LN（残差加法之前做归一化）训练更稳定，GPT-2及大多数现代模型改用Pre-LN。公式变为 $\text{output} = x + \text{Sublayer}(\text{LayerNorm}(x))$。两者在深层模型中的梯度行为差异显著，混淆这一点会影响对模型训练不稳定问题的诊断。

**误区三：认为位置信息由注意力机制自动处理。**
Transformer的注意力计算本身对位置顺序完全不敏感——打乱输入序列的顺序，注意力分数集合不变（仅对应关系改变）。位置信息必须通过**额外添加的位置编码**注入模型，原始论文使用正弦/余弦函数，现代模型多改用RoPE（旋转位置编码）等方案。

---

## 知识关联

**前置概念**：注意力机制提供了Transformer的计算核心——缩放点积注意力公式。没有对Q、K、V矩阵的理解，无法分析编码器自注意力与解码器交叉注意力的区别。

**直接延伸**：自注意力与多头注意力详细展开了Transformer内部注意力层的数学细节与工程实现；位置编码专门解决Transformer无序性缺陷的各种方案（正弦编码、学习式编码、RoPE、ALiBi）。

**模型变体**：BERT与编码器模型、GPT与解码器模型分别是Transformer编码器栈和解码器栈的专用化发展路径，理解Transformer原始结构中编码器与解码器的职责划分是区分二者的关键。

**工程链路**：分词与Tokenization处理Transformer的输入侧——词元序列如何从原始文本构建，直接决定了模型的词汇表大小（影响Embedding矩阵参数量）和序列长度（影响O(n²)注意力计算开销）。