"""Batch rewrite finance concepts: stochastic-calculus, derivatives-overview, credit-risk, statistical-arbitrage, mean-reversion."""
import json, subprocess, sys
from pathlib import Path
from datetime import datetime

PROJECT = Path("D:/echoagent/projects/ai-knowledge-graph")
RAG_ROOT = PROJECT / "data" / "rag"
DRAFTS = PROJECT / "data" / "rewrite_drafts"
DRAFTS.mkdir(parents=True, exist_ok=True)

concepts = {
    "stochastic-calculus": {
        "domain": "finance",
        "subdomain": "quantitative-finance",
        "sources": [
            {"type": "encyclopedia", "ref": "Wikipedia - Stochastic calculus", "url": "https://en.wikipedia.org/wiki/Stochastic_calculus"},
            {"type": "encyclopedia", "ref": "Wikipedia - Ito calculus", "url": "https://en.wikipedia.org/wiki/It%C3%B4_calculus"},
        ],
        "body": r"""# 随机微积分

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
- **后续**：随机微分方程（SDE）、Black-Scholes 期权定价、利率模型（Vasicek, CIR）、随机波动率模型"""
    },

    "derivatives-overview": {
        "domain": "finance",
        "subdomain": "derivatives",
        "sources": [
            {"type": "encyclopedia", "ref": "Wikipedia - Derivatives market", "url": "https://en.wikipedia.org/wiki/Derivatives_market"},
            {"type": "educational", "ref": "Investopedia - Derivative Definition", "url": "https://www.investopedia.com/terms/d/derivative.asp"},
        ],
        "body": r"""# 衍生品概述

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
- **后续**：期货基础、期权定价（Black-Scholes）、互换与利率衍生品、对冲策略"""
    },

    "credit-risk": {
        "domain": "finance",
        "subdomain": "risk-management",
        "sources": [
            {"type": "encyclopedia", "ref": "Wikipedia - Credit default swap", "url": "https://en.wikipedia.org/wiki/Credit_default_swap"},
            {"type": "educational", "ref": "Oxford Physics - Credit Default Swaps PDF", "url": "https://users.physics.ox.ac.uk/~Foot/Phynance/CDS2012.pdf"},
        ],
        "body": r"""# 信用风险

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
- **后续**：信用评级模型、CDO 与结构化产品、巴塞尔协议（资本充足率）、风险价值（VaR）"""
    },

    "statistical-arbitrage": {
        "domain": "finance",
        "subdomain": "quantitative-finance",
        "sources": [
            {"type": "encyclopedia", "ref": "Wikipedia - Statistical arbitrage", "url": "https://en.wikipedia.org/wiki/Statistical_arbitrage"},
            {"type": "educational", "ref": "CQF - What is Statistical Arbitrage", "url": "https://www.cqf.com/blog/quant-finance-101/what-is-statistical-arbitrage"},
        ],
        "body": r"""# 统计套利

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
- **后续**：高频交易、机器学习量化策略、风险因子分析"""
    },

    "mean-reversion": {
        "domain": "finance",
        "subdomain": "quantitative-finance",
        "sources": [
            {"type": "educational", "ref": "Investopedia - Mean Reversion", "url": "https://www.investopedia.com/terms/m/meanreversion.asp"},
            {"type": "educational", "ref": "Interactive Brokers - Mean Reversion Strategies", "url": "https://www.interactivebrokers.com/campus/ibkr-quant-news/mean-reversion-strategies-introduction-trading-strategies-and-more-part-i/"},
        ],
        "body": r"""# 均值回归

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
- **后续**：统计套利、配对交易实施、高频交易策略"""
    },
}


def write_back(cid, info):
    """Write rewritten content back to RAG file."""
    domain = info["domain"]
    subdomain = info["subdomain"]
    
    # Find the RAG file
    rag_dir = RAG_ROOT / domain
    # Try subdomain path first
    rag_file = rag_dir / subdomain / f"{cid}.md"
    if not rag_file.is_file():
        # Try flat path
        rag_file = rag_dir / f"{cid}.md"
    if not rag_file.is_file():
        # Search
        candidates = list(rag_dir.rglob(f"{cid}.md"))
        if candidates:
            rag_file = candidates[0]
        else:
            print(f"  ERROR: RAG file not found for {cid}")
            return False
    
    print(f"  Writing: {rag_file.relative_to(PROJECT)}")
    
    # Read existing file to get YAML frontmatter
    content = rag_file.read_text(encoding="utf-8")
    
    # Parse existing YAML
    import re, yaml
    m = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if m:
        try:
            meta = yaml.safe_load(m.group(1))
        except:
            meta = {}
    else:
        meta = {}
    
    if not isinstance(meta, dict):
        meta = {}
    
    # Update metadata
    meta["content_version"] = meta.get("content_version", 1) + 1 if meta.get("content_version") else 2
    meta["quality_tier"] = "pending-rescore"
    meta["generation_method"] = "research-rewrite-v2"
    meta["last_scored"] = datetime.now().strftime("%Y-%m-%d")
    meta["sources"] = info["sources"]
    
    # Build new YAML
    yaml_lines = ["---"]
    # Preserve key fields
    for key in ["id", "concept", "domain", "subdomain", "subdomain_name", "difficulty", "is_milestone", "tags"]:
        if key in meta:
            val = meta[key]
            if isinstance(val, str):
                yaml_lines.append(f'{key}: "{val}"')
            elif isinstance(val, bool):
                yaml_lines.append(f'{key}: {"true" if val else "false"}')
            elif isinstance(val, list):
                yaml_lines.append(f'{key}: {json.dumps(val, ensure_ascii=False)}')
            else:
                yaml_lines.append(f'{key}: {val}')
    
    yaml_lines.append("")
    yaml_lines.append("# Quality Metadata (Schema v2)")
    yaml_lines.append(f'content_version: {meta.get("content_version", 2)}')
    yaml_lines.append(f'quality_tier: "pending-rescore"')
    yaml_lines.append(f'quality_score: {meta.get("quality_score", 0)}')
    yaml_lines.append(f'generation_method: "research-rewrite-v2"')
    yaml_lines.append(f'unique_content_ratio: {meta.get("unique_content_ratio", 0)}')
    yaml_lines.append(f'last_scored: "{datetime.now().strftime("%Y-%m-%d")}"')
    yaml_lines.append("")
    yaml_lines.append("sources:")
    for src in info["sources"]:
        yaml_lines.append(f'  - type: "{src["type"]}"')
        yaml_lines.append(f'    ref: "{src["ref"]}"')
        yaml_lines.append(f'    url: "{src["url"]}"')
    yaml_lines.append("---")
    
    new_content = "\n".join(yaml_lines) + "\n" + info["body"].strip() + "\n"
    rag_file.write_text(new_content, encoding="utf-8")
    return True


def main():
    print(f"Finance Batch Rewrite - {len(concepts)} concepts")
    print("=" * 60)
    
    success = 0
    for cid, info in concepts.items():
        print(f"\n[{cid}]")
        if write_back(cid, info):
            success += 1
            print(f"  OK")
        else:
            print(f"  FAILED")
    
    print(f"\n{'='*60}")
    print(f"Done: {success}/{len(concepts)} written")
    
    # Log
    log_path = PROJECT / "data" / "research_rewrite_log.json"
    log = []
    if log_path.is_file():
        with open(log_path, "r", encoding="utf-8") as f:
            log = json.load(f)
    
    for cid, info in concepts.items():
        log.append({
            "concept_id": cid,
            "domain": info["domain"],
            "timestamp": datetime.now().isoformat(),
            "sources_count": len(info["sources"]),
            "generation_method": "research-rewrite-v2",
            "batch": "finance-batch-1"
        })
    
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    print(f"Log updated: {log_path}")


if __name__ == "__main__":
    main()
