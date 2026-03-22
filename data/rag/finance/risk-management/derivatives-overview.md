---
id: "derivatives-overview"
concept: "衍生品概述"
domain: "finance"
subdomain: "risk-management"
subdomain_name: "风险管理"
difficulty: 2
is_milestone: false
tags: ["工具"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 81.9
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.931
last_scored: "2026-03-22"

sources:
  - type: "encyclopedia"
    ref: "Wikipedia - Derivatives market"
    url: "https://en.wikipedia.org/wiki/Derivatives_market"
  - type: "educational"
    ref: "Investopedia - Derivative Definition"
    url: "https://www.investopedia.com/terms/d/derivative.asp"
scorer_version: "scorer-v2.0"
---
# 衍生品概述

## 概述

金融衍生品（Financial Derivatives）是一类价值**依赖于**（derive from）一个或多个标的资产价格的金融合约。标的资产可以是股票、债券、大宗商品、货币、利率或市场指数等。衍生品是两方或多方之间的协议，可在交易所交易（标准化）或场外交易（OTC，定制化）（Investopedia）。

衍生品最初用于解决国际贸易中的汇率波动问题，如今已发展为现代金融市场的核心工具，主要用途包括**风险对冲**（hedging）、**价格发现**（price discovery）和**投机**（speculation）。截至 2007 年底，全球未平仓 CDS 名义金额曾达到 62.2 万亿美元（Wikipedia: Credit default swap）。

四种基本衍生品类型为：期货（Futures）、远期（Forwards）、期权（Options）和互换（Swaps）。

## 核心知识点

### 四大衍生品类型

**期货合约（Futures）**：标准化的交易所合约，约定在未来特定日期以约定价格买入/卖出标的资产。每日盯市结算（mark-to-market），通过保证金制度管理对手方风险。芝加哥商品交易所（CME）是全球最大的衍生品交易所之一（Investopedia）。

**远期合约（Forwards）**：与期货类似但为场外交易（OTC），可定制条款。不经过交易所清算，因此存在更高的**对手方风险**（counterparty risk）。

**期权（Options）**：赋予持有者在到期日前以约定价格（行权价）买入（看涨期权/Call）或卖出（看跌期权/Put）标的资产的**权利但非义务**。买方支付期权费（premium）获得权利，卖方收取期权费承担义务。

**互换（Swaps）**：双方交换未来现金流的协议。最常见的是利率互换（IRS）——一方支付固定利率，另一方支付浮动利率。2018 年 6 月，全球互换市场未平仓名义金额约 8 万亿美元。

### 交易所交易 vs 场外交易

| 特征 | 交易所交易 | 场外交易（OTC） |
|------|-----------|---------------|
| 标准化 | 高度标准化 | 可定制 |
| 监管 | 严格监管 | 监管较少 |
| 对手方风险 | 由清算所承担 | 由交易对手承担 |
| 流动性 | 通常较高 | 视具体合约 |
| 透明度 | 高（公开报价） | 低（私下协商） |

2009 年以前，CDS 不在交易所交易，也无政府报告要求。2008 年金融危机暴露了 OTC 衍生品市场缺乏透明度可能造成系统性风险（Wikipedia: CDS）。

### 杠杆特性

衍生品通常具有**杠杆效应**——只需少量资本（保证金）即可控制大量标的资产头寸。这放大了潜在收益和风险。例如，期货交易的初始保证金通常只占合约价值的 5-15%。

## 关键要点

1. 衍生品的价值**衍生自**标的资产价格变动，本身不具有内在价值
2. 四大类型：期货（标准化交易所）、远期（OTC定制）、期权（权利非义务）、互换（现金流交换）
3. 杠杆特性使衍生品成为"双刃剑"——风险管理利器同时也是潜在的系统性风险来源
4. OTC 衍生品的对手方风险是 2008 金融危机的重要诱因之一
5. 对冲者用衍生品锁定利润/管理风险，投机者用衍生品押注方向获利

## 常见误区

1. **"衍生品就是赌博"**——对冲者使用衍生品降低现有风险（如农场主卖出期货锁定粮价），投机只是衍生品的用途之一
2. **"期货和远期是一样的"**——期货是标准化、每日结算、交易所交易的；远期是定制化、到期结算、OTC 交易的，两者风险特征截然不同
3. **"买期权的最大损失是无限的"**——期权**买方**的最大损失仅限于已付期权费，最大损失无限的是期权**卖方**（特别是裸卖看涨期权）

## 知识衔接

- **先修**：金融市场基础、时间价值与折现
- **后续**：期货基础、期权定价（Black-Scholes）、互换与利率衍生品、对冲策略

## 思考题

1. 衍生品的"零和博弈"特性是否意味着衍生品市场对社会没有价值？套期保值如何创造价值？
2. 为什么Warren Buffett称衍生品为"大规模杀伤性金融武器"？衍生品的系统性风险体现在哪里？
3. 场内衍生品（交易所交易）和场外衍生品（OTC）在风险管理上有什么本质差异？


## 延伸阅读

- Wikipedia: [Derivative (finance)](https://en.wikipedia.org/wiki/Derivative_(finance))
