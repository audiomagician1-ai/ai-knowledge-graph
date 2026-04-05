---
id: "vfx-particle-turbulence"
concept: "湍流与噪声"
domain: "vfx"
subdomain: "particle-physics"
subdomain_name: "粒子物理"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 湍流与噪声

## 概述

湍流（Turbulence）是流体运动中一种不规则、随机且高度混沌的状态，与层流（Laminar Flow）形成对比——层流中流体平行分层运动，而湍流中流体微团以旋涡和涡流的形式剧烈混合。在粒子特效系统中，湍流通常通过**噪声场（Noise Field）**来模拟，即利用数学噪声函数为三维空间中每一点生成一个方向向量，粒子进入该向量场后会受到与位置相关的偏转力，从而产生烟雾翻滚、火焰摇曳、沙尘漂浮等自然感强烈的视觉效果。

噪声驱动的湍流在特效领域的广泛使用始于1985年前后，Ken Perlin在为电影《创：战纪》（TRON的续作项目）开发程序纹理时发明了**Perlin Noise**，并因此获得了1997年奥斯卡科学技术奖。此后，**Curl Noise**由Robert Bridson于2007年在SIGGRAPH论文《Curl-noise for Procedural Fluid Simulation》中提出，专门用于驱动无散度（Divergence-free）的湍流速度场，使粒子运动在视觉上更贴近真实流体。这两种噪声函数至今仍是游戏引擎（Unreal Engine、Unity VFX Graph）和电影特效中粒子湍流的主流实现方式。

## 核心原理

### Perlin Noise的生成与梯度插值

Perlin Noise通过在规则网格的每个顶点上随机分配一个**梯度向量（Gradient Vector）**，然后对查询点与周围网格顶点的点积结果进行平滑插值来生成连续的噪声值。其插值采用六次多项式缓动函数 $f(t) = 6t^5 - 15t^4 + 10t^3$（由Perlin本人在2002年改进版Improved Perlin Noise中提出，替代了早期的三次插值 $3t^2 - 2t^3$），确保一阶和二阶导数在格点处均为零，消除了早期版本中肉眼可见的方块感伪影。

在三维空间中，Perlin Noise返回一个标量值 $n(\mathbf{x})$，其值域约为 $[-0.87, 0.87]$。要用Perlin Noise生成湍流速度场，通常需要对三个相互正交偏移的噪声采样点分别求值：$\mathbf{v} = (n(\mathbf{x}+\mathbf{o}_1),\ n(\mathbf{x}+\mathbf{o}_2),\ n(\mathbf{x}+\mathbf{o}_3))$，其中偏移量 $\mathbf{o}_i$ 需足够大（通常取整数值如$(0,0,0)$、$(31.416,37.0,17.0)$等）以确保三个分量之间的去相关性。

### Curl Noise与无散度约束

Curl Noise的核心思想是对一个**势场（Potential Field）** $\mathbf{\Psi}(\mathbf{x})$ 取旋度（Curl），即 $\mathbf{v} = \nabla \times \mathbf{\Psi}$。旋度运算在数学上保证了结果速度场满足 $\nabla \cdot \mathbf{v} = 0$（无散度条件），意味着粒子群既不会人为地聚集（汇聚）也不会无缘无故地扩散（发散），整体密度保持守恒，这与真实不可压缩流体（如空气、水）的物理特性一致。

在三维中，势场 $\mathbf{\Psi}$ 通常由三个独立的Perlin Noise函数组成：
$$\mathbf{v} = \nabla \times \mathbf{\Psi} = \left(\frac{\partial \Psi_z}{\partial y} - \frac{\partial \Psi_y}{\partial z},\ \frac{\partial \Psi_x}{\partial z} - \frac{\partial \Psi_z}{\partial x},\ \frac{\partial \Psi_y}{\partial x} - \frac{\partial \Psi_x}{\partial y}\right)$$
偏导数在实时计算中通常用有限差分近似，步长 $\varepsilon$ 典型取值为 $0.0001$ 到 $0.01$。步长过大会损失细节，过小则数值误差增加。

### 分形叠加（Fractal Brownian Motion）

单层噪声生成的湍流只包含一个频率的涡旋结构，视觉上显得单调。真实湍流遵循**Kolmogorov −5/3能量谱定律**，即大涡旋携带主要能量，而能量逐级传递到更小尺度的涡旋。在特效中通过叠加多倍频率（Octaves）的噪声来模拟这一特性，称为**fBm（Fractional Brownian Motion）**：
$$\text{fBm}(\mathbf{x}) = \sum_{i=0}^{N-1} \text{amplitude}^i \cdot n(\text{frequency}^i \cdot \mathbf{x})$$
典型参数为频率倍增系数（Lacunarity）= 2.0，振幅衰减系数（Gain/Persistence）= 0.5，叠加4到8层。叠加8层时，最高频层的细节尺度约为最低频层的 $2^7 = 128$ 倍，能够产生从大尺度卷云到小尺度丝缕烟雾的完整细节层次。

## 实际应用

**烟雾与火焰特效**：在Houdini的Pyro系统中，湍流噪声直接注入速度场，通过调整噪声的`scale`（控制涡旋大小）和`strength`（控制湍流强度，单位为m/s）来决定烟雾是缓慢飘散还是剧烈翻滚。典型的营火烟雾湍流强度约为0.5–2 m/s，而爆炸烟雾可达10–30 m/s。

**GPU粒子系统**：Unreal Engine的Niagara系统内置`Curl Noise Force`模块，将Curl Noise速度场作为外力叠加到粒子速度上，每帧计算量仅需对势场做6次有限差分采样，适合百万级粒子的实时计算。Unity VFX Graph中同样提供`Turbulence`节点，底层即为Curl Noise实现。

**角色特效中的魔法粒子**：魔法光球、灵魂粒子等特效常要求粒子围绕某一中心盘旋而不向外扩散，此时Curl Noise的无散度特性比普通Perlin Noise更合适，能自然形成旋涡状轨迹而无需手动添加引导力。

**环境风场扰动**：在开放世界游戏中，树叶、雪花、花粉粒子需要响应局部风场的随机扰动。通过将噪声场的查询位置随时间偏移（$\mathbf{x}_{\text{query}} = \mathbf{x}_{\text{particle}} + t \cdot \mathbf{wind\_dir}$），可以模拟风带动噪声场整体移动的效果，称为**对流噪声（Advected Noise）**。

## 常见误区

**误区一：Perlin Noise和Curl Noise可以互换使用**。Perlin Noise作为湍流力时，速度场有散度，粒子群会在噪声低频中心聚集或在边缘发散，产生不自然的密度分布。Curl Noise专门用于流体模拟的速度场驱动，而Perlin Noise更适合用于纹理扰动、密度分布控制等不要求守恒的场景。混用会导致视觉上粒子莫名出现密度高峰或低谷。

**误区二：频率（Frequency）越高湍流越"强烈"**。提高噪声频率只会增加涡旋的数量和减小单个涡旋的尺寸，使运动看起来更"碎"或"颤抖"，并不等同于速度幅度的增大。真正控制湍流强度（速度大小）的参数是**振幅（Amplitude/Strength）**。初学者常将频率调到极高，结果粒子呈现高频抖动而非流畅的湍流漩涡。

**误区三：湍流噪声不需要考虑时间维度**。将噪声查询限制在三维空间坐标而不加入时间偏移，噪声场将完全静止，粒子虽然路径弯曲但每条路径固定不变，效果僵硬。正确做法是将查询坐标扩展为四维 $(\mathbf{x}, t \cdot \text{time\_scale})$ 或采用对流偏移，使噪声场随时间演化，模拟湍流的时变特性。

## 知识关联

理解本概念需要先掌握**重力模拟**（粒子的基础速度积分框架 $\mathbf{v}_{t+1} = \mathbf{v}_t + \mathbf{F}/m \cdot \Delta t$）和**力与运动**（外力叠加原理），湍流噪声本质上是一种空间变化的外力场，其积分方式与重力完全相同，区别仅在于该力的方向和大小随粒子位置动态变化。

后续学习**阻力模型**时，会发现阻力（Drag）与湍流在物理上是相互制衡的关系：湍流力持续向粒子注入随机速度，而阻力（$\mathbf{F}_{\text{drag}} = -b\mathbf{v}$）则消耗速度。