---
id: "cg-ray-marching"
concept: "Ray Marching"
domain: "computer-graphics"
subdomain: "volume-rendering"
subdomain_name: "体积渲染"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
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

# 光线步进（Ray Marching）

## 概述

光线步进（Ray Marching）是一种通过沿光线方向逐步采样来渲染体积介质的算法。与传统光线追踪直接求解光线与几何表面的解析交点不同，光线步进将光线分割为若干固定或自适应的步长段，在每个采样点处查询体积密度、颜色等属性，然后将所有采样结果累积合成最终像素颜色。这一思路最早由Jim Kajiya与Brian Von Herzen在1984年的SIGGRAPH论文《Ray Tracing Volume Densities》中系统性地提出，奠定了体积渲染的算法基础。

光线步进之所以在体积渲染中不可或缺，是因为云、烟、雾、火焰等自然现象本质上是连续分布的参与介质（participating media），没有明确的几何表面可供解析求交。通过将连续积分离散化为有限数量的步进采样，光线步进将这一物理上无限复杂的问题转化为计算机可处理的数值积分问题。现代GPU着色器（如GLSL/HLSL中的fragment shader）可以在每个像素并行执行光线步进循环，使其成为实时体积效果的主流实现手段。

## 核心原理

### 基本算法流程

光线步进的执行逻辑可以用以下伪代码描述：从相机出发，沿观察方向发射光线；确定光线进入和离开体积包围盒的距离 `t_near` 和 `t_far`；然后以步长 `Δt` 循环前进，每步在位置 `P = origin + t × direction` 处采样密度值 `σ(P)`，直到 `t > t_far` 或累积不透明度超过阈值（通常为0.99）提前终止。

整个过程本质上是对体积渲染方程的数值积分。体积透射率（transmittance）由Beer-Lambert定律给出：

$$T(t) = \exp\left(-\int_0^t \sigma(s)\, ds\right)$$

在离散化后，每个步进点对最终颜色的贡献为：

$$C = \sum_{i=1}^{N} T_i \cdot \sigma(P_i) \cdot c(P_i) \cdot \Delta t$$

其中 $T_i$ 是从相机到第 $i$ 个采样点的累积透射率，$\sigma(P_i)$ 是该点的消光系数，$c(P_i)$ 是该点的颜色/辐射值，$\Delta t$ 是步长。

### 固定步长与自适应步长

最简单的光线步进使用均匀固定步长。若体积范围为100单位、步长设为0.5，则每条光线最多执行200次迭代。固定步长实现简单，但存在采样效率低下的问题：在密度为零的空旷区域同样会浪费大量采样次数。

自适应步长（adaptive step size）根据当前位置的密度动态调整 $\Delta t$：密度高的区域缩短步长以捕捉细节，密度为零的区域加大步长快速跳过。一种常见策略是令 $\Delta t_{\text{next}} = \Delta t_{\text{base}} / (1 + k \cdot \sigma(P))$，其中 $k$ 是控制自适应程度的调节系数。空间跳过技术（empty space skipping）通过预计算稀疏体素八叉树（sparse voxel octree）或距离场，使光线能在空旷区域以极大步长飞跃，将平均迭代次数降低60%～80%。

### 终止条件与精度权衡

光线步进有两种终止条件：一是走完整个体积（`t >= t_far`），二是累积透明度 `alpha` 超过早期终止阈值（early termination threshold，通常为0.99或0.999）。早期终止对于不透明度密集的介质（如稠密云内部）尤为重要，可大幅减少不必要的深层采样。

步长 $\Delta t$ 的选取直接影响渲染质量与性能的平衡：步长过大会导致体积边界出现明显的环状分层伪影（banding artifacts），步长过小则使帧率骤降。在实时应用中，常见的折中方案是使用8～64步的低采样数结合蓝噪声抖动（blue noise dithering）来打破规律性伪影，再通过时间抗锯齿（TAA）在帧间累积多帧结果以恢复质量。

## 实际应用

**Shadertoy体积云示例**：在GPU着色器中，体积云的光线步进通常仅用32～128步即可产生令人信服的视觉效果。每步通过分形布朗运动（FBM）噪声函数查询云层密度，并沿太阳光方向额外执行6～8步的次级光线步进（shadow ray marching）计算自阴影，从而模拟云朵厚重的阴暗底部。

**游戏中的体积雾**：虚幻引擎4/5的指数高度雾（Exponential Height Fog）在屏幕空间使用64步光线步进生成体积雾散射查找表（Froxel Volume），分辨率典型值为160×90×64的三维纹理，覆盖相机前方约64米的雾效区域，再在光照计算阶段查表合成，将体积雾的每帧开销控制在1毫秒以内。

**SDF（符号距离场）渲染**：光线步进还被广泛用于渲染数学隐式曲面，此时步长由当前点到最近几何体的SDF值直接给出（即"球形步进"Sphere Marching）。Inigo Quilez在其系列教程中展示了如何用不超过100行GLSL代码，通过SDF光线步进渲染出复杂的分形和程序几何体。

## 常见误区

**误区一：步数越多效果越好，应尽量提高步数。**
这一想法忽略了边际收益递减规律。在实践中，将步数从16提升至32对质量的改善远大于从64提升至128。当采样点间距小于体积密度的空间变化频率时，继续增加步数几乎不带来视觉收益，却线性增加GPU开销。正确做法是结合抖动和TAA，在低步数下获得高质量结果。

**误区二：光线步进只能渲染"模糊"的体积效果，无法渲染清晰边界。**
清晰的体积边界可通过以下方式实现：在靠近密度突变区域时自动细化步长；或在步进过程中用二分法精细定位密度阈值交叉点，精度可达原始步长的1/256。Valve在《Portal》系列中使用光线步进渲染带有清晰轮廓的传送门特效，证明了光线步进并不天然等同于模糊效果。

**误区三：光线步进与光线投射（Ray Casting）是同一种算法。**
光线投射（Ray Casting）通常指寻找光线与体素数据第一个不透明边界的早期算法，以1987年的《A Front-to-Back Compositing Scheme for Ray Casting of Volume Data》中的方法为代表，其不累积透射率，无法正确模拟散射与透射混合效果。光线步进则对光线穿越介质的全程进行积分，能够正确处理半透明介质的多层叠加，是概念上更为完整的体积积分方法。

## 知识关联

光线步进以体积渲染概述中建立的参与介质物理模型为前提，直接依赖消光系数 $\sigma$ 和辐射传输方程（RTE）的概念框架。在掌握光线步进的基本循环结构后，Beer-Lambert定律将为其中透射率的指数衰减公式提供严格的物理推导，而非仅作经验性使用。体积云实现和体积雾分别是光线步进在高频噪声密度场和低频解析密度场上的具体应用，两者在步数选取和噪声采样策略上存在本质差异。体积光（Volumetric Lighting，即God Rays）在光线步进框架下引入光线可见性查询，而火焰与爆炸渲染则需要在步进循环中额外处理自发光（emission）项，是光线步进渲染方程的功能扩展。