#!/usr/bin/env python3
"""Generate Psychology knowledge sphere seed graph.

8 subdomains, ~180 concepts covering cognitive to clinical psychology.
"""
import json
from datetime import datetime, timezone

NOW = datetime.now(timezone.utc).isoformat()

DOMAIN = {
    "id": "psychology",
    "name": "心理学",
    "description": "从认知心理学到临床应用的系统知识体系",
    "icon": "💜",
    "color": "#a855f7",
}

SUBDOMAINS = [
    {"id": "cognitive-psychology",      "name": "认知心理学",     "order": 1},
    {"id": "developmental-psychology",  "name": "发展心理学",     "order": 2},
    {"id": "social-psychology",         "name": "社会心理学",     "order": 3},
    {"id": "clinical-psychology",       "name": "临床心理学",     "order": 4},
    {"id": "behavioral-psychology",     "name": "行为心理学",     "order": 5},
    {"id": "biological-psychology",     "name": "生物心理学",     "order": 6},
    {"id": "personality-psychology",    "name": "人格心理学",     "order": 7},
    {"id": "research-methods",          "name": "研究方法",       "order": 8},
]

# (id, name, description, subdomain_id, difficulty, minutes, content_type, tags, is_milestone)
CONCEPTS_RAW = [
    # ── cognitive-psychology (25 concepts) ──
    ("cognitive-psychology-overview", "认知心理学概述",       "认知心理学的定义、历史与研究范畴",                   "cognitive-psychology", 1, 20, "theory", ["基础"], True),
    ("perception",                   "知觉",                 "感觉信息的组织与解释过程",                           "cognitive-psychology", 1, 25, "theory", ["基础"], False),
    ("attention",                    "注意",                 "选择性注意、分配注意与注意力模型",                   "cognitive-psychology", 2, 25, "theory", ["核心"], True),
    ("selective-attention",          "选择性注意",           "鸡尾酒会效应、过滤器模型与衰减模型",                 "cognitive-psychology", 2, 25, "theory", ["注意"], False),
    ("working-memory",               "工作记忆",             "Baddeley工作记忆模型与认知容量限制",                 "cognitive-psychology", 2, 30, "theory", ["记忆"], True),
    ("long-term-memory",             "长期记忆",             "陈述性记忆与程序性记忆的编码与提取",                 "cognitive-psychology", 2, 30, "theory", ["记忆"], False),
    ("memory-encoding",              "记忆编码",             "深层加工、精细化加工与编码特异性原则",               "cognitive-psychology", 2, 25, "theory", ["记忆"], False),
    ("forgetting",                   "遗忘",                 "遗忘曲线、干扰理论与提取失败",                       "cognitive-psychology", 2, 25, "theory", ["记忆"], False),
    ("language-cognition",           "语言与认知",           "语言习得、语法加工与Sapir-Whorf假说",               "cognitive-psychology", 3, 30, "theory", ["语言"], False),
    ("problem-solving",              "问题解决",             "算法与启发式、功能固着与顿悟",                       "cognitive-psychology", 2, 25, "theory", ["思维"], True),
    ("decision-making",              "决策",                 "理性决策模型、有限理性与前景理论",                   "cognitive-psychology", 3, 30, "theory", ["思维"], False),
    ("cognitive-biases",             "认知偏差",             "确认偏差、锚定效应、可得性启发式等",                 "cognitive-psychology", 2, 25, "theory", ["思维"], False),
    ("heuristics",                   "启发式",               "代表性启发式、可得性启发式与锚定",                   "cognitive-psychology", 2, 25, "theory", ["思维"], False),
    ("metacognition",                "元认知",               "对自身认知过程的监控与调节",                         "cognitive-psychology", 3, 25, "theory", ["高级"], False),
    ("schema-theory",                "图式理论",             "图式的形成、同化与顺应过程",                         "cognitive-psychology", 2, 25, "theory", ["知识"], False),
    ("mental-models",                "心理模型",             "心理表征与推理中的模型构建",                         "cognitive-psychology", 3, 25, "theory", ["思维"], False),
    ("cognitive-load",               "认知负荷",             "内在、外在与关联认知负荷理论",                       "cognitive-psychology", 2, 25, "theory", ["学习"], False),
    ("expertise-development",        "专家技能发展",         "从新手到专家的认知变化与刻意练习",                   "cognitive-psychology", 3, 30, "theory", ["发展"], False),
    ("creativity",                   "创造力",               "发散思维、聚合思维与创造力的认知基础",               "cognitive-psychology", 3, 25, "theory", ["高级"], False),
    ("embodied-cognition",           "具身认知",             "身体经验对认知加工的影响",                           "cognitive-psychology", 3, 25, "theory", ["前沿"], False),
    ("cognitive-development-piaget", "皮亚杰认知发展论",     "感觉运动期到形式运算期的四阶段理论",                 "cognitive-psychology", 2, 30, "theory", ["发展"], True),
    ("information-processing",       "信息加工理论",         "将心智比作计算机的信息加工框架",                     "cognitive-psychology", 2, 25, "theory", ["理论"], False),
    ("dual-process-theory",          "双加工理论",           "系统1(快速直觉)与系统2(慢速分析)思维模式",           "cognitive-psychology", 2, 25, "theory", ["理论"], False),
    ("intelligence-theories",        "智力理论",             "Spearman g因素、多元智力与三元智力理论",             "cognitive-psychology", 3, 30, "theory", ["智力"], False),
    ("emotional-intelligence",       "情绪智力",             "情绪识别、理解、管理与运用能力",                     "cognitive-psychology", 2, 25, "theory", ["情绪"], False),

    # ── developmental-psychology (23 concepts) ──
    ("developmental-overview",       "发展心理学概述",       "毕生发展观与发展心理学的核心议题",                   "developmental-psychology", 1, 20, "theory", ["基础"], True),
    ("nature-nurture",               "先天与后天",           "遗传与环境的交互作用",                               "developmental-psychology", 1, 25, "theory", ["核心"], False),
    ("prenatal-development",         "产前发展",             "从受精到出生的发展阶段与关键期",                     "developmental-psychology", 2, 25, "theory", ["婴幼儿"], False),
    ("infant-development",           "婴儿期发展",           "感知觉发展、运动发展与早期社会化",                   "developmental-psychology", 2, 25, "theory", ["婴幼儿"], False),
    ("attachment-theory",            "依恋理论",             "Bowlby依恋理论与Ainsworth陌生情境实验",              "developmental-psychology", 2, 30, "theory", ["核心"], True),
    ("language-development",         "语言发展",             "从咿呀学语到复杂语法的语言习得过程",                 "developmental-psychology", 2, 25, "theory", ["语言"], False),
    ("moral-development",            "道德发展",             "Kohlberg道德发展阶段理论与道德推理",                 "developmental-psychology", 3, 30, "theory", ["道德"], True),
    ("erikson-stages",               "Erikson心理社会发展",  "从信任vs不信任到自我整合vs绝望的八阶段",             "developmental-psychology", 2, 30, "theory", ["核心"], True),
    ("adolescent-development",       "青少年期发展",         "青春期身体变化、同一性危机与同伴关系",               "developmental-psychology", 2, 25, "theory", ["青少年"], False),
    ("identity-formation",           "同一性形成",           "Marcia同一性状态理论与自我探索",                     "developmental-psychology", 3, 25, "theory", ["青少年"], False),
    ("adult-development",            "成年期发展",           "亲密关系、职业发展与中年转变",                       "developmental-psychology", 2, 25, "theory", ["成年"], False),
    ("aging-psychology",             "老年心理学",           "认知老化、智慧发展与成功老龄化",                     "developmental-psychology", 3, 25, "theory", ["老年"], False),
    ("vygotsky-theory",              "维果茨基理论",         "最近发展区、支架式教学与社会文化理论",               "developmental-psychology", 2, 30, "theory", ["核心"], False),
    ("temperament",                  "气质",                 "气质的生物基础与Thomas-Chess气质类型",               "developmental-psychology", 2, 25, "theory", ["个体差异"], False),
    ("parenting-styles",             "教养方式",             "权威型、专制型、放任型与忽视型教养",                 "developmental-psychology", 2, 25, "theory", ["家庭"], False),
    ("play-development",             "游戏与发展",           "游戏的类型及其在认知与社会发展中的作用",             "developmental-psychology", 2, 20, "theory", ["儿童"], False),
    ("theory-of-mind",               "心理理论",             "理解他人心理状态的能力发展",                         "developmental-psychology", 3, 25, "theory", ["认知"], False),
    ("gender-development",           "性别发展",             "性别认同、性别角色与性别图式理论",                   "developmental-psychology", 2, 25, "theory", ["社会化"], False),
    ("resilience",                   "心理韧性",             "面对逆境的积极适应与保护因素",                       "developmental-psychology", 3, 25, "theory", ["积极"], False),
    ("critical-periods",             "关键期与敏感期",       "发展中的关键期概念与可塑性",                         "developmental-psychology", 2, 25, "theory", ["发展"], False),
    ("cognitive-aging",              "认知老化",             "晶体智力vs流体智力与年龄相关认知变化",               "developmental-psychology", 3, 25, "theory", ["老年"], False),
    ("developmental-psychopathology","发展精神病理学",       "发展偏差的风险因素与保护因素",                       "developmental-psychology", 3, 30, "theory", ["临床"], False),
    ("socioemotional-development",   "社会情感发展",         "情绪调节、同理心与社会能力的发展",                   "developmental-psychology", 2, 25, "theory", ["社会化"], False),

    # ── social-psychology (23 concepts) ──
    ("social-psychology-overview",   "社会心理学概述",       "社会心理学的定义、历史与核心研究领域",               "social-psychology", 1, 20, "theory", ["基础"], True),
    ("social-cognition",             "社会认知",             "印象形成、社会图式与归因过程",                       "social-psychology", 2, 25, "theory", ["认知"], False),
    ("attribution-theory",           "归因理论",             "内部归因vs外部归因、基本归因错误",                   "social-psychology", 2, 25, "theory", ["核心"], True),
    ("attitudes",                    "态度",                 "态度的形成、结构与态度-行为关系",                    "social-psychology", 2, 25, "theory", ["态度"], False),
    ("persuasion",                   "说服",                 "中心路径vs外周路径、说服的六原则",                   "social-psychology", 2, 25, "theory", ["影响"], True),
    ("cognitive-dissonance",         "认知失调",             "Festinger认知失调理论与自我辩解",                    "social-psychology", 2, 25, "theory", ["核心"], True),
    ("conformity",                   "从众",                 "Asch从众实验与信息性/规范性社会影响",                "social-psychology", 2, 25, "theory", ["群体"], False),
    ("obedience",                    "服从",                 "Milgram服从实验与权威影响",                          "social-psychology", 2, 25, "theory", ["群体"], False),
    ("group-dynamics",               "群体动力学",           "群体极化、团体思维与社会促进/抑制",                  "social-psychology", 3, 30, "theory", ["群体"], False),
    ("social-identity",              "社会认同",             "Tajfel社会认同理论与内群体偏好",                     "social-psychology", 3, 25, "theory", ["自我"], False),
    ("prejudice-discrimination",     "偏见与歧视",           "偏见的认知、情感与行为成分及其减少策略",             "social-psychology", 3, 30, "theory", ["群际"], True),
    ("stereotypes",                  "刻板印象",             "刻板印象的形成、维持与刻板印象威胁",                 "social-psychology", 2, 25, "theory", ["群际"], False),
    ("aggression",                   "攻击行为",             "攻击的生物、心理与社会文化解释",                     "social-psychology", 3, 25, "theory", ["行为"], False),
    ("prosocial-behavior",           "亲社会行为",           "利他主义、旁观者效应与助人行为的决策模型",           "social-psychology", 2, 25, "theory", ["行为"], False),
    ("interpersonal-attraction",     "人际吸引",             "亲近性、相似性、外貌与互惠在人际吸引中的作用",       "social-psychology", 2, 25, "theory", ["关系"], False),
    ("love-psychology",              "爱情心理学",           "Sternberg爱情三角理论与依恋风格",                    "social-psychology", 3, 25, "theory", ["关系"], False),
    ("social-influence",             "社会影响",             "顺从、服从、从众的心理机制",                         "social-psychology", 2, 25, "theory", ["影响"], False),
    ("self-concept",                 "自我概念",             "自我意识、自尊与自我效能感",                         "social-psychology", 2, 25, "theory", ["自我"], False),
    ("self-serving-bias",            "自利偏差",             "成功归因于自己、失败归因于外界的倾向",               "social-psychology", 2, 20, "theory", ["偏差"], False),
    ("bystander-effect",             "旁观者效应",           "责任分散与Kitty Genovese案例",                      "social-psychology", 2, 20, "theory", ["经典"], False),
    ("cultural-psychology",          "文化心理学",           "个人主义vs集体主义文化差异对心理的影响",             "social-psychology", 3, 30, "theory", ["文化"], False),
    ("social-media-psychology",      "社交媒体心理学",       "社交媒体对自我认同、社会比较与幸福感的影响",         "social-psychology", 3, 25, "theory", ["前沿"], False),
    ("leadership-psychology",        "领导力心理学",         "领导风格、变革型领导与情境领导理论",                 "social-psychology", 3, 25, "theory", ["应用"], False),

    # ── clinical-psychology (23 concepts) ──
    ("clinical-overview",            "临床心理学概述",       "临床心理学的定义、角色与伦理原则",                   "clinical-psychology", 1, 20, "theory", ["基础"], True),
    ("psychopathology",              "精神病理学",           "心理异常的定义标准与分类系统(DSM/ICD)",              "clinical-psychology", 2, 30, "theory", ["核心"], True),
    ("anxiety-disorders",            "焦虑障碍",             "广泛性焦虑、恐惧症、社交焦虑与惊恐障碍",            "clinical-psychology", 2, 30, "theory", ["障碍"], True),
    ("depressive-disorders",         "抑郁障碍",             "重度抑郁症的症状、病因与认知三联征",                 "clinical-psychology", 2, 30, "theory", ["障碍"], True),
    ("bipolar-disorder",             "双相障碍",             "躁狂期与抑郁期的交替及其神经生物学基础",             "clinical-psychology", 3, 25, "theory", ["障碍"], False),
    ("schizophrenia",                "精神分裂症",           "阳性症状、阴性症状与多巴胺假说",                     "clinical-psychology", 3, 30, "theory", ["障碍"], False),
    ("personality-disorders",        "人格障碍",             "A/B/C三类人格障碍的特征与鉴别",                      "clinical-psychology", 3, 30, "theory", ["障碍"], False),
    ("ptsd",                         "创伤后应激障碍",       "PTSD的症状、风险因素与创伤记忆加工",                 "clinical-psychology", 3, 25, "theory", ["创伤"], False),
    ("ocd",                          "强迫症",               "强迫思维、强迫行为与认知行为模型",                   "clinical-psychology", 3, 25, "theory", ["障碍"], False),
    ("eating-disorders",             "进食障碍",             "神经性厌食、贪食症与暴食障碍",                       "clinical-psychology", 3, 25, "theory", ["障碍"], False),
    ("substance-use-disorders",      "物质使用障碍",         "成瘾的生物心理社会模型与阶段变化模型",               "clinical-psychology", 3, 30, "theory", ["成瘾"], False),
    ("psychological-assessment",     "心理评估",             "临床访谈、心理测验与行为观察方法",                   "clinical-psychology", 2, 25, "practice", ["评估"], False),
    ("psychotherapy-overview",       "心理治疗概述",         "心理治疗的流派、共同因素与循证实践",                 "clinical-psychology", 2, 25, "theory", ["治疗"], True),
    ("cbt",                          "认知行为疗法",         "CBT的核心原理、认知重构与行为实验",                  "clinical-psychology", 3, 30, "practice", ["治疗"], True),
    ("psychodynamic-therapy",        "心理动力学治疗",       "自由联想、移情分析与无意识探索",                     "clinical-psychology", 3, 30, "theory", ["治疗"], False),
    ("humanistic-therapy",           "人本主义治疗",         "来访者中心疗法、无条件积极关注与同理心",             "clinical-psychology", 3, 25, "theory", ["治疗"], False),
    ("group-therapy",                "团体治疗",             "团体治疗的疗效因子与常见形式",                       "clinical-psychology", 3, 25, "practice", ["治疗"], False),
    ("crisis-intervention",          "危机干预",             "心理危机的识别、评估与短期干预技术",                 "clinical-psychology", 3, 25, "practice", ["应用"], False),
    ("child-clinical",               "儿童临床心理学",       "ADHD、自闭谱系、学习障碍的评估与干预",              "clinical-psychology", 3, 30, "theory", ["发展"], False),
    ("positive-psychology",          "积极心理学",           "幸福感、心流、品格优势与意义感",                     "clinical-psychology", 2, 25, "theory", ["积极"], False),
    ("mindfulness",                  "正念",                 "正念的心理学基础与正念减压疗法(MBSR)",               "clinical-psychology", 2, 25, "practice", ["积极"], False),
    ("therapeutic-relationship",     "治疗关系",             "治疗联盟、共情与治疗效果的关系",                     "clinical-psychology", 2, 25, "theory", ["治疗"], False),
    ("evidence-based-practice",      "循证实践",             "将研究证据、临床专业与来访者需求结合",               "clinical-psychology", 3, 25, "theory", ["方法"], False),

    # ── behavioral-psychology (22 concepts) ──
    ("behavioral-overview",          "行为心理学概述",       "行为主义的哲学基础与核心假设",                       "behavioral-psychology", 1, 20, "theory", ["基础"], True),
    ("classical-conditioning",       "经典条件反射",         "巴甫洛夫实验、习得、消退与自发恢复",                 "behavioral-psychology", 2, 25, "theory", ["核心"], True),
    ("operant-conditioning",         "操作性条件反射",       "Skinner箱实验、强化与惩罚的四种类型",                "behavioral-psychology", 2, 30, "theory", ["核心"], True),
    ("reinforcement-schedules",      "强化程式",             "固定/变化比率与间隔强化程式的行为效应",              "behavioral-psychology", 2, 25, "theory", ["学习"], False),
    ("punishment",                   "惩罚",                 "正惩罚与负惩罚的原理及其有效运用条件",               "behavioral-psychology", 2, 25, "theory", ["学习"], False),
    ("shaping",                      "行为塑造",             "通过逐步接近法建立复杂行为",                         "behavioral-psychology", 2, 20, "theory", ["技术"], False),
    ("observational-learning",       "观察学习",             "Bandura社会学习理论与Bobo玩偶实验",                 "behavioral-psychology", 2, 25, "theory", ["核心"], True),
    ("self-efficacy",                "自我效能感",           "Bandura自我效能理论与效能感的四大来源",              "behavioral-psychology", 2, 25, "theory", ["核心"], False),
    ("stimulus-generalization",      "刺激泛化",             "条件反应向相似刺激的迁移",                           "behavioral-psychology", 2, 20, "theory", ["学习"], False),
    ("stimulus-discrimination",      "刺激辨别",             "区分不同刺激的能力发展",                             "behavioral-psychology", 2, 20, "theory", ["学习"], False),
    ("extinction",                   "消退",                 "条件反应的消退过程与自发恢复",                       "behavioral-psychology", 2, 20, "theory", ["学习"], False),
    ("behavior-modification",        "行为矫正",             "基于学习原理的行为改变技术",                         "behavioral-psychology", 3, 25, "practice", ["应用"], True),
    ("token-economy",                "代币经济",             "代币制在教育与临床中的应用",                         "behavioral-psychology", 3, 20, "practice", ["应用"], False),
    ("systematic-desensitization",   "系统脱敏",             "Wolpe的系统脱敏法与放松训练在恐惧治疗中的应用",      "behavioral-psychology", 3, 25, "practice", ["治疗"], False),
    ("aversion-therapy",             "厌恶疗法",             "将不良行为与厌恶刺激配对的治疗方法",                 "behavioral-psychology", 3, 20, "theory", ["治疗"], False),
    ("biofeedback",                  "生物反馈",             "通过仪器反馈学习控制生理过程",                       "behavioral-psychology", 3, 25, "practice", ["技术"], False),
    ("applied-behavior-analysis",    "应用行为分析",         "ABA在自闭症与特殊教育中的应用",                      "behavioral-psychology", 3, 30, "practice", ["应用"], False),
    ("habit-formation",              "习惯形成",             "习惯回路(提示-惯常行为-奖赏)与习惯改变策略",         "behavioral-psychology", 2, 25, "theory", ["日常"], False),
    ("learned-helplessness",         "习得性无助",           "Seligman习得性无助实验与抑郁的联系",                 "behavioral-psychology", 3, 25, "theory", ["经典"], False),
    ("latent-learning",              "潜伏学习",             "Tolman认知地图实验与非强化条件下的学习",             "behavioral-psychology", 3, 20, "theory", ["认知"], False),
    ("motivation-behavioral",        "行为动机理论",         "驱力减少理论、激励理论与行为经济学视角",             "behavioral-psychology", 2, 25, "theory", ["动机"], False),
    ("behavioral-economics",         "行为经济学",           "心理学与经济决策: 框架效应、禀赋效应",               "behavioral-psychology", 3, 25, "theory", ["应用"], False),

    # ── biological-psychology (22 concepts) ──
    ("biological-overview",          "生物心理学概述",       "生物心理学的研究范畴与心脑关系问题",                 "biological-psychology", 1, 20, "theory", ["基础"], True),
    ("neuron-structure",             "神经元结构",           "神经元的结构、动作电位与突触传递",                   "biological-psychology", 2, 30, "theory", ["神经"], True),
    ("neurotransmitters",            "神经递质",             "多巴胺、5-HT、GABA等主要递质的功能",                "biological-psychology", 2, 30, "theory", ["神经"], True),
    ("brain-structure",              "大脑结构",             "大脑皮层四叶、边缘系统与脑干功能",                   "biological-psychology", 2, 30, "theory", ["核心"], True),
    ("cerebral-lateralization",      "大脑偏侧化",           "左右半球功能特化与胼胝体",                           "biological-psychology", 2, 25, "theory", ["大脑"], False),
    ("endocrine-system",             "内分泌系统",           "激素对情绪与行为的调节作用",                         "biological-psychology", 2, 25, "theory", ["生理"], False),
    ("autonomic-nervous-system",     "自主神经系统",         "交感神经与副交感神经在应激反应中的作用",             "biological-psychology", 2, 25, "theory", ["生理"], False),
    ("neuroplasticity",              "神经可塑性",           "突触可塑性、关键期与经验依赖的脑发展",               "biological-psychology", 3, 25, "theory", ["前沿"], True),
    ("sleep-psychology",             "睡眠心理学",           "睡眠阶段、睡眠功能与睡眠障碍",                       "biological-psychology", 2, 25, "theory", ["节律"], False),
    ("stress-physiology",            "应激生理学",           "HPA轴、皮质醇与应激的生理机制",                     "biological-psychology", 2, 30, "theory", ["应激"], False),
    ("psychopharmacology",           "精神药理学",           "抗抑郁药、抗焦虑药与抗精神病药的作用机制",           "biological-psychology", 3, 30, "theory", ["药物"], False),
    ("brain-imaging",                "脑成像技术",           "fMRI、PET、EEG等脑成像方法比较",                    "biological-psychology", 3, 25, "theory", ["技术"], False),
    ("genetics-behavior",            "遗传与行为",           "行为遗传学、双生子研究与基因-环境交互",              "biological-psychology", 3, 30, "theory", ["遗传"], False),
    ("emotion-neuroscience",         "情绪神经科学",         "杏仁核、前额叶在情绪加工中的角色",                   "biological-psychology", 3, 25, "theory", ["情绪"], False),
    ("pain-psychology",              "疼痛心理学",           "门控理论与疼痛的心理调节",                           "biological-psychology", 3, 25, "theory", ["感觉"], False),
    ("hunger-eating",                "饥饿与进食",           "下丘脑对进食行为的调控与肥胖的生理心理机制",         "biological-psychology", 2, 25, "theory", ["动机"], False),
    ("sexual-behavior-biology",      "性行为的生物基础",     "性激素、性取向的生物学解释",                         "biological-psychology", 3, 25, "theory", ["动机"], False),
    ("consciousness",                "意识",                 "意识的神经关联、变更意识状态与注意的角色",            "biological-psychology", 3, 30, "theory", ["高级"], False),
    ("evolutionary-psychology",      "进化心理学",           "适应性行为、自然选择与人类心理的进化解释",           "biological-psychology", 3, 30, "theory", ["进化"], False),
    ("comparative-psychology",       "比较心理学",           "跨物种行为比较与动物认知研究",                       "biological-psychology", 3, 25, "theory", ["进化"], False),
    ("epigenetics-behavior",         "表观遗传与行为",       "环境经验对基因表达的影响与跨代传递",                 "biological-psychology", 4, 25, "theory", ["前沿"], False),
    ("psychoneuroimmunology",        "心理神经免疫学",       "心理因素对免疫系统的影响",                           "biological-psychology", 4, 25, "theory", ["前沿"], False),

    # ── personality-psychology (22 concepts) ──
    ("personality-overview",         "人格心理学概述",       "人格的定义、人格理论的主要流派",                     "personality-psychology", 1, 20, "theory", ["基础"], True),
    ("big-five",                     "大五人格模型",         "开放性、尽责性、外向性、宜人性、神经质",             "personality-psychology", 2, 30, "theory", ["核心"], True),
    ("trait-theory",                 "特质理论",             "Allport、Cattell与Eysenck的特质理论比较",            "personality-psychology", 2, 25, "theory", ["特质"], False),
    ("psychoanalytic-theory",        "精神分析理论",         "Freud的人格结构(本我/自我/超我)与无意识",            "personality-psychology", 2, 30, "theory", ["核心"], True),
    ("defense-mechanisms",           "防御机制",             "压抑、投射、合理化、升华等防御机制",                 "personality-psychology", 2, 25, "theory", ["精神分析"], False),
    ("psychosexual-stages",          "性心理发展阶段",       "Freud口唇期到生殖期的人格发展理论",                  "personality-psychology", 2, 25, "theory", ["精神分析"], False),
    ("jung-theory",                  "荣格分析心理学",       "集体无意识、原型与个体化过程",                       "personality-psychology", 3, 30, "theory", ["精神分析"], False),
    ("humanistic-personality",       "人本主义人格理论",     "Rogers自我概念、Maslow需求层次与自我实现",           "personality-psychology", 2, 25, "theory", ["核心"], True),
    ("maslow-hierarchy",             "马斯洛需求层次",       "生理→安全→归属→尊重→自我实现的五层需求",             "personality-psychology", 2, 25, "theory", ["动机"], True),
    ("social-cognitive-personality", "社会认知人格理论",     "Bandura交互决定论与Mischel认知情感系统",             "personality-psychology", 3, 25, "theory", ["理论"], False),
    ("personality-assessment",       "人格评估",             "自陈量表、投射测验与行为评估方法",                   "personality-psychology", 2, 25, "practice", ["评估"], False),
    ("mbti",                         "MBTI人格类型",         "Myers-Briggs类型指标的四维度与16类型",               "personality-psychology", 2, 25, "theory", ["类型"], False),
    ("locus-of-control",             "控制点",               "Rotter内外控理论及其对行为的影响",                   "personality-psychology", 2, 20, "theory", ["认知"], False),
    ("self-actualization",           "自我实现",             "自我实现者的特征与高峰体验",                         "personality-psychology", 3, 25, "theory", ["人本"], False),
    ("personality-stability",        "人格稳定性",           "人格的跨时间稳定性与跨情境一致性争论",               "personality-psychology", 3, 25, "theory", ["争论"], False),
    ("narcissism",                   "自恋",                 "健康自恋vs病理性自恋的心理学分析",                   "personality-psychology", 3, 25, "theory", ["人格"], False),
    ("attachment-adult",             "成人依恋",             "成人依恋风格与亲密关系模式",                         "personality-psychology", 3, 25, "theory", ["关系"], False),
    ("personality-culture",          "人格与文化",           "文化对人格特质表达与评估的影响",                     "personality-psychology", 3, 25, "theory", ["文化"], False),
    ("dark-triad",                   "黑暗三人格",           "自恋、马基雅维利主义与精神病态的人格特征",            "personality-psychology", 3, 25, "theory", ["人格"], False),
    ("growth-mindset",               "成长型思维",           "Dweck固定思维vs成长思维对成就的影响",                "personality-psychology", 2, 25, "theory", ["积极"], False),
    ("grit",                         "坚毅",                 "Duckworth坚毅理论与长期目标的坚持",                  "personality-psychology", 2, 20, "theory", ["积极"], False),
    ("emotional-regulation",         "情绪调节",             "情绪调节策略与Gross过程模型",                        "personality-psychology", 2, 25, "theory", ["情绪"], False),

    # ── research-methods (23 concepts) ──
    ("research-methods-overview",    "研究方法概述",         "心理学研究方法的分类与科学方法论",                   "research-methods", 1, 20, "theory", ["基础"], True),
    ("scientific-method",            "科学方法",             "假设检验、可证伪性与经验主义",                       "research-methods", 1, 20, "theory", ["基础"], False),
    ("experimental-design",          "实验设计",             "自变量、因变量、控制变量与实验范式",                 "research-methods", 2, 30, "theory", ["核心"], True),
    ("random-assignment",            "随机分配",             "随机分配的原理与混淆变量的控制",                     "research-methods", 2, 20, "theory", ["实验"], False),
    ("correlational-research",       "相关研究",             "相关系数、相关不等于因果与第三变量问题",             "research-methods", 2, 25, "theory", ["核心"], True),
    ("survey-methods",               "调查法",               "问卷设计、抽样方法与自陈报告的局限",                 "research-methods", 2, 25, "practice", ["方法"], False),
    ("observational-methods",        "观察法",               "自然观察与实验室观察的优缺点",                       "research-methods", 2, 25, "practice", ["方法"], False),
    ("case-study-method",            "个案研究法",           "深度个案分析的价值与局限性",                         "research-methods", 2, 20, "theory", ["方法"], False),
    ("longitudinal-study",           "纵向研究",             "追踪研究设计与发展变化的测量",                       "research-methods", 3, 25, "theory", ["设计"], False),
    ("cross-sectional-study",        "横断研究",             "不同年龄组同时比较的设计与局限",                     "research-methods", 2, 20, "theory", ["设计"], False),
    ("descriptive-statistics",       "描述统计",             "均值、中位数、标准差与数据分布",                     "research-methods", 2, 25, "theory", ["统计"], True),
    ("inferential-statistics",       "推断统计",             "t检验、方差分析与统计显著性",                        "research-methods", 3, 30, "theory", ["统计"], False),
    ("effect-size",                  "效应量",               "Cohen's d、r与实际意义vs统计显著性",                 "research-methods", 3, 25, "theory", ["统计"], False),
    ("reliability-validity",         "信度与效度",           "内部一致性、重测信度、结构效度与内容效度",           "research-methods", 2, 25, "theory", ["测量"], True),
    ("sampling-methods",             "抽样方法",             "概率抽样与非概率抽样的比较",                         "research-methods", 2, 25, "theory", ["方法"], False),
    ("ethics-research",              "研究伦理",             "知情同意、保密性、欺骗与动物研究伦理",               "research-methods", 2, 25, "theory", ["伦理"], True),
    ("replication-crisis",           "可重复性危机",         "心理学可重复性问题与开放科学运动",                   "research-methods", 3, 25, "theory", ["前沿"], False),
    ("meta-analysis",                "元分析",               "效应量综合与跨研究一般性结论",                       "research-methods", 3, 30, "theory", ["高级"], False),
    ("qualitative-methods",          "质性研究方法",         "主题分析、扎根理论与现象学方法",                     "research-methods", 3, 25, "theory", ["方法"], False),
    ("operational-definition",       "操作性定义",           "将抽象概念转化为可观测可测量的操作定义",             "research-methods", 2, 20, "theory", ["基础"], False),
    ("internal-external-validity",   "内部效度与外部效度",   "实验控制精确性vs结果可推广性的权衡",                 "research-methods", 3, 25, "theory", ["效度"], False),
    ("apa-style",                    "APA格式",             "APA论文写作格式与引用规范",                           "research-methods", 2, 20, "practice", ["写作"], False),
    ("power-analysis",               "统计功效分析",         "样本量计算、统计功效与Type I/II错误",                "research-methods", 3, 30, "theory", ["统计"], False),
]


def build_edges(concepts):
    """Build prerequisite edges between concepts."""
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

    # ── cognitive-psychology ──
    edge("cognitive-psychology-overview", "perception")
    edge("cognitive-psychology-overview", "attention")
    edge("attention", "selective-attention")
    edge("perception", "working-memory", "related", 0.6)
    edge("attention", "working-memory")
    edge("working-memory", "long-term-memory")
    edge("long-term-memory", "memory-encoding")
    edge("long-term-memory", "forgetting")
    edge("working-memory", "cognitive-load")
    edge("cognitive-psychology-overview", "language-cognition")
    edge("cognitive-psychology-overview", "problem-solving")
    edge("problem-solving", "decision-making")
    edge("decision-making", "cognitive-biases")
    edge("decision-making", "heuristics")
    edge("cognitive-biases", "heuristics", "related", 0.7)
    edge("long-term-memory", "schema-theory")
    edge("schema-theory", "mental-models")
    edge("problem-solving", "metacognition")
    edge("metacognition", "expertise-development")
    edge("problem-solving", "creativity")
    edge("cognitive-psychology-overview", "information-processing")
    edge("information-processing", "dual-process-theory")
    edge("dual-process-theory", "heuristics", "related", 0.6)
    edge("cognitive-psychology-overview", "intelligence-theories")
    edge("intelligence-theories", "emotional-intelligence")
    edge("cognitive-psychology-overview", "embodied-cognition")
    edge("schema-theory", "cognitive-development-piaget")

    # ── developmental-psychology ──
    edge("developmental-overview", "nature-nurture")
    edge("developmental-overview", "prenatal-development")
    edge("prenatal-development", "infant-development")
    edge("infant-development", "attachment-theory")
    edge("infant-development", "language-development")
    edge("developmental-overview", "erikson-stages")
    edge("attachment-theory", "erikson-stages", "related", 0.6)
    edge("erikson-stages", "adolescent-development")
    edge("adolescent-development", "identity-formation")
    edge("erikson-stages", "adult-development")
    edge("adult-development", "aging-psychology")
    edge("developmental-overview", "moral-development")
    edge("cognitive-development-piaget", "vygotsky-theory", "related", 0.7)
    edge("infant-development", "temperament")
    edge("attachment-theory", "parenting-styles", "related", 0.6)
    edge("infant-development", "play-development")
    edge("language-development", "theory-of-mind")
    edge("developmental-overview", "gender-development")
    edge("developmental-overview", "resilience")
    edge("developmental-overview", "critical-periods")
    edge("aging-psychology", "cognitive-aging")
    edge("developmental-overview", "developmental-psychopathology")
    edge("infant-development", "socioemotional-development")

    # ── social-psychology ──
    edge("social-psychology-overview", "social-cognition")
    edge("social-cognition", "attribution-theory")
    edge("social-psychology-overview", "attitudes")
    edge("attitudes", "persuasion")
    edge("attitudes", "cognitive-dissonance")
    edge("social-psychology-overview", "conformity")
    edge("conformity", "obedience")
    edge("social-psychology-overview", "group-dynamics")
    edge("group-dynamics", "social-identity")
    edge("social-identity", "prejudice-discrimination")
    edge("social-cognition", "stereotypes")
    edge("stereotypes", "prejudice-discrimination")
    edge("social-psychology-overview", "aggression")
    edge("social-psychology-overview", "prosocial-behavior")
    edge("prosocial-behavior", "bystander-effect")
    edge("social-psychology-overview", "interpersonal-attraction")
    edge("interpersonal-attraction", "love-psychology")
    edge("conformity", "social-influence")
    edge("social-psychology-overview", "self-concept")
    edge("attribution-theory", "self-serving-bias")
    edge("social-psychology-overview", "cultural-psychology")
    edge("social-psychology-overview", "social-media-psychology")
    edge("group-dynamics", "leadership-psychology")

    # ── clinical-psychology ──
    edge("clinical-overview", "psychopathology")
    edge("psychopathology", "anxiety-disorders")
    edge("psychopathology", "depressive-disorders")
    edge("psychopathology", "bipolar-disorder")
    edge("psychopathology", "schizophrenia")
    edge("psychopathology", "personality-disorders")
    edge("anxiety-disorders", "ptsd")
    edge("anxiety-disorders", "ocd")
    edge("psychopathology", "eating-disorders")
    edge("psychopathology", "substance-use-disorders")
    edge("clinical-overview", "psychological-assessment")
    edge("clinical-overview", "psychotherapy-overview")
    edge("psychotherapy-overview", "cbt")
    edge("psychotherapy-overview", "psychodynamic-therapy")
    edge("psychotherapy-overview", "humanistic-therapy")
    edge("psychotherapy-overview", "group-therapy")
    edge("clinical-overview", "crisis-intervention")
    edge("clinical-overview", "child-clinical")
    edge("clinical-overview", "positive-psychology")
    edge("positive-psychology", "mindfulness")
    edge("psychotherapy-overview", "therapeutic-relationship")
    edge("psychotherapy-overview", "evidence-based-practice")
    edge("depressive-disorders", "cbt", "related", 0.6)

    # ── behavioral-psychology ──
    edge("behavioral-overview", "classical-conditioning")
    edge("behavioral-overview", "operant-conditioning")
    edge("classical-conditioning", "stimulus-generalization")
    edge("classical-conditioning", "stimulus-discrimination")
    edge("classical-conditioning", "extinction")
    edge("operant-conditioning", "reinforcement-schedules")
    edge("operant-conditioning", "punishment")
    edge("operant-conditioning", "shaping")
    edge("behavioral-overview", "observational-learning")
    edge("observational-learning", "self-efficacy")
    edge("operant-conditioning", "behavior-modification")
    edge("behavior-modification", "token-economy")
    edge("classical-conditioning", "systematic-desensitization")
    edge("classical-conditioning", "aversion-therapy")
    edge("behavioral-overview", "biofeedback")
    edge("behavior-modification", "applied-behavior-analysis")
    edge("operant-conditioning", "habit-formation")
    edge("operant-conditioning", "learned-helplessness")
    edge("behavioral-overview", "latent-learning")
    edge("behavioral-overview", "motivation-behavioral")
    edge("cognitive-biases", "behavioral-economics", "related", 0.6)
    edge("motivation-behavioral", "behavioral-economics")

    # ── biological-psychology ──
    edge("biological-overview", "neuron-structure")
    edge("neuron-structure", "neurotransmitters")
    edge("biological-overview", "brain-structure")
    edge("brain-structure", "cerebral-lateralization")
    edge("biological-overview", "endocrine-system")
    edge("biological-overview", "autonomic-nervous-system")
    edge("neuron-structure", "neuroplasticity")
    edge("biological-overview", "sleep-psychology")
    edge("autonomic-nervous-system", "stress-physiology")
    edge("neurotransmitters", "psychopharmacology")
    edge("brain-structure", "brain-imaging")
    edge("biological-overview", "genetics-behavior")
    edge("brain-structure", "emotion-neuroscience")
    edge("biological-overview", "pain-psychology")
    edge("biological-overview", "hunger-eating")
    edge("endocrine-system", "sexual-behavior-biology")
    edge("brain-structure", "consciousness")
    edge("genetics-behavior", "evolutionary-psychology")
    edge("evolutionary-psychology", "comparative-psychology")
    edge("genetics-behavior", "epigenetics-behavior")
    edge("stress-physiology", "psychoneuroimmunology")

    # ── personality-psychology ──
    edge("personality-overview", "big-five")
    edge("personality-overview", "trait-theory")
    edge("trait-theory", "big-five")
    edge("personality-overview", "psychoanalytic-theory")
    edge("psychoanalytic-theory", "defense-mechanisms")
    edge("psychoanalytic-theory", "psychosexual-stages")
    edge("psychoanalytic-theory", "jung-theory")
    edge("personality-overview", "humanistic-personality")
    edge("humanistic-personality", "maslow-hierarchy")
    edge("humanistic-personality", "self-actualization")
    edge("personality-overview", "social-cognitive-personality")
    edge("personality-overview", "personality-assessment")
    edge("personality-assessment", "mbti")
    edge("social-cognitive-personality", "locus-of-control")
    edge("big-five", "personality-stability")
    edge("personality-overview", "narcissism")
    edge("attachment-theory", "attachment-adult", "related", 0.7)
    edge("big-five", "personality-culture")
    edge("narcissism", "dark-triad")
    edge("social-cognitive-personality", "growth-mindset")
    edge("humanistic-personality", "grit", "related", 0.5)
    edge("personality-overview", "emotional-regulation")

    # ── research-methods ──
    edge("research-methods-overview", "scientific-method")
    edge("scientific-method", "experimental-design")
    edge("experimental-design", "random-assignment")
    edge("research-methods-overview", "correlational-research")
    edge("research-methods-overview", "survey-methods")
    edge("research-methods-overview", "observational-methods")
    edge("research-methods-overview", "case-study-method")
    edge("research-methods-overview", "longitudinal-study")
    edge("research-methods-overview", "cross-sectional-study")
    edge("experimental-design", "descriptive-statistics")
    edge("descriptive-statistics", "inferential-statistics")
    edge("inferential-statistics", "effect-size")
    edge("research-methods-overview", "reliability-validity")
    edge("research-methods-overview", "sampling-methods")
    edge("research-methods-overview", "ethics-research")
    edge("inferential-statistics", "meta-analysis")
    edge("research-methods-overview", "qualitative-methods")
    edge("scientific-method", "operational-definition")
    edge("experimental-design", "internal-external-validity")
    edge("research-methods-overview", "replication-crisis")
    edge("research-methods-overview", "apa-style")
    edge("inferential-statistics", "power-analysis")

    # ── cross-subdomain edges ──
    edge("cognitive-biases", "attribution-theory", "related", 0.6)
    edge("self-efficacy", "self-concept", "related", 0.6)
    edge("observational-learning", "social-cognition", "related", 0.5)
    edge("classical-conditioning", "anxiety-disorders", "related", 0.6)
    edge("learned-helplessness", "depressive-disorders", "related", 0.7)
    edge("neurotransmitters", "depressive-disorders", "related", 0.6)
    edge("neurotransmitters", "anxiety-disorders", "related", 0.5)
    edge("psychopharmacology", "depressive-disorders", "related", 0.6)
    edge("brain-structure", "cognitive-psychology-overview", "related", 0.5)
    edge("attachment-theory", "love-psychology", "related", 0.6)
    edge("maslow-hierarchy", "motivation-behavioral", "related", 0.6)
    edge("psychoanalytic-theory", "psychodynamic-therapy", "related", 0.7)
    edge("humanistic-personality", "humanistic-therapy", "related", 0.7)
    edge("cbt", "cognitive-biases", "related", 0.6)
    edge("experimental-design", "clinical-overview", "related", 0.5)
    edge("reliability-validity", "personality-assessment", "related", 0.6)
    edge("reliability-validity", "psychological-assessment", "related", 0.7)
    edge("descriptive-statistics", "correlational-research", "related", 0.6)
    edge("erikson-stages", "identity-formation", "related", 0.8)
    edge("cognitive-development-piaget", "moral-development", "related", 0.5)

    return edges


def main():
    concepts = []
    for (cid, name, desc, sub, diff, mins, ctype, tags, ms) in CONCEPTS_RAW:
        concepts.append({
            "id": cid,
            "name": name,
            "description": desc,
            "subdomain_id": sub,
            "domain_id": "psychology",
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

    print(f"✅ Generated psychology seed graph:")
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
