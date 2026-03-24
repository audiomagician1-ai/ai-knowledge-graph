---
id: "cg-atmosphere-scatter"
concept: "大气散射实现"
domain: "computer-graphics"
subdomain: "volume-rendering"
subdomain_name: "体积渲染"
difficulty: 4
is_milestone: false
tags: ["环境"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.444
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 大气散射实现

## 概述

大气散射实现是指在实时图形渲染中，通过预计算查表（Look-Up Table，LUT）的方式高效模拟光线穿越大气层时发生的瑞利散射（Rayleigh scattering）与米氏散射（Mie scattering）的技术方案。这一方案由 Eric Bruneton 和 Fabrice Neyret 于 2008 年在论文《Precomputed Atmospheric Scattering》中系统化提出，将原本需要逐帧数值积分的大气辐射传输方程转化为离线预计算的多维纹理查询，使实时天空渲染在现代 GPU 上成为可能。

在物理上，太阳光进入大气时会经历单次散射（光线仅被散射一次抵达观察者）和多次散射（光线在大气粒子间反复弹射后抵达观察者）两种路径。单次散射是白天天空蓝色和日落橙红色的主要来源，多次散射则贡献了天空中的漫射辉光和地平线处的光晕。如果每帧对视线积分上述过程，计算量极大，因此预计算方案将这些积分结果存储在 2D、3D 或 4D 纹理中，运行时只需少量纹理采样即可重建完整的大气外观。

## 核心原理

### 辐射传输方程与散射积分

大气散射的物理基础是辐射传输方程（Radiative Transfer Equation，RTE）。沿视线方向 **v**，从相机位置 **p** 到大气顶界，单次散射辐射 $L$ 的积分形式为：

$$L(\mathbf{p}, \mathbf{v}) = \int_0^d T(\mathbf{p}, \mathbf{x}) \cdot \sigma_s(\mathbf{x}) \cdot P(\theta) \cdot L_{sun} \cdot T(\mathbf{x}, \mathbf{s}) \, dt$$

其中 $T(\mathbf{a}, \mathbf{b})$ 是从点 **a** 到点 **b** 的透射率（transmittance），由光学深度 $\tau = \int \sigma_e \, ds$ 的指数 $e^{-\tau}$ 给出；$\sigma_s$ 是散射系数；$P(\theta)$ 是相位函数（瑞利散射相位函数为 $P(\theta) = \frac{3}{16\pi}(1 + \cos^2\theta)$，Mie 散射常用 Henyey-Greenstein 近似）；$L_{sun}$ 是太阳辐照度。这个积分无解析解，需要数值离散化计算，而这正是预计算方案要离线完成的工作。

### 透射率 LUT（Transmittance LUT）

透射率 LUT 是所有后续 LUT 的基础，通常存储为一张 256×64 的 2D 纹理。其两个维度分别参数化为：**大气层中采样点的高度** $h$（从地球表面 0 km 到大气顶界约 100 km）和**天顶角余弦** $\mu = \cos\theta$。对于每一个 $(h, \mu)$ 对，预计算时沿该方向对 Rayleigh 和 Mie 消光系数 $\sigma_e(h)$ 进行数值积分，得到光学深度并取指数，存储 RGB 三通道透射率（分别对应可见光三个波长，瑞利散射系数与 $\lambda^{-4}$ 成正比，使得蓝光散射约为红光的 5.5 倍）。运行时查询此 LUT 可以在一次纹理采样内获得任意路径的透射率，而无需实时积分。

### 单次散射 LUT 与多次散射迭代

单次散射 LUT 通常是一张 3D 或 4D 纹理，参数化维度包括高度 $h$、视线天顶角余弦 $\mu_v$、太阳天顶角余弦 $\mu_s$，部分实现还加入视线与太阳方位角差 $\nu$，构成四维参数。Bruneton 2008 方案使用 32×128×32 分辨率的 3D 纹理存储散射结果。

多次散射通过迭代方式预计算：第 $n$ 阶散射贡献以第 $n-1$ 阶的散射辐射场作为新的"光源"重新积分。通常迭代 4 次后，累积的多次散射贡献已占总辐射量的 98% 以上，额外迭代收益递减。每次迭代需要一张中间 LUT（称为 Inscattered Radiance LUT），最终将各阶散射叠加到同一张纹理中。现代实现如 Sebastien Hillaire 在 2020 年《A Scalable and Production Ready Sky and Atmosphere Rendering Technique》中的方案，将多次散射压缩到一张 32×32 的 2D LUT，通过均匀方向积分进一步简化参数，极大降低了存储开销。

### 视线散射 LUT（Sky-View LUT）与相机散射 LUT（Aerial Perspective LUT）

现代方案通常还引入两张运行时 LUT。**Sky-View LUT**（分辨率约 192×108）存储从地面摄像机位置看向天空各方向的散射辐射，每帧更新一次，用于天空穹顶的快速渲染。**Aerial Perspective LUT**（分辨率约 32×32×32 的 3D 纹理）则存储地面上方场景中大气雾化（aerial perspective）效果所需的散射和透射数据，使地形、云朵等物体能正确呈现随距离增加而变蓝变淡的大气透视效果。

## 实际应用

**游戏引擎中的集成**：虚幻引擎 5 的 Sky Atmosphere 组件直接采用 Hillaire 2020 方案，预计算 Transmittance LUT（256×64）、Multi-Scattering LUT（32×32）和每帧 Sky-View LUT（192×104），整套方案在 PS5 上运行时间约为 0.2ms，满足实时渲染需求。Lumen 全局光照系统进一步采样 Sky Atmosphere LUT 为环境光遮蔽提供天空颜色。

**行星级场景渲染**：在需要从太空观察行星大气的场景中，LUT 参数化需要扩展以支持相机位于大气层外部的情形。此时高度 $h$ 的范围必须覆盖从地面到大气顶界外侧，并处理视线不与星球相交的情况（光学深度为 0，透射率为 1）。《无人深空》等游戏使用了类似方案处理从太空进入大气的过渡。

**动态天气与时间变化**：由于太阳角度 $\mu_s$ 已编码进 LUT 参数维度，改变太阳方位只需更新纹理采样坐标，无需重新预计算，实现实时日夜循环。但改变大气成分（如雾霾、沙尘增加 Mie 散射系数）则需要重新生成 LUT，部分引擎通过在不同预计算结果间插值实现动态天气效果。

## 常见误区

**误区一：认为预计算 LUT 只能处理静态太阳位置**。实际上，Bruneton 方案的 LUT 参数中包含了太阳天顶角 $\mu_s$，因此同一套预计算纹理支持任意太阳仰角的实时查询。Sky-View LUT 每帧重建也允许支持任意太阳方位角的变化，并非仅适用于静态光照。

**误区二：多次散射迭代越多结果越精确，应尽量增加迭代次数**。在真实大气参数（Rayleigh 散射系数约 $5.8 \times 10^{-6}\ \text{m}^{-1}$ @ 550nm，Mie 散射系数约 $2.1 \times 10^{-5}\ \text{m}^{-1}$）下，第 4 次及以后散射贡献已极为微小。Hillaire 2020 方案甚至用单次64方向均匀积分近似无限阶多次散射，视觉误差在 1% 以内，但计算量仅为迭代方案的几分之一。盲目增加迭代次数会成倍增加预计算时间，而没有可感知的视觉收益。

**误区三：Aerial Perspective LUT 与 Sky-View LUT 功能相同，可以互相替代**。两者参数化目标不同：Sky-View LUT 沿视线积分到大气顶界，用于纯天空背景渲染；Aerial Perspective LUT 则记录从相机到场景中任意深度处的散射积累，用于三维场景中雾化效果。将地形物体的大气透视效果直接用 Sky-View LUT 代替会导致近处物体出现错误的浓雾，远处物体颜色偏差严重。

## 知识关联

本方案建立在大气物理的瑞利散射和米氏散射理论之上，需要理解大气密度随高度的指数衰减模型（Rayleigh 标高约 8km，Mie 标高约 1.2km）以及相位函数的角度分布特性。透射率 LUT 的构建与体积渲染中的光学深度积分方法一脉相承，而多次散射迭代预计算在概念上与路径追踪中的多次弹射类似，但利用大气的均匀分层特性将问题降维处理。掌握本方案后，可以进一步延伸到云层体积渲染（需要将大气散射 LUT 作为环境光
