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
quality_tier: "pending-rescore"
quality_score: 42.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.414
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 位置编码

## 概述

位置编码（Positional Encoding）是 Transformer 架构中用于向模型注入序列顺序信息的技术机制。由于 Transformer 的自注意力机制在计算时对所有位置并行处理，其本身对"第1个词"和"第5个词"没有任何区分能力——若不加入位置信息，"猫吃鱼"和"鱼吃猫"在模型眼中将产生完全相同的表示。位置编码正是为了解决这一根本性缺陷而设计的。

位置编码在2017年由 Vaswani 等人发表的论文《Attention Is All You Need》中首次提出，论文中提供了基于三角函数的固定编码方案（Sinusoidal Positional Encoding）。该方案使用正弦和余弦函数的不同频率对位置进行编码，使模型能够感知词与词之间的相对距离关系。此后，BERT（2018）等模型转而使用可学习的绝对位置嵌入（Learned Positional Embedding），将位置编码作为可训练参数进行优化。

位置编码的设计质量直接影响模型处理长文本的能力和泛化表现。早期 BERT 的位置编码最大支持长度仅为512个 token，GPT-2 支持1024个 token，这成为限制大模型处理长上下文的关键瓶颈之一。现代大模型对位置编码机制的改进（如 RoPE、ALiBi）已成为推动上下文窗口从数千扩展到百万 token 的核心技术路径。

---

## 核心原理

### 正弦余弦位置编码（Sinusoidal PE）

原始 Transformer 论文提出的编码公式为：

$$PE_{(pos, 2i)} = \sin\left(\frac{pos}{10000^{2i/d_{model}}}\right)$$

$$PE_{(pos, 2i+1)} = \cos\left(\frac{pos}{10000^{2i/d_{model}}}\right)$$

其中 $pos$ 为词在序列中的绝对位置（从0开始），$i$ 为编码向量的维度索引，$d_{model}$ 为模型隐层维度（原论文为512）。该公式的关键特性是：两个位置 $pos$ 和 $pos+k$ 之间的关系可以用一个线性变换矩阵来表示，因此模型可以学习到相对位置关系，而不仅仅是绝对位置。基频1/10000被选定使得不同维度对应的波长从 $2\pi$ 到 $10000 \cdot 2\pi$ 呈几何级数分布，覆盖从局部到全局的多粒度距离信息。

位置编码向量与词嵌入向量直接**相加**（而非拼接），最终输入为 $x_{pos} = \text{Embedding}(token) + PE_{pos}$。这一加法设计让位置信息渗透进每一个维度，同时保持输入向量维度不变。

### 可学习绝对位置嵌入（Learned PE）

BERT 和早期 GPT 系列采用可学习位置嵌入，即为每个位置索引 0, 1, 2, …, N-1 分配一个独立的 $d_{model}$ 维可训练向量，随反向传播更新。与 Sinusoidal PE 不同，Learned PE 不具有外推能力——模型在训练时从未见过第513个位置，推理时遇到超出训练长度的 token 时表现会急剧下降。这就是 BERT 系列模型受限于512 token 上下文的根本原因。

实验对比（原始 Transformer 论文 Table 3）显示，Sinusoidal PE 与 Learned PE 在标准 WMT 翻译任务上性能差距不超过0.1 BLEU，但 Sinusoidal PE 在超出训练长度的序列上保持更好的泛化性。

### 绝对位置编码 vs. 相对位置编码

绝对位置编码为每个位置赋予全局唯一的向量，模型需要间接推断两个 token 的相对距离。相对位置编码（Relative PE）直接在注意力矩阵计算时引入位置差 $(i-j)$ 的偏置，代表方案有 Shaw 等人2018年提出的 Relative Position Representations，以及 T5 模型使用的 Relative Bias。

T5 的相对位置方案将距离分桶（bucketed），对超过128个 token 间隔的位置差使用对数间距分桶，共使用32个桶，每个注意力头学习独立的偏置标量。这使得 T5 在推理时可以处理超过训练长度的序列，但长距离衰减特性与 RoPE 相比仍不理想。

---

## 实际应用

**ViT（视觉 Transformer）中的二维位置编码**：ViT（2020）将图像分割为 $16\times16$ 的 patch，共196个 patch（对224×224图像），同样需要位置编码。实验发现1D Learned PE（将二维图像展平为196个位置）与2D PE性能相近，说明模型可通过自注意力机制自行学习二维空间关系，但在更高分辨率时2D编码的优势才会显现。

**GPT 系列的位置编码实践**：GPT-1 和 GPT-2 使用最大长度分别为512和1024的 Learned PE。GPT-3（2020）将上下文窗口扩展至2048，同样采用 Learned PE，但训练数据中超过1024 token 的样本占比有限，导致极长上下文质量不稳定。这一缺陷直接推动了后续 LLaMA、Mistral 等模型转向 RoPE。

**位置编码的外推问题**：当推理序列长度超过训练长度时，绝对位置编码方案的困惑度（Perplexity）往往出现"悬崖式"崩塌。研究显示，LLaMA-2（训练长度4096）在推理长度超过4096后，PPL 从约5迅速升至数百，表明传统绝对位置编码完全丧失对训练外位置的预测能力。

---

## 常见误区

**误区1：位置编码只影响词序，不影响语义理解**
位置编码与词嵌入相加后共同进入注意力计算，位置信息会直接影响 Query/Key/Value 矩阵的内积结果，进而改变注意力权重分布。换言之，同一个词"苹果"在句首（pos=0）和句尾（pos=15）产生的注意力模式是不同的，模型捕捉的语义依存关系也会因此变化。

**误区2：Sinusoidal PE 具有完美的长度外推能力**
正弦编码的确在数学上可以生成任意位置的编码，但这不意味着模型训练后可以无损地推断超训练长度的位置。自注意力中的 softmax 归一化操作会导致长序列中的注意力得分分布与训练时差异极大，实际外推效果通常在超出训练长度约20%后明显退化。

**误区3：可学习位置嵌入总是优于固定编码**
Learned PE 在训练分布内的任务上可以细致地拟合位置模式，但其参数量与最大序列长度线性增长（每个位置一个 $d_{model}$ 维向量），且无法泛化到训练长度之外。在需要处理可变长序列或长文本的场景下，固定编码或相对编码方案反而具有实用优势。

---

## 知识关联

**前置知识——Transformer架构**：位置编码直接嵌入 Transformer 的输入层，其向量维度必须与 $d_{model}$ 对齐（原论文为512）；理解注意力得分计算公式 $\text{softmax}(QK^T/\sqrt{d_k})V$ 是理解位置编码如何通过 Q/K 矩阵影响注意力权重的前提。

**后续概念——RoPE（旋转位置编码）**：RoPE 的核心创新是将位置信息编码为复数旋转矩阵，在 Q/K 内积中自然实现相对位置感知，公式为 $q_m^T k_n = \text{Re}[(W_q x_m e^{im\theta})^* (W_k x_n e^{in\theta})]$，使得内积只依赖于位置差 $(m-n)$。RoPE 是 LLaMA、ChatGLM 等主流大模型抛弃传统绝对位置编码的直接替代方案，也是理解上下文窗口外推技术（如 YaRN、LongRoPE）的必要基础。
