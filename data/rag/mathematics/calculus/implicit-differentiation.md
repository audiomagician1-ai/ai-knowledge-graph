---
id: "implicit-differentiation"
concept: "隐函数求导"
domain: "mathematics"
subdomain: "calculus"
subdomain_name: "微积分"
difficulty: 6
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "pending-rescore"
quality_score: 40.2
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.423
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 隐函数求导

## 概述

隐函数求导是微积分中处理方程 $F(x, y) = 0$ 形式的导数计算方法。与显函数 $y = f(x)$ 直接给出 $y$ 关于 $x$ 的表达式不同，隐函数中变量 $y$ 被"隐藏"在与 $x$ 的关系式里，无法（或难以）将 $y$ 单独解出，因此需要专门的求导策略。

隐函数这一概念在17世纪随微积分的诞生而出现。莱布尼茨和牛顿在研究曲线切线斜率时，发现许多曲线方程（如圆方程 $x^2 + y^2 = r^2$）无法简单地写成 $y = f(x)$ 的显式形式，隐函数微分法因此应运而生。1860年代，魏尔斯特拉斯进一步从严格的分析角度证明了隐函数定理，为该方法提供了理论保障。

隐函数求导之所以重要，在于大量几何曲线、物理约束方程以及多元关系式都以隐式形式自然呈现。例如椭圆 $\frac{x^2}{a^2} + \frac{y^2}{b^2} = 1$、笛卡尔叶形线 $x^3 + y^3 = 3axy$，若强行化为显式，不仅繁琐，还会丢失对称性信息，而隐函数求导一步到位，直接得出切线斜率。

---

## 核心原理

### 对 $x$ 两边同时求导——链式法则的关键作用

隐函数求导的核心操作是：将方程 $F(x, y) = 0$ 两边对 $x$ 求导，同时牢记 $y$ 是 $x$ 的函数，对 $y$ 的任何表达式求导时都需额外乘以 $\frac{dy}{dx}$（链式法则）。

以圆方程为例：$x^2 + y^2 = 25$

两边对 $x$ 求导：
$$2x + 2y \cdot \frac{dy}{dx} = 0$$

解出 $\frac{dy}{dx}$：
$$\frac{dy}{dx} = -\frac{x}{y}$$

这里 $2y \cdot \frac{dy}{dx}$ 这一项体现了链式法则：$y^2$ 对 $x$ 的导数是 $2y \cdot y'$，而非简单的 $2y$。这是隐函数求导最容易出错的地方。

### 隐函数定理给出的通用公式

对于可微方程 $F(x, y) = 0$，若偏导数 $F_y \neq 0$，则隐函数 $y(x)$ 的导数由以下公式给出：

$$\frac{dy}{dx} = -\frac{F_x}{F_y}$$

其中 $F_x = \frac{\partial F}{\partial x}$，$F_y = \frac{\partial F}{\partial y}$，分别是 $F$ 对 $x$ 和 $y$ 的偏导数。

以 $F(x, y) = x^3 + y^3 - 3xy = 0$（笛卡尔叶形线，令 $a=1$）为例：
- $F_x = 3x^2 - 3y$
- $F_y = 3y^2 - 3x$

代入公式：$\frac{dy}{dx} = -\frac{3x^2 - 3y}{3y^2 - 3x} = \frac{y - x^2}{y^2 - x}$

该公式将隐函数求导统一为计算两个偏导数之商，适合复杂方程的系统处理。

### 二阶隐导数的求法

有时需要求 $\frac{d^2y}{dx^2}$。方法是对已得到的 $\frac{dy}{dx}$ 表达式再次对 $x$ 求导，仍然把 $y$ 视为 $x$ 的函数。

以 $x^2 + y^2 = r^2$ 为例，已知 $\frac{dy}{dx} = -\frac{x}{y}$，对其求导：

$$\frac{d^2y}{dx^2} = -\frac{y \cdot 1 - x \cdot \frac{dy}{dx}}{y^2} = -\frac{y - x \cdot \left(-\frac{x}{y}\right)}{y^2} = -\frac{y^2 + x^2}{y^3} = -\frac{r^2}{y^3}$$

最后一步利用了原方程 $x^2 + y^2 = r^2$，将结果化简，这是隐函数二阶求导的标准收尾技巧。

---

## 实际应用

**求椭圆在特定点的切线方程：** 椭圆 $4x^2 + 9y^2 = 36$ 在点 $(3\cos\theta, 2\sin\theta)$ 的切线斜率。两边对 $x$ 求导得 $8x + 18y \cdot y' = 0$，解出 $y' = -\frac{4x}{9y}$。在点 $(0, 2)$（即 $\theta = \pi/2$）处，斜率为 $0$，切线为水平线 $y = 2$，与几何直觉完全吻合。

**物理中的相关变化率（Related Rates）：** 气球充气问题中，体积与半径满足 $V = \frac{4}{3}\pi r^3$。对时间 $t$ 两边求导：$\frac{dV}{dt} = 4\pi r^2 \cdot \frac{dr}{dt}$。这本质上是将 $V$ 和 $r$ 都视为 $t$ 的隐函数，对隐式关系求导，是隐函数求导在物理建模中最典型的应用场景。

**隐式曲线的法线方程：** 对于曲线 $x^2 - xy + y^2 = 7$，在点 $(1, -2)$ 处，两边求导得 $2x - y - x y' + 2y y' = 0$，代入 $(1,-2)$ 求得 $y' = \frac{4}{5}$，法线斜率为 $-\frac{5}{4}$，法线方程为 $y + 2 = -\frac{5}{4}(x-1)$。

---

## 常见误区

**误区一：对含 $y$ 的项求导时忘记乘 $\frac{dy}{dx}$。** 例如对 $y^3$ 求 $x$ 的导数，错误写成 $3y^2$，正确应为 $3y^2 \cdot \frac{dy}{dx}$。这是因为复合函数求导需要链式法则：外层 $(\cdot)^3$ 对内层 $y(x)$ 求导时，内层对 $x$ 的导数不可省略。

**误区二：混淆 $\frac{dF}{dx}$（全导数）与 $\frac{\partial F}{\partial x}$（偏导数）。** 在使用公式 $\frac{dy}{dx} = -\frac{F_x}{F_y}$ 时，分子分母都是偏导数（将另一变量视为常数），而不是全导数。初学者容易误将 $F_x$ 算成 $F$ 对 $x$ 的全导数（包含了 $y'$ 项），导致循环错误。

**误区三：认为隐函数导数与显函数导数结果必须"形式一样"。** 以 $y = \sqrt{25 - x^2}$（圆上半部分）为例，显式求导得 $y' = \frac{-x}{\sqrt{25-x^2}}$，而隐函数法得 $y' = -\frac{x}{y}$。两者实质相同（因为 $y = \sqrt{25-x^2}$），但隐函数结果含有 $y$，这是正常的，不必强行替换 $y$ 为 $x$ 的表达式。

---

## 知识关联

隐函数求导以**复合函数求导（链式法则）**为直接基础。每次对隐式方程中含 $y$ 的项关于 $x$ 求导，都是链式法则 $\frac{d}{dx}[g(y)] = g'(y) \cdot y'$ 的直接应用；同时需要**乘法法则**处理 $xy$、$x^2y$ 等乘积项，例如 $\frac{d}{dx}(xy) = y + x y'$。

从隐函数求导出发，可以自然过渡到**多元函数微分学**中的隐函数定理：当方程 $F(x, y, z) = 0$ 定义了 $z$ 为 $x, y$ 的函数时，有 $\frac{\partial z}{\partial x} = -\frac{F_x}{F_z}$，这是单变量隐函数公式 $\frac{dy}{dx} = -\frac{F_x}{F_y}$ 的直接推广。此外，**相关变化率**问题是隐函数求导对时间参数的应用，而**参数方程求导**（$\frac{dy}{dx} = \frac{dy/dt}{dx/dt}$）则是处理隐式曲线的另一条路径，两者相辅相成。
