#!/usr/bin/env python3
"""Generate Philosophy knowledge sphere seed graph.

8 subdomains, ~170 concepts covering ancient philosophy to contemporary thought.
"""
import json
from datetime import datetime, timezone

NOW = datetime.now(timezone.utc).isoformat()

DOMAIN = {
    "id": "philosophy",
    "name": "哲学",
    "description": "从古代哲学到当代思潮的系统知识体系",
    "icon": "🔮",
    "color": "#06b6d4",
}

SUBDOMAINS = [
    {"id": "ancient-philosophy",    "name": "古代哲学",     "order": 1},
    {"id": "epistemology",          "name": "认识论",       "order": 2},
    {"id": "metaphysics",           "name": "形而上学",     "order": 3},
    {"id": "ethics",                "name": "伦理学",       "order": 4},
    {"id": "logic-reasoning",       "name": "逻辑与推理",   "order": 5},
    {"id": "political-philosophy",  "name": "政治哲学",     "order": 6},
    {"id": "aesthetics",            "name": "美学",         "order": 7},
    {"id": "modern-philosophy",     "name": "近现代哲学",   "order": 8},
]

# (id, name, description, subdomain_id, difficulty, minutes, content_type, tags, is_milestone)
CONCEPTS_RAW = [
    # ── ancient-philosophy (25 concepts) ──
    ("ancient-philosophy-overview", "古代哲学概述",       "古代哲学的起源、分期与核心议题",                     "ancient-philosophy", 1, 20, "theory", ["基础"], True),
    ("pre-socratic-overview",      "前苏格拉底哲学",     "自然哲学家对宇宙本原(arche)的探索",                "ancient-philosophy", 2, 25, "theory", ["早期"], False),
    ("heraclitus",                 "赫拉克利特",         "万物流转、逻各斯与对立统一思想",                     "ancient-philosophy", 2, 25, "theory", ["早期"], False),
    ("parmenides",                 "巴门尼德",           "存在与非存在、思维与存在同一、真理之路",             "ancient-philosophy", 3, 25, "theory", ["早期"], False),
    ("democritus",                 "德谟克利特",         "原子论与虚空、机械唯物主义的先驱",                   "ancient-philosophy", 2, 25, "theory", ["早期"], False),
    ("sophists",                   "智者学派",           "普罗泰戈拉的人是万物的尺度、修辞术与相对主义",       "ancient-philosophy", 2, 25, "theory", ["古希腊"], False),
    ("socrates",                   "苏格拉底",           "苏格拉底方法(诘问法)、认识你自己、美德即知识",      "ancient-philosophy", 2, 30, "theory", ["核心"], True),
    ("plato",                      "柏拉图",             "理念论、洞穴寓言、灵魂三分说与理想国",               "ancient-philosophy", 3, 35, "theory", ["核心"], True),
    ("plato-republic",             "《理想国》",          "正义论、哲学王、理想城邦的三阶层结构",               "ancient-philosophy", 3, 30, "theory", ["经典"], False),
    ("aristotle",                  "亚里士多德",         "四因说、实体学说、中庸之道与逻辑学奠基",             "ancient-philosophy", 3, 35, "theory", ["核心"], True),
    ("aristotle-ethics",           "亚里士多德伦理学",   "尼各马可伦理学、幸福(eudaimonia)与实践智慧",        "ancient-philosophy", 3, 30, "theory", ["伦理"], False),
    ("epicurus",                   "伊壁鸠鲁",           "快乐主义、原子论伦理学、灵魂死灭论",                 "ancient-philosophy", 3, 25, "theory", ["希腊化"], False),
    ("stoicism",                   "斯多亚学派",         "自然法则、理性生活、克制情感与命运之爱",              "ancient-philosophy", 3, 30, "theory", ["希腊化"], False),
    ("skepticism-ancient",         "古代怀疑论",         "皮浪主义、悬搁判断(epoché)与宁静生活",             "ancient-philosophy", 3, 25, "theory", ["希腊化"], False),
    ("neoplatonism",               "新柏拉图主义",       "普罗提诺的太一、流溢说与神秘主义传统",               "ancient-philosophy", 4, 25, "theory", ["晚期"], False),
    ("confucius",                  "孔子",               "仁义礼智信、君子之道与《论语》思想",                 "ancient-philosophy", 2, 30, "theory", ["东方"], True),
    ("mencius",                    "孟子",               "性善论、仁政思想与浩然之气",                         "ancient-philosophy", 3, 25, "theory", ["东方"], False),
    ("xunzi",                      "荀子",               "性恶论、隆礼重法、天人之分",                         "ancient-philosophy", 3, 25, "theory", ["东方"], False),
    ("laozi",                      "老子",               "道法自然、无为而治、《道德经》核心思想",             "ancient-philosophy", 2, 30, "theory", ["东方"], False),
    ("zhuangzi",                   "庄子",               "逍遥游、齐物论、坐忘与心斋",                         "ancient-philosophy", 3, 30, "theory", ["东方"], False),
    ("mozi",                       "墨子",               "兼爱非攻、尚贤尚同、功利主义先驱",                   "ancient-philosophy", 3, 25, "theory", ["东方"], False),
    ("legalism",                   "法家思想",           "韩非子的法术势、商鞅变法与法治思想",                 "ancient-philosophy", 3, 25, "theory", ["东方"], False),
    ("buddhist-philosophy",        "佛教哲学",           "四谛八正道、缘起性空、中观与唯识",                   "ancient-philosophy", 3, 30, "theory", ["东方"], False),
    ("yinyang-school",             "阴阳家",             "阴阳五行、天人感应与宇宙论框架",                     "ancient-philosophy", 3, 25, "theory", ["东方"], False),
    ("ancient-philosophy-legacy",  "古代哲学遗产",       "古代哲学对中世纪、近现代思想的深远影响",             "ancient-philosophy", 2, 20, "theory", ["总结"], False),

    # ── epistemology (22 concepts) ──
    ("epistemology-overview",      "认识论概述",         "认识论的核心问题:知识的本质、来源与限度",            "epistemology", 1, 20, "theory", ["基础"], True),
    ("knowledge-definition",       "知识的定义",         "JTB理论(justified true belief)及其挑战",            "epistemology", 2, 25, "theory", ["核心"], False),
    ("gettier-problem",            "盖梯尔问题",         "对JTB定义的反例与知识定义的当代争论",                 "epistemology", 3, 25, "theory", ["核心"], False),
    ("rationalism",                "理性主义",           "笛卡尔/莱布尼茨/斯宾诺莎:先天观念与理性认知",       "epistemology", 3, 30, "theory", ["流派"], True),
    ("empiricism",                 "经验主义",           "洛克/贝克莱/休谟:白板说与感觉经验的优先性",         "epistemology", 3, 30, "theory", ["流派"], True),
    ("a-priori-knowledge",         "先验知识与后验知识", "先验/后验、分析/综合命题的区分",                     "epistemology", 3, 25, "theory", ["概念"], False),
    ("kant-epistemology",          "康德认识论",         "先验综合判断、感性直观与知性范畴的统一",             "epistemology", 4, 35, "theory", ["核心"], True),
    ("skepticism",                 "怀疑论",             "笛卡尔式怀疑、休谟问题与怀疑论的当代形态",           "epistemology", 3, 25, "theory", ["流派"], False),
    ("truth-theories",             "真理理论",           "符合论、融贯论、实用主义真理观与紧缩论",             "epistemology", 3, 30, "theory", ["核心"], False),
    ("scientific-method-phil",     "科学方法论",         "归纳法、假说演绎法与科学发现的逻辑",                 "epistemology", 2, 25, "theory", ["方法"], False),
    ("induction-problem",          "归纳问题",           "休谟的归纳怀疑与归纳合理性的辩护",                   "epistemology", 3, 25, "theory", ["问题"], False),
    ("falsificationism",           "证伪主义",           "波普尔的证伪理论与科学划界问题",                     "epistemology", 3, 25, "theory", ["科学哲学"], False),
    ("paradigm-shift",             "范式转换",           "库恩的科学革命结构与范式不可通约性",                 "epistemology", 3, 25, "theory", ["科学哲学"], False),
    ("epistemological-relativism", "认识论相对主义",     "费耶阿本德的认识论无政府主义与方法多元",             "epistemology", 4, 25, "theory", ["前沿"], False),
    ("social-epistemology",        "社会认识论",         "知识的社会维度、证词与集体知识",                     "epistemology", 4, 25, "theory", ["前沿"], False),
    ("foundationalism",            "基础主义",           "知识的基础结构:基本信念与推导信念",                  "epistemology", 3, 25, "theory", ["结构"], False),
    ("coherentism",                "融贯论",             "信念的相互支持与知识的网络结构",                     "epistemology", 3, 25, "theory", ["结构"], False),
    ("reliabilism",                "可靠主义",           "戈德曼的过程可靠论与外在主义辩护",                   "epistemology", 4, 25, "theory", ["当代"], False),
    ("virtue-epistemology",        "德性认识论",         "智识德性:开放心灵、求知勇气与认知谦逊",             "epistemology", 4, 25, "theory", ["当代"], False),
    ("phenomenology-method",       "现象学方法",         "胡塞尔的意向性分析与悬搁(epoché)方法",             "epistemology", 4, 30, "theory", ["方法"], False),
    ("pragmatist-epistemology",    "实用主义认识论",     "皮尔斯/杜威/詹姆斯:知识的实践检验",                "epistemology", 3, 25, "theory", ["流派"], False),
    ("naturalized-epistemology",   "自然化认识论",       "蒯因的认识论自然化与认知科学的介入",                 "epistemology", 4, 25, "theory", ["当代"], False),

    # ── metaphysics (20 concepts) ──
    ("metaphysics-overview",       "形而上学概述",       "形而上学的研究对象:存在、实在与世界的根本结构",      "metaphysics", 1, 20, "theory", ["基础"], True),
    ("being-existence",            "存在",               "存在的意义、存在与本质的关系、存在论差异",           "metaphysics", 2, 25, "theory", ["核心"], False),
    ("ontology",                   "本体论",             "存在者的分类:实体/属性/关系/事件",                   "metaphysics", 3, 30, "theory", ["核心"], False),
    ("realism-antirealism",        "实在论与反实在论",   "外部世界是否独立于心灵存在的争论",                   "metaphysics", 3, 25, "theory", ["争论"], False),
    ("idealism",                   "唯心主义",           "贝克莱/黑格尔:心灵或理念是实在的基础",              "metaphysics", 3, 30, "theory", ["流派"], False),
    ("materialism-physicalism",    "唯物主义与物理主义", "一切存在归结为物质或物理实体",                       "metaphysics", 3, 25, "theory", ["流派"], False),
    ("dualism",                    "二元论",             "笛卡尔心物二元论与交互问题",                         "metaphysics", 3, 25, "theory", ["心灵"], False),
    ("causation",                  "因果关系",           "因果关系的本质:休谟式恒常联结vs必然联系",            "metaphysics", 3, 25, "theory", ["概念"], True),
    ("free-will",                  "自由意志",           "自由意志的存在性争论与道德责任",                     "metaphysics", 3, 30, "theory", ["核心"], True),
    ("determinism",                "决定论",             "因果决定论、物理决定论与相容论",                     "metaphysics", 3, 25, "theory", ["争论"], False),
    ("compatibilism",              "相容论",             "自由意志与决定论的调和尝试",                         "metaphysics", 4, 25, "theory", ["争论"], False),
    ("time-space",                 "时间与空间",         "时间的本质:A理论vs B理论,绝对空间vs关系空间",       "metaphysics", 4, 30, "theory", ["概念"], False),
    ("personal-identity",          "个人同一性",         "是什么使一个人在时间中保持同一:身体/记忆/心理连续性", "metaphysics", 3, 25, "theory", ["概念"], False),
    ("possible-worlds",            "可能世界",           "模态实在论:必然/可能/偶然的形而上学基础",            "metaphysics", 4, 25, "theory", ["前沿"], False),
    ("universals-particulars",     "共相与殊相",         "共相问题:实在论/唯名论/概念论",                     "metaphysics", 3, 25, "theory", ["经典"], False),
    ("substance-metaphysics",      "实体",               "实体的概念:从亚里士多德到当代本体论",                "metaphysics", 3, 25, "theory", ["概念"], False),
    ("mind-body-problem",          "心身问题",           "意识如何与物质关联:物理主义/属性二元论/泛心论",      "metaphysics", 4, 30, "theory", ["核心"], False),
    ("emergence",                  "涌现",               "复杂系统中高层属性不可还原的涌现现象",               "metaphysics", 4, 25, "theory", ["前沿"], False),
    ("abstract-objects",           "抽象对象",           "数/命题/集合等非时空实体的本体论地位",               "metaphysics", 4, 25, "theory", ["前沿"], False),
    ("chinese-metaphysics",        "中国形而上学",       "气论/理气关系/天道观:中国哲学的本体论传统",          "metaphysics", 3, 25, "theory", ["东方"], False),

    # ── ethics (25 concepts) ──
    ("ethics-overview",            "伦理学概述",         "伦理学的分类:规范伦理/元伦理/应用伦理",             "ethics", 1, 20, "theory", ["基础"], True),
    ("utilitarianism",             "功利主义",           "边沁/密尔:最大多数人的最大幸福原则",                "ethics", 2, 30, "theory", ["核心"], True),
    ("act-rule-utilitarianism",    "行为与规则功利主义", "行为功利主义vs规则功利主义的区分与争论",              "ethics", 3, 25, "theory", ["功利"], False),
    ("deontology",                 "义务论",             "康德的定言命令:普遍化法则与人作为目的",              "ethics", 3, 30, "theory", ["核心"], True),
    ("categorical-imperative",     "定言命令",           "康德三个定言命令公式与道德义务的推导",               "ethics", 4, 30, "theory", ["康德"], False),
    ("virtue-ethics",              "美德伦理学",         "亚里士多德传统:品格/德性/实践智慧(phronesis)",       "ethics", 2, 30, "theory", ["核心"], True),
    ("care-ethics",                "关怀伦理学",         "吉利根/诺丁斯:关系性道德与关怀回应",               "ethics", 3, 25, "theory", ["当代"], False),
    ("metaethics",                 "元伦理学",           "道德判断的本质:道德实在论vs反实在论",                "ethics", 4, 30, "theory", ["核心"], False),
    ("moral-realism",              "道德实在论",         "客观道德事实的存在性论证",                           "ethics", 4, 25, "theory", ["元伦理"], False),
    ("emotivism",                  "情感主义",           "艾耶尔/史蒂文森:道德判断表达情感而非事实",          "ethics", 4, 25, "theory", ["元伦理"], False),
    ("moral-relativism",           "道德相对主义",       "道德标准因文化/个人而异的立场及其挑战",              "ethics", 3, 25, "theory", ["争论"], False),
    ("problem-of-evil",            "善恶问题",           "恶的存在与全善全能上帝的矛盾:神义论困境",           "ethics", 3, 25, "theory", ["宗教哲学"], False),
    ("applied-ethics",             "应用伦理学",         "将伦理理论应用于具体道德难题的实践方法",             "ethics", 2, 20, "theory", ["应用"], False),
    ("bioethics",                  "生命伦理学",         "安乐死/基因编辑/克隆/器官分配的伦理争论",           "ethics", 3, 30, "theory", ["应用"], False),
    ("environmental-ethics",       "环境伦理学",         "深层生态学、动物权利与人类中心主义批判",             "ethics", 3, 25, "theory", ["应用"], False),
    ("business-ethics",            "商业伦理",           "企业社会责任、利益相关者理论与道德决策",             "ethics", 3, 25, "theory", ["应用"], False),
    ("tech-ethics",                "技术伦理",           "AI伦理/数据隐私/算法偏见/自主武器的伦理挑战",       "ethics", 3, 25, "theory", ["前沿"], False),
    ("human-rights-phil",          "人权的哲学基础",     "自然权利/人的尊严/普世价值的哲学论证",               "ethics", 3, 25, "theory", ["核心"], False),
    ("justice-concept",            "正义概念",           "分配正义/矫正正义/程序正义的基本区分",               "ethics", 2, 25, "theory", ["核心"], True),
    ("trolley-problem",            "电车难题",           "经典道德直觉实验与后果论vs义务论的对决",             "ethics", 2, 20, "theory", ["思想实验"], False),
    ("moral-development-phil",     "道德发展",           "科尔伯格的道德发展阶段与道德教育哲学",               "ethics", 3, 25, "theory", ["发展"], False),
    ("confucian-ethics",           "儒家伦理",           "仁义礼智的德性体系与五伦关系伦理",                   "ethics", 3, 25, "theory", ["东方"], False),
    ("buddhist-ethics",            "佛教伦理",           "慈悲/不害/业报:佛教道德框架",                       "ethics", 3, 25, "theory", ["东方"], False),
    ("moral-psychology",           "道德心理学",         "道德情感/道德直觉/道德判断的心理机制",               "ethics", 3, 25, "theory", ["交叉"], False),
    ("effective-altruism",         "有效利他主义",       "彼得·辛格与理性慈善:最大化善的当代运动",            "ethics", 3, 25, "theory", ["当代"], False),

    # ── logic-reasoning (18 concepts) ──
    ("logic-overview",             "逻辑学概述",         "逻辑学的研究对象:有效推理的规则与形式",              "logic-reasoning", 1, 20, "theory", ["基础"], True),
    ("propositional-logic",        "命题逻辑",           "命题联结词(与/或/非/蕴含)与真值表",                 "logic-reasoning", 2, 30, "theory", ["核心"], True),
    ("predicate-logic",            "谓词逻辑",           "量词(全称/存在)、谓词与一阶逻辑的表达力",           "logic-reasoning", 3, 30, "theory", ["核心"], False),
    ("deductive-reasoning",        "演绎推理",           "从一般到特殊:三段论/假言推理/析取推理",             "logic-reasoning", 2, 25, "theory", ["推理"], True),
    ("inductive-reasoning",        "归纳推理",           "从特殊到一般:归纳强度与归纳谬误",                   "logic-reasoning", 2, 25, "theory", ["推理"], False),
    ("abductive-reasoning",        "溯因推理",           "推断最佳解释:从观察到假说的推理",                   "logic-reasoning", 3, 25, "theory", ["推理"], False),
    ("analogical-reasoning",       "类比推理",           "基于相似性的推理:类比的结构与评估标准",             "logic-reasoning", 2, 25, "theory", ["推理"], False),
    ("formal-fallacies",           "形式谬误",           "肯定后件/否定前件/不当三段论等结构性推理错误",       "logic-reasoning", 2, 25, "theory", ["谬误"], False),
    ("informal-fallacies",         "非形式谬误",         "稻草人/诉诸权威/红鲱鱼/滑坡论证等内容性谬误",       "logic-reasoning", 2, 25, "theory", ["谬误"], False),
    ("paradoxes",                  "悖论",               "说谎者悖论/飞矢悖论/忒修斯之船:逻辑与哲学的交叉",  "logic-reasoning", 3, 25, "theory", ["核心"], False),
    ("modal-logic",                "模态逻辑",           "必然性与可能性算子:模态命题与可能世界语义",          "logic-reasoning", 4, 30, "theory", ["高级"], False),
    ("argument-structure",         "论证结构",           "前提/结论/论证形式与论证图析",                       "logic-reasoning", 2, 25, "theory", ["基础"], False),
    ("critical-thinking",          "批判性思维",         "论证评估/证据权衡/认知偏见识别的实践方法",           "logic-reasoning", 2, 30, "theory", ["实践"], True),
    ("philosophy-of-logic",        "逻辑哲学",           "逻辑的本质:逻辑是发现还是发明?逻辑多元主义",       "logic-reasoning", 4, 25, "theory", ["前沿"], False),
    ("dialectic",                  "辩证法",             "从苏格拉底到黑格尔:正题/反题/合题的思维运动",       "logic-reasoning", 3, 25, "theory", ["方法"], False),
    ("set-theory-phil",            "集合论基础",         "集合论悖论与数学基础的哲学反思",                     "logic-reasoning", 4, 25, "theory", ["数理"], False),
    ("philosophy-of-math",         "数学哲学",           "柏拉图主义/形式主义/直觉主义:数学对象的本质",       "logic-reasoning", 4, 30, "theory", ["交叉"], False),
    ("fuzzy-logic-phil",           "模糊逻辑",           "多值逻辑与模糊概念:对经典二值逻辑的扩展",           "logic-reasoning", 4, 25, "theory", ["前沿"], False),

    # ── political-philosophy (22 concepts) ──
    ("political-philosophy-overview", "政治哲学概述",     "政治哲学的核心问题:国家/权力/正义/自由",            "political-philosophy", 1, 20, "theory", ["基础"], True),
    ("social-contract",            "社会契约论",         "霍布斯/洛克/卢梭:政治权威的合法性基础",             "political-philosophy", 2, 30, "theory", ["核心"], True),
    ("hobbes",                     "霍布斯",             "自然状态、利维坦与绝对主权理论",                     "political-philosophy", 3, 30, "theory", ["经典"], False),
    ("locke-political",            "洛克政治哲学",       "自然权利、有限政府与财产权理论",                     "political-philosophy", 3, 30, "theory", ["经典"], False),
    ("rousseau",                   "卢梭",               "公意、人民主权与社会不平等批判",                     "political-philosophy", 3, 30, "theory", ["经典"], False),
    ("liberalism",                 "自由主义",           "个人自由/权利保障/有限政府的政治传统",               "political-philosophy", 2, 25, "theory", ["流派"], True),
    ("conservatism",               "保守主义",           "伯克传统:秩序/渐进改革/制度延续的价值",             "political-philosophy", 3, 25, "theory", ["流派"], False),
    ("socialism",                  "社会主义",           "马克思/恩格斯:阶级斗争/生产资料公有/社会公正",      "political-philosophy", 3, 30, "theory", ["流派"], False),
    ("marxism",                    "马克思主义",         "历史唯物主义/资本批判/异化/意识形态批判",            "political-philosophy", 3, 30, "theory", ["经典"], False),
    ("anarchism",                  "无政府主义",         "反国家/自治/互助:从克鲁泡特金到当代无政府主义",     "political-philosophy", 3, 25, "theory", ["流派"], False),
    ("rawls-justice",              "罗尔斯正义论",       "无知之幕、原初立场与正义两原则",                     "political-philosophy", 4, 35, "theory", ["核心"], False),
    ("nozick-libertarianism",      "诺齐克自由至上主义", "最小国家、持有正义与对再分配的批判",                 "political-philosophy", 4, 25, "theory", ["当代"], False),
    ("democracy-theory",           "民主理论",           "直接民主/代议民主/审议民主/参与式民主",              "political-philosophy", 2, 25, "theory", ["核心"], True),
    ("power-theory",               "权力理论",           "福柯的微观权力/韦伯的支配类型/权力的面孔",          "political-philosophy", 3, 25, "theory", ["概念"], False),
    ("civil-society",              "公民社会",           "公共领域/社团/市民参与与国家之间的关系",             "political-philosophy", 3, 25, "theory", ["概念"], False),
    ("rights-theory",              "权利理论",           "自然权利vs法律权利、积极权利vs消极权利",             "political-philosophy", 3, 25, "theory", ["概念"], False),
    ("nationalism",                "民族主义",           "民族国家/民族认同/民族自决权的哲学基础",             "political-philosophy", 3, 25, "theory", ["议题"], False),
    ("cosmopolitanism",            "世界主义",           "全球正义/世界公民/超越民族国家的道德义务",           "political-philosophy", 3, 25, "theory", ["当代"], False),
    ("feminism-political",         "女性主义政治哲学",   "性别平等/父权制批判/交叉性与身份政治",               "political-philosophy", 3, 25, "theory", ["当代"], False),
    ("multiculturalism",           "多元文化主义",       "文化承认/群体权利/差异政治与文化冲突",               "political-philosophy", 3, 25, "theory", ["当代"], False),
    ("chinese-political-phil",     "中国政治哲学",       "天命观/民本思想/大同理想与儒法互补",                 "political-philosophy", 3, 25, "theory", ["东方"], False),
    ("global-justice",             "全球正义",           "国际分配正义/气候正义/移民权利的哲学争论",           "political-philosophy", 4, 25, "theory", ["前沿"], False),

    # ── aesthetics (18 concepts) ──
    ("aesthetics-overview",        "美学概述",           "美学的研究对象:美/艺术/审美经验的哲学探究",         "aesthetics", 1, 20, "theory", ["基础"], True),
    ("nature-of-beauty",           "美的本质",           "客观美vs主观美:从柏拉图到经验论的美学争论",         "aesthetics", 2, 25, "theory", ["核心"], False),
    ("definition-of-art",          "艺术的定义",         "模仿论/表现论/制度论/家族相似:什么是艺术?",        "aesthetics", 3, 30, "theory", ["核心"], True),
    ("aesthetic-judgment",         "审美判断",           "康德的审美判断力批判:无利害的愉悦与共通感",         "aesthetics", 4, 30, "theory", ["核心"], False),
    ("sublime",                    "崇高",               "伯克与康德论崇高:恐惧/无限/理性的超越",            "aesthetics", 3, 25, "theory", ["概念"], False),
    ("mimesis",                    "模仿论",             "柏拉图与亚里士多德的模仿论:艺术再现现实",           "aesthetics", 2, 25, "theory", ["理论"], False),
    ("expression-theory",         "表现论",             "克罗齐/科林伍德:艺术是情感的表达与传达",            "aesthetics", 3, 25, "theory", ["理论"], False),
    ("art-form",                   "艺术形式",           "形式与内容的关系:形式主义美学与后形式主义",         "aesthetics", 3, 25, "theory", ["概念"], False),
    ("art-criticism",              "艺术批评",           "艺术评价的标准/方法/主观与客观之间的张力",           "aesthetics", 3, 25, "theory", ["实践"], False),
    ("aesthetic-experience",       "审美经验",           "审美态度/审美感知/审美情感的哲学分析",               "aesthetics", 3, 25, "theory", ["概念"], False),
    ("chinese-aesthetics",         "中国传统美学",       "气韵生动/意境/虚实/留白:中国美学的核心范畴",       "aesthetics", 3, 30, "theory", ["东方"], False),
    ("tragedy-philosophy",         "悲剧哲学",           "亚里士多德的净化论与尼采的悲剧精神",                 "aesthetics", 3, 25, "theory", ["经典"], False),
    ("philosophy-of-music",        "音乐哲学",           "音乐的本质:形式主义vs表现主义/绝对音乐与标题音乐",  "aesthetics", 3, 25, "theory", ["分支"], False),
    ("photography-aesthetics",     "摄影美学",           "本雅明的机械复制时代艺术:灵韵(aura)的消失",        "aesthetics", 3, 25, "theory", ["当代"], False),
    ("environmental-aesthetics",   "环境美学",           "自然美/景观美学/日常生活审美化",                     "aesthetics", 3, 25, "theory", ["当代"], False),
    ("digital-aesthetics",         "数字美学",           "数字艺术/生成艺术/AI创作的美学挑战",                "aesthetics", 3, 25, "theory", ["前沿"], False),
    ("taste-theory",               "趣味理论",           "休谟的趣味标准与审美教育的可能性",                   "aesthetics", 3, 25, "theory", ["概念"], False),
    ("institutional-theory",       "艺术制度论",         "丹托/迪基:艺术世界与艺术地位的社会赋予",            "aesthetics", 4, 25, "theory", ["当代"], False),

    # ── modern-philosophy (20 concepts) ──
    ("modern-philosophy-overview", "近现代哲学概述",     "从笛卡尔到后现代:西方近现代哲学的主要运动",         "modern-philosophy", 1, 20, "theory", ["基础"], True),
    ("existentialism",             "存在主义",           "萨特/加缪/海德格尔:存在先于本质与自由选择",         "modern-philosophy", 3, 30, "theory", ["核心"], True),
    ("phenomenology",              "现象学",             "胡塞尔的意向性/海德格尔的此在/梅洛-庞蒂的身体",     "modern-philosophy", 4, 35, "theory", ["核心"], False),
    ("analytic-philosophy",        "分析哲学",           "弗雷格/罗素/维特根斯坦:语言分析与逻辑清晰性",      "modern-philosophy", 3, 30, "theory", ["核心"], True),
    ("wittgenstein",               "维特根斯坦",         "逻辑哲学论/哲学研究:语言游戏与生活形式",            "modern-philosophy", 4, 30, "theory", ["人物"], False),
    ("postmodernism",              "后现代主义",         "利奥塔/鲍德里亚:大叙事的终结与模拟的时代",          "modern-philosophy", 3, 30, "theory", ["核心"], False),
    ("deconstruction",             "解构主义",           "德里达:延异/增补/文本之外无物",                     "modern-philosophy", 4, 30, "theory", ["核心"], False),
    ("pragmatism",                 "实用主义",           "皮尔斯/詹姆斯/杜威/罗蒂:真理的实践标准",           "modern-philosophy", 3, 25, "theory", ["流派"], True),
    ("philosophy-of-language",     "语言哲学",           "意义理论/指称/言语行为:语言如何承载思想",           "modern-philosophy", 4, 30, "theory", ["分支"], False),
    ("philosophy-of-mind",         "心灵哲学",           "意识难问题/感受质/功能主义/取消唯物论",              "modern-philosophy", 4, 30, "theory", ["分支"], False),
    ("feminist-philosophy",        "女性主义哲学",       "波伏娃/巴特勒:性别建构/身体政治/交叉性",            "modern-philosophy", 3, 25, "theory", ["当代"], False),
    ("postcolonial-philosophy",    "后殖民哲学",         "赛义德/斯皮瓦克/法农:东方主义/底层发声/殖民批判",   "modern-philosophy", 3, 25, "theory", ["当代"], False),
    ("critical-theory",            "批判理论",           "法兰克福学派:文化工业/工具理性/公共领域批判",        "modern-philosophy", 3, 30, "theory", ["流派"], False),
    ("hermeneutics",               "诠释学",             "伽达默尔:理解的历史性/视域融合/效果历史",            "modern-philosophy", 4, 30, "theory", ["流派"], False),
    ("structuralism",              "结构主义",           "索绪尔/列维-斯特劳斯:深层结构与二元对立",           "modern-philosophy", 3, 25, "theory", ["流派"], False),
    ("philosophy-of-science",      "科学哲学",           "科学实在论/工具主义/科学解释模型",                   "modern-philosophy", 3, 25, "theory", ["分支"], False),
    ("philosophy-of-technology",   "技术哲学",           "海德格尔论技术/技术决定论/技术的伦理维度",           "modern-philosophy", 3, 25, "theory", ["前沿"], False),
    ("process-philosophy",         "过程哲学",           "怀特海:实际存在物/过程与实在/有机哲学",              "modern-philosophy", 4, 25, "theory", ["流派"], False),
    ("new-confucianism",           "新儒学",             "牟宗三/唐君毅:中国哲学的现代转化与儒学复兴",        "modern-philosophy", 4, 25, "theory", ["东方"], False),
    ("philosophy-of-ai",           "人工智能哲学",       "中文房间/图灵测试/机器意识/AI伦理的哲学基础",       "modern-philosophy", 3, 25, "theory", ["前沿"], False),
]


def build_edges(concepts):
    """Build edges between concepts."""
    edges = []
    eid = 1

    def edge(src, tgt, rel="prerequisite", strength=0.8):
        nonlocal eid
        edges.append({
            "source_id": src,
            "target_id": tgt,
            "relation_type": rel,
            "strength": strength,
        })
        eid += 1

    # ── ancient-philosophy ──
    edge("ancient-philosophy-overview", "pre-socratic-overview")
    edge("pre-socratic-overview", "heraclitus")
    edge("pre-socratic-overview", "parmenides")
    edge("pre-socratic-overview", "democritus")
    edge("ancient-philosophy-overview", "sophists")
    edge("sophists", "socrates")
    edge("socrates", "plato")
    edge("plato", "plato-republic")
    edge("plato", "aristotle", "influences", 0.8)
    edge("aristotle", "aristotle-ethics")
    edge("democritus", "epicurus", "influences", 0.6)
    edge("socrates", "stoicism", "influences", 0.6)
    edge("plato", "neoplatonism", "influences", 0.7)
    edge("ancient-philosophy-overview", "skepticism-ancient")
    edge("ancient-philosophy-overview", "confucius")
    edge("confucius", "mencius")
    edge("confucius", "xunzi", "influences", 0.7)
    edge("ancient-philosophy-overview", "laozi")
    edge("laozi", "zhuangzi")
    edge("ancient-philosophy-overview", "mozi")
    edge("confucius", "legalism", "influences", 0.5)
    edge("xunzi", "legalism", "influences", 0.6)
    edge("ancient-philosophy-overview", "buddhist-philosophy")
    edge("ancient-philosophy-overview", "yinyang-school")
    edge("plato", "ancient-philosophy-legacy", "related", 0.5)
    edge("aristotle", "ancient-philosophy-legacy", "related", 0.5)

    # ── epistemology ──
    edge("epistemology-overview", "knowledge-definition")
    edge("knowledge-definition", "gettier-problem")
    edge("epistemology-overview", "rationalism")
    edge("epistemology-overview", "empiricism")
    edge("rationalism", "a-priori-knowledge", "related", 0.7)
    edge("empiricism", "a-priori-knowledge", "related", 0.7)
    edge("rationalism", "kant-epistemology", "influences", 0.8)
    edge("empiricism", "kant-epistemology", "influences", 0.8)
    edge("epistemology-overview", "skepticism")
    edge("epistemology-overview", "truth-theories")
    edge("epistemology-overview", "scientific-method-phil")
    edge("scientific-method-phil", "induction-problem")
    edge("induction-problem", "falsificationism")
    edge("falsificationism", "paradigm-shift")
    edge("paradigm-shift", "epistemological-relativism")
    edge("epistemology-overview", "social-epistemology")
    edge("knowledge-definition", "foundationalism")
    edge("knowledge-definition", "coherentism")
    edge("foundationalism", "reliabilism", "related", 0.6)
    edge("knowledge-definition", "virtue-epistemology")
    edge("epistemology-overview", "phenomenology-method")
    edge("empiricism", "pragmatist-epistemology", "influences", 0.6)
    edge("epistemology-overview", "naturalized-epistemology")

    # ── metaphysics ──
    edge("metaphysics-overview", "being-existence")
    edge("being-existence", "ontology")
    edge("metaphysics-overview", "realism-antirealism")
    edge("realism-antirealism", "idealism")
    edge("realism-antirealism", "materialism-physicalism")
    edge("metaphysics-overview", "dualism")
    edge("dualism", "mind-body-problem")
    edge("metaphysics-overview", "causation")
    edge("causation", "free-will", "related", 0.7)
    edge("metaphysics-overview", "free-will")
    edge("free-will", "determinism")
    edge("determinism", "compatibilism")
    edge("metaphysics-overview", "time-space")
    edge("metaphysics-overview", "personal-identity")
    edge("ontology", "possible-worlds", "related", 0.6)
    edge("ontology", "universals-particulars")
    edge("being-existence", "substance-metaphysics")
    edge("mind-body-problem", "emergence", "related", 0.6)
    edge("ontology", "abstract-objects")
    edge("metaphysics-overview", "chinese-metaphysics")

    # ── ethics ──
    edge("ethics-overview", "utilitarianism")
    edge("utilitarianism", "act-rule-utilitarianism")
    edge("ethics-overview", "deontology")
    edge("deontology", "categorical-imperative")
    edge("ethics-overview", "virtue-ethics")
    edge("ethics-overview", "care-ethics")
    edge("ethics-overview", "metaethics")
    edge("metaethics", "moral-realism")
    edge("metaethics", "emotivism")
    edge("ethics-overview", "moral-relativism")
    edge("ethics-overview", "problem-of-evil")
    edge("ethics-overview", "applied-ethics")
    edge("applied-ethics", "bioethics")
    edge("applied-ethics", "environmental-ethics")
    edge("applied-ethics", "business-ethics")
    edge("applied-ethics", "tech-ethics")
    edge("ethics-overview", "human-rights-phil")
    edge("ethics-overview", "justice-concept")
    edge("utilitarianism", "trolley-problem", "related", 0.7)
    edge("deontology", "trolley-problem", "related", 0.7)
    edge("ethics-overview", "moral-development-phil")
    edge("virtue-ethics", "confucian-ethics", "related", 0.6)
    edge("ethics-overview", "buddhist-ethics")
    edge("ethics-overview", "moral-psychology")
    edge("utilitarianism", "effective-altruism", "influences", 0.7)

    # ── logic-reasoning ──
    edge("logic-overview", "propositional-logic")
    edge("propositional-logic", "predicate-logic")
    edge("logic-overview", "deductive-reasoning")
    edge("logic-overview", "inductive-reasoning")
    edge("logic-overview", "abductive-reasoning")
    edge("logic-overview", "analogical-reasoning")
    edge("deductive-reasoning", "formal-fallacies")
    edge("inductive-reasoning", "informal-fallacies", "related", 0.6)
    edge("logic-overview", "paradoxes")
    edge("predicate-logic", "modal-logic")
    edge("logic-overview", "argument-structure")
    edge("argument-structure", "critical-thinking")
    edge("formal-fallacies", "critical-thinking", "related", 0.7)
    edge("informal-fallacies", "critical-thinking", "related", 0.7)
    edge("predicate-logic", "philosophy-of-logic")
    edge("logic-overview", "dialectic")
    edge("predicate-logic", "set-theory-phil", "related", 0.6)
    edge("set-theory-phil", "philosophy-of-math")
    edge("modal-logic", "fuzzy-logic-phil", "related", 0.5)

    # ── political-philosophy ──
    edge("political-philosophy-overview", "social-contract")
    edge("social-contract", "hobbes")
    edge("social-contract", "locke-political")
    edge("social-contract", "rousseau")
    edge("political-philosophy-overview", "liberalism")
    edge("locke-political", "liberalism", "influences", 0.8)
    edge("political-philosophy-overview", "conservatism")
    edge("political-philosophy-overview", "socialism")
    edge("socialism", "marxism")
    edge("political-philosophy-overview", "anarchism")
    edge("liberalism", "rawls-justice", "influences", 0.7)
    edge("rawls-justice", "nozick-libertarianism", "related", 0.7)
    edge("political-philosophy-overview", "democracy-theory")
    edge("political-philosophy-overview", "power-theory")
    edge("political-philosophy-overview", "civil-society")
    edge("political-philosophy-overview", "rights-theory")
    edge("locke-political", "rights-theory", "influences", 0.7)
    edge("political-philosophy-overview", "nationalism")
    edge("nationalism", "cosmopolitanism", "related", 0.6)
    edge("political-philosophy-overview", "feminism-political")
    edge("liberalism", "multiculturalism", "related", 0.5)
    edge("political-philosophy-overview", "chinese-political-phil")
    edge("rawls-justice", "global-justice", "influences", 0.6)

    # ── aesthetics ──
    edge("aesthetics-overview", "nature-of-beauty")
    edge("aesthetics-overview", "definition-of-art")
    edge("definition-of-art", "aesthetic-judgment")
    edge("aesthetics-overview", "sublime")
    edge("aesthetics-overview", "mimesis")
    edge("aesthetics-overview", "expression-theory")
    edge("definition-of-art", "art-form")
    edge("definition-of-art", "art-criticism")
    edge("aesthetics-overview", "aesthetic-experience")
    edge("aesthetics-overview", "chinese-aesthetics")
    edge("mimesis", "tragedy-philosophy", "related", 0.7)
    edge("aesthetics-overview", "philosophy-of-music")
    edge("aesthetics-overview", "photography-aesthetics")
    edge("aesthetics-overview", "environmental-aesthetics")
    edge("aesthetics-overview", "digital-aesthetics")
    edge("nature-of-beauty", "taste-theory", "related", 0.7)
    edge("definition-of-art", "institutional-theory")

    # ── modern-philosophy ──
    edge("modern-philosophy-overview", "existentialism")
    edge("modern-philosophy-overview", "phenomenology")
    edge("modern-philosophy-overview", "analytic-philosophy")
    edge("analytic-philosophy", "wittgenstein")
    edge("modern-philosophy-overview", "postmodernism")
    edge("postmodernism", "deconstruction")
    edge("modern-philosophy-overview", "pragmatism")
    edge("analytic-philosophy", "philosophy-of-language")
    edge("analytic-philosophy", "philosophy-of-mind")
    edge("modern-philosophy-overview", "feminist-philosophy")
    edge("modern-philosophy-overview", "postcolonial-philosophy")
    edge("modern-philosophy-overview", "critical-theory")
    edge("phenomenology", "hermeneutics", "influences", 0.7)
    edge("modern-philosophy-overview", "structuralism")
    edge("structuralism", "postmodernism", "influences", 0.6)
    edge("analytic-philosophy", "philosophy-of-science")
    edge("modern-philosophy-overview", "philosophy-of-technology")
    edge("modern-philosophy-overview", "process-philosophy")
    edge("modern-philosophy-overview", "new-confucianism")
    edge("philosophy-of-mind", "philosophy-of-ai", "related", 0.7)

    # ── cross-subdomain edges ──
    # ancient ↔ epistemology
    edge("socrates", "knowledge-definition", "influences", 0.7)
    edge("plato", "rationalism", "influences", 0.7)
    edge("aristotle", "empiricism", "influences", 0.6)
    edge("skepticism-ancient", "skepticism", "influences", 0.8)
    # ancient ↔ ethics
    edge("aristotle-ethics", "virtue-ethics", "influences", 0.8)
    edge("confucius", "confucian-ethics", "influences", 0.8)
    edge("buddhist-philosophy", "buddhist-ethics", "influences", 0.8)
    edge("epicurus", "utilitarianism", "influences", 0.5)
    edge("stoicism", "deontology", "influences", 0.5)
    # ancient ↔ metaphysics
    edge("plato", "idealism", "influences", 0.7)
    edge("aristotle", "substance-metaphysics", "influences", 0.7)
    edge("parmenides", "being-existence", "influences", 0.7)
    edge("laozi", "chinese-metaphysics", "influences", 0.7)
    # ancient ↔ logic
    edge("aristotle", "deductive-reasoning", "influences", 0.8)
    edge("socrates", "dialectic", "influences", 0.8)
    # ancient ↔ political
    edge("plato-republic", "political-philosophy-overview", "influences", 0.6)
    edge("confucius", "chinese-political-phil", "influences", 0.7)
    # ancient ↔ aesthetics
    edge("plato", "mimesis", "influences", 0.7)
    edge("aristotle", "tragedy-philosophy", "influences", 0.8)
    # epistemology ↔ modern
    edge("kant-epistemology", "phenomenology", "influences", 0.6)
    edge("empiricism", "analytic-philosophy", "influences", 0.6)
    edge("pragmatist-epistemology", "pragmatism", "influences", 0.8)
    edge("falsificationism", "philosophy-of-science", "influences", 0.7)
    # metaphysics ↔ modern
    edge("mind-body-problem", "philosophy-of-mind", "influences", 0.8)
    edge("free-will", "existentialism", "related", 0.6)
    # ethics ↔ political
    edge("justice-concept", "rawls-justice", "influences", 0.8)
    edge("human-rights-phil", "rights-theory", "related", 0.8)
    edge("utilitarianism", "democracy-theory", "related", 0.5)
    # logic ↔ epistemology
    edge("deductive-reasoning", "rationalism", "related", 0.5)
    edge("inductive-reasoning", "induction-problem", "related", 0.7)
    edge("critical-thinking", "scientific-method-phil", "related", 0.6)
    # logic ↔ modern
    edge("propositional-logic", "analytic-philosophy", "influences", 0.6)
    edge("philosophy-of-logic", "wittgenstein", "related", 0.6)
    edge("modal-logic", "possible-worlds", "related", 0.7)
    # aesthetics ↔ modern
    edge("aesthetic-judgment", "phenomenology", "related", 0.5)
    edge("photography-aesthetics", "critical-theory", "related", 0.5)
    # ethics ↔ modern
    edge("tech-ethics", "philosophy-of-ai", "related", 0.7)
    edge("moral-relativism", "postmodernism", "related", 0.5)
    # political ↔ modern
    edge("marxism", "critical-theory", "influences", 0.7)
    edge("feminism-political", "feminist-philosophy", "related", 0.8)
    edge("socialism", "existentialism", "related", 0.4)

    return edges


def main():
    concepts = []
    for (cid, name, desc, sub, diff, mins, ctype, tags, ms) in CONCEPTS_RAW:
        concepts.append({
            "id": cid,
            "name": name,
            "description": desc,
            "subdomain_id": sub,
            "domain_id": "philosophy",
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

    print(f"✅ Generated philosophy seed graph:")
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
