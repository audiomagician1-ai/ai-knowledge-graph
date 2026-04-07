---
id: "vfx-fluid-sph"
concept: "SPH方法"
domain: "vfx"
subdomain: "fluid-sim"
subdomain_name: "流体模拟"
difficulty: 4
is_milestone: false
tags: ["高级"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---



# SPH方法（光滑粒子流体动力学）

## 概述

光滑粒子流体动力学（Smoothed Particle Hydrodynamics，SPH）是一种无网格拉格朗日粒子方法，由Lucy、Gingold和Monaghan于1977年独立提出，最初用于天体物理学中模拟恒星碰撞。在实时特效领域，SPH将流体离散为一组携带质量、速度、密度等物理量的粒子，每个粒子通过与邻域粒子的加权求和来估算连续场的物理量，从而完全规避了传统网格方法中的网格生成与对流扩散问题。

SPH方法的核心数学思想是核函数插值：任意物理量 $A(\mathbf{r})$ 在位置 $\mathbf{r}$ 处的值，由周围粒子的贡献通过核函数 $W$ 加权累加得到。这使得自由表面追踪、大变形流体运动（如水花飞溅、海浪破碎）天然适合用SPH处理，因为粒子本身就代表流体界面，无需额外的界面重构算法。在游戏和影视特效中，SPH因其直观的粒子表达和相对易于GPU并行化的特性，成为实时水体、血液、岩浆等特效的主流选择。

## 核心原理

### 核函数与粒子插值

SPH的基础插值公式为：

$$A(\mathbf{r}) = \sum_j m_j \frac{A_j}{\rho_j} W(\mathbf{r} - \mathbf{r}_j, h)$$

其中 $m_j$ 是粒子 $j$ 的质量，$\rho_j$ 是其密度，$h$ 是光滑长度（smoothing length），决定了每个粒子的影响半径。实时特效中常用的核函数是Müller等人于2003年在SIGGRAPH论文《Particle-Based Fluid Simulation for Interactive Applications》中提出的三种专用核：压力项用 $W_\text{poly6}$，黏性项用 $W_\text{viscosity}$，表面张力项用 $W_\text{spiky}$（Spiky核）。Spiky核的设计特意避免了梯度在粒子中心趋近零的问题，从而防止粒子团聚。

### 密度、压力与Navier-Stokes离散

粒子密度通过邻域粒子求和直接估算：$\rho_i = \sum_j m_j W_{ij}$。压力由状态方程计算，实时SPH通常采用弱可压缩近似（WCSPH）：

$$p_i = k\left[\left(\frac{\rho_i}{\rho_0}\right)^\gamma - 1\right]$$

其中 $\rho_0$ 为参考密度（水约为1000 kg/m³），$k$ 为刚度系数，$\gamma=7$ 是经典选择。Navier-Stokes方程的压力梯度项和黏性项分别被离散为粒子间的力求和。Müller方法中黏性加速度为：

$$\mathbf{a}_i^\text{visc} = \nu \sum_j \frac{m_j}{\rho_j}(\mathbf{v}_j - \mathbf{v}_i)\nabla^2 W_\text{viscosity}(r_{ij}, h)$$

### 邻域搜索与实时优化

SPH最大的运行时开销在于邻域搜索——每帧每个粒子必须找到光滑半径 $h$ 范围内的所有邻居。实时实现中标准做法是均匀空间哈希网格（Spatial Hashing），将空间划分为边长等于 $2h$ 的体素，每个粒子仅检索相邻27个体素。现代GPU实现（如基于CUDA的实时SPH）通常以 $10^4$～$10^5$ 个粒子维持60fps，而离线高质量特效可达 $10^6$ 粒子以上。时间积分多采用显式蛙跳法（Leapfrog），步长受CFL条件约束，典型值为 $\Delta t \approx 0.4h / v_\text{max}$。

### 表面重建

SPH粒子模拟完成后，需将离散粒子重建为可渲染的表面网格。主流方法是Marching Cubes结合粒子密度场，或使用Zhu和Bridson（2005）提出的各向异性核函数，后者能更好地还原薄水膜和水丝细节。

## 实际应用

**游戏实时水体**：《荒野大镖客2》和《战神》等AAA游戏中的局部水花特效采用简化SPH，粒子数控制在2000～8000个，通过预计算粒子模板和LOD降级保持帧率。

**影视流体特效**：DreamWorks的Houdini管线中SPH常用于模拟细碎水珠、泡沫层（foam layer），与FLIP方法的大体量流体结合使用——FLIP负责主体水体，SPH负责飞溅粒子。

**医学与游戏血液模拟**：《战争机器》系列的血液特效利用SPH的非牛顿流体扩展（通过修改黏性系数 $\nu$ 随剪切率变化），模拟血液粘稠附着表面的行为，每次命中触发约500个SPH粒子的局部模拟。

**位置约束SPH（PBD-SPH混合）**：Unity和Unreal引擎的Niagara系统中，部分实现将SPH密度约束嵌入基于位置的动力学（PBD）框架，用密度不等式约束代替压力力计算，进一步提升稳定性。

## 常见误区

**误区一：光滑长度 $h$ 越小精度越高**。SPH的精度依赖于每个粒子拥有足够数量的邻居（三维中通常需要30～60个）。若减小 $h$ 而不同步增加粒子数量，邻居数骤降会导致密度估算噪声急剧增大，出现数值碎片化，反而使模拟崩溃。

**误区二：WCSPH中刚度系数 $k$ 可以任意调大以逼近真实不可压缩性**。增大 $k$ 会使密度波动减小（提高不可压缩性），但同时声速 $c_s = \sqrt{\gamma k / \rho_0}$ 随之升高，CFL条件要求时间步长 $\Delta t$ 等比例缩小，导致实时应用的计算成本线性增长。实时特效中通常允许1%～5%的密度偏差以换取可接受的步长。

**误区三：SPH天然守恒动量**。标准SPH中若不使用对称化压力梯度（即将 $\nabla p_i / \rho_i$ 替换为 $\sum_j m_j (p_i/\rho_i^2 + p_j/\rho_j^2)\nabla W_{ij}$），则粒子对间的作用力不满足牛顿第三定律，导致线动量漂移，长时间模拟中流体会无故加速或位移。

## 知识关联

SPH方法直接建立在Navier-Stokes方程简化的基础上：弱可压缩SPH通过状态方程绕过了泊松方程的求解，而完全不可压缩SPH（ISPH）则需要求解压力泊松方程，计算代价更高但密度守恒更好。在后续的FLIP/APIC方法中，粒子仅作为质量和动量的载体，物理量的求解转移到背景网格上完成，从而同时获得SPH的自由表面追踪优势和网格方法的数值耗散优势——这正是FLIP比纯SPH在大规模流体模拟中更普遍的根本原因。APIC（Affine Particle-In-Cell）进一步在粒子上存储仿射速度矩阵，解决了FLIP的角动量不守恒问题，而这两点正是纯SPH方法长期面临的挑战。