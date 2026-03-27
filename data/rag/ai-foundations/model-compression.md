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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 模型压缩

## 概述

模型压缩（Model Compression）是指在尽量保留模型预测精度的前提下，减少神经网络的参数量、计算量或存储占用的技术集合。一个典型的 ResNet-50 模型有约 2500 万参数、占用 97.8 MB 磁盘空间，在移动端或嵌入式设备上直接部署会遇到内存不足和推理延迟过高的问题，模型压缩正是为解决这一矛盾而生。

模型压缩的研究可追溯至 1990 年 LeCun 等人提出的 Optimal Brain Damage（OBD）方法，该方法利用二阶导数信息评估权重重要性并将其裁剪。2015 年 Han et al. 在 NeurIPS 上发表 "Deep Compression" 论文，将剪枝、量化与霍夫曼编码结合，在 AlexNet 上实现了 35× 压缩率，同时精度损失小于 1%，标志着现代模型压缩进入系统化研究阶段。

模型压缩的价值不仅在于降低存储成本，更在于减少推理时的乘加运算（MAC），使模型能在 IoT 设备、手机 NPU 或自动驾驶芯片等算力受限场景中实时运行，同时减少云端推理的电力消耗，对碳排放也有直接影响。

---

## 核心原理

### 1. 剪枝（Pruning）

剪枝的基本思路是移除对输出贡献小的权重或结构单元。按粒度分为两类：

- **非结构化剪枝（Unstructured Pruning）**：将单个权重置零，可达到 90% 以上的稀疏率，但产生的稀疏矩阵需要专用稀疏加速库（如 NVIDIA cuSPARSE）才能获得实际加速。
- **结构化剪枝（Structured Pruning）**：移除整个卷积核、通道或注意力头，生成的模型是稠密的，可直接在通用硬件上加速。例如，对 VGG-16 的卷积通道剪枝后，FLOPs 可降低约 34%，Top-5 精度仅下降 0.2%。

衡量权重重要性的常用指标包括：绝对值大小（L1/L2 范数）、梯度幅值、以及基于泰勒展开的一阶重要性分数 $I_i = |g_i \cdot w_i|$，其中 $g_i$ 为权重 $w_i$ 对应的梯度。剪枝后通常需要进行**微调（fine-tuning）**以恢复精度损失，"剪枝-微调"可迭代多轮。

### 2. 量化（Quantization）

量化将浮点权重或激活值映射到低比特整数表示。标准训练使用 FP32（32位浮点），而 INT8 量化将每个参数从 4 字节压缩至 1 字节，内存占用降至 1/4，且整数运算在 ARM、Intel VNNI 等硬件上吞吐量提升 2-4 倍。

量化分两种主要范式：

- **训练后量化（Post-Training Quantization, PTQ）**：无需重新训练，使用少量校准数据确定量化参数（scale 和 zero_point）。适用于快速部署，但 INT4 以下精度损失通常较大。
- **量化感知训练（Quantization-Aware Training, QAT）**：在训练中插入伪量化节点，前向传播模拟低比特运算，反向传播用直通估计器（Straight-Through Estimator, STE）绕过不可导的取整操作。QAT 在 MobileNetV2 上的 INT8 精度通常比 PTQ 高 0.5%-1.5%。

量化的核心公式为对称量化：
$$q = \text{round}\left(\frac{r}{s}\right), \quad s = \frac{\max(|r|)}{2^{b-1}-1}$$
其中 $r$ 为原始浮点值，$s$ 为缩放因子，$b$ 为目标比特数。

### 3. 知识蒸馏（Knowledge Distillation）

Hinton 等人于 2015 年提出知识蒸馏：用大模型（教师）的软标签（soft label）监督小模型（学生）训练。软标签通过**温度系数 $T$** 软化概率分布：

$$p_i = \frac{\exp(z_i / T)}{\sum_j \exp(z_j / T)}$$

当 $T > 1$ 时，类别间的相对概率差异变小，使学生模型能学到类别间的相似性结构（"暗知识"），而非仅学习硬标签的 0/1 分类边界。蒸馏损失为：

$$\mathcal{L} = \alpha \cdot T^2 \cdot \text{KL}(p^T_\text{teacher} \| p^T_\text{student}) + (1-\alpha) \cdot \text{CE}(y, p_\text{student})$$

其中 $\alpha$ 平衡蒸馏项与交叉熵项，$T^2$ 用于补偿梯度被温度缩放带来的幅值损失。DistilBERT 使用知识蒸馏将 BERT-base 的参数从 110M 压缩到 66M，推理速度提升 60%，在 GLUE 基准上保留了 97% 的性能。

### 4. 低秩分解（Low-Rank Decomposition）

对权重矩阵 $W \in \mathbb{R}^{m \times n}$ 进行 SVD 分解：$W \approx U \Sigma V^\top$，截取前 $r$ 个奇异值，将原始 $mn$ 个参数压缩为 $(m+n)r$ 个。当 $r \ll \min(m,n)$ 时压缩效果显著。此方法常用于 Transformer 的注意力层和大型 Embedding 层。

---

## 实际应用

**边缘端部署（MobileNet + INT8）**：Google 在 Pixel 手机上部署语音唤醒模型时，采用结构化剪枝 + INT8 PTQ 的组合，将原始 3MB 模型压缩至 300KB，在 DSP 上实现实时推理，延迟低于 10ms。

**大语言模型压缩（GPTQ / AWQ）**：LLaMA-7B 原始精度为 FP16，占用约 14GB 显存。使用 GPTQ（一种逐层 INT4 量化算法，2022 年提出）可将显存降至 3.5GB，在单张 RTX 3060（12GB）上运行，困惑度（perplexity）仅上升约 0.3。

**推荐系统 Embedding 压缩**：工业界推荐模型中 Embedding 表可达数百 GB，TikTok 等公司使用组合码（Compositional Embedding）技术，将 Embedding 用两个小矩阵相加表示，压缩率达 10-100×，CTR 指标下降不超过 0.5%。

---

## 常见误区

**误区一：量化比特数越低，速度一定越快。** INT4 相比 INT8 参数量减半，但当前主流 CPU/GPU 的 SIMD 指令集原生支持 INT8 运算，而 INT4 往往需要将两个 INT4 拼成一个 INT8 再计算，实际推理速度提升幅度因硬件而异，在某些设备上 INT4 的延迟甚至与 INT8 相近。

**误区二：知识蒸馏必须用同架构的教师和学生模型。** 实际上，教师和学生可以是完全不同的架构，例如用 Vision Transformer 作为教师蒸馏 MobileNet 学生。只有在中间层特征蒸馏（Feature-based Distillation）时才需要对齐通道维度，但可以通过投影层解决。

**误区三：剪枝后直接量化精度损失可以叠加。** 剪枝和量化分别引入的精度误差并非简单相加，而是存在非线性交互。通常推荐先剪枝微调使模型收敛，再进行量化，顺序颠倒或同步进行时需要更仔细的联合优化，否则精度损失可能超过两者之和。

---

## 知识关联

**与深度学习入门的衔接**：理解卷积核、全连接层的权重矩阵结构，以及反向传播中梯度的计算方式，是理解 L1 剪枝准则和 STE 量化梯度的直接前置知识。没有对 BatchNorm 层工作原理的了解，就难以正确处理通道剪枝后 BN 统计量的更新。

**与迁移学习的衔接**：模型压缩中的微调阶段与迁移学习的微调策略高度重合——都需要选择合适的学习率（通常为原始训练的 1/10 至 1/100），以及决定冻结哪些层。知识蒸馏在形式上也是一种迁移：将教师模型的"知识"迁移至更小的学生网络，其软标签目标函数正是该迁移过程的数学化表达。

**扩展方向**：掌握上述三大基础技术后，可进一步探索神经架构搜索（NAS）中的硬件感知搜索（Hardware-Aware NAS），以及近年兴起的稀疏大模型（Sparse Mixture-of-Experts）等研究方向，这些方向本质上都是将压缩的思想与架构设计深度结合的产物。