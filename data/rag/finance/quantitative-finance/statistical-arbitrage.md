---
id: "statistical-arbitrage"
concept: "统计套利"
domain: "finance"
subdomain: "quantitative-finance"
subdomain_name: "量化金融"
difficulty: 3
is_milestone: false
tags: ["策略"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "pending-rescore"
quality_score: 11.2
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.125
last_scored: "2026-03-21"

sources:
  - type: "encyclopedia"
    ref: "Wikipedia - Statistical arbitrage"
    url: "https://en.wikipedia.org/wiki/Statistical_arbitrage"
  - type: "educational"
    ref: "CQF - What is Statistical Arbitrage"
    url: "https://www.cqf.com/blog/quant-finance-101/what-is-statistical-arbitrage"
---
# 统计套利

## 概述

统计套利（Statistical Arbitrage，简称 StatArb 或 Stat Arb）是一类**短期量化交易策略**，利用均值回归模型对大量证券（通常数百至数千只）进行广泛分散的多空配对交易，持仓期从数秒到数天不等（Wikipedia: Statistical arbitrage）。

StatArb 从最初的**配对交易**（Pairs Trading）演化而来，现已发展为对冲基金和投资银行自营交易的主要策略之一。它是一种高度量化和计算密集型的交易方法，涉及数据挖掘、统计建模和自动化交易系统。

## 核心知识点

### 基本原理——均值回归与配对交易

StatArb 的核心假设是：统计上相关的资产之间的价格关系在偏离后会**回归均值**。

**配对交易**是最简单的 StatArb 形式：
1. 找出两只具有高**相关性**或**协整关系**（cointegration）的股票
2. 当价差偏离历史均值时：买入（做多）表现较差的，卖出（做空）表现较好的
3. 等待价差回归均值后平仓获利

数学工具包括：距离法、协整检验（Engle-Granger, Johansen）、Copula 方法等（Wikipedia: Statistical arbitrage）。

### 多因子方法

现代 StatArb 远不止简单的配对交易，通常采用**多因子模型**：

- **均值回归因子**：价格偏离移动均线的程度
- **动量因子**：短期价格趋势
- **领先-滞后效应**：行业或关联公司之间的价格传导
- **公司事件因子**：财报、并购、评级变更

策略目标是构建 **beta 中性**（对市场整体走势不敏感）的投资组合，通过大量小幅的 alpha 收益积累利润。

### 执行与成本控制

由于涉及大量股票、高频换手和微小利润空间，StatArb 高度依赖：
- **自动化交易系统**：毫秒级下单和执行
- **交易成本优化**：佣金、滑点、市场冲击成本是决定策略是否盈利的关键
- **风险管理**：实时监控组合暴露、相关性突变和极端事件

### 2007 年 Quant Crisis

2007 年 8 月，多家 StatArb 对冲基金同时遭受重大损失。原因被认为是某基金（可能是 Morgan Stanley 的 PDT）因其他业务压力被迫平仓，导致市场价格压力传导到持有相似头寸的其他 StatArb 基金——形成了**拥挤交易**（crowded trade）的连锁反应（Wikipedia: Statistical arbitrage）。

这一事件揭示了 StatArb 面临的隐性风险：**策略同质化本身就是一个风险因子**。

## 关键要点

1. StatArb 从配对交易演化而来，现代版本使用多因子模型交易数百到数千只证券
2. 核心假设是均值回归——统计关系偏离后会恢复
3. 策略目标是 beta 中性：不押注市场方向，通过大量小幅 alpha 获利
4. 交易成本控制和自动化执行是策略盈利的决定性因素
5. 2007 Quant Crisis 证明策略同质化和拥挤交易是主要系统性风险

## 常见误区

1. **"统计套利是无风险套利"**——名字中有"套利"但并非真正的无风险套利，而是**统计上有利**的交易。短期内可能遭受重大损失
2. **"只要找到高相关性就能配对交易"**——相关性 ≠ 协整。两只股票可以高度相关但价差不会回归，只有满足协整关系才适合配对交易
3. **"模型有效就能一直赚钱"**——市场结构变化、策略拥挤、监管变更都可能使历史有效的统计关系失效

## 知识衔接

- **先修**：概率与统计、时间序列分析、均值回归理论
- **后续**：高频交易、机器学习量化策略、风险因子分析
