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
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# ReSTIR：时空重采样实时直接光照算法

## 概述

ReSTIR（Reservoir-based Spatio-Temporal Importance Resampling）是2020年由NVIDIA研究员Benedikt Bitterli等人在SIGGRAPH上发表的实时直接光照算法。该算法的核心突破在于：即使场景中有**数百万个光源**，也能在每帧每像素仅追踪少量光线的条件下，生成高质量的直接光照估计。这一成就将此前需要数分钟的复杂光照计算压缩到了实时帧率（30fps以上）。

ReSTIR的重要性在于彻底改变了实时渲染中多光源处理的上限。传统实时渲染通常只能处理少量动态光源，而ReSTIR通过"借用"邻近像素和历史帧的采样结果，让每个像素都能间接探索远超自身采样数的光源空间。该算法已被集成进NVIDIA的RTX Direct Illumination（RTXDI）框架，并在多款AAA游戏中实装。

算法的数学基础是**重采样重要性采样（Resampled Importance Sampling, RIS）**与**加权蓄水池采样（Weighted Reservoir Sampling）**的结合。RIS允许从一个易于采样的提案分布中生成候选样本，再通过权重比筛选出接近目标分布的最终样本；蓄水池采样则提供了一种在流式数据中进行在线采样的高效结构，使得时空复用成为可能。

---

## 核心原理

### RIS与目标PDF的构造

ReSTIR的采样目标是最小化直接光照积分的方差。直接光照积分为：

$$L_o = \int_{\Omega} f_r(\omega_i, \omega_o) \cdot L_i(\omega_i) \cdot |\cos\theta_i| \, d\omega_i$$

RIS从提案分布 $p$ 中生成 $M$ 个候选样本 $\{x_1, ..., x_M\}$，以概率 $\hat{p}(x_i) / \sum_j \hat{p}(x_j)$ 选择其中一个，其中 $\hat{p}$ 是目标函数的未归一化近似（通常取 $f_r \cdot L_i \cdot |\cos\theta|$）。当 $M$ 越大，最终样本的分布越接近真实被积函数，方差越低。

### 蓄水池数据结构

每个像素维护一个**蓄水池（Reservoir）**，结构体包含三个字段：
- **y**：当前存储的样本（一个光源）
- **w_sum**：所有候选样本权重之和
- **W**：无偏贡献权重，定义为 $W = \frac{w\_sum}{M \cdot \hat{p}(y)}$

蓄水池合并操作满足结合律：合并两个蓄水池 $R_1$（含 $M_1$ 个候选）与 $R_2$（含 $M_2$ 个候选），等价于从 $M_1 + M_2$ 个候选中重新采样，这一性质是时空复用的数学保障。

### 时间复用（Temporal Reuse）

当前帧的每个像素将前一帧对应位置（经过运动向量重投影）的蓄水池与当前蓄水池合并。为防止历史帧累积导致的"幽灵拖影"（ghosting），算法对历史蓄水池的 $M$ 值设置上限，通常为当前帧候选数的**20倍**。超出此限制则截断历史权重，确保场景变化后能快速适应。

### 空间复用（Spatial Reuse）

每个像素额外从其屏幕空间邻域（通常半径30像素内随机选取**k=5个**邻居）采集蓄水池进行合并。由于邻居像素的表面法线、材质可能与当前像素不同，直接合并会引入偏差。ReSTIR通过**几何相似性检测**（法线夹角 < 25°，深度差 < 10%）过滤不合适的邻居，并在偏差修正模式下使用MIS权重将偏差降为零，代价是方差略有上升。

---

## 实际应用

**游戏引擎中的RTXDI集成**：在《赛博朋克2077》的光追模式中，RTXDI使用ReSTIR处理场景中动态放置的数万个霓虹灯光源。玩家行走时，每帧每像素仅发射1条阴影光线，却能呈现出接近离线渲染的柔和多光源阴影，帧率维持在60fps（RTX 3080，1080p DLSS Quality）。

**离线渲染加速**：ReSTIR的思路也被引入路径追踪器，形成ReSTIR PT（路径空间版本，SIGGRAPH 2022）。该变体将蓄水池存储的对象从单个光源扩展为完整路径前缀，使复杂的全局光照计算也能受益于时空复用，在相同时间预算下比传统路径追踪降低**5-10倍**的方差。

**虚拟现实场景**：VR渲染中左右眼的图像高度相似，ReSTIR可在双眼之间共享蓄水池，进一步降低单眼所需的原始光线数量，在保持立体一致性的同时减少约40%的GPU开销。

---

## 常见误区

**误区一：时空复用样本数越多越好，不需要限制历史帧累积**
这是错误的。虽然更多的历史样本能降低方差，但当光源、相机或物体发生移动时，过旧的历史蓄水池存储的是已无效的光源样本，合并它们会引入系统性偏差（bias），表现为画面中出现持续性亮斑或暗斑。ReSTIR设置历史帧 $M$ 上限（通常20×当前帧候选数）并非保守，而是在方差与偏差之间取得平衡的必要措施。

**误区二：ReSTIR能处理所有类型的光照，包括间接光**
基础版ReSTIR（Bitterli 2020）**仅针对直接光照**设计，即单次弹射后直接到达光源的路径。它的蓄水池存储的是光源采样，不包含路径中间弹射点的信息。将其用于间接光（多次弹射）需要额外的路径空间扩展（ReSTIR GI或ReSTIR PT），这些是独立发展的变体，具有不同的蓄水池结构和偏差分析。

**误区三：空间复用不引入偏差**
未经修正的空间复用**确实有偏**。邻居像素的无偏贡献权重 $W$ 是基于邻居自身的 $\hat{p}$ 计算的，直接用于当前像素时分母的 $\hat{p}$ 值不匹配。Bitterli等人在论文中给出了两种去偏方案：一是用当前像素重新评估邻居样本的 $\hat{p}$（1/Z估计器），二是使用MIS权重精确修正，但均需额外的着色计算开销。

---

## 知识关联

**前置知识——重要性采样**：理解ReSTIR需要先掌握为何从接近目标函数的分布采样能降低方差（$\text{Var} \propto \int (f/p - \mu)^2 p \, d\omega$）。RIS是重要性采样的扩展：当真实目标分布难以直接采样时，RIS用多候选筛选来近似目标分布，$M$ 个候选相当于将有效样本质量从 $p$ 提升向 $\hat{p}$。

**延伸方向——时空滤波（SVGF/OIDN）**：ReSTIR输出的是低噪声但非零方差的图像，通常还需配合时空降噪器（如SVGF）做最终滤波。二者分工明确：ReSTIR负责找到高质量的光源样本，降噪器负责平滑残余噪声。在实际渲染管线中，RTXDI输出的ReSTIR结果会直接送入NRD（NVIDIA Real-time Denoisers）处理。

**理论连接——MIS（多重重要性采样）**：ReSTIR的去偏修正本质上是一种MIS权重的应用，将蓄水池合并视为来自不同像素提案分布的混合采样，并按各分布的PDF之和归一化，与Veach 1997年提出的平衡启发式权重形式相同。