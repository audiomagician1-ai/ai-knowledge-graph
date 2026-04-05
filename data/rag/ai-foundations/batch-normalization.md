---
id: "batch-normalization"
concept: "批归一化"
domain: "ai-engineering"
subdomain: "ai-foundations"
subdomain_name: "AI基础"
difficulty: 4
is_milestone: false
tags: ["normalization", "training", "regularization"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 批归一化（Batch Normalization）

## 概述

批归一化（Batch Normalization，简称 BN）是由 Sergey Ioffe 和 Christian Szegedy 于 2015 年在论文《Batch Normalization: Accelerating Deep Network Training by Reducing Internal Covariate Shift》中提出的神经网络训练技术。其核心操作是对每个 mini-batch 内的激活值进行标准化处理，使其均值为 0、方差为 1，随后通过可学习参数 γ（缩放）和 β（平移）恢复网络的表达能力。

批归一化的提出直接针对深层网络训练中的"内部协变量偏移"（Internal Covariate Shift）问题——即随着训练进行，每层输入的分布不断变化，导致后续层需要持续适应新的输入分布，严重拖慢收敛速度。引入 BN 后，研究者发现可以使用高达 0.1 的学习率（而无 BN 时通常只能使用 0.001 量级），并将 Inception 模型的训练步骤从原来的 600 万步缩减至仅 270 万步即可达到相同精度。

批归一化不仅是加速训练的工具，它还具有隐式正则化效果，在许多场景下可以替代或减少 Dropout 的使用，同时允许更大的权重初始化范围，使深度网络训练变得更加稳定可靠。

---

## 核心原理

### 标准化计算公式

对于一个 mini-batch $\mathcal{B} = \{x_1, x_2, \ldots, x_m\}$，批归一化的完整计算如下：

**第一步：计算批均值**
$$\mu_\mathcal{B} = \frac{1}{m} \sum_{i=1}^{m} x_i$$

**第二步：计算批方差**
$$\sigma_\mathcal{B}^2 = \frac{1}{m} \sum_{i=1}^{m} (x_i - \mu_\mathcal{B})^2$$

**第三步：标准化**
$$\hat{x}_i = \frac{x_i - \mu_\mathcal{B}}{\sqrt{\sigma_\mathcal{B}^2 + \epsilon}}$$

其中 $\epsilon$（通常取 $10^{-5}$）是为防止除零引入的数值稳定项。

**第四步：仿射变换（重新缩放与平移）**
$$y_i = \gamma \hat{x}_i + \beta$$

其中 $\gamma$ 和 $\beta$ 是该层独立学习的参数，初始化时通常设 $\gamma=1, \beta=0$。这一步保证了批归一化在极端情况下可以退化为恒等变换，不损失网络的原始表达能力。

### 训练阶段与推理阶段的差异

批归一化在训练和推理时行为不同，这是初学者必须理解的关键点。**训练阶段**使用当前 mini-batch 的均值和方差进行标准化；**推理阶段**则使用训练过程中通过指数移动平均（Exponential Moving Average）积累的全局统计量 $\mu_{running}$ 和 $\sigma^2_{running}$：

$$\mu_{running} \leftarrow (1-\alpha)\mu_{running} + \alpha\mu_\mathcal{B}$$

动量系数 $\alpha$ 在 PyTorch 默认实现中取 0.1（即保留 90% 历史信息，融入 10% 当前 batch 统计量）。推理时若误用 batch 统计量，单张图片推理结果将会因批次大小改变而产生不稳定输出。

### 批归一化的位置与正则化机制

批归一化通常插入在**线性变换（全连接或卷积）之后、激活函数之前**，即 Linear → BN → ReLU 的顺序，也有部分研究（如 ResNet 的实际工程实现）将其放在激活函数之后。

BN 之所以具有正则化效果，是因为每个样本的标准化结果依赖于同一 batch 内其他样本的统计量，引入了随机性——不同 batch 组合带来不同的 $\mu_\mathcal{B}$ 和 $\sigma_\mathcal{B}^2$，类似于给激活值添加了随机噪声，迫使网络学习更鲁棒的特征表示。batch size 越小，这种噪声越大，正则化效果越强但训练越不稳定。

---

## 实际应用

**图像分类网络中的应用**：在 ResNet-50 中，每个卷积层后均接有批归一化层，全网络共有 53 个 BN 层。这使得 ResNet 可以使用 0.1 的初始学习率训练，而不会出现梯度爆炸，同时无需使用 Dropout。

**小 batch size 场景的替代方案**：当 GPU 显存受限导致 batch size 只有 2-4 时，批归一化的 $\mu_\mathcal{B}$ 和 $\sigma_\mathcal{B}^2$ 估计极不准确，此时应切换为**层归一化（Layer Normalization）**（对单样本的所有通道归一化）或**组归一化（Group Normalization）**（对通道分组归一化）。Facebook Research 在目标检测任务中发现，batch size=2 时 Group Normalization 比 BN 的 AP 高出约 1.8 个百分点。

**NLP/Transformer 架构中不用 BN 的原因**：文本序列长度可变，不同 token 的特征分布差异大，沿 batch 维度求均值无意义，因此 Transformer 系列模型（BERT、GPT 等）全部使用 Layer Normalization 而非 BN。

---

## 常见误区

**误区一：批归一化消除了权重初始化的重要性**
部分开发者认为有了 BN 就可以随意初始化权重。实际上，若初始权重导致某层输出在标准化前全为 0（零激活），BN 虽然能归一化但 γ 和 β 无法从零梯度中恢复。Xavier 或 He 初始化仍然是与 BN 配合的最佳实践，He 初始化（$\text{std} = \sqrt{2/n_{in}}$）专为 ReLU + BN 的组合设计。

**误区二：推理时忘记切换模式导致 bug**
在 PyTorch 中，若推理前未调用 `model.eval()`，BN 层仍会使用当前 batch 的统计量，且 running stats 会继续被更新，导致同一输入在不同调用时输出不同结果。这类 bug 在生产部署中极难发现，因为差异往往只有小数点后几位。

**误区三：批归一化完全消除了内部协变量偏移**
2018 年 MIT 的研究论文《How Does Batch Normalization Help Optimization?》通过实验证明，加入 BN 后网络各层的分布变化（Internal Covariate Shift）并未显著减少，BN 真正的贡献是让**损失曲面更加平滑**，使梯度方向更稳定、Lipschitz 常数更小，从而允许使用更大的学习率且不发散。这颠覆了 BN 原论文的理论解释，但不影响其工程价值。

---

## 知识关联

**与反向传播的关系**：BN 层的梯度计算涉及批内所有样本的耦合，$\frac{\partial \mathcal{L}}{\partial x_i}$ 不仅依赖 $\frac{\partial \mathcal{L}}{\partial y_i}$，还依赖批内所有其他样本的梯度之和，完整推导需要对 $\mu_\mathcal{B}$ 和 $\sigma_\mathcal{B}^2$ 分别求偏导后链式合并，这使得 BN 的反向传播比普通线性层复杂约 3 倍的计算步骤。

**与优化算法的关系**：批归一化使网络对学习率不敏感区间更宽，与 Adam 优化器配合时效果有时反而不如 SGD+Momentum，因为 Adam 本身也做了梯度的一阶和二阶矩归一化，与 BN 存在功能重叠，部分研究发现此组合会导致训练后期震荡。

**向更多归一化方法延伸**：理解批归一化的轴向操作（沿 batch 维度统计）之后，可以自然推导出 Layer Norm（沿特征维度）、Instance Norm（沿空间维度，用于风格迁移）和 Group Norm（通道分组）的设计动机——它们本质上是对"在哪个维度上计算均值和方差"这一问题给出不同回答。