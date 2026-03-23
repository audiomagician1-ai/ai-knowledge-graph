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
---
# 弧长公式

## 概述

弧长公式是微积分中用于计算平面曲线实际长度的积分工具。与计算面积不同，弧长计算需要沿曲线方向累积无穷多个微小线段的长度，而非面积元素。对于一段光滑曲线，其弧长定义为对曲线进行无限细分后，各折线段长度之和在细分趋于无穷时的极限值。

弧长问题的严格数学化处理出现在17至18世纪。1659年，英国数学家尼尔（William Neile）首次精确求出了半立方抛物线 $y^2 = x^3$ 的弧长，这是已知最早的非平凡弧长计算结果之一。此后莱布尼茨和约翰·伯努利进一步发展了弧长积分的一般理论，将其纳入微积分框架。

弧长公式的重要性体现在其对光滑性条件的严格依赖上：若曲线的导数不连续或不存在，公式将失效，因此学习弧长公式同时意味着学习曲线光滑性的分析方法。

---

## 核心原理

### 显式曲线的弧长公式

对于由 $y = f(x)$ 定义的曲线，若 $f'(x)$ 在区间 $[a, b]$ 上连续，则弧长 $L$ 为：

$$L = \int_a^b \sqrt{1 + \left(\frac{dy}{dx}\right)^2} \, dx$$

其推导来源于弧长微元 $ds$：将曲线上相邻两点之间的线段长度用勾股定理表示为 $ds = \sqrt{(dx)^2 + (dy)^2}$，提取 $dx$ 后得到 $ds = \sqrt{1 + (f'(x))^2} \, dx$。对该微元在 $[a, b]$ 上积分即得公式。

类似地，若曲线以 $x = g(y)$ 的形式给出，则弧长公式变为：

$$L = \int_c^d \sqrt{1 + \left(\frac{dx}{dy}\right)^2} \, dy$$

### 参数曲线的弧长公式

当曲线由参数方程 $x = x(t)$，$y = y(t)$（$t \in [\alpha, \beta]$）给出，且 $x'(t)$、$y'(t)$ 均连续且不同时为零时，弧长公式为：

$$L = \int_\alpha^\beta \sqrt{\left(\frac{dx}{dt}\right)^2 + \left(\frac{dy}{dt}\right)^2} \, dt$$

此公式本质上是速度向量模长的积分：若将 $t$ 理解为时间，则 $\sqrt{(x'(t))^2 + (y'(t))^2}$ 就是运动质点在 $t$ 时刻的速率，弧长即为总路程。

以单位圆 $x = \cos t$，$y = \sin t$（$t \in [0, 2\pi]$）为例验证：

$$L = \int_0^{2\pi} \sqrt{(-\sin t)^2 + (\cos t)^2} \, dt = \int_0^{2\pi} 1 \, dt = 2\pi$$

结果与圆周长公式 $2\pi r$（$r=1$）完全吻合。

### 极坐标曲线的弧长公式

若曲线由极坐标 $r = r(\theta)$（$\theta \in [\theta_1, \theta_2]$）给出，利用 $x = r\cos\theta$，$y = r\sin\theta$ 代入参数公式，整理后得：

$$L = \int_{\theta_1}^{\theta_2} \sqrt{r^2 + \left(\frac{dr}{d\theta}\right)^2} \, d\theta$$

例如，阿基米德螺线 $r = a\theta$（$a > 0$）在 $[0, \Theta]$ 上的弧长为：

$$L = \int_0^\Theta \sqrt{a^2\theta^2 + a^2} \, d\theta = a\int_0^\Theta \sqrt{\theta^2 + 1} \, d\theta$$

此积分需用三角代换 $\theta = \tan u$ 求解，结果含有反双曲函数或对数表达式。

---

## 实际应用

**抛物线弧长计算**：求抛物线 $y = x^2$ 在 $[0, 1]$ 上的弧长。由公式：

$$L = \int_0^1 \sqrt{1 + (2x)^2} \, dx = \int_0^1 \sqrt{1 + 4x^2} \, dx$$

令 $2x = \tan\theta$，计算后得 $L = \frac{1}{4}\left[\sqrt{5} \cdot 2 + \ln(2 + \sqrt{5})\right] \approx 1.4789$，明显大于直线距离 $\sqrt{2} \approx 1.4142$，符合物理直觉。

**工程中的缆绳悬链线**：悬挂缆索的形状为悬链线 $y = a\cosh\left(\frac{x}{a}\right)$，其弧长公式计算结果直接决定施工时所需缆绳的实际用料长度，是桥梁工程设计的基础计算之一。

**计算机图形学**：参数曲线弧长公式用于在贝塞尔曲线上实现等速点采样，确保动画运动匀速而非参数均匀分布，这需要对弧长函数求数值积分（常用高斯积分法）再做反函数插值。

---

## 常见误区

**误区一：直接用坐标差代替弧长**。初学者常将曲线从 $(a, f(a))$ 到 $(b, f(b))$ 的弧长误算为 $\sqrt{(b-a)^2 + (f(b)-f(a))^2}$，即两端点连线的直线距离。这只是弦长而非弧长，仅当曲线趋于直线时两者才近似相等。弧长始终大于或等于对应的弦长，等号成立当且仅当曲线本身就是直线段。

**误区二：参数曲线弧长与参数区间无关的假设**。如果同一条曲线用不同参数化表示（如 $t$ 和 $2t$），积分区间会相应改变，但最终弧长结果不变。这一事实需要通过换元法验证，而不能凭直觉判断。忽视这一点常导致对公式中积分上下限设置的混淆。

**误区三：将弧长微元错误地写成 $\sqrt{1 + (f(x))^2} \, dx$**。弧长公式中的被积函数含 $f'(x)$（导函数）的平方，而非 $f(x)$（原函数）本身。这与计算旋转体表面积公式 $2\pi\int_a^b f(x)\sqrt{1+(f'(x))^2}\,dx$ 中两者都出现不同，初学者常将两个公式混淆。

---

## 知识关联

弧长公式建立在**定积分**的黎曼和极限定义之上，核心操作是将折线段长度（毕达哥拉斯定理的应用）累积为积分。没有对积分极限过程的理解，弧长微元 $ds$ 的推导就无从建立。

弧长公式是计算**旋转体表面积**的直接前驱：将平面曲线绕坐标轴旋转一周，其表面积公式 $S = 2\pi\int_a^b f(x)\sqrt{1+(f'(x))^2}\,dx$ 本质上是弧长微元 $ds$ 乘以旋转半径 $2\pi f(x)$ 的积分。此外，弧长函数 $s(t) = \int_\alpha^t \sqrt{(x'(u))^2 + (y'(u))^2}\,du$ 直接引出**曲率**的定义：曲率 $\kappa = \left|\frac{d\vec{T}}{ds}\right|$，即单位切向量对弧长的变化率，是微分几何的入门概念。
