---
id: "stochastic-calculus"
concept: "随机微积分"
domain: "finance"
subdomain: "quantitative-finance"
subdomain_name: "量化金融"
difficulty: 4
is_milestone: false
tags: ["数学"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "pending-rescore"
quality_score: 11.2
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.125
last_scored: "2026-03-21"

sources:
  - type: "encyclopedia"
    ref: "Wikipedia - Stochastic calculus"
    url: "https://en.wikipedia.org/wiki/Stochastic_calculus"
  - type: "encyclopedia"
    ref: "Wikipedia - Ito calculus"
    url: "https://en.wikipedia.org/wiki/It%C3%B4_calculus"
---
# 随机微积分

## 概述

随机微积分（Stochastic Calculus）是数学的一个分支，专门研究随机过程的积分与微分运算。它由日本数学家**伊藤清**（Kiyosi Ito）在二战期间创立，为处理受随机力作用的系统提供了严谨的数学框架（Wikipedia: Stochastic calculus）。

自 1970 年代起，随机微积分在**金融数学**中得到广泛应用，用于建模股票价格和债券利率随时间的演化。Black-Scholes 期权定价模型、利率期限结构模型等现代金融理论的核心工具，均建立在随机微积分之上。

学习随机微积分之前需要掌握概率论基础和普通微积分；掌握后可深入随机微分方程（SDE）、期权定价理论和风险管理模型。

## 核心知识点

### 维纳过程（布朗运动）——随机微积分的基石

维纳过程 W(t) 是最基本的连续时间随机过程，具有以下性质：
- W(0) = 0
- 增量 W(t) - W(s) ~ N(0, t-s)，服从均值为 0、方差为 t-s 的正态分布
- 不同时间区间的增量相互独立
- 路径连续但**处处不可微**——这使得经典微积分无法直接应用

维纳过程以 Norbert Wiener 命名，最早由 Louis Bachelier（1900）和 Albert Einstein（1905）用于描述物理扩散过程（Wikipedia: Stochastic calculus）。

### 伊藤积分——随机积分的核心定义

伊藤积分将积分概念推广到随机过程：

$$Y_t = \int_0^t H_s \, dX_s$$

其中 H 是**适应过程**（adapted process），X 是半鞅（semimartingale）。关键特性：
- 使用区间**左端点**计算黎曼和（这是与 Stratonovich 积分的本质区别）
- 在金融解释中：H_s 代表 t 时刻持有的股票数量，X_s 代表价格变动，积分 Y_t 代表总收益
- "适应性"条件保证交易策略只能利用当前可得信息，排除了"预知未来"的套利可能（Wikipedia: Ito calculus）

### 伊藤引理——随机微积分的链式法则

伊藤引理是随机微积分中最重要的公式，相当于普通微积分中的链式法则，但包含额外的**二次变差项**：

对于 f(t, X_t)，其中 X_t 满足 dX_t = μdt + σdW_t：

$$df = \frac{\partial f}{\partial t}dt + \frac{\partial f}{\partial x}dX_t + \frac{1}{2}\frac{\partial^2 f}{\partial x^2}\sigma^2 dt$$

最后一项 ½f''σ²dt 是与经典微积分的**关键区别**——它来自布朗运动的二次变差性质 (dW)² = dt。这一项使得 Black-Scholes 公式的推导成为可能。

### Stratonovich 积分——另一种随机积分

Stratonovich 积分使用区间**中点**计算黎曼和：

$$\int_0^t X_{s-} \circ dY_s = \int_0^t X_{s-} dY_s + \frac{1}{2}[X,Y]_t^c$$

其中 [X,Y]^c 是连续部分的二次协变差。Stratonovich 积分遵循经典链式法则，物理学中更常用；但伊藤积分在金融中更自然，因为交易决策基于当前信息（左端点）而非未来信息（Wikipedia: Stochastic calculus）。

## 关键要点

1. **维纳过程路径处处不可微**，使得经典微积分失效，必须使用随机微积分
2. **伊藤引理**比经典链式法则多出 ½f''σ²dt 项，这一项是 (dW)² = dt 的直接结果
3. 伊藤积分（左端点）vs Stratonovich 积分（中点）：金融用伊藤，物理常用 Stratonovich，两者可互相转换
4. 几何布朗运动 dS = μSdt + σSdW 是 Black-Scholes 模型的基础假设
5. 1973 年 Black-Scholes-Merton 公式的推导直接依赖伊藤引理

## 常见误区

1. **"布朗运动只是随机游走"**——布朗运动是连续时间的极限，路径连续但处处不可微，与离散随机游走有本质区别
2. **"伊藤积分和普通积分规则相同"**——忽略二次变差项会导致严重错误，例如 ∫W dW = W²/2 - t/2（而非经典的 W²/2）
3. **"波动率越大风险越大所以收益越高"**——伊藤引理告诉我们几何布朗运动的对数收益率的漂移项是 μ - σ²/2 而非 μ，高波动率实际**降低**了复合收益率

## 知识衔接

- **先修**：概率论、普通微积分、测度论基础
- **后续**：随机微分方程（SDE）、Black-Scholes 期权定价、利率模型（Vasicek, CIR）、随机波动率模型
