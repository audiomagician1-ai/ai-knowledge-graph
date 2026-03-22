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
---
# 期望与方差

## 概述

期望（Expectation, E[X]）和方差（Variance, Var[X]）是概率论中描述随机变量的两个最基本的数字特征。期望度量随机变量的**中心位置**（"平均会得到什么"），方差度量其**离散程度**（"结果有多不确定"）。这两个量共同提供了任何分布最核心的"摘要信息"。

Feller（1968）指出：许多概率论的深刻定理——大数定律、中心极限定理——本质上都是关于期望和方差的陈述。掌握它们是理解整个概率论和统计学大厦的基石。

## 核心知识点

### 1. 期望 E[X] 的定义与计算

**离散型随机变量**：
E[X] = Sum over all x: x * P(X = x) = x1*p1 + x2*p2 + ... + xn*pn

**连续型随机变量**：
E[X] = Integral from -inf to +inf: x * f(x) dx

**直觉理解**：如果你重复同一随机实验无穷多次，观测值的算术平均将趋近于 E[X]。

**常见分布的期望**：

| 分布 | 参数 | E[X] | 直觉 |
|------|------|------|------|
| 伯努利 Bernoulli(p) | 成功概率 p | p | 一次试验的平均成功数 |
| 二项 Binomial(n,p) | n 次试验，成功率 p | np | n 次试验的平均成功数 |
| 泊松 Poisson(lambda) | 到达率 lambda | lambda | 单位时间平均事件数 |
| 均匀 Uniform(a,b) | 区间 [a,b] | (a+b)/2 | 区间中点 |
| 指数 Exp(lambda) | 率参数 lambda | 1/lambda | 平均等待时间 |
| 正态 N(mu, sigma^2) | 均值 mu，方差 sigma^2 | mu | 对称中心 |

### 2. 期望的线性性（最重要的性质）

**无论 X, Y 是否独立**：
E[aX + bY] = a*E[X] + b*E[Y]

这是期望最强大的性质，因为**不需要知道联合分布**就能计算。

**经典应用——指示器随机变量法**：

问题：100 人随机戴帽子（每人等概率戴到任意一顶），期望有多少人戴到自己的帽子？

定义 Xi = 1 如果第 i 人戴对，否则为 0。则 E[Xi] = 1/100。
总数 S = X1 + X2 + ... + X100
E[S] = E[X1] + E[X2] + ... + E[X100] = 100 * (1/100) = **1**

无论 n 是多少（10 人、1000 人、100万人），答案始终是 1。这个优美的结果完全来自线性性。

### 3. 方差 Var[X] 的定义与计算

**定义**：Var[X] = E[(X - E[X])^2] = E[X^2] - (E[X])^2

**标准差**：sigma = sqrt(Var[X])，与 X 同单位，更直观。

**计算技巧**：通常用 E[X^2] - (E[X])^2 比定义式更方便。

**常见分布的方差**：

| 分布 | Var[X] | 直觉 |
|------|--------|------|
| Bernoulli(p) | p(1-p) | p=0.5 时方差最大（最不确定） |
| Binomial(n,p) | np(1-p) | n 次独立试验的累积波动 |
| Poisson(lambda) | lambda | 方差 = 期望（泊松分布的特征） |
| Uniform(a,b) | (b-a)^2/12 | 区间越宽，方差越大 |
| Exp(lambda) | 1/lambda^2 | 指数分布的不确定性 |
| N(mu, sigma^2) | sigma^2 | 参数本身就是方差 |

### 4. 方差的性质

**缩放**：Var[aX + b] = a^2 * Var[X]（常数平移不影响离散度，缩放以平方增长）

**独立变量之和**：若 X, Y 独立，Var[X + Y] = Var[X] + Var[Y]

**注意**：如果 X, Y 不独立，需要协方差项：
Var[X + Y] = Var[X] + Var[Y] + 2*Cov(X,Y)

**重要不等式——切比雪夫不等式**：
P(|X - E[X]| >= k*sigma) <= 1/k^2

即：任何分布中，距离均值超过 k 个标准差的概率不超过 1/k^2。例如 k=3 时，P <= 1/9 约 11.1%。这是一个不依赖分布形状的万能界。

### 5. 实际应用案例

**投资组合风险评估**：
假设两支股票 A、B 的日回报率：E[A] = 0.1%, Var[A] = 4; E[B] = 0.1%, Var[B] = 4。
- 全部投 A：组合方差 = 4
- 各投 50%（独立时）：组合方差 = 0.25*4 + 0.25*4 = 2
- 分散投资将方差降低了 **50%**——这就是"不要把所有鸡蛋放在一个篮子里"的数学基础

**质量控制**：工厂零件直径 N(10mm, 0.01mm^2)。合格范围 [9.7mm, 10.3mm]。
距均值 3 个标准差 = 3*0.1mm = 0.3mm。由正态分布 3-sigma 法则，99.7% 的零件合格。

## 关键原理分析

### 大数定律的直觉预告

样本均值 X_bar = (X1+...+Xn)/n。
E[X_bar] = E[X]（无偏）。
Var[X_bar] = Var[X]/n（方差以 1/n 速度缩小）。

这意味着样本越大，样本均值越集中在真实期望附近——这就是大数定律的核心思想，也是统计推断的基础。

### 期望的"非线性陷阱"

E[g(X)] 通常不等于 g(E[X])。例如 E[X^2] 不等于 (E[X])^2（差值正是方差）。Jensen 不等式给出了凸函数/凹函数情形下的方向性结论：若 g 是凸函数，E[g(X)] >= g(E[X])。

## 实践练习

**练习 1**：掷两颗骰子，令 X = 两颗点数之和。(a) 计算 E[X]；(b) 计算 Var[X]；(c) 验证 Var[X] = Var[X1] + Var[X2]（利用独立性）。

**练习 2**：一个赌徒玩轮盘赌（38 格中有 18 红、18 黑、2 绿），每次押红 10 元。计算 (a) 单次下注的期望收益；(b) 玩 100 次后总收益的期望和标准差。

## 常见误区

1. **混淆期望与最可能值**：E[X] 不一定是 X 能取到的值。例如掷骰子 E[X] = 3.5，但永远掷不出 3.5
2. **方差可以相加 = 标准差可以相加**：Var[X+Y] = Var[X] + Var[Y]，但 sigma(X+Y) 不等于 sigma(X) + sigma(Y)
3. **忽略独立性条件**：方差的可加性需要独立性（或至少不相关），否则必须加协方差项