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

SDF光线步进（Sphere Tracing）是一种利用有符号距离场（Signed Distance Field，SDF）进行光线与隐式几何体求交的算法，由John C. Hart在1996年发表于《ACM Transactions on Graphics》的论文《Sphere Tracing: A Geometric Method for the Antialiased Ray Tracing of Implicit Surfaces》中正式提出。与传统光线-三角形求交不同，该算法不需要显式的网格数据，而是通过对空间中每一点查询"到最近几何表面的最短距离"来驱动光线推进。

有符号距离场是一个标量函数 $f(\mathbf{p})$，其中 $\mathbf{p}$ 为空间中任意一点。当 $f(\mathbf{p}) < 0$ 时，点在物体内部；$f(\mathbf{p}) = 0$ 时，点恰好在物体表面；$f(\mathbf{p}) > 0$ 时，点在物体外部。Sphere Tracing的核心思路正是：在任意位置 $\mathbf{p}$，以 $f(\mathbf{p})$ 的绝对值作为安全步进距离，因为该半径内不可能存在任何表面，从而保证步进不会越过物体。

Sphere Tracing在实时图形学领域尤为重要，Shadertoy平台（2013年由Inigo Quilez与Pol Jerez共同创建）上超过50万个公开Demo中，相当大比例正是基于该算法实现实时渲染的。它也是现代程序化生成渲染、体积云和环境光遮蔽（SSAO替代方案：基于SDF的AO）的底层技术之一。

> **参考文献**
> - Hart, J. C. (1996). *Sphere Tracing: A Geometric Method for the Antialiased Ray Tracing of Implicit Surfaces*. The Visual Computer, 12(10), 527–545.
> - Quilez, I. (2008–2024). *Modeling with Signed Distance Functions*. iquilezles.org. 收录60余种SDF图元解析公式。

---

## 核心原理

### 步进公式与收敛条件

设光线起点为 $\mathbf{o}$，方向为单位向量 $\mathbf{d}$，第 $n$ 步的位置为 $\mathbf{p}_n$。步进迭代公式为：

$$\mathbf{p}_{n+1} = \mathbf{p}_n + f(\mathbf{p}_n) \cdot \mathbf{d}$$

每一步的步长等于当前点的SDF值 $f(\mathbf{p}_n)$，即以该值为半径的"安全球体"不与任何表面相交。算法终止条件有两个：

- **命中**：$f(\mathbf{p}_n) < \varepsilon$，通常 $\varepsilon$ 取 $0.001$ 到 $0.0001$ 之间；
- **未命中**：累计步进距离 $t$ 超过最大距离 $t_{\max}$（如 $100.0$），或迭代次数超过上限（通常为64到256次）。

Sphere Tracing收敛的数学前提是SDF函数满足**Lipschitz条件**，即对任意两点 $\mathbf{p}, \mathbf{q}$，有 $|f(\mathbf{p}) - f(\mathbf{q})| \leq L \cdot |\mathbf{p} - \mathbf{q}|$，其中Lipschitz常数 $L \leq 1$。这一条件保证了以 $f(\mathbf{p})$ 为半径的球体内不存在零交叉（即表面）。

**问题**：若某SDF函数的Lipschitz常数 $L > 1$，Sphere Tracing的安全性保证将如何失效？在实际工程中应如何检测和修正这种情况？

### 基本SDF图元的解析公式

Sphere Tracing的威力来源于SDF函数可以用解析公式构造基本图元，然后通过布尔运算组合。以下是三种最常用图元的精确SDF公式：

- **球体**（圆心在原点，半径 $r$）：

$$f(\mathbf{p}) = |\mathbf{p}| - r$$

- **轴对齐盒子**（半尺寸向量为 $\mathbf{b}$）：

$$f(\mathbf{p}) = \left|\max(|\mathbf{p}| - \mathbf{b},\ \mathbf{0})\right| + \min\!\left(\max(p_x - b_x,\ p_y - b_y,\ p_z - b_z),\ 0\right)$$

- **圆环**（大半径 $R$，管半径 $r$）：

$$f(\mathbf{p}) = \left|\left(\sqrt{p_x^2 + p_z^2} - R,\ p_y\right)\right| - r$$

这些公式均保证Lipschitz常数恰好为1，是Sphere Tracing正确收敛的数学前提。

**例如**，对于半径 $r = 1.0$ 的单位球体，查询点 $\mathbf{p} = (2, 0, 0)$ 的SDF值为 $f(\mathbf{p}) = |(2,0,0)| - 1.0 = 2.0 - 1.0 = 1.0$。这意味着从该点出发，光线可以安全步进 $1.0$ 个单位而不穿越任何表面。若光线方向为 $\mathbf{d} = (-1, 0, 0)$，则下一个步进位置为 $\mathbf{p}_1 = (2,0,0) + 1.0 \cdot (-1,0,0) = (1,0,0)$，恰好到达球体表面（$f(\mathbf{p}_1) = 0$），单步即命中。

### SDF布尔运算与软融合

多个SDF图元可以通过布尔运算组合成复杂场景，对应操作如下：

- **并集**（Union）：$f_{\cup}(\mathbf{p}) = \min(f_A(\mathbf{p}),\ f_B(\mathbf{p}))$
- **交集**（Intersection）：$f_{\cap}(\mathbf{p}) = \max(f_A(\mathbf{p}),\ f_B(\mathbf{p}))$
- **差集**（Subtraction）：$f_{-}(\mathbf{p}) = \max(-f_A(\mathbf{p}),\ f_B(\mathbf{p}))$

此外，Inigo Quilez于2013年在其个人网站推广了**多项式平滑并集**（Polynomial Smooth Union）操作：

$$f_{\text{smin}}(a, b, k) = \min(a, b) - \frac{h^2 \cdot k}{4}, \quad h = \max\!\left(k - |a - b|,\ 0\right) / k$$

参数 $k$ 控制融合半径（典型值为 $0.1$ 到 $0.5$），使两个物体边界产生有机的"融合"过渡效果。这是传统多边形网格几乎无法实时实现的形态过渡，在生物体、熔岩灯、流体模拟的程序化建模中应用广泛。

### 法线估算

Sphere Tracing渲染中，表面法线不直接存储，而是通过SDF的梯度数值近似计算。标准做法是使用**中心差分**（Central Differences）：

$$\mathbf{n} = \text{normalize}\!\begin{pmatrix} f(\mathbf{p} + \varepsilon\hat{x}) - f(\mathbf{p} - \varepsilon\hat{x}) \\ f(\mathbf{p} + \varepsilon\hat{y}) - f(\mathbf{p} - \varepsilon\hat{y}) \\ f(\mathbf{p} + \varepsilon\hat{z}) - f(\mathbf{p} - \varepsilon\hat{z}) \end{pmatrix}$$

这需要对SDF函数额外调用6次，$\varepsilon$ 通常取 $0.0001$。Quilez在2022年提出了一种**四面体采样优化**方案，仅需4次SDF查询即可完成法线估算，在GPU着色器中可减少约33%的法线计算开销，适合SDF计算开销较大的复杂场景。

---

## 实际应用

### 实时渲染与Shadertoy

在WebGL/GLSL着色器中，整个场景由一个`map(vec3 p)`函数定义，每帧对每个像素执行Sphere Tracing，结合法线估算、软阴影、环境光遮蔽完成完整光照。

**例如**，Inigo Quilez于2015年发布的"Protean Clouds"（Shadertoy ID: `ldlGmt`）仅用约200行GLSL代码实现了全程序化体积云层渲染，运行于单块消费级GPU（GTX 970），以1080p分辨率实时运行帧率约为30fps，展示了Sphere Tracing在复杂体积场景中的实用性上限。

**软阴影**是另一个典型应用：沿阴影光线步进时，记录路径上的最小惩罚值 $s = \min\!\left(k \cdot f(\mathbf{p}) / t\right)$，其中 $k$ 为软化系数（典型值 $8$ 到 $32$），可产生柔和阴影半影，时间复杂度与主光线步进相同，无需光源的几何信息。

### 字体与UI的SDF渲染

Valve Software的工程师Chris Green于2007年在SIGGRAPH发表技术报告《Improved Alpha-Tested Magnification for Vector Textures and Special Effects》，提出将字体预烘焙为SDF纹理（分辨率通常为64×64至256×256），着色时对SDF值做阈值处理，即可在任意分辨率下渲染无锯齿字体。该方案被Unity引擎的TextMeshPro插件（2016年发布，2018年正式整合进Unity 2018.2）采用，成为游戏UI文字渲染的行业标准之一。这是Sphere Tracing核心思想（SDF零值作为表面边界）在2D光栅化领域的直接变体。

> **参考文献**
> - Green, C. (2007). *Improved Alpha-Tested Magnification for Vector Textures and Special Effects*. SIGGRAPH 2007 Sketch. Valve Software.
> - Quilez, I. (2015). *Protean Clouds*. Shadertoy. https://www.shadertoy.com/view/ldlGmt

### 神经隐式表面与NeRF的关联

近年来，SDF与深度学习的结合催生了**神经隐式表面**（Neural Implicit Surfaces）领域。Wang等人于2021年发表的《NeuS: Learning Neural Implicit Surfaces by Volume Rendering for Multi-view Reconstruction》，以及Yariv等人同年发表的《Volume Rendering of Neural Implicit Surfaces》，均以Sphere Tracing作为推断时的几何求交方法，但以神经网络代替解析SDF函数。步进逻辑与经典Sphere Tracing完全相同，每步需进行一次网络前向推断（约需1–10ms/像素），因此推断速度远低于实时，但重建质量大幅超越传统MVS方法。

---

## 常见误区

**误区一：步长越大收敛越快**。部分初学者试图将步长乘以一个大于1的加速因子（如 $1.5 \cdot f(\mathbf{p})$），以期减少迭代次数。然而Sphere Tracing的正确性依赖于"步长不超过SDF值"这一安全保证。若SDF函数的Lipschitz常数 $L = 1$（即精确SDF），步长超过 $f(\mathbf{p})$ 会导致光线穿过表面，产生漏洞（artifacts）。只有在SDF是"超保守近似"（$L < 1$）时，适度加速才可能安全。

**误区二：SDF布尔运算结果仍是精确SDF**。$\min(f_A, f_B)$ 的并集操作在远离交界区域时确实是精确SDF，但在两个物体的"竞争区域"附近，结果函数的Lipschitz常数可能超过1，导致步进略微越过表面。实践中通常可以接受，但在精确渲染中应将 $\varepsilon$ 适当放宽（例如从 $0.0001$ 放宽