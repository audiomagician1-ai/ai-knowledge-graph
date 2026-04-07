---
id: "mean-reversion"
concept: "均值回归"
domain: "finance"
subdomain: "quantitative-finance"
subdomain_name: "量化金融"
difficulty: 3
is_milestone: false
tags: ["策略"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 76.3
generation_method: "research-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"

sources:
  - type: "educational"
    ref: "Investopedia - Mean Reversion"
    url: "https://www.investopedia.com/terms/m/meanreversion.asp"
  - type: "educational"
    ref: "Interactive Brokers - Mean Reversion Strategies"
    url: "https://www.interactivebrokers.com/campus/ibkr-quant-news/mean-reversion-strategies-introduction-trading-strategies-and-more-part-i/"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 均值回归

## 概述

均值回归（Mean Reversion）是一种统计现象，描述资产价格或金融时间序列在偏离其历史均值后，倾向于向均值方向回归的特性。这一概念最早由Francis Galton在1886年研究人类身高遗传规律时提出，他称之为"向平庸回归"（regression to mediocrity），后来被金融学者引入资产定价领域。均值回归的数学基础是平稳性（Stationarity）——若一个时间序列是均值平稳的，其长期均值是固定的常数，价格的偏离在统计意义上是暂时的。

在量化金融中，均值回归与随机游走假说（Random Walk Hypothesis）直接对立。随机游走认为价格变化是不可预测的，而均值回归则断言价格存在可预测的均值趋近动态。实证研究表明，股票价格在日内和短周期内（数天至数周）存在显著的均值回归特征，而大宗商品（如黄金、原油）因供需均衡机制也表现出较强的均值回归倾向。均值回归策略的核心是：当价格偏离均值超过一定阈值时建立反向头寸，待价格回归后获利平仓。

## 核心原理

### ADF检验：识别均值回归序列

判断一个时间序列是否具有均值回归特性，标准方法是**增广迪基-富勒检验**（Augmented Dickey-Fuller Test，ADF检验）。ADF检验的零假设是序列存在单位根（即非平稳，无均值回归），备择假设是序列平稳（具有均值回归）。检验统计量的计算基于以下回归方程：

$$\Delta y_t = \alpha + \beta t + \gamma y_{t-1} + \sum_{i=1}^{p} \delta_i \Delta y_{t-i} + \epsilon_t$$

其中 $\gamma$ 的显著负值（通常要求p值 < 0.05）意味着序列存在均值回归。若ADF统计量低于1%显著性水平的临界值（约为-3.43，样本量250时），则强拒绝单位根假设，序列被认定为均值回归序列。除ADF外，Hurst指数（H）也是常用指标：H < 0.5表示均值回归，H = 0.5表示随机游走，H > 0.5表示趋势持续。

### 均值回归速度：Ornstein-Uhlenbeck过程

均值回归序列在连续时间下通常用**Ornstein-Uhlenbeck（OU）过程**建模：

$$dX_t = \theta(\mu - X_t)dt + \sigma dW_t$$

其中 $\theta$ 是均值回归速度（mean reversion speed），$\mu$ 是长期均值，$\sigma$ 是波动率，$dW_t$ 是维纳过程增量。$\theta$ 越大，价格回归均值的速度越快。均值回归的半衰期（half-life）可由公式 $t_{1/2} = \ln(2)/\theta$ 计算——若 $\theta = 0.1$，则半衰期约为6.93个交易日，意味着价格偏离的一半会在约7天内消失。半衰期直接决定了交易策略的持仓周期：半衰期过长（超过30天）则策略资金利用效率低；过短（小于1天）则交易成本侵蚀利润。

### Bollinger Band策略：均值回归的经典实现

基于均值回归的最经典量化策略是**布林带策略（Bollinger Bands）**，由John Bollinger于1983年设计。该策略使用 $N$ 日移动均线作为均值估计，上下轨设定为 $\pm k$ 倍标准差（通常 $N=20$，$k=2$）：

- 上轨：$\text{MA}_N + k \cdot \sigma_N$
- 下轨：$\text{MA}_N - k \cdot \sigma_N$

当价格触及下轨时做多，触及上轨时做空，在均线处平仓。统计上，若收益率服从正态分布，价格有95.4%的概率落在 $\pm 2\sigma$ 区间内，超出上下轨即属于统计异常，均值回归逻辑认为这种偏离不可持续。在实际应用中，$z$-score是更标准的衡量指标：$z = (P_t - \mu) / \sigma$，当 $|z| > 2$ 时触发交易信号。

## 实际应用

**配对交易（Pairs Trading）** 是均值回归最典型的量化应用。选取两只高度相关的股票（如贵州茅台与五粮液），通过协整检验（Engle-Granger两步法）确认价差序列具有均值回归特性，然后对价差序列构建 $z$-score信号。当价差扩大至 $z > 2$ 时，做空相对强势股并做多弱势股；当价差回归至 $|z| < 0.5$ 时平仓。该策略属于市场中性策略，能对冲系统性风险。2008年金融危机期间，许多依赖均值回归的量化基金遭遇"均值回归策略拥挤"问题——大量相似仓位同时被迫平仓，价差反而持续扩大而非回归，这一事件被称为"2007年量化危机"的延续效应。

**期货跨期套利** 也依赖均值回归原理。同一商品的近月合约与远月合约之间的价差（Calendar Spread）受无风险套利约束，理论上围绕持仓成本（Cost of Carry）均值波动。当实际价差偏离理论均值超过交易成本阈值时，套利交易将驱动价差回归，这为量化策略提供了低风险的套利机会。

## 常见误区

**误区一：均值回归等同于价格必然回到历史均值。** 均值回归的前提是时间序列的均值本身是稳定的（平稳性）。若一只股票的基本面发生结构性变化（如公司破产、行业颠覆），其均值会发生永久性漂移，ADF检验的平稳性结论也会失效。忽视结构性断裂（Structural Break）而盲目持有"均值回归"仓位，会导致严重亏损——2015年中国A股配对交易策略中，许多配对因股价停牌、政策冲击而长期不回归，正是此类风险的体现。

**误区二：半衰期短的策略一定优于半衰期长的策略。** 均值回归半衰期短意味着交易频率高，但同时也意味着每次价格偏离的幅度小。高频均值回归策略虽然单次持仓时间短，但对执行成本（滑点+佣金）极为敏感。一般经验是，若单次交易的预期收益（以 $\sigma$ 计）低于双边手续费的3倍，该策略在扣费后无法盈利。半衰期约为5-15个交易日的中频均值回归策略在A股市场历史上表现出较好的风险收益比。

**误区三：协整即均值回归，两者完全等同。** 协整（Cointegration）描述的是两个非平稳序列的线性组合是平稳的，而均值回归描述的是单一平稳序列向其均值收敛的动态。协整是构造均值回归价差序列的工具，但协整系数（对冲比率）本身会随时间变化，若不进行动态更新（如使用卡尔曼滤波估计时变对冲比率），固定对冲比率会导致"假协整"带来的策略失效。

## 知识关联

均值回归的统计检验（ADF、Hurst指数）直接依赖**时间序列分析**中平稳性的概念——对协整序列的构造和检验需要掌握单整阶数（I(0)/I(1)）的区分方法。在**统计套利**框架下，均值回归是策略盈利的底层机制：配对交易的价差收益来源正是价差序列均值回归的统计规律性。OU过程的参数估计（$\theta, \mu, \sigma$）需要用最小二乘法或最大似然估计完成，是将统计理论转化为可执行交易信号的关键步骤。从策略进化角度看，均值回归策略在获得对价格动态的深入理解后，可自然延伸至**动态对冲比率模型**与**机器学习特征工程**，将均值回归速度、半衰期等指标作为因子输入更复杂的预测模型。