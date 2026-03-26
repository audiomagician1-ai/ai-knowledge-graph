---
id: "vfx-fluid-lagrange"
concept: "拉格朗日粒子法"
domain: "vfx"
subdomain: "fluid-sim"
subdomain_name: "流体模拟"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.483
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# 拉格朗日粒子法

## 概述

拉格朗日粒子法是一种以流体本身的运动粒子为计算对象的流体模拟方法，与欧拉法在固定空间网格上记录流体属性不同，拉格朗日法让每个粒子携带自己的速度、密度、压力等物理量，随流体一起运动。这种"跟着流体走"的视角，由18世纪数学家约瑟夫-路易·拉格朗日提出，用于描述连续介质运动的数学框架。

在特效领域，拉格朗日粒子法最常见的实现形式是**光滑粒子流体动力学（SPH，Smoothed Particle Hydrodynamics）**，该方法1977年由Lucy以及Gingold和Monaghan独立提出，最初用于天体物理模拟，后来广泛应用于影视特效中的水花飞溅、熔岩流动、雪崩等场景。相比欧拉法，拉格朗日法天然支持自由表面追踪，不需要额外的Level Set或VOF界面重建步骤，这使它在处理大变形、破碎水花时表现出色。

## 核心原理

### 光滑核函数与邻域搜索

SPH的核心数学工具是**光滑核函数 W(r, h)**，其中 r 是两粒子之间的距离，h 是光滑长度（影响半径）。常用的三次样条核函数定义为：

$$W(r, h) = \frac{1}{\pi h^3} \begin{cases} 1 - \frac{3}{2}q^2 + \frac{3}{4}q^3, & 0 \leq q < 1 \\ \frac{1}{4}(2-q)^3, & 1 \leq q < 2 \\ 0, & q \geq 2 \end{cases}$$

其中 q = r/h。任意物理量 A 在粒子 i 处的值通过对周围粒子 j 的加权插值得到：

$$A_i = \sum_j m_j \frac{A_j}{\rho_j} W(|\mathbf{r}_i - \mathbf{r}_j|, h)$$

影响半径 h 的选取直接决定模拟质量：h 过小导致粒子孤立、密度计算失准；h 过大则细节模糊。实际项目中常将每个粒子的邻居数量控制在20至50个之间来动态调整 h。

### 密度与压力计算

每个粒子的局部密度由邻域内所有粒子的质量和核函数权重求和得到：

$$\rho_i = \sum_j m_j W(|\mathbf{r}_i - \mathbf{r}_j|, h)$$

得到密度后，通过**状态方程**将密度转换为压力。Tait方程是特效SPH中最常用的弱可压缩状态方程：

$$p_i = B\left[\left(\frac{\rho_i}{\rho_0}\right)^\gamma - 1\right]$$

其中 ρ₀ 是静止参考密度（水通常取1000 kg/m³），γ 通常取7，B 由目标声速决定。这个弱可压缩假设允许密度有约1%的波动，避免了求解泊松方程的高计算成本，但会引入轻微的可压缩性误差。

### 粒子受力与时间积分

粒子 i 受到的压力梯度力和黏性力分别为：

$$\mathbf{F}_i^{pressure} = -m_i \sum_j m_j \left(\frac{p_i}{\rho_i^2} + \frac{p_j}{\rho_j^2}\right) \nabla W_{ij}$$

$$\mathbf{F}_i^{viscosity} = \mu \sum_j m_j \frac{\mathbf{v}_j - \mathbf{v}_i}{\rho_j} \nabla^2 W_{ij}$$

在时间积分上，特效SPH通常使用**蛙跳法（Leapfrog Integration）**，时间步长 Δt 受CFL条件约束，典型值为 0.001 至 0.004 秒，对应音速 c 约为20 m/s的弱可压缩设定。

## 实际应用

**Houdini中的FLIP Solver** 是目前影视特效最广泛使用的拉格朗日粒子法实现，它结合了SPH的粒子追踪优势和欧拉法的压力求解稳定性——粒子携带速度，但压力在网格上求解。《奇异博士》（2016）的镜面城市水面特效、《速度与激情》系列大量水下镜头均使用此类方法。

**实时游戏引擎中的SPH**以降低精度换取速度，每帧粒子数通常控制在5000至50000个，采用空间哈希加速邻域搜索，将邻域查询从 O(N²) 降至接近 O(N)。英伟达PhysX和AMD的TressFX均内置了面向游戏的SPH流体模块。

**颗粒状物质模拟**（沙、雪、谷物）也借助SPH粒子法实现，通过修改状态方程和添加摩擦力模型来模拟非牛顿流体行为。Houdini的Grain Solver本质上是在SPH框架上添加了弹塑性约束。

## 常见误区

**误区一：粒子数量越多效果必然越好。** 在SPH中，当粒子数量 N 增加时，若光滑长度 h 没有相应缩小，粒子间距与 h 的比值会失衡，导致密度过采样和压力震荡。正确做法是保持粒子间距约等于 0.5h，增加粒子数量的同时同步缩小 h，但这会使时间步长 Δt 按 O(h) 缩小，计算量实际上按 O(N^{4/3}) 增长。

**误区二：拉格朗日法不存在数值扩散问题。** 欧拉法在对流项离散时确实有数值扩散，而SPH通过粒子运动天然避免了这一点。但SPH有自己独特的**粒子聚集（Particle Clustering）**问题：张力不稳定性（Tensile Instability）会使粒子在负压区域异常聚拢成团，需要引入人工压力修正项（Monaghan 2000年提出的ε-correction）来抑制。

**误区三：SPH只能模拟液体，不能模拟气体。** SPH对气体同样适用，但由于气体密度变化范围极大（爆炸场景密度比可达1:1000），弱可压缩假设不再成立，需要切换到全可压缩SPH并求解能量方程，计算成本大幅上升，这也是特效中气体爆炸更多用欧拉法的实际原因。

## 知识关联

学习拉格朗日粒子法之前，理解**欧拉法网格流体**至关重要——两者处理同一套Navier-Stokes方程，但离散化策略相反：欧拉法在空间固定位置采样，拉格朗日法随物质点移动采样。FLIP方法正是在两种视角之间传递信息的混合方案，其中粒子到网格（P2G）和网格到粒子（G2P）的插值步骤是连接两种视角的关键操作。

掌握SPH的密度-压力关系之后，自然会遇到完整**Navier-Stokes方程**的简化问题：弱可压缩SPH实际上是将不可压缩假设放宽为"密度偏差不超过1%"的近似，而下一步学习的**Navier-Stokes简化**将系统讲解如何在不同流体条件下（低雷诺数、薄膜流等）对完整方程进行降维处理，为实时特效中的高效流体计算打下数学基础。