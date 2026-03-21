"""Fix game-audio-sfx cross-sphere link target IDs"""
import json

p = "D:/EchoAgent/projects/ai-knowledge-graph/data/seed/cross_sphere_links.json"
d = json.load(open(p, "r", encoding="utf-8"))

# Remove the 25 broken links we just added
d["links"] = [l for l in d["links"] if l.get("source_domain") != "game-audio-sfx"]

# Add corrected links with verified target IDs
new_links = [
    # game-audio-sfx ↔ game-audio-music
    {"source_domain":"game-audio-sfx","source_id":"sfx-dsp-reverb-types","target_domain":"game-audio-music","target_id":"game-audio-music-reverb-delay","relation":"related","strength":0.8,"description":"混响技术在音乐和音效中的共享应用"},
    {"source_domain":"game-audio-sfx","source_id":"sfx-am-wwise-overview","target_domain":"game-audio-music","target_id":"game-audio-music-wwise-overview","relation":"related","strength":0.8,"description":"Wwise中间件同时管理音效和音乐"},
    {"source_domain":"game-audio-sfx","source_id":"sfx-am-fmod-overview","target_domain":"game-audio-music","target_id":"game-audio-music-fmod-overview","relation":"related","strength":0.8,"description":"FMOD中间件同时管理音效和音乐"},
    {"source_domain":"game-audio-sfx","source_id":"sfx-as-dynamic-mix","target_domain":"game-audio-music","target_id":"game-audio-music-dynamic-mixing","relation":"related","strength":0.7,"description":"动态混音同时影响环境声和音乐"},
    {"source_domain":"game-audio-sfx","source_id":"sfx-as-music-ambient-blend","target_domain":"game-audio-music","target_id":"game-audio-music-adaptive-overview","relation":"related","strength":0.7,"description":"环境音与自适应音乐的融合"},

    # game-audio-sfx ↔ game-engine
    {"source_domain":"game-audio-sfx","source_id":"sfx-am-game-integration","target_domain":"game-engine","target_id":"audio-system-intro","relation":"related","strength":0.7,"description":"音频中间件与游戏引擎音频系统的集成"},
    {"source_domain":"game-audio-sfx","source_id":"sfx-sa-3d-audio-basics","target_domain":"game-engine","target_id":"audio-source-listener","relation":"related","strength":0.7,"description":"3D音频基础与引擎Audio Source/Listener"},

    # game-audio-sfx ↔ animation
    {"source_domain":"game-audio-sfx","source_id":"sfx-fr-footsteps","target_domain":"animation","target_id":"anim-notify-event","relation":"related","strength":0.7,"description":"脚步音与动画通知事件的同步"},
    {"source_domain":"game-audio-sfx","source_id":"sfx-dp-lip-sync","target_domain":"animation","target_id":"anim-blend-basics","relation":"related","strength":0.6,"description":"口型同步与动画混合技术"},

    # game-audio-sfx ↔ vfx
    {"source_domain":"game-audio-sfx","source_id":"sfx-sdt-impact-design","target_domain":"vfx","target_id":"vfx-niagara-emitter","relation":"related","strength":0.6,"description":"打击感音效与粒子特效的协同"},
    {"source_domain":"game-audio-sfx","source_id":"sfx-sdt-layering","target_domain":"vfx","target_id":"vfx-particle-overview","relation":"related","strength":0.5,"description":"音效分层与粒子特效的同步设计"},

    # game-audio-sfx ↔ game-design
    {"source_domain":"game-audio-sfx","source_id":"sfx-sdt-feedback-loop","target_domain":"game-design","target_id":"feedback-intro","relation":"related","strength":0.7,"description":"音频反馈是游戏反馈系统的核心组成"},
    {"source_domain":"game-audio-sfx","source_id":"sfx-sdt-ui-sound","target_domain":"game-design","target_id":"juice-design","relation":"related","strength":0.6,"description":"UI音效是游戏手感(Juice)的关键元素"},

    # game-audio-sfx ↔ game-ui-ux
    {"source_domain":"game-audio-sfx","source_id":"sfx-sdt-ui-sound","target_domain":"game-ui-ux","target_id":"guiux-feedback-overview","relation":"related","strength":0.7,"description":"UI音效与交互反馈的配合"},

    # game-audio-sfx ↔ narrative-design
    {"source_domain":"game-audio-sfx","source_id":"sfx-sdt-sound-storytelling","target_domain":"narrative-design","target_id":"nd-es-prop-storytelling","relation":"related","strength":0.7,"description":"声音叙事与道具叙事的互补"},
    {"source_domain":"game-audio-sfx","source_id":"sfx-dp-interactive-dialogue","target_domain":"narrative-design","target_id":"nd-ds-dialogue-tree","relation":"related","strength":0.6,"description":"交互式对白与对话树系统的集成"},

    # game-audio-sfx ↔ technical-art
    {"source_domain":"game-audio-sfx","source_id":"sfx-am-plugin-development","target_domain":"technical-art","target_id":"ta-ue-python","relation":"related","strength":0.5,"description":"音频插件开发与UE Python脚本"},

    # game-audio-sfx ↔ level-design
    {"source_domain":"game-audio-sfx","source_id":"sfx-as-zone-based","target_domain":"level-design","target_id":"spatial-hierarchy","relation":"related","strength":0.6,"description":"区域音效与关卡空间层级的对应"},

    # game-audio-sfx ↔ multiplayer-network
    {"source_domain":"game-audio-sfx","source_id":"sfx-dp-voice-recording","target_domain":"multiplayer-network","target_id":"mn-lb-voice-chat","relation":"related","strength":0.5,"description":"语音录制技术与多人语音聊天"},

    # game-audio-sfx ↔ software-engineering
    {"source_domain":"game-audio-sfx","source_id":"sfx-am-source-control","target_domain":"software-engineering","target_id":"se-git-basics","relation":"related","strength":0.5,"description":"音频项目的版本控制实践"},
    {"source_domain":"game-audio-sfx","source_id":"sfx-ao-regression-testing","target_domain":"software-engineering","target_id":"se-unit-test","relation":"related","strength":0.5,"description":"音效回归测试与单元测试方法论"},

    # game-audio-sfx ↔ psychology
    {"source_domain":"game-audio-sfx","source_id":"sfx-sdt-psychoacoustics","target_domain":"psychology","target_id":"perception","relation":"related","strength":0.6,"description":"声音心理学与知觉心理学的交叉"},
    {"source_domain":"game-audio-sfx","source_id":"sfx-sdt-emotional-design","target_domain":"psychology","target_id":"emotional-intelligence","relation":"related","strength":0.6,"description":"声音情感设计与情绪智力"},

    # game-audio-sfx ↔ physics
    {"source_domain":"game-audio-sfx","source_id":"sfx-sa-sound-propagation","target_domain":"physics","target_id":"sound-waves","relation":"related","strength":0.6,"description":"声波传播物理特性"},
]

d["links"].extend(new_links)
d["meta"]["total"] = len(d["links"])
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"Fixed: {len(new_links)} links added. Total: {len(d['links'])}")
