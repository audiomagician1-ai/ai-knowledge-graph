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
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 隐函数求导

## 概述

隐函数求导是指对形如 $F(x, y) = 0$ 的方程两边同时对 $x$ 求导，从而求出 $\frac{dy}{dx}$ 的方法。与显函数 $y = f(x)$ 不同，隐函数中 $y$ 无法（或不便）被孤立到等号一侧，例如 $x^2 + y^2 = 1$ 定义了单位圆上的曲线关系，此时直接写出 $y = f(x)$ 需要分情况讨论，而隐函数求导则无需拆分即可直接得到斜率表达式。

这一方法由莱布尼茨在17世纪建立微积分框架时提出，其核心依赖**链式法则（chain rule）**：将 $y$ 视为 $x$ 的函数，对含 $y$ 的项求导时，额外乘以 $\frac{dy}{dx}$。隐函数求导不仅简化了复杂曲线的切线计算，也是多变量微积分中隐函数定理的单变量基础。

对于无法用初等函数显式表达的曲线（如笛卡儿叶形线 $x^3 + y^3 = 3axy$），隐函数求导是唯一可行的基本求导途径，因此在工程曲线分析、热力学状态方程求偏导等领域具有不可替代的地位。

---

## 核心原理

### 基本操作步骤

对方程 $F(x, y) = 0$ 两边关于 $x$ 求导时，遵循以下规则：

1. 含纯 $x$ 的项按普通求导处理；
2. 含 $y$ 的项使用链式法则：$\frac{d}{dx}[g(y)] = g'(y) \cdot \frac{dy}{dx}$；
3. 求导后代数整理，将所有含 $\frac{dy}{dx}$ 的项移至一侧，解出 $\frac{dy}{dx}$。

以 $x^2 + y^2 = r^2$ 为例：两边对 $x$ 求导得 $2x + 2y \cdot \frac{dy}{dx} = 0$，解得 $\frac{dy}{dx} = -\frac{x}{y}$（$y \neq 0$）。

### 链式法则的关键应用

当方程含有 $y$ 的复合形式时，链式法则不可省略。例如对 $\sin(y) + xy = 2$ 求导：
$$\cos(y) \cdot \frac{dy}{dx} + y + x \cdot \frac{dy}{dx} = 0$$
$$\frac{dy}{dx}(\cos y + x) = -y$$
$$\frac{dy}{dx} = \frac{-y}{\cos y + x}$$

注意结果中同时含有 $x$ 和 $y$，这是隐函数求导结果的典型特征——导数表达式依赖于曲线上点的坐标 $(x, y)$，而非仅仅依赖 $x$。

### 公式法（偏导数形式）

若将方程写成 $F(x, y) = 0$，且 $F$ 关于 $x$、$y$ 的偏导数存在，则：
$$\frac{dy}{dx} = -\frac{F_x}{F_y}, \quad F_y \neq 0$$

其中 $F_x = \frac{\partial F}{\partial x}$，$F_y = \frac{\partial F}{\partial y}$。对 $x^2 + y^2 - r^2 = 0$，有 $F_x = 2x$，$F_y = 2y$，代入得 $\frac{dy}{dx} = -\frac{2x}{2y} = -\frac{x}{y}$，与直接求导结果一致。这一公式在方程结构复杂时极大提升计算效率。

### 高阶隐函数求导

求二阶导数 $\frac{d^2y}{dx^2}$ 时，需对已求得的 $\frac{dy}{dx}$ 再次关于 $x$ 求导，并在化简过程中将 $\frac{dy}{dx}$ 的表达式代回。以 $x^2 + y^2 = r^2$ 为例：

已知 $\frac{dy}{dx} = -\frac{x}{y}$，再对 $x$ 求导：
$$\frac{d^2y}{dx^2} = -\frac{y - x \cdot \frac{dy}{dx}}{y^2} = -\frac{y - x \cdot (-\frac{x}{y})}{y^2} = -\frac{y^2 + x^2}{y^3} = -\frac{r^2}{y^3}$$

---

## 实际应用

**切线方程的求法**：对曲线 $x^3 + y^3 = 9$ 上的点 $(1, 2)$，用隐函数求导得 $3x^2 + 3y^2 \cdot \frac{dy}{dx} = 0$，从而 $\frac{dy}{dx} = -\frac{x^2}{y^2}$，在 $(1, 2)$ 处斜率为 $-\frac{1}{4}$，切线方程为 $y - 2 = -\frac{1}{4}(x - 1)$。

**笛卡儿叶形线**：方程 $x^3 + y^3 - 3xy = 0$ 无法写成 $y = f(x)$ 的初等闭合形式，隐函数求导给出：
$$\frac{dy}{dx} = \frac{y - x^2}{y^2 - x}$$
这直接用于分析该曲线在第一象限的极值点和渐近线行为。

**物理中的状态方程**：理想气体方程 $PV = nRT$ 若视 $P$、$V$ 均为时间 $t$ 的函数，则对 $t$ 隐式求导得 $\dot{P}V + P\dot{V} = 0$，即 $\frac{dP}{dt} = -\frac{P}{V}\frac{dV}{dt}$，这正是绝热过程分析的出发点。

---

## 常见误区

**误区一：忽略对 $y$ 的链式法则**。对 $y^3$ 求导时写成 $3y^2$ 而非 $3y^2 \cdot \frac{dy}{dx}$，是最高频的错误。这源于将 $y$ 误当成常数或自变量处理，导致最终方程中 $\frac{dy}{dx}$ 消失，无法求解。

**误区二：认为隐函数导数一定不能含 $y$**。实际上，$\frac{dy}{dx} = -\frac{x}{y}$ 这类结果是完全合法的——它表示在曲线上某点 $(x_0, y_0)$ 处的斜率，代入该点坐标即可得到数值。如果需要仅含 $x$ 的表达式，反而需要先从原方程解出 $y$，这会绕回显函数问题。

**误区三：公式法 $-F_x/F_y$ 与直接求导是两套不同方法**。两者本质完全等价，公式法是直接求导步骤的压缩形式。当 $F_y = 0$ 时，两种方法都会失效，对应曲线在该点处的切线垂直于 $x$ 轴（即导数不存在）。

---

## 知识关联

隐函数求导直接依赖**复合函数求导（链式法则）**：若没有"对 $y$ 的函数求导后乘 $\frac{dy}{dx}$"这一操作，整套方法无法成立。同时，**乘积法则**在处理 $xy$、$x^2y$ 等混合项时频繁出现，需熟练配合使用。

在更高阶的学习中，隐函数求导是**多元函数隐函数定理**的直觉基础：单变量情形 $F(x,y)=0$ 的公式 $dy/dx = -F_x/F_y$ 直接推广为多元情形 $F(x,y,z)=0$ 中的 $\partial z/\partial x = -F_x/F_z$。此外，**参数方程求导**中，当参数形式难以消去时，隐函数视角提供了等价的处理思路。掌握隐函数求导，也为后续学习**相关变化率（related rates）**问题打下直接基础，因为相关变化率本质上是对隐式关系方程两端关于时间求导。