---
id: "maximum-likelihood"
concept: "最大似然估计详解"
domain: "mathematics"
subdomain: "statistics"
subdomain_name: "数理统计"
difficulty: 8
is_milestone: false
tags: ["理论"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-25
---

# 最大似然估计详解

## 概述

最大似然估计（Maximum Likelihood Estimation，MLE）是由英国统计学家Ronald A. Fisher于1912年提出、并在1922年系统阐述的参数估计方法。其核心思想是：在已观测到样本数据的条件下，选取使该样本"最有可能"被产生的参数值作为真实参数的估计量。换言之，MLE寻找参数 $\hat{\theta}$，使得观测数据在该参数下的概率（或概率密度）乘积达到最大。

与矩估计等方法不同，MLE直接利用了分布族的完整概率结构，而非仅匹配样本矩。这使得MLE在大样本下具有无偏性、一致性和渐近有效性三重优良性质，是Cramér-Rao下界的渐近达到者。在计量经济学中，线性回归的OLS估计量在正态误差假设下等价于MLE，而Logit/Probit等有限因变量模型则必须依赖MLE求解，这使MLE成为从线性到非线性模型的枢纽性工具。

## 核心原理

### 似然函数的构造

设 $X_1, X_2, \ldots, X_n$ 为来自总体 $f(x;\theta)$ 的独立同分布样本，观测值为 $x_1, \ldots, x_n$，则**似然函数**定义为：

$$L(\theta) = \prod_{i=1}^{n} f(x_i; \theta)$$

注意似然函数与联合密度函数的形式相同，但视角相反：联合密度是固定 $\theta$ 对 $x$ 求值，而似然函数是固定 $x$ 对 $\theta$ 求值。由于连乘在数值上易导致下溢，实践中通常最大化**对数似然函数**：

$$\ell(\theta) = \sum_{i=1}^{n} \ln f(x_i; \theta)$$

MLE估计量 $\hat{\theta}_{MLE}$ 满足一阶条件（得分方程）：

$$\frac{\partial \ell(\theta)}{\partial \theta} = \sum_{i=1}^{n} \frac{\partial \ln f(x_i; \theta)}{\partial \theta} = 0$$

以正态分布 $N(\mu, \sigma^2)$ 为例，对 $\mu$ 求解得分方程可得 $\hat{\mu}_{MLE} = \bar{x}$，对 $\sigma^2$ 求解得 $\hat{\sigma}^2_{MLE} = \frac{1}{n}\sum_{i=1}^n(x_i - \bar{x})^2$——注意分母是 $n$ 而非 $n-1$，故MLE对方差的估计是有偏的（小样本偏小）。

### Fisher信息与Cramér-Rao下界

**Fisher信息量**衡量样本数据对参数 $\theta$ 的信息含量，单个观测的Fisher信息定义为：

$$\mathcal{I}(\theta) = E\left[\left(\frac{\partial \ln f(X;\theta)}{\partial \theta}\right)^2\right] = -E\left[\frac{\partial^2 \ln f(X;\theta)}{\partial \theta^2}\right]$$

两个等价表达式的成立需要正则条件（包括对 $\theta$ 微分与积分可交换）。$n$ 个独立同分布观测的总Fisher信息为 $n\mathcal{I}(\theta)$。

**Cramér-Rao下界**指出，对 $\theta$ 的任何无偏估计量 $\tilde{\theta}$，其方差必须满足：

$$\mathrm{Var}(\tilde{\theta}) \geq \frac{1}{n\mathcal{I}(\theta)}$$

MLE在大样本下渐近达到此下界，即 $\hat{\theta}_{MLE}$ 是**渐近有效估计量**，没有任何其他一致估计量在大样本下拥有更小的渐近方差。以泊松分布 $\text{Poisson}(\lambda)$ 为例，$\mathcal{I}(\lambda) = 1/\lambda$，Cramér-Rao下界为 $\lambda/n$，而 $\hat{\lambda}_{MLE} = \bar{x}$ 的方差恰好等于 $\lambda/n$，在有限样本下即达到下界。

### 渐近分布与大样本性质

MLE具备以下三条核心渐近性质，这些性质在正则条件满足时成立：

1. **一致性**：$\hat{\theta}_{MLE} \xrightarrow{p} \theta_0$（真实参数），即随样本量 $n \to \infty$，估计量依概率收敛于真值。
2. **渐近正态性**：$\sqrt{n}(\hat{\theta}_{MLE} - \theta_0) \xrightarrow{d} N(0, \mathcal{I}(\theta_0)^{-1})$，这为构造置信区间和假设检验提供了理论依据。
3. **渐近有效性**：如前所述，渐近方差达到Cramér-Rao下界。

**不变性原理**是MLE的另一实用特性：若 $\hat{\theta}_{MLE}$ 是 $\theta$ 的MLE，则对任意函数 $g$，$g(\hat{\theta}_{MLE})$ 是 $g(\theta)$ 的MLE。例如，若 $\hat{\sigma}^2_{MLE}$ 已知，则 $\hat{\sigma}_{MLE} = \sqrt{\hat{\sigma}^2_{MLE}}$ 自动成为标准差的MLE，无需重新求解。

## 实际应用

**二元Logit模型**是MLE最典型的计量经济学应用场景。设因变量 $Y_i \in \{0,1\}$，$P(Y_i=1|x_i) = \Lambda(x_i'\beta) = \frac{e^{x_i'\beta}}{1+e^{x_i'\beta}}$，则对数似然函数为：

$$\ell(\beta) = \sum_{i=1}^{n}\left[y_i \ln\Lambda(x_i'\beta) + (1-y_i)\ln(1-\Lambda(x_i'\beta))\right]$$

此函数对 $\beta$ 无封闭解，必须使用Newton-Raphson迭代（IRLS算法）数值求解，迭代公式为 $\beta^{(t+1)} = \beta^{(t)} - H^{-1}(\beta^{(t)})g(\beta^{(t)})$，其中 $H$ 为Hessian矩阵。Logit的对数似然是严格凹函数，保证全局唯一最大值存在。

**生存分析中的指数模型**：若生存时间 $T_i \sim \text{Exp}(\lambda)$，且存在右截断（censoring），截断观测的似然贡献为生存函数 $S(t_i;\lambda) = e^{-\lambda t_i}$，而非密度函数。混合似然函数为：

$$L(\lambda) = \prod_{i: \text{uncensored}} \lambda e^{-\lambda t_i} \cdot \prod_{i: \text{censored}} e^{-\lambda t_i}$$

## 常见误区

**误区一：似然值本身可以比较不同模型**。许多初学者将两个模型的似然函数值 $L(\hat{\theta}_A)$ 和 $L(\hat{\theta}_B)$ 直接比较大小，但似然值的绝对大小受样本量、分布类型影响，对连续分布甚至没有概率解释（密度值可以大于1）。正确做法是使用**对数似然比统计量** $LR = -2[\ell(\hat{\theta}_{\text{restricted}}) - \ell(\hat{\theta}_{\text{unrestricted}})]$，在原假设下渐近服从 $\chi^2(r)$ 分布，其中 $r$ 为约束个数。

**误区二：MLE总是无偏的**。MLE的优良性质是渐近的，小样本下可能存在显著偏差。正态分布方差的MLE $\hat{\sigma}^2_{MLE} = \frac{1}{n}\sum(x_i-\bar{x})^2$ 满足 $E[\hat{\sigma}^2_{MLE}] = \frac{n-1}{n}\sigma^2$，偏差为 $-\frac{\sigma^2}{n}$。样本量越小，偏差越大。此外，非线性变换 $g(\hat{\theta}_{MLE})$ 在有限样本下通常也是有偏的，尽管MLE的不变性保证其仍为MLE。

**误区三：得分方程有解就等于找到了最大值**。得分方程 $\partial\ell/\partial\theta = 0$ 是极值的必要条件，需验证Hessian矩阵 $\frac{\partial^2\ell}{\partial\theta\partial\theta'}$ 在解处为**负定矩阵**才能确认为极大值。对于多峰似然函数（如有限混合模型），数值优化可能陷入局部极大值，需从多个初值出发求解。

## 知识关联

从**线性回归**过渡到MLE的关键步骤是认识到：经典线性回归 $Y = X\beta + \varepsilon$（$\varepsilon \sim N(0,\sigma^2 I)$）在正态假设下的OLS估计量与MLE完全等价，因为最小化残差平方和等价于最大化正态对数似然。这一等价性将OLS的几何直觉与MLE的概率框架统一起来。

从**点估计**的矩估计框架到MLE，核心转变在于信息利用的充分性：矩估计仅使用样本矩匹配总体矩（最多用到二阶矩），而MLE利用完整的概率密度结构。当总体分布与假设一致时，MLE的渐近效率严格优于或等于矩估计。

MLE的掌握是理解**有