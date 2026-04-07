---
id: "calculus-of-variations"
concept: "变分法"
domain: "mathematics"
subdomain: "optimization"
subdomain_name: "最优化"
difficulty: 9
is_milestone: false
tags: ["拓展"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 82.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-25
---

# 变分法

## 概述

变分法（Calculus of Variations）是研究**泛函极值**问题的数学分支。与普通微积分求函数极值不同，变分法的目标是在某类函数空间中找到使泛函 $J[y] = \int_a^b F(x, y, y') \, dx$ 取极值的函数 $y(x)$。泛函是"以函数为自变量的函数"，例如曲线长度、物理系统的作用量，都是泛函的典型例子。

变分法的历史起源于1696年约翰·伯努利（Johann Bernoulli）提出的**最速降线问题**：在重力场中，一质点从点A沿什么形状的曲线滑到点B所需时间最短？次年，包括牛顿、莱布尼茨、约翰与雅各布·伯努利兄弟在内的五人各自给出了解答，答案是摆线（旋轮线）。这一问题推动欧拉（Euler）和拉格朗日（Lagrange）在1740–1760年代建立了系统性的变分理论，其中最核心的成果就是以两人命名的方程。

变分法在物理学、工程和几何中具有不可替代的地位。费马原理（光沿光程最短路径传播）、哈密顿最小作用量原理（经典力学的基础）、最小曲面面积问题（肥皂膜形状）——这些问题都归结为泛函极值，无法用普通求导解决，必须借助变分法。

---

## 核心原理

### 泛函的变分与极值条件

设泛函 $J[y] = \int_a^b F(x, y, y') \, dx$，边界条件固定为 $y(a) = y_a$，$y(b) = y_b$。引入"比较函数" $y(x) + \varepsilon \eta(x)$，其中 $\eta(x)$ 为任意满足 $\eta(a) = \eta(b) = 0$ 的可微函数，$\varepsilon$ 为小参数。将泛函对 $\varepsilon$ 求导并令 $\varepsilon = 0$，得到泛函的**一阶变分** $\delta J$：

$$\delta J = \int_a^b \left( \frac{\partial F}{\partial y} \eta + \frac{\partial F}{\partial y'} \eta' \right) dx = 0$$

对第二项分部积分，利用 $\eta$ 在端点为零的条件消去边界项，得到：

$$\delta J = \int_a^b \left( \frac{\partial F}{\partial y} - \frac{d}{dx}\frac{\partial F}{\partial y'} \right) \eta \, dx = 0$$

由于 $\eta(x)$ 任意，根据**变分基本引理**（杜波依斯-雷蒙德引理），括号内表达式必须恒为零。

### Euler-Lagrange 方程

泛函取极值的必要条件是极值函数 $y(x)$ 满足：

$$\frac{\partial F}{\partial y} - \frac{d}{dx}\frac{\partial F}{\partial y'} = 0$$

这就是**Euler-Lagrange方程**，展开后是关于 $y(x)$ 的二阶常微分方程：

$$F_y - F_{y'x} - F_{y'y} y' - F_{y'y'} y'' = 0$$

注意这是极值的**必要条件**而非充分条件，满足此方程的解称为**极值曲线（extremal）**，是否真正取极值还需进一步判断（类比于普通微积分中驻点的概念）。

### 特殊情形：贝尔特拉米恒等式

当被积函数 $F$ 不显含 $x$（即 $\partial F/\partial x = 0$），Euler-Lagrange方程有首次积分：

$$F - y' \frac{\partial F}{\partial y'} = C \quad \text{（常数）}$$

这称为**贝尔特拉米恒等式（Beltrami identity）**，将二阶ODE降为一阶，极大简化求解。最速降线问题正是利用此恒等式求解，最终得到参数方程形式的摆线：$x = r(\theta - \sin\theta)$，$y = r(1 - \cos\theta)$。

### 多元推广与自然边界条件

当泛函含多个函数 $y_1, y_2, \ldots, y_n$ 时，极值条件变为 $n$ 个耦合的Euler-Lagrange方程组。若边界条件不固定（自由端点问题），还需附加**自然边界条件** $\left.\frac{\partial F}{\partial y'}\right|_{x=b} = 0$，这是变分过程中边界项不自动消失时额外获得的条件。

---

## 实际应用

**最速降线（Brachistochrone）**：质量为 $m$ 的质点在重力 $g$ 下从原点滑至点 $(x_1, y_1)$，下降时间为 $T = \int_0^{x_1} \sqrt{\frac{1+y'^2}{2gy}} \, dx$。此处 $F = \sqrt{(1+y'^2)/(2gy)}$ 不含 $x$，用贝尔特拉米恒等式求解，结果为摆线，与直线相比可将滑行时间减少约10%至30%（取决于端点位置）。

**最小曲面（Plateau问题）**：旋转曲面面积 $A = 2\pi \int_a^b y\sqrt{1+y'^2}\,dx$，对应的Euler-Lagrange方程解为**悬链面**（catenary of revolution），方程为 $y = c_1 \cosh\left(\frac{x-c_2}{c_1}\right)$，这正是两个圆环之间肥皂膜的形状。

**哈密顿最小作用量原理**：在经典力学中，系统从时刻 $t_1$ 到 $t_2$ 的运动由使**作用量** $S = \int_{t_1}^{t_2} L(q, \dot{q}, t) \, dt$ 取驻值的轨迹决定，其中 $L = T - V$ 为拉格朗日量（动能减势能）。对 $q$ 应用Euler-Lagrange方程直接导出牛顿第二定律，统一了整个经典力学框架。

---

## 常见误区

**误区一：Euler-Lagrange方程的解就是极小值**。Euler-Lagrange方程仅给出泛函的驻值条件，极值曲线可能对应极小值、极大值或鞍点（类似普通函数的驻点）。判断真正的极值性质需要计算**二阶变分** $\delta^2 J$，检验其正定性（雅各比条件和勒让德条件），这在一般教材中往往被略去。

**误区二：忽视函数空间的正则性要求**。Euler-Lagrange方程的推导假设极值函数 $y(x)$ 二阶连续可微（属于 $C^2[a,b]$）。但某些泛函的真正极值函数可能是分段光滑的（"折线"解），在拐角处需要满足**韦尔斯特拉斯-厄德曼角点条件**，直接套用Euler-Lagrange方程会漏掉这类解。

**误区三：将变分法等同于参数优化**。有限维优化中对参数求偏导，而变分法的自变量是整个函数，"变分"是函数空间中的方向导数概念。两者逻辑结构相似，但变分法的解是函数而非数值向量，约束条件（等周问题）也需引入函数形式的拉格朗日乘子 $\lambda \in \mathbb{R}$，不能直接套用有限维 KKT 条件的直觉。

---

## 知识关联

**与常微分方程的关系**：变分法的核心输出正是Euler-Lagrange方程，一个二阶ODE。因此求解变分问题的最后一步通常是用常微分方程方法（分离变量、积分因子、参数法）求解该ODE，这要求扎实的ODE基础。贝尔特拉米恒等式将其降为一阶ODE，是ODE降阶技巧在变分法中的直接体现。

**通向更高级理论**：变分法是**最优控制理论**（庞特里亚金极大值原理，1956年）的直接前驱——最优控制处理的是含控制变量约束的泛函极值，Euler-Lagrange方程在此推广为哈密顿正则方程组。在偏微分方程领域，变分法对应弱解与Sobolev空间理论，是现代有限元方法的数学基础。在微分几何中，测地线（曲面上两点间最短曲线）的方程正是弧长泛函的Euler-Lagrange方程，连接了变分法与黎曼几何。