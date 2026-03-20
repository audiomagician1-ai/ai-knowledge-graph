#!/usr/bin/env python3
"""Generate Economics knowledge sphere seed graph.

8 subdomains, ~170 concepts covering microeconomics to history of economic thought.
"""
import json
from datetime import datetime, timezone

NOW = datetime.now(timezone.utc).isoformat()

DOMAIN = {
    "id": "economics",
    "name": "经济学",
    "description": "从微观经济学到经济思想史的系统知识体系",
    "icon": "💰",
    "color": "#f59e0b",
}

SUBDOMAINS = [
    {"id": "microeconomics",      "name": "微观经济学",     "order": 1},
    {"id": "macroeconomics",      "name": "宏观经济学",     "order": 2},
    {"id": "behavioral-econ",     "name": "行为经济学",     "order": 3},
    {"id": "international-econ",  "name": "国际经济学",     "order": 4},
    {"id": "development-econ",    "name": "发展经济学",     "order": 5},
    {"id": "econometrics",        "name": "计量经济学",     "order": 6},
    {"id": "public-econ",         "name": "公共经济学",     "order": 7},
    {"id": "economic-thought",    "name": "经济思想史",     "order": 8},
]

# (id, name, description, subdomain_id, difficulty, minutes, content_type, tags, is_milestone)
CONCEPTS_RAW = [
    # ── microeconomics (25 concepts) ──
    ("microeconomics-overview",       "微观经济学概述",       "稀缺性、选择与机会成本等基本经济问题",                         "microeconomics", 1, 20, "theory", ["基础"], True),
    ("supply-demand",                 "供给与需求",           "供给定律、需求定律与市场均衡价格的形成",                       "microeconomics", 1, 25, "theory", ["核心"], False),
    ("elasticity",                    "弹性理论",             "价格弹性、收入弹性、交叉弹性的计算与应用",                     "microeconomics", 2, 30, "theory", ["核心"], False),
    ("consumer-theory",               "消费者理论",           "效用函数、无差异曲线与预算约束下的最优选择",                   "microeconomics", 2, 30, "theory", ["核心"], False),
    ("utility-maximization",          "效用最大化",           "边际效用递减规律与消费者均衡条件",                             "microeconomics", 2, 25, "theory", ["核心"], False),
    ("producer-theory",               "生产者理论",           "生产函数、等产量线与成本最小化",                               "microeconomics", 2, 30, "theory", ["企业"], False),
    ("cost-theory",                   "成本理论",             "短期与长期成本曲线、规模经济与范围经济",                       "microeconomics", 3, 30, "theory", ["企业"], False),
    ("perfect-competition",           "完全竞争市场",         "价格接受者、利润最大化与长期均衡",                             "microeconomics", 2, 25, "theory", ["市场结构"], True),
    ("monopoly",                      "垄断市场",             "价格歧视、自然垄断与反垄断政策",                               "microeconomics", 3, 30, "theory", ["市场结构"], False),
    ("monopolistic-competition",      "垄断竞争",             "产品差异化、短期利润与长期零利润均衡",                         "microeconomics", 3, 25, "theory", ["市场结构"], False),
    ("oligopoly",                     "寡头市场",             "古诺模型、伯特兰模型与斯塔克伯格模型",                         "microeconomics", 3, 30, "theory", ["市场结构"], False),
    ("game-theory-econ",              "博弈论基础",           "纳什均衡、囚徒困境与策略互动分析",                             "microeconomics", 3, 35, "theory", ["分析工具"], True),
    ("market-failure",                "市场失灵",             "外部性、公共品、信息不对称与市场势力",                         "microeconomics", 3, 25, "theory", ["政策"], False),
    ("externalities",                 "外部性",               "正外部性与负外部性及其纠正手段（庇古税、科斯定理）",           "microeconomics", 3, 30, "theory", ["政策"], False),
    ("public-goods",                  "公共品",               "非竞争性、非排他性与搭便车问题",                               "microeconomics", 2, 20, "theory", ["政策"], False),
    ("information-asymmetry",         "信息不对称",           "逆向选择、道德风险与信号传递机制",                             "microeconomics", 3, 30, "theory", ["信息"], False),
    ("factor-markets",                "要素市场",             "劳动、资本与土地市场的价格决定",                               "microeconomics", 3, 25, "theory", ["分配"], False),
    ("welfare-economics",             "福利经济学",           "帕累托效率、社会福利函数与福利定理",                           "microeconomics", 3, 30, "theory", ["福利"], False),
    ("general-equilibrium",           "一般均衡理论",         "瓦尔拉斯一般均衡与阿罗-德布鲁模型",                           "microeconomics", 4, 35, "theory", ["高级"], False),
    ("auction-theory",                "拍卖理论",             "英式、荷式、密封拍卖与最优拍卖机制设计",                       "microeconomics", 4, 30, "theory", ["机制设计"], False),
    ("contract-theory",               "契约理论",             "委托代理问题、激励相容与机制设计基础",                         "microeconomics", 4, 30, "theory", ["信息"], False),
    ("behavioral-micro",              "行为微观经济学",       "有限理性对消费者与企业决策的影响",                             "microeconomics", 3, 25, "theory", ["行为"], False),
    ("market-design",                 "市场设计",             "匹配市场、学校选择与器官分配机制",                             "microeconomics", 4, 30, "theory", ["机制设计"], False),
    ("income-distribution",           "收入分配",             "洛伦茨曲线、基尼系数与收入不平等度量",                         "microeconomics", 2, 25, "theory", ["分配"], False),
    ("marginal-analysis",             "边际分析",             "边际成本、边际收益与经济决策的边际原则",                       "microeconomics", 2, 20, "theory", ["核心"], False),

    # ── macroeconomics (25 concepts) ──
    ("macroeconomics-overview",       "宏观经济学概述",       "国民经济总量指标与宏观经济学的研究框架",                       "macroeconomics", 1, 20, "theory", ["基础"], True),
    ("gdp-measurement",               "GDP核算",              "国内生产总值的三种核算方法与名义/实际GDP",                     "macroeconomics", 1, 25, "theory", ["核心"], False),
    ("aggregate-demand-supply",       "总供给与总需求",       "AD-AS模型与宏观经济均衡",                                     "macroeconomics", 2, 30, "theory", ["核心"], False),
    ("inflation",                     "通货膨胀",             "通胀的度量、成因（需求拉动/成本推动/预期）与影响",             "macroeconomics", 2, 25, "theory", ["现象"], False),
    ("unemployment",                  "失业",                 "失业类型（摩擦/结构/周期）、自然失业率与奥肯定律",             "macroeconomics", 2, 25, "theory", ["现象"], False),
    ("business-cycle",                "经济周期",             "繁荣、衰退、萧条与复苏的周期性波动",                           "macroeconomics", 2, 25, "theory", ["波动"], False),
    ("fiscal-policy",                 "财政政策",             "政府支出、税收与财政乘数效应",                                 "macroeconomics", 2, 30, "theory", ["政策"], False),
    ("monetary-policy",               "货币政策",             "利率调控、公开市场操作与量化宽松",                             "macroeconomics", 2, 30, "theory", ["政策"], True),
    ("money-banking",                 "货币与银行",           "货币创造、商业银行体系与中央银行职能",                         "macroeconomics", 2, 25, "theory", ["金融"], False),
    ("interest-rates",                "利率理论",             "名义利率与实际利率、利率的期限结构",                           "macroeconomics", 3, 25, "theory", ["金融"], False),
    ("economic-growth",               "经济增长理论",         "索洛模型、内生增长理论与全要素生产率",                         "macroeconomics", 3, 35, "theory", ["增长"], True),
    ("is-lm-model",                   "IS-LM模型",            "产品市场与货币市场的同时均衡分析",                             "macroeconomics", 3, 30, "theory", ["模型"], False),
    ("phillips-curve",                "菲利普斯曲线",         "通胀与失业的短期权衡与长期垂直",                               "macroeconomics", 3, 25, "theory", ["模型"], False),
    ("consumption-saving",            "消费与储蓄",           "凯恩斯消费函数、永久收入假说与生命周期假说",                   "macroeconomics", 3, 30, "theory", ["核心"], False),
    ("investment-theory",             "投资理论",             "投资决定因素、托宾Q理论与加速器模型",                           "macroeconomics", 3, 25, "theory", ["核心"], False),
    ("national-debt",                 "国债与财政赤字",       "政府债务的可持续性、挤出效应与代际公平",                       "macroeconomics", 3, 25, "theory", ["政策"], False),
    ("exchange-rate-macro",           "汇率与宏观经济",       "汇率决定理论、购买力平价与蒙代尔-弗莱明模型",                 "macroeconomics", 3, 30, "theory", ["开放经济"], False),
    ("open-economy-macro",            "开放经济宏观",         "经常账户、资本账户与国际收支平衡",                             "macroeconomics", 3, 25, "theory", ["开放经济"], False),
    ("rational-expectations",         "理性预期",             "理性预期假说与政策无效性命题",                                 "macroeconomics", 4, 25, "theory", ["预期"], False),
    ("new-keynesian",                 "新凯恩斯主义",         "价格粘性、菜单成本与DSGE模型基础",                             "macroeconomics", 4, 30, "theory", ["学派"], False),
    ("financial-crisis-macro",        "金融危机与宏观",       "系统性风险、银行挤兑与最后贷款人",                             "macroeconomics", 3, 25, "theory", ["危机"], False),
    ("labor-market-macro",            "宏观劳动市场",         "工资刚性、效率工资与劳动力参与率",                             "macroeconomics", 3, 25, "theory", ["劳动"], False),
    ("monetary-transmission",         "货币传导机制",         "利率渠道、信贷渠道与资产价格渠道",                             "macroeconomics", 3, 25, "theory", ["金融"], False),
    ("macroprudential-policy",        "宏观审慎政策",         "系统性风险监管、资本缓冲与逆周期工具",                         "macroeconomics", 4, 25, "theory", ["政策"], False),
    ("supply-side-economics",         "供给侧经济学",         "减税刺激供给、拉弗曲线与结构性改革",                           "macroeconomics", 3, 20, "theory", ["学派"], False),

    # ── behavioral-econ (18 concepts) ──
    ("behavioral-econ-overview",      "行为经济学概述",       "有限理性、有限意志力、有限自利与传统经济学的偏离",             "behavioral-econ", 1, 20, "theory", ["基础"], True),
    ("prospect-theory",               "前景理论",             "参考点依赖、损失厌恶与价值函数的S形曲线",                     "behavioral-econ", 2, 30, "theory", ["核心"], True),
    ("cognitive-biases-econ",         "认知偏差",             "锚定效应、可得性偏差与代表性启发在经济决策中的影响",           "behavioral-econ", 2, 25, "theory", ["偏差"], False),
    ("heuristics-econ",               "启发式判断",           "简单规则在不确定性下的决策作用与局限",                         "behavioral-econ", 2, 25, "theory", ["偏差"], False),
    ("framing-effects",               "框架效应",             "信息呈现方式对选择的系统性影响",                               "behavioral-econ", 2, 20, "theory", ["偏差"], False),
    ("mental-accounting",             "心理账户",             "消费者如何对金钱进行心理分类与非替代性",                       "behavioral-econ", 2, 25, "theory", ["消费"], False),
    ("time-inconsistency-behav",      "时间不一致性",         "双曲贴现、即时满足偏好与自我控制问题",                         "behavioral-econ", 3, 25, "theory", ["决策"], False),
    ("nudge-theory",                  "助推理论",             "自由家长主义、默认选项与选择架构设计",                         "behavioral-econ", 2, 25, "theory", ["应用"], True),
    ("bounded-rationality",           "有限理性",             "西蒙的满意决策理论与认知资源约束",                             "behavioral-econ", 2, 20, "theory", ["核心"], False),
    ("social-preferences",            "社会偏好",             "公平偏好、互惠行为与利他主义的经济学解释",                     "behavioral-econ", 3, 25, "theory", ["社会"], False),
    ("overconfidence-econ",           "过度自信",             "过度自信对投资、创业与预测的影响",                             "behavioral-econ", 2, 20, "theory", ["偏差"], False),
    ("endowment-effect",              "禀赋效应",             "拥有物品后的高估值倾向与WTP/WTA差异",                         "behavioral-econ", 2, 20, "theory", ["偏差"], False),
    ("herding-behavior",              "羊群效应",             "信息级联与从众行为在金融市场中的表现",                         "behavioral-econ", 3, 25, "theory", ["金融"], False),
    ("behavioral-finance",            "行为金融学",           "市场异象、投资者情绪与非有效市场现象",                         "behavioral-econ", 3, 30, "theory", ["金融"], False),
    ("experimental-economics",        "实验经济学",           "实验室实验、田野实验与经济理论检验方法",                       "behavioral-econ", 3, 25, "theory", ["方法"], False),
    ("neuroeconomics",                "神经经济学",           "大脑决策机制、奖赏系统与经济选择的神经基础",                   "behavioral-econ", 4, 25, "theory", ["前沿"], False),
    ("default-effects",               "默认效应",             "默认选项对退休储蓄、器官捐献等决策的巨大影响",                 "behavioral-econ", 2, 20, "theory", ["应用"], False),
    ("sunk-cost-fallacy",             "沉没成本谬误",         "已付出不可回收成本对后续决策的非理性影响",                     "behavioral-econ", 2, 20, "theory", ["偏差"], False),

    # ── international-econ (22 concepts) ──
    ("international-econ-overview",   "国际经济学概述",       "国际贸易与国际金融的基本框架",                                 "international-econ", 1, 20, "theory", ["基础"], True),
    ("comparative-advantage",         "比较优势",             "李嘉图比较优势理论与贸易互利的基本原理",                       "international-econ", 2, 25, "theory", ["贸易"], True),
    ("absolute-advantage",            "绝对优势",             "亚当·斯密的绝对优势理论与国际分工",                            "international-econ", 1, 20, "theory", ["贸易"], False),
    ("heckscher-ohlin",               "赫克歇尔-俄林模型",   "要素禀赋差异与贸易模式的决定",                                 "international-econ", 3, 30, "theory", ["贸易"], False),
    ("trade-policy",                  "贸易政策",             "关税、配额、补贴与战略性贸易政策",                             "international-econ", 2, 25, "theory", ["政策"], True),
    ("free-trade-agreements",         "自由贸易协定",         "WTO规则、区域经济一体化与FTA的福利效应",                       "international-econ", 2, 25, "theory", ["制度"], False),
    ("exchange-rate-systems",         "汇率制度",             "固定汇率、浮动汇率与管理浮动汇率制度比较",                     "international-econ", 2, 25, "theory", ["金融"], False),
    ("balance-of-payments",           "国际收支",             "经常账户、资本与金融账户的结构与平衡",                         "international-econ", 2, 25, "theory", ["金融"], False),
    ("foreign-exchange-market",       "外汇市场",             "外汇交易机制、汇率决定与套利平价条件",                         "international-econ", 3, 25, "theory", ["金融"], False),
    ("international-capital-flows",   "国际资本流动",         "FDI、证券投资与短期资本流动的动因与影响",                      "international-econ", 3, 25, "theory", ["金融"], False),
    ("currency-crisis",               "货币危机",             "投机攻击、三代货币危机模型与防范机制",                         "international-econ", 4, 30, "theory", ["危机"], False),
    ("terms-of-trade",                "贸易条件",             "进出口价格比率变动与贸易利益分配",                             "international-econ", 3, 20, "theory", ["贸易"], False),
    ("new-trade-theory",              "新贸易理论",           "规模经济、产品差异化与产业内贸易解释",                         "international-econ", 3, 30, "theory", ["理论"], False),
    ("trade-and-development",         "贸易与发展",           "出口导向vs进口替代战略与贸易对发展中国家的影响",               "international-econ", 3, 25, "theory", ["发展"], False),
    ("global-value-chains",           "全球价值链",           "生产环节的国际分工、增值贸易与产业升级",                       "international-econ", 3, 25, "theory", ["现代"], True),
    ("multinational-corporations",    "跨国公司",             "FDI理论、转移定价与跨国企业的经济影响",                        "international-econ", 3, 25, "theory", ["企业"], False),
    ("trade-wars",                    "贸易战",               "报复性关税、贸易摩擦的博弈分析与经济后果",                     "international-econ", 3, 25, "theory", ["政策"], False),
    ("international-monetary-system", "国际货币体系",         "从金本位到布雷顿森林再到牙买加体系的演变",                     "international-econ", 3, 25, "theory", ["制度"], False),
    ("regional-integration",          "区域经济一体化",       "自由贸易区、关税同盟、共同市场与经济联盟",                     "international-econ", 2, 25, "theory", ["制度"], False),
    ("trade-gravity-model",           "贸易引力模型",         "经济规模与距离对双边贸易量的决定性影响",                       "international-econ", 3, 20, "theory", ["实证"], False),
    ("migration-economics",           "移民经济学",           "劳动力国际流动的经济效应与移民政策分析",                       "international-econ", 3, 25, "theory", ["劳动"], False),
    ("digital-trade",                 "数字贸易",             "跨境数据流动、数字服务贸易与电子商务规则",                     "international-econ", 3, 25, "theory", ["现代"], False),

    # ── development-econ (20 concepts) ──
    ("development-econ-overview",     "发展经济学概述",       "经济发展与经济增长的区别、发展的多维度衡量",                   "development-econ", 1, 20, "theory", ["基础"], True),
    ("poverty-inequality",            "贫困与不平等",         "绝对贫困与相对贫困、不平等度量与贫困陷阱",                     "development-econ", 2, 25, "theory", ["核心"], True),
    ("human-development-index",       "人类发展指数",         "HDI的构成（健康/教育/收入）与发展评估",                        "development-econ", 1, 20, "theory", ["指标"], False),
    ("structural-transformation",     "结构转型",             "从农业到工业再到服务业的经济结构演变",                         "development-econ", 2, 25, "theory", ["转型"], True),
    ("industrialization",             "工业化",               "工业化路径选择、产业政策与后发优势",                           "development-econ", 2, 25, "theory", ["转型"], False),
    ("agriculture-development",       "农业与发展",           "绿色革命、小农经济与农业现代化路径",                           "development-econ", 2, 25, "theory", ["部门"], False),
    ("microfinance",                  "小额金融",             "格莱珉银行模式、普惠金融与贫困减缓效果",                       "development-econ", 2, 25, "theory", ["金融"], False),
    ("foreign-aid",                   "对外援助",             "官方发展援助的有效性争论与援助依赖问题",                       "development-econ", 3, 25, "theory", ["政策"], False),
    ("institutions-development",      "制度与发展",           "产权保护、法治与制度质量对经济发展的核心作用",                 "development-econ", 3, 30, "theory", ["制度"], True),
    ("rct-development",               "随机对照试验",         "RCT在发展经济学中的应用与政策评估革命",                        "development-econ", 3, 25, "theory", ["方法"], True),
    ("education-economics",           "教育经济学",           "人力资本投资回报、教育与经济增长的关系",                       "development-econ", 2, 25, "theory", ["人力资本"], False),
    ("health-economics-dev",          "健康经济学",           "健康与生产力、疾病负担与发展中国家医疗体系",                   "development-econ", 2, 25, "theory", ["人力资本"], False),
    ("urbanization-econ",             "城市化经济学",         "城市化进程、集聚经济与城市问题",                               "development-econ", 2, 25, "theory", ["空间"], False),
    ("natural-resources-curse",       "资源诅咒",             "自然资源丰裕与经济增长困境的理论解释",                         "development-econ", 3, 25, "theory", ["资源"], False),
    ("population-economics",          "人口经济学",           "人口转变理论、人口红利与老龄化的经济影响",                     "development-econ", 2, 25, "theory", ["人口"], False),
    ("sustainable-development",       "可持续发展",           "环境-经济协调、SDGs与绿色增长路径",                            "development-econ", 2, 25, "theory", ["环境"], False),
    ("technology-transfer",           "技术转移",             "技术扩散机制、适宜技术与创新对发展的作用",                     "development-econ", 3, 25, "theory", ["技术"], False),
    ("gender-economics",              "性别经济学",           "性别差距的经济分析、女性赋权与发展效应",                       "development-econ", 2, 25, "theory", ["社会"], False),
    ("informal-economy",              "非正规经济",           "发展中国家非正规部门的规模、成因与正规化",                     "development-econ", 3, 25, "theory", ["部门"], False),
    ("development-finance",           "发展融资",             "国内资本动员、国际融资渠道与债务可持续性",                     "development-econ", 3, 25, "theory", ["金融"], False),

    # ── econometrics (18 concepts) ──
    ("econometrics-overview",         "计量经济学概述",       "经济数据类型、计量模型的基本框架与因果推断目标",               "econometrics", 1, 20, "theory", ["基础"], True),
    ("linear-regression",             "线性回归",             "OLS估计、假设检验与回归结果解读",                              "econometrics", 2, 30, "theory", ["核心"], True),
    ("multiple-regression",           "多元回归",             "多变量模型设定、多重共线性与遗漏变量偏误",                     "econometrics", 2, 30, "theory", ["核心"], False),
    ("hypothesis-testing-econ",       "假设检验",             "t检验、F检验与经济假说的统计检验",                             "econometrics", 2, 25, "theory", ["统计"], False),
    ("endogeneity",                   "内生性问题",           "遗漏变量、测量误差与联立性导致的估计偏误",                     "econometrics", 3, 30, "theory", ["核心"], True),
    ("instrumental-variables",        "工具变量法",           "IV估计、两阶段最小二乘法(2SLS)与工具有效性检验",              "econometrics", 3, 35, "theory", ["因果"], True),
    ("panel-data",                    "面板数据分析",         "固定效应、随机效应模型与Hausman检验",                          "econometrics", 3, 30, "theory", ["方法"], False),
    ("time-series-econ",              "时间序列分析",         "平稳性检验、ARIMA模型与VAR模型",                              "econometrics", 3, 30, "theory", ["方法"], False),
    ("diff-in-diff",                  "双重差分法",           "DID设计、平行趋势假设与政策效果评估",                          "econometrics", 3, 30, "theory", ["因果"], True),
    ("regression-discontinuity",      "断点回归",             "RDD设计、局部随机化与带宽选择",                               "econometrics", 4, 30, "theory", ["因果"], False),
    ("propensity-score",              "倾向得分匹配",         "PSM方法、处理效应估计与观测数据因果推断",                      "econometrics", 3, 25, "theory", ["因果"], False),
    ("maximum-likelihood",            "极大似然估计",         "MLE原理、渐近性质与非线性模型估计",                            "econometrics", 3, 25, "theory", ["高级"], False),
    ("limited-dependent",             "有限因变量模型",       "Logit、Probit模型与离散选择分析",                              "econometrics", 3, 25, "theory", ["模型"], False),
    ("heteroskedasticity",            "异方差",               "异方差检验、后果与稳健标准误修正",                             "econometrics", 3, 25, "theory", ["诊断"], False),
    ("autocorrelation-econ",          "自相关",               "时间序列自相关的检测与修正方法",                               "econometrics", 3, 25, "theory", ["诊断"], False),
    ("causal-inference",              "因果推断",             "潜在结果框架、鲁宾因果模型与因果效应识别策略",                 "econometrics", 4, 30, "theory", ["前沿"], False),
    ("machine-learning-econ",         "机器学习与经济学",     "预测vs因果、LASSO/随机森林在经济分析中的应用",                 "econometrics", 4, 30, "theory", ["前沿"], False),
    ("synthetic-control",             "合成控制法",           "比较案例研究的定量方法与政策评估应用",                         "econometrics", 4, 25, "theory", ["因果"], False),

    # ── public-econ (22 concepts) ──
    ("public-econ-overview",          "公共经济学概述",       "政府在市场经济中的角色、公共部门的经济分析框架",               "public-econ", 1, 20, "theory", ["基础"], True),
    ("taxation-principles",           "税收原则",             "效率、公平与简便的税制设计原则",                               "public-econ", 2, 25, "theory", ["税收"], True),
    ("tax-incidence",                 "税收归宿",             "税负转嫁与弹性对税收负担分配的影响",                           "public-econ", 2, 25, "theory", ["税收"], False),
    ("optimal-taxation",              "最优税收理论",         "拉姆齐规则、最优所得税与米尔利斯模型",                         "public-econ", 4, 30, "theory", ["税收"], False),
    ("income-tax",                    "所得税",               "个人所得税与企业所得税的设计与经济效应",                       "public-econ", 2, 25, "theory", ["税种"], False),
    ("consumption-tax",               "消费税",               "增值税、销售税的效率特性与累退性讨论",                         "public-econ", 2, 20, "theory", ["税种"], False),
    ("public-expenditure",            "公共支出",             "公共支出的规模决定、效率评估与瓦格纳法则",                     "public-econ", 2, 25, "theory", ["支出"], True),
    ("social-insurance",              "社会保险",             "养老保险、医疗保险与失业保险的经济学分析",                     "public-econ", 2, 25, "theory", ["福利"], False),
    ("public-choice",                 "公共选择理论",         "投票悖论、中位选民定理与官僚行为模型",                         "public-econ", 3, 30, "theory", ["制度"], True),
    ("rent-seeking",                  "寻租",                 "寻租行为的经济损失与防范机制设计",                             "public-econ", 3, 25, "theory", ["制度"], False),
    ("cost-benefit-analysis",         "成本收益分析",         "项目评估中的折现、影子价格与社会贴现率",                       "public-econ", 3, 30, "theory", ["方法"], False),
    ("environmental-economics",       "环境经济学",           "碳税、排放权交易与环境政策的经济分析",                         "public-econ", 3, 25, "theory", ["环境"], False),
    ("fiscal-federalism",             "财政联邦主义",         "中央与地方财政关系、财政分权与转移支付",                       "public-econ", 3, 25, "theory", ["制度"], False),
    ("government-failure",            "政府失灵",             "寻租、官僚效率与政府干预的局限性",                             "public-econ", 3, 20, "theory", ["制度"], False),
    ("pigouvian-tax",                 "庇古税",               "通过税收内化外部性的理论基础与实践",                           "public-econ", 3, 20, "theory", ["环境"], False),
    ("property-rights-econ",          "产权经济学",           "产权界定、科斯定理与交易成本分析",                             "public-econ", 3, 25, "theory", ["制度"], False),
    ("regulation-economics",          "规制经济学",           "自然垄断规制、信息不对称与规制俘获",                           "public-econ", 3, 25, "theory", ["规制"], False),
    ("welfare-state",                 "福利国家",             "福利国家模式比较、再分配效应与财政可持续性",                   "public-econ", 3, 25, "theory", ["福利"], False),
    ("behavioral-public-policy",      "行为公共政策",         "助推在公共政策中的应用：退休储蓄、健康与节能",                 "public-econ", 3, 25, "theory", ["行为"], False),
    ("education-policy-econ",         "教育政策经济学",       "教育券、学校竞争与教育投入的回报率分析",                       "public-econ", 3, 25, "theory", ["政策"], False),
    ("healthcare-economics",          "医疗经济学",           "医疗保险市场、信息不对称与医疗改革经济分析",                   "public-econ", 3, 25, "theory", ["政策"], False),
    ("pension-economics",             "养老金经济学",         "现收现付vs基金制、人口老龄化与养老金改革",                     "public-econ", 3, 25, "theory", ["福利"], False),

    # ── economic-thought (20 concepts) ──
    ("economic-thought-overview",     "经济思想史概述",       "经济学从古典到现代的思想演变脉络",                             "economic-thought", 1, 20, "theory", ["基础"], True),
    ("adam-smith",                    "亚当·斯密",            "《国富论》、看不见的手与古典自由主义经济学",                   "economic-thought", 1, 25, "theory", ["古典"], True),
    ("david-ricardo",                 "大卫·李嘉图",          "比较优势、劳动价值论与收入分配理论",                           "economic-thought", 2, 25, "theory", ["古典"], False),
    ("karl-marx-econ",                "马克思经济学",         "剩余价值、资本积累与经济危机理论",                             "economic-thought", 2, 30, "theory", ["古典"], False),
    ("marginalism",                   "边际主义革命",         "杰文斯、门格尔与瓦尔拉斯的边际效用理论",                      "economic-thought", 2, 25, "theory", ["新古典"], False),
    ("alfred-marshall",               "马歇尔经济学",         "局部均衡分析、供需剪刀模型与新古典综合",                       "economic-thought", 2, 25, "theory", ["新古典"], False),
    ("keynesian-revolution",          "凯恩斯革命",           "有效需求、流动性偏好与政府干预的理论基础",                     "economic-thought", 2, 30, "theory", ["凯恩斯"], True),
    ("monetarism",                    "货币主义",             "弗里德曼的货币数量论、自然失业率与规则性政策",                 "economic-thought", 3, 25, "theory", ["芝加哥"], False),
    ("austrian-school",               "奥地利学派",           "主观价值论、企业家精神与自发秩序理论",                         "economic-thought", 3, 25, "theory", ["学派"], False),
    ("institutional-economics",       "制度经济学",           "交易成本、产权理论与制度变迁分析",                             "economic-thought", 3, 25, "theory", ["制度"], False),
    ("chicago-school",                "芝加哥学派",           "市场效率、理性预期与法律经济学传统",                           "economic-thought", 3, 25, "theory", ["学派"], False),
    ("development-thought",           "发展思想演变",         "从现代化理论到华盛顿共识再到制度主义的发展观",                 "economic-thought", 3, 25, "theory", ["发展"], False),
    ("neoclassical-synthesis",        "新古典综合",           "IS-LM框架、菲利普斯曲线与凯恩斯-新古典融合",                  "economic-thought", 3, 25, "theory", ["综合"], False),
    ("new-institutional",             "新制度经济学",         "科斯、诺斯与威廉姆森的制度分析框架",                           "economic-thought", 3, 25, "theory", ["制度"], False),
    ("behavioral-thought",            "行为经济学思想",       "从西蒙到卡尼曼：行为经济学的兴起与影响",                       "economic-thought", 2, 25, "theory", ["行为"], False),
    ("feminist-economics",            "女性主义经济学",       "性别视角下的经济分析、无偿劳动与关怀经济",                     "economic-thought", 3, 25, "theory", ["批判"], False),
    ("ecological-economics",          "生态经济学",           "稳态经济、自然资本与经济增长的生态极限",                       "economic-thought", 3, 25, "theory", ["环境"], False),
    ("complexity-economics",          "复杂性经济学",         "经济系统的涌现、非线性动态与圣塔菲学派",                       "economic-thought", 4, 25, "theory", ["前沿"], False),
    ("chinese-economic-thought",      "中国经济思想",         "从管仲到近代：中国经济思想的演变与特色",                       "economic-thought", 2, 25, "theory", ["中国"], False),
    ("nobel-economics",               "诺贝尔经济学奖",       "重要获奖理论回顾与经济学前沿发展方向",                         "economic-thought", 2, 20, "theory", ["总览"], False),
]


def build_edges(concepts):
    """Build edges between concepts."""
    cids = {c["id"] for c in concepts}
    edges = []

    def edge(src, tgt, rel="prerequisite", st=0.8):
        if src in cids and tgt in cids:
            edges.append({
                "source_id": src,
                "target_id": tgt,
                "relation_type": rel,
                "strength": st,
            })

    # ── microeconomics ──
    edge("microeconomics-overview", "supply-demand")
    edge("supply-demand", "elasticity")
    edge("supply-demand", "consumer-theory")
    edge("consumer-theory", "utility-maximization")
    edge("microeconomics-overview", "marginal-analysis")
    edge("marginal-analysis", "consumer-theory", "related", 0.6)
    edge("microeconomics-overview", "producer-theory")
    edge("producer-theory", "cost-theory")
    edge("supply-demand", "perfect-competition")
    edge("perfect-competition", "monopoly")
    edge("perfect-competition", "monopolistic-competition")
    edge("monopoly", "oligopoly")
    edge("oligopoly", "game-theory-econ")
    edge("perfect-competition", "market-failure")
    edge("market-failure", "externalities")
    edge("market-failure", "public-goods")
    edge("market-failure", "information-asymmetry")
    edge("information-asymmetry", "contract-theory")
    edge("information-asymmetry", "auction-theory", "related", 0.5)
    edge("producer-theory", "factor-markets")
    edge("welfare-economics", "general-equilibrium")
    edge("consumer-theory", "welfare-economics", "related", 0.6)
    edge("factor-markets", "income-distribution", "related", 0.6)
    edge("game-theory-econ", "market-design", "related", 0.6)
    edge("contract-theory", "market-design", "related", 0.5)
    edge("consumer-theory", "behavioral-micro", "related", 0.5)

    # ── macroeconomics ──
    edge("macroeconomics-overview", "gdp-measurement")
    edge("gdp-measurement", "aggregate-demand-supply")
    edge("aggregate-demand-supply", "inflation")
    edge("aggregate-demand-supply", "unemployment")
    edge("macroeconomics-overview", "business-cycle")
    edge("macroeconomics-overview", "fiscal-policy")
    edge("macroeconomics-overview", "monetary-policy")
    edge("monetary-policy", "money-banking")
    edge("money-banking", "interest-rates")
    edge("interest-rates", "monetary-transmission")
    edge("fiscal-policy", "national-debt")
    edge("gdp-measurement", "economic-growth")
    edge("aggregate-demand-supply", "is-lm-model")
    edge("is-lm-model", "fiscal-policy", "related", 0.7)
    edge("is-lm-model", "monetary-policy", "related", 0.7)
    edge("inflation", "phillips-curve")
    edge("unemployment", "phillips-curve", "related", 0.7)
    edge("macroeconomics-overview", "consumption-saving")
    edge("macroeconomics-overview", "investment-theory")
    edge("is-lm-model", "exchange-rate-macro")
    edge("exchange-rate-macro", "open-economy-macro")
    edge("phillips-curve", "rational-expectations")
    edge("rational-expectations", "new-keynesian", "related", 0.6)
    edge("money-banking", "financial-crisis-macro", "related", 0.6)
    edge("unemployment", "labor-market-macro")
    edge("monetary-policy", "macroprudential-policy", "related", 0.5)
    edge("fiscal-policy", "supply-side-economics", "related", 0.5)

    # ── behavioral-econ ──
    edge("behavioral-econ-overview", "prospect-theory")
    edge("behavioral-econ-overview", "cognitive-biases-econ")
    edge("cognitive-biases-econ", "heuristics-econ")
    edge("prospect-theory", "framing-effects")
    edge("prospect-theory", "endowment-effect")
    edge("behavioral-econ-overview", "bounded-rationality")
    edge("prospect-theory", "mental-accounting")
    edge("behavioral-econ-overview", "time-inconsistency-behav")
    edge("time-inconsistency-behav", "nudge-theory")
    edge("nudge-theory", "default-effects")
    edge("cognitive-biases-econ", "overconfidence-econ")
    edge("behavioral-econ-overview", "social-preferences")
    edge("overconfidence-econ", "herding-behavior", "related", 0.5)
    edge("herding-behavior", "behavioral-finance")
    edge("prospect-theory", "behavioral-finance", "related", 0.7)
    edge("behavioral-econ-overview", "experimental-economics")
    edge("behavioral-econ-overview", "neuroeconomics", "related", 0.5)
    edge("cognitive-biases-econ", "sunk-cost-fallacy")

    # ── international-econ ──
    edge("international-econ-overview", "comparative-advantage")
    edge("international-econ-overview", "absolute-advantage")
    edge("absolute-advantage", "comparative-advantage")
    edge("comparative-advantage", "heckscher-ohlin")
    edge("comparative-advantage", "trade-policy")
    edge("trade-policy", "free-trade-agreements")
    edge("trade-policy", "trade-wars")
    edge("international-econ-overview", "exchange-rate-systems")
    edge("international-econ-overview", "balance-of-payments")
    edge("exchange-rate-systems", "foreign-exchange-market")
    edge("balance-of-payments", "international-capital-flows")
    edge("foreign-exchange-market", "currency-crisis")
    edge("international-capital-flows", "currency-crisis", "related", 0.6)
    edge("comparative-advantage", "terms-of-trade")
    edge("heckscher-ohlin", "new-trade-theory")
    edge("trade-policy", "trade-and-development")
    edge("new-trade-theory", "global-value-chains")
    edge("international-capital-flows", "multinational-corporations")
    edge("exchange-rate-systems", "international-monetary-system")
    edge("free-trade-agreements", "regional-integration")
    edge("new-trade-theory", "trade-gravity-model", "related", 0.5)
    edge("international-capital-flows", "migration-economics", "related", 0.4)
    edge("global-value-chains", "digital-trade", "related", 0.5)

    # ── development-econ ──
    edge("development-econ-overview", "poverty-inequality")
    edge("development-econ-overview", "human-development-index")
    edge("development-econ-overview", "structural-transformation")
    edge("structural-transformation", "industrialization")
    edge("structural-transformation", "agriculture-development")
    edge("poverty-inequality", "microfinance")
    edge("development-econ-overview", "foreign-aid")
    edge("development-econ-overview", "institutions-development")
    edge("institutions-development", "rct-development", "related", 0.5)
    edge("development-econ-overview", "education-economics")
    edge("development-econ-overview", "health-economics-dev")
    edge("structural-transformation", "urbanization-econ")
    edge("institutions-development", "natural-resources-curse")
    edge("development-econ-overview", "population-economics")
    edge("development-econ-overview", "sustainable-development")
    edge("industrialization", "technology-transfer")
    edge("development-econ-overview", "gender-economics")
    edge("structural-transformation", "informal-economy")
    edge("poverty-inequality", "development-finance", "related", 0.5)
    edge("foreign-aid", "development-finance", "related", 0.6)

    # ── econometrics ──
    edge("econometrics-overview", "linear-regression")
    edge("linear-regression", "multiple-regression")
    edge("linear-regression", "hypothesis-testing-econ")
    edge("multiple-regression", "endogeneity")
    edge("endogeneity", "instrumental-variables")
    edge("multiple-regression", "panel-data")
    edge("multiple-regression", "time-series-econ")
    edge("endogeneity", "diff-in-diff")
    edge("diff-in-diff", "regression-discontinuity")
    edge("endogeneity", "propensity-score")
    edge("linear-regression", "maximum-likelihood", "related", 0.5)
    edge("maximum-likelihood", "limited-dependent")
    edge("multiple-regression", "heteroskedasticity")
    edge("time-series-econ", "autocorrelation-econ")
    edge("instrumental-variables", "causal-inference", "related", 0.7)
    edge("diff-in-diff", "causal-inference", "related", 0.7)
    edge("causal-inference", "machine-learning-econ", "related", 0.5)
    edge("diff-in-diff", "synthetic-control", "related", 0.6)

    # ── public-econ ──
    edge("public-econ-overview", "taxation-principles")
    edge("taxation-principles", "tax-incidence")
    edge("tax-incidence", "optimal-taxation")
    edge("taxation-principles", "income-tax")
    edge("taxation-principles", "consumption-tax")
    edge("public-econ-overview", "public-expenditure")
    edge("public-expenditure", "social-insurance")
    edge("public-econ-overview", "public-choice")
    edge("public-choice", "rent-seeking")
    edge("public-expenditure", "cost-benefit-analysis")
    edge("public-econ-overview", "environmental-economics")
    edge("environmental-economics", "pigouvian-tax")
    edge("public-econ-overview", "fiscal-federalism")
    edge("public-choice", "government-failure")
    edge("public-econ-overview", "property-rights-econ")
    edge("property-rights-econ", "regulation-economics")
    edge("social-insurance", "welfare-state")
    edge("social-insurance", "pension-economics")
    edge("nudge-theory", "behavioral-public-policy", "related", 0.7)
    edge("public-expenditure", "education-policy-econ")
    edge("public-expenditure", "healthcare-economics")
    edge("regulation-economics", "healthcare-economics", "related", 0.5)

    # ── economic-thought ──
    edge("economic-thought-overview", "adam-smith")
    edge("adam-smith", "david-ricardo")
    edge("david-ricardo", "karl-marx-econ")
    edge("adam-smith", "marginalism")
    edge("marginalism", "alfred-marshall")
    edge("alfred-marshall", "neoclassical-synthesis")
    edge("karl-marx-econ", "keynesian-revolution", "related", 0.4)
    edge("alfred-marshall", "keynesian-revolution")
    edge("keynesian-revolution", "monetarism")
    edge("economic-thought-overview", "austrian-school")
    edge("keynesian-revolution", "neoclassical-synthesis")
    edge("monetarism", "chicago-school")
    edge("economic-thought-overview", "institutional-economics")
    edge("institutional-economics", "new-institutional")
    edge("adam-smith", "development-thought", "related", 0.4)
    edge("economic-thought-overview", "behavioral-thought")
    edge("economic-thought-overview", "feminist-economics")
    edge("economic-thought-overview", "ecological-economics")
    edge("economic-thought-overview", "complexity-economics")
    edge("economic-thought-overview", "chinese-economic-thought")
    edge("economic-thought-overview", "nobel-economics", "related", 0.5)

    # ── cross-subdomain edges ──
    edge("supply-demand", "aggregate-demand-supply", "related", 0.5)
    edge("market-failure", "fiscal-policy", "related", 0.5)
    edge("externalities", "environmental-economics", "related", 0.7)
    edge("externalities", "pigouvian-tax", "related", 0.7)
    edge("public-goods", "public-expenditure", "related", 0.6)
    edge("game-theory-econ", "oligopoly", "related", 0.6)
    edge("behavioral-econ-overview", "behavioral-micro", "related", 0.7)
    edge("behavioral-thought", "behavioral-econ-overview", "influences", 0.6)
    edge("ecological-economics", "sustainable-development", "related", 0.6)
    edge("comparative-advantage", "trade-and-development", "related", 0.6)
    edge("economic-growth", "development-econ-overview", "related", 0.6)
    edge("adam-smith", "microeconomics-overview", "influences", 0.5)
    edge("keynesian-revolution", "macroeconomics-overview", "influences", 0.7)
    edge("monetarism", "monetary-policy", "influences", 0.6)
    edge("rct-development", "experimental-economics", "related", 0.7)
    edge("instrumental-variables", "endogeneity", "related", 0.6)
    edge("information-asymmetry", "healthcare-economics", "related", 0.5)
    edge("institutions-development", "new-institutional", "related", 0.7)
    edge("welfare-economics", "public-econ-overview", "related", 0.5)
    edge("income-distribution", "poverty-inequality", "related", 0.7)
    edge("inflation", "monetary-policy", "related", 0.7)
    edge("exchange-rate-macro", "exchange-rate-systems", "related", 0.7)
    edge("fiscal-policy", "public-expenditure", "related", 0.6)
    edge("fiscal-policy", "taxation-principles", "related", 0.6)
    edge("bounded-rationality", "behavioral-thought", "related", 0.6)

    return edges


def main():
    concepts = []
    for (cid, name, desc, sub, diff, mins, ctype, tags, ms) in CONCEPTS_RAW:
        concepts.append({
            "id": cid,
            "name": name,
            "description": desc,
            "subdomain_id": sub,
            "domain_id": "economics",
            "difficulty": diff,
            "estimated_minutes": mins,
            "content_type": ctype,
            "tags": tags,
            "is_milestone": ms,
        })

    edges = build_edges(concepts)

    # Verify no dangling edge references
    cids = {c["id"] for c in concepts}
    for e in edges:
        assert e["source_id"] in cids, f"Missing source: {e['source_id']}"
        assert e["target_id"] in cids, f"Missing target: {e['target_id']}"

    # Verify no duplicate concept IDs
    assert len(cids) == len(concepts), "Duplicate concept IDs detected"

    # Count milestones
    milestones = [c for c in concepts if c["is_milestone"]]

    graph = {
        "domain": DOMAIN,
        "subdomains": SUBDOMAINS,
        "concepts": concepts,
        "edges": edges,
        "meta": {
            "version": "1.0.0",
            "created_at": NOW,
            "stats": {
                "total_concepts": len(concepts),
                "total_edges": len(edges),
                "total_subdomains": len(SUBDOMAINS),
                "total_milestones": len(milestones),
            },
        },
    }

    out = json.dumps(graph, ensure_ascii=False, indent=2)
    with open("seed_graph.json", "w", encoding="utf-8") as f:
        f.write(out)

    print(f"✅ Generated economics seed graph:")
    print(f"   Concepts: {len(concepts)}")
    print(f"   Edges:    {len(edges)}")
    print(f"   Milestones: {len(milestones)}")
    print(f"   Subdomains: {len(SUBDOMAINS)}")
    for sub in SUBDOMAINS:
        count = sum(1 for c in concepts if c["subdomain_id"] == sub["id"])
        ms_count = sum(1 for c in concepts if c["subdomain_id"] == sub["id"] and c["is_milestone"])
        print(f"     {sub['id']}: {count} concepts ({ms_count} milestones)")


if __name__ == "__main__":
    main()
