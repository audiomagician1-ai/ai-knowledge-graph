---
id: "vfx-vfxgraph-noise"
concept: "噪声函数"
domain: "vfx"
subdomain: "vfx-graph"
subdomain_name: "VFX Graph"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.5
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# 噪声函数

## 概述

噪声函数是一类能够生成连续、伪随机数值的数学算法，其输出在空间或时间上保持平滑过渡，而非离散跳变。在VFX Graph中，噪声函数被封装为独立节点，直接输出标量或向量值，用于驱动粒子的位置偏移、速度扰动、颜色变化等属性，是实现烟雾、火焰、云层等有机形态特效的基础工具。

噪声函数的历史可追溯至1983年，Ken Perlin为电影《创：战纪》（Tron）的视觉特效开发了Perlin噪声算法，并于1985年在SIGGRAPH发表。该算法因其视觉自然性获得奥斯卡技术成就奖。2001年，Perlin进一步提出Simplex噪声，将计算复杂度从O(2^N)降低至O(N^2)，大幅提升了高维度下的性能表现。Curl噪声则由Robert Bridson于2007年引入，专门用于模拟无散度流体运动。

在VFX Graph中，噪声函数节点属于**数值生成类**节点，可在GPU上实时计算。与纹理采样相比，噪声函数无需预先存储贴图资源，完全由数学公式在着色器中程序化生成，节省显存并支持任意精度的无缝平铺。

---

## 核心原理

### Perlin噪声的梯度插值机制

Perlin噪声的核心操作分三步：首先将输入坐标映射到整数网格，在每个网格顶点处分配一个伪随机梯度向量；然后计算输入点到各顶点的距离向量与梯度向量的点积；最后使用**缓动函数** `f(t) = 6t⁵ - 15t⁴ + 10t³`（即Perlin改进版，2002年替换了原始的三次曲线）进行平滑插值。这条五次多项式保证了一阶和二阶导数在网格边界处均为零，消除了明显的网格痕迹。

VFX Graph中的Perlin噪声节点提供**Frequency**（频率）参数，控制噪声图案的空间密度；**Octaves**（倍频）参数叠加多层不同频率的噪声，每层的振幅乘以**Roughness**（粗糙度，默认0.5）衰减，最终合成分形噪声（fBm，Fractal Brownian Motion）。

### Simplex噪声的单纯形网格

Simplex噪声将空间划分为单纯形（2D中为三角形，3D中为四面体），而非Perlin的超立方体网格。在N维空间中，每次计算只需检查N+1个顶点，而Perlin需要检查2^N个。VFX Graph中Simplex噪声在3D情形下的计算节点数约为Perlin的60%，在粒子数量超过百万时性能差异尤为显著。Simplex噪声的另一优点是各向同性更强，不会出现Perlin在45°方向上常见的条带状伪影。

### Curl噪声的无散度特性

Curl噪声基于向量场的旋度运算：给定一个3D噪声势场 **Ψ(x,y,z)**，Curl噪声的速度场定义为 **v = ∇ × Ψ**，展开为：

```
vx = ∂Ψz/∂y - ∂Ψy/∂z
vy = ∂Ψx/∂z - ∂Ψz/∂x
vz = ∂Ψy/∂x - ∂Ψx/∂y
```

由于旋度的散度恒为零（∇·(∇×Ψ) = 0），Curl噪声生成的速度场保证不产生汇聚或发散，粒子密度在运动过程中保持守恒。在VFX Graph中，Curl噪声节点直接输出三维向量，与**Velocity from Curl Noise**模块连接后，粒子会产生类似烟雾涡旋的流体旋转运动，而不会出现粒子聚集成团的现象。

---

## 实际应用

**烟雾扰动**：在VFX Graph中使用**Add Velocity from Curl Noise**节点，将Frequency设为0.3~0.8，Intensity设为2~5，可驱动烟雾粒子沿自然涡旋路径运动。将噪声坐标输入加入时间偏移`Position + Time * 0.1`，可使噪声场随时间缓慢漂移，避免静止感。

**火焰形态**：叠加两层Perlin噪声控制粒子的横向偏移——低频层（Frequency=0.5，Octaves=1）产生整体摇摆，高频层（Frequency=3.0，Octaves=3）产生细节抖动。将输出值映射到X轴速度，并乘以随粒子年龄递减的权重，实现底部稳定、顶部飘散的火焰特征。

**程序化纹理替代**：对于需要平铺且无明显重复感的地面尘土或水面波纹特效，使用3D Simplex噪声采样粒子世界坐标，输出值驱动粒子Alpha值，可替代重复感明显的噪声贴图，且支持动态更新无需重烘焙。

---

## 常见误区

**误区一：将Frequency与Scale混淆**。VFX Graph噪声节点的Frequency参数直接与输入坐标相乘，Frequency=2.0等同于将空间坐标放大两倍，噪声图案变密。有些用户试图通过Scale节点缩放粒子位置来调整噪声，但这同时改变了粒子系统的空间分布，而非单独控制噪声密度。应始终通过噪声节点自身的Frequency参数调整图案比例。

**误区二：认为Curl噪声可以直接输出位置偏移**。Curl噪声输出的是速度向量，代表流场方向和强度，必须接入速度相关模块（如Update粒子阶段的速度积分），而非直接赋值给粒子Position。若直接用作位置偏移，粒子会在单帧内跳变到新位置，产生闪烁而非流体运动。

**误区三：叠加过多Octaves以追求细节**。每增加一层Octaves，计算量线性增加。Octaves=6以上时，高频细节在屏幕分辨率限制下往往不可见，却造成明显的GPU开销。对于移动端或低端平台，Octaves建议保持在1~3之间，并通过调整Roughness（控制各层振幅衰减比）获得足够丰富的视觉层次。

---

## 知识关联

噪声函数建立在**纹理采样**的替代逻辑之上：纹理采样通过UV坐标查询预存图像数据，而噪声函数通过数学运算实时生成等效的连续数值场，理解两者的输出格式（0~1标量或-1~1向量）的一致性，有助于在两种方式之间灵活切换。噪声函数输出的平滑随机向量场，为下一个概念**Strip粒子**的路径生成提供了驱动数据——Strip粒子沿轨迹留下拖尾，而Curl噪声产生的流线型速度场能使Strip的轨迹呈现自然的流体曲线，避免直线运动带来的机械感。