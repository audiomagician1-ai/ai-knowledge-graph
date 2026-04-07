---
id: "definite-integrals"
concept: "定积分"
domain: "mathematics"
subdomain: "calculus"
subdomain_name: "微积分"
difficulty: 6
is_milestone: false
tags: ["核心"]
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "research-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "textbook"
    ref: "Stewart, James. Calculus: Early Transcendentals, 9th Ed., Ch.5"
  - type: "textbook"
    ref: "Spivak, Michael. Calculus, 4th Ed., Ch.13-14"
  - type: "academic"
    ref: "Bressoud, David. A Radical Approach to Real Analysis, 2nd Ed., MAA, 2007"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 定积分

## 概述

定积分是对函数在某一**闭区间 $[a, b]$ 上"面积总量"的精确度量**，其核心思想是用无限多个无限细的矩形来逼近曲线下的面积。与不定积分（反导数族）不同，定积分的结果是一个**确定的数值**，而非含有任意常数 $C$ 的函数表达式。记号 $\displaystyle\int_a^b f(x)\,dx$ 中，$a$ 称为积分下限，$b$ 称为积分上限，$f(x)$ 称为被积函数。

定积分的概念可追溯至古希腊阿基米德（约公元前 287–212 年）用穷竭法计算抛物线弓形面积的工作。但严格的现代定义由德国数学家黎曼（Bernhard Riemann）于 1854 年在其就职论文中正式提出，因此该定义体系被称为**黎曼积分**。黎曼将"分割—取样—求和—取极限"这四个步骤形式化，彻底奠定了定积分的分析学基础。

定积分的重要性在于它将**离散求和推广到连续情形**：物理中的功、路程、质量分布，以及几何中的面积、体积，本质上都是定积分。掌握定积分是计算旋转体体积、弧长及广义积分的直接前提，也是理解微积分基本定理（将导数与积分联系起来）的必要基础。

---

## 核心原理

### 黎曼和的构造

设函数 $f(x)$ 在 $[a, b]$ 上有界。**黎曼和**的构造分四步：

1. **分割**：将 $[a, b]$ 分成 $n$ 个子区间，分点为 $a = x_0 < x_1 < x_2 < \cdots < x_n = b$，第 $i$ 个子区间长度为 $\Delta x_i = x_i - x_{i-1}$。
2. **取样**：在每个子区间 $[x_{i-1}, x_i]$ 内任取一点 $\xi_i$（称为**标签点**或取样点）。
3. **求和**：构造黎曼和 $S_n = \displaystyle\sum_{i=1}^n f(\xi_i)\,\Delta x_i$，其中每一项 $f(\xi_i)\,\Delta x_i$ 是以 $f(\xi_i)$ 为高、$\Delta x_i$ 为宽的矩形面积。
4. **取极限**：令分割的**最大子区间长度**（称为**范数**，记为 $\|P\| = \max_i \Delta x_i$）趋向 0，若极限存在且与分割方式和标签点的选取无关，则该极限值即为定积分。

$$\int_a^b f(x)\,dx = \lim_{\|P\|\to 0} \sum_{i=1}^n f(\xi_i)\,\Delta x_i$$

注意极限条件是 $\|P\| \to 0$，而非简单地 $n \to \infty$：若子区间长度不均匀，即便 $n$ 很大也可能有某个子区间很长，因此必须用范数控制。

### 黎曼可积的条件

并非所有有界函数都是黎曼可积的。黎曼给出的充要条件为：$f$ 在 $[a,b]$ 上黎曼可积，当且仅当对任意 $\varepsilon > 0$，存在分割使得**上黎曼和与下黎曼和之差小于 $\varepsilon$**。

实用的充分条件有两个：
- **连续函数**在闭区间上必然黎曼可积（由一致连续性保证）；
- **单调有界函数**在闭区间上也是黎曼可积的（间断点至多可数且测度为零）。

典型的**不可积例子**是 Dirichlet 函数：$D(x) = 1$（$x$ 为有理数），$D(x) = 0$（$x$ 为无理数）。在任意子区间上，其上黎曼和恒为 1，下黎曼和恒为 0，两者之差始终为 $b - a \neq 0$，故 Dirichlet 函数在任意区间上均不黎曼可积。

### 定积分的基本性质

定积分满足若干对计算至关重要的代数性质：

- **线性性**：$\displaystyle\int_a^b [\alpha f(x) + \beta g(x)]\,dx = \alpha\int_a^b f(x)\,dx + \beta\int_a^b g(x)\,dx$
- **区间可加性**：若 $a < c < b$，则 $\displaystyle\int_a^b f(x)\,dx = \int_a^c f(x)\,dx + \int_c^b f(x)\,dx$
- **交换上下限取反**：$\displaystyle\int_a^b f(x)\,dx = -\int_b^a f(x)\,dx$，特别地 $\displaystyle\int_a^a f(x)\,dx = 0$
- **积分估值不等式**：若 $m \leq f(x) \leq M$ 在 $[a,b]$ 上成立，则 $m(b-a) \leq \displaystyle\int_a^b f(x)\,dx \leq M(b-a)$
- **积分中值定理**：若 $f$ 在 $[a,b]$ 上连续，则存在 $\xi \in (a, b)$ 使得 $\displaystyle\int_a^b f(x)\,dx = f(\xi)(b-a)$，即定积分等于某个函数值乘以区间长度。

---

## 实际应用

**利用定义计算 $\displaystyle\int_0^1 x^2\,dx$**：将 $[0,1]$ 均匀分成 $n$ 份，$\Delta x = \tfrac{1}{n}$，取右端点 $\xi_i = \tfrac{i}{n}$，则

$$S_n = \sum_{i=1}^n \left(\frac{i}{n}\right)^2 \cdot \frac{1}{n} = \frac{1}{n^3}\sum_{i=1}^n i^2 = \frac{1}{n^3}\cdot\frac{n(n+1)(2n+1)}{6} \xrightarrow{n\to\infty} \frac{1}{3}$$

这验证了 $\displaystyle\int_0^1 x^2\,dx = \tfrac{1}{3}$，也说明不借助微积分基本定理、仅凭黎曼和定义求积分时计算量极大。

**物理中的应用——变力做功**：弹簧弹力 $F(x) = kx$，将弹簧从自然长度压缩（或拉伸）距离 $d$，所做的功为 $W = \displaystyle\int_0^d kx\,dx = \tfrac{1}{2}kd^2$（胡克定律应用）。若用黎曼和理解，每一小段位移 $\Delta x_i$ 上的做功约为 $F(\xi_i)\,\Delta x_i$，连续求和即为定积分。

---

## 常见误区

**误区一：认为"定积分就是不定积分代入上下限"。** 这一认识在逻辑顺序上倒置了。定积分的定义完全独立于不定积分，通过黎曼和的极限给出；而"代入上下限求值"的方法来自**微积分基本定理**（Newton-Leibniz 公式），是定积分的一个**计算工具**，而非定义本身。对不可求原函数的被积函数（如 $e^{-x^2}$），定积分仍然存在，只是无法用初等函数的原函数来计算。

**误区二：以为 $f(x) \geq 0$ 才能做定积分。** 黎曼和的定义对任意有界函数均成立，$f(\xi_i)\,\Delta x_i$ 中若 $f(\xi_i) < 0$ 则该矩形面积取负值。因此定积分是**带符号的面积**：$x$ 轴上方部分贡献正值，下方部分贡献负值，两者叠加。例如 $\displaystyle\int_0^{2\pi} \sin x\,dx = 0$，因为 $[0, \pi]$ 上的正面积与 $[\pi, 2\pi]$ 上的负面积恰好抵消。

**误区三：混淆"分割细化"与"子区间等分"。** 黎曼积分的定义要求**范数 $\|P\| \to 0$**，而非要求等分。等分只是一种特殊的分割方式，对连续函数用等分计算极限是正确的（因为连续函数在均匀细化下黎曼和一定收敛），但对某些不连续函数，非均匀分割可能导致黎曼和不收敛，而均匀分割却恰好收敛——这正是黎曼可积定义必须对**所有**分割方式成立的原因。

---

## 知识关联

定积分以**不定积分**（反导数）为预备知识，但二者的联系并非定义上的，而是由**微积分基本定理**（下一个核心主题）架桥：若 $F'(x) = f(x)$，则 $\displaystyle\int_a^b f(x)\,dx = F(b) - F(a)$。这一定理将黎曼和的极限与原函数计算直接挂钩，将定积分的计算从"繁琐的求和极限"转化为"求原函数后代入"。

在定积分基础上，直接衍生出：**曲线围面积**（利用 $\displaystyle