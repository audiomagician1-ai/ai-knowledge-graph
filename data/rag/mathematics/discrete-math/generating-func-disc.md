---
id: "generating-func-disc"
concept: "生成函数(离散)"
domain: "mathematics"
subdomain: "discrete-math"
subdomain_name: "离散数学"
difficulty: 7
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "pending-rescore"
quality_score: 40.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.393
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 生成函数（离散）

## 概述

生成函数（Generating Function）是将一个离散数列 $\{a_n\}$ 编码为一个形式幂级数 $G(x) = \sum_{n=0}^{\infty} a_n x^n$ 的数学工具。它最早由亚伯拉罕·棣·莫弗（de Moivre）于1730年在研究线性递推关系时系统使用，后经拉普拉斯和欧拉大力推广。离散数学中的生成函数本质上不关心 $x$ 的实际取值，而是把 $x$ 视为一个纯粹的形式符号，利用多项式和幂级数的代数运算提取数列信息。

离散数学中有两类核心生成函数：**普通型生成函数（OGF，Ordinary Generating Function）** 和 **指数型生成函数（EGF，Exponential Generating Function）**。OGF 定义为 $G(x) = \sum_{n=0}^{\infty} a_n x^n$，适用于组合计数（无标号对象的选取）；EGF 定义为 $\hat{G}(x) = \sum_{n=0}^{\infty} a_n \frac{x^n}{n!}$，适用于排列计数（有标号对象的排列）。两者区别在于 $x^n$ 的系数是否除以 $n!$，选择哪种类型直接决定计算的简便性。

在递推关系求解中，生成函数将递推方程转化为代数方程，从而绕开逐项迭代的繁琐过程。例如，Fibonacci 数列满足 $F_n = F_{n-1} + F_{n-2}$，利用 OGF 可直接推导出封闭公式 $F_n = \frac{1}{\sqrt{5}}\left[\left(\frac{1+\sqrt{5}}{2}\right)^n - \left(\frac{1-\sqrt{5}}{2}\right)^n\right]$。

---

## 核心原理

### 普通型生成函数（OGF）

OGF 的核心技巧是利用已知的封闭形式对应关系。最基础的公式为几何级数：

$$\frac{1}{1-x} = \sum_{n=0}^{\infty} x^n, \quad \frac{1}{(1-x)^k} = \sum_{n=0}^{\infty} \binom{n+k-1}{k-1} x^n$$

后者对应带重复的多重组合数 $\binom{n+k-1}{k-1}$，是求解"将 $n$ 个相同球分入 $k$ 个不同盒子"问题的直接来源。对于递推关系 $a_n = 5a_{n-1} - 6a_{n-2}$（初值 $a_0=0, a_1=1$），令 $G(x)=\sum a_n x^n$，两边乘以相应幂次后得到：

$$G(x) = \frac{x}{1 - 5x + 6x^2} = \frac{x}{(1-2x)(1-3x)}$$

通过部分分式分解得 $a_n = 3^n - 2^n$，整个过程不需要猜测特解形式。

### 指数型生成函数（EGF）

EGF 之所以对有标号排列问题有效，源于其卷积性质。若 $\hat{A}(x) = \sum a_n \frac{x^n}{n!}$ 且 $\hat{B}(x) = \sum b_n \frac{x^n}{n!}$，则乘积 $\hat{A}(x)\cdot\hat{B}(x)$ 的 $\frac{x^n}{n!}$ 系数恰好是 $\sum_{k=0}^{n}\binom{n}{k}a_k b_{n-k}$，即二项式卷积。这正对应于将 $n$ 个有标号对象拆分成两组后分别计数的组合意义。

错位排列数 $D_n$（全错位排列）满足 $D_n = (n-1)(D_{n-1}+D_{n-2})$，其 EGF 为：

$$\hat{D}(x) = \frac{e^{-x}}{1-x}$$

由此立即提取 $D_n = n!\sum_{k=0}^{n}\frac{(-1)^k}{k!}$，与容斥原理得到的结果完全吻合，验证了 EGF 与排列类问题的天然契合。

### 生成函数与递推关系的联立求解

设递推关系为 $a_n - c_1 a_{n-1} - c_2 a_{n-2} = f(n)$（非齐次项 $f(n)$），对应 OGF 两边求和后整理，得到一个关于 $G(x)$ 的代数方程：

$$(1 - c_1 x - c_2 x^2) G(x) = \text{初始条件项} + F(x)$$

其中 $F(x)$ 是 $f(n)$ 的 OGF。关键步骤是识别特征多项式 $1 - c_1 x - c_2 x^2$ 的根，再做部分分式分解。如果特征根有重根 $r$（重数 $m$），分解时会出现 $\frac{1}{(1-rx)^m}$ 项，对应数列中含有多项式因子 $n^{m-1}$ 的项，这与特征根法的结论完全一致。

---

## 实际应用

**整数拆分计数**：将整数 $n$ 拆分为若干正整数之和的方案数 $p(n)$，其 OGF 为著名的欧拉乘积：

$$P(x) = \prod_{k=1}^{\infty} \frac{1}{1-x^k}$$

这一结果无法用简单递推轻易写出，但生成函数直接给出了紧凑表达。

**二项式系数的组合恒等式**：Vandermonde 恒等式 $\sum_{k=0}^{r}\binom{m}{k}\binom{n}{r-k}=\binom{m+n}{r}$ 可通过比较 $(1+x)^m \cdot (1+x)^n = (1+x)^{m+n}$ 两边 $x^r$ 系数直接证明，无需归纳法。

**有标号树的计数**：$n$ 个顶点的有标号有根树数量为 $n^{n-1}$（Cayley 公式），其 EGF $T(x)$ 满足方程 $T(x) = x e^{T(x)}$，借助 Lagrange 反演公式可从该隐式方程直接提取系数，得到 $[x^n]T(x) = \frac{n^{n-1}}{n!}$。

---

## 常见误区

**误区一：混淆 OGF 与 EGF 的适用场景**。对于数列 $a_n = n!$，其 OGF 为 $\sum n! x^n$，在任何 $x \neq 0$ 处均发散，无法使用封闭形式；但其 EGF 为 $\sum n! \frac{x^n}{n!} = \frac{1}{1-x}$，完全正常。因此，当数列增长速度接近 $n!$ 量级时，应优先使用 EGF，强行套用 OGF 会导致发散困境。

**误区二：将形式幂级数当作收敛级数处理**。生成函数方法中，$x$ 是纯形式符号，"$\frac{1}{1-2x}$"代表的是序列 $\{2^n\}$ 的编码，而非要求 $|x|<\frac{1}{2}$。在提取系数时不需要讨论收敛域，但若要利用复分析（留数定理）估计渐近行为，才需要引入收敛半径概念。

**误区三：部分分式分解遗漏重根项**。对于 $G(x) = \frac{1}{(1-x)^2(1-2x)}$，正确分解应包含 $\frac{A}{1-x}+\frac{B}{(1-x)^2}+\frac{C}{1-2x}$ 三项，遗漏 $\frac{A}{1-x}$ 项后直接提取系数会导致错误答案，而恰恰这一项对应了 $a_n$ 中的线性多项式部分。

---

## 知识关联

生成函数建立在**递推关系**的基础之上：递推关系提供了数列满足的方程，而生成函数将这一方程转化为代数操作。掌握线性常系数递推关系（特征根方法）后学习 OGF，会发现两者在部分分式分解时完全对应——特征根 $r$ 对应 OGF 分母因子 $(1-rx)$，重数对应分母幂次，这种对应使得两种方法可以相互印证。

EGF 与**组合数学中的指数公式**紧密相连：若有标号结构由若干"连通块"构成，且连通块的 EGF 为 $C(x)$，则整体结构的 EGF 满足 $G(x) = e^{C(x)}$。这一公式将生成函数方法延伸至图论（连通图计数）、集合划分（Bell 数，其 EGF 为 $e^{e^x-1}$）等更广泛的离散结构，是离散数学与组合数学高级主题的核心桥梁。
