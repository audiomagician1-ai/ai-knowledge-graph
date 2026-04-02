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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 不等式技巧

## 概述

不等式技巧是代数分析中用于估计、比较和优化表达式大小的一组精确工具，核心包括算术-几何平均不等式（AM-GM）、柯西-施瓦茨不等式和排序不等式。这三类不等式各有严格的成立条件和等号条件，可以将复杂的最值问题转化为验证等号成立的代数操作。

AM-GM不等式由古希腊数学家最早发现雏形，柯西-施瓦茨不等式由奥古斯丁-路易·柯西于1821年在《分析教程》中首次严格表述，排序不等式则由哈代、李特尔伍德和波利亚在1934年的专著《不等式》中系统化。这三个不等式构成竞赛数学与分析学的基本框架，也是求函数最值、证明代数恒等式的标准方法。

掌握这些技巧之所以重要，在于它们将"不等号方向"这一定性判断转化为可以精确计算等号成立时机的定量工具。例如，用AM-GM求 $f(x)=x+\frac{1}{x}$ 的最小值，只需一步应用即可得到结论 $f(x)\geq 2$，且等号在 $x=1$ 时成立，远比求导法简洁。

---

## 核心原理

### AM-GM 不等式

对 $n$ 个正实数 $a_1, a_2, \ldots, a_n$，算术-几何平均不等式表述为：

$$\frac{a_1 + a_2 + \cdots + a_n}{n} \geq \sqrt[n]{a_1 a_2 \cdots a_n}$$

等号成立的充要条件是 $a_1 = a_2 = \cdots = a_n$。

二元形式 $\frac{a+b}{2} \geq \sqrt{ab}$（$a,b>0$）最常用。使用时的关键技巧是**凑积为常数**：若要求 $a+b$ 在 $ab=k$（常数）时的最小值，或求 $ab$ 在 $a+b=k$ 时的最大值，直接套用即可。例如，已知 $x>0$，求 $x+\frac{4}{x}$ 的最小值：

$$x + \frac{4}{x} \geq 2\sqrt{x \cdot \frac{4}{x}} = 2\sqrt{4} = 4$$

等号在 $x = \frac{4}{x}$，即 $x=2$ 时成立，故最小值为 **4**。三元AM-GM则常用于形如 $a+b+c \geq 3\sqrt[3]{abc}$ 的配凑。

### 柯西-施瓦茨不等式

对实数序列 $a_1,\ldots,a_n$ 和 $b_1,\ldots,b_n$，柯西-施瓦茨不等式为：

$$\left(\sum_{i=1}^n a_i b_i\right)^2 \leq \left(\sum_{i=1}^n a_i^2\right)\left(\sum_{i=1}^n b_i^2\right)$$

等号成立条件是两序列成比例，即存在常数 $\lambda$ 使 $a_i = \lambda b_i$ 对所有 $i$ 成立。

竞赛中最常用的是**分式和估计**（Engel形式/Titu引理）：

$$\frac{a_1^2}{b_1} + \frac{a_2^2}{b_2} + \cdots + \frac{a_n^2}{b_n} \geq \frac{(a_1+a_2+\cdots+a_n)^2}{b_1+b_2+\cdots+b_n}$$

其中 $b_i > 0$。例如，证明 $\frac{x^2}{a}+\frac{y^2}{b} \geq \frac{(x+y)^2}{a+b}$（$a,b>0$）只需直接套用Titu引理即可，等号在 $\frac{x}{a}=\frac{y}{b}$ 时成立。

### 排序不等式

设两组实数满足 $a_1 \leq a_2 \leq \cdots \leq a_n$ 和 $b_1 \leq b_2 \leq \cdots \leq b_n$，令 $b_{\sigma}$ 为 $b$ 的任意排列，则：

$$\sum_{i=1}^n a_i b_{n+1-i} \leq \sum_{i=1}^n a_i b_{\sigma(i)} \leq \sum_{i=1}^n a_i b_i$$

即**同序和 ≥ 乱序和 ≥ 逆序和**，等号仅在所有 $a_i$ 相等或所有 $b_i$ 相等时成立。

排序不等式可直接推出AM-GM不等式，也是证明切比雪夫求和不等式（$n\sum a_i b_i \geq \sum a_i \cdot \sum b_i$，同向时）的基础。排序不等式的典型应用是证明 $\frac{a}{b}+\frac{b}{c}+\frac{c}{a} \geq 3$（$a,b,c>0$）：令序列 $(a,b,c)$ 和 $(\frac{1}{b},\frac{1}{c},\frac{1}{a})$，同序和不小于乱序和，由排序不等式得证。

---

## 实际应用

**最值问题**：已知 $a+b+c=1$，$a,b,c>0$，求 $ab+bc+ca$ 的最大值。由AM-GM知 $(a+b+c)^2 = a^2+b^2+c^2+2(ab+bc+ca) \geq 3(ab+bc+ca)$，故 $ab+bc+ca \leq \frac{1}{3}$，等号在 $a=b=c=\frac{1}{3}$ 时成立。

**分式不等式证明**：证明 $\frac{1}{1+a^2}+\frac{1}{1+b^2}+\frac{1}{1+c^2} \leq \frac{3}{1+abc\cdot(\text{修正项})}$ 类问题，常使用柯西-施瓦茨先估计各项的下界或上界。

**数列求和估计**：在分析 $\sum_{k=1}^n \frac{1}{\sqrt{k}}$ 的上下界时，利用AM-GM将 $\frac{1}{\sqrt{k}}$ 与 $\sqrt{k}-\sqrt{k-1}$ 做比较，得到 $\frac{1}{\sqrt{k}} \leq 2(\sqrt{k}-\sqrt{k-1})$（由 $\sqrt{k}+\sqrt{k-1} \geq 2\sqrt{k-1}$ 等推导），从而给出 $\sum_{k=1}^n \frac{1}{\sqrt{k}} \leq 2\sqrt{n}-1$ 的精确上界。

---

## 常见误区

**误区一：忽视等号成立条件，误报最值。** AM-GM的等号条件是各项相等，但实际约束可能使各项无法同时相等。例如，对 $x+y=3$，$x,y>0$，有人写 $xy \leq \left(\frac{x+y}{2}\right)^2=\frac{9}{4}$，结论正确；但若再加约束 $x=2y$，则等号 $x=y$ 不能同时成立，最大值需重新计算。直接套AM-GM而不验证等号是否在可行域内可达，是最常见的错误。

**误区二：将柯西-施瓦茨用于负数项时混淆符号。** 柯西-施瓦茨不等式对所有实数序列成立（左边是平方，恒非负），但Titu引理要求 $b_i > 0$，若某个 $b_i < 0$，不等号方向会改变。例如，$\frac{(-1)^2}{-1}+\frac{1^2}{1}=0 \not\geq \frac{0^2}{0}$（分母为零更无意义），随意套用Engel形式会导致错误结论。

**误区三：混淆排序不等式的适用形式与切比雪夫不等式。** 排序不等式处理的是两组数的乘积之和的比较，而切比雪夫不等式给出的是 $\sum a_i b_i$ 与 $\frac{1}{n}\sum a_i \cdot \sum b_i$ 的关系。两者结论方向相同（同向排列时乘积和较大），但适用场景不同：若题目给出乘积 $\sum a_i b_i$ 与均值乘积之比，应用切比雪夫；若比较不同排列下的乘积和大小，应用排序不等式。

---

## 知识关联

**前置基础**：一元一次不等式提供了不等号的传递性、加法和乘法法则（正数乘法保号、负数乘法变号），这些是推导AM-GM中 $(\sqrt{a}-\sqrt{b})^2 \geq 0$ 展开并整理的基础操作。没有对绝对值不等式和二次不等式的熟练处理，AM-GM的等号分析也无法完成。

**横向联系**：AM-GM、柯西-施瓦茨和排序不等式三者之间存在推导关系——排序不等式可导出AM-GM（取 $a_i=b_i=\frac{1}{n}$ 的对称配置），AM-GM可作为柯西-施瓦茨的特例验证（令 $n=2$，$a_1=a_2=b_1=b_2$）。熟悉这些联系有助于在竞赛中选择最简洁的证明路径。

**后续延