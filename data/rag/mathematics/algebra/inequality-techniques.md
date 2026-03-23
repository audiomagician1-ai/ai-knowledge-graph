---
id: "inequality-techniques"
concept: "不等式技巧"
domain: "mathematics"
subdomain: "algebra"
subdomain_name: "代数"
difficulty: 7
is_milestone: false
tags: ["竞赛"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 36.3
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 0.393
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
---
# 不等式技巧

## 概述

不等式技巧是代数中用于估计、放缩和证明数量关系的一类经典方法，核心包括算术-几何平均不等式（AM-GM）、柯西-施瓦茨不等式和排序不等式。这三类工具各有其适用结构：AM-GM 处理乘积与求和的互换，柯西处理向量内积的上界，排序不等式则揭示同序相乘最大的原理。

AM-GM 不等式的系统化研究可追溯到欧拉时代，但严格证明通常归功于 19 世纪的 Cauchy（柯西），他在 1821 年的《代数分析教程》中给出了 $n$ 个变量版本的完整归纳证明。柯西-施瓦茨不等式则由 Cauchy（1821）和 Schwarz（1888）分别独立在实数和积分情形下建立，现已成为线性代数与分析的基本工具。

这三类不等式在竞赛数学、优化问题和物理估算中频繁出现。掌握它们不仅能解决"证明某式恒成立"的题型，还能在求最值时通过构造等号条件直接定位极值点，是代数工具箱中效率极高的方法。

---

## 核心原理

### AM-GM 不等式

对于 $n$ 个正实数 $a_1, a_2, \ldots, a_n$，算术平均数不小于几何平均数：

$$\frac{a_1 + a_2 + \cdots + a_n}{n} \geq \sqrt[n]{a_1 a_2 \cdots a_n}$$

等号成立当且仅当 $a_1 = a_2 = \cdots = a_n$。

**等号条件**是使用 AM-GM 求最值的关键：若要让某表达式取到最小值，必须令所有参与 AM-GM 的项相等。例如，对 $x > 0$，求 $x + \dfrac{4}{x}$ 的最小值时，令两项相等 $x = \dfrac{4}{x}$，得 $x = 2$，最小值为 $4$，而 AM-GM 给出 $x + \dfrac{4}{x} \geq 2\sqrt{x \cdot \dfrac{4}{x}} = 4$。

**使用注意**：各项必须为正数；若分组方式不满足等号可同时成立，则所得下界不可达，结论无效。

### 柯西-施瓦茨不等式

对实数序列 $a_1,\ldots,a_n$ 和 $b_1,\ldots,b_n$，有：

$$\left(\sum_{i=1}^n a_i b_i\right)^2 \leq \left(\sum_{i=1}^n a_i^2\right)\left(\sum_{i=1}^n b_i^2\right)$$

等号成立当且仅当 $\dfrac{a_1}{b_1} = \dfrac{a_2}{b_2} = \cdots = \dfrac{a_n}{b_n}$（即两序列成比例）。

柯西-施瓦茨的实用变形称为 **Engel 形式**（又名 Titu 引理）：

$$\frac{a_1^2}{b_1} + \frac{a_2^2}{b_2} + \cdots + \frac{a_n^2}{b_n} \geq \frac{(a_1 + a_2 + \cdots + a_n)^2}{b_1 + b_2 + \cdots + b_n}, \quad b_i > 0$$

这一形式在处理分式求和的下界时极为高效。例如，已知 $x, y, z > 0$ 且 $x + y + z = 1$，则 $\dfrac{x^2}{a} + \dfrac{y^2}{b} + \dfrac{z^2}{c} \geq \dfrac{1}{a+b+c}$ 可直接由 Titu 引理得出。

### 排序不等式

设两组实数满足 $a_1 \leq a_2 \leq \cdots \leq a_n$ 和 $b_1 \leq b_2 \leq \cdots \leq b_n$，对 $b_1, \ldots, b_n$ 的任意排列 $b_{\sigma(1)}, \ldots, b_{\sigma(n)}$，有：

$$\sum_{i=1}^n a_i b_{n+1-i} \leq \sum_{i=1}^n a_i b_{\sigma(i)} \leq \sum_{i=1}^n a_i b_i$$

即**同序积之和最大，逆序积之和最小，乱序居中**。

排序不等式可直接推导出 AM-GM（令 $a_i = b_i = \sqrt[n]{a_1\cdots a_n}$ 的适当变形），也可证明切比雪夫求和不等式。它在处理轮换对称式时尤为直接，无需凑项。

---

## 实际应用

**竞赛最值问题**：已知正实数 $a, b, c$ 满足 $abc = 8$，求 $a + b + c$ 的最小值。由 AM-GM：$\dfrac{a+b+c}{3} \geq \sqrt[3]{abc} = 2$，故 $a + b + c \geq 6$，等号在 $a = b = c = 2$ 时成立。

**分式不等式证明**：证明 $\dfrac{a}{b+c} + \dfrac{b}{a+c} + \dfrac{c}{a+b} \geq \dfrac{3}{2}$（Nesbitt 不等式，$a,b,c>0$）。将每个分式写成 $\dfrac{a}{b+c} = \dfrac{a^2}{a(b+c)}$，再用 Titu 引理：左式 $\geq \dfrac{(a+b+c)^2}{a(b+c)+b(a+c)+c(a+b)} = \dfrac{(a+b+c)^2}{2(ab+bc+ca)}$，结合 $(a+b+c)^2 \geq 3(ab+bc+ca)$ 即得。

**排序不等式的应用**：若 $a \geq b \geq c > 0$，则 $a^2b + b^2c + c^2a \leq a^2c + b^2a + c^2b$ 可直接由排序不等式得出，因为 $(a^2,b^2,c^2)$ 与 $(a,b,c)$ 同序，逆序排列给出更小的和。

---

## 常见误区

**误区一：AM-GM 对非正数成立**。AM-GM 要求所有变量严格为正。若 $a = -1, b = -1$，则 $\dfrac{a+b}{2} = -1$，但 $\sqrt{ab} = 1$，不等式反向。遇到含负数的情形必须先绝对值化或换元，切不可直接套用。

**误区二：等号条件不满足时仍宣称取到最值**。例如求 $x + \dfrac{1}{x} + \dfrac{1}{x+1}$（$x>0$）的最小值时，若对三项用 AM-GM，等号要求 $x = \dfrac{1}{x} = \dfrac{1}{x+1}$，三式无法同时成立，所得下界 $3\sqrt[3]{\frac{1}{x(x+1)}}$ 并非常数，AM-GM 不能直接给出最小值，需换用导数或其他方法。

**误区三：混淆柯西和 AM-GM 的适用场合**。柯西处理的是两组数列内积的平方上界，适合在给定约束为平方和时找另一量的上/下界；AM-GM 适合将乘积化为和。若题目中出现 $\sqrt{a^2+b^2}$ 的结构，柯西往往比 AM-GM 更自然；若出现 $xy$ 而需估计 $x+y$，则 AM-GM 更直接。将两者互换常导致证明路径冗长或无法收敛。

---

## 知识关联

**与一元一次不等式的联系**：一元一次不等式训练了不等号方向随乘除正负数翻转的基本规则。AM-GM 和柯西在推导等号条件、移项时同样依赖这些基本规则。理解"等号何时成立"依赖对等式条件的精确控制，这正是从线性不等式过渡到高次不等式的核心难点。

**横向联系**：三类不等式之间存在推导关系——排序不等式可推出切比雪夫不等式，AM-GM 可由 Cauchy 归纳法或 Jensen 不等式（凸函数的推广）证明，柯西-施瓦茨可看作 $\ell^2$ 空间中向量夹角余弦不超过 1 的代数表述。在学习数学分析或线性代数后，这些不等式可在更一般的内积空间中统一理解。

**在优化与数论中的延伸**：AM-GM 是拉格朗日乘数法在对称约束下的"快捷版"；柯西-施瓦茨是 $L^2$ 内积的 Hölder 不等式（指数 $p=q=2$）的特例；排序不等式的思想直接通向重排不等式和 Muirhead 定理，是处理对称多项式不等式的系统方法。
