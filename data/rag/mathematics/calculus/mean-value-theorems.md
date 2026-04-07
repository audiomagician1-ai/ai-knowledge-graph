---
id: "mean-value-theorems"
concept: "中值定理"
domain: "mathematics"
subdomain: "calculus"
subdomain_name: "微积分"
difficulty: 7
is_milestone: false
tags: ["里程碑"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 中值定理

## 概述

中值定理是微积分中描述函数在某区间内导数与函数值变化关系的一组定理，其核心思想是：在满足连续性和可微性条件的函数上，区间内部必然存在某点，使该点的导数等于某种意义上的"平均变化率"。这类定理将函数的整体行为（区间端点的函数值）与局部行为（某内部点的瞬时变化率）紧密联系起来。

历史上，Rolle定理由法国数学家Michel Rolle于1691年首次严格陈述，这比微积分被完整系统化还早约一个世纪。Lagrange中值定理由Joseph-Louis Lagrange在18世纪末建立，是微积分分析学的基石之一。Cauchy中值定理则是Augustin-Louis Cauchy在19世纪初对Lagrange定理的推广，为L'Hôpital法则提供了严格的理论依据。

中值定理的重要性在于它是证明许多微积分核心结论的桥梁：导数单调性判别法、泰勒公式余项估计、积分中值定理等均以此为基础。没有中值定理，就无法从"某点导数为零"推断出函数的全局极值行为。

## 核心原理

### Rolle定理

**条件**：设函数 $f(x)$ 在闭区间 $[a, b]$ 上连续，在开区间 $(a, b)$ 内可导，且 $f(a) = f(b)$。

**结论**：则在 $(a, b)$ 内至少存在一点 $\xi$，使得 $f'(\xi) = 0$。

Rolle定理的证明依赖闭区间上连续函数必能取到最大值和最小值（有界闭区间上连续函数的最值定理）。若最大值和最小值均在端点取得，则由 $f(a) = f(b)$ 可知函数为常数，导数恒为零；否则极值点在内部，由Fermat引理得该点导数为零。几何直观是：两端等高的光滑曲线，其上必有水平切线。

### Lagrange中值定理

**条件**：设 $f(x)$ 在 $[a, b]$ 上连续，在 $(a, b)$ 内可导。

**结论**：至少存在一点 $\xi \in (a, b)$，使得：

$$f(b) - f(a) = f'(\xi)(b - a)$$

等价形式为 $f'(\xi) = \dfrac{f(b) - f(a)}{b - a}$，即内部某点的瞬时变化率等于区间两端的平均变化率。

**证明思路**：构造辅助函数 $\varphi(x) = f(x) - f(a) - \dfrac{f(b)-f(a)}{b-a}(x-a)$，可验证 $\varphi(a) = \varphi(b) = 0$，对 $\varphi$ 应用Rolle定理即得 $\xi$ 的存在性。

Lagrange中值定理的一个重要推论：若函数在某区间上导数恒为零，则该函数在该区间上为常数。这看似显然，但严格证明必须使用Lagrange定理，不能仅凭直觉。

### Cauchy中值定理

**条件**：设 $f(x)$、$g(x)$ 均在 $[a, b]$ 上连续，在 $(a, b)$ 内可导，且 $g'(x) \neq 0$（保证 $g(b) \neq g(a)$ 且分母不为零）。

**结论**：至少存在 $\xi \in (a, b)$，使得：

$$\frac{f(b) - f(a)}{g(b) - g(a)} = \frac{f'(\xi)}{g'(\xi)}$$

当 $g(x) = x$ 时，Cauchy定理退化为Lagrange定理。Cauchy定理的参数化几何意义是：将曲线看作参数方程 $(g(t), f(t))$，则曲线上某点的切线斜率等于连接两端点割线的斜率。

**L'Hôpital法则的来源**：$\dfrac{0}{0}$ 型极限 $\lim_{x \to a} \dfrac{f(x)}{g(x)}$，其中 $f(a) = g(a) = 0$，利用Cauchy定理可将其转化为 $\lim_{\xi \to a} \dfrac{f'(\xi)}{g'(\xi)}$，从而实现求导代换。这是Cauchy定理最著名的直接应用。

## 实际应用

**估计函数值误差**：利用 $|f(b) - f(a)| = |f'(\xi)| \cdot |b-a| \leq M|b-a|$（其中 $M$ 是 $|f'|$ 的上界），可估计 $|\sin(1.01) - \sin(1)| \leq 1 \times 0.01 = 0.01$，因为 $|\cos x| \leq 1$。

**证明不等式**：证明 $|\sin a - \sin b| \leq |a - b|$ 对所有实数 $a, b$ 成立，只需对 $f(x) = \sin x$ 在 $[a, b]$ 上应用Lagrange定理，得 $|\sin a - \sin b| = |\cos \xi| \cdot |a - b| \leq |a - b|$。

**方程根的存在性与唯一性**：方程 $f(x) = 0$ 在某区间上的唯一性证明常结合Rolle定理反证：若有两个根 $x_1 < x_2$，则 $f(x_1) = f(x_2) = 0$，由Rolle定理 $\exists \xi \in (x_1, x_2)$ 使 $f'(\xi) = 0$，若能证明 $f'(x) \neq 0$ 则矛盾，从而唯一性得证。

**单调性的严格证明**：$f'(x) > 0$ 在 $(a,b)$ 上成立 $\Rightarrow$ $f$ 在 $[a,b]$ 上严格单调递增，证明需对任意 $x_1 < x_2$ 用Lagrange定理写出 $f(x_2) - f(x_1) = f'(\xi)(x_2 - x_1) > 0$。

## 常见误区

**误区一：混淆三个定理的条件层次**  
Rolle定理要求额外条件 $f(a) = f(b)$，是Lagrange定理的特殊情形；Cauchy定理涉及两个函数，是Lagrange的推广。学生常误以为Cauchy定理的 $\xi$ 可以对 $f$ 和 $g$ 分别取不同的点，但实际上定理保证的是**同一个** $\xi$ 同时出现在分子和分母的导数中，这正是它强于分别应用Lagrange定理的关键所在。

**误区二：认为 $\xi$ 的位置可以确定**  
中值定理只保证 $\xi$ 的**存在性**，不给出 $\xi$ 的具体位置。例如对 $f(x) = x^2$ 在 $[0, 2]$ 上，$\xi = \dfrac{0+2}{2} = 1$（恰好是中点），但这是该函数的巧合，一般函数的 $\xi$ 不在中点。对 $f(x) = x^3$ 在 $[-1, 1]$ 上，$\xi = \pm\dfrac{1}{\sqrt{3}} \approx \pm 0.577$，并非端点的算术平均值。

**误区三：忽视"可导"和"连续"条件缺一不可**  
在 $[0,1]$ 上取 $f(x) = |x - 0.5|$，该函数处处连续但在 $x = 0.5$ 处不可导，$f(0) = f(1) = 0.5$，但内部不存在导数为零的点（导数只取 $\pm 1$），Rolle定理失效。另外，若函数在端点不连续（仅半开区间连续），也无法保证结论成立，如 $f(x) = 1/x$ 在 $(0,1]$ 上。

## 知识关联

**前驱概念**：Rolle定理的证明直接依赖**Fermat引理**（可导函数极值点处导数为零）和**连续函数最值定理**（$[a,b]$上连续函数必取最大最小值）；Lagrange定理的辅助函数构造则需要熟练掌握**导数的线性性质**。若学生对"连续但不可导"的函数（如 $|x|$）概念模糊，将难以判断定理条件是否满足。

**后续展开**：中值定理直接支撑了**Taylor公式**的余项估计（Lagrange余项形式 $\dfrac{f^{(n+1)}(\xi)}{(n+1)!}(x-a)^{n+1}$ 本质是高阶中值定理的应用）、**积分中值定理**（$\int_a^b f(x)\,dx = f(\xi)(b-a)$）以及**L'Hôpital法则**的严格推导。掌握三个中值定理的证明结构（特别是辅助函数的构造技巧），对后续学习单调性、凹凸性分析及极值判断至关重要。