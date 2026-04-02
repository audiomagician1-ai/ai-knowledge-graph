---
id: "expectation-variance"
concept: "期望与方差"
domain: "mathematics"
subdomain: "probability"
subdomain_name: "概率论"
difficulty: 6
is_milestone: false
tags: ["里程碑"]
content_version: 3
quality_tier: "S"
quality_score: 92.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.94
last_scored: "2026-03-22"
sources:
  - type: "textbook"
    ref: "Sheldon Ross. A First Course in Probability, 10th Ed., Ch.4"
  - type: "textbook"
    ref: "Blitzstein & Hwang. Introduction to Probability, 2nd Ed., Ch.4"
  - type: "academic"
    ref: "Feller, William. An Introduction to Probability Theory, Vol.1, 1968"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 期望与方差

## 概述

期望（Expected Value）是随机变量的"加权平均值"，用 $E(X)$ 或 $\mu$ 表示，权重由概率分布决定。对离散随机变量，$E(X) = \sum_i x_i p_i$；对连续随机变量，$E(X) = \int_{-\infty}^{+\infty} x f(x)\,dx$，其中 $f(x)$ 是概率密度函数。期望的本质是对随机变量长期平均行为的刻画，而非某次观测的预测值。

方差（Variance）度量随机变量偏离其期望的程度，定义为 $\text{Var}(X) = E\left[(X - \mu)^2\right]$，等价形式为 $\text{Var}(X) = E(X^2) - [E(X)]^2$。这一等价公式在计算中极为常用：先分别计算 $E(X^2)$ 和 $E(X)$，再相减，避免了先求 $(X-\mu)^2$ 再取期望的繁琐步骤。方差的量纲是原变量量纲的平方，因此实践中常用标准差 $\sigma = \sqrt{\text{Var}(X)}$ 来描述离散程度。

期望概念可追溯至17世纪，帕斯卡与费马在1654年通信讨论"赌注分配问题"时首次系统使用了期望的思想。惠更斯于1657年在《论掷骰子游戏的计算》中给出了首个正式定义。理解期望与方差是构建中心极限定理、大数定律、最小二乘回归和风险管理模型的前提。

---

## 核心原理

### 期望的线性性质

期望最重要的性质是**线性性**：对任意随机变量 $X$、$Y$ 和常数 $a$、$b$、$c$，有

$$E(aX + bY + c) = aE(X) + bE(Y) + c$$

此性质**无需 $X$ 与 $Y$ 独立**即成立，这使它区别于方差的对应性质。例如，若 $X \sim B(n, p)$（二项分布），可将 $X$ 分解为 $n$ 个独立伯努利变量之和，每个期望为 $p$，因此 $E(X) = np$，无需直接对 $\sum_{k=0}^n k\binom{n}{k}p^k(1-p)^{n-k}$ 求和。

### 方差的运算规则

方差**不具线性性**，而有以下规则：

$$\text{Var}(aX + b) = a^2 \text{Var}(X)$$

常数平移 $b$ 不影响方差，因为方差只衡量散布程度，与位置无关。对两个随机变量之和：

$$\text{Var}(X + Y) = \text{Var}(X) + \text{Var}(Y) + 2\text{Cov}(X, Y)$$

当 $X$ 与 $Y$ **独立**时，$\text{Cov}(X,Y) = 0$，方差才可相加。协方差定义为 $\text{Cov}(X,Y) = E(XY) - E(X)E(Y)$，若 $X$、$Y$ 独立则 $E(XY) = E(X)E(Y)$，协方差为零。注意：协方差为零（不相关）不等于独立。

### 常见分布的期望与方差

以下几个结果须熟记：

| 分布 | 期望 | 方差 |
|------|------|------|
| $B(n,p)$ | $np$ | $np(1-p)$ |
| $P(\lambda)$（泊松） | $\lambda$ | $\lambda$ |
| $U(a,b)$（均匀） | $\dfrac{a+b}{2}$ | $\dfrac{(b-a)^2}{12}$ |
| $\text{Exp}(\lambda)$（指数） | $\dfrac{1}{\lambda}$ | $\dfrac{1}{\lambda^2}$ |
| $N(\mu, \sigma^2)$（正态） | $\mu$ | $\sigma^2$ |

泊松分布的期望与方差相等（均为 $\lambda$），这一特殊性质可用于检验实际数据是否服从泊松分布：若样本均值与样本方差显著不等，则泊松假设可疑。

### 无穷期望的情形

期望并非对所有随机变量都存在。**圣彼得堡悖论**中，奖金 $X = 2^k$（$k$ 为首次正面出现的投掷次数），其期望 $E(X) = \sum_{k=1}^{\infty} 2^k \cdot \frac{1}{2^k} = \sum_{k=1}^{\infty} 1 = +\infty$，导致理论上任何有限赌注都值得参与，与实际直觉矛盾。柯西分布 $f(x) = \frac{1}{\pi(1+x^2)}$ 的期望同样不存在（积分不绝对收敛）。

---

## 实际应用

**保险定价**：设某险种赔付额 $X$ 的期望为 $E(X) = 5000$ 元，方差 $\text{Var}(X) = 4\times10^6$（即标准差 $\sigma = 2000$ 元）。保险公司的纯保费至少设为 $E(X)$，风险附加保费则与 $\sigma$ 正相关。若同时承保 $n$ 份相互独立的相同险种，总赔付 $S_n = \sum_{i=1}^n X_i$ 满足 $E(S_n) = 5000n$，$\text{Var}(S_n) = 4\times10^6 n$，人均标准差从 $2000$ 降至 $\frac{2000}{\sqrt{n}}$，体现了大数池化效应。

**投资组合**：若资产 $A$ 收益率期望为 $\mu_A = 0.08$，$B$ 为 $\mu_B = 0.05$，持仓权重各占一半，则组合期望收益为 $0.5 \times 0.08 + 0.5 \times 0.05 = 0.065$。组合方差 $\text{Var}(0.5A + 0.5B) = 0.25\sigma_A^2 + 0.25\sigma_B^2 + 0.5\text{Cov}(A,B)$，当两资产负相关时协方差为负，组合方差小于各资产方差的加权均值，此即分散化原理。

**质量控制**：某生产线产品尺寸服从 $N(\mu, \sigma^2)$，期望 $\mu$ 偏移反映系统性误差（需校准机器），方差 $\sigma^2$ 偏大反映随机误差（需改进工艺），两者诊断的问题来源不同，须分开处理。

---

## 常见误区

**误区一：期望是最可能出现的值**。期望是加权平均，不等于众数（Mode）。例如，$X \sim P(0.5)$（泊松，$\lambda=0.5$）时，$E(X)=0.5$，但最可能的取值是 $x=0$（概率约为0.607）。当分布高度偏斜时，期望与众数之间可以相差悬殊。

**误区二：方差可加只需期望可加**。$\text{Var}(X+Y) = \text{Var}(X)+\text{Var}(Y)$ 要求 $X$ 与 $Y$ **不相关**（协方差为零），远比"期望可加"的条件严格。具体反例：令 $Y = X$，则 $\text{Var}(X+Y) = \text{Var}(2X) = 4\text{Var}(X) \neq 2\text{Var}(X)$。

**误区三：$E(g(X)) = g(E(X))$**。这是詹森不等式（Jensen's Inequality）告诫的错误：只有当 $g$ 是线性函数时等号成立。若 $g$ 是凸函数（如 $g(x)=x^2$），则 $E(X^2) \geq [E(X)]^2$，差值恰好是 $\text{Var}(X)$。若 $g$ 是凹函数（如 $g(x)=\ln x$），不等号反向。忽视这一点会在对数收益率与算术收益率的转换中引入系统性偏差。

---

## 知识关联

**前置知识**：离散分布（伯努利、二项、泊松）和连续分布（均匀、正态、指数）为期望与方差的计算提供了具体对象。若不熟悉 $\sum_{k=0}^n k\binom{n}{k}p^k$ 的求和技巧或 $\int x e^{-\lambda x}dx$ 的积分，则无法完成基本计算。

**后续展开**：切比雪夫不等式直接用到 $\text{Var}(X)$，给出 $P(|X-\mu| \geq k\sigma) \leq \frac{1}{k^2}$ 的界，是对方差意义的首次深化应用。大数定律说明样本均值 $\bar{X}_n$ 以概率1收敛到 $E(X)$，其收敛速度由 $\text{Var}(X)/n$ 控制。矩母函数 $M_X(t) = E(e^{tX})$ 在 $t=0$ 处的各阶导数依次给出各阶矩，$M_X'(0) = E(X)$，$M_X''(0) = E(X^2)$，从而 $\text{Var}(X) = M_X''(0) - [M_X'(0)]