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
quality_tier: "pending-rescore"
quality_score: 11.2
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.125
last_scored: "2026-03-21"

sources:
  - type: "educational"
    ref: "Investopedia - Mean Reversion"
    url: "https://www.investopedia.com/terms/m/meanreversion.asp"
  - type: "educational"
    ref: "Interactive Brokers - Mean Reversion Strategies"
    url: "https://www.interactivebrokers.com/campus/ibkr-quant-news/mean-reversion-strategies-introduction-trading-strategies-and-more-part-i/"
---
# 均值回归

## 概述

均值回归（Mean Reversion）是一个金融理论，认为资产价格和收益率会随时间**自然回归到其历史长期均值**。当资产价格显著偏离均值时（过高或过低），均值回归理论预测价格最终会向均值方向移动（Investopedia）。

这一概念不仅适用于价格和收益率，也适用于利率、市盈率（P/E ratio）、波动率等各种金融指标。均值回归是许多量化交易策略的理论基础，特别是配对交易和统计套利。

## 核心知识点

### 理论基础与数学表达

均值回归过程最常用**Ornstein-Uhlenbeck（OU）过程**建模：

$$dX_t = \theta(\mu - X_t)dt + \sigma dW_t$$

其中：
- μ 是长期均值
- θ > 0 是**回归速度**（mean-reversion speed），θ 越大回归越快
- σ 是波动率
- W_t 是维纳过程

**半衰期**（half-life）= ln(2)/θ，表示偏差缩小一半所需时间。交易者用半衰期评估策略的持仓周期。

### 度量工具

**Z-Score**——标准化偏离度：
$$Z = \frac{Price - Mean}{StandardDeviation}$$

|Z| > 2 通常被视为显著偏离，可能触发交易信号。

**布林带（Bollinger Bands）**：以移动均线为中心，上下各加减 k 倍标准差。价格触及带边界时暗示可能回归（Investopedia）。

**RSI（相对强弱指数）**：衡量近期涨跌幅度，RSI > 70 为超买（可能下行回归），RSI < 30 为超卖（可能上行回归）。

### 交易策略实施

1. **配对交易**：找两只相关资产，当价差偏离均值时做多被低估的、做空被高估的，等待价差回归后平仓（Investopedia）。
2. **波动率均值回归**：隐含波动率偏高时卖出期权，偏低时买入期权
3. **算法交易**：量化分析师使用复杂数学模型自动化执行均值回归策略

### 有效市场条件

均值回归在**震荡市场**（range-bound market）中更有效，在**趋势市场**（trending market）中可能持续亏损。判断市场状态是策略能否盈利的先决条件。不同时间框架的有效性也不同——日内交易者用分钟/小时数据，长期投资者用年度数据（Investopedia）。

## 关键要点

1. 均值回归假设价格围绕长期均值波动，显著偏离后趋于回归
2. OU 过程是标准数学模型，半衰期 = ln(2)/θ 衡量回归速度
3. Z-Score、布林带、RSI 是最常用的偏离度量工具
4. 策略在震荡市中有效、趋势市中危险——市场状态判断是前提
5. 均值回归是配对交易和统计套利的理论基础

## 常见误区

1. **"价格一定会回归均值"**——均值回归是统计倾向而非确定性，公司基本面发生根本变化时价格可能永久偏离（Investopedia）
2. **"均值是固定不变的"**——长期均值本身会随时间漂移（如公司成长、通胀），使用固定均值会导致错误信号
3. **"偏离越大回归概率越高"**——极端偏离可能意味着结构性变化（regime change）而非临时偏差，盲目抄底可能造成"接飞刀"

## 知识衔接

- **先修**：概率与统计基础、时间序列分析
- **后续**：统计套利、配对交易实施、高频交易策略

## 思考题

1. 如果一只股票连续下跌50%，均值回归理论是否意味着它会反弹？为什么需要区分"统计均值回归"和"基本面变化"？
2. 在不同时间框架（日内 vs 月度 vs 年度）中，均值回归的可靠性如何变化？什么因素导致了这种差异？
3. 如何设计一个简单的均值回归策略回测？需要考虑哪些交易成本和滑点因素？


## 延伸阅读

- Wikipedia: [Mean reversion (finance)](https://en.wikipedia.org/wiki/Mean_reversion_(finance))
