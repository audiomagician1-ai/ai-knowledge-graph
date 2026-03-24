---
id: "cg-restir"
concept: "ReSTIR"
domain: "computer-graphics"
subdomain: "ray-tracing"
subdomain_name: "光线追踪"
difficulty: 5
is_milestone: false
tags: ["前沿"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 42.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.444
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# ReSTIR：时空重采样的实时直接光照算法

## 概述

ReSTIR（Reservoir-based Spatiotemporal Importance Resampling）是2020年由 Bitterli 等人在 SIGGRAPH 2020 上发表的实时直接光照算法，全称论文为《Spatiotemporal Reservoir Resampling for Real-Time Ray Tracing with Dynamic Direct Lighting》。该算法解决了场景中存在大量光源（数千乃至数百万个面光源）时实时渲染的核心难题：如何在每像素仅追踪极少量光线（通常为1条）的预算下，仍然收敛到接近无噪声的直接光照结果。

ReSTIR 的理论基石是重采样重要性采样（Resampled Importance Sampling，RIS）和蓄水池采样（Reservoir Sampling）。RIS 允许从一个易于采样的候选分布中生成样本，再通过权重重采样逼近目标分布（通常是 BSDF × 光源辐射度 × 几何项的乘积）；蓄水池采样则使得这一过程可以在 O(1) 额外内存下流式处理任意数量的候选样本。将二者结合后，ReSTIR 能够在 GPU 上高效地对数万个光源执行重要性采样，而无需预构建复杂的光源层次结构。

ReSTIR 之所以对实时光线追踪领域产生深远影响，在于它首次证明了通过"时间复用"和"空间复用"可以将有效样本数提升数十倍。在 NVIDIA RTX 硬件上的实测数据表明，ReSTIR 能够在 1080p 分辨率、场景含4.8百万个面光源的条件下以接近实时帧率渲染，而传统的均匀随机采样在相同条件下信噪比远不可用。

---

## 核心原理

### 重采样重要性采样（RIS）与无偏权重

RIS 的核心公式为：对候选样本集 $\{x_1, \ldots, x_M\}$ 从提议分布 $p$ 中采样，以权重 $w_i = \hat{p}(x_i) / p(x_i)$ 进行重采样，最终输出样本 $x_z$ 的无偏估计权重为：

$$W(x_z) = \frac{1}{\hat{p}(x_z)} \cdot \frac{1}{M} \sum_{i=1}^{M} w_i$$

其中 $\hat{p}$ 是目标函数（未归一化），$p$ 是提议分布。ReSTIR 将目标函数设为 $\hat{p}(x) = L_e(x) \cdot G(x) \cdot |\cos\theta|$（光源辐射度乘以几何项乘以余弦项），候选样本从均匀分布的光源中随机选取，通常每像素每帧生成 $M=32$ 个初始候选。

### 蓄水池数据结构与流式更新

ReSTIR 为每个像素维护一个"蓄水池"（Reservoir），其内部仅存储三个字段：当前选中样本 $y$、权重累积值 $w_{sum}$，以及计数器 $M$（已处理的候选数量）。当一个新候选 $x$ 到来时，以概率 $w(x)/w_{sum}$ 替换当前样本，否则保留。这一 O(1) 更新使得 GPU 上对32个候选的并行处理变为串行写入单个蓄水池，极大降低了显存带宽需求。时间复用时，上一帧的蓄水池通过运动向量重投影到当前帧，并与当前帧蓄水池合并，等效样本数翻倍至 $M=64$ 乃至更高。

### 空间复用与偏差修正

空间复用阶段，每个像素从屏幕空间内半径约30像素的邻域中随机选取若干邻居（论文默认取5个），将邻居的蓄水池合并到自身蓄水池中。直接合并邻居蓄水池时存在一个微妙的偏差来源：邻居的样本是对邻居像素的目标分布 $\hat{p}_{neighbor}$ 进行采样的，而非对当前像素的目标分布采样。为修正这一偏差，ReSTIR 需要用当前像素的目标函数重新评估邻居样本，并用修正后的权重合并。若忽略此步骤，则会在深度或法线差异显著的边界处产生能量泄漏（light bleeding）伪影。论文同时提供了有偏（biased）与无偏（unbiased）两种变体，有偏版本牺牲微量精度换取更高性能。

---

## 实际应用

**游戏引擎中的实现**：ReSTIR 已被整合进多个实时渲染管线。《赛博朋克2077》的 RT Overdrive 模式及 NVIDIA Falcor 框架均实现了 ReSTIR DI（Direct Illumination）变体。在 Falcor 中，ReSTIR 的标准配置为：每像素8个初始候选光源、时间复用上限 $M_{cap}=20$、空间复用邻居数为4，整体运行时间约 1.2ms（RTX 3090，1080p）。

**ReSTIR GI 的扩展**：2022年的 ReSTIR GI 将同一蓄水池框架扩展到间接照明路径，每个蓄水池存储一条完整的次级光线路径端点，通过时空复用复用已找到的高贡献间接光路径。这证明了蓄水池框架对多次弹射全局光照的适用性，但由于路径的非局部性，空间复用的偏差修正变得更加复杂，需要在邻居的表面位置重新追踪可见性射线。

**动态光源场景**：ReSTIR 在场景含大量动态光源时优势最为显著。对于含10万个动态点光源的场景，ReSTIR 仅需每像素1条阴影光线即可获得视觉上可接受的结果，而朴素的随机采样需要至少64条才能达到相近的噪声水平。

---

## 常见误区

**误区一：时间复用等效于简单的帧间滤波**
ReSTIR 的时间复用并非将多帧颜色值平均，而是在样本选择阶段就进行蓄水池合并，复用的是"哪个光源被选中"这一信息。这意味着时间复用不会引入帧间模糊，即使场景动态变化，只要运动向量正确且蓄水池计数器被正确地 clamp（论文建议 $M_{cap}$ 不超过20倍当前帧样本数），就不会出现重影。混淆两者会导致在运动场景中错误地关闭时间复用。

**误区二：ReSTIR 可以无偏地合并任意邻居蓄水池**
只有当邻居像素与当前像素的目标分布完全一致时，直接合并才是无偏的。实际中，法线或材质差异会导致 $\hat{p}$ 不同，若不执行"用当前像素目标函数重评估邻居样本"的步骤，能量误差可高达20%。无偏变体通过 MIS（多重重要性采样）权重补偿此偏差，代价是需要额外的可见性光线。

**误区三：ReSTIR 适合替代路径追踪的所有分量**
ReSTIR 的原始形式仅处理直接光照（一次光线弹射）。它对于焦散（caustics）、多次折射等需要连接特定光路拓扑的效果无效，因为蓄水池存储的是光源连接样本而非完整光路。将其误用于这些场景会导致明显缺失的间接高光效果。

---

## 知识关联

**前置知识——重要性采样**：ReSTIR 的 RIS 步骤直接依赖重要性采样的基本概念。理解为何目标分布 $\hat{p}$ 越接近被积函数方差越低，是理解 ReSTIR 为何选择 $L_e \cdot G \cdot |\cos\theta|$ 作为目标函数的关键。蓄水池采样中的权重 $w_i = \hat{p}(x_i)/p(x_i)$ 本质上就是重要性采样比（importance weight）的直接应用。

**与路径追踪的关系**：ReSTIR 处理的是直接光照积分的采样问题，路径追踪处理完整的渲染方程递归求解。在混合渲染管线中，ReSTIR DI 通常负责第一次弹射的直接光照，其余弹射由路径追踪或 ReSTIR GI 处理，二者通过辐照度缓存（irradiance cache）或G-Buffer衔接。

**与降噪器（Denoiser）的关系**：NVIDIA OIDN 或 NRD 等降噪器通常作为 ReSTIR 的后处理步骤。ReSTIR 降低了输入降噪器的信号方差，使降噪器在相同迭代次数下输出更清晰的结果，两者是互补而非替代关系。2022年后的实时管线几乎均采用"ReSTIR + NRD"的组合架构。
