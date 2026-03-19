---
concept: attention-mechanism-basics
subdomain: ai-foundations
difficulty: 6
prereqs: [rnn-basics]
---

# 注意力机制基础

## 核心概念

注意力机制（Attention Mechanism）让模型在处理序列时能够"聚焦"于输入中最相关的部分，而非平等对待所有信息。这解决了RNN在长序列中信息衰减的核心问题。

## 动机：RNN的瓶颈

传统Seq2Seq模型（编码器-解码器）将整个输入序列压缩为单个固定长度向量，导致：
- 长序列信息丢失
- 远距离依赖捕获困难
- 解码器无法选择性关注输入的特定部分

## 注意力的直觉

人类阅读时不会均匀关注每个词。例如翻译"我爱猫"时：
- 生成"I"时主要关注"我"
- 生成"love"时主要关注"爱"
- 生成"cats"时主要关注"猫"

注意力机制让模型学习这种选择性关注能力。

## 基本计算

### Query-Key-Value框架

注意力可以统一描述为：
```
Attention(Q, K, V) = softmax(score(Q, K)) · V
```

1. **Query (Q)**: 当前位置的"查询"——我在找什么？
2. **Key (K)**: 每个位置的"标签"——我是什么？
3. **Value (V)**: 每个位置的"内容"——我能提供什么？
4. **Score**: Q和K的匹配程度
5. **softmax**: 将分数转为概率分布（权重）
6. **加权求和**: 按权重聚合V

### 评分函数

| 方法 | 公式 | 特点 |
|------|------|------|
| 点积 | Q·Kᵀ | 计算简单 |
| 缩放点积 | Q·Kᵀ / √d | Transformer使用，防止梯度消失 |
| 加法(Bahdanau) | v·tanh(W₁Q + W₂K) | 最早的注意力形式 |

## 自注意力（Self-Attention）

Q、K、V都来自同一序列——每个位置与序列中其他所有位置计算注意力。这是Transformer的核心。

```
输入: [x₁, x₂, x₃]
Q = W_Q · X
K = W_K · X
V = W_V · X
输出: softmax(QKᵀ/√d) · V
```

特点：
- 每个位置可以直接关注任意其他位置
- 消除了RNN的序列依赖，可并行计算
- 计算复杂度 O(n²d)，n为序列长度

## 多头注意力（Multi-Head Attention）

使用多组Q/K/V投影，捕获不同方面的注意力模式：
```
head_i = Attention(QW_i^Q, KW_i^K, VW_i^V)
MultiHead = Concat(head_1, ..., head_h) · W^O
```

不同的头可以关注不同的语义关系：
- 头1: 语法依赖
- 头2: 语义相似
- 头3: 位置关系

## 注意力可视化

注意力权重可以可视化为热力图，展示模型关注模式。这是理解和调试Transformer模型的重要工具。

## 与RNN的关系

注意力最初作为RNN的增强组件提出（Bahdanau 2014）。后来Transformer证明：纯注意力机制可以完全取代RNN，成为序列建模的主流方法。理解RNN的局限性有助于理解注意力机制的动机和价值。
