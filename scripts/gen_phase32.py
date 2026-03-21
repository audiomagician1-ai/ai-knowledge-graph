"""Phase 32: 音效设计知识球 (game-audio-sfx) — 种子图谱+RAG生成"""
import json, os, random
from datetime import datetime

DOMAIN = "game-audio-sfx"
DOMAIN_NAME = "音效设计"
PREFIX = "sfx"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── 9 subdomains ──
subdomains = [
    {"id": "sound-design-theory", "name": "音效设计理论", "description": "声音心理学、音效分类、音效设计方法论与美学原则", "order": 1},
    {"id": "foley-recording", "name": "Foley录制", "description": "拟音技术、录音设备、声音采集与后期处理", "order": 2},
    {"id": "audio-middleware", "name": "音频中间件", "description": "Wwise/FMOD集成、事件系统、RTPC参数与音频管线", "order": 3},
    {"id": "spatial-audio", "name": "空间音频", "description": "3D音频、HRTF、声源衰减、遮挡与声学传播模拟", "order": 4},
    {"id": "dsp-effects", "name": "混响与DSP", "description": "混响算法、EQ/压缩/失真等效果器链与音频DSP处理", "order": 5},
    {"id": "audio-asset-management", "name": "声音资源管理", "description": "音频格式、压缩策略、内存管理、流式加载与资源组织", "order": 6},
    {"id": "dialogue-processing", "name": "对白处理", "description": "语音录制、对白编辑、语音合成与本地化音频管线", "order": 7},
    {"id": "ambient-sound", "name": "环境声设计", "description": "环境氛围音、天气/生物音景、随机化与动态混音", "order": 8},
    {"id": "audio-optimization", "name": "音效优化", "description": "音频性能分析、预算管理、平台适配与质量保证", "order": 9},
]

# ── concepts per subdomain (20 each = 180 total) ──
concepts_data = {
    "sound-design-theory": [
        ("sfx-sdt-psychoacoustics", "声音心理学", "研究人类对声音的感知、频率敏感度与听觉认知"),
        ("sfx-sdt-sound-taxonomy", "音效分类体系", "按功能(UI/环境/反馈/特效)和来源(录制/合成/处理)分类音效"),
        ("sfx-sdt-emotional-design", "声音情感设计", "利用音效触发情感反应，建立听觉情感映射"),
        ("sfx-sdt-layering", "音效分层技术", "多层声音叠加构建丰富复杂的音效"),
        ("sfx-sdt-sweetener", "Sweetener增强", "添加微妙的辅助声音增强主音效的冲击力与质感"),
        ("sfx-sdt-silence-design", "静默设计", "有意识地使用静默和留白创造戏剧性效果"),
        ("sfx-sdt-diegetic-vs-nondiegetic", "叙事内外音效", "区分故事世界内部音效和非叙事音效(UI/音乐)"),
        ("sfx-sdt-sound-metaphor", "声音隐喻", "使用象征性声音传达抽象概念或游戏状态"),
        ("sfx-sdt-frequency-spectrum", "频谱分析与管理", "管理音效的频率分布避免遮蔽和冲突"),
        ("sfx-sdt-impact-design", "打击感音效设计", "设计具有物理冲击感的动作音效"),
        ("sfx-sdt-ui-sound", "UI音效设计", "界面交互音效的设计原则与一致性策略"),
        ("sfx-sdt-feedback-loop", "音频反馈循环", "通过音效提供即时游戏状态反馈"),
        ("sfx-sdt-audio-branding", "音频品牌化", "创建可识别的声音标识与音效风格"),
        ("sfx-sdt-procedural-audio", "程序化音频", "使用算法和参数实时生成音效"),
        ("sfx-sdt-synthesis-basics", "声音合成基础", "减法/加法/FM/粒子合成的原理与应用"),
        ("sfx-sdt-sampling-technique", "采样技术", "录音采样、Round-Robin与Velocity层的设计"),
        ("sfx-sdt-transient-design", "瞬态设计", "塑造声音的起始阶段(Attack)以增强辨识度"),
        ("sfx-sdt-pitch-variation", "音高变化技术", "通过音高随机化和调制增加音效多样性"),
        ("sfx-sdt-sound-storytelling", "声音叙事", "利用音效推动故事发展和建立世界观"),
        ("sfx-sdt-reference-library", "参考音效库", "建立和组织音效参考库辅助创作"),
    ],
    "foley-recording": [
        ("sfx-fr-foley-basics", "拟音基础", "Foley录制的历史、原理与基本流程"),
        ("sfx-fr-footsteps", "脚步音录制", "不同地面材质的脚步声录制技术"),
        ("sfx-fr-cloth-movement", "布料运动音", "服装和布料运动产生的声音录制"),
        ("sfx-fr-prop-handling", "道具操作音", "武器、工具等道具的声音录制技术"),
        ("sfx-fr-microphone-selection", "麦克风选择", "不同类型麦克风的特性与录音场景适配"),
        ("sfx-fr-recording-environment", "录音环境", "录音棚设计、声学处理与外景录音"),
        ("sfx-fr-contact-mic", "接触式麦克风", "通过振动传感录制物体内部声音"),
        ("sfx-fr-field-recording", "外景录音", "户外环境声和特殊声源的现场采集"),
        ("sfx-fr-recording-chain", "录音信号链", "前置放大器、AD转换器与监听系统"),
        ("sfx-fr-editing-workflow", "音频编辑工作流", "录音素材的剪辑、降噪与整理"),
        ("sfx-fr-noise-reduction", "降噪技术", "录音中的噪音消除与修复技术"),
        ("sfx-fr-sound-library-build", "声音库建设", "系统化建立和维护个人/工作室声音库"),
        ("sfx-fr-metadata-tagging", "元数据标签", "音效文件的命名规范与元数据管理"),
        ("sfx-fr-destructive-recording", "破坏性录音", "不可重复的特殊音效(爆炸/碎裂)录制"),
        ("sfx-fr-water-sounds", "水声录制", "各种水体效果声音的录制技术"),
        ("sfx-fr-vehicle-recording", "载具录音", "汽车、飞机等载具引擎与运动声录制"),
        ("sfx-fr-creature-voice", "生物音效设计", "怪物/NPC声音的创意录制与处理"),
        ("sfx-fr-impact-recording", "撞击音录制", "各类材质碰撞声音的录制方法"),
        ("sfx-fr-ambience-capture", "环境音捕捉", "自然和城市环境音的立体声/环绕声采集"),
        ("sfx-fr-session-management", "录音会话管理", "大型录音项目的时间/资源/人员协调"),
    ],
    "audio-middleware": [
        ("sfx-am-wwise-overview", "Wwise概览", "Audiokinetic Wwise的架构、工作流与核心概念"),
        ("sfx-am-fmod-overview", "FMOD概览", "FMOD Studio的架构、工作流与核心概念"),
        ("sfx-am-event-system", "事件系统", "音频事件的创建、触发与参数控制"),
        ("sfx-am-rtpc", "RTPC参数", "实时参数控制(距离/速度/状态)驱动音效变化"),
        ("sfx-am-switch-state", "Switch与State", "基于游戏状态的音效切换与分组管理"),
        ("sfx-am-soundbank", "SoundBank管理", "音频资源的打包、加载与内存管理策略"),
        ("sfx-am-bus-routing", "总线路由", "音频信号流的总线层级、路由与混音"),
        ("sfx-am-profiler", "音频Profiler", "实时监控音频性能、CPU/内存消耗与调试"),
        ("sfx-am-game-integration", "游戏引擎集成", "Wwise/FMOD与UE5/Unity的集成方法"),
        ("sfx-am-interactive-music", "交互音乐集成", "在中间件中实现自适应音乐系统"),
        ("sfx-am-random-container", "随机容器", "使用随机播放容器增加音效多样性"),
        ("sfx-am-sequence-container", "序列容器", "按序列播放音效组的容器设计"),
        ("sfx-am-blend-container", "混合容器", "多轨音效的参数化混合容器"),
        ("sfx-am-attenuation", "衰减曲线", "声源距离衰减的自定义曲线与配置"),
        ("sfx-am-obstruction-occlusion", "遮挡与阻隔", "基于几何的声音遮挡(Obstruction)与阻隔(Occlusion)"),
        ("sfx-am-aux-send", "辅助发送", "使用Aux Bus实现环境混响与效果共享"),
        ("sfx-am-dialogue-system", "对白系统", "中间件中的对白管理、优先级与本地化"),
        ("sfx-am-plugin-development", "插件开发", "为Wwise/FMOD开发自定义DSP插件"),
        ("sfx-am-source-control", "版本控制集成", "音频项目的Git/Perforce版本管理"),
        ("sfx-am-batch-processing", "批量处理", "大规模音效资产的批量导入、转换与处理"),
    ],
    "spatial-audio": [
        ("sfx-sa-3d-audio-basics", "3D音频基础", "3D声音定位的原理与实现方法"),
        ("sfx-sa-hrtf", "HRTF头部传输函数", "基于头部传输函数的精确声音空间定位"),
        ("sfx-sa-binaural-audio", "双耳音频", "通过耳机实现逼真3D音频的技术"),
        ("sfx-sa-surround-sound", "环绕声系统", "5.1/7.1/Atmos等多声道环绕声的实现"),
        ("sfx-sa-ambisonics", "Ambisonics", "全景声场捕捉与解码到各种扬声器配置"),
        ("sfx-sa-distance-model", "距离模型", "声源距离衰减的物理模型与游戏适配"),
        ("sfx-sa-doppler-effect", "多普勒效应", "运动声源的频率偏移模拟"),
        ("sfx-sa-room-acoustics", "房间声学", "封闭空间的声学特性模拟与早反射"),
        ("sfx-sa-reverb-zone", "混响区域", "空间触发的混响区域与过渡混合"),
        ("sfx-sa-sound-propagation", "声音传播", "声波在复杂环境中的传播路径计算"),
        ("sfx-sa-occlusion-geometry", "几何遮挡", "基于场景几何的声音遮挡计算"),
        ("sfx-sa-portal-system", "Portal声学系统", "通过门窗等开口的声音传播模拟"),
        ("sfx-sa-listener-position", "听者位置", "虚拟听者的定位与多听者场景"),
        ("sfx-sa-speaker-panning", "声像摆位", "多声道输出的声像分配算法"),
        ("sfx-sa-spatial-plugin", "空间音频插件", "Project Acoustics/Steam Audio等插件"),
        ("sfx-sa-vr-audio", "VR音频", "虚拟现实中的360°音频与头部追踪"),
        ("sfx-sa-height-channel", "高度通道", "Dolby Atmos等包含高度信息的音频格式"),
        ("sfx-sa-outdoor-acoustics", "室外声学", "开放空间的声音衰减与环境效果"),
        ("sfx-sa-underwater-audio", "水下音效", "水下环境的声学特性与效果模拟"),
        ("sfx-sa-directivity-pattern", "声源指向性", "不同声源的辐射方向性模式设置"),
    ],
    "dsp-effects": [
        ("sfx-dsp-reverb-types", "混响类型", "算法混响、卷积混响与混合混响的对比"),
        ("sfx-dsp-convolution-reverb", "卷积混响", "使用IR脉冲响应实现真实空间混响"),
        ("sfx-dsp-eq-filtering", "EQ均衡与滤波", "参数EQ、图形EQ与滤波器的音效塑形"),
        ("sfx-dsp-compression", "动态压缩", "压缩器/限制器/扩展器的动态范围控制"),
        ("sfx-dsp-distortion", "失真效果", "过载/Bitcrush/Wave Shaping等失真处理"),
        ("sfx-dsp-delay-echo", "延迟与回声", "延迟线、Ping-Pong延迟与回声效果"),
        ("sfx-dsp-chorus-flanger", "合唱与镶边", "Chorus/Flanger/Phaser调制效果"),
        ("sfx-dsp-pitch-shifting", "变调处理", "实时变调与时间拉伸算法"),
        ("sfx-dsp-granular-processing", "粒度处理", "粒子合成与粒度时间拉伸技术"),
        ("sfx-dsp-sidechain", "侧链处理", "使用侧链信号控制效果器(Ducking等)"),
        ("sfx-dsp-noise-gate", "噪声门", "基于阈值的噪声抑制与声音门控"),
        ("sfx-dsp-vocoder", "声码器", "载波/调制信号的声码处理与机器人音效"),
        ("sfx-dsp-spectral-processing", "频谱处理", "FFT频域音频处理与频谱重塑"),
        ("sfx-dsp-transient-shaper", "瞬态塑形", "增强或抑制声音的瞬态(Attack/Sustain)"),
        ("sfx-dsp-multiband", "多段处理", "分频段独立处理的多段压缩/效果"),
        ("sfx-dsp-limiter-maximizer", "限幅与最大化", "响度最大化与真峰值限制"),
        ("sfx-dsp-effect-chain", "效果链设计", "音效处理效果链的顺序与组合策略"),
        ("sfx-dsp-parallel-processing", "并行处理", "干湿信号并行混合的处理技术"),
        ("sfx-dsp-automation", "参数自动化", "效果器参数的时间轴自动化与包络控制"),
        ("sfx-dsp-custom-dsp", "自定义DSP开发", "使用C++/JUCE开发自定义音频处理插件"),
    ],
    "audio-asset-management": [
        ("sfx-aam-audio-formats", "音频格式", "WAV/OGG/ADPCM/Opus等格式的特性与选择"),
        ("sfx-aam-compression-strategy", "压缩策略", "不同平台和场景下的音频压缩方案"),
        ("sfx-aam-memory-budget", "内存预算", "音频内存分配与使用上限管理"),
        ("sfx-aam-streaming-audio", "流式加载", "大文件音频的流式传输与预加载策略"),
        ("sfx-aam-naming-convention", "命名规范", "音效文件的标准化命名与目录结构"),
        ("sfx-aam-asset-pipeline", "音频资产管线", "从录制到引擎的完整音频资产工作流"),
        ("sfx-aam-version-control", "版本控制", "音频文件的版本管理与团队协作"),
        ("sfx-aam-sample-rate", "采样率选择", "44.1/48/96kHz采样率的场景选择"),
        ("sfx-aam-bit-depth", "位深度", "16/24/32bit音频精度与性能权衡"),
        ("sfx-aam-batch-conversion", "批量转换", "自动化批量格式转换与处理脚本"),
        ("sfx-aam-asset-database", "资产数据库", "音效资产的数据库管理与快速检索"),
        ("sfx-aam-localization-audio", "本地化音频", "多语言音频资源的组织与切换策略"),
        ("sfx-aam-redundancy-check", "冗余检查", "检测和消除重复/未使用的音频资源"),
        ("sfx-aam-quality-tiers", "质量分级", "根据平台能力提供不同质量的音频"),
        ("sfx-aam-dynamic-loading", "动态加载", "运行时按需加载和卸载音频资源"),
        ("sfx-aam-soundbank-strategy", "SoundBank策略", "音频包的分组、加载顺序与依赖管理"),
        ("sfx-aam-backup-archival", "备份与归档", "音频项目的长期存储与灾备策略"),
        ("sfx-aam-delivery-spec", "交付规格", "音效资产的交付标准与验收检查表"),
        ("sfx-aam-platform-specific", "平台特定处理", "PC/主机/移动端的音频格式与限制"),
        ("sfx-aam-documentation", "音效文档", "音效设计文档(Sound Design Document)的编写"),
    ],
    "dialogue-processing": [
        ("sfx-dp-voice-recording", "语音录制", "配音演员指导、录音流程与技术要求"),
        ("sfx-dp-dialogue-editing", "对白编辑", "语音剪辑、降噪、均衡与动态处理"),
        ("sfx-dp-tts-synthesis", "语音合成(TTS)", "文本转语音技术在游戏中的应用"),
        ("sfx-dp-lip-sync", "口型同步", "语音与角色口型动画的时间对齐"),
        ("sfx-dp-voice-direction", "配音导演", "配音录制会话中的表演指导与质量控制"),
        ("sfx-dp-casting", "演员选角", "配音演员的选角流程与试音评估"),
        ("sfx-dp-processing-chain", "对白处理链", "对白音频的标准处理流程(EQ→Comp→DeEss→Limit)"),
        ("sfx-dp-emotion-variation", "情感变体", "同一台词不同情感状态的录制与管理"),
        ("sfx-dp-radio-comm", "无线电通讯音效", "模拟无线电/通讯设备的对白效果处理"),
        ("sfx-dp-crowd-walla", "人群底噪", "背景人群声(Walla)的录制与混音"),
        ("sfx-dp-barks-efforts", "Barks与动作音", "短促反应音(受伤/惊讶/用力)的录制"),
        ("sfx-dp-localization-pipeline", "本地化管线", "多语言配音的录制、管理与集成"),
        ("sfx-dp-interactive-dialogue", "交互式对白", "分支对话系统的音频管理"),
        ("sfx-dp-subtitles-integration", "字幕集成", "音频与字幕时间码的同步方案"),
        ("sfx-dp-noise-floor", "底噪标准", "录音室底噪标准与一致性控制"),
        ("sfx-dp-de-esser", "齿音消除", "De-Esser处理消除过亮的齿擦音"),
        ("sfx-dp-breath-control", "呼吸音处理", "对白中呼吸音的保留/减弱/移除决策"),
        ("sfx-dp-voice-aging", "声音老化处理", "模拟角色年龄变化的语音处理技术"),
        ("sfx-dp-alien-voice", "非人类语音", "怪物/机器人/外星人语音的创意设计"),
        ("sfx-dp-dialogue-priority", "对白优先级", "对白与其他音频的优先级调度与闪避"),
    ],
    "ambient-sound": [
        ("sfx-as-ambience-layers", "环境音分层", "基础底层+细节层+随机事件层的分层设计"),
        ("sfx-as-weather-system", "天气音效系统", "风/雨/雷/雪等天气声的动态混合"),
        ("sfx-as-biome-soundscape", "生态音景", "不同生态环境(森林/沙漠/城市)的声景设计"),
        ("sfx-as-day-night-cycle", "昼夜音效", "随时间变化的环境声过渡与切换"),
        ("sfx-as-crowd-system", "人群音效系统", "动态人群密度和活动类型的音效调度"),
        ("sfx-as-random-emitter", "随机发射器", "带随机延迟/音高/位置的环境音事件"),
        ("sfx-as-dynamic-mix", "动态混音", "基于游戏状态自适应调整环境声层级"),
        ("sfx-as-music-ambient-blend", "音乐与环境融合", "环境音与背景音乐的无缝过渡"),
        ("sfx-as-interior-exterior", "室内外过渡", "进入/离开建筑时的声学环境切换"),
        ("sfx-as-zone-based", "区域音效", "基于游戏区域的环境声管理与过渡"),
        ("sfx-as-interactive-ambient", "交互式环境音", "响应玩家行为变化的环境声音"),
        ("sfx-as-wind-system", "风声系统", "根据地形和高度变化的动态风声"),
        ("sfx-as-water-ambient", "水体环境音", "河流/海浪/雨滴等水相关环境声"),
        ("sfx-as-wildlife-audio", "野生动物音效", "鸟鸣/虫鸣等生物音效的时空分布"),
        ("sfx-as-industrial-ambient", "工业环境音", "机械/工厂/城市机器的环境声设计"),
        ("sfx-as-horror-ambient", "恐怖氛围音", "恐怖游戏特有的心理压迫音效设计"),
        ("sfx-as-sci-fi-ambient", "科幻环境音", "太空站/飞船/未来城市的声景设计"),
        ("sfx-as-silence-technique", "静默技巧", "利用突然的静默增强紧张感或戏剧性"),
        ("sfx-as-procedural-ambient", "程序化环境音", "运行时参数驱动的环境声生成"),
        ("sfx-as-lfe-rumble", "低频震动", "LFE声道的隆隆声与体感反馈音效"),
    ],
    "audio-optimization": [
        ("sfx-ao-voice-limit", "同时发声限制", "最大同时发声数的管理与优先级策略"),
        ("sfx-ao-priority-system", "音效优先级", "基于重要性和距离的音效优先级系统"),
        ("sfx-ao-virtualization", "声音虚拟化", "超出发声限制时的声音虚拟化处理"),
        ("sfx-ao-lod-audio", "音频LOD", "基于距离的音效细节层级(简化/完整)"),
        ("sfx-ao-cpu-profiling", "CPU性能分析", "音频线程的CPU占用分析与优化"),
        ("sfx-ao-memory-profiling", "内存分析", "音频内存使用的监控与泄漏检测"),
        ("sfx-ao-platform-budget", "平台预算", "不同平台(PC/主机/移动)的音频预算分配"),
        ("sfx-ao-decode-cost", "解码成本", "不同编码格式的解码CPU开销对比"),
        ("sfx-ao-streaming-strategy", "流式策略", "音频流的预缓冲、优先级与带宽控制"),
        ("sfx-ao-sample-pooling", "采样池化", "共享采样数据减少内存重复占用"),
        ("sfx-ao-effect-budget", "效果器预算", "DSP效果的CPU消耗预算与分配"),
        ("sfx-ao-occlusion-cost", "遮挡计算成本", "空间音频遮挡计算的性能优化"),
        ("sfx-ao-batch-operation", "批量操作优化", "音频操作的批处理减少系统调用"),
        ("sfx-ao-mobile-optimization", "移动端优化", "手机/平板设备的音频特殊优化"),
        ("sfx-ao-latency-reduction", "延迟优化", "音频输出延迟的测量与减少方法"),
        ("sfx-ao-mix-snapshot", "快照混音", "预设混音快照的快速切换(战斗/对话/菜单)"),
        ("sfx-ao-regression-testing", "回归测试", "音频变更后的自动化回归测试"),
        ("sfx-ao-qa-checklist", "QA检查表", "音效质量保证的标准检查清单"),
        ("sfx-ao-platform-certification", "平台认证", "Sony/Microsoft/Nintendo音频认证要求"),
        ("sfx-ao-final-mix", "终混与母带", "游戏音频的最终混音平衡与响度标准"),
    ],
}

# Build concepts list and milestones
concepts = []
milestones = []
milestone_order = 0
for sub_id, items in concepts_data.items():
    for i, (cid, name, desc) in enumerate(items):
        is_ms = (i == 2 or i == 9 or i == 17)  # ~3-4 milestones per subdomain
        concepts.append({
            "id": cid,
            "name": name,
            "description": desc,
            "domain_id": DOMAIN,
            "subdomain_id": sub_id,
            "difficulty": min(5, 1 + i // 4),
            "estimated_minutes": 25 + (i % 4) * 5,
            "content_type": "conceptual" if i < 10 else "practical",
            "tags": [],
            "is_milestone": is_ms,
        })
        if is_ms:
            milestone_order += 1
            milestones.append({
                "concept_id": cid,
                "name": name,
                "description": f"掌握{name}的核心理论与实践方法",
                "order": milestone_order,
            })

# Build edges (within-subdomain sequential + cross-subdomain)
edges = []
for sub_id, items in concepts_data.items():
    ids = [it[0] for it in items]
    for j in range(len(ids) - 1):
        edges.append({"source_id": ids[j], "target_id": ids[j+1], "relation_type": "prerequisite", "strength": 0.8})

# Cross-subdomain edges
cross_edges = [
    ("sfx-sdt-layering", "sfx-fr-foley-basics", "related", 0.6),
    ("sfx-sdt-procedural-audio", "sfx-am-wwise-overview", "related", 0.6),
    ("sfx-fr-microphone-selection", "sfx-fr-recording-chain", "prerequisite", 0.7),
    ("sfx-am-event-system", "sfx-sa-3d-audio-basics", "related", 0.6),
    ("sfx-am-attenuation", "sfx-sa-distance-model", "related", 0.7),
    ("sfx-am-obstruction-occlusion", "sfx-sa-occlusion-geometry", "related", 0.8),
    ("sfx-dsp-reverb-types", "sfx-sa-room-acoustics", "related", 0.7),
    ("sfx-dsp-convolution-reverb", "sfx-sa-reverb-zone", "related", 0.7),
    ("sfx-dsp-eq-filtering", "sfx-dp-processing-chain", "related", 0.6),
    ("sfx-aam-audio-formats", "sfx-aam-compression-strategy", "prerequisite", 0.8),
    ("sfx-aam-memory-budget", "sfx-ao-memory-profiling", "related", 0.7),
    ("sfx-aam-streaming-audio", "sfx-ao-streaming-strategy", "related", 0.7),
    ("sfx-dp-voice-recording", "sfx-fr-microphone-selection", "related", 0.6),
    ("sfx-dp-dialogue-editing", "sfx-dsp-eq-filtering", "related", 0.5),
    ("sfx-as-ambience-layers", "sfx-am-random-container", "related", 0.6),
    ("sfx-as-weather-system", "sfx-as-random-emitter", "prerequisite", 0.7),
    ("sfx-ao-voice-limit", "sfx-am-profiler", "related", 0.6),
    ("sfx-ao-priority-system", "sfx-am-bus-routing", "related", 0.5),
    ("sfx-sdt-synthesis-basics", "sfx-dsp-granular-processing", "related", 0.6),
]
for src, tgt, rel, st in cross_edges:
    edges.append({"source_id": src, "target_id": tgt, "relation_type": rel, "strength": st})

seed_graph = {
    "domain": DOMAIN,
    "subdomains": subdomains,
    "concepts": concepts,
    "edges": edges,
    "milestones": milestones,
}

seed_path = os.path.join(BASE_DIR, "data", "seed", DOMAIN, "seed_graph.json")
with open(seed_path, "w", encoding="utf-8") as f:
    json.dump(seed_graph, f, ensure_ascii=False, indent=2)
print(f"Seed: {len(concepts)} concepts, {len(edges)} edges, {len(subdomains)} subdomains, {len(milestones)} milestones")

# ── Generate RAG docs ──
rag_dir = os.path.join(BASE_DIR, "data", "rag", DOMAIN)
total_chars = 0
doc_by_sub = {}
doc_list = []

for c in concepts:
    sub = c["subdomain_id"]
    sub_name = next(s["name"] for s in subdomains if s["id"] == sub)
    
    content = f"""---
domain: {DOMAIN}
subdomain: {sub}
concept_id: {c['id']}
difficulty: {c['difficulty']}
---

# {c['name']}

## 概述

{c['description']}。这是{DOMAIN_NAME}领域「{sub_name}」子域的核心概念，难度等级为{c['difficulty']}/5。

## 核心要点

### 1. 基本概念

{c['name']}是{sub_name}中的重要环节。理解它的基本原理是音效设计实践的基础。

### 2. 实践方法

在实际游戏音效项目中，{c['name']}的应用需要结合具体的游戏类型和平台特性。常见的实践方法包括：

- 从参考音效和音效库入手，建立对目标效果的听觉认知
- 通过反复迭代和用户测试调整参数
- 在游戏引擎中实时验证音效的表现

### 3. 进阶技巧

掌握基础后，可以探索{c['name']}的高级应用：

- 结合程序化生成增加音效多样性
- 优化CPU/内存消耗满足性能预算
- 与音频中间件深度集成实现复杂交互

## 常见问题

1. **如何评估{c['name']}的质量？** — 通过AB对比测试和玩家反馈来量化效果。
2. **性能影响如何？** — 需在音频Profiler中监测实时开销并优化。

## 相关概念

- 所属子域：{sub_name}
- 所属领域：{DOMAIN_NAME}
"""
    
    fpath = os.path.join(rag_dir, f"{c['id']}.md")
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)
    
    total_chars += len(content)
    doc_by_sub[sub] = doc_by_sub.get(sub, 0) + 1
    doc_list.append({"id": c["id"], "file": f"{c['id']}.md", "subdomain": sub, "chars": len(content)})

# Generate _index.json
index = {
    "version": "1.0.0",
    "domain": DOMAIN,
    "domain_name": DOMAIN_NAME,
    "generated_at": datetime.now().isoformat(),
    "total_concepts": len(doc_list),
    "stats": {
        "total_docs": len(doc_list),
        "total_chars": total_chars,
        "by_subdomain": dict(sorted(doc_by_sub.items()))
    },
    "documents": doc_list
}

with open(os.path.join(rag_dir, "_index.json"), "w", encoding="utf-8") as f:
    json.dump(index, f, ensure_ascii=False, indent=2)

print(f"RAG: {len(doc_list)} docs, {total_chars} chars, {len(doc_by_sub)} subdomains")
print("Done!")
