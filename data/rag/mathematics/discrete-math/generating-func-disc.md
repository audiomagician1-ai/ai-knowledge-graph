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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 生成函数（离散）

## 概述

生成函数是将数列 $\{a_n\}$ 编码为形式幂级数 $A(x) = \sum_{n=0}^{\infty} a_n x^n$ 的代数工具，其核心思想是把组合计数问题转化为多项式或幂级数的代数运算。离散数学中的生成函数分为两大类：**普通型生成函数**（Ordinary Generating Function, OGF）和**指数型生成函数**（Exponential Generating Function, EGF），二者的区别在于系数的编码方式不同，前者直接用 $a_n$ 作系数，后者用 $\frac{a_n}{n!}$ 作系数。

生成函数方法由Abraham de Moivre在18世纪初用于研究线性递推数列，Euler随后将其系统化用于整数分拆问题，而Laplace则发展了指数型生成函数处理排列计数。1990年代，Flajolet和Sedgewick建立的"解析组合"（Analytic Combinatorics）将生成函数提升为处理算法复杂度分析的标准框架。

生成函数在离散数学中的价值在于：它能将递推关系变为代数方程（例如Fibonacci数列的递推 $F_n = F_{n-1} + F_{n-2}$ 对应方程 $F(x) = xF(x) + x^2F(x) + x$），从而用有理函数的部分分式展开直接求出封闭公式，避免猜测法的盲目性。

---

## 核心原理

### 普通型生成函数（OGF）

给定数列 $a_0, a_1, a_2, \ldots$，其OGF定义为：
$$A(x) = \sum_{n=0}^{\infty} a_n x^n$$

OGF最适合处理**多重集合选取**（无顺序的组合）问题。经典例子：从无限供应的苹果、香蕉、橘子各取若干，恰好取 $n$ 个的方案数，其OGF为 $\frac{1}{(1-x)^3}$，展开系数为 $\binom{n+2}{2}$。

两个常用的OGF公式须牢记：
- $\frac{1}{1-x} = \sum_{n=0}^{\infty} x^n$（全1数列）
- $\frac{1}{(1-x)^k} = \sum_{n=0}^{\infty} \binom{n+k-1}{k-1} x^n$（多重集合数）

利用OGF求解线性递推的步骤为：设 $A(x) = \sum a_n x^n$，将递推关系两边同乘 $x^n$ 后对 $n$ 求和，得到含 $A(x)$ 的代数方程，解出 $A(x)$ 后做部分分式展开，再逐项读出系数。

### 指数型生成函数（EGF）

EGF定义为：
$$\hat{A}(x) = \sum_{n=0}^{\infty} a_n \frac{x^n}{n!}$$

EGF专门处理**有标号结构**（带顺序的排列）问题，因为 $\frac{x^n}{n!}$ 正好抵消了排列中的 $n!$ 因子。设数列 $a_n = n!$（全排列数），则其EGF为 $\frac{1}{1-x}$，而其OGF $\sum n! x^n$ 在 $x \neq 0$ 处发散，所以此时只能用EGF。

EGF的乘法公式具有特殊的组合意义：若 $\hat{A}(x)$ 和 $\hat{B}(x)$ 分别是数列 $a_n$ 和 $b_n$ 的EGF，则乘积 $\hat{A}(x)\hat{B}(x)$ 对应系数为 $c_n = \sum_{k=0}^{n} \binom{n}{k} a_k b_{n-k}$，即**二项卷积**，对应将 $n$ 个有标号元素分成两组分别计数的操作。

错位排列数（Derangement）$D_n$ 满足 $D_n = (n-1)(D_{n-1}+D_{n-2})$，其EGF为 $\hat{D}(x) = \frac{e^{-x}}{1-x}$，由此可读出 $D_n = n!\sum_{k=0}^{n}\frac{(-1)^k}{k!}$，当 $n\to\infty$ 时趋近于 $n!/e$。

### OGF与EGF的选择原则

选择OGF还是EGF取决于计数对象的本质：
- **无标号计数**（整数分拆、多集选取、括号匹配）→ OGF
- **有标号计数**（排列、有标号树、满射函数）→ EGF

整数分拆 $p(n)$ 的OGF为 $\prod_{k=1}^{\infty}\frac{1}{1-x^k}$，这个无穷乘积没有封闭形式，但可用Euler的五边形数定理得到递推：$p(n) = \sum_{k \neq 0} (-1)^{k+1} p\!\left(n - \frac{k(3k-1)}{2}\right)$，其中求和只在 $\frac{k(3k-1)}{2} \leq n$ 时有非零项。

---

## 实际应用

**求解Catalan数的封闭公式**：设 $C(x) = \sum_{n=0}^{\infty} C_n x^n$，由递推 $C_n = \sum_{k=0}^{n-1} C_k C_{n-1-k}$ 得 $C(x) = xC(x)^2 + 1$，解二次方程得 $C(x) = \frac{1-\sqrt{1-4x}}{2x}$，用广义二项式定理展开得 $C_n = \frac{1}{n+1}\binom{2n}{n}$，这是OGF的典型应用。

**Bell数的EGF**：Bell数 $B_n$（$n$ 个元素的集合划分数，$B_0=1, B_1=1, B_2=2, B_3=5, B_4=15$）的EGF为 $\hat{B}(x) = e^{e^x - 1}$，由此可推导Bell三角形的递推规律，并证明 $B_n$ 超指数增长。

**硬币找零问题**：用面值为1、5、10、25分的硬币凑成 $n$ 分的方案数，其OGF为 $\frac{1}{(1-x)(1-x^5)(1-x^{10})(1-x^{25})}$，可用计算机代数系统展开第 $n$ 项系数，无需穷举。

---

## 常见误区

**误区一：混用OGF和EGF的卷积公式**。OGF的乘积系数是普通卷积 $c_n = \sum_{k=0}^{n} a_k b_{n-k}$，而EGF的乘积系数是二项卷积 $c_n = \sum_{k=0}^{n}\binom{n}{k}a_k b_{n-k}$，二者相差 $\binom{n}{k}$ 因子。许多学生在处理排列计数时错误地使用OGF乘法，导致少计了排列方式数。

**误区二：认为形式幂级数必须收敛**。生成函数在此是**形式幂级数**，不是分析意义上的函数，$x$ 只是占位符，不需要考虑 $|x|<1$ 等收敛条件。例如 $\sum_{n=0}^{\infty} n! x^n$ 作为形式幂级数完全合法，可以正常做加减乘除运算，只是不能代入具体数值求和。

**误区三：Catalan数递推的边界处理失误**。在建立 $C(x)$ 满足 $C(x) = xC(x)^2 + 1$ 时，必须正确处理 $C_0 = 1$ 这个初值，否则会得到 $C(x) = xC(x)^2$ 导致平凡解 $C(x)=0$。解二次方程时出现两个根，需根据 $C_0=1$（即 $C(0)=1$）来选取 $\frac{1-\sqrt{1-4x}}{2x}$ 而非另一根。

---

## 知识关联

**与递推关系的连接**：线性常系数递推 $a_n = c_1 a_{n-1} + \cdots + c_k a_{n-k}$ 对应的特征多项式 $p(r) = r^k - c_1 r^{k-1} - \cdots - c_k$，其OGF为有理函数 $\frac{Q(x)}{1 - c_1 x - \cdots - c_k x^k}$，分母恰好是特征多项式的"翻转"。对有理OGF作部分分式，每个极点 $r_i$ 贡献项 $\alpha_i r_i^n$，直接给出通项公式，这与特征根法等价但步骤更系统化。

**与组合恒等式的关联**：Vandermonde恒等式 $\sum_{k=0}^{r}\binom{m}{k}\binom{n}{r-k} = \binom{m+n}{r}$ 等价于OGF乘法 $(1+x)^m (1+x)^n = (1+x)^{m+n}$ 中 $x^r$ 的系数相等，生成函数提供了组合恒等式的统一证明框架。二项式定理、负二项式展开等都是此框架的特例。

**通往高级主题的路径**：掌握OGF与EGF后，可进一步学习