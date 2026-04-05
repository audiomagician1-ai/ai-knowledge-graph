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
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
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

循环神经网络（Recurrent Neural Network，RNN）是一类专为处理**序列数据**而设计的神经网络架构，其核心特征是网络中存在有向循环连接，使得网络在处理当前输入时能够保留对历史信息的"记忆"。与卷积神经网络（CNN）处理具有空间局部性的网格数据不同，RNN的设计哲学是让神经元的输出在时间维度上回馈到自身，形成隐藏状态（hidden state）在时间步之间的传递。

RNN的理论基础可追溯至1982年John Hopfield提出的Hopfield网络，而真正意义上的现代RNN由David Rumelhart等人在1986年通过**反向传播算法的扩展**（即BPTT算法）奠定训练基础。1990年，Elman网络的提出明确了"上下文单元"的概念，成为简单RNN（Simple RNN）的经典形式。此后RNN在语言建模、语音识别、机器翻译等时序任务中被广泛采用。

RNN之所以重要，在于现实世界中大量信息天然具有顺序依赖性：一句话中第5个词的意义依赖于前4个词，股票价格的预测依赖于历史价格序列。RNN提供了一种在固定参数量下处理任意长度序列的机制，为后续注意力机制和Transformer架构的出现埋下了关键伏笔。

---

## 核心原理

### 隐藏状态递推公式

RNN的计算核心是如下递推关系：

$$h_t = f(W_{hh} \cdot h_{t-1} + W_{xh} \cdot x_t + b_h)$$

$$y_t = W_{hy} \cdot h_t + b_y$$

其中：
- $h_t$ 是第 $t$ 个时间步的隐藏状态向量
- $x_t$ 是第 $t$ 个时间步的输入向量
- $W_{hh}$ 是隐藏层到隐藏层的**权重矩阵**（循环权重，所有时间步共享）
- $W_{xh}$ 是输入层到隐藏层的权重矩阵
- $f(\cdot)$ 通常为 $\tanh$ 激活函数
- $y_t$ 是第 $t$ 步的输出

**参数共享**是RNN的关键设计：无论序列多长，$W_{hh}$、$W_{xh}$、$W_{hy}$ 在所有时间步中完全相同，这使得RNN能以常数参数量处理变长序列。

### 时间反向传播（BPTT）

训练RNN采用**Backpropagation Through Time（BPTT）**算法，本质是将RNN沿时间轴"展开"为一个深层前馈网络，再执行标准反向传播。若序列长度为 $T$，则梯度需要从最后一步反向流经 $T$ 个节点。

梯度在每一步传递时都乘以循环权重矩阵 $W_{hh}$ 的某种函数，当 $T$ 较大时：
- 若 $W_{hh}$ 的最大奇异值 $> 1$，梯度**指数级爆炸**
- 若最大奇异值 $< 1$，梯度**指数级消失**

梯度消失问题导致普通RNN实际上难以学习超过**约10个时间步**以外的长程依赖，这一局限性直接催生了LSTM和GRU的设计。

### 多种网络拓扑结构

RNN并非只有单一形式，按输入输出关系可分为：

- **一对多（One-to-Many）**：单张图片生成文字描述（Image Captioning）
- **多对一（Many-to-One）**：整句文本做情感分类，只取最后时间步输出
- **多对多（Many-to-Many，同步）**：视频逐帧分类，每步产生输出
- **多对多（Many-to-Many，异步/Seq2Seq）**：机器翻译，编码器压缩源语言序列，解码器生成目标语言序列

**双向RNN（Bi-directional RNN）**由Schuster和Paliwal于1997年提出，在正向RNN基础上增加一个从序列末尾向前处理的反向RNN，将两者隐藏状态拼接后用于预测，显著提升了命名实体识别等任务的性能。

---

## 实际应用

**自然语言处理中的语言建模**：给定前 $n$ 个词预测第 $n+1$ 个词的条件概率 $P(w_{n+1}|w_1,...,w_n)$，RNN通过隐藏状态累积上下文，曾是GPT类模型出现之前的主流方案。Andrej Karpathy 2015年的工作展示了单层RNN在莎士比亚文本上字符级建模的效果，引发广泛关注。

**语音识别**：将声学特征序列（如MFCC特征，每帧约13维）映射到音素序列。传统HMM-GMM系统被深度双向RNN+CTC（Connectionist Temporal Classification）损失函数的方案取代，Google在2014年将该技术投入实用产品。

**时间序列预测**：将传感器读数序列（如每隔5分钟采样一次的温度数据）输入多对多RNN，预测未来若干时间步的数值，广泛应用于工厂设备异常检测。

**Seq2Seq机器翻译**：Sutskever等人在2014年提出的4层LSTM编码-解码架构，在English-French翻译任务（WMT'14数据集）上将BLEU分数提升至34.8，首次证明端到端神经机器翻译可超越传统统计方法。

---

## 常见误区

**误区一：认为RNN的隐藏状态能无限期记住早期信息**

许多初学者认为 $h_t$ 中包含从 $h_0$ 到 $h_{t-1}$ 的全部历史信息。实际上，由于梯度消失问题，标准RNN中 $h_t$ 对几十步之前的输入几乎没有感知。实验表明，在序列长度超过20-30的情况下，简单RNN的长程依赖建模能力急剧下降，需要LSTM或GRU的门控机制来解决。

**误区二：混淆RNN展开后的"层"与真实的网络深度**

RNN沿时间轴展开后看起来像一个很深的网络，但这 $T$ 个"层"共享相同的参数，并非深层前馈网络中各层独立的参数。真正意义上的**深度RNN**是将多个RNN层在垂直方向叠加：第一层RNN的 $h_t$ 序列作为第二层RNN的输入序列，两层参数完全独立。

**误区三：认为LSTM和GRU只是"更好的RNN"，本质不同**

LSTM（1997年，Hochreiter & Schmidhuber）和GRU（2014年，Cho等人）仍然是RNN的变体，同样依赖隐藏状态的顺序递推，**无法并行化处理序列内各时间步**这一根本限制依然存在。这与Transformer使用自注意力机制、可完全并行处理整个序列有本质区别，而非仅仅是性能的量级差异。

---

## 知识关联

**与CNN的关系**：CNN通过共享卷积核处理空间局部特征，RNN通过共享循环权重处理时间局部/全局特征。两者可结合使用，如**CNN-RNN架构**：先用CNN提取图像每帧的空间特征向量，再输入RNN建模帧间时序关系，常见于视频理解任务。

**向LSTM/GRU的演进**：理解RNN的梯度消失问题（具体表现为 $\partial h_t / \partial h_k$ 在 $t-k$ 很大时趋近于零）是理解LSTM引入**输入门、遗忘门、输出门**这三个可学习门控的必要前提。LSTM的细胞状态（cell state）通过加法而非乘法传递信息，有效缓解梯度消失。

**向注意力机制的演进**：Seq2Seq模型将整个源序列压缩进单个固定维度向量 $h_T$ 是其瓶颈，2015年Bahdanau等人提出注意力机制，让解码器在每一步动态地"查询"编码器所有时间步的隐藏状态 $\{h_1, ..., h_T\}$，绕开了RNN的顺序瓶颈。彻底抛弃RNN递推结构、完全依赖注意力的Transformer（2017年）则是这一思路的终极形态。