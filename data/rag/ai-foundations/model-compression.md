---
id: "model-compression"
concept: "模型压缩"
domain: "ai-engineering"
subdomain: "ai-foundations"
subdomain_name: "AI基础"
difficulty: 5
is_milestone: false
tags: ["pruning", "quantization", "distillation"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.2
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.419
last_scored: "2026-03-23"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 模型压缩

## 概述

模型压缩（Model Compression）是指在尽量保持模型预测精度的前提下，通过技术手段减小模型的参数量、计算量或存储占用，使其适合在资源受限的环境（如移动端、边缘设备、嵌入式芯片）中部署的一组工程技术。2006年Buciluǎ等人发表的论文《Model Compression》首次系统性地提出将大模型知识迁移到小模型的方法，此后该领域在深度学习兴起后迅速扩展，形成了剪枝、量化、知识蒸馏、低秩分解等多条技术路线。

以GPT-3为例，其拥有1750亿参数，原始推理需要数百GB显存，直接部署在消费级硬件上不可行。模型压缩的价值在于：将推理延迟降低至毫秒级、将模型文件大小从GB压缩到MB，同时维持95%以上的原始精度。这一目标不仅是工程上的优化，更涉及精度与效率之间的量化权衡，需要在压缩率（Compression Ratio）与精度损失（Accuracy Drop）之间找到最优操作点。

---

## 核心原理

### 1. 剪枝（Pruning）

剪枝的核心假设来自"彩票假说"（Lottery Ticket Hypothesis，Frankle & Carlin, 2019）：大型神经网络中存在规模更小的子网络（"中奖彩票"），经过单独训练后可达到与原网络相近的精度。

剪枝分为**结构化剪枝**和**非结构化剪枝**两类：
- **非结构化剪枝**：将权重矩阵中绝对值低于阈值 θ 的参数直接置零，形成稀疏矩阵。典型判断标准为 L1 范数：若 |w_ij| < θ，则 w_ij = 0。稀疏度可达 90% 以上，但需要专用稀疏计算硬件才能实现真实加速。
- **结构化剪枝**：移除整个卷积核、注意力头或神经元通道，使模型可以在标准硬件上直接加速。例如在 VGG-16 上移除 50% 的卷积核后，推理速度提升约 2×，而 Top-5 准确率仅下降 0.3%。

剪枝流程通常遵循"训练→剪枝→微调"的三阶段循环，微调阶段用于恢复被剪枝损失的精度。

### 2. 量化（Quantization）

量化将模型参数和激活值从高精度浮点数（通常为 FP32，32位）转换为低精度整数（INT8、INT4 甚至二值）。核心公式为线性均匀量化：

$$Q(x) = \text{round}\left(\frac{x - x_{min}}{x_{max} - x_{min}} \times (2^b - 1)\right)$$

其中 b 为目标比特数，$x_{min}$ 和 $x_{max}$ 为校准数据集上的观测范围。

量化分为两种工程路径：
- **训练后量化（PTQ，Post-Training Quantization）**：不需要重新训练，只需少量校准数据（通常100~1000张图片）即可完成，TensorFlow Lite 和 ONNX Runtime 均原生支持 INT8 PTQ。FP32 → INT8 可使模型体积缩小 4×，推理速度在 CPU 上提升 2~3×。
- **量化感知训练（QAT，Quantization-Aware Training）**：在前向传播中模拟量化噪声，通过梯度传播学习对量化更鲁棒的权重分布，可将 INT4 量化的精度损失控制在 1% 以内，但需要原始训练数据和完整训练流程。

### 3. 知识蒸馏（Knowledge Distillation）

知识蒸馏由 Hinton 等人在 2015 年正式提出（《Distilling the Knowledge in a Neural Network》）。其核心机制是让小模型（Student）学习大模型（Teacher）的**软标签（Soft Labels）**，而非仅仅学习 one-hot 硬标签。

损失函数为：

$$\mathcal{L} = \alpha \cdot \mathcal{L}_{CE}(y, \hat{y}_{student}) + (1-\alpha) \cdot T^2 \cdot \mathcal{L}_{KL}\left(\sigma\left(\frac{z_T}{T}\right), \sigma\left(\frac{z_S}{T}\right)\right)$$

其中 T 为温度超参数（通常取 3~10），$\alpha$ 控制两类损失的权重，$z_T$ 和 $z_S$ 分别为 Teacher 和 Student 的 logits。温度 T 使原本尖锐的概率分布变得平滑，从而让 Student 学到类别间的相关性信息（例如"猫"与"虎"的相似性远大于"猫"与"汽车"）。

BERT 的知识蒸馏版本 DistilBERT 将参数量从 1.1 亿压缩到 6600 万（缩减 40%），推理速度提升 60%，而在 GLUE 基准上保留了 97% 的原始性能。

### 4. 低秩分解（Low-Rank Decomposition）

将权重矩阵 W（m×n）近似分解为两个小矩阵的乘积：W ≈ UV，其中 U 为 m×r，V 为 r×n，r ≪ min(m,n)。参数量从 mn 减少到 r(m+n)，当 r < mn/(m+n) 时实现压缩。SVD（奇异值分解）是实现低秩分解的常用工具，通过保留前 r 个最大奇异值来控制近似误差。

---

## 实际应用

**移动端图像分类**：MobileNetV3 利用深度可分离卷积（Depthwise Separable Convolution）结合通道剪枝，将标准 ResNet-50 的 2500 万参数压缩到 530 万，同时 ImageNet Top-1 精度仅降低约 2%，可在 ARM Cortex-A 芯片上以 50ms 完成单张图片推理。

**大语言模型边缘部署**：LLaMA-7B 通过 GPTQ（4-bit 量化）将模型从 13GB 压缩到约 4GB，可在 8GB 显存的消费级 GPU（如 RTX 3080）上运行，是目前最流行的本地 LLM 部署方案之一。

**语音识别芯片**：华为 NPU 上部署的语音模型通过 INT8 量化感知训练，在骁龙 888 芯片上将 ASR 推理延迟从 120ms 降低到 45ms，功耗降低 35%。

---

## 常见误区

**误区一：量化比特数越低，压缩效果一定越好。**
这忽略了精度损失随比特数降低呈非线性上升的规律。从 FP32 → INT8 精度损失通常低于 1%，但从 INT8 → INT4 精度损失可能跳升至 3%~10%，对 Transformer 中的注意力权重尤为敏感。实际工程中常采用**混合精度量化**，对关键层保留 INT8，只对其余层做 INT4，以平衡压缩率与精度。

**误区二：知识蒸馏中 Student 模型可以无限缩小。**
当 Student 的容量（参数量）远低于 Teacher 时，会出现"容量瓶颈"，无论如何调整温度 T 或损失权重 α，Student 都无法充分吸收 Teacher 的软标签信息。实证研究表明，Student 参数量低于 Teacher 的 10% 后，蒸馏增益会急剧下降，此时应结合剪枝先从 Teacher 中派生中间模型再逐步蒸馏。

**误区三：剪枝后无需微调即可保持精度。**
非结构化剪枝后即使稀疏度只有 50%，不经过微调的模型精度通常下降 5%~15%。实验表明，微调步数至少需要原训练步数的 10%~20% 才能充分恢复精度，跳过这一步直接部署是工程实践中最常见的失误之一。

---

## 知识关联

**与深度学习入门的关系**：模型压缩的操作对象是已训练好的神经网络权重矩阵，需要掌握反向传播、梯度计算和 Batch Normalization 的工作原理，才能理解量化感知训练中梯度如何穿越离散化操作（通过直通估计器 STE 实现）以及剪枝后微调的参数更新过程。

**与迁移学习的关系**：知识蒸馏可视为一种特殊的迁移学习——Teacher 扮演"知识源"，而 Student 通过模仿 Teacher 的输出分布而非直接微调 Teacher 的权重，来实现从大模型到小模型的知识转移。迁移学习中的预训练-微调范式同样适用于蒸馏后的 Student 模型在下游任务上的精细调整。在实际 MLOps 流水线中，模型压缩通常是模型从训练集群走向推理服务的最后一道必经工程关卡，与 A/B 测试、推理延迟基准测试共同构成上线前的质量保障体系。
