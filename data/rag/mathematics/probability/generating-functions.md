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
# 生成函数（概率论）

## 概述

概率生成函数（Probability Generating Function，简称 PGF）是处理非负整数值随机变量的强大工具，其定义为：若随机变量 $X$ 取非负整数值，则其概率生成函数为 $G_X(z) = \mathbb{E}[z^X] = \sum_{k=0}^{\infty} P(X=k)\, z^k$，其中 $z$ 是形式变量，级数在 $|z| \leq 1$ 的范围内收敛。这一定义将随机变量的全部概率信息"编码"进一个幂级数的系数序列，使得概率分布与解析函数之间建立了直接对应。

生成函数的思想可追溯至 Abraham de Moivre 在 1730 年代对递推数列的研究，以及拉普拉斯（Laplace）在 18 世纪末对"生成函数"概念的系统化。在概率论中，Galton 和 Watson 于 1874 年将概率生成函数应用于分支过程（Galton-Watson 过程），分析种群灭绝概率，这是 PGF 最早的概率论应用之一，至今仍是教学的标准范例。

PGF 的价值在于它将卷积运算转化为乘法运算：若 $X$ 与 $Y$ 独立，则 $G_{X+Y}(z) = G_X(z) \cdot G_Y(z)$。这一性质使得计算 $n$ 个独立同分布随机变量之和的分布，从繁琐的卷积求和直接变为函数的幂次运算，从而高效求解递推关系和分布族问题。

## 核心原理

### 从系数提取概率与矩

PGF 最直接的用法是通过对 $z$ 求导来提取概率值和矩。具体地，$P(X = k) = \dfrac{G_X^{(k)}(0)}{k!}$，即第 $k$ 阶导数在 $z=0$ 处的值除以 $k!$。均值和方差则通过以下公式获得：

$$\mathbb{E}[X] = G_X'(1), \qquad \text{Var}(X) = G_X''(1) + G_X'(1) - [G_X'(1)]^2$$

注意这里必须在 $z=1$ 处求值，而非 $z=0$。以泊松分布 $\text{Poisson}(\lambda)$ 为例，其 PGF 为 $G(z) = e^{\lambda(z-1)}$，对其求导得 $G'(z) = \lambda e^{\lambda(z-1)}$，令 $z=1$ 得 $\mathbb{E}[X] = \lambda$，与定义完全吻合。

### 独立和的卷积转乘积

设 $X_1, X_2, \ldots, X_n$ 独立同分布，每个变量的 PGF 均为 $G(z)$，则 $S_n = X_1 + \cdots + X_n$ 的 PGF 为 $G_{S_n}(z) = [G(z)]^n$。这一性质是 PGF 处理递推关系的核心机制。以几何分布为例，若 $X \sim \text{Geom}(p)$（表示首次成功所需试验次数），其 PGF 为 $G(z) = \dfrac{pz}{1-qz}$（其中 $q=1-p$），则等待第 $r$ 次成功所需次数（负二项分布）的 PGF 为 $\left(\dfrac{pz}{1-qz}\right)^r$，无需直接计算复杂的卷积公式。

### 递推关系的求解

PGF 在求解线性递推关系方面尤为有力。设概率序列 $\{p_k\}$ 满足递推 $p_k = \alpha p_{k-1} + \beta p_{k-2}$（$k \geq 2$），将其两侧乘以 $z^k$ 并对 $k$ 求和，可将递推关系转化为关于 $G(z)$ 的代数方程，然后通过部分分数分解来提取系数。例如，分支过程中后代数的 PGF 满足灭绝概率方程 $s = G(s)$，其最小非负实数根即为种群最终灭绝的概率。若后代均值 $\mu = G'(1) \leq 1$，则灭绝概率为 1；若 $\mu > 1$，灭绝概率严格小于 1，这一临界性质完全由 $G'(1)$ 的值决定。

### 复合分布与随机和

PGF 对"随机和"有特别简洁的处理方式：若 $N$ 是随机变量（取非负整数值），$X_1, X_2, \ldots$ 独立同分布且与 $N$ 独立，令 $S = X_1 + \cdots + X_N$（$N=0$ 时 $S=0$），则 $G_S(z) = G_N(G_X(z))$，即 PGF 的复合。这个公式直接给出了复合泊松分布、复合几何分布等复合分布族的完整概率结构，其均值为 $\mathbb{E}[S] = \mathbb{E}[N] \cdot \mathbb{E}[X]$，方差为 $\text{Var}(S) = \mathbb{E}[N]\,\text{Var}(X) + \mathbb{E}[X]^2\,\text{Var}(N)$。

## 实际应用

**Galton-Watson 分支过程**：设每个个体独立产生后代，后代数的 PGF 为 $G(z)$。第 $n$ 代种群规模的 PGF 满足递推 $G_n(z) = G_{n-1}(G(z))$，即 $G$ 的 $n$ 次函数复合 $G^{\circ n}(z)$。灭绝概率 $q_n = G_n(0)$ 随 $n$ 单调递增趋向最终灭绝概率 $q^* = G(q^*)$ 的最小根。若后代分布为 $\text{Poisson}(1.5)$，其 PGF 为 $e^{1.5(z-1)}$，方程 $s = e^{1.5(s-1)}$ 的最小正根约为 $0.583$，即该种群有约 $58.3\%$ 的概率最终灭绝。

**排队论中的等待时间分布**：在 M/G/1 排队模型的分析中，顾客数的 PGF 出现在 Pollaczek-Khinchine 公式里，通过 PGF 的部分分数分解可以直接得到稳态队列长度的分布，避免了直接求解无穷维的平衡方程组。

**赌徒破产问题**：设赌徒在每轮以概率 $p$ 赢 1 元、概率 $q=1-p$ 输 1 元，从 $k$ 元出发最终破产（到达 0 元）的概率满足递推方程，利用 PGF 方法可将其转化为特征方程 $\lambda^2 - (1/p)\lambda + q/p = 0$，两根之积为 $q/p$，进而得到破产概率的封闭形式 $\min\left(1,\, (q/p)^k\right)$。

## 常见误区

**误区一：将 PGF 与矩生成函数（MGF）混淆**。MGF 定义为 $M_X(t) = \mathbb{E}[e^{tX}]$，而 PGF 为 $G_X(z) = \mathbb{E}[z^X]$。两者通过代换 $z = e^t$ 相互联系，但 MGF 适用于任意实值随机变量，PGF 专门针对非负整数值分布。对连续型随机变量强行套用 PGF 公式是概念性错误，因为此时 $P(X=k)=0$（对所有整数 $k$），级数退化为零。

**误区二：认为 $G_X(1)$ 总等于 1 需要额外验证**。实际上，由 $G_X(1) = \sum_{k=0}^\infty P(X=k) = 1$ 这一等式本身就是概率归一化条件的体现，对任何合法的概率分布自动成立，无需单独验证——除非级数在 $z=1$ 处不收敛（这意味着所给"分布"不合法）。

**误区三：复合 PGF 公式 $G_S(z) = G_N(G_X(z))$ 要求 $N$ 与各 $X_i$ 独立**。许多学生在计算随机和时忽略独立性条件，若 $N$ 与 $X_i$ 相关（例如 $N$ 的取值依赖于部分 $X_i$ 的结果），复合公式不再成立，必须回到条件期望的基本定义重新推导。

## 知识关联

**前置知识**：掌握幂级数的收敛半径与逐项求导是操作 PGF 的基础——PGF 本质上是幂级数 $\sum p_k z^k$，Abel 定理保证了在 $|z|<1$ 内逐项求导的合法性。二项式定理则直接给出了二项分布 $B(n,p)$ 的 PGF：$G(z) = (q + pz)^n$，这是从二项式定理到 PGF 框架的最直观过渡。

**后续扩展**：概率论中的 PGF 是离散数学中一般"生成函数"技术的概率特化版本。进入"生成函数（离散）"的学习后，普通生成函数（
