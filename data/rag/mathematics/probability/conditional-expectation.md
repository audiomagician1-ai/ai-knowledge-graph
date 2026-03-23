---
id: "conditional-expectation"
concept: "条件期望"
domain: "mathematics"
subdomain: "probability"
subdomain_name: "概率论"
difficulty: 7
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 6
quality_tier: "pending-rescore"
quality_score: 40.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.393
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 条件期望

## 概述

条件期望（Conditional Expectation）是在已知某一事件或随机变量取值的条件下，另一随机变量的平均值。形式上，给定事件 $B$（且 $P(B)>0$），随机变量 $X$ 关于 $B$ 的条件期望定义为：

$$E(X \mid B) = \sum_x x \cdot P(X=x \mid B)$$

（离散情形），或 $E(X \mid B) = \int_{-\infty}^{+\infty} x \cdot f_{X|B}(x) \, dx$（连续情形）。它将普通期望从无条件情形推广到已知部分信息的情形，是概率论中将"信息"纳入计算的核心工具。

条件期望的现代严格定义由柯尔莫哥洛夫（Kolmogorov）在1933年建立测度论概率体系时给出：$E(X \mid \mathcal{F})$ 是 $X$ 关于 $\sigma$-代数 $\mathcal{F}$ 的条件期望，定义为满足特定可测性与积分条件的随机变量。这一抽象框架使条件期望在金融数学（鞅理论）、贝叶斯统计和随机过程中获得了严格的数学基础。在实际问题中，条件期望让我们能够利用已观察到的信息来精确预测未知量的平均水平，例如已知今天下雨，明天气温期望值是多少。

## 核心原理

### 离散型条件期望的计算

设 $X$ 和 $Y$ 均为离散型随机变量，则 $X$ 在 $Y=y$ 条件下的条件期望为：

$$E(X \mid Y=y) = \sum_x x \cdot P(X=x \mid Y=y) = \sum_x x \cdot \frac{P(X=x, Y=y)}{P(Y=y)}$$

例如，设二维分布中 $P(X=1, Y=1)=0.2$，$P(X=2, Y=1)=0.3$，$P(Y=1)=0.5$，则：

$$E(X \mid Y=1) = 1 \times \frac{0.2}{0.5} + 2 \times \frac{0.3}{0.5} = 0.4 + 1.2 = 1.6$$

这个值 $1.6$ 与无条件期望 $E(X)$ 一般不相等，正是因为 $Y=1$ 这一信息改变了 $X$ 的概率分布。

### 全期望公式（重期望定律）

全期望公式（Law of Total Expectation）表明：

$$E(X) = E[E(X \mid Y)]$$

其中内层期望 $E(X \mid Y)$ 本身是 $Y$ 的函数（也是随机变量），外层期望再对 $Y$ 求均值。对离散情形展开即为：

$$E(X) = \sum_y E(X \mid Y=y) \cdot P(Y=y)$$

这一公式的威力在于分层计算：若直接求 $E(X)$ 困难，可先固定 $Y$ 的取值求条件期望，再对 $Y$ 求期望。例如，设某保险公司一天的理赔次数 $N$ 服从参数为 $\lambda=5$ 的泊松分布，每次理赔金额 $X_i$ 的均值为 $\mu=1000$ 元，则总理赔额 $S = X_1+\cdots+X_N$ 满足：

$$E(S) = E[E(S \mid N)] = E[N\mu] = \mu \cdot E(N) = 1000 \times 5 = 5000 \text{ 元}$$

### 条件期望作为最优预测

从最小均方误差角度，$E(X \mid Y)$ 是利用 $Y$ 预测 $X$ 的最优（均方误差最小）预测量。具体地，对任意 $Y$ 的函数 $g(Y)$：

$$E[(X - E(X \mid Y))^2] \leq E[(X - g(Y))^2]$$

这意味着在所有仅依赖 $Y$ 的预测函数中，$E(X \mid Y)$ 使得预测误差的期望平方和最小。这一性质直接支撑了线性回归中最小二乘估计的理论地位——当 $E(X \mid Y)$ 恰好是 $Y$ 的线性函数时，线性回归给出全局最优解。

## 实际应用

**随机和的期望（复合分布）**：设某商店每天顾客数 $N \sim \text{Poisson}(\lambda)$，每位顾客消费额 $X_i$ 相互独立且同分布，均值为 $\mu$。总销售额 $S=\sum_{i=1}^N X_i$ 的期望用全期望公式可得 $E(S) = \lambda\mu$，而直接展开则需要复杂的级数运算。

**递推求解期望（赌徒破产问题）**：设赌徒每局赢概率为 $p$，输概率为 $1-p$，当前资金为 $k$，求达到目标金额 $N$ 的期望局数 $T_k$。利用条件期望建立递推：

$$E(T_k) = 1 + p \cdot E(T_{k+1}) + (1-p) \cdot E(T_{k-1})$$

这将原本复杂的随机过程问题转化为线性递推方程，当 $p=1/2$ 时解为 $E(T_k) = k(N-k)$。

**贝叶斯估计**：在贝叶斯框架中，参数 $\theta$ 被视为随机变量，观测数据为 $X$。后验期望 $E(\theta \mid X)$ 是 $\theta$ 在平方损失下的贝叶斯最优估计量。例如，若 $\theta \sim \text{Beta}(\alpha, \beta)$，$X \mid \theta \sim \text{Binomial}(n, \theta)$，则 $E(\theta \mid X=k) = \frac{\alpha+k}{\alpha+\beta+n}$，这是先验信息与样本信息的加权平均。

## 常见误区

**误区一：混淆 $E(X \mid Y=y)$（数值）与 $E(X \mid Y)$（随机变量）**

$E(X \mid Y=y)$ 在固定 $y$ 后是一个具体的实数，而 $E(X \mid Y)$ 是 $Y$ 的函数，是一个随机变量。全期望公式 $E(X) = E[E(X \mid Y)]$ 中，外层期望正是对这个随机变量求期望，若将内层误认为常数则公式失去意义。

**误区二：认为条件期望具有"条件独立性"——$E(X \mid Y) = E(X)$ 当且仅当 $X$ 与 $Y$ 不相关**

正确结论是：$E(X \mid Y) = E(X)$（几乎处处成立）当且仅当 $X$ 与 $Y$ **独立**，而非仅仅不相关。不相关仅表示线性无关，即 $E(XY) = E(X)E(Y)$，但非线性依赖关系仍可使条件期望随 $Y$ 变化。例如，$X \sim U(-1,1)$，$Y=X^2$，则 $X$ 与 $Y$ 不相关，但 $E(X \mid Y=y) = 0 \neq E(X) = 0$……注意此例中两者恰好相等；更典型的反例需仔细构造，核心是不相关不蕴含独立。

**误区三：全期望公式仅适用于有限个条件事件的划分**

全期望公式对连续型随机变量 $Y$ 同样成立：$E(X) = \int_{-\infty}^{+\infty} E(X \mid Y=y) \cdot f_Y(y) \, dy$。很多学生误以为该公式只能写成有限求和 $\sum_y E(X|Y=y)P(Y=y)$，从而回避连续型条件期望的计算，导致在涉及混合分布或连续先验的问题中无从下手。

## 知识关联

条件期望直接建立在**条件概率**的基础上：条件概率 $P(A \mid B)$ 给出了在已知 $B$ 发生时 $A$ 的概率，而条件期望用这套条件分布来计算加权平均，是条件概率向量化/期望化的自然延伸。同时，条件期望必须借助**期望的线性性**来简化运算，例如 $E(aX+b \mid Y) = aE(X \mid Y)+b$ 这一性质与无条件期望完全类比。

向更高阶概念延伸，条件期望是**鞅（Martingale）**理论的核心：随机过程 $\{M_n\}$ 是鞅，当且仅当 $E(M_{n+1} \mid M_1, \ldots, M_n) = M_n$ 几乎处处成立。在测度论框架下，条件期望 $E(X \mid \mathcal{F})$ 关于 $\sigma$-代数的定义则连接了**随机过程**与**信息流**（filtration）的概念，是现代金融数学中期权定价（Black-Scholes模型）的数学基础。
