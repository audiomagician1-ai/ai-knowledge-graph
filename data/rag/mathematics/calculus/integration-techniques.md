---
id: "integration-techniques"
concept: "积分技巧"
domain: "mathematics"
subdomain: "calculus"
subdomain_name: "微积分"
difficulty: 6
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 82.9
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

# 积分技巧

## 概述

积分技巧是一套将看似无法直接计算的不定积分转化为可求解形式的方法体系，其中最核心的两种方法是**换元积分法**（substitution）和**分部积分法**（integration by parts）。这两种方法分别对应链式法则和乘积法则的"逆运算"——换元法逆用链式法则，分部积分法逆用乘积求导法则。

换元积分法最早由莱布尼茨（Leibniz）在17世纪末的微积分符号体系中隐含提出，而分部积分公式则在18世纪由布鲁克·泰勒（Brook Taylor）等人系统整理。这两种方法至今仍是处理初等函数积分的主要工具，覆盖了大学微积分课程中约80%的手算积分题型。

掌握这两种技巧的意义在于：初等函数的导数总是初等函数，但初等函数的积分未必是初等函数（如 $e^{-x^2}$ 无初等原函数）。因此，能否识别并选用正确的积分方法，直接决定了一道题目能否被精确求解。

---

## 核心原理

### 换元积分法（第一类换元法 / 凑微分法）

第一类换元法的核心公式为：

$$\int f[\varphi(x)]\,\varphi'(x)\,dx = \int f(u)\,du \Big|_{u=\varphi(x)} = F[\varphi(x)] + C$$

其中 $u = \varphi(x)$ 是可微函数，$F'(u) = f(u)$。操作的本质是在被积式中识别出 $\varphi'(x)\,dx = d[\varphi(x)]$，即"凑微分"。

典型例子：求 $\int \sin(3x)\,dx$。令 $u = 3x$，则 $du = 3\,dx$，原式变为 $\frac{1}{3}\int \sin u\,du = -\frac{1}{3}\cos(3x) + C$。凑微分的关键在于被积函数中必须存在 $\varphi'(x)$ 因子（或可凑出该因子）。

**第二类换元法**则是令 $x = \psi(t)$（要求 $\psi$ 单调可微），将原积分变量替换为 $t$，适用于含 $\sqrt{a^2 - x^2}$、$\sqrt{x^2 \pm a^2}$ 等根式的被积函数。例如处理 $\sqrt{a^2 - x^2}$ 时令 $x = a\sin t$，利用三角恒等式 $1 - \sin^2 t = \cos^2 t$ 消去根号。

### 分部积分法

分部积分公式来源于乘积法则 $(uv)' = u'v + uv'$，两端积分整理后得：

$$\int u\,dv = uv - \int v\,du$$

其中 $u = u(x)$，$v = v(x)$ 均为 $x$ 的可微函数。方法的关键在于**如何选取 $u$ 和 $dv$**：选取原则通常遵循 **LIATE 优先级**（对数 Logarithm → 反三角 Inverse trig → 代数 Algebraic → 三角 Trigonometric → 指数 Exponential），将排名靠前的函数选作 $u$，剩余部分选作 $dv$。

典型例子：求 $\int x e^x\,dx$。按 LIATE，$x$（代数）优于 $e^x$（指数），取 $u = x$，$dv = e^x\,dx$，则 $du = dx$，$v = e^x$，代入公式得 $xe^x - \int e^x\,dx = xe^x - e^x + C = (x-1)e^x + C$。

**循环积分**是分部积分的特殊情形：对 $\int e^x \sin x\,dx$ 两次分部积分后，右侧会重新出现原积分 $I$，此时方程两端移项解出 $I = \frac{e^x(\sin x - \cos x)}{2} + C$，而非无限递归。

### 方法选择的判断逻辑

- 被积函数含复合结构（如 $f(ax+b)$、$f(\ln x)$）→ 优先换元法；
- 被积函数为两类不同函数的乘积（如多项式乘指数、对数乘代数式）→ 优先分部积分；
- 含三角函数的有理式（如 $\int \frac{dx}{1+\sin x}$）→ 考虑万能代换 $t = \tan\frac{x}{2}$，此时 $\sin x = \frac{2t}{1+t^2}$，$dx = \frac{2}{1+t^2}dt$。

---

## 实际应用

**工程信号处理中的拉普拉斯变换**大量使用分部积分。例如计算 $\mathcal{L}\{t^n\} = \int_0^\infty t^n e^{-st}\,dt$ 时，反复对 $t^n$ 部分分部积分，每次降低指数的幂次，最终得到递推公式 $\mathcal{L}\{t^n\} = \frac{n!}{s^{n+1}}$（$n$ 为正整数）。

**概率统计**中计算正态分布的矩时，需要求 $\int_{-\infty}^{+\infty} x^2 e^{-x^2/2}\,dx$。先用第一类换元法令 $u = x^2/2$ 处理指数部分，再结合分部积分降幂，最终结果为 $\sqrt{2\pi}$，这一数值是方差计算的基础。

**几何中弧长与面积**的计算也常依赖换元法。求椭圆 $\frac{x^2}{a^2} + \frac{y^2}{b^2} = 1$ 的面积时，令 $x = a\cos t$，$y = b\sin t$，面积公式化为 $\int_0^{2\pi} ab\sin^2 t\,dt$，再用二倍角公式 $\sin^2 t = \frac{1-\cos 2t}{2}$ 化简，得 $\pi ab$。

---

## 常见误区

**误区一：换元后忘记替换积分上下限（定积分换元）**
在定积分的换元中，令 $u = \varphi(x)$ 后，积分限必须同步变换：$x: a \to b$ 应变为 $u: \varphi(a) \to \varphi(b)$。不少学生在换元后仍保留原变量 $x$ 的上下限，导致数值错误。例如 $\int_0^1 2x\sqrt{1-x^2}\,dx$，令 $u = 1-x^2$，上下限由 $[0,1]$ 变为 $[1,0]$，方向发生翻转，需注意负号。

**误区二：分部积分中 $u$ 和 $dv$ 选择颠倒**
若对 $\int \ln x\,dx$ 错误地取 $u = 1$（常数），$dv = \ln x\,dx$，则 $v = \int \ln x\,dx$ 本身就是待求量，形成循环死局。正确做法是取 $u = \ln x$，$dv = dx$，得 $x\ln x - \int x \cdot \frac{1}{x}\,dx = x\ln x - x + C$。LIATE 原则正是为避免此类错误而设计的。

**误区三：认为换元法只能用一次**
对于复杂被积函数（如 $\int \sqrt{1 - \sin^2 x}\cos x\,dx$ 的变形版本），可能需要先用三角换元消去根号，再用一次代数换元化简有理式，两次换元叠加使用是完全合法且常见的操作，学生不应人为限制换元次数。

---

## 知识关联

**前置知识**：不定积分的定义和基本积分表（如 $\int x^n\,dx = \frac{x^{n+1}}{n+1}+C$，$\int \frac{1}{x}\,dx = \ln|x|+C$）是换元法和分部积分法的操作基础——换元后或分部积分后得到的新积分，最终仍需要查基本积分表才能求出原函数。

**后续应用**：在**常微分方程初步**中，分离变量法本质上就是对方程两端分别关于不同变量做换元积分；一阶线性微分方程的常数变易法则大量依赖分部积分来求特解。没有熟练的积分技巧，常微分方程中的求解过程将寸步难行。此外，多元积分（重积分）中的坐标变换（极坐标、球坐标替换）是第二类换元法在高维情形的直接推广，其雅可比行列式正是换元公式中 $\varphi'(x)$ 的多维对应物。