"""Batch rewrite finance concepts #2: volatility-modeling, high-frequency-trading, futures-basics, time-series-analysis, monte-carlo-simulation."""
import json, sys, re, yaml
from pathlib import Path
from datetime import datetime

PROJECT = Path("D:/echoagent/projects/ai-knowledge-graph")
RAG_ROOT = PROJECT / "data" / "rag"

concepts = {
    "volatility-modeling": {
        "domain": "finance",
        "subdomain": "quantitative-finance",
        "sources": [
            {"type": "encyclopedia", "ref": "Wikipedia - ARCH/GARCH models", "url": "https://en.wikipedia.org/wiki/Autoregressive_conditional_heteroskedasticity"},
            {"type": "educational", "ref": "Investopedia - GARCH", "url": "https://www.investopedia.com/terms/g/garch.asp"},
            {"type": "academic", "ref": "NYU Stern - GARCH 101 (Engle)", "url": "https://www.stern.nyu.edu/rengle/GARCH101.PDF"},
        ],
        "body": """# 波动率建模

## 概述

波动率建模（Volatility Modeling）是量化金融的核心课题之一，旨在刻画和预测资产收益率波动率随时间的变化规律。金融时间序列的一个关键经验事实是**波动率聚集**（volatility clustering）——大幅波动往往跟随大幅波动，小幅波动跟随小幅波动——这使得假设恒定波动率的模型（如基础版 Black-Scholes）产生系统性偏差。

1982 年，Robert F. Engle 提出 **ARCH 模型**（Autoregressive Conditional Heteroskedasticity），首次将时变方差引入计量经济学，因此获得 2003 年诺贝尔经济学奖。1986 年，Tim Bollerslev 将其推广为 **GARCH 模型**（Generalized ARCH），成为至今最广泛使用的波动率模型（Wikipedia: ARCH）。

## 核心知识点

### ARCH(q) 模型

ARCH 模型将条件方差表达为过去残差平方的线性函数：

$$\\sigma_t^2 = \\alpha_0 + \\alpha_1 \\epsilon_{t-1}^2 + \\cdots + \\alpha_q \\epsilon_{t-q}^2$$

其中 ε_t = σ_t·z_t，z_t 为白噪声。参数约束：α₀ > 0，αᵢ ≥ 0。ARCH 效应可通过 Engle 的拉格朗日乘数检验（LM test）检测：在原假设（无 ARCH 效应）下，T'R² 服从 χ²(q) 分布（Wikipedia: ARCH）。

### GARCH(p,q) 模型

GARCH 在 ARCH 基础上加入条件方差的自回归项：

$$\\sigma_t^2 = \\alpha_0 + \\sum_{i=1}^{q} \\alpha_i \\epsilon_{t-i}^2 + \\sum_{j=1}^{p} \\beta_j \\sigma_{t-j}^2$$

**GARCH(1,1)** 是实践中最常用的形式（α₁ + β₁ 的持久性衡量波动率均值回归速度）。当 α₁ + β₁ 接近 1 时，波动率冲击衰减缓慢——这在股票市场中普遍观察到（NYU Stern: GARCH 101）。

### 扩展模型

- **EGARCH**（Nelson, 1991）：捕捉**杠杆效应**——坏消息对波动率的影响大于同等幅度的好消息
- **GJR-GARCH/TARCH**：通过门限变量区分正负冲击的不对称影响
- **随机波动率模型**（Stochastic Volatility）：波动率本身也是随机过程（如 Heston 模型），更灵活但估计更复杂

### 隐含波动率 vs 历史波动率

**历史波动率**从实际价格数据计算，反映过去。**隐含波动率**（IV）从期权市场价格反推（通过 Black-Scholes 公式），反映市场对未来波动率的预期。VIX 指数是标普 500 期权隐含波动率的加权指数，被称为"恐惧指数"。

## 关键要点

1. ARCH/GARCH 模型族是波动率建模的工业标准，GARCH(1,1) 覆盖绝大部分应用场景
2. ARCH 由 Engle (1982) 提出，GARCH 由 Bollerslev (1986) 推广，Engle 因此获 2003 年诺贝尔奖
3. 波动率聚集和尖峰厚尾是金融时间序列的普遍特征，恒定波动率假设是系统性偏差来源
4. EGARCH 和 GJR-GARCH 可以捕捉杠杆效应（坏消息的波动率冲击 > 好消息）
5. 隐含波动率反映市场预期，历史波动率反映过去实现——两者的差异是波动率交易的基础

## 常见误区

1. **"波动率 = 风险"**——波动率只衡量价格变化的幅度，不区分上涨和下跌。尾部风险（极端损失）需要额外的指标（如 VaR、CVaR）
2. **"GARCH(1,1) 总是最好的"**——在存在明显杠杆效应的市场（如股票），EGARCH/GJR-GARCH 通常表现更好
3. **"高 VIX = 股市必跌"**——VIX 反映预期波动率而非方向，高 VIX 可以对应下跌也可以对应急速反弹

## 知识衔接

- **先修**：时间序列分析、概率与统计
- **后续**：期权定价（Black-Scholes）、波动率曲面、风险度量（VaR）"""
    },

    "high-frequency-trading": {
        "domain": "finance",
        "subdomain": "quantitative-finance",
        "sources": [
            {"type": "encyclopedia", "ref": "Wikipedia - High-frequency trading", "url": "https://en.wikipedia.org/wiki/High-frequency_trading"},
            {"type": "educational", "ref": "Investopedia - HFT", "url": "https://www.investopedia.com/terms/h/high-frequency-trading.asp"},
        ],
        "body": """# 高频交易

## 概述

高频交易（High-Frequency Trading，HFT）是一种利用强大计算能力和高速通信技术，以极短时间（秒或毫秒级）进出头寸的算法化自动交易方式。HFT 的核心特征是**高速度**、**高换手率**和**高订单/成交比**（Wikipedia: HFT）。

2009 年，美国高频交易公司仅占交易公司总数的约 2%，但贡献了 **73%** 的股票订单量。2016 年，HFT 平均占股票交易量的 10-40%，外汇和大宗商品交易量的 10-15%（Wikipedia: HFT）。

HFT 公司不持有大量资本、不积累头寸、不隔夜持仓，而是通过大量交易每笔赚取极微小的利润（有时不到 1 美分）。这使得其潜在夏普比率（Sharpe ratio）可以比传统买入持有策略高出数十倍。

## 核心知识点

### 主要策略类型

**做市策略（Market Making）**：HFT 做市商在买卖两端持续报价，赚取**买卖价差**（bid-ask spread）。SEC 定义做市商为"在公开报价下，随时准备买卖特定股票的公司"。

**统计套利（Statistical Arbitrage）**：利用相关资产之间的短暂价格偏差进行配对交易。

**事件驱动套利**：在财报发布、经济数据公告等事件后的毫秒内捕捉价格反应。

**延迟套利（Latency Arbitrage）**：利用不同交易所之间的微小延迟差异获利。

### 技术基础设施

- **共置托管（Co-location）**：将交易服务器物理放置在交易所机房内，将延迟从毫秒降至微秒级
- 2010 年代，HFT 执行时间已从数秒降至**毫秒和微秒级**（Wikipedia: HFT）
- FPGA（现场可编程门阵列）和定制硬件用于进一步降低延迟

### 争议与监管

**2010 年闪电崩盘（Flash Crash）**：2010 年 5 月 6 日，道琼斯指数在几分钟内暴跌近 1000 点又迅速反弹。调查发现 HFT 和算法交易者在流动性快速撤出中起了推波助澜的作用（Wikipedia: HFT）。

2013 年 9 月 2 日，意大利成为全球首个专门针对 HFT 征税的国家——对持仓不足 0.5 秒的交易征收 0.02% 的税。多个欧洲国家也提议限制或禁止 HFT。

HFT 的利润从 2009 年峰值约 50 亿美元降至 2012 年约 12.5 亿美元（Purdue University 估计），反映了竞争加剧和利润空间压缩。

## 关键要点

1. HFT 是算法交易的极端形式：毫秒/微秒级执行，每笔利润极微小但交易量巨大
2. 2009 年美国 HFT 公司占 2% 但贡献 73% 订单量
3. 共置托管（co-location）是 HFT 的关键技术优势，将延迟压缩到微秒级
4. 2010 Flash Crash 暴露了 HFT 在极端行情下可能加剧市场波动的风险
5. HFT 利润从 2009 约 50 亿降至 2012 约 12.5 亿，反映策略拥挤

## 常见误区

1. **"HFT 就是抢在散户前面交易"**——绝大多数 HFT 策略利用微小的市场效率偏差，而非直接针对散户订单
2. **"HFT 对市场有害"**——HFT 做市商提供流动性、缩小买卖价差；但在市场压力时流动性可能瞬间消失
3. **"速度越快越赚钱"**——关键不仅是速度，还有策略的 alpha 来源。纯速度竞赛的利润率在持续下降

## 知识衔接

- **先修**：算法交易基础、市场微结构
- **后续**：市场微结构分析、做市策略、延迟优化"""
    },

    "futures-basics": {
        "domain": "finance",
        "subdomain": "derivatives",
        "sources": [
            {"type": "encyclopedia", "ref": "Wikipedia - Futures contract", "url": "https://en.wikipedia.org/wiki/Futures_contract"},
            {"type": "educational", "ref": "CME Group - Futures Expiration and Settlement", "url": "https://www.cmegroup.com/education/courses/introduction-to-futures/get-to-know-futures-expiration-and-settlement"},
        ],
        "body": """# 期货基础

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
- **后续**：期权基础、对冲策略、基差交易"""
    },

    "time-series-analysis": {
        "domain": "finance",
        "subdomain": "quantitative-finance",
        "sources": [
            {"type": "encyclopedia", "ref": "Wikipedia - ARIMA", "url": "https://en.wikipedia.org/wiki/Autoregressive_integrated_moving_average"},
            {"type": "encyclopedia", "ref": "Wikipedia - Autocorrelation", "url": "https://en.wikipedia.org/wiki/Autocorrelation"},
        ],
        "body": """# 时间序列分析

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
- **后续**：波动率建模（GARCH）、均值回归策略、机器学习时间序列预测"""
    },

    "monte-carlo-simulation": {
        "domain": "finance",
        "subdomain": "quantitative-finance",
        "sources": [
            {"type": "encyclopedia", "ref": "Wikipedia - Monte Carlo methods in finance", "url": "https://en.wikipedia.org/wiki/Monte_Carlo_methods_in_finance"},
            {"type": "academic", "ref": "QuantEcon - Monte Carlo and Option Pricing", "url": "https://intro.quantecon.org/monte_carlo.html"},
        ],
        "body": """# 蒙特卡洛模拟

## 概述

蒙特卡洛方法（Monte Carlo Method）是一类利用**随机采样**来近似求解定量问题的统计技术。在金融领域，蒙特卡洛模拟通过模拟影响金融工具价值的各种不确定性来源，计算其在可能结果范围内的价值分布（Wikipedia: Monte Carlo methods in finance）。

蒙特卡洛方法于 1964 年由 **David B. Hertz** 首次引入金融领域（发表于 Harvard Business Review）。1977 年，**Phelim Boyle** 开创性地将其应用于衍生品定价（发表于 Journal of Financial Economics）。如今它已成为量化金融中不可或缺的工具——当不确定性的维度（来源数量）增加时，蒙特卡洛方法相对于其他数值方法的优势越发明显（Wikipedia: MC in finance）。

## 核心知识点

### 基本原理

蒙特卡洛模拟的核心步骤：
1. **建立随机模型**：指定标的资产价格的随机过程（如几何布朗运动 GBM）
2. **生成大量随机路径**：使用伪随机数模拟价格的可能演化路径
3. **计算每条路径的收益**：在每条路径的终点计算期权/投资的收益
4. **取均值并折现**：所有路径收益的平均值按无风险利率折现 = 期权/投资的价值

精度与模拟次数 N 的关系：标准误差 ∝ 1/√N——要将精度提高 10 倍需要 100 倍的模拟次数。

### 核心金融应用

**期权定价**：特别是路径依赖型期权（亚式期权、障碍期权、回望期权），这些期权的收益取决于标的资产的整个价格路径而非仅到期价格，解析解通常不存在。

**项目估值（实物期权）**：蒙特卡洛模拟用于构建项目 NPV 的概率分布，允许分析者估计项目 NPV 大于零的概率，而非仅得到单一确定值（Wikipedia: MC in finance）。

**固定收益证券**：通过模拟利率的各种可能演化路径，计算债券和利率衍生品在不同利率情景下的价格，然后取平均。

**风险管理（VaR）**：蒙特卡洛法是计算投资组合 VaR（Value at Risk）的三大方法之一，能处理非线性头寸和非正态分布。

### 方差缩减技术

为提高效率（减少达到目标精度所需的模拟次数）：
- **对偶变量法**（Antithetic Variates）：每生成一条路径，同时生成"镜像"路径
- **控制变量法**（Control Variates）：利用已知解析解的相似问题校正估计量
- **重要性采样**（Importance Sampling）：从优化的分布中采样，增加"重要"路径的权重
- **准蒙特卡洛**（Quasi-MC）：使用 Sobol 或 Halton 低差异序列替代伪随机数，可显著加速收敛

## 关键要点

1. 蒙特卡洛模拟的核心是"模拟→计算→平均→折现"
2. 精度 ∝ 1/√N——精度提高 10 倍需要 100 倍计算量
3. 在高维问题（多个不确定性来源）中，MC 比有限差分法、二叉树等方法更有优势
4. 路径依赖型期权（亚式、障碍、回望）是 MC 定价的典型应用场景
5. 方差缩减技术（对偶变量、控制变量、重要性采样）可大幅提高效率

## 常见误区

1. **"蒙特卡洛太慢不实用"**——现代方差缩减技术 + GPU 并行计算使 MC 可在毫秒内完成复杂定价
2. **"模拟次数越多结果越准"**——精度还取决于模型假设的正确性。错误模型 + 百万次模拟 = 精确的错误答案
3. **"蒙特卡洛只能用于期权定价"**——它广泛用于 VaR 计算、项目估值、信用风险建模、投资组合优化等

## 知识衔接

- **先修**：概率与统计、随机过程、衍生品基础
- **后续**：期权定价高级方法、风险价值（VaR）、信用风险建模"""
    },
}


def write_back(cid, info):
    domain = info["domain"]
    rag_dir = RAG_ROOT / domain
    candidates = list(rag_dir.rglob(f"{cid}.md"))
    if not candidates:
        print(f"  ERROR: not found {cid}.md in {rag_dir}")
        return False
    rag_file = candidates[0]
    print(f"  Writing: {rag_file.relative_to(PROJECT)}")
    
    content = rag_file.read_text(encoding="utf-8")
    m = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    meta = {}
    if m:
        try:
            meta = yaml.safe_load(m.group(1)) or {}
        except:
            meta = {}
    
    meta["content_version"] = (meta.get("content_version", 1) or 1) + 1
    meta["generation_method"] = "research-rewrite-v2"
    meta["last_scored"] = datetime.now().strftime("%Y-%m-%d")
    meta["sources"] = info["sources"]
    
    yaml_lines = ["---"]
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
    yaml_lines.append('quality_tier: "pending-rescore"')
    yaml_lines.append(f'quality_score: {meta.get("quality_score", 0)}')
    yaml_lines.append('generation_method: "research-rewrite-v2"')
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
    print(f"Finance Batch Rewrite #2 - {len(concepts)} concepts")
    print("=" * 60)
    
    success = 0
    for cid, info in concepts.items():
        print(f"\n[{cid}]")
        if write_back(cid, info):
            success += 1
            print("  OK")
        else:
            print("  FAILED")
    
    print(f"\n{'='*60}")
    print(f"Done: {success}/{len(concepts)} written")
    
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
            "batch": "finance-batch-2"
        })
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    print(f"Log updated: {log_path}")

if __name__ == "__main__":
    main()
