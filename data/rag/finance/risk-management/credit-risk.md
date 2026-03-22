---
id: "credit-risk"
concept: "信用风险"
domain: "finance"
subdomain: "risk-management"
subdomain_name: "风险管理"
difficulty: 2
is_milestone: false
tags: ["类别"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "research-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-03-22"

sources:
  - type: "encyclopedia"
    ref: "Wikipedia - Credit default swap"
    url: "https://en.wikipedia.org/wiki/Credit_default_swap"
  - type: "educational"
    ref: "Oxford Physics - Credit Default Swaps PDF"
    url: "https://users.physics.ox.ac.uk/~Foot/Phynance/CDS2012.pdf"
scorer_version: "scorer-v2.0"
---
# 信用风险

## 概述

信用风险（Credit Risk）是指债务人未能按合同约定履行还款义务的风险，是金融机构面临的最基本风险类型之一。信用风险包括**违约风险**（default risk）——借款人完全无法偿还、**降级风险**（downgrade risk）——信用评级下调导致资产价值下降、以及**信用利差风险**（credit spread risk）——市场对信用风险的定价变化。

信用风险管理的核心工具之一是**信用违约互换**（CDS），它允许投资者将违约风险转移给另一方。截至 2007 年底，全球未平仓 CDS 名义金额达到 **62.2 万亿美元**，到 2010 年中降至 26.3 万亿美元，2018 年 6 月约为 8 万亿美元（Wikipedia: CDS）。

## 核心知识点

### 信用违约互换（CDS）——信用风险转移的核心工具

CDS 是一种**金融互换协议**：保护买方定期向保护卖方支付费用（CDS 利差/spread），如果参考实体（reference entity）发生**信用事件**，卖方向买方支付补偿（Wikipedia: CDS）。

信用事件包括：
- **未能偿付**（failure to pay）
- **债务重组**（restructuring）
- **破产**（bankruptcy）
- 对于主权债务还包括：拒绝偿付（repudiation）、延期偿付（moratorium）、加速到期（acceleration）

CDS 利差以**基点**（basis points）报价。例如 Risky Corp 的 CDS 利差为 50 基点（0.5%），则买入 1000 万美元保护的投资者每年支付 5 万美元，通常按季度后付（Wikipedia: CDS）。

### 违约概率度量

**风险中性违约概率**（Risk-Neutral Default Probability）可从 CDS 利差反推。假设回收率为 R，年化 CDS 利差为 s，则近似有：

$$PD \approx \frac{s}{1-R}$$

例如，CDS 利差 200bp、回收率 40% → 违约概率 ≈ 3.33%/年。注意这是风险中性概率，通常高于实际（物理测度下的）违约概率。

**信用评级**由穆迪（Moody's）、标普（S&P）、惠誉（Fitch）三大评级机构提供。AAA 级 10 年累计违约率约 0.07%，BBB 级约 2-4%，BB 级约 10-15%。

### 信用风险模型

**结构化模型（Structural Models）**：以 Merton（1974）模型为代表，将公司股权视为以资产价值为标的的看涨期权。当资产价值跌破债务面值时发生违约。

**简约化模型（Reduced-Form Models）**：不建模违约的经济原因，而是直接假设违约服从某个随机强度过程（如泊松过程）。Jarrow-Turnbull（1995）和 Duffie-Singleton（1999）是代表性模型。

### 2008 金融危机与信用风险

2008 年金融危机的核心教训之一是 OTC 衍生品市场（特别是 CDS）缺乏透明度带来的**系统性风险**。AIG 作为大量 CDS 的卖方，在住房抵押贷款大规模违约时面临巨额赔付，最终需要政府 1850 亿美元救助。此后监管推动 CDS 标准化和集中清算（Wikipedia: CDS）。

## 关键要点

1. 信用风险三个维度：违约风险、降级风险、信用利差风险
2. CDS 是信用风险转移的核心工具，买方支付利差获得违约保护
3. CDS 利差隐含了市场对违约概率的定价：PD ≈ spread / (1 - Recovery Rate)
4. 裸 CDS（无持有标的债务）允许投机者押注信用事件，增加了市场系统性风险
5. 结构化模型（Merton）视股权为看涨期权；简约化模型直接建模违约强度

## 常见误区

1. **"CDS 就是保险"**——CDS 不受保险监管，可以裸买（无保险利益），且未平仓 CDS 金额可以远超标的债务总额
2. **"高评级 = 零风险"**——AAA 评级也有违约可能（如 2008 年大量 AAA 级 MBS 违约），评级反映相对而非绝对的信用质量
3. **"违约概率 = CDS 利差"**——CDS 利差还包含回收率假设和流动性溢价，简单等同会高估违约概率

## 知识衔接

- **先修**：衍生品概述、概率与统计基础
- **后续**：信用评级模型、CDO 与结构化产品、巴塞尔协议（资本充足率）、风险价值（VaR）
