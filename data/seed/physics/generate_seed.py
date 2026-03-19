#!/usr/bin/env python3
"""Generate physics knowledge sphere seed graph.

Target: ~200 concepts, ~260 edges, 10 subdomains, ~25 milestones
Domain: physics (🟢 #22c55e)
"""

import json
from datetime import datetime, timezone

NOW = datetime.now(timezone.utc).isoformat()

DOMAIN = {
    "id": "physics",
    "name": "物理",
    "description": "从经典力学到量子力学的系统知识体系",
    "icon": "🟢",
    "color": "#22c55e"
}

SUBDOMAINS = [
    {"id": "classical-mechanics",  "name": "经典力学",   "order": 1},
    {"id": "thermodynamics",       "name": "热力学",     "order": 2},
    {"id": "waves-and-optics",     "name": "波动与光学", "order": 3},
    {"id": "electromagnetism",     "name": "电磁学",     "order": 4},
    {"id": "modern-physics",       "name": "近代物理",   "order": 5},
    {"id": "quantum-mechanics",    "name": "量子力学",   "order": 6},
    {"id": "nuclear-physics",      "name": "核物理",     "order": 7},
    {"id": "astrophysics",         "name": "天体物理",   "order": 8},
    {"id": "fluid-mechanics",      "name": "流体力学",   "order": 9},
    {"id": "solid-state-physics",  "name": "固态物理",   "order": 10},
]

# ── concepts per subdomain ──────────────────────────────────────────────
# Format: (id, name, description, difficulty, content_type, tags, is_milestone)

CONCEPTS_BY_SUBDOMAIN = {
    "classical-mechanics": [
        ("physical-quantities",      "物理量与单位",           "SI单位制、量纲分析、有效数字", 1, "theory", ["基础"], False),
        ("vectors-in-physics",       "物理中的向量",           "向量分解、合成、标量积与矢量积在物理中的应用", 2, "theory", ["基础"], False),
        ("kinematics-1d",            "一维运动学",             "位移、速度、加速度、匀变速运动方程", 2, "theory", ["基础"], False),
        ("kinematics-2d",            "二维运动学",             "抛体运动、圆周运动的运动学描述", 3, "theory", ["核心"], False),
        ("newtons-first-law",        "牛顿第一定律",           "惯性、惯性参考系的概念", 2, "theory", ["核心"], False),
        ("newtons-second-law",       "牛顿第二定律",           "F=ma、力的叠加原理、自由体图", 3, "theory", ["里程碑"], True),
        ("newtons-third-law",        "牛顿第三定律",           "作用力与反作用力、力的相互性", 2, "theory", ["核心"], False),
        ("friction",                 "摩擦力",                 "静摩擦、动摩擦、摩擦系数", 3, "theory", ["核心"], False),
        ("circular-motion",          "圆周运动",               "向心加速度、向心力、匀速与非匀速圆周运动", 4, "theory", ["核心"], False),
        ("work-energy",              "功与能",                 "功的定义、动能定理、功率", 3, "theory", ["核心"], False),
        ("potential-energy",         "势能",                   "重力势能、弹性势能、保守力与势能函数", 4, "theory", ["核心"], False),
        ("energy-conservation",      "能量守恒",               "机械能守恒定律、能量转化与耗散", 4, "theory", ["里程碑"], True),
        ("momentum",                 "动量与冲量",             "动量定义、冲量-动量定理", 3, "theory", ["核心"], False),
        ("momentum-conservation",    "动量守恒",               "动量守恒定律、碰撞问题", 4, "theory", ["里程碑"], True),
        ("collisions",               "碰撞",                   "弹性碰撞、完全非弹性碰撞、能量损失", 4, "theory", ["核心"], False),
        ("rotational-kinematics",    "转动运动学",             "角位移、角速度、角加速度、匀角加速运动", 4, "theory", ["核心"], False),
        ("torque",                   "力矩",                   "力矩的定义、力臂、合力矩", 4, "theory", ["核心"], False),
        ("rotational-dynamics",      "转动动力学",             "转动惯量、τ=Iα、平行轴定理", 5, "theory", ["里程碑"], True),
        ("angular-momentum",         "角动量",                 "角动量定义、角动量守恒定律", 5, "theory", ["核心"], False),
        ("static-equilibrium",       "静力学平衡",             "力平衡与力矩平衡条件、重心", 3, "theory", ["核心"], False),
        ("gravitation",              "万有引力",               "万有引力定律、引力势能、开普勒定律", 4, "theory", ["里程碑"], True),
        ("orbital-mechanics",        "轨道力学",               "圆轨道、椭圆轨道、逃逸速度、宇宙速度", 5, "theory", ["进阶"], False),
        ("simple-harmonic-motion",   "简谐运动",               "弹簧振子、单摆、周期与频率、相位", 4, "theory", ["核心"], False),
        ("damped-driven-oscillation","阻尼与受迫振动",         "阻尼振动、共振现象、品质因子", 5, "theory", ["进阶"], False),
        ("non-inertial-frames",      "非惯性系",               "惯性力、科里奥利力、离心力", 5, "theory", ["进阶"], False),
        ("projectile-motion",        "抛体运动",               "斜抛运动分析、射程与最大高度", 3, "theory", ["应用"], False),
        ("elastic-force",            "弹性力",                 "胡克定律、弹簧系统、弹性势能", 3, "theory", ["核心"], False),
        ("center-of-mass",           "质心",                   "质心定义、质心运动定理、质心坐标", 4, "theory", ["核心"], False),
        ("rigid-body-motion",        "刚体运动",               "平动与转动、定轴转动、滚动", 5, "theory", ["进阶"], False),
        ("coupled-oscillations",     "耦合振动",               "耦合振子、简正模、节拍", 5, "theory", ["进阶"], False),
        ("mechanical-waves-medium",  "介质中的机械波",         "弦上的波、棒中的纵波、波的能量传输", 4, "theory", ["核心"], False),
        ("lagrangian-mechanics",     "拉格朗日力学初步",       "广义坐标、拉格朗日方程、变分原理", 6, "theory", ["进阶"], False),
        ("hamiltonian-mechanics",    "哈密顿力学初步",         "哈密顿量、相空间、正则方程", 7, "theory", ["拓展"], False),
        ("keplers-laws",             "开普勒定律",             "三大定律、椭圆轨道、面积速度", 4, "theory", ["核心"], False),
        ("tidal-forces",             "潮汐力",                 "引力差异、潮汐加热、洛希极限", 5, "theory", ["进阶"], False),
    ],
    "thermodynamics": [
        ("temperature-heat",         "温度与热量",             "温度标度、热量的微观本质、热平衡", 2, "theory", ["基础"], False),
        ("ideal-gas-law",            "理想气体定律",           "PV=nRT、气体状态方程、等温/等压/等容过程", 3, "theory", ["核心"], False),
        ("kinetic-theory",           "气体动理论",             "分子运动、压强的微观解释、麦克斯韦速率分布", 4, "theory", ["核心"], False),
        ("heat-transfer",            "传热方式",               "热传导、对流、辐射、傅里叶热传导定律", 3, "theory", ["核心"], False),
        ("specific-heat",            "比热容与热容量",         "比热容、相变潜热、量热学实验", 3, "theory", ["基础"], False),
        ("first-law-thermo",         "热力学第一定律",         "内能、功与热的关系、ΔU=Q-W", 4, "theory", ["里程碑"], True),
        ("thermodynamic-processes",  "热力学过程",             "等温、绝热、等压、等容过程的PV图分析", 4, "theory", ["核心"], False),
        ("second-law-thermo",        "热力学第二定律",         "卡诺定理、克劳修斯表述、开尔文表述", 5, "theory", ["里程碑"], True),
        ("entropy",                  "熵",                     "熵的定义、熵增原理、统计诠释", 5, "theory", ["里程碑"], True),
        ("heat-engines",             "热机",                   "卡诺循环、效率、制冷机与热泵", 4, "theory", ["应用"], False),
        ("phase-transitions",        "相变",                   "熔化、汽化、升华、相图、临界点", 4, "theory", ["核心"], False),
        ("free-energy",              "自由能",                 "亥姆霍兹自由能、吉布斯自由能、热力学势", 6, "theory", ["进阶"], False),
        ("thermal-expansion",        "热膨胀",                 "线膨胀、体膨胀、膨胀系数", 2, "theory", ["基础"], False),
        ("statistical-mechanics",    "统计力学初步",           "玻尔兹曼分布、配分函数、能量均分定理", 6, "theory", ["进阶"], False),
        ("third-law-thermo",         "热力学第三定律",         "绝对零度不可达、低温极限下熵趋于零", 5, "theory", ["核心"], False),
        ("carnot-theorem",           "卡诺定理",               "可逆热机效率最高、卡诺效率公式", 5, "theory", ["核心"], False),
        ("maxwell-relations",        "麦克斯韦关系",           "热力学势的偏导数关系、全微分条件", 6, "theory", ["进阶"], False),
        ("real-gases",               "实际气体",               "范德瓦尔斯方程、临界常数、对比态定律", 5, "theory", ["进阶"], False),
        ("boltzmann-distribution",   "玻尔兹曼分布",           "能量分布函数、配分函数、熵的统计定义", 6, "theory", ["进阶"], False),
        ("adiabatic-process",        "绝热过程",               "绝热方程、绝热膨胀做功、绝热指数", 4, "theory", ["核心"], False),
        ("enthalpy",                 "焓",                     "焓的定义H=U+PV、等压过程的焓变", 5, "theory", ["核心"], False),
        ("irreversibility",         "不可逆过程",             "自发过程、耗散、自由膨胀", 5, "theory", ["核心"], False),
    ],
    "waves-and-optics": [
        ("wave-basics",              "波的基本概念",           "横波与纵波、波长、频率、波速", 3, "theory", ["基础"], False),
        ("wave-equation",            "波动方程",               "一维波方程、行波解、波的数学描述", 4, "theory", ["核心"], False),
        ("superposition",            "波的叠加",               "叠加原理、干涉、驻波", 4, "theory", ["核心"], False),
        ("sound-waves",              "声波",                   "声速、声强、多普勒效应", 3, "theory", ["核心"], False),
        ("resonance",                "共振",                   "受迫振动共振、自然频率、品质因子", 4, "theory", ["核心"], False),
        ("reflection-refraction",    "反射与折射",             "反射定律、折射定律(Snell's law)、全内反射", 3, "theory", ["核心"], False),
        ("geometric-optics",         "几何光学",               "薄透镜成像、镜面成像、光线追迹", 4, "theory", ["里程碑"], True),
        ("interference",             "光的干涉",               "杨氏双缝实验、薄膜干涉、等厚干涉", 5, "theory", ["里程碑"], True),
        ("diffraction",              "光的衍射",               "单缝衍射、圆孔衍射、衍射光栅", 5, "theory", ["核心"], False),
        ("polarization",             "光的偏振",               "偏振态、马吕斯定律、布儒斯特角", 5, "theory", ["核心"], False),
        ("dispersion",               "色散",                   "折射率与波长关系、棱镜色散、光谱", 4, "theory", ["核心"], False),
        ("optical-instruments",      "光学仪器",               "显微镜、望远镜、分辨率(瑞利判据)", 4, "theory", ["应用"], False),
        ("wave-particle-duality",    "波粒二象性",             "光的粒子性与波动性、德布罗意波长", 5, "theory", ["里程碑"], True),
        ("electromagnetic-waves",    "电磁波",                 "电磁波谱、赫兹实验、电磁波的能量与动量", 4, "theory", ["核心"], False),
        ("fiber-optics",             "光纤与光通信",           "全内反射应用、光纤原理、通信基础", 4, "theory", ["应用"], False),
        ("huygens-principle",        "惠更斯原理",             "波前传播、次波源、折射的波动解释", 4, "theory", ["核心"], False),
        ("doppler-effect-light",     "光的多普勒效应",         "红移与蓝移、相对论多普勒效应", 5, "theory", ["核心"], False),
        ("holography",               "全息术",                 "全息记录与再现原理、全息干涉测量", 5, "theory", ["拓展"], False),
        ("nonlinear-optics-intro",   "非线性光学简介",         "倍频、自聚焦、光学参量效应", 6, "theory", ["拓展"], False),
    ],
    "electromagnetism": [
        ("electric-charge",          "电荷",                   "电荷守恒、库仑定律、电荷量子化", 2, "theory", ["基础"], False),
        ("electric-field",           "电场",                   "电场强度、电场线、点电荷的电场", 3, "theory", ["核心"], False),
        ("gauss-law",                "高斯定律",               "电通量、高斯定理、对称性应用", 4, "theory", ["里程碑"], True),
        ("electric-potential",       "电势",                   "电势的定义、等势面、电势差与功", 4, "theory", ["核心"], False),
        ("capacitance",              "电容",                   "电容器、平行板电容、介电质、电场能量", 4, "theory", ["核心"], False),
        ("dc-circuits",              "直流电路",               "欧姆定律、串并联、基尔霍夫定律", 3, "theory", ["核心"], False),
        ("rc-circuits",              "RC电路",                 "充放电过程、时间常数、暂态分析", 4, "theory", ["进阶"], False),
        ("magnetic-field",           "磁场",                   "磁感应强度、磁力线、载流导线的磁场", 4, "theory", ["核心"], False),
        ("lorentz-force",            "洛伦兹力",               "运动电荷在磁场中的受力、带电粒子回旋", 4, "theory", ["核心"], False),
        ("biot-savart",              "毕奥-萨伐尔定律",       "电流元产生的磁场、直导线与环形电流", 5, "theory", ["核心"], False),
        ("amperes-law",              "安培定律",               "安培环路定理、螺线管磁场", 5, "theory", ["里程碑"], True),
        ("faradays-law",             "法拉第电磁感应",         "感应电动势、楞次定律、法拉第定律", 5, "theory", ["里程碑"], True),
        ("inductance",               "电感",                   "自感、互感、RL电路、磁场能量", 5, "theory", ["核心"], False),
        ("ac-circuits",              "交流电路",               "交流电基本量、阻抗、RLC串联谐振", 5, "theory", ["核心"], False),
        ("maxwells-equations",       "麦克斯韦方程组",         "四个方程统一电磁理论、位移电流", 6, "theory", ["里程碑"], True),
        ("electromagnetic-radiation","电磁辐射",               "加速电荷辐射、天线原理、Larmor公式", 5, "theory", ["进阶"], False),
        ("em-energy-poynting",       "电磁能与坡印廷矢量",   "能量密度、坡印廷矢量、辐射压", 5, "theory", ["进阶"], False),
        ("dielectrics",              "电介质",                 "极化、介电常数、电极化强度", 5, "theory", ["进阶"], False),
        ("magnetic-materials",       "磁性材料",               "顺磁、抗磁、铁磁、磁化强度、磁滞", 5, "theory", ["进阶"], False),
        ("superconductivity-intro",  "超导简介",               "迈斯纳效应、BCS理论简介、临界温度", 6, "theory", ["拓展"], False),
        ("electric-dipole",          "电偶极子",               "偶极矩、偶极子电场、极化", 4, "theory", ["核心"], False),
        ("magnetic-dipole",          "磁偶极子",               "磁矩、载流线圈的磁矩、磁场中的力矩", 4, "theory", ["核心"], False),
        ("kirchhoffs-laws",          "基尔霍夫定律",           "节点电流定律、回路电压定律、复杂电路分析", 3, "theory", ["核心"], False),
        ("power-transmission",       "电能传输",               "变压器原理、高压输电、功率损耗", 4, "theory", ["应用"], False),
        ("electromagnetic-induction-app", "电磁感应应用",     "发电机、电动机、涡流、电磁制动", 4, "theory", ["应用"], False),
    ],
    "modern-physics": [
        ("special-relativity-postulates", "狭义相对论公设",     "光速不变原理、相对性原理", 5, "theory", ["里程碑"], True),
        ("time-dilation",            "时间膨胀",               "运动时钟变慢、洛伦兹因子γ", 5, "theory", ["核心"], False),
        ("length-contraction",       "长度收缩",               "运动方向上的长度缩短", 5, "theory", ["核心"], False),
        ("lorentz-transformations",  "洛伦兹变换",             "洛伦兹变换公式、同时性的相对性", 5, "theory", ["核心"], False),
        ("relativistic-momentum-energy", "相对论性动量与能量", "E=mc²、质能等价、四维动量", 5, "theory", ["里程碑"], True),
        ("spacetime-diagrams",       "时空图",                 "闵可夫斯基时空、世界线、光锥", 5, "theory", ["核心"], False),
        ("general-relativity-intro", "广义相对论初步",         "等效原理、弯曲时空、引力波简介", 6, "theory", ["拓展"], False),
        ("photoelectric-effect",     "光电效应",               "光电效应实验、光子假说、爱因斯坦方程", 4, "theory", ["里程碑"], True),
        ("compton-scattering",       "康普顿散射",             "光子与电子的碰撞、康普顿波长", 5, "theory", ["核心"], False),
        ("blackbody-radiation",      "黑体辐射",               "普朗克量子假说、Stefan-Boltzmann定律、Wien位移律", 5, "theory", ["核心"], False),
        ("bohr-model",               "玻尔模型",               "氢原子能级、光谱线系、玻尔半径", 4, "theory", ["里程碑"], True),
        ("atomic-spectra",           "原子光谱",               "发射谱与吸收谱、量子数、选择定则", 5, "theory", ["核心"], False),
        ("matter-waves",             "物质波",                 "德布罗意假说、电子衍射实验", 5, "theory", ["核心"], False),
        ("uncertainty-principle",    "不确定性原理",           "海森堡不确定性原理ΔxΔp≥ℏ/2", 5, "theory", ["里程碑"], True),
        ("x-rays",                   "X射线",                 "X射线产生、布拉格衍射、晶体结构分析", 4, "theory", ["应用"], False),
        ("lasers",                   "激光",                   "受激辐射、粒子数反转、激光器原理", 5, "theory", ["应用"], False),
        ("pair-production",          "正负电子对产生",         "光子能量阈值、质能转化、反物质", 5, "theory", ["核心"], False),
        ("zeeman-effect",            "塞曼效应",               "磁场中谱线分裂、正常与反常塞曼效应", 5, "theory", ["核心"], False),
        ("franck-hertz",             "弗兰克-赫兹实验",       "原子能级的实验验证、非弹性碰撞", 4, "theory", ["实验"], False),
        ("twin-paradox",             "双生子佯谬",             "时间膨胀的思想实验、加速参考系", 5, "theory", ["核心"], False),
    ],
    "quantum-mechanics": [
        ("wave-function",            "波函数",                 "量子态描述、概率诠释、归一化", 6, "theory", ["核心"], False),
        ("schrodinger-equation",     "薛定谔方程",             "含时与定态薛定谔方程、算符形式", 6, "theory", ["里程碑"], True),
        ("infinite-square-well",     "无限深方势阱",           "一维方势阱的定态解、能量量子化", 6, "theory", ["核心"], False),
        ("quantum-harmonic-oscillator","量子谐振子",           "量子谐振子能级、零点能、升降算符", 7, "theory", ["核心"], False),
        ("hydrogen-atom-qm",         "氢原子量子解",           "径向方程、球谐函数、轨道量子数", 7, "theory", ["核心"], False),
        ("quantum-tunneling",        "量子隧穿",               "势垒穿透、隧穿概率、STM应用", 6, "theory", ["核心"], False),
        ("spin",                     "自旋",                   "自旋角动量、Stern-Gerlach实验、自旋1/2", 6, "theory", ["里程碑"], True),
        ("pauli-exclusion",          "泡利不相容原理",         "费米子不可占据相同量子态、电子排布", 6, "theory", ["核心"], False),
        ("quantum-entanglement",     "量子纠缠",               "EPR佯谬、Bell不等式、量子非局域性", 7, "theory", ["核心"], False),
        ("quantum-superposition",    "量子叠加",               "叠加态、测量与塌缩、薛定谔猫", 6, "theory", ["核心"], False),
        ("operators-observables",    "算符与可观测量",         "厄米算符、本征值、对易关系", 7, "theory", ["进阶"], False),
        ("angular-momentum-qm",      "量子角动量",             "轨道角动量量子化、角动量耦合", 7, "theory", ["进阶"], False),
        ("perturbation-theory",      "微扰理论",               "定态微扰、简并微扰、一级修正", 8, "theory", ["进阶"], False),
        ("quantum-computing-intro",  "量子计算简介",           "量子比特、量子门、Shor算法简介", 7, "theory", ["拓展"], False),
        ("bose-einstein-fermi-dirac","量子统计",               "玻色-爱因斯坦统计与费米-狄拉克统计", 7, "theory", ["进阶"], False),
        ("finite-square-well",       "有限深方势阱",           "束缚态与散射态、透射系数", 7, "theory", ["核心"], False),
        ("density-matrix",           "密度矩阵",               "混合态描述、退相干、约化密度矩阵", 8, "theory", ["进阶"], False),
        ("path-integrals-intro",     "路径积分简介",           "费曼路径积分思想、传播子", 8, "theory", ["拓展"], False),
        ("selection-rules",          "选择定则",               "电偶极跃迁规则、禁戒跃迁", 7, "theory", ["核心"], False),
    ],
    "nuclear-physics": [
        ("nuclear-structure",        "原子核结构",             "质子、中子、核力、核的大小与结合能", 4, "theory", ["核心"], False),
        ("binding-energy",           "结合能",                 "质量亏损、结合能曲线、核稳定性", 5, "theory", ["里程碑"], True),
        ("radioactive-decay",        "放射性衰变",             "α衰变、β衰变、γ辐射、衰变定律", 4, "theory", ["核心"], False),
        ("half-life",                "半衰期",                 "指数衰变、放射性活度、碳-14定年", 4, "theory", ["核心"], False),
        ("nuclear-fission",          "核裂变",                 "链式反应、临界质量、核反应堆原理", 5, "theory", ["核心"], False),
        ("nuclear-fusion",           "核聚变",                 "恒星能源、等离子体约束、ITER", 5, "theory", ["核心"], False),
        ("particle-physics-intro",   "粒子物理初步",           "夸克模型、轻子、规范玻色子、标准模型简介", 6, "theory", ["拓展"], False),
        ("nuclear-reactions",        "核反应",                 "核反应方程、Q值、截面", 5, "theory", ["核心"], False),
        ("radiation-protection",     "辐射防护",               "辐射剂量、生物效应、防护原则", 3, "theory", ["应用"], False),
        ("nuclear-applications",     "核技术应用",             "医学影像(PET/CT)、工业探伤、辐照", 4, "theory", ["应用"], False),
        ("nuclear-models",           "核模型",                 "液滴模型、壳模型、集体模型", 5, "theory", ["进阶"], False),
        ("neutrinos",                "中微子",                 "中微子类型、中微子振荡、弱相互作用", 6, "theory", ["核心"], False),
        ("antimatter",               "反物质",                 "正电子、反质子、CP破缺、物质-反物质不对称", 6, "theory", ["拓展"], False),
    ],
    "astrophysics": [
        ("stellar-structure",        "恒星结构",               "静力学平衡、辐射传输、恒星模型", 5, "theory", ["核心"], False),
        ("stellar-evolution",        "恒星演化",               "主序星、红巨星、白矮星、中子星、黑洞", 5, "theory", ["里程碑"], True),
        ("hr-diagram",               "赫罗图",                 "光度-温度关系、恒星分类", 4, "theory", ["核心"], False),
        ("cosmology-basics",         "宇宙学基础",             "哈勃定律、宇宙膨胀、宇宙大爆炸", 5, "theory", ["核心"], False),
        ("cosmic-microwave-bg",      "宇宙微波背景",           "CMB辐射、黑体谱、宇宙年龄", 5, "theory", ["核心"], False),
        ("dark-matter-energy",       "暗物质与暗能量",         "星系旋转曲线、宇宙加速膨胀证据", 6, "theory", ["拓展"], False),
        ("gravitational-waves-astro","引力波",                 "LIGO探测、双中子星合并、引力波天文学", 6, "theory", ["核心"], False),
        ("black-holes",              "黑洞",                   "史瓦西半径、事件视界、霍金辐射", 6, "theory", ["核心"], False),
        ("exoplanets",               "系外行星",               "凌星法、径向速度法、宜居带", 4, "theory", ["拓展"], False),
        ("nucleosynthesis",          "核合成",                 "大爆炸核合成、恒星核合成、元素起源", 5, "theory", ["核心"], False),
        ("neutron-stars",            "中子星",                 "脉冲星、磁星、中子星状态方程", 6, "theory", ["核心"], False),
        ("galactic-structure",       "星系结构",               "旋涡星系、椭圆星系、星系团", 4, "theory", ["核心"], False),
        ("cosmic-inflation",         "宇宙暴胀",               "暴胀模型、平坦性问题、视界问题", 7, "theory", ["拓展"], False),
    ],
    "fluid-mechanics": [
        ("fluid-statics",            "流体静力学",             "压强、帕斯卡原理、液压系统", 3, "theory", ["基础"], False),
        ("buoyancy",                 "浮力",                   "阿基米德原理、浮力与密度", 3, "theory", ["核心"], False),
        ("continuity-equation",      "连续性方程",             "质量守恒、不可压缩流体的连续方程", 4, "theory", ["核心"], False),
        ("bernoullis-equation",      "伯努利方程",             "沿流线的能量守恒、文丘里管、升力原理", 4, "theory", ["里程碑"], True),
        ("viscosity",                "粘性",                   "牛顿粘性定律、雷诺数、层流与湍流", 5, "theory", ["核心"], False),
        ("navier-stokes-intro",      "纳维-斯托克斯方程简介", "NS方程的物理含义、简化情况", 6, "theory", ["进阶"], False),
        ("surface-tension",          "表面张力",               "分子间力、毛细现象、Young-Laplace方程", 4, "theory", ["核心"], False),
        ("drag-force",               "阻力",                   "形状阻力、摩擦阻力、终端速度", 4, "theory", ["核心"], False),
        ("ideal-fluid-flow",         "理想流体流动",           "势流、无旋流、流函数与势函数", 5, "theory", ["进阶"], False),
        ("vorticity",                "涡量",                   "涡量定义、环量、Kelvin环量定理", 6, "theory", ["进阶"], False),
        ("dimensional-analysis",     "量纲分析",               "白金汉π定理、无量纲数、相似律", 4, "theory", ["核心"], False),
        ("boundary-layer",           "边界层",                 "边界层概念、分离、湍流边界层", 6, "theory", ["进阶"], False),
        ("compressible-flow-intro",  "可压缩流简介",           "马赫数、激波、等熵流", 6, "theory", ["进阶"], False),
        ("pipe-flow",                "管道流动",               "Hagen-Poiseuille方程、管道阻力、水锤", 5, "theory", ["应用"], False),
    ],
    "solid-state-physics": [
        ("crystal-structure",        "晶体结构",               "布拉菲格子、密勒指数、晶系", 5, "theory", ["核心"], False),
        ("x-ray-diffraction-solid",  "X射线衍射(固体)",       "布拉格条件、粉末法、结构因子", 5, "theory", ["核心"], False),
        ("phonons",                  "声子",                   "晶格振动量子化、声子色散关系、德拜模型", 6, "theory", ["核心"], False),
        ("free-electron-model",      "自由电子模型",           "Drude模型、Sommerfeld模型、费米能", 6, "theory", ["核心"], False),
        ("band-theory",              "能带理论",               "布洛赫定理、导体/半导体/绝缘体的能带", 6, "theory", ["里程碑"], True),
        ("semiconductors",           "半导体",                 "本征半导体、掺杂、n型与p型", 5, "theory", ["核心"], False),
        ("pn-junction",              "PN结",                   "PN结原理、整流特性、二极管", 5, "theory", ["核心"], False),
        ("transistors-intro",        "晶体管简介",             "BJT、MOSFET基本原理、放大与开关", 5, "theory", ["应用"], False),
        ("magnetic-order",           "磁有序",                 "铁磁性、反铁磁性、磁畴", 6, "theory", ["核心"], False),
        ("superconductivity-solid",  "超导",                   "超导现象、BCS理论、超导应用", 7, "theory", ["拓展"], False),
        ("hall-effect",              "霍尔效应",               "经典霍尔效应、量子霍尔效应、霍尔传感器", 5, "theory", ["核心"], False),
        ("optical-properties-solid", "固体光学性质",           "吸收、反射、透射、等离子体频率", 6, "theory", ["核心"], False),
        ("amorphous-solids",         "非晶态固体",             "玻璃、无序结构、短程序", 5, "theory", ["核心"], False),
        ("nanomaterials-intro",      "纳米材料简介",           "量子点、纳米管、尺寸效应", 6, "theory", ["拓展"], False),
    ],
}


def build_concepts():
    concepts = []
    for sub_id, items in CONCEPTS_BY_SUBDOMAIN.items():
        for (cid, name, desc, diff, ctype, tags, milestone) in items:
            concepts.append({
                "id": cid,
                "name": name,
                "description": desc,
                "domain_id": "physics",
                "subdomain_id": sub_id,
                "difficulty": diff,
                "estimated_minutes": 25,
                "content_type": ctype,
                "tags": tags,
                "is_milestone": milestone,
                "created_at": NOW,
            })
    return concepts


# ── edges ────────────────────────────────────────────────────────────────
# (source_id, target_id, relation_type, strength)

EDGES_RAW = [
    # classical-mechanics internal
    ("physical-quantities",   "vectors-in-physics",      "prerequisite", 0.9),
    ("vectors-in-physics",    "kinematics-1d",           "prerequisite", 0.9),
    ("kinematics-1d",         "kinematics-2d",           "prerequisite", 0.9),
    ("kinematics-1d",         "newtons-first-law",       "prerequisite", 0.8),
    ("newtons-first-law",     "newtons-second-law",      "prerequisite", 0.9),
    ("newtons-second-law",    "newtons-third-law",       "related",     0.8),
    ("newtons-second-law",    "friction",                "prerequisite", 0.8),
    ("kinematics-2d",         "circular-motion",         "prerequisite", 0.8),
    ("newtons-second-law",    "circular-motion",         "prerequisite", 0.8),
    ("newtons-second-law",    "work-energy",             "prerequisite", 0.9),
    ("work-energy",           "potential-energy",         "prerequisite", 0.9),
    ("potential-energy",      "energy-conservation",      "prerequisite", 0.9),
    ("newtons-second-law",    "momentum",                "prerequisite", 0.8),
    ("momentum",              "momentum-conservation",    "prerequisite", 0.9),
    ("momentum-conservation", "collisions",              "prerequisite", 0.9),
    ("energy-conservation",   "collisions",              "related",     0.7),
    ("circular-motion",       "rotational-kinematics",   "prerequisite", 0.8),
    ("newtons-second-law",    "torque",                  "prerequisite", 0.7),
    ("torque",                "rotational-dynamics",      "prerequisite", 0.9),
    ("rotational-kinematics", "rotational-dynamics",      "prerequisite", 0.9),
    ("rotational-dynamics",   "angular-momentum",         "prerequisite", 0.9),
    ("torque",                "static-equilibrium",       "prerequisite", 0.8),
    ("newtons-second-law",    "gravitation",             "prerequisite", 0.8),
    ("energy-conservation",   "gravitation",             "related",     0.7),
    ("gravitation",           "orbital-mechanics",        "prerequisite", 0.9),
    ("energy-conservation",   "simple-harmonic-motion",   "related",     0.7),
    ("newtons-second-law",    "simple-harmonic-motion",   "prerequisite", 0.8),
    ("simple-harmonic-motion","damped-driven-oscillation","prerequisite", 0.9),
    ("newtons-second-law",    "non-inertial-frames",     "prerequisite", 0.7),
    ("circular-motion",       "non-inertial-frames",     "related",     0.6),
    ("kinematics-2d",         "projectile-motion",       "prerequisite", 0.9),
    ("newtons-second-law",    "elastic-force",           "prerequisite", 0.7),
    ("elastic-force",         "simple-harmonic-motion",  "prerequisite", 0.8),
    ("momentum",              "center-of-mass",          "prerequisite", 0.7),
    ("rotational-dynamics",   "rigid-body-motion",       "prerequisite", 0.8),
    ("simple-harmonic-motion","coupled-oscillations",    "prerequisite", 0.8),
    ("coupled-oscillations",  "mechanical-waves-medium", "related",     0.7),
    ("wave-basics",           "mechanical-waves-medium", "prerequisite", 0.8),
    ("energy-conservation",   "lagrangian-mechanics",    "related",     0.6),
    ("newtons-second-law",    "lagrangian-mechanics",    "related",     0.7),
    ("lagrangian-mechanics",  "hamiltonian-mechanics",   "prerequisite", 0.9),
    ("gravitation",           "keplers-laws",            "prerequisite", 0.9),
    ("orbital-mechanics",     "keplers-laws",            "related",     0.8),
    ("gravitation",           "tidal-forces",            "prerequisite", 0.7),

    # thermodynamics internal
    ("temperature-heat",      "ideal-gas-law",           "prerequisite", 0.8),
    ("temperature-heat",      "specific-heat",           "prerequisite", 0.8),
    ("ideal-gas-law",         "kinetic-theory",          "prerequisite", 0.9),
    ("temperature-heat",      "heat-transfer",           "prerequisite", 0.7),
    ("temperature-heat",      "thermal-expansion",       "prerequisite", 0.7),
    ("specific-heat",         "first-law-thermo",        "prerequisite", 0.8),
    ("work-energy",           "first-law-thermo",        "related",     0.7),
    ("first-law-thermo",      "thermodynamic-processes",  "prerequisite", 0.9),
    ("thermodynamic-processes","second-law-thermo",       "prerequisite", 0.9),
    ("second-law-thermo",     "entropy",                 "prerequisite", 0.9),
    ("thermodynamic-processes","heat-engines",            "prerequisite", 0.8),
    ("second-law-thermo",     "heat-engines",            "related",     0.8),
    ("first-law-thermo",      "phase-transitions",       "related",     0.6),
    ("entropy",               "free-energy",             "prerequisite", 0.8),
    ("kinetic-theory",        "statistical-mechanics",    "prerequisite", 0.8),
    ("entropy",               "statistical-mechanics",    "related",     0.7),
    ("entropy",               "third-law-thermo",        "related",     0.7),
    ("second-law-thermo",     "carnot-theorem",          "prerequisite", 0.9),
    ("free-energy",           "maxwell-relations",       "prerequisite", 0.8),
    ("ideal-gas-law",         "real-gases",              "prerequisite", 0.8),
    ("kinetic-theory",        "boltzmann-distribution",  "prerequisite", 0.8),
    ("statistical-mechanics", "boltzmann-distribution",  "related",     0.8),
    ("thermodynamic-processes","adiabatic-process",      "prerequisite", 0.8),
    ("first-law-thermo",      "enthalpy",               "prerequisite", 0.7),
    ("second-law-thermo",     "irreversibility",        "prerequisite", 0.8),
    ("entropy",               "irreversibility",        "related",     0.7),

    # waves-and-optics internal
    ("simple-harmonic-motion","wave-basics",              "prerequisite", 0.8),
    ("wave-basics",           "wave-equation",           "prerequisite", 0.9),
    ("wave-basics",           "superposition",           "prerequisite", 0.9),
    ("wave-basics",           "sound-waves",             "prerequisite", 0.8),
    ("damped-driven-oscillation","resonance",            "prerequisite", 0.8),
    ("wave-basics",           "reflection-refraction",   "prerequisite", 0.8),
    ("reflection-refraction", "geometric-optics",        "prerequisite", 0.9),
    ("superposition",         "interference",            "prerequisite", 0.9),
    ("interference",          "diffraction",             "prerequisite", 0.8),
    ("wave-basics",           "polarization",            "prerequisite", 0.7),
    ("reflection-refraction", "dispersion",              "prerequisite", 0.7),
    ("geometric-optics",      "optical-instruments",     "prerequisite", 0.8),
    ("interference",          "wave-particle-duality",   "related",     0.7),
    ("wave-basics",           "electromagnetic-waves",   "related",     0.7),
    ("reflection-refraction", "fiber-optics",            "prerequisite", 0.7),
    ("wave-basics",           "huygens-principle",       "prerequisite", 0.8),
    ("huygens-principle",     "diffraction",             "related",     0.7),
    ("sound-waves",           "doppler-effect-light",    "related",     0.6),
    ("special-relativity-postulates","doppler-effect-light","prerequisite", 0.7),
    ("interference",          "holography",              "prerequisite", 0.7),
    ("lasers",                "holography",              "related",     0.6),
    ("lasers",                "nonlinear-optics-intro",  "prerequisite", 0.7),

    # electromagnetism internal
    ("electric-charge",       "electric-field",          "prerequisite", 0.9),
    ("electric-field",        "gauss-law",               "prerequisite", 0.9),
    ("electric-field",        "electric-potential",       "prerequisite", 0.9),
    ("electric-potential",    "capacitance",             "prerequisite", 0.8),
    ("electric-charge",       "dc-circuits",             "prerequisite", 0.7),
    ("dc-circuits",           "rc-circuits",             "prerequisite", 0.8),
    ("electric-charge",       "magnetic-field",          "related",     0.6),
    ("magnetic-field",        "lorentz-force",           "prerequisite", 0.9),
    ("magnetic-field",        "biot-savart",             "prerequisite", 0.9),
    ("biot-savart",           "amperes-law",             "prerequisite", 0.9),
    ("magnetic-field",        "faradays-law",            "prerequisite", 0.8),
    ("faradays-law",          "inductance",              "prerequisite", 0.9),
    ("dc-circuits",           "ac-circuits",             "prerequisite", 0.7),
    ("inductance",            "ac-circuits",             "related",     0.7),
    ("capacitance",           "ac-circuits",             "related",     0.7),
    ("gauss-law",             "maxwells-equations",      "prerequisite", 0.8),
    ("amperes-law",           "maxwells-equations",      "prerequisite", 0.8),
    ("faradays-law",          "maxwells-equations",      "prerequisite", 0.8),
    ("maxwells-equations",    "electromagnetic-radiation","prerequisite", 0.8),
    ("maxwells-equations",    "em-energy-poynting",      "prerequisite", 0.8),
    ("maxwells-equations",    "electromagnetic-waves",   "prerequisite", 0.9),
    ("electric-field",        "dielectrics",             "prerequisite", 0.7),
    ("magnetic-field",        "magnetic-materials",      "prerequisite", 0.7),
    ("magnetic-materials",    "superconductivity-intro", "related",     0.6),
    ("electric-field",        "electric-dipole",         "prerequisite", 0.7),
    ("magnetic-field",        "magnetic-dipole",         "prerequisite", 0.7),
    ("dc-circuits",           "kirchhoffs-laws",         "prerequisite", 0.8),
    ("faradays-law",          "power-transmission",      "prerequisite", 0.7),
    ("faradays-law",          "electromagnetic-induction-app","prerequisite", 0.8),

    # modern-physics internal
    ("special-relativity-postulates","time-dilation",    "prerequisite", 0.9),
    ("special-relativity-postulates","length-contraction","prerequisite", 0.9),
    ("time-dilation",         "lorentz-transformations",  "prerequisite", 0.8),
    ("length-contraction",    "lorentz-transformations",  "prerequisite", 0.8),
    ("lorentz-transformations","relativistic-momentum-energy","prerequisite", 0.9),
    ("lorentz-transformations","spacetime-diagrams",      "prerequisite", 0.7),
    ("relativistic-momentum-energy","general-relativity-intro","related", 0.6),
    ("wave-particle-duality", "photoelectric-effect",    "related",     0.8),
    ("photoelectric-effect",  "compton-scattering",      "related",     0.7),
    ("blackbody-radiation",   "photoelectric-effect",    "related",     0.7),
    ("photoelectric-effect",  "bohr-model",              "prerequisite", 0.8),
    ("bohr-model",            "atomic-spectra",          "prerequisite", 0.8),
    ("wave-particle-duality", "matter-waves",            "prerequisite", 0.9),
    ("matter-waves",          "uncertainty-principle",    "prerequisite", 0.8),
    ("electromagnetic-waves", "x-rays",                  "related",     0.6),
    ("bohr-model",            "lasers",                  "related",     0.6),
    ("atomic-spectra",        "lasers",                  "prerequisite", 0.7),
    ("relativistic-momentum-energy","pair-production",   "prerequisite", 0.7),
    ("bohr-model",            "zeeman-effect",           "prerequisite", 0.7),
    ("atomic-spectra",        "zeeman-effect",           "related",     0.7),
    ("bohr-model",            "franck-hertz",            "related",     0.7),
    ("time-dilation",         "twin-paradox",            "prerequisite", 0.8),

    # quantum-mechanics internal
    ("matter-waves",          "wave-function",           "prerequisite", 0.9),
    ("uncertainty-principle", "wave-function",           "related",     0.7),
    ("wave-function",         "schrodinger-equation",    "prerequisite", 0.9),
    ("schrodinger-equation",  "infinite-square-well",    "prerequisite", 0.9),
    ("schrodinger-equation",  "quantum-harmonic-oscillator","prerequisite", 0.8),
    ("schrodinger-equation",  "hydrogen-atom-qm",        "prerequisite", 0.8),
    ("schrodinger-equation",  "quantum-tunneling",       "prerequisite", 0.8),
    ("wave-function",         "quantum-superposition",   "prerequisite", 0.8),
    ("bohr-model",            "hydrogen-atom-qm",        "related",     0.7),
    ("angular-momentum",      "spin",                    "related",     0.6),
    ("spin",                  "pauli-exclusion",         "prerequisite", 0.8),
    ("quantum-superposition", "quantum-entanglement",    "prerequisite", 0.8),
    ("schrodinger-equation",  "operators-observables",   "prerequisite", 0.8),
    ("operators-observables", "angular-momentum-qm",     "prerequisite", 0.7),
    ("operators-observables", "perturbation-theory",     "prerequisite", 0.7),
    ("quantum-entanglement",  "quantum-computing-intro", "related",     0.6),
    ("pauli-exclusion",       "bose-einstein-fermi-dirac","prerequisite", 0.7),
    ("infinite-square-well",  "finite-square-well",      "prerequisite", 0.8),
    ("finite-square-well",    "quantum-tunneling",       "related",     0.7),
    ("operators-observables", "density-matrix",          "prerequisite", 0.7),
    ("schrodinger-equation",  "path-integrals-intro",    "related",     0.6),
    ("angular-momentum-qm",   "selection-rules",         "prerequisite", 0.7),
    ("hydrogen-atom-qm",      "selection-rules",         "related",     0.7),

    # nuclear-physics internal
    ("nuclear-structure",     "binding-energy",          "prerequisite", 0.9),
    ("nuclear-structure",     "radioactive-decay",       "prerequisite", 0.8),
    ("radioactive-decay",     "half-life",               "prerequisite", 0.9),
    ("binding-energy",        "nuclear-fission",         "prerequisite", 0.8),
    ("binding-energy",        "nuclear-fusion",          "prerequisite", 0.8),
    ("nuclear-structure",     "nuclear-reactions",       "prerequisite", 0.8),
    ("radioactive-decay",     "radiation-protection",    "prerequisite", 0.7),
    ("nuclear-fission",       "nuclear-applications",    "related",     0.6),
    ("nuclear-structure",     "particle-physics-intro",  "related",     0.6),
    ("relativistic-momentum-energy","binding-energy",    "related",     0.7),
    ("nuclear-structure",     "nuclear-models",          "prerequisite", 0.8),
    ("radioactive-decay",     "neutrinos",               "related",     0.7),
    ("pair-production",       "antimatter",              "related",     0.7),
    ("particle-physics-intro","antimatter",              "related",     0.6),

    # astrophysics internal
    ("nuclear-fusion",        "stellar-structure",       "related",     0.7),
    ("stellar-structure",     "stellar-evolution",       "prerequisite", 0.9),
    ("stellar-evolution",     "hr-diagram",              "related",     0.8),
    ("general-relativity-intro","cosmology-basics",      "related",     0.6),
    ("cosmology-basics",      "cosmic-microwave-bg",     "prerequisite", 0.8),
    ("cosmology-basics",      "dark-matter-energy",      "prerequisite", 0.7),
    ("general-relativity-intro","gravitational-waves-astro","prerequisite", 0.7),
    ("general-relativity-intro","black-holes",           "prerequisite", 0.8),
    ("stellar-evolution",     "black-holes",             "related",     0.7),
    ("stellar-evolution",     "nucleosynthesis",         "related",     0.7),
    ("nuclear-fusion",        "nucleosynthesis",         "prerequisite", 0.8),
    ("cosmology-basics",      "exoplanets",              "related",     0.5),
    ("stellar-evolution",     "neutron-stars",           "prerequisite", 0.8),
    ("stellar-evolution",     "galactic-structure",      "related",     0.5),
    ("cosmology-basics",      "cosmic-inflation",        "prerequisite", 0.8),

    # fluid-mechanics internal
    ("fluid-statics",         "buoyancy",                "prerequisite", 0.9),
    ("fluid-statics",         "continuity-equation",     "prerequisite", 0.8),
    ("continuity-equation",   "bernoullis-equation",     "prerequisite", 0.9),
    ("energy-conservation",   "bernoullis-equation",     "related",     0.7),
    ("bernoullis-equation",   "viscosity",               "related",     0.6),
    ("viscosity",             "navier-stokes-intro",     "prerequisite", 0.8),
    ("fluid-statics",         "surface-tension",         "related",     0.5),
    ("viscosity",             "drag-force",              "prerequisite", 0.7),
    ("continuity-equation",   "ideal-fluid-flow",        "prerequisite", 0.7),
    ("ideal-fluid-flow",      "vorticity",               "prerequisite", 0.8),
    ("viscosity",             "boundary-layer",          "prerequisite", 0.8),
    ("viscosity",             "pipe-flow",               "prerequisite", 0.7),
    ("bernoullis-equation",   "compressible-flow-intro", "related",     0.6),
    ("viscosity",             "dimensional-analysis",    "related",     0.5),
    ("bernoullis-equation",   "pipe-flow",               "related",     0.6),

    # solid-state-physics internal
    ("crystal-structure",     "x-ray-diffraction-solid", "prerequisite", 0.8),
    ("crystal-structure",     "phonons",                 "prerequisite", 0.8),
    ("phonons",               "free-electron-model",     "related",     0.5),
    ("free-electron-model",   "band-theory",             "prerequisite", 0.9),
    ("band-theory",           "semiconductors",          "prerequisite", 0.9),
    ("semiconductors",        "pn-junction",             "prerequisite", 0.9),
    ("pn-junction",           "transistors-intro",       "prerequisite", 0.8),
    ("magnetic-materials",    "magnetic-order",          "prerequisite", 0.7),
    ("superconductivity-intro","superconductivity-solid","related",     0.8),
    ("pauli-exclusion",       "free-electron-model",     "related",     0.7),
    ("bose-einstein-fermi-dirac","free-electron-model",  "related",     0.6),
    ("band-theory",           "hall-effect",             "related",     0.6),
    ("lorentz-force",         "hall-effect",             "prerequisite", 0.7),
    ("band-theory",           "optical-properties-solid","prerequisite", 0.7),
    ("crystal-structure",     "amorphous-solids",        "related",     0.5),
    ("band-theory",           "nanomaterials-intro",     "related",     0.5),

    # cross-subdomain edges
    ("energy-conservation",   "first-law-thermo",        "related",     0.8),
    ("maxwells-equations",    "electromagnetic-waves",   "prerequisite", 0.9),
    ("bohr-model",            "hydrogen-atom-qm",        "prerequisite", 0.7),
    ("gravitation",           "general-relativity-intro","related",     0.6),
    ("gravitation",           "stellar-structure",       "related",     0.5),
    ("statistical-mechanics", "bose-einstein-fermi-dirac","related",    0.7),
    ("x-rays",                "x-ray-diffraction-solid", "related",     0.7),
    ("band-theory",           "superconductivity-solid", "related",     0.5),
]


def build_edges():
    seen = set()
    edges = []
    for (src, tgt, rel, strength) in EDGES_RAW:
        key = (src, tgt)
        if key in seen:
            continue
        seen.add(key)
        edges.append({
            "source_id": src,
            "target_id": tgt,
            "relation_type": rel,
            "strength": strength,
        })
    return edges


def verify(concepts, edges):
    """Check graph integrity."""
    ids = {c["id"] for c in concepts}
    orphans = []
    edge_node_ids = set()
    for e in edges:
        edge_node_ids.add(e["source_id"])
        edge_node_ids.add(e["target_id"])
        if e["source_id"] not in ids:
            print(f"⚠ Edge source not found: {e['source_id']}")
        if e["target_id"] not in ids:
            print(f"⚠ Edge target not found: {e['target_id']}")
    for c in concepts:
        if c["id"] not in edge_node_ids:
            orphans.append(c["id"])
    if orphans:
        print(f"⚠ Orphan nodes (no edges): {orphans}")
    # Check for ID collisions with other domains
    collisions = ids & {"linear-regression", "logistic-regression", "gradient-descent", "graph-coloring"}
    if collisions:
        print(f"⚠ Concept ID collision with existing domains: {collisions}")
    # Count stats
    milestones = sum(1 for c in concepts if c["is_milestone"])
    subdomain_set = {c["subdomain_id"] for c in concepts}
    print(f"✅ Concepts: {len(concepts)}, Edges: {len(edges)}, Subdomains: {len(subdomain_set)}, Milestones: {milestones}")
    if orphans:
        return False
    return True


def main():
    concepts = build_concepts()
    edges = build_edges()

    if not verify(concepts, edges):
        print("❌ Verification failed — fix orphan nodes")
        return

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
                "milestones": sum(1 for c in concepts if c["is_milestone"]),
            }
        }
    }

    import os
    out_path = os.path.join(os.path.dirname(__file__), "seed_graph.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, ensure_ascii=False, indent=2)
    print(f"✅ Written to {out_path}")


if __name__ == "__main__":
    main()
