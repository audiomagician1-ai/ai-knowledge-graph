---
id: "parametric-curves"
concept: "参数曲线"
domain: "mathematics"
subdomain: "analytic-geometry"
subdomain_name: "解析几何"
difficulty: 6
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 参数曲线

## 概述

参数曲线是指平面（或空间）中用一个（或多个）参数 $t$ 来同时表达点的各坐标分量的曲线表示形式。具体地，平面参数曲线的形式为 $\{(x,y) \mid x = f(t),\ y = g(t),\ t \in I\}$，其中 $I$ 是参数 $t$ 的取值区间，$f$ 与 $g$ 是定义在 $I$ 上的函数。与直接用 $y = h(x)$ 给出的显式曲线不同，参数形式允许曲线在 $x$ 方向"折返"——即同一 $x$ 值可以对应多个 $y$ 值，这是描述圆、椭圆、摆线等曲线不可缺少的工具。

历史上，伽利略（Galileo Galilei）在17世纪初研究抛体运动时，实际上已隐式使用了参数描述：水平方向 $x = v_0 t$，竖直方向 $y = \frac{1}{2}g t^2$，参数正是飞行时间 $t$。莱布尼茨（Leibniz）在1694年对参数曲线的切线进行了系统研究，给出了利用参数微分求斜率的公式 $\frac{dy}{dx} = \frac{dy/dt}{dx/dt}$，奠定了参数曲线微积分的基础。

参数曲线之所以在解析几何中占据重要位置，在于它能统一处理许多普通方程无法简洁表达的几何对象：摆线（cycloid）的一拱面积恰好是生成圆面积的 $3\pi r^2$，星形线的弧长计算在参数形式下只需一次直接积分，这些结果若用隐式方程处理则极为繁琐。

---

## 核心原理

### 参数方程的建立与几何意义

给定平面曲线，建立参数方程时需要选取具有明确几何意义的参量。以圆 $x^2 + y^2 = r^2$ 为例，令参数 $t$ 为点与正 $x$ 轴的夹角（即极角），则 $x = r\cos t,\ y = r\sin t,\ t \in [0, 2\pi)$。参数 $t$ 的变化方向决定了曲线的**定向**（orientation）：$t$ 增大时，点沿逆时针方向运动。同一条几何曲线可以有无穷多种参数化，例如令 $t \to 2t$ 得到 $x = r\cos 2t,\ y = r\sin 2t,\ t \in [0, \pi)$，所描述的几何轨迹完全相同，但"速度"翻倍。这说明参数方程不仅描述形状，还隐含了点沿曲线运动的节奏信息。

### 消去参数（消参）的方法

消参是将参数方程 $x = f(t),\ y = g(t)$ 转化为关于 $x, y$ 的方程 $F(x, y) = 0$ 的过程。常用的消参策略有以下三类：

**代数消参**：直接从一个方程解出 $t$ 后代入另一个。例如直线的参数方程 $x = 1 + 2t,\ y = 3 - t$，从第二式得 $t = 3 - y$，代入第一式得 $x = 1 + 2(3-y) = 7 - 2y$，即 $x + 2y = 7$。

**三角恒等式消参**：当参数以三角函数出现时，利用 $\sin^2 t + \cos^2 t = 1$ 或 $\sec^2 t - \tan^2 t = 1$ 消去参数。例如椭圆参数方程 $x = a\cos t,\ y = b\sin t$，则 $\frac{x^2}{a^2} + \frac{y^2}{b^2} = \cos^2 t + \sin^2 t = 1$，直接得到椭圆标准方程。双曲线参数方程 $x = a\sec t,\ y = b\tan t$ 则利用 $\sec^2 t - \tan^2 t = 1$，得 $\frac{x^2}{a^2} - \frac{y^2}{b^2} = 1$。

**消参后的定义域限制**：消参并非总能还原完整曲线。例如 $x = t^2,\ y = t^3$（$t \in \mathbb{R}$），消参得 $y^2 = x^3$（半三次抛物线），但原参数曲线在 $x \geq 0$ 且覆盖了 $y$ 的正负两侧，消参后方程本身没有限制 $x \geq 0$ 的信息，需要额外注明 $x \geq 0$。

### 切线、弧长与面积的参数化计算

**切线斜率**：若 $\frac{dx}{dt} \neq 0$，则曲线在参数 $t$ 处的切线斜率为
$$\frac{dy}{dx} = \frac{g'(t)}{f'(t)}$$
若 $f'(t_0) = 0$ 而 $g'(t_0) \neq 0$，则该点切线垂直于 $x$ 轴（竖直切线）；若两者均为零，需进一步分析奇点类型。

**弧长公式**：从 $t = \alpha$ 到 $t = \beta$ 的弧长为
$$L = \int_{\alpha}^{\beta} \sqrt{\left(\frac{dx}{dt}\right)^2 + \left(\frac{dy}{dt}\right)^2}\, dt$$
以摆线 $x = r(t - \sin t),\ y = r(1 - \cos t)$ 一拱（$t \in [0, 2\pi]$）为例，计算得 $L = 8r$，是生成圆直径的 $4$ 倍，这一结论在1658年由雷恩（Christopher Wren）首次证明。

**围成面积**：由参数曲线与 $x$ 轴围成的面积为
$$A = \int_{\alpha}^{\beta} y(t)\, f'(t)\, dt$$
积分方向需与曲线定向一致，否则结果差一个负号。

---

## 实际应用

**摆线（旋轮线）的分析**：车轮半径为 $r$ 的圆沿直线滚动，轮缘上一点的轨迹为 $x = r(t - \sin t),\ y = r(1 - \cos t)$。这条曲线满足"最速降线"（brachistochrone）和"等时曲线"（tautochrone）两个经典性质，均只能在参数形式下高效推导。其一拱面积为 $3\pi r^2$，弧长为 $8r$，都是利用上述参数积分公式直接得到。

**星形线（astroid）的弧长**：$x = a\cos^3 t,\ y = a\sin^3 t$（$t \in [0, 2\pi]$），消参得 $x^{2/3} + y^{2/3} = a^{2/3}$。弧长计算：$\frac{dx}{dt} = -3a\cos^2 t \sin t$，$\frac{dy}{dt} = 3a\sin^2 t \cos t$，故 $ds = 3a|\sin t \cos t|\,dt$，一周弧长 $L = 6a$，恰为外接圆周长 $2\pi a$ 的 $\frac{3}{\pi}$ 倍。

**计算机图形学中的贝塞尔曲线**：三次贝塞尔曲线由参数方程 $P(t) = (1-t)^3 P_0 + 3(1-t)^2 t P_1 + 3(1-t)t^2 P_2 + t^3 P_3$（$t \in [0,1]$）定义，其中 $P_0, P_1, P_2, P_3$ 为四个控制点。这种参数形式使得字体轮廓、路径动画的精确控制成为可能，消参在此没有实用意义，参数形式本身就是最终工具。

---

## 常见误区

**误区一：认为消参后方程与参数曲线完全等价**。消参只能得到曲线所在的代数曲线（locus），但可能包含额外的点或缺少定义域限制。例如 $x = \cos^2 t,\ y = \sin^2 t$，消参得 $x + y = 1$，但原参数曲线实际上只是线段 $\{(x,y) \mid x + y = 1,\ 0 \leq x \leq 1\}$，而不是整条直线；此外参数曲线上每个点被重复经过（$t$ 和 $\pi - t$ 给出同一点）。

**误区二：混淆参数曲线的"速度"与曲线本身的几何性质**。弧长、曲率等几何量与具体的参数化无关，但速度向量 $(f'(t), g'(t))$ 则依赖参数化选择。换参 $t = \phi(s)$ 后，切线方向不变，但切向量的模会改变。在用弧长 $s$ 作参数时（自然参数化），$\left|\frac{d\mathbf{r}}{ds}\right| = 1$，此时曲率公式最为简洁：$\kappa = \left|\frac{d^2\mathbf{r}}{ds^2}\right|$。

**误区三：对竖直切线处的切线斜率公式滥用**。当 $f'(t_0) = 0$ 时，公式 $dy/dx = g'(t)/f'(t)$ 不适用，需要直接分析 $x(t)$ 在 $t_