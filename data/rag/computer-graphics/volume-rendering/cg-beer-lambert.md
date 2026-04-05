---
id: "cg-beer-lambert"
concept: "Beer-Lambert定律"
domain: "computer-graphics"
subdomain: "volume-rendering"
subdomain_name: "体积渲染"
difficulty: 2
is_milestone: false
tags: ["物理"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 73.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# Beer-Lambert定律

## 概述

Beer-Lambert定律（又称Beer-Lambert-Bouguer定律）描述了光线穿过均匀吸收介质时强度的衰减规律。其核心公式为：

**I = I₀ · e^(-μ · d)**

其中 I₀ 为入射光强度，I 为透射光强度，μ 为消光系数（extinction coefficient，单位 m⁻¹），d 为光线穿越介质的路径长度。指数衰减形式意味着每增加相同厚度的介质，光强都会按相同比例减弱，而非等量减弱。

该定律由三位科学家分阶段建立：Pierre Bouguer 于1729年最早观察到光在海水中的衰减现象，Johann Heinrich Lambert 于1760年将其数学化，August Beer 于1852年进一步将消光系数与介质浓度联系起来。在体积渲染领域，Beer-Lambert定律是描述光在雾、云、烟、水体等参与介质中衰减的基础物理模型，任何体积渲染管线都必须在光线积分过程中实现这一衰减计算。

## 核心原理

### 光学深度（Optical Depth）

光学深度 τ（tau）是Beer-Lambert定律中的关键中间量，定义为消光系数沿光线路径的积分：

**τ = ∫₀ᵈ μₜ(x) dx**

其中 μₜ(x) 是位置 x 处的消光系数，可随空间变化。透射率（Transmittance）T 由光学深度直接给出：

**T = e^(-τ)**

当介质均匀时 μₜ 为常数，τ = μₜ · d，退化为最简形式。光学深度 τ = 1 时透射率约为 36.8%（即 1/e），τ = 3 时透射率仅剩约 5%，τ = 10 时透射率小于 0.005%，介质在实践中视为不透明。

### 消光系数的物理分解

在体积渲染的物理模型中，消光系数 μₜ 由两部分构成：

**μₜ = μₐ + μₛ**

其中 μₐ 为吸收系数（absorption coefficient），光子被介质吸收并转化为热能；μₛ 为散射系数（scattering coefficient），光子改变方向但未被消灭。两者的比值决定了介质的散射反照率 ω₀ = μₛ / μₜ。纯吸收介质（如染色玻璃）ω₀ ≈ 0，高散射介质（如云层）ω₀ 接近 1.0。单纯使用Beer-Lambert定律只处理消光，不包含散射光的重新注入，因此它描述的是"衰减"而非完整的体积光照。

### 在Ray Marching中的离散化实现

在Ray Marching中，光线被分割为 N 个步长为 Δx 的采样段，透射率以累乘方式计算：

**T_total = ∏ᵢ e^(-μₜᵢ · Δx) = e^(-Σᵢ μₜᵢ · Δx)**

每一段的局部透射率 tᵢ = e^(-μₜᵢ · Δx) 在代码中通常写为 `exp(-density * stepSize * extinctionCoeff)`。累积透射率从1开始不断乘以各段 tᵢ，当累积透射率降至某阈值（如 0.01）时，可提前终止步进以节省计算量，这一优化在实时渲染中至关重要。

## 实际应用

**云和雾的渲染**：在Houdini的VDB体积渲染或实时游戏引擎（如Unreal Engine的Volumetric Fog）中，消光系数由密度场 ρ(x) 乘以材质的消光率 σ 给出：μₜ(x) = σ · ρ(x)。雾效通常取 μₜ 在 0.01～0.1 m⁻¹ 之间，云层则可达 10～100 m⁻¹。

**水下渲染**：水对不同波长光的吸收系数差异显著：红光在水中 μₐ ≈ 0.35 m⁻¹，蓝绿光 μₐ ≈ 0.01 m⁻¹。因此5米水深后红光几乎完全消失，画面整体偏蓝绿，这一颜色漂移效果正是对Beer-Lambert定律按RGB三通道分别应用的结果。

**阴影光线的透射率计算**：体积阴影（Volumetric Shadow）需要沿光源方向对遮挡体积积分光学深度，然后将 e^(-τ) 作为阴影衰减系数叠加到直接光照上。这与相机光线的透射率计算原理完全相同，只是积分方向指向光源。

## 常见误区

**误区一：认为Beer-Lambert定律描述了完整的体积光照**。Beer-Lambert定律只处理光的消减（extinction），完全忽略了散射进入光线的能量（in-scattering）。在高散射介质（云、牛奶）中，如果只应用Beer-Lambert定律而不加入散射项，体积会显得异常黑暗，因为从四面八方散射来的光贡献被完全漏掉了。完整的渲染方程需要在此基础上加入体积发射和散射的积分。

**误区二：步长越小透射率计算越准确，因此应无限细分**。虽然减小 Δx 确实提高了光学深度积分的精度，但当步长小于介质密度变化的特征尺度时，精度提升可以忽略。更关键的是，浮点精度限制下，当单步光学深度 μₜ · Δx 极小时，`exp(-x) ≈ 1 - x` 的线性近似已足够精确，过度细分只浪费GPU算力。

**误区三：消光系数 μₜ 与波长无关**。这只在简化模型中成立。真实介质（烟雾、彩色玻璃）的 μₜ 是波长的函数，正确处理需对RGB三通道使用不同的消光系数，否则无法再现大气散射产生的蓝天、日落橙色等波长相关现象。

## 知识关联

**前置概念——Ray Marching**：Beer-Lambert定律本身只提供了衰减公式，它必须嵌入Ray Marching的步进循环才能被执行。Ray Marching决定采样点的位置和步长，而Beer-Lambert定律决定每一步对累积透射率的贡献量。两者的结合才构成体积密度积分的完整实现。

**后续概念——参与介质（Participating Media）**：参与介质将Beer-Lambert定律扩展为完整的体积渲染方程（Volume Rendering Equation，VRE）。VRE在Beer-Lambert衰减的基础上增加了相函数（Phase Function）描述的散射方向分布、自发光项，以及多次散射的路径追踪处理。理解Beer-Lambert定律中光学深度 τ 的定义，是推导VRE中透射率权重的直接前提，因为VRE中每个采样点的贡献都要乘以从相机到该点的累积透射率 e^(-τ)。