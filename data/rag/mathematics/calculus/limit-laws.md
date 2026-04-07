---
id: "limit-laws"
concept: "极限运算法则"
domain: "mathematics"
subdomain: "calculus"
subdomain_name: "微积分"
difficulty: 5
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 极限运算法则

## 概述

极限运算法则是一套将复杂极限计算分解为若干简单极限组合的规则体系。其核心思想是：若函数 $f(x)$ 和 $g(x)$ 在 $x \to a$ 时极限分别存在且有限，则两者之间的四则运算的极限，等于各自极限进行相同四则运算的结果。这一规则在17世纪随牛顿和莱布尼茨建立微积分体系时已被隐式使用，而严格的 $\varepsilon$-$\delta$ 语言表述则由柯西（Augustin-Louis Cauchy）在19世纪初的《分析教程》（1821年）中正式确立。

极限运算法则的重要性体现在它将"逐点验证极限存在性"转变为"代数组合运算"。没有这套法则，每计算一个多项式或有理函数的极限，都必须从定义出发，用 $\varepsilon$-$\delta$ 论证，极为繁琐。有了这套法则，计算 $\lim_{x \to 2}(3x^2 + 5x - 1)$ 只需逐项拆分、代入即可得到 $3(4)+5(2)-1=21$，省去大量重复论证。

## 核心原理

### 四则运算法则

设 $\lim_{x \to a} f(x) = A$，$\lim_{x \to a} g(x) = B$（$A$、$B$ 均为有限实数），则以下四条法则成立：

- **加减法则**：$\lim_{x \to a}[f(x) \pm g(x)] = A \pm B$
- **乘法法则**：$\lim_{x \to a}[f(x) \cdot g(x)] = A \cdot B$
- **除法法则**：$\lim_{x \to a}\dfrac{f(x)}{g(x)} = \dfrac{A}{B}$，要求 $B \neq 0$
- **常数倍法则**：$\lim_{x \to a}[c \cdot f(x)] = c \cdot A$，$c$ 为任意常数

乘法法则可推广至有限个函数之积：$\lim_{x \to a}[f_1(x) \cdot f_2(x) \cdots f_n(x)] = A_1 \cdot A_2 \cdots A_n$。特别地，$\lim_{x \to a}[f(x)]^n = A^n$（$n$ 为正整数）。

四则运算法则的前提条件至关重要：**两个极限必须同时存在且有限**。若其中一个极限不存在（如趋向无穷），则法则不能直接套用。例如 $\lim_{x \to 0}\left(x \cdot \frac{1}{x}\right)$ 不能分裂为 $\lim_{x \to 0}x \cdot \lim_{x \to 0}\frac{1}{x}$，因为后者不存在（为 $\infty$），但整体极限等于1。

### 夹逼定理（Squeeze Theorem）

夹逼定理（又称"三明治定理"）处理的是无法用代数法则直接计算的极限。定理表述如下：

> 若在点 $a$ 的某去心邻域内，$g(x) \leq f(x) \leq h(x)$，且 $\lim_{x \to a}g(x) = \lim_{x \to a}h(x) = L$，则 $\lim_{x \to a}f(x) = L$。

夹逼定理最经典的应用是证明 $\lim_{x \to 0}\frac{\sin x}{x} = 1$。利用单位圆面积比较可建立不等式：

$$\cos x \leq \frac{\sin x}{x} \leq 1 \quad (0 < |x| < \frac{\pi}{2})$$

由于 $\lim_{x \to 0}\cos x = 1$ 且 $\lim_{x \to 0}1 = 1$，由夹逼定理得出结论。这一极限是证明 $(\sin x)' = \cos x$ 的基石。

另一典型案例是 $\lim_{n \to \infty}\sqrt[n]{n} = 1$。令 $\sqrt[n]{n} = 1 + \alpha_n$（$\alpha_n \geq 0$），展开 $n = (1+\alpha_n)^n \geq \frac{n(n-1)}{2}\alpha_n^2$，得 $0 \leq \alpha_n \leq \sqrt{\frac{2}{n-1}}$，再用夹逼定理即得。

### 复合函数极限法则

若 $\lim_{x \to a} g(x) = u_0$，且 $\lim_{u \to u_0} f(u) = L$，并在 $a$ 的去心邻域内 $g(x) \neq u_0$，则：

$$\lim_{x \to a} f(g(x)) = L = f(u_0)$$

此法则是将极限与连续性联系的桥梁。例如，$\lim_{x \to 0}\sin(x^2)$：令 $u = x^2$，$x \to 0$ 时 $u \to 0$，故极限为 $\sin(0) = 0$。

## 实际应用

**有理函数分母不为零时**，直接代入即可：$\lim_{x \to 3}\frac{x^2 - 9}{x - 3}$ 的分母在 $x=3$ 处为零，不可直接用除法法则，需先因式分解为 $x+3$，再令 $x \to 3$ 得6。

**利用第一重要极限** $\lim_{x \to 0}\frac{\sin x}{x} = 1$ 衍生计算：

$$\lim_{x \to 0}\frac{\tan x}{x} = \lim_{x \to 0}\frac{\sin x}{x} \cdot \frac{1}{\cos x} = 1 \cdot 1 = 1$$

此处同时使用了乘法法则和复合函数极限法则。

**无穷小乘有界量为无穷小**也是夹逼定理的应用：$\lim_{x \to 0}x\sin\frac{1}{x}$，由 $|x\sin\frac{1}{x}| \leq |x|$ 和夹逼定理得极限为0。

## 常见误区

**误区一：0/0型直接用除法法则**。除法法则要求分母极限不为零。当 $\lim g(x) = 0$ 时，形如 $\frac{f(x)}{g(x)}$ 的极限属于不定式，必须先通过因式分解、有理化、等价无穷小替换或洛必达法则处理，不能套用 $A/B$ 的公式。许多学生看到分式就直接代入，在 $x \to 1$ 时计算 $\frac{x^2-1}{x-1}$ 得 $\frac{0}{0}$，再错误地声称"极限不存在"。

**误区二：将夹逼定理误用于不等式方向相反的情形**。夹逼定理要求被夹函数 $f(x)$ 始终介于 $g(x)$ 和 $h(x)$ 之间。若不等式在某些点不成立，定理失效。例如，$x^2\sin\frac{1}{x}$ 当 $x \to 0$ 时需用 $-x^2 \leq x^2\sin\frac{1}{x} \leq x^2$ 来夹，两边界极限均为0，结论成立；但若错误地写成 $0 \leq x^2\sin\frac{1}{x}$（当 $\sin\frac{1}{x} < 0$ 时不成立），则夹逼条件不满足。

**误区三：极限运算法则适用于无穷大极限**。$\lim_{x \to +\infty}(x^2 - x)$ 不能拆分为 $\lim x^2 - \lim x = \infty - \infty$，因为 $\infty - \infty$ 是不定式。正确做法是提取公因式：$x^2-x = x(x-1) \to +\infty$。加减法则仅在两个极限均为有限值时合法。

## 知识关联

极限运算法则直接依赖于**极限的 $\varepsilon$-$\delta$ 定义**：四则运算法则的证明本质上是将 $|f(x) \cdot g(x) - AB|$ 用三角不等式拆分，并利用两个极限定义中的 $\varepsilon_1$ 和 $\varepsilon_2$ 构造合适的界。

掌握极限运算法则后，可直接推导出**连续性**的代数性质——连续函数的四则运算仍连续、复合仍连续，其证明完全依赖于上述极限法则。而当四则运算法则和代入法均失效（即遭遇 $0/0$、$\infty/\infty$ 等不定式）时，就需要引入**洛必达法则**，通过对分子分母分别求导来绕过不定式障碍。因此，极限运算法则既是连续性理论的代数工具，也在遭遇边界情形时自然引出洛必达法则的必要性。