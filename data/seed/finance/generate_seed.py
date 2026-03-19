#!/usr/bin/env python3
"""Generate Finance knowledge sphere seed graph.

8 subdomains, ~160 concepts covering personal finance to quantitative finance.
"""
import json
from datetime import datetime, timezone

NOW = datetime.now(timezone.utc).isoformat()

DOMAIN = {
    "id": "finance",
    "name": "金融理财",
    "description": "从个人理财到量化金融的系统知识体系",
    "icon": "🟠",
    "color": "#f97316",
}

SUBDOMAINS = [
    {"id": "personal-finance",    "name": "个人理财",     "order": 1},
    {"id": "investment-basics",   "name": "投资基础",     "order": 2},
    {"id": "stock-market",        "name": "股票市场",     "order": 3},
    {"id": "fixed-income",        "name": "固定收益",     "order": 4},
    {"id": "corporate-finance",   "name": "公司金融",     "order": 5},
    {"id": "risk-management",     "name": "风险管理",     "order": 6},
    {"id": "fintech",             "name": "金融科技",     "order": 7},
    {"id": "quantitative-finance","name": "量化金融",     "order": 8},
]

# (id, name, description, subdomain_id, difficulty, minutes, content_type, tags, is_milestone)
CONCEPTS_RAW = [
    # ── personal-finance (20 concepts) ──
    ("personal-finance-overview",  "个人理财概述",           "个人理财的定义、重要性与核心原则",                     "personal-finance", 1, 20, "theory", ["基础"], True),
    ("income-management",          "收入管理",               "工资、被动收入与收入多元化策略",                       "personal-finance", 1, 20, "theory", ["基础"], False),
    ("budgeting",                  "预算编制",               "50/30/20法则、零基预算与预算工具",                     "personal-finance", 1, 25, "practice", ["工具"], True),
    ("saving-strategies",          "储蓄策略",               "应急基金、目标储蓄与自动储蓄机制",                     "personal-finance", 1, 20, "practice", ["策略"], False),
    ("debt-management",            "债务管理",               "好债与坏债、雪球法与雪崩法还债策略",                   "personal-finance", 2, 25, "practice", ["策略"], False),
    ("credit-score",               "信用评分",               "信用评分体系、影响因素与提升方法",                     "personal-finance", 2, 20, "theory", ["信用"], False),
    ("tax-basics",                 "税务基础",               "个人所得税、专项扣除与合法节税方法",                   "personal-finance", 2, 30, "theory", ["税务"], True),
    ("insurance-basics",           "保险基础",               "寿险、健康险、财产险的选择原则",                       "personal-finance", 2, 25, "theory", ["保险"], False),
    ("retirement-planning",        "退休规划",               "养老金、401k/IRA、退休金缺口计算",                    "personal-finance", 3, 35, "practice", ["长期"], True),
    ("estate-planning",            "遗产规划",               "遗嘱、信托与财富传承策略",                             "personal-finance", 3, 30, "theory", ["高级"], False),
    ("financial-goal-setting",     "财务目标设定",           "SMART财务目标与短中长期规划",                          "personal-finance", 1, 20, "practice", ["规划"], False),
    ("emergency-fund",             "应急基金",               "应急储备的最佳规模与存放策略",                         "personal-finance", 1, 15, "practice", ["基础"], False),
    ("consumer-psychology",        "消费心理学",             "心理账户、锚定效应与非理性消费行为",                   "personal-finance", 2, 25, "theory", ["行为"], False),
    ("mortgage-basics",            "房贷基础",               "等额本息vs等额本金、LPR与固定利率选择",                "personal-finance", 2, 30, "practice", ["贷款"], False),
    ("education-funding",          "教育金规划",             "子女教育基金的投资策略与529计划",                      "personal-finance", 3, 25, "practice", ["规划"], False),
    ("inflation-hedging",          "通胀对冲",               "通货膨胀对购买力的影响与应对策略",                     "personal-finance", 2, 25, "theory", ["宏观"], False),
    ("financial-statements-personal","个人财务报表",         "个人资产负债表与现金流量表编制",                       "personal-finance", 2, 25, "practice", ["工具"], False),
    ("compound-interest",          "复利效应",               "复利的数学原理、72法则与时间价值",                     "personal-finance", 1, 20, "theory", ["核心"], True),
    ("financial-independence",     "财务自由",               "FIRE运动、被动收入覆盖率与实现路径",                   "personal-finance", 3, 30, "theory", ["目标"], False),
    ("family-financial-planning",  "家庭财务规划",           "家庭生命周期各阶段的理财策略",                         "personal-finance", 3, 30, "practice", ["规划"], False),

    # ── investment-basics (20 concepts) ──
    ("investment-overview",        "投资概述",               "投资的定义、目的与基本原则",                           "investment-basics", 1, 20, "theory", ["基础"], True),
    ("risk-return-tradeoff",       "风险收益权衡",           "风险与回报的正相关关系与有效前沿",                     "investment-basics", 2, 25, "theory", ["核心"], True),
    ("time-value-of-money",        "货币时间价值",           "现值、终值、年金与贴现率计算",                         "investment-basics", 2, 30, "theory", ["核心"], True),
    ("asset-classes",              "资产类别",               "股票、债券、商品、房地产、另类投资概览",               "investment-basics", 1, 25, "theory", ["基础"], False),
    ("diversification",            "分散投资",               "相关性、分散化原理与不把鸡蛋放一个篮子",              "investment-basics", 2, 25, "theory", ["策略"], True),
    ("asset-allocation",           "资产配置",               "战略配置vs战术配置、年龄法则与再平衡",                 "investment-basics", 2, 30, "practice", ["策略"], False),
    ("dollar-cost-averaging",      "定投策略",               "定期定额投资的优势、局限与实操方法",                   "investment-basics", 2, 20, "practice", ["策略"], False),
    ("market-efficiency",          "市场有效性",             "有效市场假说三种形式与市场异象",                       "investment-basics", 3, 30, "theory", ["理论"], False),
    ("behavioral-finance",         "行为金融学",             "过度自信、损失厌恶、羊群效应等认知偏差",               "investment-basics", 3, 30, "theory", ["行为"], False),
    ("investment-vehicles",        "投资工具",               "共同基金、ETF、REITs等投资载体比较",                   "investment-basics", 2, 25, "theory", ["工具"], False),
    ("index-investing",            "指数投资",               "被动投资哲学、指数基金与追踪误差",                     "investment-basics", 2, 25, "practice", ["策略"], False),
    ("portfolio-theory",           "投资组合理论",           "马科维茨均值-方差模型与最优组合",                      "investment-basics", 3, 35, "theory", ["理论"], False),
    ("capm-model",                 "CAPM模型",               "资本资产定价模型：β系数、市场风险溢价",                "investment-basics", 3, 35, "theory", ["模型"], False),
    ("apt-model",                  "套利定价理论",           "APT多因子模型与套利机会",                              "investment-basics", 4, 30, "theory", ["模型"], False),
    ("investment-psychology",      "投资心理",               "恐惧与贪婪、情绪管理与投资纪律",                       "investment-basics", 2, 25, "theory", ["行为"], False),
    ("investment-horizon",         "投资期限",               "短期vs中期vs长期投资策略选择",                         "investment-basics", 2, 20, "theory", ["策略"], False),
    ("liquidity-concept",          "流动性概念",             "资产流动性定义、衡量与流动性溢价",                     "investment-basics", 2, 20, "theory", ["核心"], False),
    ("benchmark-index",            "基准指数",               "沪深300、标普500等主要指数与业绩基准",                 "investment-basics", 2, 20, "theory", ["工具"], False),
    ("fee-impact",                 "费用影响",               "管理费、交易成本对长期收益的侵蚀效应",                 "investment-basics", 2, 20, "theory", ["实务"], False),
    ("tax-efficient-investing",    "税务优化投资",           "资本利得税、税收递延账户与税务规划",                   "investment-basics", 3, 25, "practice", ["税务"], False),

    # ── stock-market (20 concepts) ──
    ("stock-market-overview",      "股票市场概述",           "股票市场的功能、参与者与交易机制",                     "stock-market", 1, 25, "theory", ["基础"], True),
    ("stock-valuation",            "股票估值",               "内在价值、安全边际与估值方法总览",                     "stock-market", 2, 30, "theory", ["核心"], True),
    ("pe-ratio",                   "市盈率分析",             "PE、PEG、动态PE与行业PE比较",                          "stock-market", 2, 25, "practice", ["指标"], False),
    ("pb-ratio",                   "市净率分析",             "PB估值法及其在不同行业的适用性",                       "stock-market", 2, 25, "practice", ["指标"], False),
    ("dcf-valuation",              "现金流折现",             "DCF模型：自由现金流预测与折现率确定",                  "stock-market", 3, 40, "practice", ["模型"], True),
    ("financial-statement-analysis","财务报表分析",          "三大报表阅读：利润表、资产负债表、现金流量表",         "stock-market", 2, 35, "practice", ["分析"], True),
    ("ratio-analysis",             "比率分析",               "盈利能力、偿债能力、运营效率关键比率",                 "stock-market", 2, 30, "practice", ["分析"], False),
    ("technical-analysis-basics",  "技术分析基础",           "K线图、均线、成交量与趋势判断",                        "stock-market", 2, 30, "practice", ["技术"], False),
    ("chart-patterns",             "图表形态",               "头肩顶/底、双重顶/底、三角形态等经典形态",             "stock-market", 3, 30, "practice", ["技术"], False),
    ("moving-averages",            "移动平均线",             "SMA、EMA、金叉死叉与均线系统",                         "stock-market", 2, 25, "practice", ["指标"], False),
    ("macd-indicator",             "MACD指标",               "MACD原理、信号线、柱状图与背离信号",                   "stock-market", 3, 25, "practice", ["指标"], False),
    ("value-investing",            "价值投资",               "格雷厄姆/巴菲特价值投资哲学与实践",                    "stock-market", 3, 30, "theory", ["策略"], True),
    ("growth-investing",           "成长投资",               "高增长公司识别、PEG估值与成长陷阱",                    "stock-market", 3, 30, "theory", ["策略"], False),
    ("dividend-investing",         "股息投资",               "股息率、派息比率与股息增长策略",                       "stock-market", 2, 25, "practice", ["策略"], False),
    ("sector-analysis",            "行业分析",               "行业生命周期、波特五力与行业轮动",                     "stock-market", 3, 30, "theory", ["分析"], False),
    ("ipo-analysis",               "IPO分析",                "新股发行定价、申购策略与破发风险",                     "stock-market", 3, 25, "practice", ["实务"], False),
    ("market-sentiment",           "市场情绪",               "恐慌指数VIX、投资者情绪指标与逆向投资",                "stock-market", 3, 25, "theory", ["行为"], False),
    ("short-selling",              "做空机制",               "融券卖空的原理、风险与市场功能",                       "stock-market", 3, 25, "theory", ["机制"], False),
    ("stock-screening",            "股票筛选",               "量化筛选条件设定与多因子选股方法",                     "stock-market", 3, 25, "practice", ["工具"], False),
    ("earnings-analysis",          "盈利分析",               "EPS、财报季解读与盈利预期差异",                        "stock-market", 2, 25, "practice", ["分析"], False),

    # ── fixed-income (20 concepts) ──
    ("fixed-income-overview",      "固定收益概述",           "债券市场的功能、参与者与基本概念",                     "fixed-income", 1, 25, "theory", ["基础"], True),
    ("bond-basics",                "债券基础",               "面值、票息、期限、信用评级等核心要素",                 "fixed-income", 1, 25, "theory", ["基础"], True),
    ("yield-curve",                "收益率曲线",             "期限结构、正常/倒挂/平坦收益率曲线解读",               "fixed-income", 2, 30, "theory", ["核心"], True),
    ("bond-pricing",               "债券定价",               "债券价格与收益率的反向关系、久期与凸度",               "fixed-income", 3, 35, "theory", ["核心"], False),
    ("duration-convexity",         "久期与凸度",             "麦考利久期、修正久期与凸度的风险度量",                 "fixed-income", 3, 35, "theory", ["风险"], False),
    ("government-bonds",           "国债",                   "国债种类、拍卖机制与无风险利率基准",                   "fixed-income", 2, 25, "theory", ["品种"], False),
    ("corporate-bonds",            "公司债",                 "公司债信用分析、利差与违约风险",                       "fixed-income", 2, 25, "theory", ["品种"], False),
    ("municipal-bonds",            "地方政府债",             "市政债免税优势与信用分析要点",                         "fixed-income", 2, 25, "theory", ["品种"], False),
    ("bond-rating",                "债券评级",               "标普/穆迪/惠誉评级体系与评级迁移",                     "fixed-income", 2, 25, "theory", ["信用"], False),
    ("credit-spread",              "信用利差",               "信用利差的驱动因素与经济周期关系",                     "fixed-income", 3, 25, "theory", ["风险"], False),
    ("interest-rate-risk",         "利率风险",               "利率变动对债券价格的影响机制",                         "fixed-income", 2, 25, "theory", ["风险"], False),
    ("inflation-linked-bonds",     "通胀挂钩债券",           "TIPS等通胀保护债券的定价与策略",                       "fixed-income", 3, 25, "theory", ["品种"], False),
    ("convertible-bonds",          "可转换债券",             "转债的股债双重属性与转换价值分析",                     "fixed-income", 3, 30, "theory", ["品种"], False),
    ("bond-etf",                   "债券ETF",                "债券ETF的构建、追踪误差与流动性特征",                  "fixed-income", 2, 20, "practice", ["工具"], False),
    ("repo-market",                "回购市场",               "回购协议的机制、功能与系统性风险",                     "fixed-income", 3, 25, "theory", ["市场"], False),
    ("money-market",               "货币市场",               "短期资金市场：同业拆借、商业票据、货币基金",           "fixed-income", 2, 25, "theory", ["市场"], False),
    ("abs-mbs",                    "资产证券化",             "ABS/MBS的结构、分层与提前偿还风险",                    "fixed-income", 4, 35, "theory", ["结构化"], False),
    ("high-yield-bonds",           "高收益债券",             "垃圾债的风险收益特征与投资策略",                       "fixed-income", 3, 25, "theory", ["品种"], False),
    ("bond-ladder",                "债券阶梯策略",           "分散到期日降低再投资风险的策略",                       "fixed-income", 2, 20, "practice", ["策略"], False),
    ("fixed-income-portfolio",     "固收组合管理",           "免疫策略、现金流匹配与积极管理",                       "fixed-income", 4, 35, "practice", ["高级"], False),

    # ── corporate-finance (20 concepts) ──
    ("corporate-finance-overview", "公司金融概述",           "公司金融的三大决策：投资、融资与分配",                 "corporate-finance", 1, 25, "theory", ["基础"], True),
    ("capital-budgeting",          "资本预算",               "NPV、IRR、回收期等投资决策方法",                       "corporate-finance", 2, 35, "practice", ["核心"], True),
    ("npv-analysis",               "净现值分析",             "NPV计算方法、敏感性分析与决策规则",                    "corporate-finance", 2, 30, "practice", ["工具"], False),
    ("irr-method",                 "内部收益率",             "IRR的计算、优缺点与多重IRR问题",                       "corporate-finance", 3, 30, "practice", ["工具"], False),
    ("cost-of-capital",            "资本成本",               "WACC计算：债务成本、股权成本与资本结构权重",           "corporate-finance", 3, 35, "theory", ["核心"], True),
    ("capital-structure",          "资本结构",               "MM定理、权衡理论与最优资本结构",                       "corporate-finance", 3, 35, "theory", ["理论"], True),
    ("dividend-policy",            "股利政策",               "股利无关论、信号理论与回购替代",                       "corporate-finance", 3, 30, "theory", ["分配"], False),
    ("working-capital",            "营运资本管理",           "应收账款、存货、应付账款的优化管理",                   "corporate-finance", 2, 30, "practice", ["运营"], False),
    ("mergers-acquisitions",       "并购分析",               "M&A动机、估值方法与整合挑战",                          "corporate-finance", 4, 40, "theory", ["高级"], False),
    ("leveraged-buyout",           "杠杆收购",               "LBO的结构、回报驱动因素与退出策略",                    "corporate-finance", 4, 35, "theory", ["高级"], False),
    ("ipo-process",                "IPO流程",                "上市准备、定价、路演与上市后管理",                     "corporate-finance", 3, 30, "theory", ["实务"], False),
    ("equity-financing",           "股权融资",               "天使轮到IPO的融资阶段与估值方法",                     "corporate-finance", 2, 25, "theory", ["融资"], False),
    ("debt-financing",             "债务融资",               "银行贷款、债券发行与融资租赁的比较",                   "corporate-finance", 2, 25, "theory", ["融资"], False),
    ("financial-modeling",         "财务建模",               "三表联动模型、DCF模型与LBO模型构建",                  "corporate-finance", 3, 40, "practice", ["技能"], False),
    ("corporate-governance",       "公司治理",               "董事会、股东权益与代理问题",                           "corporate-finance", 2, 25, "theory", ["治理"], False),
    ("esg-investing",              "ESG投资",                "环境、社会、治理因素的投资整合",                       "corporate-finance", 2, 25, "theory", ["前沿"], False),
    ("venture-capital",            "风险投资",               "VC的投资流程、估值方法与退出机制",                     "corporate-finance", 3, 30, "theory", ["创投"], False),
    ("private-equity",             "私募股权",               "PE基金运作、投资策略与价值创造",                       "corporate-finance", 4, 35, "theory", ["创投"], False),
    ("real-options",               "实物期权",               "实物期权在企业投资决策中的应用",                       "corporate-finance", 4, 30, "theory", ["高级"], False),
    ("financial-distress",         "财务困境",               "破产预测模型、债务重组与清算",                         "corporate-finance", 3, 30, "theory", ["风险"], False),

    # ── risk-management (20 concepts) ──
    ("risk-management-overview",   "风险管理概述",           "金融风险的类别、度量与管理框架",                       "risk-management", 1, 25, "theory", ["基础"], True),
    ("market-risk",                "市场风险",               "股票、利率、汇率、商品价格风险",                       "risk-management", 2, 25, "theory", ["类别"], False),
    ("credit-risk",                "信用风险",               "违约概率、违约损失率与信用风险建模",                   "risk-management", 2, 30, "theory", ["类别"], False),
    ("operational-risk",           "操作风险",               "内部流程、人员、系统失误与外部事件风险",               "risk-management", 2, 25, "theory", ["类别"], False),
    ("var-method",                 "VaR方法",                "在险价值的计算：历史模拟、参数法、蒙特卡洛",           "risk-management", 3, 35, "practice", ["工具"], True),
    ("stress-testing",             "压力测试",               "极端情景设计与组合压力测试方法",                       "risk-management", 3, 30, "practice", ["工具"], False),
    ("derivatives-overview",       "衍生品概述",             "期货、期权、互换、远期合约基础",                       "risk-management", 2, 30, "theory", ["工具"], True),
    ("options-basics",             "期权基础",               "看涨/看跌期权、期权定价要素与损益图",                  "risk-management", 2, 30, "theory", ["衍生品"], True),
    ("options-strategies",         "期权策略",               "保护性看跌、备兑看涨、价差策略等",                     "risk-management", 3, 35, "practice", ["衍生品"], False),
    ("futures-basics",             "期货基础",               "期货合约要素、保证金制度与交割机制",                   "risk-management", 2, 25, "theory", ["衍生品"], False),
    ("hedging-strategies",         "对冲策略",               "利用衍生品对冲市场风险的方法",                         "risk-management", 3, 30, "practice", ["策略"], False),
    ("black-scholes-model",        "Black-Scholes模型",      "BS期权定价公式的推导、假设与应用",                     "risk-management", 4, 40, "theory", ["模型"], False),
    ("greeks",                     "希腊字母",               "Delta、Gamma、Theta、Vega等风险度量",                  "risk-management", 3, 30, "theory", ["衍生品"], False),
    ("swap-contracts",             "互换合约",               "利率互换、货币互换的结构与定价",                       "risk-management", 3, 30, "theory", ["衍生品"], False),
    ("currency-risk",              "汇率风险",               "交易风险、折算风险与经济风险管理",                     "risk-management", 2, 25, "theory", ["类别"], False),
    ("liquidity-risk",             "流动性风险",             "资产流动性风险与融资流动性风险",                       "risk-management", 2, 25, "theory", ["类别"], False),
    ("risk-budgeting",             "风险预算",               "风险预算分配与风险平价策略",                           "risk-management", 3, 30, "practice", ["高级"], False),
    ("insurance-products",         "保险产品",               "金融保险产品：年金、万能险、投连险",                   "risk-management", 2, 25, "theory", ["产品"], False),
    ("regulatory-framework",       "金融监管",               "巴塞尔协议、证券法规与合规要求",                       "risk-management", 3, 30, "theory", ["监管"], False),
    ("systemic-risk",              "系统性风险",             "系统性风险的传导机制与宏观审慎监管",                   "risk-management", 4, 30, "theory", ["宏观"], False),

    # ── fintech (20 concepts) ──
    ("fintech-overview",           "金融科技概述",           "金融科技的发展历程、分类与监管挑战",                   "fintech", 1, 25, "theory", ["基础"], True),
    ("mobile-payment",             "移动支付",               "支付宝/微信支付/Apple Pay的技术与商业模式",            "fintech", 1, 20, "theory", ["支付"], False),
    ("digital-banking",            "数字银行",               "纯线上银行的商业模式与技术架构",                       "fintech", 2, 25, "theory", ["银行"], False),
    ("robo-advisor",               "智能投顾",               "算法驱动的资产配置与再平衡服务",                       "fintech", 2, 30, "theory", ["投资"], True),
    ("p2p-lending",                "P2P借贷",                "点对点借贷平台的模式、风险与监管",                     "fintech", 2, 25, "theory", ["借贷"], False),
    ("blockchain-basics",          "区块链基础",             "分布式账本、共识机制与密码学基础",                     "fintech", 2, 30, "theory", ["区块链"], True),
    ("cryptocurrency",             "加密货币",               "比特币、以太坊的技术原理与价值主张",                   "fintech", 2, 30, "theory", ["区块链"], False),
    ("defi",                       "去中心化金融",           "DeFi协议：DEX、借贷、流动性挖矿",                     "fintech", 3, 35, "theory", ["区块链"], False),
    ("stablecoin",                 "稳定币",                 "法币锚定、算法稳定币与CBDC",                           "fintech", 3, 25, "theory", ["区块链"], False),
    ("regtech",                    "监管科技",               "合规自动化、KYC/AML技术解决方案",                      "fintech", 3, 25, "theory", ["监管"], False),
    ("insurtech",                  "保险科技",               "大数据定价、智能理赔与UBI车险",                        "fintech", 2, 25, "theory", ["保险"], False),
    ("open-banking",               "开放银行",               "API经济、数据共享与PSD2合规",                          "fintech", 3, 25, "theory", ["银行"], False),
    ("credit-scoring-ai",          "AI信用评分",             "机器学习在信用评估中的应用与公平性",                   "fintech", 3, 30, "theory", ["AI"], False),
    ("nft-basics",                 "NFT基础",                "非同质化代币的技术标准与应用场景",                     "fintech", 2, 25, "theory", ["区块链"], False),
    ("smart-contracts",            "智能合约",               "自动执行合约的编程、审计与安全",                       "fintech", 3, 30, "theory", ["区块链"], False),
    ("embedded-finance",           "嵌入式金融",             "将金融服务嵌入非金融平台的模式",                       "fintech", 2, 25, "theory", ["趋势"], False),
    ("wealth-management-tech",     "财富管理科技",           "智能投顾进阶、目标导向投资与税务优化",                 "fintech", 3, 30, "theory", ["投资"], False),
    ("digital-currency",           "数字货币CBDC",           "央行数字货币的设计原理与影响",                         "fintech", 3, 25, "theory", ["货币"], False),
    ("cloud-banking",              "云原生银行",             "微服务架构在银行系统中的应用",                         "fintech", 3, 30, "theory", ["技术"], False),
    ("financial-data-analytics",   "金融数据分析",           "大数据在金融风控、营销、定价中的应用",                 "fintech", 2, 25, "practice", ["数据"], False),

    # ── quantitative-finance (20 concepts) ──
    ("quant-finance-overview",     "量化金融概述",           "量化金融的发展、主要领域与职业路径",                   "quantitative-finance", 1, 25, "theory", ["基础"], True),
    ("statistical-arbitrage",      "统计套利",               "配对交易、均值回归与协整关系",                         "quantitative-finance", 3, 35, "theory", ["策略"], False),
    ("factor-models",              "因子模型",               "Fama-French三因子、五因子与多因子投资",                "quantitative-finance", 3, 35, "theory", ["模型"], True),
    ("momentum-strategy",          "动量策略",               "价格动量、盈利动量与动量崩溃风险",                     "quantitative-finance", 3, 30, "practice", ["策略"], False),
    ("mean-reversion",             "均值回归",               "均值回归现象的统计检验与交易策略",                     "quantitative-finance", 3, 30, "theory", ["策略"], False),
    ("high-frequency-trading",     "高频交易",               "HFT策略、市场微结构与技术基础设施",                    "quantitative-finance", 4, 35, "theory", ["高级"], False),
    ("algorithmic-trading",        "算法交易",               "TWAP、VWAP、智能订单路由等执行算法",                   "quantitative-finance", 3, 30, "practice", ["技术"], True),
    ("backtesting",                "回测框架",               "策略回测方法论、过拟合陷阱与样本外验证",               "quantitative-finance", 3, 35, "practice", ["工具"], True),
    ("monte-carlo-simulation",     "蒙特卡洛模拟",           "随机模拟在期权定价与风险管理中的应用",                 "quantitative-finance", 3, 35, "practice", ["工具"], False),
    ("time-series-analysis",       "时间序列分析",           "ARIMA、GARCH等金融时间序列模型",                       "quantitative-finance", 3, 35, "theory", ["统计"], False),
    ("machine-learning-finance",   "机器学习与金融",         "ML在alpha生成、风控、NLP情绪分析中的应用",             "quantitative-finance", 4, 40, "theory", ["AI"], False),
    ("portfolio-optimization",     "组合优化",               "均值-方差优化、Black-Litterman与风险平价",             "quantitative-finance", 4, 40, "practice", ["优化"], False),
    ("risk-factor-analysis",       "风险因子分析",           "系统性风险因子分解与风险归因",                         "quantitative-finance", 3, 30, "theory", ["风险"], False),
    ("execution-cost",             "交易执行成本",           "滑点、市场冲击与最优执行理论",                         "quantitative-finance", 3, 25, "theory", ["实务"], False),
    ("quant-programming",          "量化编程",               "Python/R在量化金融中的应用与工具库",                   "quantitative-finance", 2, 30, "practice", ["技能"], False),
    ("stochastic-calculus",        "随机微积分",             "布朗运动、伊藤引理与SDE在金融中的应用",               "quantitative-finance", 4, 45, "theory", ["数学"], False),
    ("volatility-modeling",        "波动率建模",             "隐含波动率、波动率微笑与GARCH族模型",                 "quantitative-finance", 4, 35, "theory", ["模型"], False),
    ("market-microstructure",      "市场微结构",             "限价订单簿、做市商与价格发现机制",                     "quantitative-finance", 4, 35, "theory", ["理论"], False),
    ("sentiment-analysis-finance", "金融情绪分析",           "新闻/社交媒体文本的情绪提取与交易信号",               "quantitative-finance", 3, 30, "practice", ["AI"], False),
    ("alternative-data",           "另类数据",               "卫星图像、信用卡数据等非传统数据源的投资应用",         "quantitative-finance", 3, 30, "theory", ["前沿"], False),
]


def build_concepts():
    concepts = []
    for (cid, name, desc, sub, diff, mins, ctype, tags, ms) in CONCEPTS_RAW:
        concepts.append({
            "id": cid,
            "name": name,
            "description": desc,
            "domain_id": "finance",
            "subdomain_id": sub,
            "difficulty": diff,
            "estimated_minutes": mins,
            "content_type": ctype,
            "tags": tags,
            "is_milestone": ms,
            "created_at": NOW,
        })
    return concepts


# Edge definitions: (source, target, relation, strength)
EDGES_RAW = [
    # ── personal-finance internal ──
    ("personal-finance-overview", "income-management", "prerequisite", 0.9),
    ("personal-finance-overview", "budgeting", "prerequisite", 0.9),
    ("personal-finance-overview", "financial-goal-setting", "prerequisite", 0.9),
    ("personal-finance-overview", "compound-interest", "prerequisite", 0.8),
    ("income-management", "saving-strategies", "prerequisite", 0.8),
    ("budgeting", "saving-strategies", "prerequisite", 0.8),
    ("saving-strategies", "emergency-fund", "prerequisite", 0.9),
    ("budgeting", "debt-management", "prerequisite", 0.7),
    ("debt-management", "credit-score", "related", 0.8),
    ("debt-management", "mortgage-basics", "prerequisite", 0.7),
    ("credit-score", "mortgage-basics", "related", 0.7),
    ("tax-basics", "retirement-planning", "prerequisite", 0.7),
    ("insurance-basics", "retirement-planning", "related", 0.7),
    ("retirement-planning", "estate-planning", "prerequisite", 0.7),
    ("retirement-planning", "financial-independence", "related", 0.8),
    ("compound-interest", "inflation-hedging", "related", 0.7),
    ("financial-goal-setting", "financial-statements-personal", "prerequisite", 0.7),
    ("consumer-psychology", "budgeting", "related", 0.6),
    ("education-funding", "retirement-planning", "related", 0.7),
    ("financial-independence", "family-financial-planning", "related", 0.7),
    ("saving-strategies", "education-funding", "prerequisite", 0.7),
    ("estate-planning", "family-financial-planning", "related", 0.8),

    # ── investment-basics internal ──
    ("investment-overview", "risk-return-tradeoff", "prerequisite", 0.9),
    ("investment-overview", "asset-classes", "prerequisite", 0.9),
    ("investment-overview", "investment-horizon", "prerequisite", 0.8),
    ("risk-return-tradeoff", "diversification", "prerequisite", 0.9),
    ("risk-return-tradeoff", "time-value-of-money", "related", 0.8),
    ("diversification", "asset-allocation", "prerequisite", 0.9),
    ("asset-allocation", "dollar-cost-averaging", "related", 0.7),
    ("asset-classes", "investment-vehicles", "prerequisite", 0.8),
    ("investment-vehicles", "index-investing", "prerequisite", 0.8),
    ("market-efficiency", "behavioral-finance", "related", 0.8),
    ("market-efficiency", "index-investing", "related", 0.7),
    ("diversification", "portfolio-theory", "prerequisite", 0.8),
    ("portfolio-theory", "capm-model", "prerequisite", 0.9),
    ("capm-model", "apt-model", "prerequisite", 0.8),
    ("behavioral-finance", "investment-psychology", "related", 0.9),
    ("investment-vehicles", "benchmark-index", "related", 0.7),
    ("investment-vehicles", "fee-impact", "related", 0.7),
    ("tax-basics", "tax-efficient-investing", "prerequisite", 0.8),
    ("liquidity-concept", "asset-classes", "related", 0.7),

    # ── stock-market internal ──
    ("stock-market-overview", "stock-valuation", "prerequisite", 0.9),
    ("stock-market-overview", "financial-statement-analysis", "prerequisite", 0.9),
    ("stock-market-overview", "technical-analysis-basics", "prerequisite", 0.8),
    ("stock-valuation", "pe-ratio", "prerequisite", 0.9),
    ("stock-valuation", "pb-ratio", "prerequisite", 0.9),
    ("stock-valuation", "dcf-valuation", "prerequisite", 0.9),
    ("financial-statement-analysis", "ratio-analysis", "prerequisite", 0.9),
    ("financial-statement-analysis", "earnings-analysis", "prerequisite", 0.8),
    ("technical-analysis-basics", "chart-patterns", "prerequisite", 0.8),
    ("technical-analysis-basics", "moving-averages", "prerequisite", 0.8),
    ("moving-averages", "macd-indicator", "prerequisite", 0.8),
    ("stock-valuation", "value-investing", "prerequisite", 0.8),
    ("stock-valuation", "growth-investing", "prerequisite", 0.8),
    ("value-investing", "dividend-investing", "related", 0.7),
    ("financial-statement-analysis", "sector-analysis", "prerequisite", 0.7),
    ("stock-market-overview", "ipo-analysis", "prerequisite", 0.7),
    ("behavioral-finance", "market-sentiment", "related", 0.8),
    ("stock-market-overview", "short-selling", "prerequisite", 0.7),
    ("ratio-analysis", "stock-screening", "prerequisite", 0.7),

    # ── fixed-income internal ──
    ("fixed-income-overview", "bond-basics", "prerequisite", 0.9),
    ("fixed-income-overview", "money-market", "prerequisite", 0.8),
    ("bond-basics", "yield-curve", "prerequisite", 0.9),
    ("bond-basics", "bond-pricing", "prerequisite", 0.9),
    ("bond-basics", "bond-rating", "prerequisite", 0.8),
    ("bond-pricing", "duration-convexity", "prerequisite", 0.9),
    ("yield-curve", "interest-rate-risk", "prerequisite", 0.8),
    ("interest-rate-risk", "duration-convexity", "related", 0.9),
    ("bond-rating", "credit-spread", "prerequisite", 0.8),
    ("bond-rating", "corporate-bonds", "prerequisite", 0.7),
    ("fixed-income-overview", "government-bonds", "prerequisite", 0.8),
    ("bond-basics", "municipal-bonds", "related", 0.7),
    ("bond-basics", "inflation-linked-bonds", "related", 0.7),
    ("bond-basics", "convertible-bonds", "prerequisite", 0.7),
    ("investment-vehicles", "bond-etf", "related", 0.7),
    ("money-market", "repo-market", "prerequisite", 0.7),
    ("corporate-bonds", "abs-mbs", "prerequisite", 0.7),
    ("credit-spread", "high-yield-bonds", "prerequisite", 0.8),
    ("bond-basics", "bond-ladder", "prerequisite", 0.7),
    ("duration-convexity", "fixed-income-portfolio", "prerequisite", 0.8),

    # ── corporate-finance internal ──
    ("corporate-finance-overview", "capital-budgeting", "prerequisite", 0.9),
    ("corporate-finance-overview", "cost-of-capital", "prerequisite", 0.9),
    ("corporate-finance-overview", "capital-structure", "prerequisite", 0.9),
    ("capital-budgeting", "npv-analysis", "prerequisite", 0.9),
    ("capital-budgeting", "irr-method", "prerequisite", 0.9),
    ("cost-of-capital", "capital-structure", "related", 0.9),
    ("capital-structure", "dividend-policy", "related", 0.7),
    ("corporate-finance-overview", "working-capital", "prerequisite", 0.7),
    ("corporate-finance-overview", "corporate-governance", "prerequisite", 0.7),
    ("capital-budgeting", "mergers-acquisitions", "prerequisite", 0.7),
    ("mergers-acquisitions", "leveraged-buyout", "prerequisite", 0.8),
    ("corporate-finance-overview", "equity-financing", "prerequisite", 0.8),
    ("corporate-finance-overview", "debt-financing", "prerequisite", 0.8),
    ("equity-financing", "ipo-process", "prerequisite", 0.8),
    ("equity-financing", "venture-capital", "related", 0.8),
    ("venture-capital", "private-equity", "prerequisite", 0.8),
    ("npv-analysis", "financial-modeling", "prerequisite", 0.7),
    ("dcf-valuation", "financial-modeling", "related", 0.8),
    ("capital-budgeting", "real-options", "prerequisite", 0.7),
    ("debt-financing", "financial-distress", "related", 0.7),
    ("corporate-governance", "esg-investing", "related", 0.7),

    # ── risk-management internal ──
    ("risk-management-overview", "market-risk", "prerequisite", 0.9),
    ("risk-management-overview", "credit-risk", "prerequisite", 0.9),
    ("risk-management-overview", "operational-risk", "prerequisite", 0.8),
    ("risk-management-overview", "derivatives-overview", "prerequisite", 0.8),
    ("market-risk", "var-method", "prerequisite", 0.9),
    ("var-method", "stress-testing", "prerequisite", 0.8),
    ("derivatives-overview", "options-basics", "prerequisite", 0.9),
    ("derivatives-overview", "futures-basics", "prerequisite", 0.9),
    ("derivatives-overview", "swap-contracts", "prerequisite", 0.8),
    ("options-basics", "options-strategies", "prerequisite", 0.9),
    ("options-basics", "black-scholes-model", "prerequisite", 0.8),
    ("options-basics", "greeks", "prerequisite", 0.8),
    ("black-scholes-model", "greeks", "related", 0.9),
    ("derivatives-overview", "hedging-strategies", "prerequisite", 0.8),
    ("market-risk", "currency-risk", "related", 0.8),
    ("market-risk", "liquidity-risk", "related", 0.7),
    ("var-method", "risk-budgeting", "prerequisite", 0.7),
    ("insurance-basics", "insurance-products", "prerequisite", 0.8),
    ("credit-risk", "regulatory-framework", "related", 0.7),
    ("systemic-risk", "regulatory-framework", "related", 0.8),
    ("liquidity-risk", "systemic-risk", "related", 0.7),

    # ── fintech internal ──
    ("fintech-overview", "mobile-payment", "prerequisite", 0.9),
    ("fintech-overview", "digital-banking", "prerequisite", 0.8),
    ("fintech-overview", "blockchain-basics", "prerequisite", 0.8),
    ("fintech-overview", "financial-data-analytics", "prerequisite", 0.8),
    ("digital-banking", "open-banking", "prerequisite", 0.8),
    ("digital-banking", "cloud-banking", "related", 0.7),
    ("blockchain-basics", "cryptocurrency", "prerequisite", 0.9),
    ("blockchain-basics", "smart-contracts", "prerequisite", 0.9),
    ("cryptocurrency", "stablecoin", "prerequisite", 0.8),
    ("cryptocurrency", "defi", "prerequisite", 0.8),
    ("smart-contracts", "defi", "related", 0.8),
    ("blockchain-basics", "nft-basics", "prerequisite", 0.7),
    ("fintech-overview", "robo-advisor", "prerequisite", 0.8),
    ("robo-advisor", "wealth-management-tech", "prerequisite", 0.8),
    ("fintech-overview", "p2p-lending", "prerequisite", 0.7),
    ("p2p-lending", "credit-scoring-ai", "related", 0.7),
    ("fintech-overview", "regtech", "prerequisite", 0.7),
    ("fintech-overview", "insurtech", "prerequisite", 0.7),
    ("stablecoin", "digital-currency", "related", 0.8),
    ("fintech-overview", "embedded-finance", "prerequisite", 0.7),

    # ── quantitative-finance internal ──
    ("quant-finance-overview", "factor-models", "prerequisite", 0.9),
    ("quant-finance-overview", "statistical-arbitrage", "prerequisite", 0.8),
    ("quant-finance-overview", "algorithmic-trading", "prerequisite", 0.8),
    ("quant-finance-overview", "quant-programming", "prerequisite", 0.9),
    ("factor-models", "momentum-strategy", "prerequisite", 0.8),
    ("factor-models", "risk-factor-analysis", "prerequisite", 0.8),
    ("statistical-arbitrage", "mean-reversion", "prerequisite", 0.8),
    ("algorithmic-trading", "high-frequency-trading", "prerequisite", 0.8),
    ("algorithmic-trading", "backtesting", "prerequisite", 0.9),
    ("algorithmic-trading", "execution-cost", "related", 0.8),
    ("backtesting", "monte-carlo-simulation", "related", 0.7),
    ("time-series-analysis", "volatility-modeling", "prerequisite", 0.8),
    ("portfolio-theory", "portfolio-optimization", "prerequisite", 0.8),
    ("black-scholes-model", "stochastic-calculus", "related", 0.8),
    ("monte-carlo-simulation", "stochastic-calculus", "related", 0.7),
    ("machine-learning-finance", "sentiment-analysis-finance", "prerequisite", 0.8),
    ("machine-learning-finance", "alternative-data", "related", 0.7),
    ("high-frequency-trading", "market-microstructure", "related", 0.9),
    ("quant-programming", "backtesting", "related", 0.8),
    ("time-series-analysis", "mean-reversion", "related", 0.7),

    # ── cross-subdomain edges ──
    ("compound-interest", "time-value-of-money", "related", 0.9),
    ("investment-overview", "personal-finance-overview", "prerequisite", 0.7),
    ("asset-allocation", "retirement-planning", "related", 0.7),
    ("stock-market-overview", "investment-overview", "prerequisite", 0.8),
    ("fixed-income-overview", "investment-overview", "prerequisite", 0.8),
    ("risk-return-tradeoff", "risk-management-overview", "related", 0.7),
    ("dcf-valuation", "time-value-of-money", "prerequisite", 0.9),
    ("capital-structure", "corporate-bonds", "related", 0.7),
    ("cost-of-capital", "bond-pricing", "related", 0.7),
    ("financial-modeling", "financial-statement-analysis", "related", 0.8),
    ("portfolio-theory", "risk-budgeting", "related", 0.7),
    ("capm-model", "factor-models", "prerequisite", 0.8),
    ("behavioral-finance", "consumer-psychology", "related", 0.7),
    ("market-sentiment", "sentiment-analysis-finance", "related", 0.8),
    ("stock-screening", "algorithmic-trading", "related", 0.6),
    ("robo-advisor", "asset-allocation", "related", 0.8),
    ("credit-risk", "bond-rating", "related", 0.8),
    ("credit-scoring-ai", "machine-learning-finance", "related", 0.7),
    ("quant-finance-overview", "investment-overview", "prerequisite", 0.7),
    ("volatility-modeling", "var-method", "related", 0.8),
]


def build_edges():
    edges = []
    seen = set()
    for (src, tgt, rel, strength) in EDGES_RAW:
        key = (src, tgt)
        if key not in seen:
            seen.add(key)
            edges.append({
                "source_id": src,
                "target_id": tgt,
                "relation_type": rel,
                "strength": strength,
            })
    return edges


def validate(concepts, edges):
    ids = {c["id"] for c in concepts}
    # Check uniqueness
    assert len(ids) == len(concepts), f"Duplicate concept IDs: {len(concepts)} concepts but {len(ids)} unique IDs"
    # Check edges reference valid concepts
    for e in edges:
        assert e["source_id"] in ids, f"Edge source {e['source_id']} not found"
        assert e["target_id"] in ids, f"Edge target {e['target_id']} not found"
    # Check orphans
    connected = set()
    for e in edges:
        connected.add(e["source_id"])
        connected.add(e["target_id"])
    orphans = ids - connected
    assert len(orphans) == 0, f"Orphan concepts: {orphans}"
    # Check subdomains
    subs = {s["id"] for s in SUBDOMAINS}
    for c in concepts:
        assert c["subdomain_id"] in subs, f"Concept {c['id']} has invalid subdomain {c['subdomain_id']}"


def main():
    concepts = build_concepts()
    edges = build_edges()
    validate(concepts, edges)

    milestones = [c for c in concepts if c["is_milestone"]]

    graph = {
        "domain": DOMAIN,
        "subdomains": SUBDOMAINS,
        "concepts": concepts,
        "edges": edges,
        "meta": {
            "version": "1.0.0",
            "generated_at": NOW,
            "stats": {
                "total_concepts": len(concepts),
                "total_edges": len(edges),
                "subdomains": len(SUBDOMAINS),
                "milestones": len(milestones),
            }
        }
    }

    import os
    out = os.path.join(os.path.dirname(__file__), "seed_graph.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(graph, f, ensure_ascii=False, indent=2)

    print(f"Generated: {len(concepts)} concepts, {len(edges)} edges, {len(SUBDOMAINS)} subdomains, {len(milestones)} milestones")
    from collections import Counter
    subs = Counter(c["subdomain_id"] for c in concepts)
    for s, cnt in subs.most_common():
        print(f"  {s}: {cnt}")


if __name__ == "__main__":
    main()
