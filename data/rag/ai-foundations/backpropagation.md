---
id: "backpropagation"
concept: "反向传播"
domain: "ai-engineering"
subdomain: "ai-foundations"
subdomain_name: "AI基础"
difficulty: 7
is_milestone: false
tags: ["DL"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "pending-rescore"
quality_score: 41.8
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-23"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 反向传播

## 概述

反向传播（Backpropagation，简称BP）是训练多层神经网络的核心算法，其本质是利用链式法则高效计算损失函数对每一层网络参数的梯度。与正向传播（输入→输出）相反，反向传播从输出层的误差出发，逐层向输入方向传递梯度信号，使网络能够知道每个权重应该如何调整以减小预测误差。

反向传播算法由 Rumelhart、Hinton 和 Williams 于 1986 年在《Nature》杂志发表的论文《Learning representations by back-propagating errors》中正式确立并推广，使得神经网络在实践中真正可训练。尽管类似思想早在 1970 年代便有雏形（Werbos 1974 年博士论文），但正是 1986 年的工作点燃了第一次神经网络复兴。

反向传播的重要性在于：深度神经网络可能包含数亿个参数，若逐个参数数值扰动来估计梯度（有限差分法），计算开销与参数量成正比，不可行；而反向传播只需两次前向/后向传递，便可在一次计算中获得所有参数的精确梯度，计算复杂度仅为 $O(W)$，其中 $W$ 是参数总数。

---

## 核心原理

### 链式法则与计算图

反向传播的数学基础是多元复合函数的链式法则。设损失函数为 $L$，网络第 $l$ 层的权重矩阵为 $W^{(l)}$，中间激活值为 $a^{(l)}$，则：

$$\frac{\partial L}{\partial W^{(l)}} = \frac{\partial L}{\partial a^{(l)}} \cdot \frac{\partial a^{(l)}}{\partial W^{(l)}}$$

现代深度学习框架（如 PyTorch、TensorFlow）将网络表示为**计算图（Computational Graph）**，图中每个节点存储前向计算结果及对应的反向梯度函数。PyTorch 的 `autograd` 引擎在前向传播时动态构建此图，反向传播时沿图的反方向逐节点调用梯度函数。

### 误差项（δ）的逐层传递

定义第 $l$ 层的误差项 $\delta^{(l)} = \frac{\partial L}{\partial z^{(l)}}$，其中 $z^{(l)} = W^{(l)} a^{(l-1)} + b^{(l)}$ 是激活前的线性组合值。反向传播的递推公式为：

$$\delta^{(l)} = \left(W^{(l+1)}\right)^T \delta^{(l+1)} \odot f'\!\left(z^{(l)}\right)$$

其中 $\odot$ 表示 Hadamard 逐元素乘积，$f'$ 是激活函数的导数。权重梯度由下式给出：

$$\frac{\partial L}{\partial W^{(l)}} = \delta^{(l)} \left(a^{(l-1)}\right)^T$$

这个公式揭示了一个关键事实：若激活函数在某处导数接近零（如 Sigmoid 在饱和区导数趋近 0.0025），则 $\delta^{(l)}$ 经多次乘法后会指数级缩小，导致**梯度消失**问题。

### 梯度消失与梯度爆炸

梯度消失（Vanishing Gradient）和梯度爆炸（Exploding Gradient）是反向传播在深层网络中的两大病态现象，均源于误差项递推公式中矩阵连乘的特性。设网络深度为 $n$ 层，若每层传递因子的谱范数 $\|W^{(l)}\| < 1$，梯度以指数速率衰减；若 $\|W^{(l)}\| > 1$，则梯度爆炸。

- **ReLU 激活函数**（$f'(z)=1$ for $z>0$）在正区间导数恒为 1，有效缓解梯度消失，这正是 2012 年 AlexNet 抛弃 Sigmoid 改用 ReLU 并大获成功的核心原因。
- **梯度裁剪（Gradient Clipping）**将梯度的 L2 范数限制在阈值 $\theta$（常见取值 1.0 或 5.0）以内，是 RNN/LSTM 训练中对抗梯度爆炸的标准手段。

---

## 实际应用

### 卷积神经网络中的反向传播

在 CNN 中，卷积层的权重是共享的滤波器。反向传播需要计算损失对每个滤波器参数的梯度，具体为误差图与输入特征图的**互相关（cross-correlation）**运算。一个 3×3 滤波器在 224×224 输入上的梯度计算，等价于将上游误差图与输入做卷积——这一结构使得 GPU 并行化极为高效。

### Transformer 中的梯度流

在 BERT（12 层，768 隐藏维度）这类 Transformer 模型训练时，反向传播需要穿越多头自注意力中的 Softmax 操作。Softmax 的梯度为 $\frac{\partial \text{softmax}(z)_i}{\partial z_j} = \text{softmax}(z)_i(\delta_{ij} - \text{softmax}(z)_j)$，其雅可比矩阵是满秩的，因此注意力层通常不会引起梯度消失，残差连接（Residual Connection）进一步保障了梯度的畅通传递。

### 调试技巧：梯度数值检验

在实现自定义层时，常用**数值梯度检验**验证反向传播实现正确性：对参数 $\theta$ 施加扰动 $\epsilon = 10^{-5}$，计算 $\frac{L(\theta+\epsilon) - L(\theta-\epsilon)}{2\epsilon}$，与解析梯度对比，若相对误差超过 $10^{-4}$ 则提示实现有误。

---

## 常见误区

**误区一：反向传播等同于梯度下降**
两者是不同层次的概念。反向传播只负责**计算梯度**，不更新参数；梯度下降（或 Adam、RMSprop 等优化器）利用这些梯度**执行参数更新**。去掉反向传播，梯度下降就无从获得梯度；去掉梯度下降，反向传播计算的梯度也只会堆积在内存中无所作为。

**误区二：反向传播会修改前向传播的中间值**
反向传播是纯读取操作——它读取前向传播缓存的激活值 $a^{(l)}$ 来计算梯度，但不会修改这些值。这正是为什么 PyTorch 在调用 `loss.backward()` 后，若不清零梯度（`optimizer.zero_grad()`），梯度会**累积叠加**而非被覆盖，这是一个极常见的 Bug 来源。

**误区三：更深的网络梯度消失一定更严重**
这在没有残差连接的网络中成立，但 ResNet（2015，Kaiming He 等）通过引入 $F(x)+x$ 的跳跃连接，使得梯度可以"绕过"若干层直接回传，成功训练了 152 层的网络。深度与梯度消失之间并非必然正比关系，网络架构设计对反向传播的梯度流有决定性影响。

---

## 知识关联

**前置概念——梯度下降**：梯度下降提供了参数更新的迭代规则 $\theta \leftarrow \theta - \eta \nabla_\theta L$，但没有告诉你如何高效求 $\nabla_\theta L$。反向传播正是填补这一空白的计算引擎，两者共同构成神经网络训练的完整闭环。

**后续概念——批归一化（Batch Normalization）**：批归一化直接影响反向传播中的梯度流。BN 层对每批次激活值进行标准化，使每层输入分布稳定，从而避免激活函数陷入饱和区，让反向传播时的导数 $f'(z)$ 保持在有效范围内。理解反向传播中梯度消失的成因，是理解为什么 BN 能加速训练、允许更大学习率（从 0.001 提升到 0.01 量级）的前提。