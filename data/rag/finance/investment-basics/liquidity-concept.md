---
id: "liquidity-concept"
concept: "流动性概念"
domain: "finance"
subdomain: "investment-basics"
subdomain_name: "投资基础"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 78.4
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
  - type: "academic"
    citation: "Amihud, Y., & Mendelson, H. (1986). Asset pricing and the bid-ask spread. Journal of Financial Economics, 17(2), 223–249."
  - type: "academic"
    citation: "Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. Review of Financial Studies, 22(6), 2201–2238."
  - type: "academic"
    citation: "Pastor, L., & Stambaugh, R. F. (2003). Liquidity risk and expected stock returns. Journal of Political Economy, 111(3), 642–685."
  - type: "academic"
    citation: "Kyle, A. S. (1985). Continuous auctions and insider trading. Econometrica, 53(6), 1315–1335."
  - type: "book"
    citation: "Keynes, J. M. (1936). The General Theory of Employment, Interest and Money. Macmillan. 中译本：凯恩斯《就业、利息和货币通论》，商务印书馆，1983年。"
  - type: "book"
    citation: "Hasbrouck, J. (2007). Empirical Market Microstructure: The Institutions, Economics, and Econometrics of Securities Trading. Oxford University Press."
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# 流动性概念

## 概述

流动性（Liquidity）是指一项资产在**不显著损失价值的前提下**，迅速转换为现金的能力。这一概念由经济学家约翰·梅纳德·凯恩斯（John Maynard Keynes）在1936年出版的《就业、利息和货币通论》（*The General Theory of Employment, Interest and Money*）中系统阐述。凯恩斯将流动性偏好（Liquidity Preference）定义为人们持有现金而非其他资产的欲望，并将其作为利率决定的核心机制之一——利率本质上是放弃流动性的"报酬"。现金本身的流动性为100%，是衡量其他所有资产流动性的基准参照。

流动性不仅描述"能否变现"，更强调**变现的速度**与**变现时的价格损耗**两个维度。一套市中心公寓可能价值500万元，但若需要在48小时内出售，可能不得不以430万元成交，损失14%的价值——这正是流动性不足的直接代价。对投资者而言，理解资产的流动性特征，直接影响其应对紧急资金需求、把握市场机会的能力。

值得注意的是，流动性是一个**相对概念**，而非绝对属性。同一资产在不同市场环境、不同交易规模下，其流动性表现可能截然不同。市场微观结构学者 Kyle（1985）在其奠基性论文《连续拍卖与内幕交易》（*Continuous Auctions and Insider Trading*）中提出了衡量流动性的三个核心维度：**宽度**（Tightness，即买卖价差大小）、**深度**（Depth，即不引起价格变动的最大交易量）、**弹性**（Resiliency，即价格受冲击后恢复的速度）。这一三维框架至今仍是学术界与从业者分析流动性的标准范式。Hasbrouck（2007）进一步在《实证市场微观结构》一书中对上述框架进行了系统的计量化拓展，为流动性的精确测量提供了方法论基础。

> **思考问题**：如果一只股票日均成交量高达10亿元，但某机构投资者需要出售的头寸恰好也价值10亿元，这只股票对该机构而言是否依然具有高流动性？流动性是资产的固有属性，还是投资者规模与资产深度之间的相对关系？

## 核心原理

### 流动性的两个核心维度

衡量资产流动性时，必须同时考察**变现速度**与**价格冲击**两个维度：

- **变现速度**：从决定出售到实际获得资金所需的时间。上海证券交易所A股实行T+1交割制度，即今日成交、明日到账；纽约证券交易所（NYSE）于2024年5月28日正式将股票结算周期从T+2缩短至T+1，成为美国证券史上近30年来最重要的结算制度改革；而私募股权投资的退出周期通常为5至7年，风险投资（VC）基金的平均锁定期甚至可达10年。中国境内公募基金中，货币市场基金（如余额宝对应的天弘基金）自2018年起实现7×24小时快速赎回，单日快速赎回上限为1万元，体现了流动性管理的技术进步。
- **价格冲击（Price Impact）**：大额交易对市场价格造成的不利影响。若某投资者持有某只小盘股流通市值的20%，其卖出行为本身会压低股价，导致实际成交均价低于初始报价。**案例**：2021年3月美国家族办公室Archegos Capital因集中持有ViacomCBS、Discovery、百度、腾讯音乐等多只股票，通过总收益互换（Total Return Swap）将实际杠杆率推至约5至8倍，当相关标的股价回落触发追保通知后，高盛、摩根士丹利等主要经纪商在2021年3月26日至29日期间集中强制平仓约200亿美元头寸，导致ViacomCBS单日跌幅超过27%、Discovery单日跌幅超过40%，充分暴露了集中持仓在流动性收紧时的系统性风险。

### 买卖价差：流动性的直接量化指标

市场微观结构理论中，**买卖价差（Bid-Ask Spread）** 是衡量流动性最直观的指标。计算公式为：

$$\text{相对价差} = \frac{P_{ask} - P_{bid}}{P_{mid}} \times 100\%$$

其中 $P_{ask}$ 为做市商（Market Maker）的卖出报价，$P_{bid}$ 为买入报价，$P_{mid} = \frac{P_{ask} + P_{bid}}{2}$ 为中间价。相对价差直接代表了投资者"买入后立即卖出"所损失的成本比例，是一次完整交易的摩擦成本下限。

**例如**，以某典型交易日的市场数据为参照：苹果公司股票（AAPL）的买卖价差约为0.01美元，中间价约为180美元，相对价差仅约0.006%，流动性极高；而某些小盘股或信用债券的相对价差可达2%至5%，意味着每次交易都要付出2%至5%的隐性成本。若某投资者每月进行4次此类交易，年化隐性成本可高达96%至240%，远超任何合理的投资回报预期。A股市场中，沪深300指数成分股的相对价差通常在0.02%至0.1%之间，而部分北交所小盘股的相对价差则可达1%以上，差距达数十倍。**这一隐性成本长期累积，对投资组合的复合回报具有显著的侵蚀效应，是主动管理型基金难以持续跑赢指数的重要原因之一。**

Amihud 与 Mendelson（1986）在研究纽约证券交易所1961至1980年间的横截面数据时进一步发现，买卖价差每扩大1个百分点，股票年化预期收益率平均上升约0.211个百分点，两者之间存在显著的凸性（Concave）正相关关系——即高流动性资产对流动性改善的边际定价敏感度低于低流动性资产。这一发现奠定了流动性溢价定价的实证基础。

### 流动性溢价：持有非流动资产的补偿

由于流动性差的资产难以迅速变现，理性投资者要求更高的预期回报来补偿这一劣势，这额外的回报要求被称为**流动性溢价（Liquidity Premium）**。

Amihud 与 Mendelson（1986）的经典研究发现，美国市场上流动性最差的10%股票相较于流动性最好的10%股票，年化超额回报约为3%至4%，且这一溢价在控制规模、价值等因子后依然显著。非流动性溢价的量化分析中，**阿米胡德非流动性指标（Amihud Illiquidity Ratio）** 最为常用，其公式为：

$$ILLIQ_i = \frac{1}{D_i} \sum_{d=1}^{D_i} \frac{|R_{id}|}{VOL_{id}}$$

其中 $R_{id}$ 为股票 $i$ 在第 $d$ 日的收益率（以小数表示），$VOL_{id}$ 为对应日期的成交金额（单位：百万元），$D_i$ 为计算期内的交易日数。该值越大，说明单位成交金额能够引发的价格波动越剧烈，资产的流动性越差。

**例如**，某股票连续20个交易日的平均日收益率绝对值为1%（即0.01），日均成交金额为500万元（即5百万元），则其阿米胡德非流动性指标约为 $\frac{0.01}{5} = 0.002$。若另一只股票同期指标为0.010，则其流动性约为前者的五分之一，要求更高的流动性溢价补偿。私募基金、非上市股权、艺术品等资产的流动性溢价往往在年化2%至8%之间，这解释了为何这类资产的锁定期要求能被追求长期回报的机构投资者接受——中国社保基金和耶鲁大学捐赠基金（Yale Endowment）等长线资金将私募股权配置比例维持在20%至40%，正是主动"出售"流动性以换取溢价收益的战略体现。

Pastor 与 Stambaugh（2003）进一步发现，股票对**流动性风险**（即系统性流动性变化的敞口）本身也是一个定价因子——在市场整体流动性下降时价格跌幅更大的股票，需要更高的期望回报率作为补偿。他们构建了基于1966至1999年NYSE/AMEX股票的流动性因子，发现流动性风险敞口最高的股票组合相较于最低组合，年化超额回报约为7.5%。这一发现将流动性从资产特征层面提升至系统性风险层面，与市场风险（Beta）、规模因子（SMB）、价值因子（HML）并列为资产定价的独立维度。

### 市场流动性与资金流动性的区分

流动性存在两个层面：**市场流动性**（Market Liquidity）指某类资产在市场上整体的交易便利程度；**资金流动性**（Funding Liquidity）指投资者自身获取资金（如抵押融资、信用额度）的能力。Brunnermeier 与 Pedersen（2009）提出了"流动性螺旋"（Liquidity Spiral）理论，系统描述了两者之间的相互强化机制：

1. 资金流动性收紧（如银行收紧抵押贷款成数，或提高初始保证金比例）
2. 机构投资者被迫去杠杆，抛售资产以满足追保要求
3. 市场流动性恶化，资产价格下跌，买卖价差扩大
4. 抵押品价值缩水，进一步压缩融资空间，维持保证金（Maintenance Margin）被突破
5. 回到步骤2，形成自我强化的恶性循环

2008年全球金融危机正是这一机制的极端演绎：雷曼兄弟于2008年9月15日申请破产保护后，货币市场基金Reserve Primary Fund因持有7.85亿美元雷曼兄弟商业票据而"跌破面值"（Breaking the Buck，净值跌至0.97美元），引发大规模赎回潮，仅两日内赎回申请超过400亿美元，美国商业票据市场在数日内几近冻结。美联储随即于2008年10月启动商业票据融资便利（Commercial