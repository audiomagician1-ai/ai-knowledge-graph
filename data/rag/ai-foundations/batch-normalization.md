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
quality_tier: "B"
quality_score: 49.4
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.452
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 批归一化

## 概述

批归一化（Batch Normalization，简称 BatchNorm）是由 Sergey Ioffe 和 Christian Szegedy 于 2015 年在论文《Batch Normalization: Accelerating Deep Network Training by Reducing Internal Covariate Shift》中提出的训练技术。其核心操作是：在神经网络的每一层，对当前 mini-batch 内的激活值进行标准化，使其均值为 0、方差为 1，然后再通过可学习的缩放参数 γ 和平移参数 β 恢复表达能力。

批归一化解决的核心问题称为**内部协变量偏移（Internal Covariate Shift）**：随着训练进行，前一层参数更新会导致后一层的输入分布持续变化，迫使每层不断适应新的输入统计特性。BatchNorm 通过固定每层输入的分布来减轻这种效应，使得训练过程可以使用更大的学习率（实验中可将学习率提高 5-10 倍），并显著减少对精细初始化的依赖。

该技术在 ImageNet 分类任务上产生了显著效果：应用 BatchNorm 的 Inception 网络（Inception-v2）在 ImageNet 上的 Top-5 错误率降低至 4.8%，并且仅用原来 1/14 的训练步数就达到了原始 Inception 模型的精度。

## 核心原理

### 前向传播公式

BatchNorm 的前向计算分为四步。设一个 mini-batch 包含 $m$ 个样本，某层的激活值集合为 $\{x_1, x_2, \ldots, x_m\}$：

1. **计算批均值**：$\mu_B = \frac{1}{m} \sum_{i=1}^{m} x_i$

2. **计算批方差**：$\sigma_B^2 = \frac{1}{m} \sum_{i=1}^{m} (x_i - \mu_B)^2$

3. **标准化**：$\hat{x}_i = \frac{x_i - \mu_B}{\sqrt{\sigma_B^2 + \epsilon}}$，其中 $\epsilon$（通常取 $10^{-5}$）防止除以零

4. **缩放与平移**：$y_i = \gamma \hat{x}_i + \beta$，其中 $\gamma$ 和 $\beta$ 是随训练更新的可学习参数

这意味着 BatchNorm 给每个特征通道引入了 2 个额外的参数（$\gamma$ 和 $\beta$），如果一个卷积层有 256 个输出通道，对应的 BatchNorm 层就增加了 512 个参数。

### 训练与推理的行为差异

BatchNorm 在**训练阶段**使用当前 mini-batch 的统计量（$\mu_B$、$\sigma_B^2$）进行归一化。而在**推理阶段**，单个样本无法计算批统计量，因此模型使用训练过程中通过**指数移动平均（EMA）** 累积的全局均值 $\mu_{running}$ 和方差 $\sigma^2_{running}$，动量系数通常默认为 0.1（即 PyTorch 中 `momentum=0.1`）。这一训练/推理行为差异是实际工程中常见 bug 的来源——若推理时错误地保持 `model.train()` 模式，会导致测试性能不稳定。

### BatchNorm 对反向传播的影响

由于归一化操作对整个 mini-batch 的激活值进行了耦合，反向传播时梯度需要流经批统计量的计算图。具体而言，损失对 $x_i$ 的梯度不仅来自 $\hat{x}_i$ 本身，还来自 $\mu_B$ 和 $\sigma_B^2$ 对批内其他样本的依赖，这使得梯度天然地带有"批级别"的正则化效应。这种效应等价于在每个样本的梯度中注入了源于同批其他样本的噪声，被认为是 BatchNorm 具有轻微正则化作用的机制原因（在 batch size=32 时此效应最为明显，batch size 过大时正则化效应减弱）。

### 放置位置的惯例

BatchNorm 层通常插入在**线性变换（全连接/卷积）之后、激活函数之前**，即 Linear → BN → ReLU 的顺序。原始论文推荐此顺序，因为归一化的对象是线性变换的输出，使激活函数接收到分布稳定的输入。部分研究者将其置于激活函数之后，但实验表明前者在大多数场景下表现更优。

## 实际应用

**卷积神经网络训练加速**：在 ResNet 系列中，每个残差块的卷积层后均接 BatchNorm。ResNet-50 的批归一化层共有 53 个（每个残差块 2-3 个），若去掉这些层，使用相同学习率（0.1）训练会在数个 epoch 后出现梯度爆炸。BatchNorm 允许 ResNet 直接使用 SGD + 学习率 0.1 稳定训练 90 个 epoch。

**批大小敏感性**：当 batch size 小于 8 时，BatchNorm 的批统计量估计噪声过大，性能会显著下降。这是目标检测（如 Faster R-CNN 在单 GPU 上 batch size 仅为 2）和医学图像分析（高分辨率图像导致 batch size 受限）场景中改用 **Layer Normalization** 或 **Group Normalization** 的直接原因。FAIR 在 2018 年的研究表明，batch size 从 32 降至 2 时，BatchNorm 的检测 AP 下降约 1.5 个百分点，而 Group Normalization（分组数 G=32）几乎不受影响。

**迁移学习中的冻结策略**：使用预训练模型进行微调时，通常需要**冻结 BatchNorm 的 running stats**（调用 `model.eval()` 或逐层设置 `bn.eval()`），防止小 batch 的统计量覆盖掉在大规模数据上积累的可靠全局统计量，否则微调效果可能不稳定。

## 常见误区

**误区一：BatchNorm 完全等价于"将输入归一化到标准正态分布"**。实际上，由于可学习参数 γ 和 β 的存在，BatchNorm 层的最终输出分布并非固定为均值 0、方差 1。γ 和 β 会在训练中自主调整，极端情况下若 γ 被学习为很大的值，输出方差可以远超 1。标准化只发生在 $\hat{x}_i$ 这一中间步骤，最终输出 $y_i$ 的分布完全由数据和优化器共同决定。

**误区二：BatchNorm 的正则化效应足以完全替代 Dropout**。尽管 BatchNorm 具有轻微正则化效果，但两者机制不同：Dropout 以概率 p（常取 0.5）随机丢弃神经元，产生更强的正则化效果；BatchNorm 的噪声来自批统计量估计，随 batch size 增大而减弱。在小数据集（如 CIFAR-10 使用复杂模型）场景下，同时使用 BatchNorm 和 Dropout 仍然必要。值得注意的是，两者叠加使用有时会产生"BN-Dropout 不兼容"问题：Dropout 改变了激活值的方差，导致训练时的方差统计与推理时出现偏差，实践中建议将 Dropout 置于 BatchNorm 之后。

**误区三：推理时直接用测试集统计量替换 running stats 会更准确**。这在技术上可行，但会使模型在不同测试批次间行为不一致，且在生产部署中无法实时计算全量测试集统计量。正确做法是在训练阶段充分积累可靠的 running mean 和 running var，并在推理时固定使用它们。

## 知识关联

BatchNorm 的前向公式直接依赖对**反向传播**中计算图的理解——标准化步骤中 $\mu_B$ 和 $\sigma_B^2$ 都是关于 $\{x_i\}$ 的函数，反向传播时梯度需要正确流经这两个中间节点，手动推导 BatchNorm 的梯度公式（含 $\frac{\partial L}{\partial \gamma}$、$\frac{\partial L}{\partial \beta}$、$\frac{\partial L}{\partial x_i}$ 三项）是检验反向传播掌握程度的经典练习题。

BatchNorm 是理解**深度学习优化景观**的重要切入点：Santurkar 等人在 2018 年的论文中通过实验证明，BatchNorm 的主要贡献并非直接减少内部协变量偏移，而是使损失函数的梯度更加 Lipschitz 平滑（梯度的 $\ell_2$ 范数减少了约 30%），从而允许更大步长的优化。这一发现挑战了原论文的理论解释，至今仍是研究热点。理解 BatchNorm 后，可以自然延伸到针对不同场景设计的归一化变体：处理序列数据时使用 **Layer Norm**（对单样本所有特征归一化），生成对抗网络中使用 **Instance Norm**（对单样本单通道归一化），以及不依赖 batch size 的 **Group Norm**。