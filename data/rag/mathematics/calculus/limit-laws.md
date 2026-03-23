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
quality_tier: "pending-rescore"
quality_score: 35.0
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 0.393
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
---
# 极限运算法则

## 概述

极限运算法则是将复杂极限问题分解为若干简单极限之积、商、和、差的系统方法。其核心前提是：**参与运算的每个极限必须单独存在且有限**，在此条件下，极限号可以"穿透"四则运算符号进行分配。这一法则将抽象的极限问题转化为代数计算，是微积分从定义走向实用计算的关键桥梁。

极限四则运算法则最早在柯西（Augustin-Louis Cauchy）1821年出版的《分析教程》（*Cours d'analyse*）中被系统整理，与严格的ε-δ定义同时确立。夹逼定理（又称"夹挤定理"或"三明治定理"）的雏形可追溯至阿基米德用内接外切多边形逼近圆周率π的方法，但其现代形式同样在19世纪分析学严格化进程中被明确表述。

这两类法则解决了两种截然不同的计算困境：四则运算法则处理的是可直接分解的极限；夹逼定理处理的是直接代入导致不定型或无法代数分解的极限，例如 $\lim_{x \to 0} x\sin\frac{1}{x}$ 这类包含有界振荡因子的情形。

---

## 核心原理

### 四则运算法则的精确表述

设 $\lim_{x \to a} f(x) = A$，$\lim_{x \to a} g(x) = B$，其中 $A, B$ 均为有限实数，则：

- **加减法**：$\lim_{x \to a}[f(x) \pm g(x)] = A \pm B$
- **乘法**：$\lim_{x \to a}[f(x) \cdot g(x)] = A \cdot B$
- **除法**：$\lim_{x \to a}\dfrac{f(x)}{g(x)} = \dfrac{A}{B}$，要求 $B \neq 0$
- **数乘推论**：$\lim_{x \to a}[c \cdot f(x)] = c \cdot A$，$c$ 为常数

乘法法则可推广到幂次：若 $n$ 为正整数，则 $\lim_{x \to a}[f(x)]^n = A^n$。进一步，若 $f(x) \geq 0$ 且 $A \geq 0$，则 $\lim_{x \to a}\sqrt[n]{f(x)} = \sqrt[n]{A}$。

**关键限制**：上述法则在 $A, B$ 为 $\pm\infty$ 时**不能直接套用**。例如 $\infty - \infty$、$0 \cdot \infty$ 均属不定型，需要先变形再应用法则。

### 夹逼定理（Squeeze Theorem）

**定理表述**：若在点 $a$ 的某去心邻域内有 $g(x) \leq f(x) \leq h(x)$，且 $\lim_{x \to a} g(x) = \lim_{x \to a} h(x) = L$，则 $\lim_{x \to a} f(x) = L$。

夹逼定理成立的逻辑依据来自极限的序关系保持性：若 $f \leq h$ 且二者极限均为 $L$，则对任意 $\varepsilon > 0$，存在 $\delta > 0$ 使得当 $0 < |x-a| < \delta$ 时，同时有 $|g(x) - L| < \varepsilon$ 和 $|h(x) - L| < \varepsilon$，从而 $L - \varepsilon < g(x) \leq f(x) \leq h(x) < L + \varepsilon$，即 $|f(x) - L| < \varepsilon$。

**使用夹逼定理的关键技巧**在于构造恰当的上下界函数。最常用的放缩工具是：

- $-1 \leq \sin x \leq 1$，$-1 \leq \cos x \leq 1$（有界性）
- 不等式 $\sin x < x < \tan x$（当 $0 < x < \pi/2$ 时）

### 两个重要极限

四则运算法则与夹逼定理共同推导出两个微积分中频繁使用的基本极限：

**第一重要极限**（由夹逼定理证明）：
$$\lim_{x \to 0} \frac{\sin x}{x} = 1$$
证明的核心不等式为 $\cos x \leq \dfrac{\sin x}{x} \leq 1$（当 $x \to 0^+$），利用夹逼得出结果。

**第二重要极限**（自然对数底数定义）：
$$\lim_{x \to \infty}\left(1 + \frac{1}{x}\right)^x = e \approx 2.71828\ldots$$

---

## 实际应用

**应用1：有理函数在有限点处的极限**

计算 $\lim_{x \to 2} \dfrac{x^2 - 3x + 1}{x + 5}$。因分母在 $x=2$ 处极限为 $7 \neq 0$，直接应用除法法则：
$$= \frac{\lim_{x\to2}(x^2 - 3x + 1)}{\lim_{x\to2}(x+5)} = \frac{4 - 6 + 1}{2 + 5} = \frac{-1}{7}$$

**应用2：夹逼定理处理振荡函数**

计算 $\lim_{x \to 0} x^2 \sin\dfrac{1}{x}$。由于 $\left|\sin\dfrac{1}{x}\right| \leq 1$，有：
$$-x^2 \leq x^2\sin\frac{1}{x} \leq x^2$$
而 $\lim_{x\to 0}(-x^2) = \lim_{x\to 0} x^2 = 0$，由夹逼定理得极限为 $0$。

**应用3：利用第一重要极限的变形**

计算 $\lim_{x \to 0} \dfrac{\sin 3x}{x}$。令 $t = 3x$，则：
$$\lim_{x \to 0} \frac{\sin 3x}{x} = \lim_{t \to 0} \frac{\sin t}{t/3} = 3\lim_{t\to 0}\frac{\sin t}{t} = 3 \times 1 = 3$$

---

## 常见误区

**误区1：在极限不存在时强行使用四则运算法则**

学生常错误地将 $\lim[f(x) + g(x)]$ 分拆为 $\lim f(x) + \lim g(x)$，即便 $\lim f(x)$ 或 $\lim g(x)$ 不存在。典型错误：$\lim_{x\to\infty}\left[(x+1) - x\right] = \lim_{x\to\infty}(x+1) - \lim_{x\to\infty}x = \infty - \infty$（错误！）。正确做法是先化简：$\lim_{x\to\infty}[(x+1)-x] = \lim_{x\to\infty}1 = 1$。法则的前提是**每个分极限单独存在**。

**误区2：夹逼定理要求上下界在全域成立**

不少学生认为不等式 $g(x) \leq f(x) \leq h(x)$ 必须在 $x$ 的整个定义域成立。实际上定理只需要在 $a$ 的某**去心邻域**（即 $0 < |x-a| < \delta$ 的某个 $\delta > 0$）内成立即可。例如证明 $\lim_{x\to0} x\sin\frac{1}{x} = 0$ 时，只需在 $x \neq 0$ 的邻域内使用 $|x\sin\frac{1}{x}| \leq |x|$。

**误区3：将 $\lim(f \cdot g) = (\lim f)\cdot(\lim g)$ 误用于 $0 \cdot \infty$ 型**

若 $\lim f(x) = 0$，$\lim g(x) = \infty$，**不能**直接得出乘积极限为 $0$ 或 $\infty$。这是不定型，实际结果取决于两者趋近速度的比较，需转化为 $\frac{0}{0}$ 或 $\frac{\infty}{\infty}$ 型后再处理。

---

## 知识关联

**前置概念衔接**：极限运算法则的合法性完全依赖于极限的ε-δ定义。四则运算法则的证明直接使用ε-δ语言——例如乘法法则的证明利用恒等式 $f(x)g(x) - AB = [f(x)-A]g(x) + A[g(x)-B]$，逐项用 $\varepsilon/2$ 控制误差。没有精确的极限定义，运算法则只能是经验规律而非定理。

**通向连续性**：四则运算法则直接导出连续函数的代数封闭性——若 $f, g$ 在点 $a$ 连续（即极限值等于函数值），则 $f \pm g$、$f \cdot g$、$f/g$（$g(a) \neq 0$）均在 $a$ 连续。这正是多项式函数、有理函数在其定义域内处处连续的代数根据。

**通向洛必达法则**：当四则运算法则和代数变形均无法处理 $\frac{0}{0}$ 或 $\frac{\infty}{\infty}$ 不定型时，需要洛必达法则（L'Hôpital's Rule，1696年首次发表）。洛必达法则本质上是用导数的比值替代原函数的比
