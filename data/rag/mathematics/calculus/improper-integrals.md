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
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 广义积分

## 概述

广义积分（Improper Integral）是将黎曼定积分扩展至**无穷区间**或**被积函数存在无穷间断点**两种情形的积分理论。标准黎曼积分要求积分区间有限且被积函数有界，而广义积分突破了这两个限制，允许积分上下限趋向无穷，或允许函数在某点取值趋向正负无穷（瑕点）。

广义积分的系统研究与19世纪黎曼、柯西的工作密切相关。柯西（Augustin-Louis Cauchy）于1820年代明确给出了广义积分收敛的极限定义框架，将原本模糊的"无穷面积"问题变为可严格讨论的数学命题。这一理论的成熟直接支撑了后续傅里叶变换、拉普拉斯变换等工程与物理工具的数学合法性——例如 $\int_0^\infty e^{-st}f(t)\,dt$ 这一拉普拉斯核心积分本身就是一个关于无穷区间的广义积分。

广义积分与普通定积分的本质区别在于：它的值是通过**极限过程**定义的，因此可能收敛，也可能发散。即使形式上写出积分符号，结果也未必存在，必须经过收敛性判断才能使用。

---

## 核心原理

### 无穷区间上的广义积分

设 $f(x)$ 在 $[a, +\infty)$ 上连续，定义：

$$\int_a^{+\infty} f(x)\,dx = \lim_{b \to +\infty} \int_a^b f(x)\,dx$$

若该极限存在且有限，则称积分**收敛**；极限不存在或为无穷大，则称**发散**。类似地可定义 $\int_{-\infty}^b$，以及双侧无穷积分 $\int_{-\infty}^{+\infty} f(x)\,dx$，后者需拆成两个单侧极限**分别收敛**才算整体收敛。

**典型案例**：$\int_1^{+\infty} \frac{1}{x^p}\,dx$ 的收敛性完全由参数 $p$ 决定——当 $p > 1$ 时收敛，结果为 $\frac{1}{p-1}$；当 $p \leq 1$ 时发散。这一 $p$ 级数判别法是后续比较判别法的基准。

### 瑕积分（无界函数的广义积分）

若 $f(x)$ 在 $x = a$ 处趋向无穷（称 $a$ 为**瑕点**），而在 $(a, b]$ 上连续，则定义：

$$\int_a^b f(x)\,dx = \lim_{\varepsilon \to 0^+} \int_{a+\varepsilon}^b f(x)\,dx$$

同理，若瑕点在区间内部 $c \in (a,b)$，必须拆分为 $\int_a^c$ 和 $\int_c^b$ 两段，**两段均收敛**方为整体收敛。

**典型案例**：$\int_0^1 \frac{1}{x^q}\,dx$，当 $q < 1$ 时收敛，值为 $\frac{1}{1-q}$；当 $q \geq 1$ 时发散。注意 $q=1$ 时 $\int_0^1 \frac{1}{x}\,dx = \lim_{\varepsilon\to 0^+}[-\ln\varepsilon] = +\infty$，发散。

### 收敛性判别法

**比较判别法**：若 $0 \leq f(x) \leq g(x)$，则 $\int_a^{+\infty} g(x)\,dx$ 收敛可推出 $\int_a^{+\infty} f(x)\,dx$ 收敛；$\int_a^{+\infty} f(x)\,dx$ 发散可推出 $\int_a^{+\infty} g(x)\,dx$ 发散。

**极限比较判别法**：若 $f(x), g(x) \geq 0$，且

$$\lim_{x \to +\infty} \frac{f(x)}{g(x)} = L \in (0, +\infty)$$

则两者有相同的收敛散性。这在实际判断中往往比直接比较更易操作，例如判断 $\int_1^{+\infty} \frac{\sin^2 x + 1}{x^2}\,dx$ 收敛，可令 $g(x) = \frac{2}{x^2}$，极限为常数，而 $\int_1^{+\infty}\frac{1}{x^2}dx$ 收敛（$p=2>1$），故原积分收敛。

**绝对收敛与条件收敛**：若 $\int_a^{+\infty}|f(x)|\,dx$ 收敛，则称原积分**绝对收敛**，它必然收敛。若原积分收敛但 $\int|f|$ 发散，则称**条件收敛**。典型例子：$\int_1^{+\infty}\frac{\sin x}{x}\,dx$ 条件收敛（可用狄利克雷判别法证明），而 $\int_1^{+\infty}\frac{|\sin x|}{x}\,dx$ 发散。

---

## 实际应用

**概率论中的正态分布归一化**：高斯积分 $\int_{-\infty}^{+\infty} e^{-x^2}\,dx = \sqrt{\pi}$ 是广义积分中最著名的结果之一，其收敛性源于 $e^{-x^2}$ 的衰减速度远快于任意幂函数，可用比较法对照 $e^{-x}$ 证明。正态分布 $\frac{1}{\sqrt{2\pi}\sigma}e^{-\frac{(x-\mu)^2}{2\sigma^2}}$ 在 $(-\infty,+\infty)$ 上积分等于1，正是依赖此广义积分。

**伽马函数**：$\Gamma(n) = \int_0^{+\infty} x^{n-1}e^{-x}\,dx$ 是定义在正实数上的广义积分（兼具无穷上限和 $x=0$ 处的潜在瑕点），满足递推关系 $\Gamma(n+1) = n\Gamma(n)$，且 $\Gamma(n) = (n-1)!$（$n$ 为正整数）。验证其收敛性需在 $[0,1]$ 和 $[1,+\infty)$ 两段分别处理。

**物理中的引力势能**：将质点从地面移至无穷远所做的功 $W = \int_R^{+\infty} \frac{GMm}{r^2}\,dr$，由于 $p=2>1$，该积分收敛，结果为 $\frac{GMm}{R}$，这是宇宙速度计算的数学基础。

---

## 常见误区

**误区一：混淆双侧无穷积分与柯西主值**

许多学生将 $\int_{-\infty}^{+\infty} f(x)\,dx$ 理解为 $\lim_{b\to+\infty}\int_{-b}^{b}f(x)\,dx$，后者称为**柯西主值**，两者不等价。例如 $\int_{-\infty}^{+\infty} x\,dx$ 按定义须分拆为 $\int_{-\infty}^0 x\,dx + \int_0^{+\infty}x\,dx$，两段均发散，故整体发散；但柯西主值 $\lim_{b\to+\infty}\int_{-b}^b x\,dx = 0$，因奇函数对称区间积分为零。两者不能混用。

**误区二：瑕点未被识别导致计算错误**

对 $\int_{-1}^{1}\frac{1}{x^2}\,dx$，若直接套用牛顿-莱布尼茨公式，得 $\left[-\frac{1}{x}\right]_{-1}^{1} = -1-1 = -2$，这是错误的。$x=0$ 是瑕点，正确做法是拆分后各取极限，两段均为 $+\infty$，积分**发散**。被积函数在区间内无界时必须警觉。

**误区三：收敛与绝对收敛混淆**

看到 $\int_1^{+\infty}f(x)\,dx$ 的被积函数趋向于0，就认为积分收敛——这是错误的。$f(x) = \frac{1}{x}$ 趋向0但 $\int_1^{+\infty}\frac{1}{x}\,dx$ 发散（$p=1$，临界发散）。收敛性需要函数趋向零的**速度**足够快，$p>1$ 才保证幂函数型积分收敛。

---

## 知识关联

**前置知识**：广义积分的计算直接依赖定积分的牛顿-莱布尼茨公式和换元、分部积分等技巧——例如计算 $\int_0^{+\infty}e^{-x}\sin x\,dx$ 需要两次分部积分，再对极限 $\lim_{b\to+\infty}e^{-b}(\sin b + \cos b)=0$ 进行分析。若对定积分的计算技巧不熟练，广义积分的计算会寸步难行。

**后续衔接——拉普拉斯变换**：拉普拉斯变换定义为 $\mathcal{L}\{f(t)\}(s) = \int_0^{+\infty}e^{-st}f(t)\,dt$，其本质是含参数 $s$ 的广