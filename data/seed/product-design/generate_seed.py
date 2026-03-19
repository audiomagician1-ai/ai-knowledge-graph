#!/usr/bin/env python3
"""Generate Product Design knowledge sphere seed graph.

8 subdomains, ~180 concepts covering user research to growth operations.
"""
import json
from datetime import datetime, timezone

NOW = datetime.now(timezone.utc).isoformat()

DOMAIN = {
    "id": "product-design",
    "name": "产品设计",
    "description": "从用户研究到增长运营的产品设计知识体系",
    "icon": "🔴",
    "color": "#ef4444",
}

SUBDOMAINS = [
    {"id": "user-research",       "name": "用户研究",     "order": 1},
    {"id": "product-thinking",    "name": "产品思维",     "order": 2},
    {"id": "interaction-design",  "name": "交互设计",     "order": 3},
    {"id": "visual-design",       "name": "视觉设计",     "order": 4},
    {"id": "prototyping",         "name": "原型与测试",   "order": 5},
    {"id": "data-driven",         "name": "数据驱动",     "order": 6},
    {"id": "product-management",  "name": "产品管理",     "order": 7},
    {"id": "growth",              "name": "增长运营",     "order": 8},
]

# (id, name, description, subdomain_id, difficulty, minutes, content_type, tags, is_milestone)
CONCEPTS_RAW = [
    # ── user-research (24 concepts) ──
    ("user-research-overview",     "用户研究概述",       "用户研究的定义、价值与方法论框架",                 "user-research", 1, 20, "theory", ["基础"], True),
    ("user-interview",             "用户访谈",           "一对一深度访谈的设计、执行与分析",                 "user-research", 2, 30, "practice", ["定性"], False),
    ("contextual-inquiry",         "情境调查",           "在用户真实使用环境中观察与访谈",                   "user-research", 2, 25, "practice", ["定性"], False),
    ("survey-design",              "问卷设计",           "量化问卷的题目设计、量表选择与分发策略",           "user-research", 2, 30, "practice", ["定量"], False),
    ("user-persona",               "用户画像",           "基于研究数据构建代表性用户角色模型",               "user-research", 2, 25, "practice", ["建模"], True),
    ("empathy-map",                "同理心地图",         "可视化用户所想、所说、所做、所感",                 "user-research", 2, 20, "practice", ["工具"], False),
    ("journey-map",                "用户旅程图",         "端到端用户体验旅程的可视化与分析",                 "user-research", 3, 35, "practice", ["工具"], True),
    ("jobs-to-be-done",            "待完成工作理论",     "JTBD框架：用户雇佣产品完成特定工作",               "user-research", 3, 30, "theory", ["框架"], False),
    ("usability-testing",          "可用性测试",         "任务导向的产品易用性评估方法",                     "user-research", 3, 35, "practice", ["测试"], True),
    ("card-sorting",               "卡片分类法",         "信息架构验证的用户参与式分类方法",                 "user-research", 2, 20, "practice", ["IA"], False),
    ("diary-study",                "日记研究法",         "用户在自然环境中长期记录使用体验",                 "user-research", 3, 25, "practice", ["定性"], False),
    ("focus-group",                "焦点小组",           "小组讨论式定性研究方法",                           "user-research", 2, 25, "practice", ["定性"], False),
    ("competitive-analysis",       "竞品分析",           "系统性分析竞争对手的产品策略与功能",               "user-research", 2, 30, "practice", ["分析"], False),
    ("heuristic-evaluation",       "启发式评估",         "基于可用性原则的专家评审方法",                     "user-research", 3, 25, "practice", ["评估"], False),
    ("eye-tracking",               "眼动追踪",           "通过眼动数据分析用户视觉注意力分布",               "user-research", 4, 30, "theory", ["量化"], False),
    ("think-aloud-protocol",       "出声思考法",         "用户操作时口述思维过程的观察方法",                 "user-research", 2, 20, "practice", ["定性"], False),
    ("ethnographic-research",      "民族志研究",         "深入用户生活环境的长期沉浸式研究",                 "user-research", 4, 35, "theory", ["定性"], False),
    ("quantitative-ux-metrics",    "UX量化指标",         "SUS、NPS、CSAT等标准化用户体验度量",               "user-research", 3, 30, "theory", ["量化"], False),
    ("research-synthesis",         "研究综合分析",       "多来源研究数据的整合与洞察提炼",                   "user-research", 3, 30, "practice", ["分析"], False),
    ("affinity-diagram",           "亲和图法",           "将零散数据归类整理发现模式的方法",                 "user-research", 2, 20, "practice", ["工具"], False),
    ("accessibility-research",     "无障碍研究",         "面向残障用户群体的研究方法与标准",                 "user-research", 3, 25, "theory", ["包容性"], False),
    ("research-ethics",            "研究伦理",           "知情同意、隐私保护与研究偏见控制",                 "user-research", 2, 20, "theory", ["伦理"], False),
    ("stakeholder-interview",      "利益相关者访谈",     "与业务方/技术方的需求对齐访谈",                    "user-research", 2, 25, "practice", ["商业"], False),
    ("research-planning",          "研究计划制定",       "研究目标、方法选择与时间预算规划",                 "user-research", 2, 25, "practice", ["规划"], False),

    # ── product-thinking (24 concepts) ──
    ("product-thinking-overview",  "产品思维概述",       "产品经理的核心思维模式与决策框架",                 "product-thinking", 1, 20, "theory", ["基础"], True),
    ("design-thinking",            "设计思维",           "以人为本的创新方法论：共情→定义→构思→原型→测试",   "product-thinking", 2, 30, "theory", ["方法论"], True),
    ("lean-startup",               "精益创业",           "MVP→构建→测量→学习循环的快速验证方法",             "product-thinking", 2, 30, "theory", ["方法论"], False),
    ("product-market-fit",         "产品市场契合",       "PMF的定义、衡量标准与实现路径",                    "product-thinking", 3, 35, "theory", ["战略"], True),
    ("value-proposition",          "价值主张",           "产品为目标用户解决的核心问题与独特价值",           "product-thinking", 2, 25, "theory", ["战略"], False),
    ("business-model-canvas",      "商业模式画布",       "9大要素的商业模式可视化分析工具",                  "product-thinking", 3, 30, "practice", ["工具"], False),
    ("product-vision",             "产品愿景",           "长期方向的定义与团队对齐",                         "product-thinking", 2, 25, "theory", ["战略"], False),
    ("product-strategy",           "产品策略",           "目标市场、差异化与竞争优势规划",                   "product-thinking", 3, 35, "theory", ["战略"], False),
    ("mvp-design",                 "MVP设计",            "最小可行产品的范围界定与快速验证",                 "product-thinking", 2, 30, "practice", ["方法论"], False),
    ("user-story-mapping",         "用户故事地图",       "从用户活动到功能优先级的可视化规划",               "product-thinking", 2, 25, "practice", ["工具"], False),
    ("prioritization-frameworks",  "优先级排序框架",     "RICE、MoSCoW、Kano模型等排序方法",                 "product-thinking", 3, 30, "practice", ["工具"], False),
    ("product-lifecycle",          "产品生命周期",       "引入期→成长期→成熟期→衰退期的管理策略",           "product-thinking", 2, 25, "theory", ["战略"], False),
    ("platform-thinking",          "平台思维",           "双边市场、网络效应与平台战略设计",                 "product-thinking", 4, 35, "theory", ["高级"], False),
    ("systems-thinking",           "系统思维",           "理解产品作为复杂系统的整体关联与反馈循环",         "product-thinking", 3, 30, "theory", ["思维"], False),
    ("first-principles",           "第一性原理",         "从基本事实出发推导产品决策的思维方式",             "product-thinking", 3, 25, "theory", ["思维"], False),
    ("opportunity-assessment",     "机会评估",           "市场规模、技术可行性与商业价值的综合判断",         "product-thinking", 3, 30, "practice", ["分析"], False),
    ("product-positioning",        "产品定位",           "目标用户心智中的差异化位置确立",                   "product-thinking", 3, 25, "theory", ["战略"], False),
    ("behavioral-economics",       "行为经济学",         "非理性决策、锚定效应等行为理论在产品中的应用",     "product-thinking", 4, 35, "theory", ["高级"], False),
    ("ecosystem-design",           "生态系统设计",       "产品与周边产品/服务的协同价值设计",                "product-thinking", 4, 30, "theory", ["高级"], False),
    ("innovation-types",           "创新类型",           "渐进式创新vs颠覆式创新的策略选择",                 "product-thinking", 3, 25, "theory", ["战略"], False),
    ("blue-ocean-strategy",        "蓝海战略",           "创造无竞争新市场空间的策略方法",                   "product-thinking", 3, 30, "theory", ["战略"], False),
    ("hypothesis-driven-dev",      "假设驱动开发",       "将产品决策转化为可验证假设的方法",                 "product-thinking", 2, 25, "practice", ["方法论"], False),
    ("user-centered-design",       "以用户为中心的设计", "UCD流程：理解用户→设计方案→评估→迭代",             "product-thinking", 2, 25, "theory", ["方法论"], False),
    ("product-ethics",             "产品伦理",           "暗黑模式、成瘾性设计等伦理问题与设计原则",         "product-thinking", 3, 25, "theory", ["伦理"], False),

    # ── interaction-design (24 concepts) ──
    ("interaction-design-overview", "交互设计概述",      "交互设计的原则、流程与核心概念",                   "interaction-design", 1, 20, "theory", ["基础"], True),
    ("information-architecture",   "信息架构",           "内容组织、导航结构与标签系统设计",                 "interaction-design", 2, 30, "theory", ["IA"], True),
    ("navigation-design",          "导航设计",           "全局导航、局部导航与面包屑的设计模式",             "interaction-design", 2, 25, "practice", ["模式"], False),
    ("form-design",                "表单设计",           "输入控件选择、验证反馈与表单流程优化",             "interaction-design", 2, 30, "practice", ["模式"], False),
    ("micro-interaction",          "微交互设计",         "触发器→规则→反馈→循环的细节交互设计",              "interaction-design", 3, 25, "practice", ["动效"], False),
    ("responsive-design",          "响应式设计",         "跨设备适配的布局策略与断点设计",                   "interaction-design", 2, 30, "practice", ["布局"], False),
    ("mobile-design-patterns",     "移动端设计模式",     "手势交互、底部导航、下拉刷新等移动特有模式",       "interaction-design", 3, 30, "practice", ["移动"], False),
    ("design-system",              "设计系统",           "组件库、设计令牌与设计规范的构建与维护",           "interaction-design", 4, 40, "practice", ["系统"], True),
    ("gestalt-principles",         "格式塔原则",         "接近、相似、闭合、连续等视知觉组织原则",           "interaction-design", 2, 25, "theory", ["心理学"], False),
    ("fitts-law",                  "费茨定律",           "目标大小与距离对操作时间的影响定律",               "interaction-design", 3, 20, "theory", ["心理学"], False),
    ("hicks-law",                  "希克定律",           "选项数量与决策时间的对数关系",                     "interaction-design", 3, 20, "theory", ["心理学"], False),
    ("progressive-disclosure",     "渐进式披露",         "按需展示信息降低认知负荷的设计策略",               "interaction-design", 2, 20, "theory", ["原则"], False),
    ("error-handling-ux",          "错误处理设计",       "错误预防、错误提示与恢复路径设计",                 "interaction-design", 2, 25, "practice", ["模式"], False),
    ("onboarding-design",          "新手引导设计",       "首次使用体验、教程与空状态设计",                   "interaction-design", 3, 30, "practice", ["模式"], False),
    ("search-design",              "搜索设计",           "搜索框、自动补全、筛选与结果呈现",                 "interaction-design", 3, 25, "practice", ["模式"], False),
    ("notification-design",        "通知设计",           "推送、应用内与邮件通知的策略与节奏",               "interaction-design", 3, 25, "practice", ["模式"], False),
    ("empty-state-design",         "空状态设计",         "无内容状态的引导性与情感化设计",                   "interaction-design", 2, 15, "practice", ["模式"], False),
    ("dark-mode-design",           "深色模式设计",       "深色主题的色彩策略与可读性保障",                   "interaction-design", 2, 20, "practice", ["主题"], False),
    ("animation-principles",       "动效设计原则",       "缓动曲线、时长与迪士尼动画12原则在UI中的应用",     "interaction-design", 3, 30, "theory", ["动效"], False),
    ("accessibility-design",       "无障碍设计",         "WCAG标准、屏幕阅读器适配与色彩对比度",             "interaction-design", 3, 30, "theory", ["包容性"], False),
    ("multi-platform-design",      "多平台设计",         "桌面/移动/平板/手表的跨平台一致性策略",            "interaction-design", 3, 25, "practice", ["跨平台"], False),
    ("voice-ui-design",            "语音界面设计",       "对话式交互、语音指令与多模态界面",                 "interaction-design", 4, 30, "theory", ["新兴"], False),
    ("gamification",               "游戏化设计",         "积分、徽章、排行榜与进度系统的激励设计",           "interaction-design", 3, 25, "practice", ["激励"], False),
    ("content-strategy",           "内容策略",           "UX文案、语气风格与内容治理",                       "interaction-design", 3, 25, "practice", ["内容"], False),

    # ── visual-design (22 concepts) ──
    ("visual-design-overview",     "视觉设计概述",       "视觉设计的基本原则与在产品中的作用",               "visual-design", 1, 20, "theory", ["基础"], True),
    ("color-theory",               "色彩理论",           "色轮、色彩心理学与产品配色方案",                   "visual-design", 2, 30, "theory", ["基础"], True),
    ("typography",                 "字体排印学",         "字体选择、字号层级、行距与可读性",                 "visual-design", 2, 30, "theory", ["基础"], False),
    ("layout-grid",                "布局与栅格",         "栅格系统、间距规范与视觉节奏",                     "visual-design", 2, 25, "practice", ["布局"], False),
    ("iconography",                "图标设计",           "图标风格、尺寸规范与语义一致性",                   "visual-design", 2, 25, "practice", ["元素"], False),
    ("illustration-design",        "插画设计",           "产品插画的风格定义与应用场景",                     "visual-design", 3, 30, "practice", ["元素"], False),
    ("visual-hierarchy",           "视觉层级",           "大小、颜色、对比度与留白建立信息层次",             "visual-design", 2, 25, "theory", ["原则"], False),
    ("brand-design",               "品牌设计",           "品牌标识、调性定义与视觉一致性",                   "visual-design", 3, 35, "practice", ["品牌"], True),
    ("design-token",               "设计令牌",           "颜色/字体/间距的变量化与跨平台同步",               "visual-design", 3, 25, "practice", ["系统"], False),
    ("data-visualization",         "数据可视化",         "图表类型选择、数据墨水比与交互式可视化",           "visual-design", 3, 35, "practice", ["数据"], False),
    ("emotional-design",           "情感化设计",         "Norman三层模型：本能层→行为层→反思层",              "visual-design", 3, 25, "theory", ["心理学"], False),
    ("material-design",            "Material Design",    "Google的设计语言：表面、运动与交互规范",           "visual-design", 2, 25, "theory", ["规范"], False),
    ("ios-human-interface",        "iOS Human Interface", "Apple的HIG设计规范与平台特性",                    "visual-design", 2, 25, "theory", ["规范"], False),
    ("whitespace-design",          "留白设计",           "负空间的运用与呼吸感创造",                         "visual-design", 2, 20, "theory", ["原则"], False),
    ("contrast-design",            "对比设计",           "色彩对比、尺寸对比与风格对比的运用",               "visual-design", 2, 20, "theory", ["原则"], False),
    ("design-consistency",         "设计一致性",         "内部一致性、外部一致性与实际一致性原则",           "visual-design", 2, 20, "theory", ["原则"], False),
    ("responsive-imagery",         "响应式图片",         "不同分辨率与设备的图片适配策略",                   "visual-design", 2, 20, "practice", ["技术"], False),
    ("dark-light-theme",           "明暗主题设计",       "双主题的色彩方案与自动切换策略",                   "visual-design", 3, 25, "practice", ["主题"], False),
    ("3d-in-ui",                   "3D与UI融合",         "3D元素在扁平UI中的应用与性能考量",                 "visual-design", 4, 30, "theory", ["新兴"], False),
    ("motion-design",              "运动设计",           "UI动效的时间线编排与品牌运动语言",                 "visual-design", 3, 30, "practice", ["动效"], False),
    ("skeuomorphism-vs-flat",      "拟物与扁平",         "设计风格的演变：拟物→扁平→新拟态",                 "visual-design", 2, 20, "theory", ["历史"], False),
    ("design-handoff",             "设计交付",           "标注、切图与开发协作规范",                         "visual-design", 2, 25, "practice", ["协作"], False),

    # ── prototyping (20 concepts) ──
    ("prototyping-overview",       "原型设计概述",       "从纸面原型到高保真原型的方法谱",                   "prototyping", 1, 20, "theory", ["基础"], True),
    ("wireframe",                  "线框图",             "低保真页面结构与布局的快速表达",                   "prototyping", 1, 20, "practice", ["低保真"], False),
    ("low-fi-prototype",           "低保真原型",         "纸面原型与快速草图的验证方法",                     "prototyping", 1, 15, "practice", ["低保真"], False),
    ("high-fi-prototype",          "高保真原型",         "接近最终产品的交互式可点击原型",                   "prototyping", 3, 30, "practice", ["高保真"], True),
    ("figma-basics",               "Figma基础",          "Figma的组件、自动布局与原型连线",                  "prototyping", 2, 35, "practice", ["工具"], False),
    ("figma-advanced",             "Figma高级",          "变体、设计系统与团队协作工作流",                   "prototyping", 3, 30, "practice", ["工具"], False),
    ("sketch-to-code",             "设计到代码",         "设计稿转前端代码的工具与流程",                     "prototyping", 3, 25, "practice", ["工程"], False),
    ("interactive-prototype",      "交互原型",           "微交互、页面跳转与状态切换的原型制作",             "prototyping", 3, 30, "practice", ["高保真"], False),
    ("prototype-testing",          "原型测试",           "基于原型的用户测试设计与执行",                     "prototyping", 3, 30, "practice", ["测试"], True),
    ("rapid-prototyping",          "快速原型",           "快速迭代验证产品概念的技术与方法",                 "prototyping", 2, 25, "practice", ["方法论"], False),
    ("component-library",          "组件库建设",         "可复用UI组件的设计、文档与版本管理",               "prototyping", 3, 35, "practice", ["系统"], False),
    ("design-spec",                "设计规格说明",       "标注文档、交互说明与验收标准",                     "prototyping", 2, 25, "practice", ["协作"], False),
    ("storyboard",                 "故事板",             "用户使用场景的叙事性视觉化表达",                   "prototyping", 2, 20, "practice", ["工具"], False),
    ("wizard-of-oz",               "绿野仙踪法",        "人工模拟系统行为的概念验证方法",                   "prototyping", 3, 25, "practice", ["测试"], False),
    ("concept-testing",            "概念测试",           "产品概念阶段的用户接受度验证",                     "prototyping", 2, 25, "practice", ["测试"], False),
    ("design-critique",            "设计评审",           "结构化的设计方案评审与反馈方法",                   "prototyping", 2, 20, "practice", ["协作"], False),
    ("design-iteration",           "设计迭代",           "基于反馈的快速改进循环",                           "prototyping", 2, 20, "theory", ["方法论"], False),
    ("ab-testing-design",          "A/B测试设计",        "对照实验的变量控制与统计显著性",                   "prototyping", 3, 30, "practice", ["测试"], False),
    ("multivariate-testing",       "多变量测试",         "多因素同时测试的实验设计方法",                     "prototyping", 4, 30, "theory", ["高级"], False),
    ("design-review-checklist",    "设计走查清单",       "交付前的系统性设计质量检查",                       "prototyping", 2, 20, "practice", ["质量"], False),

    # ── data-driven (22 concepts) ──
    ("data-driven-overview",       "数据驱动概述",       "数据在产品决策中的角色与方法论",                   "data-driven", 1, 20, "theory", ["基础"], True),
    ("product-metrics",            "产品核心指标",       "北极星指标、AARRR海盗指标与指标体系",             "data-driven", 2, 30, "theory", ["指标"], True),
    ("funnel-analysis",            "漏斗分析",           "转化漏斗的构建、诊断与优化",                       "data-driven", 2, 30, "practice", ["分析"], False),
    ("cohort-analysis",            "群组分析",           "按用户群组追踪行为变化的分析方法",                 "data-driven", 3, 30, "practice", ["分析"], False),
    ("retention-analysis",         "留存分析",           "次日/7日/30日留存的计算与改善策略",                "data-driven", 3, 30, "practice", ["分析"], True),
    ("ab-testing-analysis",        "A/B测试分析",        "假设检验、样本量计算与显著性判断",                 "data-driven", 3, 35, "practice", ["实验"], False),
    ("event-tracking",             "埋点设计",           "行为事件定义、参数规划与数据采集方案",             "data-driven", 2, 30, "practice", ["采集"], False),
    ("user-segmentation",          "用户分群",           "基于行为/属性/价值的用户群体划分",                 "data-driven", 3, 25, "practice", ["分析"], False),
    ("analytics-tools",            "分析工具",           "GA4、Mixpanel、Amplitude等产品分析工具",            "data-driven", 2, 25, "practice", ["工具"], False),
    ("sql-for-pm",                 "产品经理SQL",        "产品分析常用SQL查询与数据提取",                    "data-driven", 3, 30, "practice", ["技能"], False),
    ("data-storytelling",          "数据叙事",           "用数据讲故事的方法与可视化呈现",                   "data-driven", 3, 25, "practice", ["沟通"], False),
    ("attribution-model",          "归因模型",           "首次/末次/线性/时间衰减等归因方法",               "data-driven", 4, 30, "theory", ["高级"], False),
    ("predictive-analytics",       "预测分析",           "用户行为预测与流失预警模型",                       "data-driven", 4, 35, "theory", ["高级"], False),
    ("data-privacy-compliance",    "数据隐私合规",       "GDPR、CCPA与用户数据保护实践",                     "data-driven", 3, 25, "theory", ["合规"], False),
    ("dashboard-design",           "数据看板设计",       "业务看板的指标选择、布局与刷新策略",               "data-driven", 3, 30, "practice", ["可视化"], False),
    ("experiment-design",          "实验设计方法",       "对照组、自变量、因变量与外部效度",                 "data-driven", 3, 30, "theory", ["实验"], False),
    ("statistical-significance",   "统计显著性",         "p值、置信区间与统计功效",                          "data-driven", 4, 30, "theory", ["统计"], False),
    ("behavioral-analytics",       "行为分析",           "用户行为序列、路径分析与热图",                     "data-driven", 3, 25, "practice", ["分析"], False),
    ("ltv-calculation",            "LTV计算",            "用户生命周期价值的估算方法",                       "data-driven", 3, 25, "practice", ["指标"], False),
    ("churn-analysis",             "流失分析",           "用户流失的定义、原因诊断与挽回策略",               "data-driven", 3, 30, "practice", ["分析"], False),
    ("feature-flag",               "功能开关",           "灰度发布、功能开关与渐进式上线",                   "data-driven", 3, 25, "practice", ["工程"], False),
    ("data-quality",               "数据质量治理",       "数据清洗、口径统一与数据治理流程",                 "data-driven", 3, 25, "practice", ["治理"], False),

    # ── product-management (24 concepts) ──
    ("product-management-overview", "产品管理概述",      "产品经理的角色、职责与核心能力模型",               "product-management", 1, 20, "theory", ["基础"], True),
    ("product-roadmap",            "产品路线图",         "OKR驱动的路线图制定与沟通",                        "product-management", 2, 30, "practice", ["规划"], True),
    ("prd-writing",                "PRD编写",            "产品需求文档的结构、内容与维护",                   "product-management", 2, 35, "practice", ["文档"], False),
    ("sprint-planning",            "Sprint规划",         "敏捷迭代的范围、估算与承诺",                       "product-management", 2, 25, "practice", ["敏捷"], False),
    ("scrum-framework",            "Scrum框架",          "角色、仪式与工件的完整Scrum实践",                  "product-management", 2, 30, "theory", ["敏捷"], False),
    ("kanban-method",              "看板方法",           "可视化工作流、WIP限制与持续交付",                  "product-management", 2, 25, "practice", ["敏捷"], False),
    ("stakeholder-management",     "利益相关者管理",     "利益相关者地图与影响力-利益矩阵",                  "product-management", 3, 25, "practice", ["沟通"], False),
    ("cross-functional-collab",    "跨职能协作",         "与开发、设计、市场的协作模式与冲突处理",           "product-management", 3, 25, "practice", ["协作"], False),
    ("backlog-management",         "需求池管理",         "需求收集、评审、优先级排序与版本规划",             "product-management", 2, 25, "practice", ["管理"], False),
    ("release-management",         "发布管理",           "发布计划、灰度策略与回滚机制",                     "product-management", 3, 25, "practice", ["工程"], False),
    ("okr-method",                 "OKR方法",            "目标与关键结果的设定、追踪与复盘",                 "product-management", 2, 25, "practice", ["目标"], False),
    ("technical-debt",             "技术债务管理",       "技术债识别、量化与偿还策略",                       "product-management", 3, 25, "theory", ["工程"], False),
    ("product-launch",             "产品发布策略",       "Go-to-Market策略、发布清单与影响力放大",            "product-management", 3, 30, "practice", ["发布"], True),
    ("feedback-loop",              "反馈循环",           "用户反馈收集、分类与闭环处理",                     "product-management", 2, 25, "practice", ["运营"], False),
    ("competitive-moat",           "竞争壁垒",           "网络效应、数据壁垒、品牌与规模效应",               "product-management", 4, 30, "theory", ["战略"], False),
    ("product-analytics-review",   "产品数据复盘",       "周/月度数据review的方法与行动计划",                "product-management", 3, 25, "practice", ["数据"], False),
    ("team-building",              "产品团队建设",       "产品团队的组成、能力模型与文化建设",               "product-management", 3, 25, "theory", ["管理"], False),
    ("remote-collaboration",       "远程协作",           "分布式团队的工具、流程与文化",                     "product-management", 2, 20, "practice", ["协作"], False),
    ("product-doc-system",         "产品文档体系",       "需求文档、设计文档、技术文档的组织与维护",         "product-management", 2, 25, "practice", ["文档"], False),
    ("estimation-techniques",      "工作量估算",         "故事点、T-shirt Sizing与三点估算法",               "product-management", 2, 25, "practice", ["敏捷"], False),
    ("retrospective",              "迭代回顾",           "回顾会议的组织方法与持续改进",                     "product-management", 2, 20, "practice", ["敏捷"], False),
    ("feature-specification",      "功能规格说明",       "从用户故事到详细功能规格的转化",                   "product-management", 2, 25, "practice", ["文档"], False),
    ("product-communication",      "产品沟通技巧",       "向上汇报、跨部门对齐与用户沟通",                  "product-management", 3, 25, "practice", ["沟通"], False),
    ("product-metrics-review",     "指标异动排查",       "数据波动的根因分析与应对方案",                     "product-management", 3, 30, "practice", ["数据"], False),

    # ── growth (22 concepts) ──
    ("growth-overview",            "增长概述",           "增长黑客思维、增长模型与增长团队",                 "growth", 1, 20, "theory", ["基础"], True),
    ("aarrr-model",                "AARRR漏斗模型",      "获客→激活→留存→变现→推荐的增长框架",               "growth", 2, 30, "theory", ["框架"], True),
    ("growth-hacking",             "增长黑客",           "低成本高效率的增长实验与策略",                     "growth", 3, 30, "practice", ["策略"], False),
    ("viral-loop",                 "病毒循环",           "邀请机制、社交分享与K系数优化",                    "growth", 3, 30, "practice", ["获客"], False),
    ("user-activation",            "用户激活",           "Aha Moment识别与新用户激活优化",                   "growth", 3, 30, "practice", ["激活"], True),
    ("retention-strategy",         "留存策略",           "功能留存、内容留存与习惯养成",                     "growth", 3, 35, "practice", ["留存"], False),
    ("monetization-strategy",      "变现策略",           "订阅/广告/增值服务/交易抽成的变现模型",           "growth", 3, 30, "theory", ["变现"], False),
    ("pricing-strategy",           "定价策略",           "价值定价、竞争定价与心理定价方法",                 "growth", 3, 30, "theory", ["变现"], False),
    ("content-marketing",          "内容营销",           "SEO、博客、社交媒体内容策略",                      "growth", 2, 25, "practice", ["获客"], False),
    ("seo-basics",                 "SEO基础",            "搜索引擎优化的技术与内容策略",                     "growth", 2, 30, "practice", ["获客"], False),
    ("push-notification-strategy", "推送策略",           "推送时机、频率与个性化策略",                       "growth", 3, 25, "practice", ["留存"], False),
    ("email-marketing",            "邮件营销",           "邮件序列、个性化与打开率优化",                     "growth", 2, 25, "practice", ["获客"], False),
    ("referral-program",           "推荐计划",           "双边激励的推荐系统设计",                           "growth", 3, 25, "practice", ["获客"], False),
    ("onboarding-optimization",    "新手引导优化",       "首次体验流程的转化率优化",                         "growth", 3, 30, "practice", ["激活"], False),
    ("growth-experiment",          "增长实验",           "实验假设→设计→执行→分析的完整流程",                "growth", 3, 30, "practice", ["实验"], False),
    ("user-lifecycle",             "用户生命周期管理",   "新用户→活跃→衰退→流失→召回的全周期运营",          "growth", 3, 30, "theory", ["运营"], False),
    ("community-building",         "社区建设",           "用户社区的搭建、运营与活跃度提升",                 "growth", 3, 25, "practice", ["运营"], False),
    ("paywall-design",             "付费墙设计",         "免费/付费边界与转化触发点设计",                    "growth", 3, 25, "practice", ["变现"], False),
    ("freemium-model",             "免费增值模式",       "免费版与付费版的功能拆分策略",                     "growth", 3, 25, "theory", ["模式"], False),
    ("network-effects",            "网络效应",           "直接/间接网络效应与临界质量",                      "growth", 4, 30, "theory", ["高级"], False),
    ("growth-loops",               "增长飞轮",           "自强化增长循环的设计与加速",                       "growth", 4, 30, "theory", ["高级"], False),
    ("marketplace-growth",         "双边市场增长",       "供给侧与需求侧的冷启动与平衡增长",                "growth", 4, 35, "theory", ["高级"], False),
]

def build_concepts():
    concepts = []
    for (cid, name, desc, sub, diff, mins, ctype, tags, ms) in CONCEPTS_RAW:
        concepts.append({
            "id": cid,
            "name": name,
            "description": desc,
            "domain_id": "product-design",
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
    # ── user-research internal ──
    ("user-research-overview", "user-interview", "prerequisite", 0.9),
    ("user-research-overview", "survey-design", "prerequisite", 0.9),
    ("user-research-overview", "research-planning", "prerequisite", 0.9),
    ("user-research-overview", "research-ethics", "prerequisite", 0.8),
    ("user-interview", "contextual-inquiry", "prerequisite", 0.8),
    ("user-interview", "think-aloud-protocol", "related", 0.7),
    ("user-interview", "focus-group", "related", 0.7),
    ("user-interview", "stakeholder-interview", "related", 0.7),
    ("survey-design", "quantitative-ux-metrics", "prerequisite", 0.8),
    ("user-interview", "user-persona", "prerequisite", 0.9),
    ("survey-design", "user-persona", "prerequisite", 0.8),
    ("user-persona", "empathy-map", "related", 0.8),
    ("user-persona", "journey-map", "prerequisite", 0.9),
    ("empathy-map", "journey-map", "related", 0.7),
    ("journey-map", "usability-testing", "prerequisite", 0.8),
    ("user-interview", "jobs-to-be-done", "prerequisite", 0.8),
    ("usability-testing", "heuristic-evaluation", "related", 0.7),
    ("usability-testing", "think-aloud-protocol", "related", 0.8),
    ("card-sorting", "information-architecture", "prerequisite", 0.8),
    ("diary-study", "ethnographic-research", "prerequisite", 0.7),
    ("contextual-inquiry", "ethnographic-research", "prerequisite", 0.8),
    ("quantitative-ux-metrics", "eye-tracking", "related", 0.6),
    ("research-planning", "research-synthesis", "prerequisite", 0.8),
    ("focus-group", "research-synthesis", "related", 0.7),
    ("research-synthesis", "affinity-diagram", "related", 0.8),
    ("usability-testing", "accessibility-research", "related", 0.7),
    ("competitive-analysis", "product-positioning", "prerequisite", 0.8),

    # ── product-thinking internal ──
    ("product-thinking-overview", "design-thinking", "prerequisite", 0.9),
    ("product-thinking-overview", "user-centered-design", "prerequisite", 0.9),
    ("product-thinking-overview", "first-principles", "prerequisite", 0.8),
    ("design-thinking", "lean-startup", "related", 0.8),
    ("lean-startup", "mvp-design", "prerequisite", 0.9),
    ("lean-startup", "hypothesis-driven-dev", "prerequisite", 0.8),
    ("mvp-design", "product-market-fit", "prerequisite", 0.9),
    ("value-proposition", "product-market-fit", "prerequisite", 0.8),
    ("value-proposition", "product-positioning", "related", 0.8),
    ("product-vision", "product-strategy", "prerequisite", 0.9),
    ("product-strategy", "product-roadmap", "prerequisite", 0.8),
    ("product-strategy", "product-positioning", "related", 0.7),
    ("business-model-canvas", "value-proposition", "related", 0.8),
    ("business-model-canvas", "monetization-strategy", "prerequisite", 0.7),
    ("user-story-mapping", "prioritization-frameworks", "prerequisite", 0.8),
    ("product-lifecycle", "product-strategy", "related", 0.7),
    ("systems-thinking", "platform-thinking", "prerequisite", 0.7),
    ("systems-thinking", "ecosystem-design", "related", 0.7),
    ("opportunity-assessment", "product-market-fit", "related", 0.7),
    ("innovation-types", "blue-ocean-strategy", "related", 0.8),
    ("behavioral-economics", "gamification", "related", 0.7),
    ("product-ethics", "design-thinking", "related", 0.6),

    # ── interaction-design internal ──
    ("interaction-design-overview", "gestalt-principles", "prerequisite", 0.9),
    ("interaction-design-overview", "information-architecture", "prerequisite", 0.9),
    ("interaction-design-overview", "progressive-disclosure", "prerequisite", 0.8),
    ("gestalt-principles", "visual-hierarchy", "prerequisite", 0.8),
    ("information-architecture", "navigation-design", "prerequisite", 0.9),
    ("navigation-design", "search-design", "related", 0.7),
    ("form-design", "error-handling-ux", "prerequisite", 0.8),
    ("micro-interaction", "animation-principles", "prerequisite", 0.8),
    ("responsive-design", "mobile-design-patterns", "prerequisite", 0.8),
    ("responsive-design", "multi-platform-design", "related", 0.7),
    ("design-system", "component-library", "prerequisite", 0.9),
    ("design-system", "design-token", "prerequisite", 0.8),
    ("fitts-law", "form-design", "related", 0.7),
    ("hicks-law", "navigation-design", "related", 0.7),
    ("hicks-law", "progressive-disclosure", "related", 0.8),
    ("onboarding-design", "empty-state-design", "related", 0.7),
    ("onboarding-design", "onboarding-optimization", "related", 0.8),
    ("notification-design", "push-notification-strategy", "related", 0.8),
    ("dark-mode-design", "dark-light-theme", "related", 0.8),
    ("accessibility-design", "accessibility-research", "related", 0.8),
    ("voice-ui-design", "multi-platform-design", "related", 0.6),
    ("gamification", "micro-interaction", "related", 0.6),
    ("content-strategy", "prd-writing", "related", 0.6),

    # ── visual-design internal ──
    ("visual-design-overview", "color-theory", "prerequisite", 0.9),
    ("visual-design-overview", "typography", "prerequisite", 0.9),
    ("visual-design-overview", "visual-hierarchy", "prerequisite", 0.9),
    ("color-theory", "dark-light-theme", "prerequisite", 0.8),
    ("color-theory", "contrast-design", "related", 0.8),
    ("typography", "layout-grid", "related", 0.8),
    ("layout-grid", "responsive-imagery", "related", 0.7),
    ("iconography", "illustration-design", "related", 0.7),
    ("brand-design", "design-consistency", "prerequisite", 0.8),
    ("brand-design", "motion-design", "related", 0.7),
    ("design-token", "dark-light-theme", "related", 0.7),
    ("emotional-design", "brand-design", "related", 0.7),
    ("material-design", "ios-human-interface", "related", 0.7),
    ("material-design", "design-system", "related", 0.7),
    ("whitespace-design", "visual-hierarchy", "related", 0.8),
    ("motion-design", "animation-principles", "related", 0.9),
    ("skeuomorphism-vs-flat", "material-design", "related", 0.6),
    ("3d-in-ui", "motion-design", "related", 0.6),
    ("data-visualization", "dashboard-design", "prerequisite", 0.8),
    ("design-handoff", "design-spec", "related", 0.9),
    ("design-handoff", "sketch-to-code", "related", 0.8),

    # ── prototyping internal ──
    ("prototyping-overview", "wireframe", "prerequisite", 0.9),
    ("prototyping-overview", "low-fi-prototype", "prerequisite", 0.9),
    ("wireframe", "high-fi-prototype", "prerequisite", 0.8),
    ("low-fi-prototype", "high-fi-prototype", "prerequisite", 0.8),
    ("low-fi-prototype", "storyboard", "related", 0.7),
    ("figma-basics", "figma-advanced", "prerequisite", 0.9),
    ("figma-basics", "wireframe", "related", 0.7),
    ("figma-advanced", "component-library", "prerequisite", 0.8),
    ("high-fi-prototype", "interactive-prototype", "prerequisite", 0.9),
    ("interactive-prototype", "prototype-testing", "prerequisite", 0.9),
    ("prototype-testing", "design-iteration", "prerequisite", 0.8),
    ("rapid-prototyping", "mvp-design", "related", 0.8),
    ("concept-testing", "prototype-testing", "related", 0.7),
    ("wizard-of-oz", "concept-testing", "related", 0.7),
    ("design-critique", "design-iteration", "related", 0.8),
    ("design-review-checklist", "design-handoff", "prerequisite", 0.8),
    ("ab-testing-design", "ab-testing-analysis", "prerequisite", 0.9),
    ("ab-testing-design", "multivariate-testing", "prerequisite", 0.8),
    ("design-spec", "design-review-checklist", "related", 0.7),

    # ── data-driven internal ──
    ("data-driven-overview", "product-metrics", "prerequisite", 0.9),
    ("data-driven-overview", "event-tracking", "prerequisite", 0.9),
    ("product-metrics", "funnel-analysis", "prerequisite", 0.9),
    ("product-metrics", "retention-analysis", "prerequisite", 0.9),
    ("product-metrics", "ltv-calculation", "related", 0.8),
    ("funnel-analysis", "cohort-analysis", "prerequisite", 0.8),
    ("retention-analysis", "churn-analysis", "related", 0.8),
    ("event-tracking", "analytics-tools", "prerequisite", 0.8),
    ("event-tracking", "behavioral-analytics", "related", 0.7),
    ("analytics-tools", "sql-for-pm", "related", 0.7),
    ("ab-testing-analysis", "experiment-design", "related", 0.8),
    ("ab-testing-analysis", "statistical-significance", "prerequisite", 0.8),
    ("user-segmentation", "cohort-analysis", "related", 0.7),
    ("data-storytelling", "dashboard-design", "related", 0.7),
    ("attribution-model", "funnel-analysis", "related", 0.7),
    ("predictive-analytics", "churn-analysis", "related", 0.7),
    ("data-privacy-compliance", "event-tracking", "related", 0.7),
    ("data-quality", "event-tracking", "related", 0.7),
    ("feature-flag", "release-management", "related", 0.8),
    ("feature-flag", "ab-testing-design", "related", 0.7),

    # ── product-management internal ──
    ("product-management-overview", "product-roadmap", "prerequisite", 0.9),
    ("product-management-overview", "prd-writing", "prerequisite", 0.9),
    ("product-management-overview", "okr-method", "prerequisite", 0.8),
    ("product-roadmap", "sprint-planning", "prerequisite", 0.8),
    ("product-roadmap", "backlog-management", "prerequisite", 0.8),
    ("sprint-planning", "scrum-framework", "related", 0.8),
    ("scrum-framework", "kanban-method", "related", 0.7),
    ("scrum-framework", "retrospective", "prerequisite", 0.8),
    ("backlog-management", "prioritization-frameworks", "related", 0.8),
    ("backlog-management", "feature-specification", "prerequisite", 0.8),
    ("release-management", "product-launch", "prerequisite", 0.8),
    ("stakeholder-management", "cross-functional-collab", "related", 0.8),
    ("stakeholder-management", "product-communication", "related", 0.8),
    ("okr-method", "product-analytics-review", "related", 0.7),
    ("product-analytics-review", "product-metrics-review", "related", 0.9),
    ("technical-debt", "backlog-management", "related", 0.7),
    ("feedback-loop", "backlog-management", "related", 0.7),
    ("team-building", "remote-collaboration", "related", 0.7),
    ("estimation-techniques", "sprint-planning", "related", 0.8),
    ("product-doc-system", "prd-writing", "related", 0.8),
    ("competitive-moat", "product-strategy", "related", 0.8),

    # ── growth internal ──
    ("growth-overview", "aarrr-model", "prerequisite", 0.9),
    ("growth-overview", "growth-hacking", "prerequisite", 0.8),
    ("aarrr-model", "user-activation", "prerequisite", 0.9),
    ("aarrr-model", "retention-strategy", "prerequisite", 0.9),
    ("aarrr-model", "viral-loop", "prerequisite", 0.8),
    ("aarrr-model", "monetization-strategy", "prerequisite", 0.8),
    ("user-activation", "onboarding-optimization", "prerequisite", 0.9),
    ("retention-strategy", "push-notification-strategy", "related", 0.7),
    ("retention-strategy", "user-lifecycle", "related", 0.8),
    ("viral-loop", "referral-program", "prerequisite", 0.8),
    ("viral-loop", "network-effects", "related", 0.7),
    ("content-marketing", "seo-basics", "related", 0.8),
    ("content-marketing", "email-marketing", "related", 0.7),
    ("monetization-strategy", "pricing-strategy", "prerequisite", 0.8),
    ("monetization-strategy", "paywall-design", "related", 0.8),
    ("monetization-strategy", "freemium-model", "related", 0.8),
    ("growth-experiment", "ab-testing-design", "related", 0.8),
    ("growth-experiment", "growth-hacking", "related", 0.8),
    ("community-building", "retention-strategy", "related", 0.7),
    ("network-effects", "growth-loops", "prerequisite", 0.8),
    ("growth-loops", "marketplace-growth", "related", 0.7),
    ("user-lifecycle", "churn-analysis", "related", 0.8),

    # ── cross-subdomain edges ──
    ("user-persona", "product-thinking-overview", "prerequisite", 0.7),
    ("journey-map", "interaction-design-overview", "prerequisite", 0.7),
    ("usability-testing", "prototype-testing", "related", 0.9),
    ("design-thinking", "prototyping-overview", "prerequisite", 0.7),
    ("product-market-fit", "growth-overview", "prerequisite", 0.8),
    ("product-metrics", "product-analytics-review", "related", 0.8),
    ("retention-analysis", "retention-strategy", "related", 0.9),
    ("product-roadmap", "prioritization-frameworks", "related", 0.8),
    ("design-system", "brand-design", "related", 0.7),
    ("information-architecture", "navigation-design", "prerequisite", 0.9),
    ("data-visualization", "data-storytelling", "related", 0.8),
    ("product-launch", "growth-overview", "related", 0.7),
    ("mvp-design", "rapid-prototyping", "related", 0.9),
    ("competitive-analysis", "opportunity-assessment", "related", 0.8),
    ("user-centered-design", "interaction-design-overview", "prerequisite", 0.7),
    ("visual-design-overview", "design-system", "prerequisite", 0.7),
    ("funnel-analysis", "user-activation", "related", 0.7),
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
    # Stats per subdomain
    from collections import Counter
    sub_counts = Counter(c["subdomain_id"] for c in concepts)
    for s in SUBDOMAINS:
        print(f"  {s['name']}: {sub_counts[s['id']]} concepts")

if __name__ == "__main__":
    main()
