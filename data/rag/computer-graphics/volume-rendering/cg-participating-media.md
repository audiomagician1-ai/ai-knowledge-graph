---
id: "cg-participating-media"
concept: "参与介质"
domain: "computer-graphics"
subdomain: "volume-rendering"
subdomain_name: "体积渲染"
difficulty: 3
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.394
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 参与介质

## 概述

参与介质（Participating Media）是指光线在穿越时会发生吸收、散射或自发光三类物理交互的三维体积物质。与普通不透明表面不同，参与介质对光线的作用发生在体积内部的每一个微元处，而非仅在几何边界上。雾、云、烟、牛奶、皮肤次表面层乃至星云都属于参与介质的典型实例。

参与介质的理论体系源自19世纪的辐射传输理论（Radiative Transfer Theory），由天文学家 Subrahmanyan Chandrasekhar 于1950年在其著作《辐射传输》中系统化。在图形学领域，James Kajiya 与 Brian Von Herzen 于1984年将该理论引入体积渲染，发表论文《Ray Tracing Volume Densities》，奠定了现代参与介质渲染的基础。

参与介质的重要性在于它是自然界中大量视觉现象的物理根源。没有散射模型就无法模拟丁达尔效应中光柱的可见性，没有吸收模型就无法再现深海的颜色渐变。现代游戏引擎（如虚幻引擎5的 Heterogeneous Volumes 特性）和离线渲染器（如 RenderMan、Arnold）都将参与介质作为一等渲染对象处理。

## 核心原理

### 体积渲染方程（VRE）

参与介质的完整数学描述由**体积渲染方程**（Volumetric Rendering Equation，VRE）给出：

$$\frac{dL(\mathbf{x}, \omega)}{dt} = -(\sigma_a + \sigma_s) L(\mathbf{x}, \omega) + \sigma_a L_e(\mathbf{x}, \omega) + \sigma_s \int_{S^2} p(\omega', \omega) L(\mathbf{x}, \omega') \, d\omega'$$

其中：
- $L(\mathbf{x}, \omega)$ 为位置 $\mathbf{x}$ 处沿方向 $\omega$ 的辐射亮度
- $\sigma_a$（absorption coefficient）为**吸收系数**，单位 m⁻¹
- $\sigma_s$（scattering coefficient）为**散射系数**，单位 m⁻¹
- $\sigma_t = \sigma_a + \sigma_s$ 为**消光系数**（extinction coefficient）
- $L_e$ 为介质自身发射的辐射（如火焰的热辐射）
- $p(\omega', \omega)$ 为相函数，描述散射方向分布

方程右侧第一项为消光项（光线能量损失），后两项分别为自发光增益和散射入射光增益。

### 三种物理交互机制

**吸收（Absorption）**：介质粒子将光子能量转化为热能或其他形式，导致光线沿传播方向单调衰减。Beer-Lambert 定律描述纯吸收情形下的指数衰减，透射率为 $T = e^{-\sigma_a \cdot d}$，其中 $d$ 为光程长度。红葡萄酒对绿光的强吸收、蓝光的弱吸收正是参与介质选择性吸收的典型表现。

**散射（Scattering）**：光子与介质粒子碰撞后改变传播方向，分为**外散射**（out-scattering，光从当前方向被散射走，表现为能量损失）和**内散射**（in-scattering，其他方向的光被散射进当前方向，表现为能量增益）。散射系数 $\sigma_s$ 与粒子密度 $\rho$ 和单粒子散射截面 $C_s$ 的关系为 $\sigma_s = \rho \cdot C_s$。大气中瑞利散射的 $\sigma_s \propto \lambda^{-4}$ 解释了天空为何呈蓝色。

**发射（Emission）**：介质自身作为光源，向外辐射能量。发射项仅在温度较高或含荧光物质的介质中不可忽略。火焰渲染中，温度场直接映射为发射辐射，通常使用黑体辐射公式 $L_e \propto T^4$ 近似（Stefan-Boltzmann 定律）。

### 单次散射与多次散射

**单次散射**（Single Scattering）假设每个光子在到达观测点之前最多发生一次散射事件，计算量较小，适合薄介质（如淡雾）。其贡献可解析积分：

$$L_{single}(\mathbf{x}, \omega) = \int_0^d T(\mathbf{x}, \mathbf{x}(t)) \cdot \sigma_s \cdot p(\omega_L, \omega) \cdot L_{light} \cdot T_{shadow} \, dt$$

**多次散射**（Multiple Scattering）允许光子在浓密介质（如云、牛奶）中经历数十乃至数千次散射，是浓雾中无方向感漫射光的来源。多次散射通常无解析解，需借助路径追踪、光子映射或扩散近似（Diffusion Approximation）数值求解。

## 实际应用

**大气散射**：游戏引擎中的大气渲染将整个大气层建模为以高度为密度函数的参与介质，使用 Bruneton-Neyret 2008 年提出的预计算查找表方法，将 $\sigma_s(\lambda, h)$ 分为瑞利层（标高约8 km）和 Mie 散射层（标高约1.2 km）分别处理，最终合成日落时橙红色的散射效果。

**烟雾渲染**：Arnold、Houdini 中的烟雾将密度场 $\rho(\mathbf{x})$ 存储在 OpenVDB 格式的稀疏体素网格中（典型分辨率 256³ 至 1024³），在渲染时按 $\sigma_s = \rho \cdot k_s$（$k_s$ 为用户可调散射密度系数）动态计算介质参数，通过 Delta Tracking（也称 Woodcock Tracking）算法在非均匀密度场中无偏采样自由飞行距离。

**皮肤渲染**：皮肤的多层结构（表皮、真皮）可建模为浅层参与介质，采用扩散近似的偶极模型（Dipole Model，Jensen et al. 2001）计算次表面散射，其中平均自由程 $l_{mfp} = 1/\sigma_t$ 对人类皮肤约为 1–2 mm，决定了皮肤的通透感和次表面光晕范围。

## 常见误区

**误区1：将消光系数等同于不透明度**。消光系数 $\sigma_t$ 是单位长度的衰减率（单位 m⁻¹），而不是一个无量纲的概率值。同一个 $\sigma_t = 1.0 \text{ m}^{-1}$ 的介质，在 0.1 m 厚时透射率为 $e^{-0.1} \approx 90.5\%$，在 5 m 厚时仅剩 $e^{-5} \approx 0.67\%$。忽略厚度直接用 $\sigma_t$ 控制"透明度"会导致与厚度无关的错误结果。

**误区2：认为散射必然使介质看起来更亮**。散射同时包含外散射（能量损失）和内散射（能量增益）两个过程。在高反照率（$\omega_0 = \sigma_s / \sigma_t$ 接近1）的介质中，散射确实保留大量能量；但当 $\omega_0$ 较低（如含碳烟灰的黑烟，$\omega_0 \approx 0.2$）时，主要表现为强烈消光，介质整体显暗而非亮。

**误区3：用透明表面的折射来替代介质的散射**。折射（Snell定律）描述光在界面处的方向改变，而参与介质散射是体积内部连续发生的统计过程。雾的弥散感来自数百万次微粒散射事件的积累，绝非可用一次折射建模。混淆两者会导致雾效果带有不真实的玻璃感。

## 知识关联

**前置概念**：Beer-Lambert 定律给出了纯吸收介质中的指数透射率公式，是 VRE 中消光项的单光束简化形式。理解参与介质需要将 Beer-Lambert 从标量透射率扩展到包含方向性散射和发射的完整辐射传输框架。

**直接后继**：**相函数**（Phase Function）专门描述 VRE 中 $p(\omega', \omega)$ 项，即散射方向的概率分布，Henyey-Greenstein 相函数（1941年）是图形学中最常用的单参数近似模型。掌握参与介质后，**体积阴影**（Volume Shadows/Deep Shadow Maps）处理光线在介质中传播至阴影采样点时的透射率积累；**流体渲染**和**烟雾模拟**则在参与介质渲染框架之上引入流体动力学的密度场生成；**异构体积**（Heterogeneous Volume）进一步处理空间变化的 $\sigma_a(\mathbf{x})$ 和 $\sigma_s(\mathbf{x})$ 带来的非均匀积分挑战。
