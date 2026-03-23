---
id: "improper-integrals"
concept: "广义积分"
domain: "mathematics"
subdomain: "calculus"
subdomain_name: "微积分"
difficulty: 7
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "pending-rescore"
quality_score: 40.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.407
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 广义积分

## 概述

广义积分（也称反常积分）是将黎曼定积分的概念延伸到**无穷积分区间**或**被积函数在区间内有无界点**的情形。标准黎曼积分要求积分区间 $[a,b]$ 有限且被积函数在其上有界，当这两个条件之一不满足时，就必须借助极限来定义积分的值，这便是广义积分的本质。

广义积分的系统研究可追溯至19世纪，柯西（Cauchy）在1820年代正式引入了用极限定义无界积分的方法。欧拉更早（1730年代）在计算Gamma函数 $\Gamma(n) = \int_0^{+\infty} t^{n-1}e^{-t}\,dt$ 时已隐式使用了这一思想。这一积分在概率论、物理和工程中极为常见——例如正态分布的归一化常数依赖于 $\int_{-\infty}^{+\infty} e^{-x^2}\,dx = \sqrt{\pi}$，这是一个典型的无穷区间广义积分结果。

广义积分的收敛与发散直接决定诸多重要公式能否成立。$\int_1^{+\infty} \frac{1}{x^p}\,dx$ 当 $p>1$ 时收敛、$p\leq 1$ 时发散这一结论，是数学分析和级数理论的基础判定工具。

---

## 核心原理

### 无穷区间上的广义积分

设 $f(x)$ 在 $[a, +\infty)$ 上连续，定义：

$$\int_a^{+\infty} f(x)\,dx = \lim_{b \to +\infty} \int_a^b f(x)\,dx$$

若极限存在（有限值），称该广义积分**收敛**；若极限不存在或为无穷，称其**发散**。类似地可定义 $\int_{-\infty}^b f(x)\,dx$ 以及双侧无穷积分 $\int_{-\infty}^{+\infty} f(x)\,dx$（后者须分拆为两个单侧积分，**两者均收敛**才算整体收敛）。

经典例子：$\int_1^{+\infty} \frac{1}{x^p}\,dx$，当 $p \neq 1$ 时计算得 $\frac{1}{p-1}$（$p>1$）或发散（$p \leq 1$）；$p=1$ 时 $\int_1^{+\infty}\frac{1}{x}\,dx = \lim_{b\to+\infty}\ln b = +\infty$，发散。

### 瑕积分（无界函数的广义积分）

若 $f(x)$ 在 $x = a$（瑕点）附近无界，但在 $(a, b]$ 上连续，定义：

$$\int_a^b f(x)\,dx = \lim_{\varepsilon \to 0^+} \int_{a+\varepsilon}^b f(x)\,dx$$

典型例子：$\int_0^1 \frac{1}{x^q}\,dx$，当 $q<1$ 时收敛于 $\frac{1}{1-q}$；当 $q \geq 1$ 时发散。注意**瑕点可以在积分区间内部**，此时须在瑕点处拆分，分别求极限，两者均收敛方可相加。

### 收敛判定法则

**比较判别法**：若 $0 \leq f(x) \leq g(x)$，且 $\int_a^{+\infty} g(x)\,dx$ 收敛，则 $\int_a^{+\infty} f(x)\,dx$ 收敛；反之若小函数的积分发散，则大函数也发散。

**极限比较判别法**：若 $f(x),g(x) \geq 0$，且 $\lim_{x\to+\infty}\frac{f(x)}{g(x)} = L$（$0 < L < +\infty$），则两个积分同敛散。这比直接比较更灵活，常取 $g(x)=\frac{1}{x^p}$ 作为参照函数。

**绝对收敛与条件收敛**：若 $\int_a^{+\infty}|f(x)|\,dx$ 收敛，称原积分**绝对收敛**；若 $\int_a^{+\infty}f(x)\,dx$ 收敛但 $\int_a^{+\infty}|f(x)|\,dx$ 发散，称**条件收敛**。绝对收敛必收敛，反之不然。例如 $\int_1^{+\infty}\frac{\sin x}{x}\,dx$ 条件收敛但非绝对收敛。

---

## 实际应用

**Gamma函数的定义**直接依赖广义积分：$\Gamma(\alpha) = \int_0^{+\infty} x^{\alpha-1}e^{-x}\,dx$，其中 $x=0$ 处可能为瑕点（当 $0 < \alpha < 1$），$+\infty$ 处为无穷积分，需验证两端均收敛才能使用。利用 $e^{-x}$ 衰减极快，以极限比较法可证明对所有 $\alpha > 0$ 该积分收敛。

**概率密度函数的归一化**：标准正态分布的归一化条件 $\int_{-\infty}^{+\infty}\frac{1}{\sqrt{2\pi}}e^{-x^2/2}\,dx = 1$ 中，核心计算 $\int_{-\infty}^{+\infty}e^{-x^2}\,dx = \sqrt{\pi}$ 通过极坐标变换将双重广义积分化为有限值，展示了广义积分在统计物理中的关键角色。

**拉普拉斯变换**的定义式 $\mathcal{L}\{f(t)\}(s) = \int_0^{+\infty} f(t)e^{-st}\,dt$ 本质上是一个关于参数 $s$ 的含参广义积分，其收敛条件（$s$ 需大于 $f(t)$ 的增长指数）正是广义积分收敛判定的直接运用。

---

## 常见误区

**误区一：将发散积分当作"等于无穷"来计算**。$\int_{-\infty}^{+\infty} x\,dx$ 不等于 $0$，虽然被积函数是奇函数，但该积分因两侧极限 $\lim_{b\to+\infty}\int_{-b}^{b}x\,dx = 0$（柯西主值）与真正的广义积分定义不同——正确定义要求 $\int_0^{+\infty}x\,dx$ 和 $\int_{-\infty}^0 x\,dx$ 分别收敛，两者均为 $+\infty$ 或 $-\infty$，故整体发散。不可用对称区间抵消代替收敛判断。

**误区二：忽视瑕点导致错误计算**。计算 $\int_{-1}^{1}\frac{1}{x^2}\,dx$ 时，若直接套用牛顿-莱布尼茨公式得 $\left[-\frac{1}{x}\right]_{-1}^{1} = -2$，这是错误的。$x=0$ 是瑕点，必须拆分为 $\int_{-1}^0$ 与 $\int_0^1$ 两个广义积分分别求极限，结果两者均为 $+\infty$，整体发散，而非 $-2$。

**误区三：混淆条件收敛与绝对收敛的判定**。对非负函数，比较判别法直接适用；但对振荡函数如 $\frac{\sin x}{x}$，即使 $\int_1^{+\infty}\frac{|\sin x|}{x}\,dx = +\infty$（发散），$\int_1^{+\infty}\frac{\sin x}{x}\,dx$ 仍可收敛（条件收敛）。此时需借助**狄利克雷判别法**：若 $g(x)$ 单调趋于零，$F(x)=\int_a^x f(t)\,dt$ 有界，则 $\int_a^{+\infty}f(x)g(x)\,dx$ 收敛。

---

## 知识关联

广义积分以**定积分**为前提——牛顿-莱布尼茨公式、换元法、分部积分法在广义积分中同样适用，只是最终需补上极限过程。例如对瑕积分 $\int_0^1 \ln x\,dx$，先用分部积分得 $[x\ln x - x]_\varepsilon^1$，再令 $\varepsilon \to 0^+$ 利用 $\lim_{\varepsilon\to 0^+}\varepsilon\ln\varepsilon = 0$ 得结果为 $-1$。

广义积分是**拉普拉斯变换**的直接基础。拉普拉斯变换 $\mathcal{L}\{f\}(s)$ 要求对每个 $s$ 值判断含参广义积分是否收敛，收敛域的确定依赖于广义积分的比较判别和绝对收敛理论。掌握 $\int_0^{+\infty}e^{-st}t^n\,dt = \frac{n!}{s^{n+1}}$（$s>0$）这类标准结果，需要对广义积分的计算技巧（分部积分+递推）相当熟练。此外，广义积分也为**级数收敛**的积分判别法提供工具：$\sum_{n=1}^\infty f(n)$ 与 $\int_1^{+\infty}f(x)\,dx$ 同敛散（当
