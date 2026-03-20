"""
关卡设计知识球 — 种子图谱生成器 (Phase 19)
~200 概念节点 + 10 子域 + ~220 边 + 里程碑节点
输出: data/seed/level-design/seed_graph.json
"""
import json, os

DOMAIN = {
    "id": "level-design",
    "name": "关卡设计",
    "description": "从空间叙事到关卡编辑器的完整关卡设计知识体系",
    "icon": "🗺️",
    "color": "#d97706",
}

SUBDOMAINS = [
    {"id": "spatial-narrative", "name": "空间叙事", "order": 1},
    {"id": "pacing-curve", "name": "节奏曲线", "order": 2},
    {"id": "guidance-design", "name": "引导设计", "order": 3},
    {"id": "blockout", "name": "Blockout", "order": 4},
    {"id": "metrics-design", "name": "Metric设计", "order": 5},
    {"id": "combat-space", "name": "战斗空间", "order": 6},
    {"id": "level-editor", "name": "关卡编辑器", "order": 7},
    {"id": "terrain-design", "name": "地形设计", "order": 8},
    {"id": "lighting-narrative", "name": "光照叙事", "order": 9},
    {"id": "ld-documentation", "name": "LD文档", "order": 10},
]

# =============================================
# Concept definitions per subdomain
# =============================================
def make_concept(cid, name, desc, sub, diff, mins, ctype="theory", tags=None, milestone=False):
    return {
        "id": cid, "name": name, "description": desc,
        "subdomain_id": sub, "domain_id": "level-design",
        "difficulty": diff, "estimated_minutes": mins,
        "content_type": ctype, "tags": tags or ["基础"],
        "is_milestone": milestone,
    }

C = []
# ── 1. spatial-narrative (空间叙事) — 20 concepts ──
sub = "spatial-narrative"
C += [
    make_concept("ld-overview", "关卡设计概述", "关卡设计的定义、职责与工作流程", sub, 1, 20, tags=["基础"], milestone=True),
    make_concept("spatial-storytelling", "空间叙事原理", "通过空间布局传递故事的核心方法论", sub, 1, 25, tags=["叙事"], milestone=True),
    make_concept("env-storytelling", "环境叙事", "用环境细节讲述背景故事（不依赖文字/对白）", sub, 2, 30, tags=["叙事"]),
    make_concept("visual-language", "视觉语言", "建筑风格、色彩、材质传递的信息与情感", sub, 2, 25, tags=["视觉"]),
    make_concept("landmark-design", "地标设计", "用地标引导玩家方向感与空间记忆", sub, 2, 25, tags=["导航"]),
    make_concept("negative-space", "负空间", "空旷区域的情感作用与节奏控制", sub, 2, 20, tags=["空间"]),
    make_concept("spatial-hierarchy", "空间层次", "主路径、支线路径与隐藏区域的层次设计", sub, 2, 25, tags=["结构"]),
    make_concept("world-building-ld", "世界观搭建(LD视角)", "关卡设计师如何服务于世界观一致性", sub, 3, 30, tags=["叙事"]),
    make_concept("set-piece", "定制场景(Set-piece)", "高潮事件的空间与脚本编排", sub, 3, 30, tags=["叙事"], milestone=True),
    make_concept("discovery-design", "发现感设计", "秘密区域、隐藏路径与探索奖励", sub, 2, 25, tags=["探索"]),
    make_concept("point-of-interest", "兴趣点(POI)设计", "吸引玩家注意力的关键位置规划", sub, 2, 25, tags=["导航"]),
    make_concept("linear-vs-open", "线性vs开放世界", "两种关卡结构的设计取舍与适用场景", sub, 2, 30, tags=["结构"]),
    make_concept("hub-spoke", "Hub-and-Spoke结构", "中心区域辐射多路线的经典布局", sub, 2, 25, tags=["结构"]),
    make_concept("looping-path", "环形路径设计", "Shortcut与解锁捷径的空间设计", sub, 2, 25, tags=["结构"]),
    make_concept("verticality", "垂直性设计", "多层空间、高度差与垂直探索", sub, 2, 25, tags=["空间"]),
    make_concept("scale-proportion", "尺度与比例", "建筑与环境尺度对玩家感知的影响", sub, 2, 25, tags=["空间"]),
    make_concept("density-design", "密度设计", "内容密度、留白与信息过载平衡", sub, 3, 25, tags=["节奏"]),
    make_concept("theme-variation", "主题变化", "同一关卡内的视觉/玩法主题递进", sub, 3, 25, tags=["叙事"]),
    make_concept("player-path-analysis", "玩家路径分析", "热力图、轨迹追踪与路径优化", sub, 3, 30, tags=["数据"]),
    make_concept("immersion-design", "沉浸感设计", "减少打破沉浸的设计原则", sub, 3, 25, tags=["体验"]),
]

# ── 2. pacing-curve (节奏曲线) — 20 concepts ──
sub = "pacing-curve"
C += [
    make_concept("pacing-intro", "节奏设计概述", "关卡节奏的定义与情感曲线", sub, 1, 20, tags=["基础"], milestone=True),
    make_concept("tension-release", "紧张与释放", "高压→放松的情感波动设计", sub, 2, 25, tags=["情感"]),
    make_concept("intensity-curve", "强度曲线", "关卡内挑战强度的变化规律", sub, 2, 25, tags=["曲线"]),
    make_concept("three-act-level", "三幕式关卡", "起承转合的经典叙事结构应用", sub, 2, 25, tags=["结构"], milestone=True),
    make_concept("rest-area", "休息区设计", "安全地带与补给点的节奏作用", sub, 2, 20, tags=["节奏"]),
    make_concept("climax-design", "高潮设计", "关卡终局的情感高潮编排", sub, 3, 30, tags=["设计"]),
    make_concept("micro-pacing", "微观节奏", "房间级别的张力变化设计", sub, 2, 25, tags=["节奏"]),
    make_concept("macro-pacing", "宏观节奏", "关卡间/章节间的难度与情感曲线", sub, 3, 25, tags=["节奏"]),
    make_concept("reward-pacing", "奖励节奏", "奖励分布频率与玩家满足感曲线", sub, 2, 25, tags=["奖励"]),
    make_concept("content-gating", "内容门控", "何时解锁新机制/新区域的时机设计", sub, 2, 25, tags=["门控"]),
    make_concept("mechanic-introduction", "机制引入节奏", "新机制的教学→练习→挑战递进", sub, 2, 30, tags=["教学"]),
    make_concept("difficulty-ramp", "难度爬坡", "关卡内/关卡间的难度递增策略", sub, 2, 25, tags=["难度"]),
    make_concept("surprise-moment", "惊喜时刻", "打破预期的关卡事件与节奏转折", sub, 2, 20, tags=["情感"]),
    make_concept("backtracking-design", "回溯设计", "回到已探索区域的新体验设计", sub, 3, 25, tags=["结构"]),
    make_concept("level-length", "关卡时长控制", "单关卡时长与玩家注意力曲线", sub, 2, 25, tags=["时间"]),
    make_concept("checkpoint-pacing", "检查点节奏", "存档点间距与失败成本控制", sub, 2, 20, tags=["容错"]),
    make_concept("narrative-pacing", "叙事节奏", "对话、过场、可玩段落的交替编排", sub, 3, 25, tags=["叙事"]),
    make_concept("exploration-pacing", "探索节奏", "开放区域的发现频率与报酬密度", sub, 2, 25, tags=["探索"]),
    make_concept("downtime-design", "停顿设计", "无战斗/低压区段的情感功能", sub, 2, 20, tags=["情感"]),
    make_concept("pacing-analysis", "节奏分析方法", "图表化关卡节奏并识别问题", sub, 3, 30, "practice", tags=["分析"], milestone=True),
]

# ── 3. guidance-design (引导设计) — 20 concepts ──
sub = "guidance-design"
C += [
    make_concept("guidance-intro", "引导设计概述", "玩家引导的分类与设计原则", sub, 1, 20, tags=["基础"], milestone=True),
    make_concept("visual-guidance", "视觉引导", "光线、颜色、对比度引导视线", sub, 2, 25, tags=["视觉"]),
    make_concept("audio-guidance", "音频引导", "声音线索辅助空间定位与事件提示", sub, 2, 20, tags=["音频"]),
    make_concept("layout-guidance", "布局引导", "走廊、门洞、坡道的自然导流", sub, 2, 25, tags=["空间"]),
    make_concept("breadcrumb-trail", "面包屑引导", "物品、NPC、特效的路径暗示", sub, 2, 25, tags=["路径"]),
    make_concept("affordance-ld", "可供性(Affordance)", "环境元素暗示可交互性的视觉语言", sub, 2, 25, tags=["交互"]),
    make_concept("gating-mechanic", "门控机制", "钥匙、技能、事件解锁路径的设计", sub, 2, 25, tags=["门控"]),
    make_concept("tutorial-level", "教学关卡设计", "首关/教学关的机制引入与引导策略", sub, 2, 30, tags=["教学"], milestone=True),
    make_concept("show-dont-tell", "展示而非告知", "通过关卡设计隐式传递规则", sub, 2, 25, tags=["原则"]),
    make_concept("signposting", "标识指引", "箭头、涂鸦、NPC对话的显式引导", sub, 1, 20, tags=["显式"]),
    make_concept("implicit-vs-explicit", "隐式vs显式引导", "两种引导策略的适用场景与平衡", sub, 2, 25, tags=["策略"]),
    make_concept("flow-channel-ld", "心流通道(LD)", "引导玩家进入心流状态的空间设计", sub, 3, 25, tags=["体验"]),
    make_concept("player-expectation", "玩家预期管理", "建立、满足与颠覆玩家预期", sub, 3, 25, tags=["心理"]),
    make_concept("camera-control-ld", "摄像机引导", "摄像机运动辅助空间理解与引导", sub, 2, 25, tags=["摄像机"]),
    make_concept("npc-guidance", "NPC引导行为", "同行NPC的导航与行为设计", sub, 2, 25, tags=["AI"]),
    make_concept("minimap-guidance", "小地图引导", "小地图与标记系统的信息层级", sub, 2, 20, tags=["UI"]),
    make_concept("objective-marker", "目标标记设计", "任务标记的侵入性与信息量平衡", sub, 2, 20, tags=["UI"]),
    make_concept("lost-player-recovery", "迷路玩家恢复", "玩家迷失方向后的恢复机制", sub, 3, 25, tags=["容错"]),
    make_concept("difficulty-communication", "难度沟通", "通过视觉暗示传递区域危险等级", sub, 2, 25, tags=["沟通"]),
    make_concept("onboarding-sequence", "新手引导序列", "多关卡渐进式机制教学规划", sub, 3, 30, tags=["教学"], milestone=True),
]

# ── 4. blockout (Blockout) — 20 concepts ──
sub = "blockout"
C += [
    make_concept("blockout-intro", "Blockout概述", "灰盒关卡原型的目的与工作流", sub, 1, 20, tags=["基础"], milestone=True),
    make_concept("greybox-workflow", "灰盒工作流", "从Blockout到美术资产替换的流程", sub, 2, 25, tags=["流程"]),
    make_concept("bsp-blocking", "BSP阻挡体", "引擎内置几何体快速搭建关卡", sub, 2, 25, "practice", tags=["工具"]),
    make_concept("modular-kit", "模块化套件", "可复用建筑模块的设计与拼接规范", sub, 2, 30, tags=["资产"]),
    make_concept("scale-reference", "尺度参考", "角色模型作为尺度基准的重要性", sub, 1, 20, tags=["度量"]),
    make_concept("collision-volume", "碰撞体积设计", "碰撞体、导航阻挡与玩家可达性", sub, 2, 25, tags=["物理"]),
    make_concept("playable-path", "可行走路径规划", "主路径、支路与死胡同的灰盒布局", sub, 2, 25, tags=["路径"]),
    make_concept("prototype-test", "原型测试", "灰盒关卡的可玩性测试方法", sub, 2, 25, "practice", tags=["测试"]),
    make_concept("iteration-blockout", "Blockout迭代", "基于反馈快速修改灰盒的策略", sub, 2, 25, tags=["迭代"]),
    make_concept("cover-placement", "掩体布局", "射击游戏掩体的战术性放置", sub, 2, 25, tags=["战术"]),
    make_concept("spawn-point", "出生点设计", "玩家/敌人出生点的放置规则", sub, 2, 25, tags=["规则"]),
    make_concept("trigger-volume", "触发体积设计", "事件触发区域的大小与位置", sub, 2, 25, tags=["脚本"]),
    make_concept("navmesh-basics", "导航网格基础", "NavMesh生成与AI可行走区域", sub, 2, 25, tags=["AI"]),
    make_concept("sightline-test", "视线测试", "检查视线遮挡与信息暴露", sub, 2, 20, "practice", tags=["测试"]),
    make_concept("flow-testing", "流程测试", "完整流程走通与时间测量", sub, 2, 25, "practice", tags=["测试"]),
    make_concept("blockout-checklist", "Blockout检查清单", "灰盒阶段必须验证的项目列表", sub, 2, 20, tags=["流程"], milestone=True),
    make_concept("kit-bashing", "Kit-bashing技法", "组合现有模块快速搭建复杂场景", sub, 2, 25, "practice", tags=["技法"]),
    make_concept("proxy-asset", "代理资产", "临时占位模型的规范与管理", sub, 2, 20, tags=["资产"]),
    make_concept("blockout-annotation", "Blockout标注", "灰盒中的文字/颜色标注规范", sub, 1, 20, tags=["沟通"]),
    make_concept("blockout-review", "Blockout评审", "团队评审灰盒关卡的流程与标准", sub, 2, 25, tags=["流程"]),
]

# ── 5. metrics-design (Metric设计) — 20 concepts ──
sub = "metrics-design"
C += [
    make_concept("metrics-intro", "Metric设计概述", "关卡度量标准的定义与重要性", sub, 1, 20, tags=["基础"], milestone=True),
    make_concept("character-metrics", "角色度量", "角色高度、宽度、跳跃高度等核心参数", sub, 1, 25, tags=["角色"]),
    make_concept("movement-speed", "移动速度标准", "行走/跑步/冲刺速度与关卡尺度关系", sub, 2, 25, tags=["移动"]),
    make_concept("jump-metrics", "跳跃度量", "跳跃距离、高度与平台间距标准", sub, 2, 25, tags=["移动"]),
    make_concept("corridor-width", "走廊宽度标准", "不同场景下走廊宽度的设计规范", sub, 2, 20, tags=["空间"]),
    make_concept("ceiling-height", "天花板高度标准", "室内空间净高与压迫感控制", sub, 2, 20, tags=["空间"]),
    make_concept("door-size", "门洞尺寸标准", "出入口尺寸与通行体验", sub, 1, 20, tags=["度量"]),
    make_concept("stair-slope", "楼梯与坡道标准", "楼梯间距、坡度与可行走角度", sub, 2, 25, tags=["度量"]),
    make_concept("platform-gap", "平台间距", "跳跃平台的安全距离与挑战距离", sub, 2, 25, tags=["平台"]),
    make_concept("combat-range", "战斗距离度量", "近战/远程武器的有效距离标准", sub, 2, 25, tags=["战斗"]),
    make_concept("cover-height", "掩体高度标准", "全掩/半掩/可翻越的高度定义", sub, 2, 20, tags=["战术"]),
    make_concept("visibility-range", "可视距离", "视野范围与LOD距离标准", sub, 2, 25, tags=["视觉"]),
    make_concept("interaction-range", "交互距离", "玩家与物体交互的有效距离", sub, 2, 20, tags=["交互"]),
    make_concept("spawn-distance", "出怪距离标准", "敌人刷新点与玩家的安全距离", sub, 2, 25, tags=["战斗"]),
    make_concept("camera-distance-ld", "摄像机距离标准", "第三人称摄像机与墙壁的最小距离", sub, 2, 20, tags=["摄像机"]),
    make_concept("ai-patrol-range", "AI巡逻范围", "敌人巡逻路径的长度与区域覆盖", sub, 2, 25, tags=["AI"]),
    make_concept("audio-range", "音效触发范围", "环境音/敌人音效的传播距离标准", sub, 2, 20, tags=["音频"]),
    make_concept("metric-sheet", "度量表制作", "项目度量标准文档的编写与维护", sub, 2, 25, "practice", tags=["文档"], milestone=True),
    make_concept("metric-validation", "度量验证", "通过自动化测试验证关卡符合度量标准", sub, 3, 25, "practice", tags=["测试"]),
    make_concept("metric-exception", "度量例外", "何时可以合理突破标准度量", sub, 3, 25, tags=["设计"]),
]

# ── 6. combat-space (战斗空间) — 20 concepts ──
sub = "combat-space"
C += [
    make_concept("combat-space-intro", "战斗空间概述", "战斗空间的设计目标与分类", sub, 1, 20, tags=["基础"], milestone=True),
    make_concept("arena-layout", "竞技场布局", "封闭式战斗区域的空间设计", sub, 2, 30, tags=["布局"]),
    make_concept("corridor-combat", "走廊战斗空间", "线性空间中的战术选择设计", sub, 2, 25, tags=["布局"]),
    make_concept("elevation-tactics", "高度差战术", "高低差地形对战斗策略的影响", sub, 2, 25, tags=["地形"]),
    make_concept("flanking-route", "侧翼路线", "绕后/包抄路线的空间设计", sub, 2, 25, tags=["战术"]),
    make_concept("cover-system-ld", "掩体系统(LD)", "掩体分布、密度与战斗节奏关系", sub, 2, 30, tags=["掩体"], milestone=True),
    make_concept("choke-point", "瓶颈点设计", "防守/推进的关键地形节点", sub, 2, 25, tags=["战术"]),
    make_concept("escape-route", "逃生路线", "允许玩家撤退与重新接近的路线", sub, 2, 20, tags=["路线"]),
    make_concept("enemy-spawn-area", "敌人刷新区域", "敌人出现位置的戏剧性与公平性", sub, 2, 25, tags=["敌人"]),
    make_concept("wave-arena", "波次战斗空间", "多波次敌人的空间与节奏设计", sub, 3, 30, tags=["波次"]),
    make_concept("boss-arena", "Boss战场", "Boss战专用空间的设计原则", sub, 3, 30, tags=["Boss"], milestone=True),
    make_concept("stealth-space", "潜行空间", "允许隐蔽行动的空间布局", sub, 2, 25, tags=["潜行"]),
    make_concept("destructible-env", "可破坏环境", "场景破坏对战术选择的影响", sub, 3, 25, tags=["环境"]),
    make_concept("hazard-placement", "危险物放置", "陷阱、岩浆、电击等环境危害", sub, 2, 25, tags=["危害"]),
    make_concept("ammo-health-placement", "补给点放置", "弹药/生命值的战略性分布", sub, 2, 20, tags=["补给"]),
    make_concept("combat-flow", "战斗流线", "从接敌到战斗结束的空间流动", sub, 3, 25, tags=["流线"]),
    make_concept("sightline-combat", "战斗视线管理", "视线开放度与信息暴露控制", sub, 2, 25, tags=["视线"]),
    make_concept("multi-level-combat", "多层战斗空间", "立体战斗空间的高低差利用", sub, 3, 25, tags=["立体"]),
    make_concept("vehicle-combat-space", "载具战斗空间", "大尺度载具战斗的空间需求", sub, 3, 25, tags=["载具"]),
    make_concept("combat-space-review", "战斗空间评审", "实战测试与数据驱动的空间优化", sub, 3, 25, "practice", tags=["评审"]),
]

# ── 7. level-editor (关卡编辑器) — 20 concepts ──
sub = "level-editor"
C += [
    make_concept("level-editor-intro", "关卡编辑器概述", "主流引擎关卡编辑工具对比", sub, 1, 20, tags=["基础"], milestone=True),
    make_concept("ue5-level-editor", "UE5关卡编辑器", "Unreal Engine 5的关卡编辑核心功能", sub, 2, 30, tags=["UE5"]),
    make_concept("unity-scene-editor", "Unity场景编辑器", "Unity的场景管理与关卡编辑", sub, 2, 30, tags=["Unity"]),
    make_concept("blueprint-scripting", "蓝图脚本(LD)", "关卡设计师常用的蓝图脚本技术", sub, 2, 30, tags=["脚本"]),
    make_concept("level-streaming", "关卡流式加载", "大地图分区加载与无缝衔接", sub, 3, 30, tags=["技术"]),
    make_concept("world-partition", "World Partition", "UE5的世界分区与大世界管理", sub, 3, 30, tags=["UE5"], milestone=True),
    make_concept("sublevel-management", "子关卡管理", "Sub-level的组织、加载与权限控制", sub, 2, 25, tags=["管理"]),
    make_concept("version-control-ld", "关卡版本控制", "二进制关卡文件的版本管理策略", sub, 2, 25, tags=["协作"]),
    make_concept("multi-user-editing", "多人协同编辑", "多LD同时编辑同一关卡的工作流", sub, 3, 25, tags=["协作"]),
    make_concept("landscape-tool", "地形工具", "引擎内置地形编辑器的使用", sub, 2, 25, tags=["地形"]),
    make_concept("foliage-tool", "植被工具", "程序化植被散布与性能控制", sub, 2, 25, tags=["环境"]),
    make_concept("sequencer-ld", "Sequencer(LD)", "关卡事件序列与过场动画编辑", sub, 2, 25, tags=["脚本"]),
    make_concept("gameplay-ability-ld", "Gameplay Ability(LD)", "GAS在关卡交互中的应用", sub, 3, 25, tags=["UE5"]),
    make_concept("pcg-level-gen", "PCG关卡生成", "程序化内容生成在关卡设计中的应用", sub, 3, 30, tags=["PCG"]),
    make_concept("custom-editor-tool", "自定义编辑器工具", "为LD制作专用编辑器插件", sub, 3, 30, tags=["工具"]),
    make_concept("data-layer", "数据层管理", "Gameplay数据与美术数据的分层", sub, 2, 25, tags=["架构"]),
    make_concept("debug-visualization", "调试可视化", "NavMesh/碰撞体/触发器的可视化调试", sub, 2, 20, "practice", tags=["调试"]),
    make_concept("profiling-ld", "关卡性能分析", "Draw call/三角形/内存预算分析", sub, 3, 25, tags=["性能"]),
    make_concept("optimization-ld", "关卡优化", "LOD、裁剪、合批与内存优化", sub, 3, 30, tags=["性能"], milestone=True),
    make_concept("build-pipeline-ld", "关卡构建管线", "打包、光照烘焙与资产依赖管理", sub, 3, 25, tags=["管线"]),
]

# ── 8. terrain-design (地形设计) — 20 concepts ──
sub = "terrain-design"
C += [
    make_concept("terrain-intro", "地形设计概述", "游戏地形的类型、工具与设计原则", sub, 1, 20, tags=["基础"], milestone=True),
    make_concept("heightmap", "高度图", "高度图的创建、编辑与导入", sub, 2, 25, tags=["技术"]),
    make_concept("terrain-sculpting", "地形雕刻", "引擎内地形刷的使用技巧", sub, 2, 25, "practice", tags=["技法"]),
    make_concept("terrain-material", "地形材质", "多层材质混合与Splatmap", sub, 2, 25, tags=["材质"]),
    make_concept("terrain-lod", "地形LOD", "地形细节层次与远景衰减", sub, 3, 25, tags=["性能"]),
    make_concept("procedural-terrain", "程序化地形", "噪声函数与侵蚀模拟生成地形", sub, 3, 30, tags=["PCG"]),
    make_concept("road-river", "道路与河流", "道路网络、河流路径的地形融合", sub, 2, 25, tags=["环境"]),
    make_concept("cliff-cave", "悬崖与洞穴", "非高度图地形的网格建模方案", sub, 3, 25, tags=["环境"]),
    make_concept("biome-design", "生态区设计", "沙漠/雪原/森林等区域的地形差异化", sub, 2, 30, tags=["环境"], milestone=True),
    make_concept("water-body", "水体设计", "海洋、湖泊、河流的地形与渲染", sub, 2, 25, tags=["环境"]),
    make_concept("vegetation-placement", "植被放置策略", "树木、草丛的分布规则与性能", sub, 2, 25, tags=["环境"]),
    make_concept("rock-placement", "岩石放置", "岩石散布、材质变化与碰撞", sub, 2, 20, tags=["环境"]),
    make_concept("weather-terrain", "天气对地形的影响", "雨雪、泥泞、冰面对玩法的影响", sub, 3, 25, tags=["玩法"]),
    make_concept("terrain-collision", "地形碰撞", "地形碰撞面的精度与性能", sub, 2, 25, tags=["物理"]),
    make_concept("open-world-terrain", "开放世界地形", "大地图地形的分块加载与管理", sub, 3, 30, tags=["大地图"]),
    make_concept("level-art-handoff", "关卡美术交接", "灰盒到美术资产的地形交接流程", sub, 2, 25, tags=["协作"]),
    make_concept("terrain-data", "地形数据管理", "高度图、Splatmap的存储与版本管理", sub, 2, 25, tags=["管理"]),
    make_concept("world-machine", "World Machine工具", "World Machine程序化地形生成入门", sub, 3, 25, tags=["工具"]),
    make_concept("gaea-terrain", "Gaea地形工具", "Gaea地形生成与导出流程", sub, 3, 25, tags=["工具"]),
    make_concept("terrain-optimization", "地形优化", "地形渲染与内存的性能优化", sub, 3, 25, tags=["性能"], milestone=True),
]

# ── 9. lighting-narrative (光照叙事) — 20 concepts ──
sub = "lighting-narrative"
C += [
    make_concept("lighting-intro", "光照叙事概述", "光照在关卡设计中的叙事与引导作用", sub, 1, 20, tags=["基础"], milestone=True),
    make_concept("light-as-guide", "光照引导", "用明暗对比引导玩家移动方向", sub, 2, 25, tags=["引导"]),
    make_concept("mood-lighting", "氛围光照", "不同色温/亮度创造的情感氛围", sub, 2, 25, tags=["情感"]),
    make_concept("dynamic-lighting", "动态光照", "时间/事件驱动的光照变化", sub, 3, 25, tags=["动态"]),
    make_concept("baked-vs-realtime", "烘焙vs实时光照", "预烘焙与实时光照的取舍", sub, 2, 25, tags=["技术"]),
    make_concept("light-probe", "光照探针", "间接光照与反射探针的布局", sub, 3, 25, tags=["技术"]),
    make_concept("shadow-design", "阴影设计", "阴影在空间暗示与情感中的作用", sub, 2, 25, tags=["视觉"]),
    make_concept("color-temperature", "色温控制", "冷暖光色的情感映射", sub, 2, 20, tags=["色彩"]),
    make_concept("contrast-lighting", "对比度照明", "高/低对比照明的空间效果", sub, 2, 25, tags=["视觉"]),
    make_concept("volumetric-lighting", "体积光效", "雾光/上帝光的视觉与叙事效果", sub, 3, 25, tags=["特效"], milestone=True),
    make_concept("practical-light", "实用光源", "场景中火把/路灯等叙事性光源", sub, 2, 25, tags=["叙事"]),
    make_concept("light-puzzle", "光照谜题", "以光照为核心机制的关卡设计", sub, 3, 25, tags=["玩法"]),
    make_concept("horror-lighting", "恐怖光照", "恐怖游戏的黑暗与手电筒机制", sub, 3, 25, tags=["品类"]),
    make_concept("outdoor-lighting", "室外光照", "太阳光、天空光与时间系统", sub, 2, 25, tags=["室外"]),
    make_concept("indoor-lighting", "室内光照", "人工光源布局与反弹光", sub, 2, 25, tags=["室内"]),
    make_concept("light-performance", "光照性能", "光源数量、阴影贴图与性能预算", sub, 3, 25, tags=["性能"]),
    make_concept("post-process-ld", "后处理(LD)", "关卡设计师常用的后处理效果", sub, 2, 25, tags=["后处理"]),
    make_concept("day-night-cycle", "昼夜循环", "昼夜光照变化对关卡体验的影响", sub, 3, 25, tags=["动态"]),
    make_concept("emissive-material", "自发光材质", "自发光物体的引导与装饰作用", sub, 2, 20, tags=["材质"]),
    make_concept("lighting-review", "光照评审", "团队评审光照效果的标准与流程", sub, 2, 25, tags=["流程"]),
]

# ── 10. ld-documentation (LD文档) — 20 concepts ──
sub = "ld-documentation"
C += [
    make_concept("ld-doc-intro", "LD文档概述", "关卡设计文档的类型与用途", sub, 1, 20, tags=["基础"], milestone=True),
    make_concept("level-overview-doc", "关卡概览文档", "单个关卡的概念、目标与布局概述", sub, 1, 25, tags=["文档"]),
    make_concept("level-flowchart", "关卡流程图", "用流程图描述关卡路径与分支", sub, 2, 25, "practice", tags=["工具"]),
    make_concept("top-down-map", "俯视图设计", "2D俯视图的绘制规范与标注", sub, 2, 25, "practice", tags=["工具"], milestone=True),
    make_concept("encounter-doc", "遭遇战文档", "单场战斗的敌人配置与空间说明", sub, 2, 25, tags=["战斗"]),
    make_concept("script-event-doc", "脚本事件文档", "关卡内触发事件的时序与逻辑", sub, 2, 25, tags=["脚本"]),
    make_concept("pacing-chart", "节奏图表", "关卡强度/情感曲线的可视化文档", sub, 2, 25, tags=["节奏"]),
    make_concept("playtest-report", "测试报告", "关卡可玩性测试结果的记录格式", sub, 2, 25, tags=["测试"]),
    make_concept("feedback-log", "反馈日志", "测试反馈的收集、分类与处理", sub, 2, 20, tags=["反馈"]),
    make_concept("iteration-log", "迭代日志", "记录每次修改的原因、内容与效果", sub, 2, 20, tags=["迭代"]),
    make_concept("naming-convention", "命名规范", "关卡文件/资产/触发器的命名标准", sub, 1, 20, tags=["规范"]),
    make_concept("asset-list", "资产清单", "关卡所需美术资产的清单与优先级", sub, 2, 20, tags=["管理"]),
    make_concept("ld-review-process", "评审流程", "关卡评审的参与者、标准与节奏", sub, 2, 25, tags=["流程"]),
    make_concept("milestone-criteria", "里程碑标准", "灰盒/Alpha/Beta/Gold各阶段完成标准", sub, 2, 25, tags=["流程"], milestone=True),
    make_concept("design-intent-doc", "设计意图文档", "记录设计决策背后的理由与预期", sub, 2, 25, tags=["文档"]),
    make_concept("bug-report-ld", "Bug报告(LD)", "关卡Bug的描述模板与严重性分级", sub, 2, 20, tags=["测试"]),
    make_concept("handoff-doc", "交接文档", "关卡移交给其他LD/美术的文档", sub, 2, 25, tags=["协作"]),
    make_concept("postmortem-ld", "复盘文档(LD)", "项目结束后的关卡设计经验总结", sub, 3, 25, tags=["总结"]),
    make_concept("ld-portfolio", "LD作品集", "关卡设计师作品集的组织与展示", sub, 2, 30, tags=["职业"]),
    make_concept("ld-career", "LD职业发展", "从初级到高级关卡设计师的成长路径", sub, 2, 25, tags=["职业"], milestone=True),
]

# =============================================
# Edge definitions
# =============================================
E = []
def edge(s, t, rtype="prerequisite", strength=0.8):
    E.append({"source_id": s, "target_id": t, "relation_type": rtype, "strength": strength})

# ── spatial-narrative edges ──
edge("ld-overview", "spatial-storytelling")
edge("ld-overview", "visual-language")
edge("spatial-storytelling", "env-storytelling")
edge("spatial-storytelling", "landmark-design")
edge("spatial-storytelling", "negative-space")
edge("visual-language", "spatial-hierarchy")
edge("spatial-hierarchy", "linear-vs-open")
edge("spatial-hierarchy", "hub-spoke")
edge("spatial-hierarchy", "looping-path")
edge("spatial-storytelling", "world-building-ld")
edge("env-storytelling", "set-piece")
edge("landmark-design", "point-of-interest")
edge("spatial-hierarchy", "verticality")
edge("visual-language", "scale-proportion")
edge("spatial-storytelling", "discovery-design")
edge("negative-space", "density-design")
edge("env-storytelling", "theme-variation")
edge("spatial-storytelling", "immersion-design")
edge("point-of-interest", "player-path-analysis")

# ── pacing-curve edges ──
edge("ld-overview", "pacing-intro")
edge("pacing-intro", "tension-release")
edge("pacing-intro", "intensity-curve")
edge("tension-release", "three-act-level")
edge("intensity-curve", "three-act-level")
edge("three-act-level", "climax-design")
edge("pacing-intro", "rest-area")
edge("pacing-intro", "micro-pacing")
edge("micro-pacing", "macro-pacing")
edge("pacing-intro", "reward-pacing")
edge("pacing-intro", "content-gating")
edge("content-gating", "mechanic-introduction")
edge("intensity-curve", "difficulty-ramp")
edge("tension-release", "surprise-moment")
edge("rest-area", "backtracking-design")
edge("pacing-intro", "level-length")
edge("rest-area", "checkpoint-pacing")
edge("three-act-level", "narrative-pacing")
edge("rest-area", "exploration-pacing")
edge("rest-area", "downtime-design")
edge("macro-pacing", "pacing-analysis")

# ── guidance-design edges ──
edge("ld-overview", "guidance-intro")
edge("guidance-intro", "visual-guidance")
edge("guidance-intro", "audio-guidance")
edge("guidance-intro", "layout-guidance")
edge("visual-guidance", "breadcrumb-trail")
edge("layout-guidance", "affordance-ld")
edge("guidance-intro", "gating-mechanic")
edge("guidance-intro", "tutorial-level")
edge("guidance-intro", "show-dont-tell")
edge("guidance-intro", "signposting")
edge("signposting", "implicit-vs-explicit")
edge("show-dont-tell", "implicit-vs-explicit")
edge("visual-guidance", "flow-channel-ld")
edge("implicit-vs-explicit", "player-expectation")
edge("visual-guidance", "camera-control-ld")
edge("layout-guidance", "npc-guidance")
edge("signposting", "minimap-guidance")
edge("signposting", "objective-marker")
edge("guidance-intro", "lost-player-recovery")
edge("visual-guidance", "difficulty-communication")
edge("tutorial-level", "onboarding-sequence")

# ── blockout edges ──
edge("ld-overview", "blockout-intro")
edge("blockout-intro", "greybox-workflow")
edge("blockout-intro", "bsp-blocking")
edge("blockout-intro", "modular-kit")
edge("blockout-intro", "scale-reference")
edge("bsp-blocking", "collision-volume")
edge("blockout-intro", "playable-path")
edge("greybox-workflow", "prototype-test")
edge("prototype-test", "iteration-blockout")
edge("blockout-intro", "cover-placement")
edge("blockout-intro", "spawn-point")
edge("blockout-intro", "trigger-volume")
edge("collision-volume", "navmesh-basics")
edge("playable-path", "sightline-test")
edge("prototype-test", "flow-testing")
edge("iteration-blockout", "blockout-checklist")
edge("modular-kit", "kit-bashing")
edge("greybox-workflow", "proxy-asset")
edge("blockout-intro", "blockout-annotation")
edge("blockout-checklist", "blockout-review")

# ── metrics-design edges ──
edge("blockout-intro", "metrics-intro")
edge("metrics-intro", "character-metrics")
edge("character-metrics", "movement-speed")
edge("character-metrics", "jump-metrics")
edge("metrics-intro", "corridor-width")
edge("metrics-intro", "ceiling-height")
edge("metrics-intro", "door-size")
edge("metrics-intro", "stair-slope")
edge("jump-metrics", "platform-gap")
edge("metrics-intro", "combat-range")
edge("metrics-intro", "cover-height")
edge("metrics-intro", "visibility-range")
edge("metrics-intro", "interaction-range")
edge("combat-range", "spawn-distance")
edge("metrics-intro", "camera-distance-ld")
edge("combat-range", "ai-patrol-range")
edge("metrics-intro", "audio-range")
edge("metrics-intro", "metric-sheet")
edge("metric-sheet", "metric-validation")
edge("metric-sheet", "metric-exception")

# ── combat-space edges ──
edge("blockout-intro", "combat-space-intro")
edge("combat-space-intro", "arena-layout")
edge("combat-space-intro", "corridor-combat")
edge("arena-layout", "elevation-tactics")
edge("arena-layout", "flanking-route")
edge("combat-space-intro", "cover-system-ld")
edge("arena-layout", "choke-point")
edge("combat-space-intro", "escape-route")
edge("combat-space-intro", "enemy-spawn-area")
edge("arena-layout", "wave-arena")
edge("arena-layout", "boss-arena")
edge("combat-space-intro", "stealth-space")
edge("arena-layout", "destructible-env")
edge("combat-space-intro", "hazard-placement")
edge("combat-space-intro", "ammo-health-placement")
edge("cover-system-ld", "combat-flow")
edge("combat-space-intro", "sightline-combat")
edge("elevation-tactics", "multi-level-combat")
edge("arena-layout", "vehicle-combat-space")
edge("combat-flow", "combat-space-review")

# ── level-editor edges ──
edge("blockout-intro", "level-editor-intro")
edge("level-editor-intro", "ue5-level-editor")
edge("level-editor-intro", "unity-scene-editor")
edge("ue5-level-editor", "blueprint-scripting")
edge("ue5-level-editor", "level-streaming")
edge("level-streaming", "world-partition")
edge("ue5-level-editor", "sublevel-management")
edge("level-editor-intro", "version-control-ld")
edge("version-control-ld", "multi-user-editing")
edge("ue5-level-editor", "landscape-tool")
edge("ue5-level-editor", "foliage-tool")
edge("blueprint-scripting", "sequencer-ld")
edge("blueprint-scripting", "gameplay-ability-ld")
edge("level-editor-intro", "pcg-level-gen")
edge("level-editor-intro", "custom-editor-tool")
edge("level-editor-intro", "data-layer")
edge("level-editor-intro", "debug-visualization")
edge("level-editor-intro", "profiling-ld")
edge("profiling-ld", "optimization-ld")
edge("optimization-ld", "build-pipeline-ld")

# ── terrain-design edges ──
edge("level-editor-intro", "terrain-intro")
edge("terrain-intro", "heightmap")
edge("heightmap", "terrain-sculpting")
edge("terrain-intro", "terrain-material")
edge("terrain-intro", "terrain-lod")
edge("heightmap", "procedural-terrain")
edge("terrain-intro", "road-river")
edge("terrain-intro", "cliff-cave")
edge("terrain-intro", "biome-design")
edge("terrain-intro", "water-body")
edge("biome-design", "vegetation-placement")
edge("biome-design", "rock-placement")
edge("terrain-intro", "weather-terrain")
edge("terrain-intro", "terrain-collision")
edge("terrain-intro", "open-world-terrain")
edge("terrain-intro", "level-art-handoff")
edge("heightmap", "terrain-data")
edge("procedural-terrain", "world-machine")
edge("procedural-terrain", "gaea-terrain")
edge("terrain-lod", "terrain-optimization")

# ── lighting-narrative edges ──
edge("ld-overview", "lighting-intro")
edge("lighting-intro", "light-as-guide")
edge("lighting-intro", "mood-lighting")
edge("lighting-intro", "dynamic-lighting")
edge("lighting-intro", "baked-vs-realtime")
edge("baked-vs-realtime", "light-probe")
edge("lighting-intro", "shadow-design")
edge("mood-lighting", "color-temperature")
edge("mood-lighting", "contrast-lighting")
edge("dynamic-lighting", "volumetric-lighting")
edge("lighting-intro", "practical-light")
edge("lighting-intro", "light-puzzle")
edge("mood-lighting", "horror-lighting")
edge("lighting-intro", "outdoor-lighting")
edge("lighting-intro", "indoor-lighting")
edge("baked-vs-realtime", "light-performance")
edge("lighting-intro", "post-process-ld")
edge("dynamic-lighting", "day-night-cycle")
edge("lighting-intro", "emissive-material")
edge("light-performance", "lighting-review")

# ── ld-documentation edges ──
edge("ld-overview", "ld-doc-intro")
edge("ld-doc-intro", "level-overview-doc")
edge("ld-doc-intro", "level-flowchart")
edge("ld-doc-intro", "top-down-map")
edge("ld-doc-intro", "encounter-doc")
edge("ld-doc-intro", "script-event-doc")
edge("ld-doc-intro", "pacing-chart")
edge("ld-doc-intro", "playtest-report")
edge("playtest-report", "feedback-log")
edge("feedback-log", "iteration-log")
edge("ld-doc-intro", "naming-convention")
edge("ld-doc-intro", "asset-list")
edge("ld-doc-intro", "ld-review-process")
edge("ld-review-process", "milestone-criteria")
edge("ld-doc-intro", "design-intent-doc")
edge("playtest-report", "bug-report-ld")
edge("ld-doc-intro", "handoff-doc")
edge("milestone-criteria", "postmortem-ld")
edge("ld-doc-intro", "ld-portfolio")
edge("ld-portfolio", "ld-career")

# ── cross-subdomain edges (related) ──
edge("spatial-storytelling", "pacing-intro", "related", 0.7)
edge("visual-guidance", "light-as-guide", "related", 0.7)
edge("blockout-intro", "metrics-intro", "prerequisite", 0.8)  # already added above
edge("cover-placement", "cover-system-ld", "related", 0.7)
edge("playable-path", "combat-flow", "related", 0.7)
edge("landmark-design", "light-as-guide", "related", 0.7)
edge("terrain-intro", "biome-design", "prerequisite", 0.8)  # already added
edge("blockout-review", "ld-review-process", "related", 0.7)
edge("pacing-analysis", "pacing-chart", "related", 0.7)
edge("set-piece", "climax-design", "related", 0.7)
edge("prototype-test", "playtest-report", "related", 0.7)
edge("navmesh-basics", "ai-patrol-range", "related", 0.7)
edge("lighting-intro", "visual-guidance", "related", 0.7)
edge("scale-reference", "character-metrics", "related", 0.7)

# =============================================
# Deduplicate edges
# =============================================
seen = set()
deduped = []
for e in E:
    key = (e["source_id"], e["target_id"])
    if key not in seen:
        seen.add(key)
        deduped.append(e)
E = deduped

# =============================================
# Validation
# =============================================
cids = {c["id"] for c in C}
for e in E:
    assert e["source_id"] in cids, f"Edge source {e['source_id']} not found"
    assert e["target_id"] in cids, f"Edge target {e['target_id']} not found"

milestones = [c for c in C if c["is_milestone"]]
subdomain_coverage = {s["id"] for s in SUBDOMAINS}
milestone_subs = {c["subdomain_id"] for c in milestones}
assert milestone_subs == subdomain_coverage, f"Missing milestone subs: {subdomain_coverage - milestone_subs}"

# =============================================
# Output
# =============================================
data = {
    "domain": DOMAIN,
    "subdomains": SUBDOMAINS,
    "concepts": C,
    "edges": E,
}

out_dir = os.path.join(os.path.dirname(__file__), "..", "seed", "level-design")
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "seed_graph.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ Level Design seed graph generated:")
print(f"   Concepts: {len(C)}")
print(f"   Edges: {len(E)}")
print(f"   Subdomains: {len(SUBDOMAINS)}")
print(f"   Milestones: {len(milestones)}")
print(f"   Output: {out_path}")
