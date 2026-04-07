# SDF光线步进

## 概述

SDF光线步进（Sphere Tracing）是一种利用有符号距离场（Signed Distance Field，SDF）进行光线与隐式几何体求交的算法，由John C. Hart在1996年发表于《The Visual Computer》期刊第12卷第10期的论文《Sphere Tracing: A Geometric Method for the Antialiased Ray Tracing of Implicit Surfaces》中正式提出。与传统光线-三角形求交不同，该算法不需要显式的网格数据，而是通过对空间中每一点查询"到最近几何表面的最短距离"来驱动光线推进。

有符号距离场是一个标量函数 $f(\mathbf{p})$，其中 $\mathbf{p}$ 为空间中任意一点。当 $f(\mathbf{p}) < 0$ 时，点在物体内部；$f(\mathbf{p}) = 0$ 时，点恰好在物体表面；$f(\mathbf{p}) > 0$ 时，点在物体外部。Sphere Tracing的核心思路正是：在任意位置 $\mathbf{p}$，以 $f(\mathbf{p})$ 的绝对值作为安全步进距离，因为该半径内不可能存在任何表面，从而保证步进不会越过物体。

Sphere Tracing在实时图形学领域尤为重要，Shadertoy平台（2013年由Inigo Quilez与Pol Jerez共同创建）上超过50万个公开Demo中，相当大比例正是基于该算法实现实时渲染的。它也是现代程序化生成渲染、体积云和环境光遮蔽（SSAO替代方案：基于SDF的AO）的底层技术之一。算法本身的计算复杂度与场景几何的多边形数量完全无关，使其特别适合表达分形、流体、生物形态等传统网格难以描述的隐式几何。

**关键问题**：当场景中有数百个基本SDF图元叠加时，每步迭代都需要对所有图元求值并取最小值，时间复杂度为 $O(N)$（$N$ 为图元数量）。这一性质使得Sphere Tracing在复杂场景中面临严峻的性能挑战——应如何设计数据结构或空间划分策略，在保证SDF数学性质的前提下加速查询？

---

## 核心原理

### 步进公式与收敛条件

设光线起点为 $\mathbf{o}$，方向为单位向量 $\mathbf{d}$，第 $n$ 步的位置为 $\mathbf{p}_n$，累计行进距离为 $t_n$。步进迭代公式为：

$$\mathbf{p}_{n+1} = \mathbf{p}_n + f(\mathbf{p}_n) \cdot \mathbf{d}$$

等价地，以标量形式表示累计距离的递推：

$$t_{n+1} = t_n + f(\mathbf{o} + t_n \mathbf{d})$$

每一步的步长等于当前点的SDF值 $f(\mathbf{p}_n)$，即以该值为半径的"安全球体"不与任何表面相交。算法终止条件有两个：

- **命中**：$f(\mathbf{p}_n) < \varepsilon$，通常 $\varepsilon$ 取 $0.001$ 到 $0.0001$ 之间，具体值视场景尺度而定；
- **未命中**：累计步进距离 $t$ 超过最大距离 $t_{\max}$（如 $100.0$），或迭代次数超过上限（通常为64到256次）。

Sphere Tracing收敛的数学前提是SDF函数满足**Lipschitz条件**，即对任意两点 $\mathbf{p}, \mathbf{q}$，有：

$$|f(\mathbf{p}) - f(\mathbf{q})| \leq L \cdot |\mathbf{p} - \mathbf{q}|$$

其中Lipschitz常数 $L \leq 1$。这一条件保证了以 $f(\mathbf{p})$ 为半径的球体内不存在零交叉（即表面）。当 $L = 1$ 时称为精确SDF（Exact SDF），收敛最快；当 $L < 1$ 时为保守SDF（Conservative SDF），步进偏慢但依然安全；当 $L > 1$ 时，步长可能超过实际最近表面距离，导致光线穿越表面产生漏洞（artifacts）。

若某SDF函数的Lipschitz常数 $L > 1$（例如某些不当的域变形操作导致的梯度拉伸），Sphere Tracing的安全性保证将失效。在实际工程中，可以通过计算SDF函数的数值梯度模长来检测 $L$，当 $|\nabla f(\mathbf{p})| > 1$ 时即为警示信号。修正方法包括对SDF值乘以惩罚因子 $1/L$ 以恢复保守性，或借助Eikonal方程正则化约束网络输出（在神经隐式场景中尤为常见）。Eikonal方程表达为 $|\nabla f(\mathbf{p})| = 1$，在NeuS（Wang et al., 2021）等神经隐式表面重建工作中，该方程被作为训练损失项强制施加，以确保网络输出的隐函数具备真正的SDF语义。

### 基本SDF图元的解析公式

Sphere Tracing的威力来源于SDF函数可以用解析公式构造基本图元，然后通过布尔运算组合。以下是四种最常用图元的精确SDF公式：

**球体**（圆心在原点，半径 $r$）：

$$f(\mathbf{p}) = |\mathbf{p}| - r$$

**轴对齐盒子**（半尺寸向量为 $\mathbf{b} = (b_x, b_y, b_z)$）：

$$f(\mathbf{p}) = \left|\max(|\mathbf{p}| - \mathbf{b},\ \mathbf{0})\right| + \min\!\left(\max(p_x - b_x,\ p_y - b_y,\ p_z - b_z),\ 0\right)$$

其中第一项为外部距离，第二项为内部有符号深度，两项合并恰好给出全空间的精确有符号距离。

**圆环**（大半径 $R$，管半径 $r$，圆环位于 $xz$ 平面）：

$$f(\mathbf{p}) = \left|\left(\sqrt{p_x^2 + p_z^2} - R,\ p_y\right)\right| - r$$

**胶囊体**（端点 $\mathbf{a}$、$\mathbf{b}$，半径 $r$）：

$$f(\mathbf{p}) = \left|\mathbf{p} - \mathbf{a} - \text{clamp}\!\left(\frac{(\mathbf{p}-\mathbf{a})\cdot(\mathbf{b}-\mathbf{a})}{|\mathbf{b}-\mathbf{a}|^2},\ 0,\ 1\right)\cdot(\mathbf{b}-\mathbf{a})\right| - r$$

这些公式均保证Lipschitz常数恰好为1，是Sphere Tracing正确收敛的数学前提。Inigo Quilez在其个人网站（iquilezles.org）上系统整理了超过60种SDF图元的解析公式，涵盖棱柱、六边形、贝塞尔曲线管道、分形等复杂形体，是实践SDF建模的权威参考。

**例如**，对于半径 $r = 1.0$ 的单位球体，查询点 $\mathbf{p} = (2, 0, 0)$ 的SDF值为 $f(\mathbf{p}) = |(2,0,0)| - 1.0 = 2.0 - 1.0 = 1.0$。这意味着从该点出发，光线可以安全步进 $1.0$ 个单位而不穿越任何表面。若光线方向为 $\mathbf{d} = (-1, 0, 0)$，则下一个步进位置为 $\mathbf{p}_1 = (2,0,0) + 1.0 \cdot (-1,0,0) = (1,0,0)$，恰好到达球体表面（$f(\mathbf{p}_1) = 0$），单步即命中。这一理想情况在实践中仅发生于光线方向恰好指向最近表面点时；一般情况下需要多次迭代逐步逼近。

**深入问题**：若光线以接近切线的方向掠过一个球体，步进过程会发生什么？切线光线在极端情况下可能需要数十次迭代才能收敛，原因是光线始终与表面保持极小间距，SDF值趋近于零但始终不触发命中条件。这被称为"掠射问题"（Grazing Problem），是Sphere Tracing性能调优中必须重视的边界情形。

### SDF布尔运算与软融合

多个SDF图元可以通过布尔运算组合成复杂场景，对应操作如下：

- **并集**（Union）：$f_{\cup}(\mathbf{p}) = \min(f_A(\mathbf{p}),\ f_B(\mathbf{p}))$
- **交集**（Intersection）：$f_{\cap}(\mathbf{p}) = \max(f_A(\mathbf{p}),\ f_B(\mathbf{p}))$
- **差集**（Subtraction）：$f_{-}(\mathbf{p}) = \max(-f_A(\mathbf{p}),\ f_B(\mathbf{p}))$

值得注意的是，$\min$ 并集结果在两物体的竞争边界区域会产生Lipschitz常数略超1的问题（详见常见误区一节），但在大多数实时渲染场景中误差可以接受。

此外，Inigo Quilez于2013年在其个人网站推广了**多项式平滑并集**（Polynomial Smooth Union）操作：

$$f_{\text{smin}}(a, b, k) = \min(a, b) - \frac{h^2 \cdot k}{4}, \quad h = \max\!\left(k - |a - b|,\ 0\right) / k$$

参数 $k$ 控制融合半径（典型值为 $0.1$ 到 $0.5$），使两个物体边界产生有机的"融合"过渡效果，混合宽度恰好为 $k$ 个世界空间单位。这是传统多边形网格几乎无法实时实现的形态过渡，在生物体、熔岩灯、流体模拟的程序化建模中应用广泛。

**案例**：将两个半径均为0.5的球体（圆心分别位于 $(-0.6, 0, 0)$ 和 $(0.6, 0, 0)$）用 $k = 0.4$ 的平滑并集合并，在两球恰好不相交时仍能产生连续的融合过渡区，视觉上酷似水银滴合并的动态效果。这一操作在GLSL中仅需5行代码，但在传统多边形流程中需要借助动态Remeshing或Metaball等代价更高的方案。

### 法线估算

Sphere Tracing渲染中，表面法线不直接存储，而是通过SDF的梯度数值近似计算。根据微积分基本定理，精确SDF的梯度模长在表面处恒为1（即 $|\nabla f| = 1$），梯度方向即为外法线方向。标准做法是使用**中心差分**（Central Differences）：

$$\mathbf{n} = \text{normalize}\!\begin{pmatrix} f(\mathbf{p} + \varepsilon\hat{x}) - f(\mathbf{p} - \varepsilon\hat{x}) \\ f(\mathbf{p} + \varepsilon\hat{y}) - f(\mathbf{p} - \varepsilon\hat{y}) \\ f(\mathbf{p} + \varepsilon\hat{z}) - f(\mathbf{p} - \varepsilon\hat{z}) \end{pmatrix}$$

这需要对SDF函数额外调用6次，$\varepsilon$ 通常取 $0.0001$。Quilez在2022年提出了一种**四面体采样优化**方案，仅需4次SDF查询即可完成法线估算，在GPU着色器中可减少约33%的法线计算开销，适合SDF计算开销较大的复杂场景。其核心思路是利用正四面体的4个顶点方向代替轴对齐的6个方向：

$$\mathbf{n} = \text{normalize}\!\left( k_0\, f(\mathbf{p}+k_0\varepsilon) + k_1\, f(\mathbf{p}+k_1\varepsilon) + k_2\, f(\mathbf{p}+k_2\varepsilon) + k_3\, f(\mathbf{p}+k_3\varepsilon) \right)$$

其中 $k_0=(+1,-