---
id: "power-series"
concept: "幂级数"
domain: "mathematics"
subdomain: "calculus"
subdomain_name: "微积分"
difficulty: 7
is_milestone: false
tags: ["进阶"]

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

# 幂级数

## 概述

幂级数是形如 $\sum_{n=0}^{\infty} a_n (x - x_0)^n$ 的函数项级数，其中 $a_n$ 称为幂级数的系数，$x_0$ 称为展开中心（通常取 $x_0 = 0$，化为 $\sum_{n=0}^{\infty} a_n x^n$）。与数项级数不同，幂级数的每一项都是关于 $x$ 的多项式，其收敛性随 $x$ 的取值而变化，因此幂级数定义的是一个以 $x$ 为自变量的函数，而非单一数值。

幂级数的系统研究始于18世纪。欧拉（Euler）在1748年的著作《无穷分析引论》中广泛使用了幂级数展开，但严格收敛理论的建立要归功于19世纪初的柯西（Cauchy）和阿贝尔（Abel）。阿贝尔在1826年发表的论文中首次严格证明了关于幂级数在收敛圆盘边界处行为的定理，奠定了幂级数理论的逻辑基础。

幂级数的重要性在于它将解析函数的局部行为完整编码为一列系数 $\{a_n\}$。通过收敛半径，可以精确刻画幂级数代表的函数的定义域；通过逐项求导和逐项积分，可以在无需额外验证的前提下对函数进行微积分运算——这是普通函数项级数所不具备的特权。

---

## 核心原理

### 收敛半径与收敛区间

对任意幂级数 $\sum_{n=0}^{\infty} a_n x^n$，存在唯一的**收敛半径** $R \in [0, +\infty]$，使得当 $|x| < R$ 时级数绝对收敛，当 $|x| > R$ 时级数发散。收敛半径由 **Hadamard 公式**给出：

$$R = \frac{1}{\limsup_{n \to \infty} |a_n|^{1/n}}$$

实践中更常用**比值法**：若 $\lim_{n\to\infty} \left|\dfrac{a_{n+1}}{a_n}\right| = \rho$，则 $R = \dfrac{1}{\rho}$。

关键细节在于**端点处的收敛性需单独判断**：$x = R$ 和 $x = -R$ 处级数可能收敛也可能发散，构成四种不同的收敛区间类型：$(−R, R)$、$[−R, R)$、$(−R, R]$、$[−R, R]$。例如，$\sum_{n=1}^{\infty} \dfrac{x^n}{n}$ 的收敛半径为 $R=1$，在 $x=-1$ 处收敛（交错调和级数），在 $x=1$ 处发散（调和级数）。

### Abel 定理

Abel 第一定理指出：若幂级数 $\sum a_n x^n$ 在 $x = R$ 处收敛，则其和函数在 $x = R$ 处左连续；对应地，若在 $x = -R$ 处收敛，则右连续。精确表述为：

$$\lim_{x \to R^-} \sum_{n=0}^{\infty} a_n x^n = \sum_{n=0}^{\infty} a_n R^n$$

这个定理的非平凡之处在于：它允许将**内部的极限与求和交换**，而一般函数项级数无此性质。典型应用是借助已知的 $\ln 2 = 1 - \dfrac{1}{2} + \dfrac{1}{3} - \cdots$，通过对 $\ln(1+x) = \sum_{n=1}^{\infty} \dfrac{(-1)^{n-1}}{n} x^n$（收敛半径 $R=1$）在 $x=1$ 处应用 Abel 定理，严格证明上述等式成立。

### 逐项求导与逐项积分

幂级数在收敛区间内部（即开区间 $(-R, R)$ 内）具有**任意阶连续导数**，且可以逐项求导和逐项积分，所得级数与原级数有相同的收敛半径 $R$：

$$\frac{d}{dx}\sum_{n=0}^{\infty} a_n x^n = \sum_{n=1}^{\infty} n a_n x^{n-1}, \quad |x| < R$$

$$\int_0^x \sum_{n=0}^{\infty} a_n t^n \, dt = \sum_{n=0}^{\infty} \frac{a_n}{n+1} x^{n+1}, \quad |x| < R$$

注意：逐项求导后收敛半径不变，但端点处的收敛性可能改变。例如 $\sum_{n=1}^{\infty} \dfrac{x^n}{n}$ 在 $x=-1$ 收敛，求导后得 $\sum_{n=1}^{\infty} x^{n-1} = \dfrac{1}{1-x}$，在 $x=-1$ 处已发散。

---

## 实际应用

**求函数展开式**：利用已知展开式 $\dfrac{1}{1-x} = \sum_{n=0}^{\infty} x^n$（$|x|<1$），通过逐项积分可得 $-\ln(1-x) = \sum_{n=1}^{\infty} \dfrac{x^n}{n}$；对 $\dfrac{1}{1+x^2} = \sum_{n=0}^{\infty} (-1)^n x^{2n}$ 逐项积分，直接得到 $\arctan x = \sum_{n=0}^{\infty} \dfrac{(-1)^n x^{2n+1}}{2n+1}$，避免了直接求高阶导数的繁琐。

**求数项级数之和**：将 $\arctan 1 = \dfrac{\pi}{4}$ 代入 $\arctan x$ 的展开式，需结合 Abel 定理在 $x=1$ 处的连续性（因 $\sum_{n=0}^{\infty} \dfrac{(-1)^n}{2n+1}$ 收敛），立得 **Leibniz 公式** $\dfrac{\pi}{4} = 1 - \dfrac{1}{3} + \dfrac{1}{5} - \cdots$。

**求解常微分方程**：幂级数方法（Frobenius 方法）可求解如 Bessel 方程 $x^2 y'' + xy' + (x^2 - \nu^2)y = 0$ 的幂级数解，通过代入 $y = \sum a_n x^n$ 确定递推系数关系。

---

## 常见误区

**误区一：收敛半径等于收敛区间的半长度，就可忽略端点检验。** 许多学生认为 $R=1$ 就意味着收敛区间是 $(-1,1)$，但端点 $\pm 1$ 处的收敛性依赖具体系数 $a_n$ 的行为，必须单独使用数项级数收敛判别法（如 Leibniz 判别法、Dirichlet 判别法）检验。

**误区二：逐项求导后收敛半径会缩小。** 实际上逐项求导和逐项积分均不改变收敛半径，这由 Hadamard 公式保证：$\lim |na_n|^{1/n} = \lim |a_n|^{1/n}$，因为 $n^{1/n} \to 1$。学生常错误地认为"系数变大"会导致收敛域缩小，混淆了系数大小与上极限的关系。

**误区三：Abel 定理允许在端点处任意交换极限与求和。** Abel 定理的成立前提是级数在该端点处**本身收敛**。若级数在 $x=R$ 处发散，则不能断言 $\lim_{x\to R^-} \sum a_n x^n$ 等于 $\sum a_n R^n$，后者根本没有意义。

---

## 知识关联

**前置知识**：幂级数的收敛性分析直接调用**数项级数**的比值判别法和根值判别法，收敛半径公式是这两个判别法在函数项语境下的自然推广。**泰勒展开**则提供了幂级数系数的具体来源：若 $f(x)$ 在 $x_0$ 处无穷次可微，则 $a_n = \dfrac{f^{(n)}(x_0)}{n!}$；幂级数理论的逐项求导定理反过来也严格证明了泰勒级数的合法性。

**后续概念**：**生成函数**将幂级数 $\sum_{n=0}^{\infty} a_n x^n$ 视为数列 $\{a_n\}$ 的编码工具，利用幂级数的代数运算（乘法对应卷积、求导对应移位变换）来求解组合计数和递推关系。幂级数的逐项运算规则是生成函数方法得以机械化操作的数学基础。