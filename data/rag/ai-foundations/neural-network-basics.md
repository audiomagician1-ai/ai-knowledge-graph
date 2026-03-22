---
id: "neural-network-basics"
concept: "神经网络基础"
domain: "ai-foundations"
subdomain: "deep-learning"
subdomain_name: "深度学习"
difficulty: 4
is_milestone: false
tags: ["核心"]
content_version: 3
quality_tier: "S"
quality_score: 92.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.94
last_scored: "2026-03-22"
sources:
  - type: "textbook"
    ref: "Goodfellow, Bengio & Courville. Deep Learning, MIT Press, 2016, Ch.6"
  - type: "academic"
    ref: "Rumelhart, Hinton & Williams. Learning representations by back-propagating errors, Nature, 1986"
  - type: "textbook"
    ref: "Bishop, Christopher. Pattern Recognition and Machine Learning, 2006, Ch.5"
  - type: "academic"
    ref: "Hornik, Kurt. Approximation capabilities of multilayer feedforward networks, Neural Networks, 1991"
scorer_version: "scorer-v2.0"
---
# 神经网络基础

## 概述

人工神经网络（Artificial Neural Network, ANN）是一类**由大量简单计算单元（神经元）通过可学习权重连接而成的参数化函数族**。其核心思想是：单个神经元只能做简单的线性变换+非线性激活，但数百万个神经元的组合可以逼近任意复杂的函数——这就是**万能近似定理**（Universal Approximation Theorem, Hornik 1991）。

1986 年 Rumelhart、Hinton 与 Williams 发表了反向传播算法（Backpropagation），解决了多层网络的训练问题，奠定了现代深度学习的基础。如今，神经网络已在图像识别（ResNet）、自然语言处理（Transformer/GPT）、游戏AI（AlphaGo）等领域达到或超过人类水平。

## 核心知识点

### 1. 单个神经元（感知器）

一个神经元接收 n 个输入 x1...xn，计算：
output = activation(w1*x1 + w2*x2 + ... + wn*xn + b)

其中：
- **w1...wn** 是可学习的**权重**（Weights）
- **b** 是**偏置**（Bias）
- **activation** 是**激活函数**（非线性变换）

**几何解释**：线性部分 w*x + b = 0 定义了输入空间中的一个超平面，激活函数决定超平面两侧的输出值。单个神经元等价于一个**线性分类器**。

### 2. 激活函数

| 函数 | 公式 | 输出范围 | 优势 | 问题 |
|------|------|---------|------|------|
| **Sigmoid** | 1/(1+e^(-x)) | (0, 1) | 输出可解释为概率 | 梯度消失（饱和区梯度趋近0） |
| **Tanh** | (e^x - e^(-x))/(e^x + e^(-x)) | (-1, 1) | 零中心化 | 仍有梯度消失 |
| **ReLU** | max(0, x) | [0, +inf) | 计算简单、缓解梯度消失 | "死神经元"（x<0 时梯度为0） |
| **Leaky ReLU** | max(0.01x, x) | (-inf, +inf) | 解决死神经元问题 | 多一个超参数 |
| **GELU** | x * Phi(x) | 连续近似 | Transformer 标准选择 | 计算稍复杂 |

**为什么需要非线性**：没有激活函数时，多层网络的复合仍是线性变换（矩阵乘法的链式仍是矩阵）——等价于单层网络。非线性激活使网络能表示非线性决策边界。

### 3. 多层前馈网络（MLP）

**架构**：输入层 -> 隐藏层1 -> 隐藏层2 -> ... -> 输出层

每层执行：h = activation(W * x + b)
- W 是权重矩阵（输出维度 x 输入维度）
- 整个网络是函数复合：f(x) = f_L(f_{L-1}(...f_1(x)))

**万能近似定理**（Hornik, 1991）：
一个具有**单个足够宽的隐藏层**和非线性激活函数的前馈网络，可以以任意精度逼近任何连续函数。但定理只保证存在性——不保证能通过训练找到这样的权重，也不保证所需神经元数量是实际可行的。**实践中深网络（多层较窄）比浅网络（单层极宽）效率高得多**。

### 4. 反向传播算法

**目标**：计算损失函数 L 关于所有权重的梯度 dL/dW，用于梯度下降更新。

**核心**：链式法则的系统化应用。

**前向传播**（Forward Pass）：从输入到输出，逐层计算并缓存中间结果。
**反向传播**（Backward Pass）：从输出到输入，逐层计算梯度。

以单隐藏层为例：
- 前向：z = W1*x + b1; h = ReLU(z); y_hat = W2*h + b2; L = (y - y_hat)^2
- 反向：dL/dy_hat = 2*(y_hat - y); dL/dW2 = dL/dy_hat * h^T; dL/dh = W2^T * dL/dy_hat; dL/dz = dL/dh * ReLU'(z); dL/dW1 = dL/dz * x^T

**计算复杂度**：前向和反向传播的计算量大致相同，都是 O(参数总数)。

### 5. 训练循环

完整的训练过程：
1. **初始化权重**（Xavier/He 初始化，避免梯度消失/爆炸）
2. **前向传播**：计算预测值和损失
3. **反向传播**：计算所有参数梯度
4. **参数更新**：W = W - lr * dL/dW（lr = 学习率）
5. 重复 2-4 直到收敛

**关键超参数**：
- **学习率**（最重要）：太大震荡不收敛，太小收敛极慢。典型起始值 0.001
- **批大小**（Batch Size）：太小噪声大，太大泛化差。典型 32-256
- **训练轮数**（Epochs）：过多导致过拟合

## 关键原理分析

### 深度的意义

为什么深网络优于宽网络？直觉：深度网络通过**层级特征抽象**实现效率——第 1 层学习边缘，第 2 层组合边缘成纹理，第 3 层组合纹理成部件，第 4 层组合部件成物体。每层复用下层的特征，避免了指数级的组合爆炸。

### 过拟合与正则化

当网络参数远多于训练样本时，网络可以"记住"训练数据而非学习规律。对策：
- **Dropout**（Srivastava et al., 2014）：训练时随机关闭 50% 神经元
- **权重衰减**（L2 正则化）：损失函数加入 lambda * ||W||^2
- **早停**（Early Stopping）：验证集性能不再提升时停止训练

## 实践练习

**练习 1**：手动计算一个 2-2-1 网络（2输入、2隐藏、1输出，ReLU激活）对输入 [1, 0] 的前向传播结果。自定义权重。

**练习 2**：用 PyTorch 构建一个 3 层 MLP，在 MNIST 数据集上训练分类器。对比不同学习率（0.1, 0.01, 0.001）的收敛速度。

## 常见误区

1. **"更多层一定更好"**：过深的网络面临梯度消失/爆炸，需要 BatchNorm、ResNet 等技术
2. **"神经网络模仿了大脑"**：生物神经元的工作方式远比人工神经元复杂（脉冲编码、突触可塑性、化学信号），相似性主要是概念层面的
3. **"训练损失下降=模型变好"**：必须同时监控验证集损失，训练损失下降但验证损失上升说明过拟合