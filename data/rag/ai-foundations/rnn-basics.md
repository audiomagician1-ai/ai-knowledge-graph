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
---
# 循环神经网络（RNN）

## 概述

循环神经网络（Recurrent Neural Network，RNN）是一类专为处理**序列数据**而设计的神经网络架构，其核心特征是神经元的输出会作为下一时间步的输入反馈回网络本身，形成"循环"连接。与CNN处理空间局部特征不同，RNN通过隐状态（hidden state）在时间维度上传递上下文信息，使网络具备对历史信息的"记忆"能力。

RNN的理论雏形可追溯至1982年John Hopfield提出的Hopfield网络，但现代意义上的RNN架构由David Rumelhart等人在1986年的《Parallel Distributed Processing》中系统阐述，并配合反向传播算法（BPTT，Backpropagation Through Time）实现了可训练的循环结构。1990年代，Elman网络和Jordan网络进一步规范了简单RNN的标准形式。然而，直到LSTM（1997年，Hochreiter & Schmidhuber）的出现，RNN才真正在长序列任务上展现出实用价值。

RNN在语音识别、机器翻译、文本生成、时间序列预测等任务中具有不可替代的地位。即便Transformer架构在众多NLP任务上取得领先，理解RNN的运作原理仍是掌握序列建模思想的必要前提，因为注意力机制中的序列对齐概念直接脱胎于RNN编解码器框架。

---

## 核心原理

### 时间步展开与状态方程

RNN的数学核心是递推方程：

$$h_t = f(W_{hh} \cdot h_{t-1} + W_{xh} \cdot x_t + b_h)$$

$$\hat{y}_t = W_{hy} \cdot h_t + b_y$$

其中：
- $h_t \in \mathbb{R}^n$ 为第 $t$ 时间步的隐状态向量
- $x_t$ 为当前时间步输入
- $W_{hh}$、$W_{xh}$、$W_{hy}$ 为**所有时间步共享**的权重矩阵（参数共享是RNN区别于全连接序列模型的关键）
- $f$ 通常为 $\tanh$ 或 $\text{ReLU}$ 激活函数

将RNN沿时间轴"展开"（unroll）后，可得到一个深度等于序列长度 $T$ 的有向无环计算图，这也是BPTT算法的基础。

### 随时间反向传播（BPTT）与梯度问题

BPTT计算损失对某时刻权重的梯度时，需要沿时间步累乘Jacobian矩阵：

$$\frac{\partial L}{\partial W_{hh}} = \sum_{t=1}^{T} \frac{\partial L_t}{\partial h_t} \cdot \prod_{k=t}^{T-1} \frac{\partial h_{k+1}}{\partial h_k}$$

当序列较长（如 $T > 20$）时，连乘项中若 $\left\|\frac{\partial h_{k+1}}{\partial h_k}\right\| < 1$ 则导致**梯度消失**，若 $> 1$ 则导致**梯度爆炸**。梯度爆炸可通过梯度裁剪（Gradient Clipping，通常设阈值为5.0）缓解，而梯度消失问题则推动了LSTM和GRU的诞生。

### LSTM：通过门控解决长期依赖

LSTM（Long Short-Term Memory）在1997年由Hochreiter和Schmidhuber提出，通过引入**细胞状态（cell state）** $c_t$ 和三个门控机制彻底改善了梯度消失问题：

- **遗忘门** $f_t = \sigma(W_f \cdot [h_{t-1}, x_t] + b_f)$：决定丢弃多少历史信息
- **输入门** $i_t = \sigma(W_i \cdot [h_{t-1}, x_t] + b_i)$：决定写入多少新信息
- **输出门** $o_t = \sigma(W_o \cdot [h_{t-1}, x_t] + b_o)$：决定输出多少细胞状态

细胞状态更新为 $c_t = f_t \odot c_{t-1} + i_t \odot \tilde{c}_t$，其中 $\odot$ 为逐元素乘法。细胞状态的加法更新路径使梯度可以不衰减地流过较长时间跨度，这是LSTM能处理数百步以上长程依赖的根本原因。

### GRU：LSTM的简化变体

2014年Cho等人提出GRU（Gated Recurrent Unit），将遗忘门与输入门合并为**更新门** $z_t$，并取消独立的细胞状态，参数量约为LSTM的75%。在序列长度适中的任务（如200步以内）上，GRU通常与LSTM性能相当但训练更快。

---

## 实际应用

**语言模型与文本生成**：字符级RNN（char-RNN）由Andrej Karpathy于2015年在博客中演示，使用单层LSTM（512个隐藏单元）在莎士比亚文集上训练后，即可生成风格相似的文本，展示了RNN对字符序列分布的建模能力。

**序列到序列（Seq2Seq）机器翻译**：2014年Sutskever等人提出基于两个LSTM的编码器-解码器架构，首次将端到端神经机器翻译付诸实践。编码器将源句压缩为固定长度的上下文向量 $c$，解码器逐词生成目标句。该架构在WMT英法翻译任务上达到了当时最优的BLEU分数34.8，但固定长度瓶颈随后被注意力机制所克服。

**时间序列预测**：在金融风控、IoT传感器异常检测场景中，多层双向LSTM（Bidirectional LSTM）被广泛应用。双向结构通过同时处理正向和反向序列，使每个时间步的隐状态同时包含过去和未来的上下文，在命名实体识别（NER）等任务中F1分数通常比单向LSTM高出2-4个百分点。

---

## 常见误区

**误区1：RNN的"记忆"是无限的**
普通RNN在理论上可以传递任意长度的历史信息，但由于梯度消失，实际上隐状态 $h_t$ 在经过约5-10步后对早期输入 $x_1$ 的依赖已极度微弱。即便是LSTM，在序列超过1000步时性能也会显著下降。这是选用Transformer架构处理超长文档的根本原因，而非RNN在架构上"不支持"长序列。

**误区2：所有时间步共享权重会降低表达能力**
初学者常认为权重共享限制了模型的表达能力。恰恰相反，参数共享使RNN能够将同一语言规律（如"动词后接名词"的模式）泛化应用于序列中任意位置，同时大幅降低参数量——一个处理500步序列的RNN与处理5步序列的RNN拥有**完全相同数量的参数**，这是标准前馈网络无法实现的。

**误区3：LSTM的遗忘门初始化为零**
实践中LSTM遗忘门的偏置 $b_f$ 应初始化为**正值**（通常取1.0或2.0，由Jozefowicz等人在2015年通过大规模实验验证）。若初始化为0，遗忘门输出约为0.5，网络在训练初期会过度遗忘历史信息，导致收敛变慢甚至失败。这一细节在标准教材中鲜少提及，却是工程实践中影响LSTM训练稳定性的关键超参数之一。

---

## 知识关联

**与深度学习基础的关系**：RNN的BPTT算法是标准反向传播在时间维度上的直接扩展，梯度消失问题的分析依赖对激活函数导数范围（如 $\tanh'(x) \in (0, 1]$）的理解；没有对链式法则的掌握，无法理解为何时间步连乘会导致梯度衰减。

**与CNN的对比**：CNN通过卷积核在空间维度实现局部感受野和参数共享，RNN通过循环连接在时间维度实现上下文传递和参数共享。一维卷积（1D-CNN）也可处理序列，但其感受野固定，无法动态积累任意长度的历史——这是二者本质差异所在。

**通往注意力机制**：Seq2Seq模型中固定长度上下文向量的瓶颈问题，直接催生了Bahdanau等人在2015年提出的注意力机制。注意力机制让解码器在每一步生成时动态地"查询"编码器所有时间步的隐状态，计算公式 $\alpha_{t,s} = \text{softmax}(e_{t,s})$ 中的对齐分数 $e_{t,s}$ 本质上是对RNN隐状态的加权求和，因此掌握RNN的隐状态概念是理解注意力计算过程的直接前提。
