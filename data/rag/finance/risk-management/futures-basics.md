---
id: "futures-basics"
concept: "期货基础"
domain: "finance"
subdomain: "risk-management"
subdomain_name: "风险管理"
difficulty: 2
is_milestone: false
tags: ["衍生品"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "pending-rescore"
quality_score: 11.2
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.125
last_scored: "2026-03-21"

sources:
  - type: "encyclopedia"
    ref: "Wikipedia - Futures contract"
    url: "https://en.wikipedia.org/wiki/Futures_contract"
  - type: "educational"
    ref: "CME Group - Futures Expiration and Settlement"
    url: "https://www.cmegroup.com/education/courses/introduction-to-futures/get-to-know-futures-expiration-and-settlement"
---
# 期货基础

## 概述

期货合约（Futures Contract）是一种标准化的法律协议，约定在未来某个特定日期以约定价格买入或卖出特定数量的标的资产。期货合约在期货交易所（如 CME、CBOT、ICE）交易，通过**每日盯市结算**（mark-to-market）和**保证金制度**管理风险（Wikipedia: Futures contract）。

期货最初起源于农产品市场（如玉米、小麦），帮助农户和加工商锁定未来价格。如今期货已覆盖股指、利率、外汇、能源、金属等各类标的资产。

## 核心知识点

### 保证金制度

期货交易采用**杠杆**机制：交易者不需支付合约全额，只需缴纳一定比例的保证金。

- **初始保证金**（Initial Margin）：开仓时需缴纳的最低金额，一般为合约价值的 **5-15%**（对冲者可能更低）。例如黄金期货保证金在 2% 到 20% 之间波动，取决于现货市场波动率（Wikipedia: Futures contract）。
- **维持保证金**（Maintenance Margin）：账户余额的最低维持水平，通常低于初始保证金
- **追加保证金通知**（Margin Call）：当账户余额跌破维持保证金时，须补足至初始保证金水平

### 每日盯市结算

期货合约每天按当日结算价重新估值，盈亏直接结入账户：
- 盈利方账户增加、亏损方账户减少
- 这消除了对手方违约风险的积累——与远期合约（到期才结算）的关键区别

### 交割与平仓

**实物交割**：到期时实际交付标的资产（如原油、大豆）。只有约 **1-3%** 的期货合约最终进行实物交割。

**现金交割**：按到期日现货价与合约价的差额进行现金结算（如股指期货）。

**对冲平仓**：大多数交易者在到期前通过建立反向头寸平仓——买入者卖出相同合约，卖出者买入相同合约。

### 期货 vs 远期

| 特征 | 期货 | 远期 |
|------|------|------|
| 交易场所 | 交易所 | 场外（OTC） |
| 标准化 | 高度标准化 | 可定制 |
| 结算 | 每日盯市 | 到期结算 |
| 对手方风险 | 由清算所承担 | 由交易对手承担 |
| 流动性 | 高 | 通常较低 |

## 关键要点

1. 期货是标准化的交易所合约，通过保证金和每日盯市管理风险
2. 初始保证金通常为合约价值的 5-15%，提供 7-20 倍杠杆
3. 每日盯市结算消除了对手方违约风险积累——这是与远期的核心区别
4. 仅 1-3% 的合约进行实物交割，绝大多数在到期前对冲平仓
5. 期货价格与现货价格的关系由持有成本模型决定：F = S × e^((r-q)T)

## 常见误区

1. **"买期货 = 现在就要付全款"**——只需缴纳初始保证金（合约价值的 5-15%），这正是期货的杠杆来源
2. **"期货到期必须交割"**——绝大多数合约在到期前通过反向交易平仓，许多品种还支持现金交割
3. **"期货价格 = 对未来现货价格的预测"**——期货价格还受利率、储存成本、便利收益等因素影响，不等于市场对未来价格的无偏预期

## 知识衔接

- **先修**：衍生品概述、时间价值
- **后续**：期权基础、对冲策略、基差交易
