---
id: "cg-heterogeneous"
concept: "异构体积"
domain: "computer-graphics"
subdomain: "volume-rendering"
subdomain_name: "体积渲染"
difficulty: 4
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 异构体积

## 概述

异构体积（Heterogeneous Volume）是指消光系数 σₜ(x) 随空间位置 x 变化的参与介质，与均匀体积（σₜ 为常数）相对。云朵、烟雾、火焰、皮肤次表面散射等自然现象都呈现出高度空间变化的密度场，无法用单一标量表征整个体积的光学特性。在体积渲染中，异构体积的核心难题在于：透射率积分 T(a,b) = exp(−∫ₐᵇ σₜ(x) dx) 没有解析解，必须依赖数值方法估计。

20世纪60至70年代，核物理中的蒙特卡洛中子输运领域最早发展了处理空间变化截面的采样技术。Woodcock等人于1965年提出了 Woodcock Tracking（即 Delta Tracking 的前身），通过引入虚拟碰撞将非均匀问题转化为均匀问题处理。图形学界在2010年代将此方法系统引入路径追踪渲染器，Kutz、Hachisuka 等人2017年在 SIGGRAPH 发表的工作进一步从理论上统一了 Delta Tracking 的无偏估计框架。

异构体积对实时与离线渲染都构成显著的性能瓶颈：由于每步采样都需要查询三维纹理或稀疏体素格（如 OpenVDB），采样频率和加速结构的设计直接决定渲染效率。正确理解异构体积的采样算法，是实现云渲染、体积光散射等效果不可或缺的基础。

---

## 核心原理

### Delta Tracking 算法

Delta Tracking 的核心思想是引入一个全局上界 σ̄，使得 σ̄ ≥ σₜ(x) 对体积内所有位置 x 成立。将差值 σₙ(x) = σ̄ − σₜ(x) 定义为**虚拟（null）碰撞截面**，则总截面恒为常数 σ̄，可以像均匀介质一样生成指数分布的候选碰撞距离：

> t ~ Exponential(σ̄)，即 t = −ln(ξ) / σ̄，ξ ∈ (0,1)

到达候选点 x = ray_origin + t·d 后，执行**概率接受-拒绝**：
- 以概率 σₜ(x) / σ̄ 接受为**真实碰撞**（散射或吸收）
- 以概率 σₙ(x) / σ̄ 拒绝，视为**虚拟碰撞**，继续追踪

该过程无需预先计算透射率，每次迭代只需一次局部密度查询，天然适合空间稀疏且分布不规则的介质。

### 上界 σ̄ 的选取与 DDA 加速

σ̄ 的选取直接影响算法效率：若 σ̄ 设置过高，虚拟碰撞占比 σₙ/σ̄ 增大，平均需要更多次迭代才能找到真实碰撞，浪费算力。实践中常采用**层次化包围盒（Hierarchical Bounding Volume）**或 **DDA（Digital Differential Analyzer）**网格遍历，将体积划分为若干格子，每个格子存储局部最大密度 σ̄_cell。Delta Tracking 在每个格子内使用该格子的局部上界，跨格时更新 σ̄_cell，称为 **Residual Ratio Tracking** 或 **Majorant Grid** 方案。

OpenVDB 中的 VDB 树结构天然契合这一需求：其层次节点（Root→Internal→Leaf）的每一层都可缓存子树的最大值，从而提供多分辨率的 σ̄_cell 估计，将平均步进次数从数百次压缩至十次量级。

### 透射率估计：Ratio Tracking

若需估计两点间的透射率 T(a,b) 而非直接采样碰撞点（例如计算阴影），Delta Tracking 的对应方法称为 **Ratio Tracking**：

> T(a,b) = E[ ∏ᵢ (1 − σₜ(xᵢ) / σ̄) ]

沿射线按 σ̄ 采样候选点序列 x₁, x₂, …，每个候选点贡献权重因子 (1 − σₜ(xᵢ)/σ̄)，所有因子的乘积即为无偏透射率估计量。相比 Ray Marching 的固定步长积分，Ratio Tracking 在低密度区域自动用较少的样本点，在高密度区域自动密集采样，方差通常更低。

---

## 实际应用

**云与大气散射渲染**：《荣耀战魂》与《地平线：零之曙光》等游戏使用基于 Majorant Grid 的 Delta Tracking 渲染实时体积云，将云层的 σ̄ 分格存储在 32³ 的低分辨率网格中，节约了约 60%-80% 的虚拟碰撞步数。

**电影级烟雾渲染**：Pixar 的 RenderMan 及 SideFX Houdini 的 Mantra 渲染器均支持 OpenVDB 格式输入的异构体积，采用 Delta Tracking 配合多重重要性采样（MIS）进行路径追踪。典型的烟雾模拟帧包含 500³ 至 2000³ 的体素场，每条光路在体积内平均散射 3-8 次才逃逸。

**医学体绘制（Volume Rendering）**：CT/MRI 数据本质上是三维异构密度场，但医学渲染更常用确定性积分（如 GPU Ray Casting + 预积分传输函数），而非蒙特卡洛 Delta Tracking——这是领域差异的一个典型分界点。

---

## 常见误区

**误区一：以为 σ̄ 取体积的全局最大值是最优策略**
初学者常将 σ̄ 设为整个体积内 σₜ 的全局上界，导致在大量空旷区域执行极高频率的虚拟碰撞。正确做法是使用 Majorant Grid，让局部格子的 σ̄_cell 尽可能贴近局部真实密度，当体积稀疏度超过 90% 时，局部上界可将期望步进次数从 O(σ̄_global/σ̄_avg) 降低至接近 O(1)。

**误区二：将 Delta Tracking 与 Ray Marching 的偏差混淆**
Ray Marching 用固定步长 Δt 近似透射率积分，本质上是有偏估计，步长选择不当会导致能量误差（通常需 Δt ≤ 1/σ̄ 以避免欠采样）。Delta Tracking 是严格无偏的——只要密度查询本身正确，无论 σ̄ 多大，估计量的期望值始终等于真实透射率，误差仅体现为方差增加，而非系统性偏差。

**误区三：认为异构体积的相函数必须也是空间变化的**
密度 σₜ(x) 的空间变化与相函数 f_p(ω, ω') 的空间变化是相互独立的两件事。一个体积可以有高度异构的密度场，但同时使用全局均匀的 Henyey-Greenstein 相函数（不对称因子 g 为常数）。Delta Tracking 仅负责采样碰撞位置，碰撞方向的采样由相函数独立处理。

---

## 知识关联

**前置概念：参与介质**提供了 σₜ、σₛ、σₐ 以及透射率 T(a,b) 的数学定义，是理解异构体积为何难以积分的基础。均匀介质中 T(a,b) = exp(−σₜ(b−a)) 有解析形式，而异构体积将此公式推广为 σₜ(x) 的路径积分，消除了解析解的可能。

**延伸方向**：理解异构体积后，可进一步研究**谱 MIS（Spectral MIS）**与**多色 Delta Tracking**——在波长相关的消光系数场景中（如彩色烟雾），不同波长的 σₜ(x,λ) 各不相同，需要为每个波长维护独立的 σ̄(λ) 或采用单一英雄波长（Hero Wavelength）策略来联合采样，这是 2019 年后电影渲染中的活跃研究方向。