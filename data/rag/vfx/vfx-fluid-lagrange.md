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
quality_tier: "A"
quality_score: 76.3
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


# 拉格朗日粒子法

## 概述

拉格朗日粒子法是一类以**跟踪流体质点运动轨迹**为核心的无网格流体仿真方法，与欧拉法固定空间网格观察流场的思路相反——它让每一个离散粒子携带质量、速度、压力等物理量，随流体一同运动，"粒子走到哪里，信息就带到哪里"。该方法得名于法国数学家约瑟夫-路易·拉格朗日（Joseph-Louis Lagrange，1736–1813），他在分析力学中首先提出以物质点本身为参考系来描述运动的框架。在视觉特效领域，最主流的拉格朗日粒子实现是**光滑粒子流体动力学（Smoothed Particle Hydrodynamics，SPH）**，由 Lucy、Gingold 和 Monaghan 于 1977 年独立提出，最初用于天体物理模拟，后被广泛移植到影视级流体特效。

拉格朗日粒子法的最大优势在于**天然处理大变形自由液面**：水花四溅、液滴分裂、波涛翻滚等拓扑变化复杂的场景，不需要额外追踪界面标记，粒子群的空间分布本身就代表了液面形状。相比欧拉法需要额外的 Level Set 或 VOF 方法追踪界面，拉格朗日粒子法在特效制作中能以更直观的方式控制液体轮廓，是《加勒比海盗》《奇异博士》等影片水体特效的底层技术之一。

---

## 核心原理

### 1. SPH 核函数插值

SPH 的数学基础是用**核函数（Kernel Function）W** 对连续场进行离散近似。对于粒子 $i$ 处的任意物理量 $A$，其估计值为：

$$A(\mathbf{r}_i) = \sum_j m_j \frac{A_j}{\rho_j} W(\mathbf{r}_i - \mathbf{r}_j,\, h)$$

其中：
- $m_j$ 为邻域粒子 $j$ 的质量
- $\rho_j$ 为粒子 $j$ 的密度
- $W$ 为核函数，$h$ 为**光滑长度（smoothing length）**，决定每个粒子的影响半径

常用核函数是 **Müller（2003）提出的三次样条核**，其支撑域半径通常设为 $2h$，意味着每个粒子只与距离不超过 $2h$ 的邻域粒子发生相互作用，典型 $h$ 值为粒子间距的 1.2–2 倍。核函数必须满足归一化条件 $\int W\,d\mathbf{r} = 1$ 以及在 $h$ 之外严格为零的紧支撑性。

### 2. 密度与压力计算

每帧更新中，粒子密度由邻域粒子叠加核函数值得出：

$$\rho_i = \sum_j m_j W(|\mathbf{r}_i - \mathbf{r}_j|,\, h)$$

压力则通过**理想气体状态方程**或**Tait 方程**由密度推算：

$$P_i = k \left[\left(\frac{\rho_i}{\rho_0}\right)^\gamma - 1\right]$$

其中 $\rho_0$ 为静止参考密度，$\gamma = 7$ 是 Tait 方程常用指数，$k$ 为与音速相关的刚度系数。$\gamma$ 越大，可压缩性越低，模拟的"不可压缩感"越强，但同时要求更小的时间步长以维持数值稳定性。

### 3. 运动方程离散化

流体粒子的加速度由压力梯度力、粘性力和外力（重力）叠加而成：

$$\frac{d\mathbf{v}_i}{dt} = -\sum_j m_j \left(\frac{P_i}{\rho_i^2} + \frac{P_j}{\rho_j^2}\right) \nabla W_{ij} + \nu \sum_j m_j \frac{\mathbf{v}_{ij} \cdot \mathbf{r}_{ij}}{|\mathbf{r}_{ij}|^2 + \epsilon^2} \nabla W_{ij} + \mathbf{g}$$

粒子位置随后通过**Leapfrog 或 Verlet 积分**更新，时间步长受 CFL 条件限制，典型值为 $\Delta t \leq 0.4\,h/c_s$，其中 $c_s$ 为声速。每帧模拟通常需要执行数十到数百个子步骤。

### 4. 邻域粒子搜索

由于每一步都需要找出每个粒子的邻域粒子，SPH 最常用**均匀网格哈希（Spatial Hashing）**将三维空间划分为边长 $2h$ 的格子，将粒子桶排序到对应格子，查询时仅检查 $3\times3\times3 = 27$ 个相邻格子。对于百万量级粒子，这一结构可将复杂度从 $O(N^2)$ 降至接近 $O(N)$。

---

## 实际应用

**影视特效水体模拟**：Houdini 的 FLIP（Fluid-Implicit Particle）求解器将 SPH 的粒子对流与欧拉网格的压力投影结合，粒子负责携带速度并防止数值耗散，网格负责精确求解压力泊松方程。《复仇者联盟》中斯特兰奇打开传送门时的水环特效即使用了基于 FLIP 的拉格朗日-欧拉混合方案。

**游戏实时流体**：NVIDIA PhysX 的 GPU 加速 SPH 模块允许在实时游戏中模拟约 10 万–100 万粒子，通过将邻域搜索和力计算全部映射到 CUDA 线程，单帧计算控制在 1–5 毫秒。粒子渲染通常采用**屏幕空间流体渲染（Screen-Space Fluid Rendering）**将粒子点云合成连续液面。

**特效中的表面张力效果**：SPH 可通过 **Akinci（2013）的表面张力模型**在粒子层面添加内聚力项，产生液滴成球、液膜拉伸等微观现象，这在纯欧拉网格方案中需要复杂的曲率估计才能实现。

---

## 常见误区

**误区一：粒子数量越多，结果一定越准确。**  
SPH 的精度不仅取决于粒子数量，更取决于**粒子分布的均匀性**。在拉伸严重的区域，粒子间距增大导致核函数积分误差急剧上升，出现密度下降虚假膨胀（particle deficiency problem）。仅靠增加粒子数而不维护粒子均匀性，在自由液面薄层区域反而会产生非物理振荡压力。解决方案包括引入粒子分裂/合并（particle splitting/merging）机制，或使用 Shifting 技术定期修正粒子分布。

**误区二：拉格朗日粒子法天然守恒，不存在质量损失。**  
标准 SPH 中每个粒子质量确实固定，总质量守恒；但**体积守恒和不可压缩性**并不自动保证。弱可压缩 SPH（WCSPH）允许最多约 1% 的密度波动以换取计算效率，密度波动会在长时间模拟中积累为可见的体积收缩或膨胀误差。真正的不可压缩 SPH（ISPH）需要每步求解压力泊松方程，计算代价是 WCSPH 的 3–5 倍。

**误区三：SPH 比欧拉网格法在所有流体场景下都更自然。**  
拉格朗日粒子法在大量气体填充空间的场景（如烟雾、爆炸冲击波）效率极低：气体粒子会扩散至巨大体积，邻域粒子密度极低，导致插值精度崩溃。这类场景反而是欧拉网格法更擅长的领域。SPH 的优势域是**高密度、大变形液体**，而非所有流体类型。

---

## 知识关联

学习拉格朗日粒子法需要掌握**欧拉法网格流体**中建立的流体运动方程体系：连续性方程 $\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \mathbf{v}) = 0$ 和动量方程在 SPH 框架下转化为粒子间相互作用力的形式，两套描述体系描述的是同一套物理，只是参考系不同。

在掌握 SPH 的粒子离散化思路之后，后续学习**Navier-Stokes 简化**时会更容易理解：SPH 公式中的粘性项正是完整 Navier-Stokes 粘性扩散项 $\mu \nabla^2 \mathbf{v}$ 经 SPH 核函数离散后的近似形式，通过对比两者推导过程，可以直观看出哪些物理项在特效制作常见的简化方案中被忽略（如忽略可压缩效应、湍流封闭模型等），以及这些简化对液体视觉表现的具体影响。