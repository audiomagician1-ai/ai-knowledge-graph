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
quality_tier: "B"
quality_score: 49.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.452
last_scored: "2026-03-22"
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

湍流与噪声是粒子特效系统中用于模拟不规则、自然流动状态的核心技术，通过数学噪声函数驱动粒子产生看似随机却具有空间连续性的运动轨迹。与简单的随机数不同，Perlin Noise（由Ken Perlin于1983年为电影《Tron》开发，并于1985年发表）和Curl Noise所生成的值在空间上是平滑连续的，相邻采样点之间不会发生突变，从而模拟出烟雾、火焰、水流等自然现象中常见的漩涡状扰动。

这类技术之所以在特效制作中不可替代，是因为真实世界中的湍流（Turbulence）并非纯粹随机，而是具有"多尺度叠加"的统计特征——大型漩涡中嵌套小型漩涡，能量从大尺度向小尺度级联传递，这一规律由Kolmogorov于1941年在湍流理论中首次量化描述。噪声驱动的粒子系统通过叠加多层不同频率的噪声（称为Octave叠加）来模拟这种层次结构。

## 核心原理

### Perlin Noise 的数学基础

Perlin Noise的核心思想是在整数网格点上分配随机梯度向量，然后对查询点到周围网格点的距离向量与梯度向量做点积，再通过平滑插值函数 `f(t) = 6t⁵ - 15t⁴ + 10t³`（即Quintic插值，由Perlin在2002年的改进版本Simplex Noise中引入）混合结果。输出值范围约为 [-1, 1]，可直接映射为粒子在X、Y、Z轴上的速度偏移量。在2D噪声场中，每个空间坐标 (x, y) 对应一个确定的噪声值 N(x, y)，粒子运动时持续采样其当前位置的噪声值，驱动速度发生渐变式偏转。

### Curl Noise 与无散场

Curl Noise由Robert Bridson等人于2007年的SIGGRAPH论文中提出，专门解决Perlin Noise直接驱动粒子时会导致粒子堆积（即流场有散度，违反质量守恒）的问题。其计算公式为：

**v = ∇ × Ψ**

其中 Ψ 是一个噪声势场（通常用Perlin Noise生成），∇ × 表示旋度算子（Curl）。在3D空间中，旋度展开为：

```
vx = ∂Ψz/∂y - ∂Ψy/∂z
vy = ∂Ψx/∂z - ∂Ψz/∂x
vz = ∂Ψy/∂x - ∂Ψx/∂y
```

对旋度向量场取散度恒为零（∇·v = 0），这意味着粒子在流场中不会无故聚集或消散，非常适合模拟烟雾和液体的保体积流动。Houdini的`curlnoise()`函数直接实现了上述公式，参数`roughness`控制高频细节的权重。

### 频率、振幅与Octave叠加

单层噪声只能模拟单一尺度的扰动，实际特效中通常叠加多个Octave（倍频层）。每叠加一层，频率乘以一个称为Lacunarity的系数（通常取2.0），振幅乘以一个称为Persistence（或Gain）的系数（通常取0.5）。最终位移值为：

**D = Σ(i=0 to n-1) amplitude_i × N(pos × frequency_i)**

4到6个Octave即可产生视觉上足够丰富的细节，超过8个Octave在视觉上几乎无法分辨差异，但计算成本会线性增加。时间维度的湍流动画通过在噪声采样时加入时间偏移 N(x, y, z, t×speed) 实现，time offset参数控制湍流演化速度。

## 实际应用

**烟雾与火焰特效**：在Houdini的Pyro系统中，湍流噪声被注入速度场（vel field），使烟雾产生卷曲上升的形态。典型参数设置为：Turbulence Scale（噪声缩放）0.5~2.0，Amplitude 0.3~1.5，4个Octave。过高的Amplitude会让烟雾产生不自然的"爆炸感"，需配合后续的阻力（Drag）参数平衡。

**星云与宇宙粒子**：影视中的星云特效常使用3层Curl Noise叠加，第一层控制整体流向（低频，Scale=10），第二层添加中等漩涡（Scale=3），第三层增加表面细节（Scale=0.8）。《银河护卫队》系列中的星云场景即采用类似多尺度噪声叠加策略。

**布料与毛发飘动**：毛发粒子在风场中的扰动可以用2D Perlin Noise切片驱动，噪声的时间偏移速度模拟风速，通常设置为0.1~0.5单位/帧，可产生自然的阵风感而不显得机械。

## 常见误区

**误区一：Perlin Noise和随机数（Random）可以互相替代**。直接使用`rand(id)`为每个粒子分配随机速度，粒子之间完全无空间关联，产生的是"盐粒撒落"式的离散运动，而非烟雾的连续扰动。Perlin Noise保证了空间上相邻粒子受到方向相近的力，这是模拟流体行为的必要条件。

**误区二：Curl Noise比Perlin Noise"更真实"，应该总是使用Curl Noise**。Curl Noise的无散特性适合模拟保体积流体，但对于需要粒子聚拢效果的场景（如龙卷风的汇聚点、黑洞吸积盘），带有散度的噪声场反而更合适。选择依据是目标流体的物理特性，而非追求"更高级"的算法。

**误区三：叠加更多Octave总能得到更好的效果**。当最高频率Octave的噪声波长小于粒子采样步长时，粒子无法感知该层细节，增加的计算量完全浪费。实践中应根据粒子密度和噪声Scale确定有效的最大Octave数，公式参考为：最大有效频率 ≈ 1 / (粒子平均间距 × 2)。

## 知识关联

湍流与噪声的应用建立在**重力模拟**和**力与运动**的基础之上：粒子已具备速度和加速度的基本运动框架，噪声函数生成的扰动向量被添加为额外的力或速度偏移，与重力、初速度共同决定粒子轨迹。理解牛顿第二定律 F = ma 在粒子系统中的离散化形式（`vel += force × dt`）是正确注入噪声力的前提。

学习湍流噪声后，下一个关键概念是**阻力模型**：无约束的湍流会使粒子速度无限累积，阻力（Drag）通过 `F_drag = -k × v`（线性阻力）或 `-k × |v| × v`（二次阻力）限制粒子最大速度，使湍流运动收敛至视觉上稳定的平衡状态，这是烟雾、火焰粒子不会飞散消失的关键机制。两者的配合参数调整是流体粒子特效调试的核心工作流程。