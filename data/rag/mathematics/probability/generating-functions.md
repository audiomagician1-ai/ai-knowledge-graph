---
id: "generating-functions"
concept: "生成函数"
domain: "mathematics"
subdomain: "probability"
subdomain_name: "概率论"
difficulty: 8
is_milestone: false
tags: ["拓展"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 生成函数（概率论）

## 概述

概率生成函数（Probability Generating Function，简称 PGF）是将离散随机变量的概率分布编码为一个幂级数的数学工具。对于取非负整数值的随机变量 $X$，其概率生成函数定义为：

$$G_X(z) = \mathbb{E}[z^X] = \sum_{k=0}^{\infty} P(X = k) \cdot z^k$$

其中 $z$ 是一个复数或实数参数，级数在 $|z| \leq 1$ 时绝对收敛。PGF 的思想可追溯至 18 世纪，拉普拉斯（Laplace）在 1812 年的《概率分析理论》中系统使用了类似的母函数技术来处理组合与概率问题。棣莫弗（de Moivre）更早在 1718 年分析赌徒破产问题时已隐含使用了生成函数的思路。

PGF 之所以在概率论中受到重视，是因为它将卷积运算（独立随机变量之和的分布）转化为代数乘法，将递推关系转化为代数方程，从而极大简化了计算过程。特别地，对于分支过程、随机游走、排队论等涉及递推结构的问题，PGF 提供了系统性的分析框架。

---

## 核心原理

### 从概率分布到幂级数的编码

PGF 的构造本质是以概率值作为幂级数的系数。对于泊松分布 $X \sim \text{Poisson}(\lambda)$，代入定义得：

$$G_X(z) = \sum_{k=0}^{\infty} \frac{e^{-\lambda}\lambda^k}{k!} z^k = e^{-\lambda} \sum_{k=0}^{\infty} \frac{(\lambda z)^k}{k!} = e^{\lambda(z-1)}$$

这个紧凑的闭合表达式将无穷多个概率值压缩为一个初等函数。对于几何分布 $P(X=k) = (1-p)^k p$（$k=0,1,2,\ldots$），其 PGF 为：

$$G_X(z) = \frac{p}{1-(1-p)z}, \quad |z| < \frac{1}{1-p}$$

提取第 $k$ 阶系数就能还原 $P(X=k)$，这与幂级数展开一一对应。

### 矩的提取公式

PGF 对 $z$ 求导后令 $z=1$ 可系统提取各阶阶乘矩（factorial moments）。具体地：

$$G_X'(1) = \mathbb{E}[X]$$
$$G_X''(1) = \mathbb{E}[X(X-1)]$$
$$G_X^{(r)}(1) = \mathbb{E}[X(X-1)\cdots(X-r+1)]$$

因此方差可以写为 $\text{Var}(X) = G_X''(1) + G_X'(1) - [G_X'(1)]^2$。对于上述泊松分布，$G_X'(z) = \lambda e^{\lambda(z-1)}$，于是 $G_X'(1) = \lambda$，$G_X''(1) = \lambda^2$，进而 $\text{Var}(X) = \lambda^2 + \lambda - \lambda^2 = \lambda$，与已知结论吻合。这套求矩方法比直接计算期望更机械化、更易推广。

### 独立随机变量之和与乘法定理

若 $X$ 与 $Y$ 相互独立，则 $Z = X + Y$ 的 PGF 满足：

$$G_Z(z) = G_X(z) \cdot G_Y(z)$$

这是 PGF 最核心的代数性质。其证明直接来自独立性：$\mathbb{E}[z^{X+Y}] = \mathbb{E}[z^X]\mathbb{E}[z^Y]$。推论：$n$ 个独立同分布的随机变量之和的 PGF 是单个变量 PGF 的 $n$ 次幂。例如，$n$ 个独立 $\text{Poisson}(\lambda)$ 之和的 PGF 为 $[e^{\lambda(z-1)}]^n = e^{n\lambda(z-1)}$，对应 $\text{Poisson}(n\lambda)$ 分布，直接验证了泊松分布的可加性。

### 递推关系与生成函数方程

许多概率问题以递推形式出现，PGF 可将递推转化为代数方程求解。以 Galton-Watson 分支过程为例，设每个个体产生后代数的 PGF 为 $f(z)$，则第 $n$ 代种群规模的 PGF 满足：

$$G_n(z) = f(G_{n-1}(z)) = \underbrace{f \circ f \circ \cdots \circ f}_{n \text{ 次}}(z)$$

灭绝概率 $q$（即种群最终灭绝的概率）是方程 $f(z) = z$ 在 $[0,1]$ 内的最小非负根。当 $f'(1) = \mu \leq 1$（均值不超过 1）时，$q=1$（必然灭绝）；当 $\mu > 1$ 时，$q < 1$，且 $q$ 是 $f(z)=z$ 在 $(0,1)$ 内的唯一根。这一结论完全依赖 PGF 的迭代结构得出。

---

## 实际应用

**赌徒破产问题**：令 $p$ 为赢一局的概率，$q=1-p$。设从资金 $k$ 出发最终破产（到达 $0$）的概率满足递推 $u_k = p \cdot u_{k+1} + q \cdot u_{k-1}$。对此线性递推引入生成函数 $U(z) = \sum_{k=1}^{N-1} u_k z^k$，可将边界条件与递推同时编码，从而系统求解 $u_k = \left(\frac{q}{p}\right)^k$ 形式的解（$p \neq q$ 时）。

**随机游走首达时分布**：对于对称一维随机游走（$p=1/2$），从原点出发首次返回原点的时刻 $T$ 的 PGF 为：

$$G_T(z) = 1 - \sqrt{1-z^2}$$

其系数给出首达时恰为 $2n$ 步的概率 $P(T=2n) = \frac{1}{2n-1}\binom{2n}{n}\frac{1}{4^n}$，此结果通过 PGF 提取系数远比组合计数直接。

**复合泊松分布**：若索赔次数 $N \sim \text{Poisson}(\lambda)$，每次索赔额 $X_i$ 独立同分布，则总索赔额 $S = \sum_{i=1}^N X_i$ 的 PGF（当 $X_i$ 取整数值时）为：

$$G_S(z) = G_N(G_X(z)) = e^{\lambda(G_X(z)-1)}$$

这是**复合分布**的 PGF 公式，广泛用于精算学中的破产概率计算。

---

## 常见误区

**误区一：混淆 PGF 与矩母函数（MGF）**。PGF 的参数是 $z^X$（$z$ 为底数），而矩母函数是 $e^{tX}$（$t$ 为参数）。二者的关系是 $G_X(e^t) = M_X(t)$，但 PGF 仅适用于取非负整数值的离散随机变量，而 MGF 适用范围更广。将连续分布套用 PGF 公式会导致级数无意义。

**误区二：认为 $G_X(1) = 1$ 是平凡的因而忽略它的作用**。实际上 $G_X(1) = \sum_{k=0}^\infty P(X=k) = 1$ 是验证全概率归一化的必要条件，也是判断级数收敛域的关键出发点。对于某些亚概率生成函数（如分支过程中的灭绝分析），$G_X(1) < 1$ 恰好表明存在以正概率"逃逸至无穷"的情形，不可忽视。

**误区三：认为乘法定理 $G_{X+Y}(z)=G_X(z)G_Y(z)$ 在相关情形下仍成立**。该公式严格依赖 $X$ 与 $Y$ 的独立性。若 $X$ 与 $Y$ 相关，例如 $(X,Y)$ 服从二维负二项分布，则须使用联合 PGF $G(z_1, z_2) = \mathbb{E}[z_1^X z_2^Y]$，不可直接分解为两个单变量 PGF 的乘积。

---

## 知识关联

**与幂级数的关系**：PGF 的收敛性分析依赖幂级数理论，$G_X(z)$ 的收敛半径 $R \geq 1$（由于 $\sum P(X=k)=1$ 收敛）。幂级数的逐项求导定理保证了提取矩公式的合法性。二项式定理直接给出二项分布 $B(n,p)$ 的 PGF：$G_X(z) = (pz+1-p)^n$，这是 PGF 与二项式定理最直接的交汇点。

**向离散生成函数的延伸**：概率生成函数是组合数学中**普通生成函数**（Ordinary Generating Function，OGF）在概率语境下的特例，其中系数被赋予了概率意义的约束（