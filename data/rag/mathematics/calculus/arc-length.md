---
id: "arc-length"
concept: "弧长公式"
domain: "mathematics"
subdomain: "calculus"
subdomain_name: "微积分"
difficulty: 7
is_milestone: false
tags: ["应用"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 35.1
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 0.407
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 弧长公式

## 概述

弧长公式是微积分中用于精确计算曲线长度的积分表达式。对于一条光滑曲线，其长度并非简单地由端点坐标决定，而需要将曲线分割成无数微小线段，通过对这些线段长度求和取极限来得到。这一思想最早可追溯到17世纪，1659年威廉·尼尔（William Neile）首次成功计算了半立方抛物线 $y^2 = x^3$ 的弧长，这是历史上第一个被严格求解的非平凡弧长问题。

弧长公式的核心在于勾股定理的无穷小推广。将曲线上相邻两点之间的微弧段近似为直线段，其长度为 $ds = \sqrt{(dx)^2 + (dy)^2}$，对全段积分即得总弧长。这一方法要求被积函数连续，因此函数的光滑性（即导数连续）是公式成立的基本前提。

在工程与物理中，弧长公式用于计算输电线的悬垂长度、弹簧展开长度、行星轨道周长等问题。在微分几何中，弧长更是曲线参数化、曲率定义的基础——曲率 $\kappa$ 的定义本身就依赖于对弧长参数的求导。

## 核心原理

### 显式函数的弧长公式

设函数 $y = f(x)$ 在区间 $[a, b]$ 上具有连续导数 $f'(x)$，则曲线的弧长为：

$$L = \int_a^b \sqrt{1 + [f'(x)]^2} \, dx$$

推导过程：将 $[a,b]$ 分成 $n$ 个小区间，第 $i$ 段弧近似为折线段，其长度为：

$$\Delta s_i \approx \sqrt{(\Delta x_i)^2 + (\Delta y_i)^2} = \sqrt{1 + \left(\frac{\Delta y_i}{\Delta x_i}\right)^2} \cdot \Delta x_i$$

由均值定理，$\frac{\Delta y_i}{\Delta x_i} = f'(\xi_i)$，令 $n \to \infty$，即得上述积分公式。注意：被积函数 $\sqrt{1+[f'(x)]^2} \geq 1$，这意味着任何非平凡曲线的弧长严格大于其水平投影长度 $b - a$。

### 参数曲线的弧长公式

设曲线由参数方程 $x = x(t)$，$y = y(t)$，$t \in [\alpha, \beta]$ 给出，且 $x'(t)$、$y'(t)$ 连续，则弧长为：

$$L = \int_\alpha^\beta \sqrt{[x'(t)]^2 + [y'(t)]^2} \, dt$$

此公式统一了显式函数的情形：若令 $x(t) = t$，则 $x'(t) = 1$，代入即还原为 $\int_a^b \sqrt{1 + [f'(t)]^2} \, dt$。

**经典示例：圆的周长验证。** 取 $x = r\cos t$，$y = r\sin t$，$t \in [0, 2\pi]$，则：

$$L = \int_0^{2\pi} \sqrt{r^2\sin^2 t + r^2\cos^2 t} \, dt = \int_0^{2\pi} r \, dt = 2\pi r$$

结果与几何公式完全吻合，验证了公式的正确性。

### 极坐标曲线的弧长公式

设曲线由极坐标方程 $r = r(\theta)$，$\theta \in [\theta_1, \theta_2]$ 给出，利用 $x = r\cos\theta$，$y = r\sin\theta$ 转化为参数方程，可推导得：

$$L = \int_{\theta_1}^{\theta_2} \sqrt{r^2 + \left(\frac{dr}{d\theta}\right)^2} \, d\theta$$

**示例：阿基米德螺线** $r = a\theta$，$\theta \in [0, 2\pi]$：代入得 $L = \int_0^{2\pi} \sqrt{a^2\theta^2 + a^2} \, d\theta = a\int_0^{2\pi}\sqrt{\theta^2+1}\,d\theta$，此积分需借助双曲代换才能精确求出。

### 微弧长元素 $ds$

三种坐标系下的弧长微元分别为：

- 直角坐标：$ds = \sqrt{1 + (y')^2} \, dx$
- 参数方程：$ds = \sqrt{(x')^2 + (y')^2} \, dt$
- 极坐标：$ds = \sqrt{r^2 + (r')^2} \, d\theta$

弧长微元 $ds$ 本身是一个重要工具：曲面积分、第一型曲线积分的被积元素都直接使用 $ds$，掌握它的三种形式对后续学习至关重要。

## 实际应用

**悬链线弧长计算：** 悬链线方程为 $y = a\cosh\left(\frac{x}{a}\right)$，其中 $a$ 为参数。其导数为 $y' = \sinh\left(\frac{x}{a}\right)$，利用恒等式 $1 + \sinh^2 u = \cosh^2 u$，弧长化简为：

$$L = \int_{-b}^{b} a\cosh\left(\frac{x}{a}\right) dx = 2a\sinh\left(\frac{b}{a}\right)$$

这一公式被用于电缆工程计算两塔之间导线的实际所需长度。

**星形线弧长：** 星形线参数方程为 $x = a\cos^3 t$，$y = a\sin^3 t$，$t \in [0, 2\pi]$。计算得 $x' = -3a\cos^2 t \sin t$，$y' = 3a\sin^2 t \cos t$，则：

$$\sqrt{(x')^2+(y')^2} = 3a|\sin t \cos t| = \frac{3a}{2}|\sin 2t|$$

利用对称性，$L = 4\int_0^{\pi/2} \frac{3a}{2}\sin 2t \, dt = 6a$，即星形线总弧长恰好为 $6a$，这是一个整洁的精确结果。

## 常见误区

**误区一：将弧长与弦长混淆。** 许多学生将曲线从 $A$ 到 $B$ 的弧长理解为端点间的直线距离（弦长）。实际上弦长是 $\sqrt{(x_B-x_A)^2+(y_B-y_A)^2}$，而弧长是对整条路径积分的结果，弧长 $\geq$ 弦长，当且仅当路径为直线时等号成立。

**误区二：忽略公式对导数连续性的要求。** 公式 $L = \int_a^b \sqrt{1+(f')^2}\,dx$ 要求 $f'$ 在 $[a,b]$ 上连续。若 $f'$ 在某点无界（如 $f(x) = x^{2/3}$ 在 $x=0$ 处），则须处理瑕积分，否则会直接得出错误的有限值。例如对 $y = x^{2/3}$ 在 $[-1,1]$ 上，$y' = \frac{2}{3}x^{-1/3}$ 在 $x=0$ 无定义，需将积分分裂为 $\int_{-1}^0 + \int_0^1$ 分别讨论收敛性。

**误区三：参数方程重复计数。** 若参数曲线在 $t \in [\alpha, \beta]$ 内自我相交或回绕，直接套用公式会将重叠路径重复计入。例如取 $x = \cos 2t$，$y = \sin 2t$，$t \in [0, 2\pi]$ 时会绕圆两圈，计算得 $L = 4\pi r$ 而非单圈的 $2\pi r$。使用公式前需确认参数区间与曲线一一对应。

## 知识关联

弧长公式的推导直接依赖**定积分**的极限定义和黎曼和，以及**微分中值定理**在折线近似中的应用。对**三角函数与双曲函数**的熟练掌握是化简被积函数 $\sqrt{1+(f')^2}$ 的实际操作基础——许多弧长积分需要三角代换或双曲代换才能求出原函数，否则只能得到数值结果。

弧长公式衍生出的弧长微元 $ds$ 是**第一型曲线积分**（对弧长的曲线积分）$\int_C f(x,y)\,ds$ 的积分元素，是将弧长思想推广到曲线上函数积分的关键桥梁。在微分几何中，弧长参数化是定义**曲率** $\kappa = \left|\frac{d\vec{T}}{ds}\right|$ 和**挠率**的自然参数选取方式，使得曲线的几何性质与参数化方式无关。