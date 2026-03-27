---
id: "rnn-basics"
concept: "循环神经网络(RNN)"
domain: "ai-engineering"
subdomain: "ai-foundations"
subdomain_name: "AI基础"
difficulty: 7
is_milestone: false
tags: ["DL", "序列"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 45.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.438
last_scored: "2026-03-23"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 循环神经网络（RNN）

## 概述

循环神经网络（Recurrent Neural Network，RNN）是一类专门处理**序列数据**的神经网络架构，其核心特征是网络中存在**定向循环连接**，使得当前时间步的隐藏状态 $h_t$ 同时依赖于当前输入 $x_t$ 和上一时间步的隐藏状态 $h_{t-1}$。这种结构赋予了网络"记忆"能力，使其能够捕捉时序依赖关系。

RNN 的概念最早可追溯至 1982 年 John Hopfield 提出的 Hopfield 网络，而现代 RNN 的标准形式由 David Rumelhart 等人在 1986 年提出的反向传播算法框架中得到形式化定义。1990 年，Jeffrey Elman 提出了简洁实用的 Elman 网络，奠定了今天所使用的标准 RNN 基本结构。

RNN 的重要性在于它打破了前馈神经网络（包括 CNN）"输入独立同分布"的假设。在文本翻译、语音识别、时间序列预测等任务中，序列中的每个元素与其前后元素存在强依赖关系。标准 CNN 处理一句话时无法利用词序信息，而 RNN 通过隐藏状态的传递，天然支持可变长度序列的建模。

---

## 核心原理

### 前向传播公式与状态更新

标准 RNN 的前向传播由以下两个公式完整描述：

$$h_t = \tanh(W_{hh} \cdot h_{t-1} + W_{xh} \cdot x_t + b_h)$$

$$\hat{y}_t = \text{softmax}(W_{hy} \cdot h_t + b_y)$$

其中：
- $h_t \in \mathbb{R}^n$ 为第 $t$ 时间步的隐藏状态向量，$n$ 为隐藏单元数
- $W_{hh} \in \mathbb{R}^{n \times n}$ 为**循环权重矩阵**，负责传递历史信息
- $W_{xh} \in \mathbb{R}^{n \times d}$ 为输入权重矩阵，$d$ 为输入维度
- 关键约束：$W_{hh}$ 和 $W_{xh}$ 在所有时间步**共享**，这使 RNN 参数量与序列长度无关

激活函数通常选 $\tanh$（而非 ReLU），因为 $\tanh$ 的输出范围为 $(-1, 1)$，有助于限制梯度量级。

### 随时间反向传播（BPTT）与梯度问题

RNN 的训练使用**随时间反向传播**（Backpropagation Through Time，BPTT）算法。将 RNN 沿时间轴"展开"后，梯度需要从最终时间步 $T$ 逐步传回到第 $1$ 步。损失对 $h_1$ 的梯度涉及连乘项：

$$\frac{\partial h_T}{\partial h_1} = \prod_{t=2}^{T} \frac{\partial h_t}{\partial h_{t-1}} = \prod_{t=2}^{T} W_{hh}^T \cdot \text{diag}(\tanh'(\cdot))$$

当序列长度 $T$ 较大时，若 $W_{hh}$ 的最大奇异值 $< 1$，梯度指数级衰减（**梯度消失**）；若 $> 1$，梯度指数级爆炸（**梯度爆炸**）。梯度爆炸通常通过**梯度裁剪**（Gradient Clipping，设阈值为 5 或 1）缓解，而梯度消失则是促使 LSTM 诞生的根本动因。

### 序列到序列的建模范式

RNN 支持多种输入输出结构，这是 CNN 等固定拓扑网络所不具备的：

| 范式 | 结构 | 典型应用 |
|------|------|----------|
| 一对多 | 单输入 → 序列输出 | 图像描述生成 |
| 多对一 | 序列输入 → 单输出 | 文本情感分类 |
| 多对多（同步） | 序列 → 等长序列 | 词性标注 |
| 多对多（编码解码） | 序列 → 任意长序列 | 机器翻译 |

编码器-解码器（Encoder-Decoder）架构由 Cho 等人在 2014 年提出，使用两个 RNN 分别完成序列压缩与序列生成，是早期神经机器翻译的标准范式。

---

## 实际应用

**语言模型（Character-level LM）**：Andrej Karpathy 于 2015 年展示的字符级 RNN 语言模型，使用单层 512 个隐藏单元的 RNN，在莎士比亚文集上训练后能生成风格相似的文本。该模型直接预测 $P(x_{t+1} | x_1, ..., x_t)$，每个字符作为 one-hot 向量输入，展示了 RNN 捕捉长程文体特征的能力。

**语音识别**：谷歌在 2015 年发布的 Deep Speech 系统的核心是双向 RNN（BiRNN），将正向 RNN 与反向 RNN 的隐藏状态拼接，在 LibriSpeech 数据集上达到了当时领先的词错率（WER）。双向 RNN 要求序列完整可用，因此适用于离线识别但不适用于实时流式识别。

**时间序列预测**：在金融量化领域，RNN 被用于预测股票价格或交易量。输入序列通常为过去 $T=60$ 个交易日的特征向量，输出为未来 $k$ 步的预测值。需特别注意对输入进行归一化处理，否则 $\tanh$ 饱和导致梯度近乎为零。

---

## 常见误区

**误区一：认为 RNN 可以记住任意长的历史信息**。标准 RNN 在理论上隐藏状态包含所有历史信息，但由于梯度消失问题，实践中标准 RNN 有效记忆长度通常不超过 10~20 个时间步。超过此范围的长程依赖需要使用 LSTM 或 GRU 架构——Hochreiter 和 Schmidhuber 在 1997 年正是针对这一具体缺陷设计了 LSTM，引入了遗忘门、输入门和输出门三个门控机制。

**误区二：将 RNN 的循环权重 $W_{hh}$ 理解为"每个时间步的不同参数"**。事实上，RNN 最关键的设计是**跨时间步共享参数**，整个序列的处理只使用同一组 $W_{hh}$、$W_{xh}$、$b_h$。这一设计使模型具有时间不变性，并大幅减少参数量，但同时也是 BPTT 梯度连乘问题的来源。

**误区三：以为双向 RNN（BiRNN）适用于所有序列任务**。BiRNN 在预测第 $t$ 步时同时利用了 $t$ 之后的信息，这在文本分类、命名实体识别等离线任务中是合理的，但在**自回归生成**（如逐词生成文本）或**实时推理**场景中，未来信息不可获取，使用 BiRNN 会造成信息泄漏，导致模型评估指标虚高。

---

## 知识关联

**与前序知识的衔接**：RNN 的前向传播本质上是带循环的全连接层叠加，理解 CNN 中的特征图与感受野概念后，可以类比地将 RNN 的隐藏状态 $h_t$ 理解为"时序感受野"——但不同于 CNN 的固定大小感受野，RNN 的感受野理论上覆盖整个历史序列。反向传播算法（来自深度学习入门课程）在 RNN 中演变为 BPTT，需特别关注展开图中参数共享导致的梯度累加。

**通向注意力机制**：标准 RNN 将整段输入序列压缩为单一固定长度向量 $h_T$ 作为 Decoder 的初始状态，这在长序列翻译任务中是性能瓶颈（Cho 等人 2014 年的论文中实验显示序列超过 30 词后 BLEU 分数明显下降）。注意力机制（Bahdanau et al., 2015）正是为解决这一瓶颈而提出的：让 Decoder 在每个解码步动态地对 Encoder 所有隐藏状态 $\{h_1, ..., h_T\}$ 计算加权求和，彻底突破了固定向量瓶颈，并最终演化为 Transformer 中的 Self-Attention 架构。