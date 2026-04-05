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
quality_tier: "A"
quality_score: 79.6
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


# 反向传播

## 概述

反向传播（Backpropagation，简称BP）是一种通过链式法则高效计算神经网络中所有参数梯度的算法。其核心思想是：将网络输出端的损失误差，从输出层向输入层逐层"反向"传递，同时计算每个参数对最终损失的偏导数。这个过程将原本需要对每个参数独立扰动估算的梯度计算，降低到了 O(W) 的时间复杂度（W 为总参数量），而非朴素有限差分法所需的 O(W²)。

反向传播算法由 Rumelhart、Hinton 和 Williams 于1986年在《Nature》杂志发表的论文中正式推广，使训练多层感知机成为可行方案，直接推动了第二次神经网络研究热潮。尽管相关数学思想在1970年代便由 Linnainmaa 等人独立提出，但1986年的论文首次将其与梯度下降结合并在实验中展示了隐含层特征学习能力。

反向传播的重要性在于：没有它，就无法高效训练具有隐含层的深度网络。现代大语言模型（如 GPT-4 拥有数千亿参数）的训练，本质上仍依赖反向传播在每次前向传播后计算梯度，再通过优化器更新权重。

---

## 核心原理

### 链式法则与计算图

反向传播的数学基础是多元复合函数的链式法则。设损失函数 L 经过一系列复合运算得到，对于网络中任意参数 w，其梯度为：

$$\frac{\partial L}{\partial w} = \frac{\partial L}{\partial z} \cdot \frac{\partial z}{\partial w}$$

其中 z 是直接依赖 w 的中间变量。实际网络中路径可能有多条，需将所有路径的梯度贡献相加：

$$\frac{\partial L}{\partial w} = \sum_{k} \frac{\partial L}{\partial z_k} \cdot \frac{\partial z_k}{\partial w}$$

在计算图（Computational Graph）视角下，前向传播构建有向无环图，反向传播则沿该图的反方向传递"误差信号"，即δ值（delta）。PyTorch 和 TensorFlow 的自动微分引擎（Autograd）正是基于此动态构建并反向遍历计算图。

### 前向传播与反向传播的两阶段过程

**前向传播**阶段：对于第 l 层，计算加权输入 $z^{(l)} = W^{(l)} a^{(l-1)} + b^{(l)}$，再经激活函数得到激活值 $a^{(l)} = \sigma(z^{(l)})$，同时缓存所有中间变量供反向使用。

**反向传播**阶段：从输出层开始，计算损失对输出层加权输入的梯度（误差项）：
$$\delta^{(L)} = \nabla_a L \odot \sigma'(z^{(L)})$$

然后逐层向前递推：
$$\delta^{(l)} = \left((W^{(l+1)})^\top \delta^{(l+1)}\right) \odot \sigma'(z^{(l)})$$

最终权重梯度为：
$$\frac{\partial L}{\partial W^{(l)}} = \delta^{(l)} (a^{(l-1)})^\top$$

其中 ⊙ 表示逐元素乘法（Hadamard 积）。

### 梯度消失与梯度爆炸

反向传播在深层网络中面临两大数值问题，均源于误差项 δ 在逐层传递时与激活函数导数的连乘。

**梯度消失**：Sigmoid 函数的导数最大值为 0.25，在20层网络中，梯度最大可缩小至 $(0.25)^{20} \approx 9 \times 10^{-13}$，导致靠近输入层的参数几乎无法更新。ReLU 激活函数（导数为0或1）的引入直接解决了这一问题，使深层网络训练成为可能。

**梯度爆炸**：权重矩阵的奇异值大于1时，误差项会指数级放大。循环神经网络（RNN）的时间反向传播（BPTT）尤其容易出现此问题，通常采用梯度裁剪（Gradient Clipping）限制梯度的L2范数不超过某个阈值（如1.0或5.0）。

---

## 实际应用

**卷积神经网络中的反向传播**：在 CNN 中，反向传播需对卷积操作求导。对卷积核权重的梯度为输入特征图与误差项的互相关，对上一层激活值的梯度则是误差项与卷积核的全卷积（Full Convolution），即用零填充后的反卷积操作。ResNet 中的残差连接 $a^{(l+1)} = F(a^{(l)}) + a^{(l)}$ 使梯度可以跳过若干层直接传回，将 ImageNet 上可训练深度从十几层扩展到152层。

**Transformer 中的反向传播**：注意力机制中 $\text{Softmax}(QK^\top/\sqrt{d_k})V$ 的反向传播需要计算 Softmax 的 Jacobian 矩阵，其特殊结构 $\text{diag}(s) - ss^\top$ 使得每个注意力头的梯度计算仍保持可处理的复杂度。Flash Attention 技术通过分块（Tiling）重新计算前向中间值（而非全部缓存），在反向传播时节省了 GPU 显存的 O(N²) 占用。

**调试中的梯度检验（Gradient Checking）**：工程实践中验证反向传播实现正确性的标准方法是用数值梯度对比解析梯度。对参数 θ 加减微小扰动 ε=1e-7，计算 $\frac{L(\theta+\varepsilon) - L(\theta-\varepsilon)}{2\varepsilon}$，若与反向传播结果的相对误差超过 1e-5，则说明实现存在 bug。

---

## 常见误区

**误区一：反向传播等同于梯度下降**。反向传播仅负责计算梯度，即求解 ∂L/∂W 的值；梯度下降（或 Adam、RMSProp 等优化器）负责利用这些梯度更新参数。二者是相互配合但独立的步骤。在调试时可以仅运行反向传播验证梯度是否正确，而不必执行参数更新。

**误区二：反向传播要求网络结构必须是层状（Layer-wise）的**。实际上，反向传播对任意可微的计算图均适用，包括有条件分支（如 Mixture of Experts 中的门控）、动态图（如 PyTorch 的 eager mode）乃至图神经网络中的消息传递结构。约束条件是每个节点的操作必须几乎处处可微。

**误区三：前向传播可以不缓存中间值**。为了在反向传播时计算激活函数导数 σ'(z)，必须保存前向传播中的 z 值或 a 值。这是深度学习训练比推理（inference）消耗更多显存的根本原因。梯度检查点技术（Gradient Checkpointing）通过在反向时重新计算部分前向值，以额外约33%的计算量换取显存占用的大幅压缩。

---

## 知识关联

**与梯度下降的关系**：梯度下降算法需要知道每个参数的梯度 ∂L/∂w 才能执行参数更新。反向传播正是高效提供这组梯度的计算方法。学习梯度下降时若停留在单参数或线性模型，就无需反向传播；一旦引入隐含层，链式法则的逐层传播便不可或缺。

**通向批归一化的路径**：批归一化（Batch Normalization）在前向传播中引入均值和方差的规范化操作，其反向传播梯度公式推导较为复杂——归一化操作使得批内样本相互依赖，导致 ∂L/∂x̂ 的计算需要同时考虑均值和方差对梯度的贡献。理解批归一化的训练行为，需要准确掌握其反向传播公式中 1/σ²、∂μ/∂x 项如何改变梯度的幅度与方向，进而理解批归一化为何能缓解梯度消失并允许使用更大学习率。