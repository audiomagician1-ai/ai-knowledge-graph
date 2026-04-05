---
id: "cg-sdf-tracing"
concept: "SDF光线步进"
domain: "computer-graphics"
subdomain: "ray-tracing"
subdomain_name: "光线追踪"
difficulty: 3
is_milestone: false
tags: ["技术"]

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
updated_at: 2026-03-26
---


# SDF光线步进

## 概述

SDF光线步进（Sphere Tracing）是一种利用有符号距离场（Signed Distance Field，SDF）进行光线与隐式几何体求交的算法，由John C. Hart在1996年的论文《Sphere Tracing: A Geometric Method for the Antialiased Ray Tracing of Implicit Surfaces》中正式提出。与传统光线-三角形求交不同，该算法不需要显式的网格数据，而是通过对空间中每一点查询"到最近几何表面的最短距离"来驱动光线推进。

有符号距离场是一个标量函数 `f(p)`，其中 `p` 为空间中任意一点。当 `f(p) < 0` 时，点在物体内部；`f(p) = 0` 时，点恰好在物体表面；`f(p) > 0` 时，点在物体外部。Sphere Tracing的核心思路正是：在任意位置 `p`，以 `f(p)` 的绝对值作为安全步进距离，因为该半径内不可能存在任何表面，从而保证步进不会越过物体。

Sphere Tracing在实时图形学领域尤为重要，Shadertoy平台上大量的实时渲染Demo正是基于该算法，它也是现代程序化生成渲染、体积云和环境光遮蔽（SSAO替代方案AO from SDF）的底层技术之一。

---

## 核心原理

### 步进公式与收敛条件

设光线起点为 `o`，方向为单位向量 `d`，第 `n` 步的位置为 `p_n`。步进迭代公式为：

```
p_{n+1} = p_n + f(p_n) * d
```

每一步的步长等于当前点的SDF值 `f(p_n)`，即以该值为半径的"安全球体"不与任何表面相交。算法终止条件有两个：
- **命中**：`f(p_n) < ε`，通常 `ε` 取 `0.001` 到 `0.0001` 之间；
- **未命中**：累计步进距离 `t` 超过最大距离 `t_max`（如 `100.0`），或迭代次数超过上限（通常为64到256次）。

### 基本SDF图元的解析公式

Sphere Tracing的威力来源于SDF函数可以用解析公式构造基本图元，然后通过布尔运算组合：

- **球体**（圆心在原点，半径 `r`）：`f(p) = |p| - r`
- **轴对齐盒子**（半尺寸为 `b`）：`f(p) = |max(|p| - b, 0)|`（分量wise操作后取模长）
- **圆环**（大半径 `R`，管半径 `r`）：`f(p) = |(√(p.x²+p.z²) - R, p.y)| - r`

这些公式能保证Lipschitz常数为1，是Sphere Tracing收敛的数学前提。

### SDF布尔运算与软融合

多个SDF图元可以通过布尔运算组合成复杂场景，对应操作如下：

- **并集**（Union）：`f_union(p) = min(f_A(p), f_B(p))`
- **交集**（Intersection）：`f_inter(p) = max(f_A(p), f_B(p))`
- **差集**（Subtraction）：`f_diff(p) = max(-f_A(p), f_B(p))`

此外，Inigo Quilez（iq）推广了**平滑并集**（Smooth Union）操作：

```
f_smin(a, b, k) = min(a, b) - k²/(4*max(k - |a-b|, 0)) 
```
（polynomial smooth版本），参数 `k` 控制融合半径，使两个物体边界产生有机的"融合"过渡效果，这是传统多边形网格几乎无法实时实现的。

### 法线估算

Sphere Tracing渲染中，表面法线不直接存储，而是通过SDF的梯度数值近似计算：

```
n = normalize( f(p + ε*x̂) - f(p - ε*x̂),
               f(p + ε*ŷ) - f(p - ε*ŷ),
               f(p + ε*ẑ) - f(p - ε*ẑ) )
```

这是一次中心差分近似，需要对SDF函数额外调用6次，`ε` 通常取 `0.0001`。

---

## 实际应用

**Shadertoy实时渲染**：在WebGL/GLSL着色器中，整个场景由一个`map(vec3 p)`函数定义，每帧对每个像素执行Sphere Tracing，结合法线估算、软阴影（沿阴影光线累计最小SDF值）、环境光遮蔽（步进若干步累加SDF值的倒数）完成完整光照。Inigo Quilez的"Protean Clouds"在2015年仅用约200行GLSL实现了全程序化云层渲染。

**软阴影**：沿阴影光线步进时，记录路径上的最小惩罚值 `min(k * f(p) / t)`，其中 `k` 为软化系数（典型值 `8` 到 `32`），可产生柔和阴影半影，时间复杂度与主光线步进相同，无需光源的几何信息。

**字体与UI的SDF渲染**：Valve在2007年发表的技术报告《Improved Alpha-Tested Magnification for Vector Textures and Special Effects》中提出将字体预烘焙为SDF纹理，着色时对SDF值做阈值处理，即可在任意分辨率下渲染无锯齿字体，这是Sphere Tracing思想在2D领域的变体。

---

## 常见误区

**误区一：步长越大收敛越快**。部分初学者试图将步长乘以一个大于1的加速因子（如 `1.5 * f(p)`），以期减少迭代次数。然而Sphere Tracing的正确性依赖于"步长不超过SDF值"这一安全保证。若SDF函数的Lipschitz常数正好为1（即精确SDF），步长超过`f(p)`会导致光线穿过表面，产生漏洞（artifacts）。只有在SDF是"保守近似"（Lipschitz < 1的超保守SDF）时，适度加速才可能安全。

**误区二：SDF布尔运算结果仍是精确SDF**。`min(f_A, f_B)` 的并集操作在远离交界区域时确实是精确SDF，但在两个物体的"竞争区域"附近，结果函数的Lipschitz常数可能超过1，导致步进可能略微越过表面。实践中通常可以接受，但在精确渲染中应将 `ε` 适当放宽，或限制最大步长。

**误区三：Sphere Tracing与光线行进（Ray Marching）是同一概念**。Ray Marching泛指所有沿光线按固定步长推进的算法族（包括体积渲染的固定步长积分），而Sphere Tracing特指利用SDF自适应确定步长的特定算法。两者的本质区别在于步长策略：固定步长的Ray Marching效率低且容易漏步，而Sphere Tracing的步长由几何信息驱动，自适应且有理论收敛保证。

---

## 知识关联

**前置知识**：光线求交提供了"光线参数化"的基础思想，即将光线写为 `r(t) = o + t*d`，Sphere Tracing正是对参数 `t` 的迭代推进。与传统光线-三角形求交相比，Sphere Tracing放弃了解析求交，转而用迭代逼近换取对任意隐式几何的统一处理能力。

**延伸方向**：掌握Sphere Tracing后，可以自然过渡到**SDF场景的全局光照**（通过路径追踪结合Sphere Tracing的混合方法）、**动态SDF形变动画**（对多个SDF做时间插值）、以及**神经隐式表面**（NeRF和NeuS等方法用神经网络代替解析SDF函数，步进逻辑相同但需要网络推断）。Inigo Quilez在其个人网站 `iquilezles.org` 上维护了超过60种SDF图元的解析公式，是该领域最权威的参考资料。