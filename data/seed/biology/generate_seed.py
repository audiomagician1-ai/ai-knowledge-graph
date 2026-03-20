#!/usr/bin/env python3
"""Generate Biology knowledge sphere seed graph.

8 subdomains, ~170 concepts covering molecular biology to ecosystems.
"""
import json
from datetime import datetime, timezone

NOW = datetime.now(timezone.utc).isoformat()

DOMAIN = {
    "id": "biology",
    "name": "生物学",
    "description": "从分子生物学到生态系统的系统知识体系",
    "icon": "🟤",
    "color": "#84cc16",
}

SUBDOMAINS = [
    {"id": "cell-biology",        "name": "细胞生物学",     "order": 1},
    {"id": "molecular-biology",   "name": "分子生物学",     "order": 2},
    {"id": "genetics",            "name": "遗传学",         "order": 3},
    {"id": "evolution",           "name": "进化生物学",     "order": 4},
    {"id": "human-physiology",    "name": "人体生理学",     "order": 5},
    {"id": "ecology",             "name": "生态学",         "order": 6},
    {"id": "microbiology",        "name": "微生物学",       "order": 7},
    {"id": "botany-zoology",      "name": "植物与动物学",   "order": 8},
]

# (id, name, description, subdomain_id, difficulty, minutes, content_type, tags, is_milestone)
CONCEPTS_RAW = [
    # ── cell-biology (22 concepts) ──
    ("cell-biology-overview",       "细胞生物学概述",       "细胞学说、细胞的基本结构与功能",                       "cell-biology", 1, 20, "theory", ["基础"], True),
    ("prokaryotic-cells",           "原核细胞",             "细菌和古菌的细胞结构特征",                             "cell-biology", 1, 20, "theory", ["基础"], False),
    ("eukaryotic-cells",            "真核细胞",             "真核细胞的结构特征与膜性细胞器",                       "cell-biology", 1, 25, "theory", ["基础"], False),
    ("cell-membrane",               "细胞膜",               "磷脂双分子层结构、流动镶嵌模型与物质转运",             "cell-biology", 2, 30, "theory", ["结构"], True),
    ("membrane-transport",          "膜转运",               "被动运输、主动运输与囊泡转运机制",                     "cell-biology", 2, 30, "theory", ["功能"], False),
    ("endoplasmic-reticulum",       "内质网",               "粗面内质网与滑面内质网的结构与功能",                   "cell-biology", 2, 25, "theory", ["细胞器"], False),
    ("golgi-apparatus",             "高尔基体",             "蛋白质加工、分选与分泌功能",                           "cell-biology", 2, 25, "theory", ["细胞器"], False),
    ("mitochondria",                "线粒体",               "线粒体结构、有氧呼吸与ATP合成",                       "cell-biology", 2, 30, "theory", ["细胞器"], True),
    ("chloroplast",                 "叶绿体",               "叶绿体结构与光合作用的场所",                           "cell-biology", 2, 25, "theory", ["细胞器"], False),
    ("nucleus",                     "细胞核",               "核膜、染色质、核仁与基因表达调控",                     "cell-biology", 2, 25, "theory", ["结构"], False),
    ("cytoskeleton",                "细胞骨架",             "微管、微丝与中间纤维的结构与功能",                     "cell-biology", 2, 25, "theory", ["结构"], False),
    ("cell-cycle",                  "细胞周期",             "G1/S/G2/M期与细胞周期调控机制",                       "cell-biology", 3, 30, "theory", ["增殖"], True),
    ("mitosis",                     "有丝分裂",             "前期、中期、后期与末期的细胞分裂过程",                 "cell-biology", 2, 25, "theory", ["增殖"], False),
    ("meiosis",                     "减数分裂",             "减数分裂I/II与遗传多样性的产生",                       "cell-biology", 3, 30, "theory", ["增殖"], False),
    ("apoptosis",                   "细胞凋亡",             "程序性细胞死亡的分子机制与生物学意义",                 "cell-biology", 3, 25, "theory", ["调控"], False),
    ("cell-signaling",              "细胞信号转导",         "受体、第二信使与信号级联放大机制",                     "cell-biology", 3, 30, "theory", ["通讯"], True),
    ("stem-cells",                  "干细胞",               "胚胎干细胞与成体干细胞的特性与应用",                   "cell-biology", 3, 25, "theory", ["前沿"], False),
    ("cellular-respiration",        "细胞呼吸",             "糖酵解、柠檬酸循环与氧化磷酸化",                       "cell-biology", 3, 35, "theory", ["代谢"], False),
    ("photosynthesis",              "光合作用",             "光反应与暗反应(Calvin循环)的完整过程",                 "cell-biology", 3, 35, "theory", ["代谢"], False),
    ("cell-differentiation",        "细胞分化",             "基因差异性表达与细胞命运决定",                         "cell-biology", 3, 25, "theory", ["发育"], False),
    ("lysosomes-peroxisomes",       "溶酶体与过氧化物酶体", "细胞内消化与解毒功能",                                 "cell-biology", 2, 20, "theory", ["细胞器"], False),
    ("endomembrane-system",         "内膜系统",             "内质网-高尔基体-溶酶体的功能协作网络",                 "cell-biology", 3, 25, "theory", ["系统"], False),

    # ── molecular-biology (22 concepts) ──
    ("molecular-biology-overview",  "分子生物学概述",       "分子生物学的中心法则与研究范畴",                       "molecular-biology", 1, 20, "theory", ["基础"], True),
    ("dna-structure",               "DNA结构",              "双螺旋结构、碱基配对与DNA的理化性质",                 "molecular-biology", 2, 30, "theory", ["核酸"], True),
    ("rna-types",                   "RNA类型",              "mRNA、tRNA、rRNA及非编码RNA的功能",                   "molecular-biology", 2, 25, "theory", ["核酸"], False),
    ("dna-replication",             "DNA复制",              "半保留复制、复制叉与DNA聚合酶",                       "molecular-biology", 3, 30, "theory", ["核酸"], False),
    ("transcription",               "转录",                 "RNA聚合酶、启动子识别与mRNA加工",                     "molecular-biology", 3, 30, "theory", ["基因表达"], True),
    ("translation",                 "翻译",                 "核糖体、密码子与蛋白质合成过程",                       "molecular-biology", 3, 30, "theory", ["基因表达"], False),
    ("gene-regulation",             "基因调控",             "操纵子模型、转录因子与表观遗传调控",                   "molecular-biology", 4, 35, "theory", ["调控"], True),
    ("protein-structure",           "蛋白质结构",           "一级到四级结构与蛋白质折叠",                           "molecular-biology", 2, 30, "theory", ["蛋白质"], False),
    ("enzyme-function",             "酶的功能",             "酶的催化机制、动力学与调节",                           "molecular-biology", 2, 30, "theory", ["蛋白质"], False),
    ("protein-modification",        "蛋白质修饰",           "磷酸化、糖基化、泛素化等翻译后修饰",                   "molecular-biology", 3, 25, "theory", ["蛋白质"], False),
    ("signal-transduction-mol",     "分子信号通路",         "MAPK、PI3K/Akt与Wnt等经典信号通路",                   "molecular-biology", 4, 30, "theory", ["信号"], False),
    ("epigenetics",                 "表观遗传学",           "DNA甲基化、组蛋白修饰与染色质重塑",                   "molecular-biology", 4, 30, "theory", ["前沿"], False),
    ("recombinant-dna",             "重组DNA技术",          "限制酶、连接酶与质粒载体的基因工程基础",               "molecular-biology", 3, 30, "theory", ["技术"], False),
    ("pcr-technology",              "PCR技术",              "聚合酶链式反应的原理与应用",                           "molecular-biology", 3, 25, "theory", ["技术"], False),
    ("gene-editing",                "基因编辑",             "CRISPR-Cas9系统的原理与应用前景",                     "molecular-biology", 4, 30, "theory", ["前沿"], True),
    ("genomics",                    "基因组学",             "全基因组测序、比较基因组学与功能基因组学",             "molecular-biology", 4, 30, "theory", ["组学"], False),
    ("proteomics",                  "蛋白质组学",           "蛋白质组分析技术与功能研究",                           "molecular-biology", 4, 25, "theory", ["组学"], False),
    ("bioinformatics",              "生物信息学",           "序列比对、基因注释与生物数据库",                       "molecular-biology", 4, 30, "theory", ["技术"], False),
    ("molecular-cloning",           "分子克隆",             "基因克隆的策略与载体系统",                             "molecular-biology", 3, 25, "theory", ["技术"], False),
    ("rna-interference",            "RNA干扰",              "siRNA与miRNA介导的基因沉默机制",                      "molecular-biology", 4, 25, "theory", ["调控"], False),
    ("central-dogma",               "中心法则",             "DNA→RNA→蛋白质的遗传信息流动",                        "molecular-biology", 2, 20, "theory", ["核心"], False),
    ("dna-repair",                  "DNA修复",              "错配修复、碱基切除修复与核苷酸切除修复",               "molecular-biology", 3, 25, "theory", ["核酸"], False),

    # ── genetics (22 concepts) ──
    ("genetics-overview",           "遗传学概述",           "遗传学的基本概念、历史与研究方法",                     "genetics", 1, 20, "theory", ["基础"], True),
    ("mendelian-genetics",          "孟德尔遗传",           "分离定律与自由组合定律",                               "genetics", 2, 30, "theory", ["经典"], True),
    ("gene-concept",                "基因概念",             "基因的定义演变与现代基因观",                           "genetics", 2, 25, "theory", ["核心"], False),
    ("alleles-genotype",            "等位基因与基因型",     "显性与隐性、纯合与杂合、基因型与表型",                 "genetics", 2, 25, "theory", ["经典"], False),
    ("chromosomal-inheritance",     "染色体遗传",           "染色体学说、连锁与交换",                               "genetics", 3, 30, "theory", ["经典"], False),
    ("sex-linked-inheritance",      "伴性遗传",             "X连锁遗传与Y连锁遗传模式",                            "genetics", 3, 25, "theory", ["经典"], False),
    ("polygenic-inheritance",       "多基因遗传",           "数量性状遗传与多基因假说",                             "genetics", 3, 25, "theory", ["复杂"], False),
    ("gene-interaction",            "基因互作",             "上位性、互补作用与基因多效性",                         "genetics", 3, 25, "theory", ["复杂"], False),
    ("mutation-types",              "突变类型",             "点突变、插入/缺失与染色体变异",                       "genetics", 2, 25, "theory", ["变异"], True),
    ("chromosomal-abnormalities",   "染色体异常",           "非整倍体、结构畸变与遗传病",                           "genetics", 3, 25, "theory", ["变异"], False),
    ("population-genetics",         "群体遗传学",           "Hardy-Weinberg平衡与等位基因频率",                     "genetics", 4, 30, "theory", ["群体"], True),
    ("quantitative-genetics",       "数量遗传学",           "遗传力、选择响应与数量性状座位",                       "genetics", 4, 30, "theory", ["群体"], False),
    ("human-genetics",              "人类遗传学",           "人类基因组计划、遗传病与遗传咨询",                     "genetics", 3, 30, "theory", ["医学"], False),
    ("genetic-mapping",             "遗传图谱",             "连锁分析、基因定位与基因组作图",                       "genetics", 4, 30, "theory", ["技术"], False),
    ("gene-expression-regulation",  "基因表达调控",         "原核与真核基因表达的多层次调控",                       "genetics", 4, 30, "theory", ["调控"], False),
    ("extranuclear-inheritance",    "核外遗传",             "线粒体遗传与叶绿体遗传",                               "genetics", 3, 25, "theory", ["非经典"], False),
    ("genetic-counseling",          "遗传咨询",             "遗传风险评估与产前诊断",                               "genetics", 3, 25, "theory", ["医学"], False),
    ("behavioral-genetics",         "行为遗传学",           "双生子研究与遗传-环境交互作用",                       "genetics", 4, 25, "theory", ["交叉"], False),
    ("pharmacogenomics",            "药物基因组学",         "基因多态性与个体化用药",                               "genetics", 4, 25, "theory", ["前沿"], False),
    ("genetic-engineering",         "遗传工程",             "转基因技术、基因治疗与合成生物学",                     "genetics", 4, 30, "theory", ["应用"], False),
    ("pedigree-analysis",           "家系分析",             "系谱图绘制与遗传模式判断",                             "genetics", 2, 25, "theory", ["方法"], False),
    ("genetic-drift",               "遗传漂变",             "随机遗传漂变、瓶颈效应与建立者效应",                   "genetics", 3, 25, "theory", ["群体"], False),

    # ── evolution (20 concepts) ──
    ("evolution-overview",          "进化生物学概述",       "进化论的发展历程与核心原理",                           "evolution", 1, 20, "theory", ["基础"], True),
    ("natural-selection",           "自然选择",             "达尔文自然选择理论与适者生存",                         "evolution", 2, 30, "theory", ["核心"], True),
    ("evidence-evolution",          "进化证据",             "化石记录、比较解剖学与分子证据",                       "evolution", 2, 25, "theory", ["证据"], False),
    ("speciation",                  "物种形成",             "地理隔离、生殖隔离与渐进式物种分化",                   "evolution", 3, 30, "theory", ["宏观"], True),
    ("adaptive-radiation",          "适应辐射",             "共同祖先的快速多样化与生态位分化",                     "evolution", 3, 25, "theory", ["宏观"], False),
    ("coevolution",                 "协同进化",             "物种间相互影响的进化过程",                             "evolution", 3, 25, "theory", ["宏观"], False),
    ("sexual-selection",            "性选择",               "性内选择与性间选择的进化机制",                         "evolution", 3, 25, "theory", ["机制"], False),
    ("molecular-evolution",         "分子进化",             "中性进化理论与分子钟假说",                             "evolution", 4, 30, "theory", ["分子"], False),
    ("phylogenetics",               "系统发育",             "进化树构建方法与分子系统学",                           "evolution", 4, 30, "theory", ["方法"], True),
    ("macroevolution",              "宏观进化",             "大灭绝事件、进化趋势与进化速率",                       "evolution", 3, 25, "theory", ["宏观"], False),
    ("microevolution",              "微观进化",             "种群内等位基因频率的变化",                             "evolution", 2, 25, "theory", ["基础"], False),
    ("adaptation",                  "适应",                 "形态、生理与行为适应的进化基础",                       "evolution", 2, 25, "theory", ["核心"], False),
    ("origin-of-life",              "生命起源",             "化学进化、RNA世界假说与原始细胞",                     "evolution", 3, 30, "theory", ["起源"], False),
    ("human-evolution",             "人类进化",             "从南方古猿到智人的进化历程",                           "evolution", 3, 30, "theory", ["人类"], False),
    ("kin-selection",               "亲缘选择",             "Hamilton法则与利他行为的进化解释",                     "evolution", 4, 25, "theory", ["行为"], False),
    ("evolutionary-development",    "进化发育生物学",       "Hox基因、发育约束与evo-devo",                         "evolution", 4, 30, "theory", ["前沿"], False),
    ("convergent-evolution",        "趋同进化",             "不同谱系中相似特征的独立进化",                         "evolution", 3, 20, "theory", ["模式"], False),
    ("divergent-evolution",         "趋异进化",             "同源结构的多样化与辐射适应",                           "evolution", 3, 20, "theory", ["模式"], False),
    ("endosymbiosis",               "内共生学说",           "线粒体与叶绿体的内共生起源",                           "evolution", 3, 25, "theory", ["起源"], False),
    ("extinction",                  "灭绝",                 "物种灭绝的原因、五次大灭绝与当代灭绝危机",             "evolution", 2, 25, "theory", ["宏观"], False),

    # ── human-physiology (24 concepts) ──
    ("physiology-overview",         "人体生理学概述",       "人体生理学的基本原理与稳态概念",                       "human-physiology", 1, 20, "theory", ["基础"], True),
    ("nervous-system",              "神经系统",             "中枢与外周神经系统的结构与功能",                       "human-physiology", 2, 30, "theory", ["系统"], True),
    ("neuron-synapse",              "神经元与突触",         "动作电位产生与突触传递机制",                           "human-physiology", 3, 30, "theory", ["神经"], False),
    ("brain-function",              "脑的功能",             "大脑皮层分区、功能定位与神经可塑性",                   "human-physiology", 3, 30, "theory", ["神经"], False),
    ("endocrine-system",            "内分泌系统",           "激素的分类、作用机制与反馈调节",                       "human-physiology", 2, 30, "theory", ["系统"], True),
    ("cardiovascular-system",       "心血管系统",           "心脏结构、血液循环与血压调节",                         "human-physiology", 2, 30, "theory", ["系统"], False),
    ("respiratory-system",          "呼吸系统",             "肺通气、气体交换与呼吸调节",                           "human-physiology", 2, 25, "theory", ["系统"], False),
    ("digestive-system",            "消化系统",             "消化道结构、酶消化与营养吸收",                         "human-physiology", 2, 25, "theory", ["系统"], False),
    ("immune-system",               "免疫系统",             "先天免疫、适应性免疫与免疫记忆",                       "human-physiology", 3, 35, "theory", ["系统"], True),
    ("immune-cells",                "免疫细胞",             "T细胞、B细胞、巨噬细胞与NK细胞",                     "human-physiology", 3, 25, "theory", ["免疫"], False),
    ("antibody-response",           "抗体反应",             "免疫球蛋白结构、类别转换与亲和力成熟",                 "human-physiology", 3, 25, "theory", ["免疫"], False),
    ("musculoskeletal-system",      "运动系统",             "骨骼肌收缩机制与骨关节结构",                           "human-physiology", 2, 25, "theory", ["系统"], False),
    ("urinary-system",              "泌尿系统",             "肾小球滤过、肾小管重吸收与尿液形成",                   "human-physiology", 2, 25, "theory", ["系统"], False),
    ("reproductive-system",         "生殖系统",             "男女生殖系统结构与配子形成",                           "human-physiology", 2, 25, "theory", ["系统"], False),
    ("homeostasis",                 "稳态",                 "体温调节、血糖调节与酸碱平衡",                         "human-physiology", 2, 30, "theory", ["核心"], True),
    ("blood-composition",           "血液组成",             "血浆、红细胞、白细胞与血小板",                         "human-physiology", 2, 25, "theory", ["血液"], False),
    ("lymphatic-system",            "淋巴系统",             "淋巴循环、淋巴器官与免疫防御",                         "human-physiology", 2, 25, "theory", ["系统"], False),
    ("sensory-system",              "感觉系统",             "视觉、听觉、嗅觉、味觉与触觉机制",                   "human-physiology", 2, 25, "theory", ["神经"], False),
    ("autonomic-nervous-system",    "自主神经系统",         "交感与副交感神经的拮抗调节",                           "human-physiology", 3, 25, "theory", ["神经"], False),
    ("hormone-regulation",          "激素调节",             "下丘脑-垂体轴与反馈调节机制",                         "human-physiology", 3, 25, "theory", ["内分泌"], False),
    ("metabolism-overview",         "代谢概览",             "合成代谢与分解代谢的能量转化",                         "human-physiology", 2, 25, "theory", ["代谢"], False),
    ("nutrition-physiology",        "营养生理学",           "三大营养素的消化、吸收与代谢",                         "human-physiology", 2, 25, "theory", ["营养"], False),
    ("aging-physiology",            "衰老生理学",           "衰老的生理变化与端粒学说",                             "human-physiology", 3, 25, "theory", ["特殊"], False),
    ("exercise-physiology",         "运动生理学",           "运动对心血管、呼吸与肌肉系统的影响",                   "human-physiology", 3, 25, "theory", ["应用"], False),

    # ── ecology (22 concepts) ──
    ("ecology-overview",            "生态学概述",           "生态学的层次、研究方法与基本概念",                     "ecology", 1, 20, "theory", ["基础"], True),
    ("population-ecology",          "种群生态学",           "种群增长模型、容纳量与种群调节",                       "ecology", 2, 30, "theory", ["种群"], True),
    ("community-ecology",           "群落生态学",           "群落结构、物种多样性与演替",                           "ecology", 3, 30, "theory", ["群落"], True),
    ("ecosystem-ecology",           "生态系统生态学",       "能量流动与物质循环的基本规律",                         "ecology", 3, 30, "theory", ["生态系统"], True),
    ("food-web",                    "食物网",               "营养级、食物链与能量金字塔",                           "ecology", 2, 25, "theory", ["生态系统"], False),
    ("nutrient-cycling",            "物质循环",             "碳循环、氮循环与磷循环",                               "ecology", 3, 25, "theory", ["生态系统"], False),
    ("biomes",                      "生物群落",             "陆地与水生生物群落的分布与特征",                       "ecology", 2, 25, "theory", ["宏观"], False),
    ("species-interactions",        "种间关系",             "竞争、捕食、互利共生与寄生",                           "ecology", 2, 25, "theory", ["群落"], False),
    ("biodiversity",                "生物多样性",           "物种多样性、遗传多样性与生态系统多样性",               "ecology", 2, 25, "theory", ["保护"], True),
    ("conservation-biology",        "保护生物学",           "濒危物种保护策略与栖息地管理",                         "ecology", 3, 30, "theory", ["保护"], False),
    ("ecological-succession",       "生态演替",             "初生演替与次生演替的过程与机制",                       "ecology", 3, 25, "theory", ["动态"], False),
    ("niche-theory",                "生态位理论",           "基础生态位与实际生态位的概念",                         "ecology", 3, 25, "theory", ["核心"], False),
    ("island-biogeography",         "岛屿生物地理学",       "岛屿面积-物种数关系与MacArthur-Wilson模型",            "ecology", 4, 25, "theory", ["理论"], False),
    ("climate-change-ecology",      "气候变化与生态",       "全球变暖对生态系统的影响与碳循环",                     "ecology", 3, 30, "theory", ["全球"], False),
    ("ecosystem-services",          "生态系统服务",         "供给、调节、文化与支持服务",                           "ecology", 2, 25, "theory", ["应用"], False),
    ("behavioral-ecology",          "行为生态学",           "觅食策略、领地行为与动物通讯",                         "ecology", 3, 25, "theory", ["行为"], False),
    ("population-dynamics",         "种群动态",             "Lotka-Volterra模型与种群波动",                        "ecology", 4, 30, "theory", ["数学"], False),
    ("landscape-ecology",           "景观生态学",           "斑块-廊道-基质模型与景观格局",                        "ecology", 4, 25, "theory", ["宏观"], False),
    ("marine-ecology",              "海洋生态学",           "海洋生态系统的结构与功能特征",                         "ecology", 3, 25, "theory", ["水生"], False),
    ("freshwater-ecology",          "淡水生态学",           "河流与湖泊生态系统的特征与保护",                       "ecology", 3, 25, "theory", ["水生"], False),
    ("restoration-ecology",         "恢复生态学",           "退化生态系统的修复原理与技术",                         "ecology", 4, 25, "theory", ["应用"], False),
    ("urban-ecology",               "城市生态学",           "城市生态系统的结构与人类活动影响",                     "ecology", 3, 25, "theory", ["应用"], False),

    # ── microbiology (20 concepts) ──
    ("microbiology-overview",       "微生物学概述",         "微生物的分类、发现史与研究方法",                       "microbiology", 1, 20, "theory", ["基础"], True),
    ("bacteria-structure",          "细菌结构",             "细菌细胞壁、鞭毛、荚膜与芽孢",                       "microbiology", 2, 25, "theory", ["细菌"], False),
    ("bacterial-metabolism",        "细菌代谢",             "细菌的能量代谢与生物合成途径",                         "microbiology", 3, 25, "theory", ["细菌"], False),
    ("bacterial-genetics",          "细菌遗传",             "转化、转导与接合等基因转移方式",                       "microbiology", 3, 25, "theory", ["细菌"], False),
    ("virus-biology",               "病毒生物学",           "病毒结构、分类与复制周期",                             "microbiology", 2, 30, "theory", ["病毒"], True),
    ("viral-replication",           "病毒复制",             "裂解循环与溶原循环的分子机制",                         "microbiology", 3, 25, "theory", ["病毒"], False),
    ("fungi-biology",               "真菌生物学",           "真菌的结构、生殖与生态角色",                           "microbiology", 2, 25, "theory", ["真菌"], False),
    ("protists",                    "原生生物",             "原生动物与藻类的多样性",                               "microbiology", 2, 25, "theory", ["多样性"], False),
    ("antibiotic-resistance",       "抗生素耐药性",         "耐药机制的产生与全球健康威胁",                         "microbiology", 3, 25, "theory", ["医学"], True),
    ("microbiome",                  "微生物组",             "人体微生物组的组成与健康影响",                         "microbiology", 3, 30, "theory", ["前沿"], False),
    ("pathogenic-mechanisms",       "致病机制",             "病原微生物的毒力因子与致病策略",                       "microbiology", 3, 25, "theory", ["医学"], False),
    ("immune-evasion",              "免疫逃逸",             "病原体逃避宿主免疫防御的策略",                         "microbiology", 4, 25, "theory", ["医学"], False),
    ("vaccine-biology",             "疫苗生物学",           "疫苗类型、免疫原理与疫苗开发",                         "microbiology", 3, 30, "theory", ["医学"], True),
    ("food-microbiology",           "食品微生物学",         "发酵食品、食品腐败与食品安全",                         "microbiology", 2, 25, "theory", ["应用"], False),
    ("environmental-microbiology",  "环境微生物学",         "微生物在生物地球化学循环中的作用",                     "microbiology", 3, 25, "theory", ["环境"], False),
    ("industrial-microbiology",     "工业微生物学",         "微生物发酵、生物制药与生物能源",                       "microbiology", 3, 25, "theory", ["应用"], False),
    ("archaea",                     "古菌",                 "古菌的发现、分类与极端环境适应",                       "microbiology", 3, 25, "theory", ["多样性"], False),
    ("biofilm",                     "生物膜",               "微生物群落的生物膜形成与临床意义",                     "microbiology", 3, 25, "theory", ["生态"], False),
    ("prions",                      "朊病毒",               "蛋白质错误折叠引起的传染性疾病",                       "microbiology", 4, 20, "theory", ["特殊"], False),
    ("emerging-infectious",         "新发传染病",           "新发传染病的起源、传播与防控",                         "microbiology", 3, 25, "theory", ["公卫"], False),

    # ── botany-zoology (20 concepts) ──
    ("botany-zoology-overview",     "植物与动物学概述",     "多细胞生物的分类体系与比较研究",                       "botany-zoology", 1, 20, "theory", ["基础"], True),
    ("plant-anatomy",               "植物解剖学",           "根、茎、叶的组织结构与功能",                           "botany-zoology", 2, 25, "theory", ["植物"], False),
    ("plant-physiology",            "植物生理学",           "水分运输、矿质营养与气孔调节",                         "botany-zoology", 2, 30, "theory", ["植物"], True),
    ("plant-reproduction",          "植物繁殖",             "有性生殖与无性生殖策略",                               "botany-zoology", 2, 25, "theory", ["植物"], False),
    ("plant-hormones",              "植物激素",             "生长素、赤霉素、细胞分裂素等的作用",                   "botany-zoology", 3, 25, "theory", ["植物"], False),
    ("plant-responses",             "植物应答",             "向光性、向地性与逆境响应",                             "botany-zoology", 3, 25, "theory", ["植物"], False),
    ("animal-diversity",            "动物多样性",           "从无脊椎动物到脊椎动物的分类与特征",                   "botany-zoology", 2, 30, "theory", ["动物"], True),
    ("invertebrate-biology",        "无脊椎动物生物学",     "节肢动物、软体动物与棘皮动物",                         "botany-zoology", 2, 25, "theory", ["动物"], False),
    ("vertebrate-biology",          "脊椎动物生物学",       "鱼类、两栖、爬行、鸟类与哺乳动物",                   "botany-zoology", 2, 25, "theory", ["动物"], False),
    ("animal-behavior",             "动物行为学",           "先天行为、学习行为与社会行为",                         "botany-zoology", 3, 25, "theory", ["行为"], True),
    ("embryology",                  "胚胎学",               "受精、卵裂、原肠胚形成与器官发生",                     "botany-zoology", 3, 30, "theory", ["发育"], False),
    ("comparative-anatomy",         "比较解剖学",           "同源器官、同功器官与痕迹器官",                         "botany-zoology", 2, 25, "theory", ["比较"], False),
    ("plant-classification",        "植物分类",             "苔藓、蕨类、裸子与被子植物的分类体系",                 "botany-zoology", 2, 25, "theory", ["分类"], False),
    ("seed-biology",                "种子生物学",           "种子结构、休眠与萌发机制",                             "botany-zoology", 2, 25, "theory", ["植物"], False),
    ("animal-physiology-comp",      "动物比较生理学",       "不同动物类群的生理适应策略",                           "botany-zoology", 3, 25, "theory", ["比较"], False),
    ("pollination-ecology",         "传粉生态学",           "传粉者多样性与植物-传粉者协同进化",                   "botany-zoology", 3, 25, "theory", ["生态"], False),
    ("migration-hibernation",       "迁徙与冬眠",           "动物的季节性行为适应策略",                             "botany-zoology", 3, 25, "theory", ["行为"], False),
    ("symbiosis",                   "共生关系",             "互利共生、共栖与寄生的生物学基础",                     "botany-zoology", 2, 25, "theory", ["生态"], False),
    ("developmental-biology",       "发育生物学",           "模式生物中的形态发生与细胞分化",                       "botany-zoology", 4, 30, "theory", ["发育"], False),
    ("biomimetics",                 "仿生学",               "从生物结构与功能中汲取工程灵感",                       "botany-zoology", 3, 25, "theory", ["应用"], False),
]


def build_edges(concepts):
    """Build prerequisite and related edges between concepts."""
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

    # ── cell-biology ──
    edge("cell-biology-overview", "prokaryotic-cells")
    edge("cell-biology-overview", "eukaryotic-cells")
    edge("eukaryotic-cells", "cell-membrane")
    edge("cell-membrane", "membrane-transport")
    edge("eukaryotic-cells", "endoplasmic-reticulum")
    edge("eukaryotic-cells", "golgi-apparatus")
    edge("endoplasmic-reticulum", "golgi-apparatus", "related", 0.7)
    edge("eukaryotic-cells", "mitochondria")
    edge("eukaryotic-cells", "chloroplast")
    edge("eukaryotic-cells", "nucleus")
    edge("eukaryotic-cells", "cytoskeleton")
    edge("cell-biology-overview", "cell-cycle")
    edge("cell-cycle", "mitosis")
    edge("cell-cycle", "meiosis")
    edge("cell-cycle", "apoptosis")
    edge("cell-biology-overview", "cell-signaling")
    edge("cell-signaling", "stem-cells", "related", 0.5)
    edge("mitochondria", "cellular-respiration")
    edge("chloroplast", "photosynthesis")
    edge("cell-cycle", "cell-differentiation")
    edge("eukaryotic-cells", "lysosomes-peroxisomes")
    edge("endoplasmic-reticulum", "endomembrane-system")
    edge("golgi-apparatus", "endomembrane-system", "related", 0.7)
    edge("lysosomes-peroxisomes", "endomembrane-system", "related", 0.6)

    # ── molecular-biology ──
    edge("molecular-biology-overview", "dna-structure")
    edge("molecular-biology-overview", "central-dogma")
    edge("dna-structure", "rna-types")
    edge("dna-structure", "dna-replication")
    edge("dna-structure", "dna-repair")
    edge("central-dogma", "transcription")
    edge("central-dogma", "translation")
    edge("transcription", "translation")
    edge("transcription", "gene-regulation")
    edge("molecular-biology-overview", "protein-structure")
    edge("protein-structure", "enzyme-function")
    edge("translation", "protein-modification")
    edge("cell-signaling", "signal-transduction-mol", "related", 0.7)
    edge("gene-regulation", "epigenetics")
    edge("dna-structure", "recombinant-dna")
    edge("recombinant-dna", "molecular-cloning")
    edge("dna-replication", "pcr-technology")
    edge("gene-regulation", "gene-editing")
    edge("recombinant-dna", "gene-editing", "related", 0.6)
    edge("dna-structure", "genomics")
    edge("protein-structure", "proteomics")
    edge("genomics", "bioinformatics")
    edge("proteomics", "bioinformatics", "related", 0.6)
    edge("gene-regulation", "rna-interference")
    edge("rna-types", "rna-interference", "related", 0.6)

    # ── genetics ──
    edge("genetics-overview", "mendelian-genetics")
    edge("genetics-overview", "gene-concept")
    edge("mendelian-genetics", "alleles-genotype")
    edge("mendelian-genetics", "chromosomal-inheritance")
    edge("chromosomal-inheritance", "sex-linked-inheritance")
    edge("mendelian-genetics", "polygenic-inheritance")
    edge("mendelian-genetics", "gene-interaction")
    edge("gene-concept", "mutation-types")
    edge("mutation-types", "chromosomal-abnormalities")
    edge("mendelian-genetics", "population-genetics")
    edge("population-genetics", "quantitative-genetics")
    edge("genetics-overview", "human-genetics")
    edge("chromosomal-inheritance", "genetic-mapping")
    edge("gene-regulation", "gene-expression-regulation", "related", 0.8)
    edge("genetics-overview", "extranuclear-inheritance")
    edge("human-genetics", "genetic-counseling")
    edge("genetics-overview", "behavioral-genetics")
    edge("human-genetics", "pharmacogenomics")
    edge("recombinant-dna", "genetic-engineering", "related", 0.7)
    edge("gene-editing", "genetic-engineering", "related", 0.7)
    edge("mendelian-genetics", "pedigree-analysis")
    edge("population-genetics", "genetic-drift")

    # ── evolution ──
    edge("evolution-overview", "natural-selection")
    edge("evolution-overview", "evidence-evolution")
    edge("natural-selection", "speciation")
    edge("speciation", "adaptive-radiation")
    edge("natural-selection", "coevolution")
    edge("natural-selection", "sexual-selection")
    edge("natural-selection", "molecular-evolution")
    edge("molecular-evolution", "phylogenetics")
    edge("speciation", "macroevolution")
    edge("evolution-overview", "microevolution")
    edge("natural-selection", "adaptation")
    edge("evolution-overview", "origin-of-life")
    edge("phylogenetics", "human-evolution")
    edge("natural-selection", "kin-selection")
    edge("evolution-overview", "evolutionary-development")
    edge("adaptation", "convergent-evolution")
    edge("speciation", "divergent-evolution")
    edge("origin-of-life", "endosymbiosis")
    edge("macroevolution", "extinction")
    edge("population-genetics", "microevolution", "related", 0.7)
    edge("genetic-drift", "microevolution", "related", 0.6)

    # ── human-physiology ──
    edge("physiology-overview", "nervous-system")
    edge("nervous-system", "neuron-synapse")
    edge("neuron-synapse", "brain-function")
    edge("physiology-overview", "endocrine-system")
    edge("physiology-overview", "cardiovascular-system")
    edge("physiology-overview", "respiratory-system")
    edge("physiology-overview", "digestive-system")
    edge("physiology-overview", "immune-system")
    edge("immune-system", "immune-cells")
    edge("immune-cells", "antibody-response")
    edge("physiology-overview", "musculoskeletal-system")
    edge("physiology-overview", "urinary-system")
    edge("physiology-overview", "reproductive-system")
    edge("physiology-overview", "homeostasis")
    edge("cardiovascular-system", "blood-composition")
    edge("immune-system", "lymphatic-system", "related", 0.7)
    edge("nervous-system", "sensory-system")
    edge("nervous-system", "autonomic-nervous-system")
    edge("endocrine-system", "hormone-regulation")
    edge("physiology-overview", "metabolism-overview")
    edge("digestive-system", "nutrition-physiology")
    edge("homeostasis", "aging-physiology", "related", 0.5)
    edge("cardiovascular-system", "exercise-physiology", "related", 0.6)
    edge("respiratory-system", "exercise-physiology", "related", 0.5)

    # ── ecology ──
    edge("ecology-overview", "population-ecology")
    edge("population-ecology", "community-ecology")
    edge("community-ecology", "ecosystem-ecology")
    edge("ecosystem-ecology", "food-web")
    edge("ecosystem-ecology", "nutrient-cycling")
    edge("ecology-overview", "biomes")
    edge("community-ecology", "species-interactions")
    edge("ecology-overview", "biodiversity")
    edge("biodiversity", "conservation-biology")
    edge("community-ecology", "ecological-succession")
    edge("community-ecology", "niche-theory")
    edge("biodiversity", "island-biogeography")
    edge("ecosystem-ecology", "climate-change-ecology")
    edge("ecology-overview", "ecosystem-services")
    edge("ecology-overview", "behavioral-ecology")
    edge("population-ecology", "population-dynamics")
    edge("ecology-overview", "landscape-ecology")
    edge("ecology-overview", "marine-ecology")
    edge("ecology-overview", "freshwater-ecology")
    edge("conservation-biology", "restoration-ecology")
    edge("ecology-overview", "urban-ecology")

    # ── microbiology ──
    edge("microbiology-overview", "bacteria-structure")
    edge("bacteria-structure", "bacterial-metabolism")
    edge("bacteria-structure", "bacterial-genetics")
    edge("microbiology-overview", "virus-biology")
    edge("virus-biology", "viral-replication")
    edge("microbiology-overview", "fungi-biology")
    edge("microbiology-overview", "protists")
    edge("bacterial-genetics", "antibiotic-resistance")
    edge("microbiology-overview", "microbiome")
    edge("virus-biology", "pathogenic-mechanisms")
    edge("bacteria-structure", "pathogenic-mechanisms", "related", 0.6)
    edge("pathogenic-mechanisms", "immune-evasion")
    edge("immune-system", "vaccine-biology", "related", 0.7)
    edge("virus-biology", "vaccine-biology", "related", 0.6)
    edge("microbiology-overview", "food-microbiology")
    edge("microbiology-overview", "environmental-microbiology")
    edge("microbiology-overview", "industrial-microbiology")
    edge("microbiology-overview", "archaea")
    edge("bacteria-structure", "biofilm")
    edge("virus-biology", "prions", "related", 0.4)
    edge("pathogenic-mechanisms", "emerging-infectious")

    # ── botany-zoology ──
    edge("botany-zoology-overview", "plant-anatomy")
    edge("plant-anatomy", "plant-physiology")
    edge("botany-zoology-overview", "plant-reproduction")
    edge("plant-physiology", "plant-hormones")
    edge("plant-hormones", "plant-responses")
    edge("botany-zoology-overview", "animal-diversity")
    edge("animal-diversity", "invertebrate-biology")
    edge("animal-diversity", "vertebrate-biology")
    edge("botany-zoology-overview", "animal-behavior")
    edge("botany-zoology-overview", "embryology")
    edge("botany-zoology-overview", "comparative-anatomy")
    edge("botany-zoology-overview", "plant-classification")
    edge("plant-reproduction", "seed-biology")
    edge("vertebrate-biology", "animal-physiology-comp")
    edge("plant-reproduction", "pollination-ecology")
    edge("animal-behavior", "migration-hibernation")
    edge("species-interactions", "symbiosis", "related", 0.6)
    edge("embryology", "developmental-biology")
    edge("comparative-anatomy", "biomimetics", "related", 0.5)

    # ── cross-subdomain edges ──
    edge("mitochondria", "endosymbiosis", "related", 0.7)
    edge("chloroplast", "endosymbiosis", "related", 0.7)
    edge("dna-structure", "mendelian-genetics", "related", 0.5)
    edge("gene-concept", "central-dogma", "related", 0.6)
    edge("meiosis", "mendelian-genetics", "related", 0.7)
    edge("mutation-types", "natural-selection", "related", 0.6)
    edge("population-genetics", "natural-selection", "related", 0.7)
    edge("immune-system", "pathogenic-mechanisms", "related", 0.6)
    edge("vaccine-biology", "antibody-response", "related", 0.7)
    edge("photosynthesis", "nutrient-cycling", "related", 0.5)
    edge("cellular-respiration", "metabolism-overview", "related", 0.6)
    edge("neuron-synapse", "cell-signaling", "related", 0.6)
    edge("cell-differentiation", "embryology", "related", 0.7)
    edge("gene-regulation", "cell-differentiation", "related", 0.7)
    edge("antibiotic-resistance", "natural-selection", "related", 0.6)
    edge("biodiversity", "extinction", "related", 0.6)
    edge("evolutionary-development", "embryology", "related", 0.7)
    edge("human-evolution", "comparative-anatomy", "related", 0.5)
    edge("microbiome", "immune-system", "related", 0.5)
    edge("behavioral-ecology", "animal-behavior", "related", 0.7)
    edge("coevolution", "pollination-ecology", "related", 0.6)
    edge("photosynthesis", "plant-physiology", "related", 0.7)
    edge("plant-hormones", "gene-regulation", "related", 0.4)
    edge("epigenetics", "cell-differentiation", "related", 0.6)
    edge("genomics", "human-genetics", "related", 0.6)
    edge("climate-change-ecology", "conservation-biology", "related", 0.7)

    return edges


def main():
    concepts = []
    for (cid, name, desc, sub, diff, mins, ctype, tags, ms) in CONCEPTS_RAW:
        concepts.append({
            "id": cid,
            "name": name,
            "description": desc,
            "subdomain_id": sub,
            "domain_id": "biology",
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

    print(f"✅ Generated biology seed graph:")
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
