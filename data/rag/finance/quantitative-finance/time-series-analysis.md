---
id: "time-series-analysis"
concept: "时间序列分析"
domain: "finance"
subdomain: "quantitative-finance"
subdomain_name: "量化金融"
difficulty: 3
is_milestone: false
tags: ["统计"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "A"
quality_score: 76.3
generation_method: "research-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"

sources:
  - type: "encyclopedia"
    ref: "Wikipedia - ARIMA"
    url: "https://en.wikipedia.org/wiki/Autoregressive_integrated_moving_average"
  - type: "encyclopedia"
    ref: "Wikipedia - Autocorrelation"
    url: "https://en.wikipedia.org/wiki/Autocorrelation"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 时间序列分析

## 概述

时间序列分析是以等间隔时间点上记录的数据序列为对象，通过建立数学模型来捕捉数据的历史规律并预测未来走势的统计方法。在金融领域，股票收盘价、日度成交量、汇率报价等都是典型的时间序列数据。与横截面数据不同，时间序列数据的相邻观测值之间存在时序相关性（自相关），这是时间序列分析区别于普通回归分析的根本特征。

时间序列分析的现代框架由 George Box 和 Gwilym Jenkins 在 1970 年出版的《Time Series Analysis: Forecasting and Control》中系统化，由此发展出的 ARIMA 模型族被称为 Box-Jenkins 方法，至今仍是金融预测的基准模型。1982 年，Robert Engle 提出 ARCH 模型，专门描述金融收益率的波动聚集现象，并因此获得 2003 年诺贝尔经济学奖，标志着金融时间序列分析进入专业化阶段。

金融从业者需要时间序列分析是因为金融资产价格天然具有路径依赖性——昨日价格影响今日价格，市场波动具有集聚性（大波动后往往跟随大波动），而这些特征无法通过静态统计工具捕捉。准确建模这些动态特征，直接决定了期权定价、风险价值（VaR）计算和量化交易策略的有效性。

---

## 核心原理

### 平稳性与差分变换

平稳性是大多数时间序列模型的前提条件。若一个序列的均值、方差以及任意两期之间的自协方差均不随时间变化，则称该序列为**弱平稳序列**。金融资产价格（如股价）通常是非平稳的，因为它们存在随机游走趋势；但价格的对数收益率 $r_t = \ln(P_t / P_{t-1})$ 通常是平稳的。

判断平稳性的标准工具是**增广迪基-富勒检验（ADF检验）**，其零假设为序列存在单位根（非平稳）。若对原序列差分 $d$ 次后变为平稳，则称原序列为 $I(d)$ 过程，其中沪深300指数日收盘价通常是 $I(1)$ 序列，对其一阶差分即可实现平稳。

### ARIMA 模型结构

ARIMA$(p, d, q)$ 模型由三部分组合而成：
- **AR$(p)$（自回归项）**：当前值是过去 $p$ 期值的线性组合，公式为 $y_t = c + \phi_1 y_{t-1} + \cdots + \phi_p y_{t-p} + \varepsilon_t$
- **I$(d)$（差分阶数）**：对原序列做 $d$ 次差分以消除单位根
- **MA$(q)$（移动平均项）**：当前值包含过去 $q$ 期随机冲击的线性组合，即 $+\theta_1\varepsilon_{t-1}+\cdots+\theta_q\varepsilon_{t-q}$

完整模型写作：
$$\phi(B)(1-B)^d y_t = \theta(B)\varepsilon_t$$

其中 $B$ 为滞后算子，$\varepsilon_t \sim N(0, \sigma^2)$ 为白噪声。模型阶数 $p$ 和 $q$ 的选择依据自相关函数（ACF）和偏自相关函数（PACF）的截尾/拖尾模式，最终用 AIC 或 BIC 准则确定最优参数组合。

### GARCH 模型与波动率动态

金融收益率序列往往呈现**波动聚集性**：大涨大跌后通常跟随更剧烈的波动。ARIMA 假设残差方差恒定，无法刻画这一现象。Bollerslev 在 1986 年将 Engle 的 ARCH 扩展为 GARCH$(p, q)$ 模型，其条件方差方程为：

$$\sigma_t^2 = \omega + \sum_{i=1}^{q} \alpha_i \varepsilon_{t-i}^2 + \sum_{j=1}^{p} \beta_j \sigma_{t-j}^2$$

其中 $\omega > 0$，$\alpha_i \geq 0$，$\beta_j \geq 0$，且需满足 $\sum\alpha_i + \sum\beta_j < 1$ 以保证方差的协方差平稳性。实际研究中，标普500指数日收益率用 GARCH(1,1) 拟合时，$\alpha_1 + \beta_1$ 的估计值通常接近 0.97，反映波动冲击具有极强的持续性。

---

## 实际应用

**量化交易中的价格预测**：对沪深300指数日收益率建立 ARIMA(2,0,1) 模型，利用前20日数据滚动预测次日方向，可以作为趋势型因子的原型信号，尽管单纯 ARIMA 预测效果有限，但其残差序列可用于检测是否存在可利用的线性模式。

**风险管理中的 VaR 计算**：银行在计算99%置信水平下的10日风险价值时，常用 GARCH(1,1) 模型估计未来波动率路径。2008年金融危机中，采用静态历史波动率的 VaR 模型严重低估了风险，而 GARCH 模型因能捕捉波动突变在压力测试中表现更优。

**期权隐含波动率建模**：将 GARCH 条件方差 $\sigma_t^2$ 代入 Black-Scholes 公式，可构建时变波动率期权定价模型（Duan, 1995），比固定波动率假设更能拟合期权的"波动率微笑"曲面。

---

## 常见误区

**误区一：对价格序列直接建模而非收益率序列**。许多初学者直接对股票价格拟合 ARIMA 模型，但股价是 $I(1)$ 序列，不满足平稳性要求，导致出现"伪回归"——模型 $R^2$ 很高但实际没有预测意义。正确做法是对价格取对数差分，转化为收益率序列后再建模，ADF 检验 $p$ 值通常会从 >0.5 降至 <0.01。

**误区二：认为 ARIMA 能预测趋势，GARCH 能预测价格方向**。ARIMA 的均值方程预测的是收益率的条件均值，而金融收益率的可预测性极弱，长期预测迅速收敛至样本均值。GARCH 建模的是条件方差（波动率），输出的是风险量级而非涨跌方向——GARCH 预测波动率增大，并不意味着价格一定下跌。

**误区三：忽视模型残差诊断**。建立 ARIMA-GARCH 模型后，必须检验标准化残差 $\hat{\varepsilon}_t / \hat{\sigma}_t$ 是否通过 Ljung-Box 检验（无序列相关）和 ARCH-LM 检验（无剩余波动聚集效应）。若标准化残差平方仍有自相关，说明 GARCH 阶数选取不足，模型捕捉的波动动态不完整。

---

## 知识关联

**前置知识衔接**：时间序列分析需要概率统计基础中的随机变量、期望、方差和协方差概念，以及简单线性回归的最小二乘思想——ARIMA 的参数估计本质上是带约束的条件最大似然估计，理解这一点有助于把握 AIC 准则的统计含义。

**通向波动率建模**：GARCH(1,1) 是波动率建模的起点，掌握其条件方差方程后，可以进一步学习 EGARCH（捕捉波动的杠杆效应，即下跌时波动率上升更显著）、TGARCH 以及随机波动率模型（SV模型），这些模型专门针对金融时间序列中的负偏度和厚尾特征做出改进。

**通向均值回归策略**：时间序列的平稳性检验直接支撑统计套利。若两只股票的价格之差构成平稳序列（即存在协整关系），则可据此设计均值回归交易策略——价差偏离历史均值超过2倍标准差时开仓，回归时平仓，这是配对交易策略的统计基础。