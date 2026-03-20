#!/usr/bin/env python3
"""Generate Writing knowledge sphere seed graph.

8 subdomains, ~170 concepts covering writing fundamentals to revision craft.
"""
import json
from datetime import datetime, timezone

NOW = datetime.now(timezone.utc).isoformat()

DOMAIN = {
    "id": "writing",
    "name": "写作",
    "description": "从写作基础到文体修改的系统知识体系",
    "icon": "✍️",
    "color": "#f59e0b",
}

SUBDOMAINS = [
    {"id": "writing-fundamentals",  "name": "写作基础",     "order": 1},
    {"id": "narrative-writing",     "name": "叙事写作",     "order": 2},
    {"id": "expository-writing",    "name": "说明文写作",   "order": 3},
    {"id": "persuasive-writing",    "name": "论说文写作",   "order": 4},
    {"id": "creative-writing",      "name": "创意写作",     "order": 5},
    {"id": "academic-writing",      "name": "学术写作",     "order": 6},
    {"id": "professional-writing",  "name": "职业写作",     "order": 7},
    {"id": "revision-craft",        "name": "修改与文体",   "order": 8},
]

# (id, name, description, subdomain_id, difficulty, minutes, content_type, tags, is_milestone)
CONCEPTS_RAW = [
    # ── writing-fundamentals (22 concepts) ──
    ("writing-overview",            "写作概述",             "写作的本质、目的与分类概览",                             "writing-fundamentals", 1, 20, "theory", ["基础"], True),
    ("sentence-structure",          "句子结构",             "主谓宾、简单句与复合句的构造原则",                       "writing-fundamentals", 1, 25, "theory", ["语法"], True),
    ("paragraph-structure",         "段落结构",             "主题句、支撑句与结尾句的段落组织",                       "writing-fundamentals", 1, 25, "theory", ["结构"], True),
    ("punctuation-usage",           "标点符号运用",         "常用标点符号的功能与正确使用规范",                       "writing-fundamentals", 1, 20, "theory", ["语法"], False),
    ("word-choice",                 "词语选择",             "精准选词、避免冗余与词汇搭配技巧",                       "writing-fundamentals", 2, 25, "theory", ["语言"], False),
    ("coherence-cohesion",          "连贯与衔接",           "过渡词、逻辑连接与语篇连贯性",                           "writing-fundamentals", 2, 25, "theory", ["结构"], True),
    ("topic-selection",             "选题与立意",           "如何选择写作话题并确立中心思想",                         "writing-fundamentals", 2, 25, "theory", ["策略"], False),
    ("outline-planning",            "提纲与构思",           "写作前的思维导图、大纲与结构规划",                       "writing-fundamentals", 2, 25, "theory", ["策略"], False),
    ("writing-process",             "写作过程",             "预写、起草、修改、校对的完整写作流程",                   "writing-fundamentals", 1, 20, "theory", ["流程"], True),
    ("audience-awareness",          "读者意识",             "根据目标读者调整语言风格与内容深度",                     "writing-fundamentals", 2, 25, "theory", ["策略"], False),
    ("tone-and-voice",              "语气与声音",           "正式与非正式语气、作者独特声音的塑造",                   "writing-fundamentals", 2, 25, "theory", ["风格"], False),
    ("active-passive-voice",        "主动与被动语态",       "主动语态与被动语态的选择与效果",                         "writing-fundamentals", 2, 20, "theory", ["语法"], False),
    ("parallel-structure",          "平行结构",             "句式对称与并列结构的修辞效果",                           "writing-fundamentals", 2, 20, "theory", ["修辞"], False),
    ("figurative-language",         "修辞手法",             "比喻、拟人、夸张等常用修辞手法",                         "writing-fundamentals", 2, 30, "theory", ["修辞"], True),
    ("writing-genres-overview",     "写作体裁概览",         "记叙文、说明文、议论文、应用文等体裁特征",               "writing-fundamentals", 1, 20, "theory", ["基础"], False),
    ("reading-writing-connection",  "读写互动",             "阅读对写作的促进作用与借鉴方法",                         "writing-fundamentals", 2, 25, "theory", ["策略"], False),
    ("freewriting-techniques",      "自由写作技法",         "自由写作、头脑风暴与快速草稿的入门方法",                 "writing-fundamentals", 1, 20, "practice", ["入门"], False),
    ("grammar-essentials",          "语法要点",             "主谓一致、时态、代词指代等写作必备语法",                 "writing-fundamentals", 1, 25, "theory", ["语法"], False),
    ("vocabulary-building",         "词汇积累",             "扩大写作词汇量的策略与方法",                             "writing-fundamentals", 2, 25, "theory", ["语言"], False),
    ("sentence-variety",            "句式变化",             "长短句交替、句式多样化与节奏控制",                       "writing-fundamentals", 2, 25, "theory", ["风格"], False),
    ("writing-confidence",          "写作自信",             "克服写作焦虑、培养写作习惯与自我激励",                   "writing-fundamentals", 1, 20, "theory", ["心理"], False),
    ("writing-tools",               "写作工具",             "常用写作软件、笔记方法与数字化工具",                     "writing-fundamentals", 1, 15, "practice", ["工具"], False),

    # ── narrative-writing (22 concepts) ──
    ("narrative-overview",          "叙事写作概述",         "叙事文学的基本要素与创作原则",                           "narrative-writing", 1, 20, "theory", ["基础"], True),
    ("plot-structure",              "情节结构",             "起承转合、三幕式结构与弗赖塔格金字塔",                   "narrative-writing", 2, 30, "theory", ["结构"], True),
    ("character-creation",          "人物塑造",             "主要人物与次要人物的性格刻画与成长弧线",                 "narrative-writing", 2, 30, "theory", ["人物"], True),
    ("setting-description",         "场景描写",             "时间、地点、环境氛围的营造技法",                         "narrative-writing", 2, 25, "theory", ["描写"], False),
    ("point-of-view",               "叙事视角",             "第一人称、第三人称、全知视角的选择与效果",               "narrative-writing", 2, 25, "theory", ["技法"], True),
    ("dialogue-writing",            "对话写作",             "真实自然的对话技巧与对话标点规范",                       "narrative-writing", 2, 30, "theory", ["技法"], False),
    ("show-dont-tell",              "展示而非告知",         "通过细节、动作、感官描写代替直接陈述",                   "narrative-writing", 3, 25, "theory", ["技法"], True),
    ("conflict-tension",            "冲突与张力",           "内在冲突、外在冲突与悬念制造技巧",                       "narrative-writing", 3, 25, "theory", ["结构"], False),
    ("pacing-rhythm",               "节奏控制",             "叙事节奏的快慢调节与场景切换技巧",                       "narrative-writing", 3, 25, "theory", ["技法"], False),
    ("narrative-arc",               "叙事弧线",             "开端、发展、高潮、结局的完整叙事弧线",                   "narrative-writing", 2, 25, "theory", ["结构"], False),
    ("theme-development",           "主题发展",             "在叙事中自然地传达深层主题与意义",                       "narrative-writing", 3, 25, "theory", ["内涵"], False),
    ("sensory-detail",              "感官细节",             "视觉、听觉、嗅觉、触觉、味觉的描写运用",               "narrative-writing", 2, 25, "theory", ["描写"], False),
    ("flashback-foreshadow",        "闪回与伏笔",           "时间线操控与悬念铺设的高级叙事技法",                     "narrative-writing", 3, 25, "theory", ["技法"], False),
    ("unreliable-narrator",         "不可靠叙述者",         "利用叙述者偏见创造悬疑与深度",                           "narrative-writing", 4, 25, "theory", ["高级"], False),
    ("memoir-writing",              "回忆录写作",           "个人经历的文学化表达与情感真实性",                       "narrative-writing", 3, 25, "practice", ["应用"], False),
    ("short-story-craft",           "短篇小说技巧",         "短篇小说的篇幅控制、聚焦与结尾技巧",                   "narrative-writing", 3, 30, "practice", ["应用"], False),
    ("novel-structure",             "长篇小说结构",         "多线叙事、章节安排与长篇作品的节奏控制",               "narrative-writing", 4, 35, "theory", ["高级"], False),
    ("biographical-writing",        "传记写作",             "人物传记的资料收集、选材与叙事策略",                     "narrative-writing", 3, 25, "practice", ["应用"], False),
    ("travel-writing",              "旅行写作",             "旅行见闻的文学化记录与文化观察",                         "narrative-writing", 3, 25, "practice", ["应用"], False),
    ("narrative-essay",             "叙事散文",             "以个人经历为核心的散文写作技巧",                         "narrative-writing", 3, 25, "practice", ["应用"], False),
    ("storytelling-oral",           "口头叙事",             "口头讲故事的技巧与书面叙事的转化",                       "narrative-writing", 2, 20, "practice", ["基础"], False),
    ("micro-fiction",               "微型小说",             "极短篇幅内的叙事艺术与冲击力营造",                       "narrative-writing", 3, 20, "practice", ["应用"], False),

    # ── expository-writing (20 concepts) ──
    ("expository-overview",         "说明文概述",           "说明文的定义、分类与写作目的",                           "expository-writing", 1, 20, "theory", ["基础"], True),
    ("definition-essay",            "定义型说明文",         "通过界定概念进行说明的写作方法",                         "expository-writing", 2, 25, "theory", ["类型"], False),
    ("process-essay",               "过程型说明文",         "步骤说明、流程描述的写作方法",                           "expository-writing", 2, 25, "theory", ["类型"], True),
    ("comparison-contrast",         "比较对比文",           "两个或多个事物的异同分析写作方法",                       "expository-writing", 2, 25, "theory", ["类型"], False),
    ("cause-effect-essay",          "因果分析文",           "分析原因与结果关系的写作方法",                           "expository-writing", 2, 25, "theory", ["类型"], True),
    ("classification-essay",        "分类说明文",           "按标准分类、逐类说明的写作方法",                         "expository-writing", 2, 25, "theory", ["类型"], False),
    ("descriptive-essay",           "描述型说明文",         "客观描述事物特征与状态的写作方法",                       "expository-writing", 2, 25, "theory", ["类型"], False),
    ("informative-writing",         "信息型写作",           "传递客观信息、数据和事实的写作技巧",                     "expository-writing", 2, 25, "theory", ["技法"], False),
    ("data-presentation",           "数据呈现",             "图表、统计数据在说明文中的运用与解读",                   "expository-writing", 3, 25, "theory", ["技法"], False),
    ("technical-description",       "技术描述",             "技术产品、系统与流程的准确说明方法",                     "expository-writing", 3, 25, "theory", ["应用"], False),
    ("science-writing",             "科普写作",             "将科学知识转化为通俗易懂的大众读物",                     "expository-writing", 3, 30, "practice", ["应用"], True),
    ("news-writing",                "新闻写作",             "倒金字塔结构、5W1H与新闻报道写作",                       "expository-writing", 2, 25, "practice", ["应用"], False),
    ("feature-writing",             "专题报道",             "深度报道与特写的写作技巧与结构",                         "expository-writing", 3, 30, "practice", ["应用"], False),
    ("instruction-manual",          "说明书写作",           "用户手册、操作指南的清晰写作方法",                       "expository-writing", 2, 25, "practice", ["应用"], False),
    ("summary-writing",             "摘要写作",             "提取要点、压缩信息的摘要与缩写技巧",                     "expository-writing", 2, 25, "theory", ["技法"], False),
    ("interview-writing",           "采访写作",             "采访准备、提问技巧与采访稿整理",                         "expository-writing", 3, 25, "practice", ["应用"], False),
    ("review-writing",              "评论写作",             "书评、影评、产品评测等评论文章写作",                     "expository-writing", 3, 25, "practice", ["应用"], False),
    ("explanatory-structure",       "解释性结构",           "由浅入深、层层递进的说明文组织策略",                     "expository-writing", 2, 25, "theory", ["结构"], False),
    ("visual-aids-writing",         "图文配合写作",         "插图、图表与文字的协调配合方法",                         "expository-writing", 2, 20, "practice", ["工具"], False),
    ("fact-checking",               "事实核查",             "信息来源验证、数据准确性检查的方法",                     "expository-writing", 2, 25, "theory", ["规范"], False),

    # ── persuasive-writing (22 concepts) ──
    ("persuasive-overview",         "论说文概述",           "论说文的定义、要素与说服目的",                           "persuasive-writing", 1, 20, "theory", ["基础"], True),
    ("thesis-statement",            "论点陈述",             "清晰有力的中心论点的提出与表述",                         "persuasive-writing", 2, 25, "theory", ["核心"], True),
    ("argument-structure",          "论证结构",             "论点—论据—论证的逻辑组织方法",                           "persuasive-writing", 2, 30, "theory", ["结构"], True),
    ("evidence-types",              "论据类型",             "事实论据、数据论据、专家引证与案例论据",                 "persuasive-writing", 2, 25, "theory", ["论据"], False),
    ("logical-reasoning-writing",   "逻辑推理写作",         "演绎推理、归纳推理在论证中的运用",                       "persuasive-writing", 3, 30, "theory", ["逻辑"], True),
    ("counterargument",             "反驳与让步",           "预设反对意见并进行有效反驳的策略",                       "persuasive-writing", 3, 25, "theory", ["技法"], False),
    ("rhetorical-appeals",          "修辞诉求",             "逻辑诉求、情感诉求与人格诉求的综合运用",               "persuasive-writing", 3, 30, "theory", ["修辞"], True),
    ("logical-fallacies-writing",   "逻辑谬误识别",         "常见逻辑谬误的识别与避免方法",                           "persuasive-writing", 3, 25, "theory", ["逻辑"], False),
    ("persuasive-techniques",       "说服技巧",             "重复、类比、对比、设问等说服手法",                       "persuasive-writing", 2, 25, "theory", ["技法"], False),
    ("editorial-writing",           "社论写作",             "报刊社论与时评的结构与语言特征",                         "persuasive-writing", 3, 25, "practice", ["应用"], False),
    ("debate-writing",              "辩论稿写作",           "辩论赛立论、驳论与总结陈词的写作",                       "persuasive-writing", 3, 25, "practice", ["应用"], False),
    ("speech-writing",              "演讲稿写作",           "演讲稿的结构、语言与修辞技巧",                           "persuasive-writing", 3, 30, "practice", ["应用"], True),
    ("opinion-essay",               "观点文写作",           "表达个人观点并进行论证的短文写作",                       "persuasive-writing", 2, 25, "practice", ["应用"], False),
    ("proposal-writing",            "提案写作",             "项目建议书与方案提议的写作结构",                         "persuasive-writing", 3, 25, "practice", ["应用"], False),
    ("advertising-copywriting",     "广告文案",             "商业广告与营销文案的说服性写作",                         "persuasive-writing", 3, 25, "practice", ["应用"], False),
    ("ethos-building",              "人格信誉构建",         "通过专业性、可信度建立作者权威",                         "persuasive-writing", 3, 25, "theory", ["修辞"], False),
    ("pathos-techniques",           "情感唤起技法",         "通过故事、意象与情感语言打动读者",                       "persuasive-writing", 3, 25, "theory", ["修辞"], False),
    ("logos-strategies",            "逻辑论证策略",         "运用数据、证据与推理说服读者的方法",                     "persuasive-writing", 3, 25, "theory", ["逻辑"], False),
    ("call-to-action",              "行动号召",             "文章结尾的行动号召与读者激励技巧",                       "persuasive-writing", 2, 20, "theory", ["技法"], False),
    ("critical-analysis-essay",     "批判分析文",           "对文本、观点或现象的深度批判与分析",                     "persuasive-writing", 4, 30, "theory", ["高级"], False),
    ("propaganda-analysis",         "宣传手法分析",         "识别与分析宣传手法的批判性阅读方法",                     "persuasive-writing", 3, 25, "theory", ["批判"], False),
    ("persuasive-ethics",           "说服伦理",             "说服性写作中的道德边界与责任意识",                       "persuasive-writing", 2, 20, "theory", ["伦理"], False),

    # ── creative-writing (22 concepts) ──
    ("creative-overview",           "创意写作概述",         "创意写作的定义、领域与创作精神",                         "creative-writing", 1, 20, "theory", ["基础"], True),
    ("poetry-basics",               "诗歌基础",             "韵律、节奏、意象与诗歌形式概述",                         "creative-writing", 2, 30, "theory", ["诗歌"], True),
    ("free-verse",                  "自由诗",               "自由体诗歌的创作方法与审美特征",                         "creative-writing", 2, 25, "practice", ["诗歌"], False),
    ("classical-poetry-forms",      "古典诗词",             "中国古典诗词的格律、意境与创作传统",                     "creative-writing", 3, 30, "theory", ["诗歌"], True),
    ("imagery-symbolism",           "意象与象征",           "意象构建与象征手法在创意写作中的运用",                   "creative-writing", 3, 25, "theory", ["技法"], True),
    ("creative-nonfiction",         "创意非虚构",           "将文学手法应用于真实事件的写作方式",                     "creative-writing", 3, 25, "theory", ["类型"], False),
    ("flash-fiction",               "闪小说",               "极短篇幅(千字以内)的小说创作技巧",                       "creative-writing", 3, 25, "practice", ["类型"], False),
    ("dramatic-writing",            "戏剧写作",             "戏剧剧本的对话、动作与舞台提示写作",                     "creative-writing", 3, 30, "theory", ["类型"], False),
    ("screenplay-basics",           "剧本写作基础",         "电影/电视剧本的格式、结构与场景描写",                   "creative-writing", 3, 30, "theory", ["类型"], True),
    ("song-lyrics",                 "歌词创作",             "歌词的韵律、意象与情感表达技巧",                         "creative-writing", 3, 25, "practice", ["类型"], False),
    ("world-building",              "世界构建",             "虚构世界的设定、规则与细节构建方法",                     "creative-writing", 3, 30, "theory", ["虚构"], False),
    ("voice-style",                 "文学声音与风格",       "发展独特的写作声音与个人风格",                           "creative-writing", 3, 25, "theory", ["风格"], False),
    ("experimental-writing",        "实验性写作",           "突破传统形式的先锋写作与元小说技法",                     "creative-writing", 4, 25, "theory", ["先锋"], False),
    ("humor-writing",               "幽默写作",             "喜剧效果的营造、讽刺与反讽技巧",                         "creative-writing", 3, 25, "theory", ["风格"], False),
    ("horror-suspense-writing",     "恐怖悬疑写作",         "悬疑氛围营造与恐怖效果的文学技法",                       "creative-writing", 3, 25, "theory", ["类型"], False),
    ("childrens-writing",           "儿童文学写作",         "适合不同年龄段儿童的故事创作方法",                       "creative-writing", 3, 25, "practice", ["类型"], False),
    ("writing-prompts",             "写作提示与练习",       "利用写作提示激发创意的练习方法",                         "creative-writing", 1, 20, "practice", ["练习"], False),
    ("literary-devices",            "文学手法",             "反讽、隐喻、转喻、通感等高级文学技法",                   "creative-writing", 3, 30, "theory", ["技法"], False),
    ("genre-fiction",               "类型小说",             "科幻、奇幻、推理、言情等类型小说特征",                   "creative-writing", 2, 25, "theory", ["类型"], False),
    ("creative-process",            "创作过程",             "灵感捕捉、素材积累与创意孵化的方法",                     "creative-writing", 2, 25, "theory", ["流程"], False),
    ("publishing-basics",           "出版入门",             "投稿、审稿、版权与自出版的基本知识",                     "creative-writing", 2, 25, "practice", ["出版"], False),
    ("writing-workshop",            "写作工坊",             "创意写作工坊的同行评议与反馈方法",                       "creative-writing", 2, 25, "practice", ["社群"], False),

    # ── academic-writing (22 concepts) ──
    ("academic-overview",           "学术写作概述",         "学术写作的特征、规范与基本要求",                         "academic-writing", 2, 25, "theory", ["基础"], True),
    ("research-question",           "研究问题",             "如何提出有效的研究问题与研究假设",                       "academic-writing", 2, 25, "theory", ["研究"], True),
    ("literature-review",           "文献综述",             "学术文献的检索、评价与综述写作",                         "academic-writing", 3, 35, "theory", ["研究"], True),
    ("research-methodology",        "研究方法论写作",       "定量、定性与混合研究方法的写作呈现",                     "academic-writing", 3, 30, "theory", ["研究"], False),
    ("academic-argument",           "学术论证",             "学术论文中的论点提出与论证展开",                         "academic-writing", 3, 30, "theory", ["论证"], True),
    ("citation-referencing",        "引用与参考文献",       "APA、MLA、Chicago等引用格式与文献管理",                 "academic-writing", 2, 25, "theory", ["规范"], True),
    ("abstract-writing",            "摘要写作",             "学术论文摘要的结构与写作技巧",                           "academic-writing", 2, 25, "practice", ["格式"], False),
    ("introduction-writing",        "引言写作",             "学术论文引言的CARS模式与写作策略",                       "academic-writing", 3, 25, "practice", ["格式"], False),
    ("methodology-section",         "方法部分",             "研究方法部分的写作要素与组织",                           "academic-writing", 3, 25, "practice", ["格式"], False),
    ("results-discussion",          "结果与讨论",           "数据呈现、结果分析与讨论的写作方法",                     "academic-writing", 3, 30, "practice", ["格式"], False),
    ("conclusion-writing",          "结论写作",             "学术论文结论的总结、贡献与展望",                         "academic-writing", 3, 25, "practice", ["格式"], False),
    ("academic-tone",               "学术语体",             "客观、准确、严谨的学术语言风格",                         "academic-writing", 2, 25, "theory", ["风格"], False),
    ("hedging-language",            "模糊限制语",           "学术写作中的谨慎表述与程度限定",                         "academic-writing", 3, 20, "theory", ["语言"], False),
    ("thesis-writing",              "学位论文写作",         "硕士/博士学位论文的结构与写作流程",                     "academic-writing", 4, 35, "theory", ["高级"], True),
    ("peer-review-process",         "同行评审",             "学术论文投稿与同行评审的流程与应对",                     "academic-writing", 3, 25, "theory", ["出版"], False),
    ("plagiarism-avoidance",        "避免抄袭",             "学术诚信、引用规范与抄袭检测工具",                       "academic-writing", 2, 20, "theory", ["伦理"], False),
    ("conference-paper",            "会议论文",             "学术会议论文的撰写与报告准备",                           "academic-writing", 3, 25, "practice", ["出版"], False),
    ("grant-proposal",              "科研基金申请",         "科研项目申请书的写作结构与策略",                         "academic-writing", 4, 30, "practice", ["高级"], False),
    ("academic-book-review",        "学术书评",             "学术著作的批判性评介与评论写作",                         "academic-writing", 3, 25, "practice", ["应用"], False),
    ("data-visualization-writing",  "数据可视化写作",       "学术写作中图表的设计、描述与解读",                       "academic-writing", 3, 25, "practice", ["工具"], False),
    ("collaborative-writing",       "合作写作",             "多作者协作写作的工具、流程与规范",                       "academic-writing", 2, 20, "practice", ["流程"], False),
    ("academic-presentation",       "学术报告",             "学术口头报告与海报展示的准备方法",                       "academic-writing", 2, 25, "practice", ["展示"], False),

    # ── professional-writing (20 concepts) ──
    ("professional-overview",       "职业写作概述",         "职业环境中的写作类型与基本要求",                         "professional-writing", 1, 20, "theory", ["基础"], True),
    ("business-email",              "商务邮件",             "商务邮件的格式、语气与高效沟通技巧",                     "professional-writing", 2, 25, "practice", ["应用"], True),
    ("report-writing",              "报告写作",             "工作报告、调研报告的结构与写作方法",                     "professional-writing", 2, 30, "practice", ["应用"], True),
    ("resume-cover-letter",         "简历与求职信",         "个人简历与求职信的写作策略与格式",                       "professional-writing", 2, 25, "practice", ["职业"], True),
    ("meeting-minutes",             "会议纪要",             "会议记录与纪要的规范写作方法",                           "professional-writing", 2, 20, "practice", ["应用"], False),
    ("memo-writing",                "备忘录写作",           "内部备忘录的格式、结构与写作要点",                       "professional-writing", 2, 20, "practice", ["应用"], False),
    ("technical-writing",           "技术文档写作",         "技术文档、API文档与开发者指南的写作",                   "professional-writing", 3, 30, "practice", ["技术"], True),
    ("ux-writing",                  "用户体验写作",         "界面文案、微文案与用户引导文字的设计",                   "professional-writing", 3, 25, "practice", ["设计"], False),
    ("content-marketing",           "内容营销写作",         "博客文章、白皮书与内容策略的写作方法",                   "professional-writing", 3, 25, "practice", ["营销"], False),
    ("social-media-writing",        "社交媒体写作",         "不同社交平台的文案特征与写作技巧",                       "professional-writing", 2, 20, "practice", ["营销"], False),
    ("press-release",               "新闻稿",               "企业新闻稿的标准格式与写作规范",                         "professional-writing", 2, 25, "practice", ["公关"], False),
    ("contract-legal-writing",      "合同与法律文书",       "合同条款、法律文件的准确性与规范性",                     "professional-writing", 4, 30, "theory", ["法律"], False),
    ("grant-report",                "项目总结报告",         "项目进展报告与最终成果报告的写作",                       "professional-writing", 3, 25, "practice", ["应用"], False),
    ("crisis-communication",        "危机沟通写作",         "危机公关声明、致歉信与应急通知的写作",                   "professional-writing", 3, 25, "practice", ["公关"], False),
    ("policy-writing",              "政策文件写作",         "政策文件、规章制度的清晰准确写作",                       "professional-writing", 3, 25, "practice", ["行政"], False),
    ("pitch-deck-narrative",        "商业计划叙事",         "创业路演与商业计划书的叙事策略",                         "professional-writing", 3, 25, "practice", ["商业"], False),
    ("localization-writing",        "本地化写作",           "跨文化语境下的文本翻译与本地化策略",                     "professional-writing", 3, 25, "theory", ["国际"], False),
    ("seo-writing",                 "SEO写作",              "搜索引擎优化写作的关键词策略与技巧",                     "professional-writing", 3, 25, "practice", ["数字"], False),
    ("newsletter-writing",          "通讯写作",             "企业通讯、电子邮件通讯的编写方法",                       "professional-writing", 2, 20, "practice", ["营销"], False),
    ("documentation-standards",     "文档标准",             "企业文档管理规范、模板与版本控制",                       "professional-writing", 2, 20, "theory", ["规范"], False),

    # ── revision-craft (20 concepts) ──
    ("revision-overview",           "修改概述",             "修改的重要性、层次与基本原则",                           "revision-craft", 1, 20, "theory", ["基础"], True),
    ("self-editing",                "自我编辑",             "自我审读、检查清单与距离感策略",                         "revision-craft", 2, 25, "theory", ["技法"], True),
    ("structural-revision",         "结构修改",             "文章整体结构、段落组织的调整方法",                       "revision-craft", 2, 25, "theory", ["层次"], True),
    ("sentence-level-editing",      "句子层修改",           "句子清晰度、简洁性与力度的打磨技巧",                     "revision-craft", 2, 25, "theory", ["层次"], False),
    ("word-level-editing",          "词语层修改",           "精确选词、消除冗余与语言打磨",                           "revision-craft", 2, 25, "theory", ["层次"], False),
    ("proofreading",                "校对",                 "拼写、语法、标点与格式的最终检查",                       "revision-craft", 1, 20, "theory", ["流程"], True),
    ("peer-feedback",               "同行反馈",             "有效给予与接受写作反馈的方法",                           "revision-craft", 2, 25, "theory", ["社群"], False),
    ("style-consistency",           "风格一致性",           "文体、语气与格式在全文中的统一维护",                     "revision-craft", 2, 25, "theory", ["风格"], False),
    ("clarity-conciseness",         "清晰与简洁",           "消除歧义、减少冗余、提高表达清晰度",                     "revision-craft", 2, 25, "theory", ["原则"], True),
    ("rhythm-flow",                 "节奏与流畅",           "句式节奏、段落衔接与全文流畅度的优化",                   "revision-craft", 3, 25, "theory", ["风格"], False),
    ("cutting-killing-darlings",    "删减与割爱",           "大胆删除冗余内容与心爱但无用的段落",                     "revision-craft", 3, 20, "theory", ["技法"], False),
    ("fact-verification",           "事实核实",             "修改阶段的事实、数据与引用准确性检查",                   "revision-craft", 2, 20, "theory", ["规范"], False),
    ("formatting-layout",           "排版与格式",           "文档排版、标题层级与视觉呈现规范",                       "revision-craft", 1, 20, "theory", ["格式"], False),
    ("style-guide",                 "写作风格指南",         "常用风格指南(AP/Chicago/GB)的核心规范",                 "revision-craft", 2, 25, "theory", ["规范"], False),
    ("developmental-editing",       "发展性编辑",           "宏观层面的内容、结构与论证质量评估",                     "revision-craft", 3, 30, "theory", ["专业"], False),
    ("copyediting",                 "文字编辑",             "语法、用词、风格与一致性的专业编辑",                     "revision-craft", 3, 25, "theory", ["专业"], False),
    ("ai-writing-tools",            "AI写作工具",           "GPT、Grammarly等AI辅助写作工具的应用与局限",           "revision-craft", 2, 25, "practice", ["工具"], False),
    ("revision-strategies",         "修改策略",             "分层修改、朗读法与逆向大纲等修改方法",                   "revision-craft", 2, 25, "theory", ["方法"], False),
    ("editor-author-relation",      "编辑与作者关系",       "专业编辑流程中的沟通、协作与决策",                       "revision-craft", 3, 20, "theory", ["专业"], False),
    ("portfolio-building",          "作品集建设",           "写作作品的选择、修订与作品集的构建策略",                 "revision-craft", 2, 25, "practice", ["职业"], False),
]


def build_edges(concepts):
    """Build edges between concepts."""
    edges = []
    cids = {c["id"] for c in concepts}

    def edge(src, tgt, rel="prerequisite", strength=0.8):
        assert src in cids, f"Missing source: {src}"
        assert tgt in cids, f"Missing target: {tgt}"
        edges.append({
            "source_id": src,
            "target_id": tgt,
            "relation_type": rel,
            "strength": strength,
        })

    # ── writing-fundamentals prerequisites ──
    edge("writing-overview", "sentence-structure")
    edge("writing-overview", "paragraph-structure")
    edge("writing-overview", "writing-process")
    edge("writing-overview", "writing-genres-overview")
    edge("sentence-structure", "punctuation-usage")
    edge("sentence-structure", "word-choice")
    edge("sentence-structure", "grammar-essentials")
    edge("paragraph-structure", "coherence-cohesion")
    edge("writing-process", "outline-planning")
    edge("writing-process", "topic-selection")
    edge("writing-overview", "audience-awareness")
    edge("audience-awareness", "tone-and-voice")
    edge("sentence-structure", "active-passive-voice")
    edge("sentence-structure", "parallel-structure")
    edge("word-choice", "figurative-language")
    edge("sentence-structure", "sentence-variety")
    edge("writing-overview", "freewriting-techniques")
    edge("word-choice", "vocabulary-building")
    edge("writing-overview", "writing-confidence")
    edge("writing-overview", "writing-tools")
    edge("writing-overview", "reading-writing-connection")

    # ── narrative-writing ──
    edge("narrative-overview", "plot-structure")
    edge("narrative-overview", "character-creation")
    edge("narrative-overview", "setting-description")
    edge("narrative-overview", "point-of-view")
    edge("plot-structure", "narrative-arc")
    edge("plot-structure", "conflict-tension")
    edge("character-creation", "dialogue-writing")
    edge("setting-description", "sensory-detail")
    edge("narrative-overview", "show-dont-tell")
    edge("plot-structure", "pacing-rhythm")
    edge("narrative-arc", "theme-development")
    edge("plot-structure", "flashback-foreshadow")
    edge("point-of-view", "unreliable-narrator")
    edge("narrative-overview", "memoir-writing")
    edge("plot-structure", "short-story-craft")
    edge("plot-structure", "novel-structure")
    edge("character-creation", "biographical-writing")
    edge("narrative-overview", "travel-writing")
    edge("narrative-overview", "narrative-essay")
    edge("narrative-overview", "storytelling-oral")
    edge("short-story-craft", "micro-fiction")

    # ── expository-writing ──
    edge("expository-overview", "definition-essay")
    edge("expository-overview", "process-essay")
    edge("expository-overview", "comparison-contrast")
    edge("expository-overview", "cause-effect-essay")
    edge("expository-overview", "classification-essay")
    edge("expository-overview", "descriptive-essay")
    edge("expository-overview", "informative-writing")
    edge("informative-writing", "data-presentation")
    edge("informative-writing", "technical-description")
    edge("expository-overview", "science-writing")
    edge("expository-overview", "news-writing")
    edge("news-writing", "feature-writing")
    edge("expository-overview", "instruction-manual")
    edge("expository-overview", "summary-writing")
    edge("news-writing", "interview-writing")
    edge("expository-overview", "review-writing")
    edge("expository-overview", "explanatory-structure")
    edge("data-presentation", "visual-aids-writing")
    edge("informative-writing", "fact-checking")

    # ── persuasive-writing ──
    edge("persuasive-overview", "thesis-statement")
    edge("thesis-statement", "argument-structure")
    edge("argument-structure", "evidence-types")
    edge("argument-structure", "logical-reasoning-writing")
    edge("argument-structure", "counterargument")
    edge("persuasive-overview", "rhetorical-appeals")
    edge("logical-reasoning-writing", "logical-fallacies-writing")
    edge("rhetorical-appeals", "persuasive-techniques")
    edge("persuasive-overview", "editorial-writing")
    edge("argument-structure", "debate-writing")
    edge("rhetorical-appeals", "speech-writing")
    edge("persuasive-overview", "opinion-essay")
    edge("argument-structure", "proposal-writing")
    edge("persuasive-techniques", "advertising-copywriting")
    edge("rhetorical-appeals", "ethos-building")
    edge("rhetorical-appeals", "pathos-techniques")
    edge("rhetorical-appeals", "logos-strategies")
    edge("persuasive-techniques", "call-to-action")
    edge("argument-structure", "critical-analysis-essay")
    edge("logical-fallacies-writing", "propaganda-analysis")
    edge("persuasive-overview", "persuasive-ethics")

    # ── creative-writing ──
    edge("creative-overview", "poetry-basics")
    edge("poetry-basics", "free-verse")
    edge("poetry-basics", "classical-poetry-forms")
    edge("creative-overview", "imagery-symbolism")
    edge("creative-overview", "creative-nonfiction")
    edge("creative-overview", "flash-fiction")
    edge("creative-overview", "dramatic-writing")
    edge("dramatic-writing", "screenplay-basics")
    edge("poetry-basics", "song-lyrics")
    edge("creative-overview", "world-building")
    edge("creative-overview", "voice-style")
    edge("voice-style", "experimental-writing")
    edge("creative-overview", "humor-writing")
    edge("creative-overview", "horror-suspense-writing")
    edge("creative-overview", "childrens-writing")
    edge("creative-overview", "writing-prompts")
    edge("imagery-symbolism", "literary-devices")
    edge("creative-overview", "genre-fiction")
    edge("creative-overview", "creative-process")
    edge("creative-overview", "publishing-basics")
    edge("creative-overview", "writing-workshop")

    # ── academic-writing ──
    edge("academic-overview", "research-question")
    edge("research-question", "literature-review")
    edge("academic-overview", "research-methodology")
    edge("academic-overview", "academic-argument")
    edge("academic-overview", "citation-referencing")
    edge("academic-overview", "abstract-writing")
    edge("research-question", "introduction-writing")
    edge("research-methodology", "methodology-section")
    edge("methodology-section", "results-discussion")
    edge("results-discussion", "conclusion-writing")
    edge("academic-overview", "academic-tone")
    edge("academic-tone", "hedging-language")
    edge("literature-review", "thesis-writing")
    edge("academic-overview", "peer-review-process")
    edge("citation-referencing", "plagiarism-avoidance")
    edge("academic-overview", "conference-paper")
    edge("thesis-writing", "grant-proposal")
    edge("academic-overview", "academic-book-review")
    edge("results-discussion", "data-visualization-writing")
    edge("academic-overview", "collaborative-writing")
    edge("academic-overview", "academic-presentation")

    # ── professional-writing ──
    edge("professional-overview", "business-email")
    edge("professional-overview", "report-writing")
    edge("professional-overview", "resume-cover-letter")
    edge("professional-overview", "meeting-minutes")
    edge("professional-overview", "memo-writing")
    edge("professional-overview", "technical-writing")
    edge("professional-overview", "ux-writing")
    edge("professional-overview", "content-marketing")
    edge("content-marketing", "social-media-writing")
    edge("professional-overview", "press-release")
    edge("professional-overview", "contract-legal-writing")
    edge("report-writing", "grant-report")
    edge("press-release", "crisis-communication")
    edge("professional-overview", "policy-writing")
    edge("content-marketing", "pitch-deck-narrative")
    edge("professional-overview", "localization-writing")
    edge("content-marketing", "seo-writing")
    edge("content-marketing", "newsletter-writing")
    edge("professional-overview", "documentation-standards")

    # ── revision-craft ──
    edge("revision-overview", "self-editing")
    edge("revision-overview", "structural-revision")
    edge("structural-revision", "sentence-level-editing")
    edge("sentence-level-editing", "word-level-editing")
    edge("word-level-editing", "proofreading")
    edge("revision-overview", "peer-feedback")
    edge("revision-overview", "style-consistency")
    edge("revision-overview", "clarity-conciseness")
    edge("clarity-conciseness", "rhythm-flow")
    edge("self-editing", "cutting-killing-darlings")
    edge("revision-overview", "fact-verification")
    edge("revision-overview", "formatting-layout")
    edge("revision-overview", "style-guide")
    edge("structural-revision", "developmental-editing")
    edge("sentence-level-editing", "copyediting")
    edge("revision-overview", "ai-writing-tools")
    edge("revision-overview", "revision-strategies")
    edge("developmental-editing", "editor-author-relation")
    edge("revision-overview", "portfolio-building")

    # ── cross-subdomain edges ──
    edge("writing-overview", "narrative-overview", "related", 0.6)
    edge("writing-overview", "expository-overview", "related", 0.6)
    edge("writing-overview", "persuasive-overview", "related", 0.6)
    edge("writing-overview", "creative-overview", "related", 0.6)
    edge("writing-overview", "academic-overview", "related", 0.5)
    edge("writing-overview", "professional-overview", "related", 0.5)
    edge("writing-process", "revision-overview", "related", 0.7)
    edge("figurative-language", "imagery-symbolism", "related", 0.7)
    edge("figurative-language", "literary-devices", "related", 0.7)
    edge("coherence-cohesion", "structural-revision", "related", 0.6)
    edge("audience-awareness", "ux-writing", "related", 0.5)
    edge("audience-awareness", "content-marketing", "related", 0.5)
    edge("tone-and-voice", "voice-style", "related", 0.7)
    edge("tone-and-voice", "academic-tone", "related", 0.6)
    edge("argument-structure", "academic-argument", "related", 0.8)
    edge("thesis-statement", "research-question", "related", 0.6)
    edge("evidence-types", "citation-referencing", "related", 0.5)
    edge("show-dont-tell", "sensory-detail", "related", 0.7)
    edge("show-dont-tell", "imagery-symbolism", "related", 0.6)
    edge("plot-structure", "screenplay-basics", "related", 0.6)
    edge("character-creation", "dramatic-writing", "related", 0.6)
    edge("dialogue-writing", "dramatic-writing", "related", 0.7)
    edge("news-writing", "press-release", "related", 0.6)
    edge("summary-writing", "abstract-writing", "related", 0.7)
    edge("fact-checking", "fact-verification", "related", 0.8)
    edge("proposal-writing", "grant-proposal", "related", 0.7)
    edge("technical-description", "technical-writing", "related", 0.8)
    edge("data-presentation", "data-visualization-writing", "related", 0.7)
    edge("review-writing", "academic-book-review", "related", 0.6)
    edge("speech-writing", "academic-presentation", "related", 0.5)
    edge("report-writing", "results-discussion", "related", 0.5)
    edge("self-editing", "proofreading", "related", 0.6)
    edge("style-guide", "style-consistency", "related", 0.7)
    edge("word-choice", "word-level-editing", "related", 0.7)
    edge("sentence-variety", "sentence-level-editing", "related", 0.6)
    edge("sentence-variety", "rhythm-flow", "related", 0.6)
    edge("creative-nonfiction", "narrative-essay", "related", 0.7)
    edge("creative-nonfiction", "memoir-writing", "related", 0.7)
    edge("flash-fiction", "micro-fiction", "related", 0.8)
    edge("advertising-copywriting", "content-marketing", "related", 0.6)
    edge("persuasive-techniques", "pathos-techniques", "related", 0.6)
    edge("logical-reasoning-writing", "logos-strategies", "related", 0.7)

    return edges


def main():
    concepts = []
    for (cid, name, desc, sub, diff, mins, ctype, tags, ms) in CONCEPTS_RAW:
        concepts.append({
            "id": cid,
            "name": name,
            "description": desc,
            "subdomain_id": sub,
            "domain_id": "writing",
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

    print(f"✅ Generated writing seed graph:")
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
