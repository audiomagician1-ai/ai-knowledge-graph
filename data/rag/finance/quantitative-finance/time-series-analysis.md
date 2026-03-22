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
quality_tier: "S"
quality_score: 84.6
generation_method: "research-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-03-22"

sources:
  - type: "encyclopedia"
    ref: "Wikipedia - ARIMA"
    url: "https://en.wikipedia.org/wiki/Autoregressive_integrated_moving_average"
  - type: "encyclopedia"
    ref: "Wikipedia - Autocorrelation"
    url: "https://en.wikipedia.org/wiki/Autocorrelation"
scorer_version: "scorer-v2.0"
---
# 时间序列分析

## 概述

时间序列分析（Time Series Analysis）是一套用于分析按时间顺序排列的数据的统计方法，旨在提取有意义的统计特征和识别数据的内在结构。在金融中，时间序列分析是量化交易、风险管理和宏观经济预测的基础工具（Wikipedia: Autocorrelation）。

金融时间序列（如股票价格、利率、汇率）通常表现出**非平稳性**、**波动率聚集**、**尖峰厚尾**和**自相关**等特征，这些特征使得标准统计方法不能直接适用，需要专门的时间序列模型。

## 核心知识点

### 平稳性与差分

**弱平稳**（Weak Stationarity）要求均值和自协方差函数不随时间变化。大多数金融价格序列是非平稳的（有趋势或单位根），但对数收益率通常近似平稳。

**ADF 检验**（Augmented Dickey-Fuller Test）是最常用的单位根检验，原假设为序列存在单位根（非平稳）。

**差分**：将非平稳序列转化为平稳序列。d 阶差分后的序列如果平稳，则原序列是 I(d) 过程。

### ARIMA(p,d,q) 模型

**自回归积分移动平均**模型是时间序列分析的经典框架：

- **AR(p)**——自回归：当前值取决于前 p 个时期的值：X_t = c + Σφᵢ X_{t-i} + ε_t
- **I(d)**——积分：需要 d 阶差分达到平稳
- **MA(q)**——移动平均：当前值取决于前 q 个时期的误差项：X_t = μ + ε_t + Σθⱼ ε_{t-j}

ARIMA 将三者结合，可建模范围广泛的平稳和非平稳序列。参数选择通常依据 **AIC/BIC** 信息准则，以及 ACF/PACF 图的截尾或拖尾特征（Wikipedia: ARIMA）。

**SARIMA** 进一步引入季节性分量，适用于有明显周期性的数据（如零售销售、电力需求）。

### 自相关函数（ACF）与偏自相关函数（PACF）

**ACF**：度量时间序列与其滞后值之间的相关性。ACF 是信号处理和时间序列分析中广泛使用的工具。

**PACF**：在控制了中间滞后的影响后，度量序列与特定滞后的直接相关性。

应用规则：
- AR(p) 过程：PACF 在 lag p 后截尾，ACF 拖尾衰减
- MA(q) 过程：ACF 在 lag q 后截尾，PACF 拖尾衰减
- ARMA：两者都拖尾

### 金融应用专题

- **收益率预测**：ARIMA 用于预测短期收益率，但预测能力通常有限（有效市场假说）
- **波动率建模**：GARCH 族模型（见波动率建模词条）建模时变方差
- **协整分析**：两个非平稳序列的线性组合可能平稳（协整），这是配对交易的理论基础

## 关键要点

1. 金融时间序列通常非平稳，需要差分后才能用 ARIMA 建模
2. ARIMA(p,d,q)：p=自回归阶数、d=差分阶数、q=移动平均阶数
3. ACF/PACF 图是识别 AR/MA 阶数的核心诊断工具
4. ADF 检验检测单位根（非平稳性），Ljung-Box 检验检测残差自相关
5. 金融中常结合 ARIMA（均值方程）+ GARCH（方差方程）联合建模

## 常见误区

1. **"ARIMA 能预测股价走势"**——对弱有效市场，价格变化近似随机游走，ARIMA 的预测能力极其有限
2. **"差分次数越多越好"**——过度差分会引入不必要的移动平均结构，增加模型复杂度
3. **"高 R² = 好模型"**——时间序列中 R² 可能具有误导性，需要用 AIC/BIC 和样本外预测来评估

## 知识衔接

- **先修**：概率与统计、回归分析
- **后续**：波动率建模（GARCH）、均值回归策略、机器学习时间序列预测


### 实际案例

例如，Box-Jenkins方法论在GDP预测中的应用：经济学家使用ARIMA模型对美国季度GDP增长率建模时，首先需要检验序列平稳性（ADF检验），发现原始GDP序列非平稳后取一阶差分(d=1)，然后通过ACF和PACF图选择p=2, q=1参数。经实证研究，ARIMA(2,1,1)模型对短期GDP预测的准确性通常优于简单趋势外推法。

## 思考题

1. 为什么在对金融时间序列建模之前需要检验平稳性？非平稳序列直接建模会导致什么问题？
2. ARIMA模型中的三个参数(p,d,q)分别控制什么？如何选择最优参数组合？
3. 时间序列预测中，为什么样本外测试（out-of-sample）比样本内拟合（in-sample）更能反映模型质量？


## 延伸阅读

- Wikipedia: [Time series](https://en.wikipedia.org/wiki/Time_series)
