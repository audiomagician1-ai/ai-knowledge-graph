#!/usr/bin/env python3
"""Fix broken cross-sphere links for game-qa domain with exact correct IDs."""
import json, glob, os

# Load all concept IDs per domain
domain_concepts = {}
for f in glob.glob('data/seed/*/seed_graph.json'):
    with open(f, 'r', encoding='utf-8') as fh:
        d = json.load(fh)
        domain = d.get('domain', os.path.basename(os.path.dirname(f)))
        if isinstance(domain, dict):
            domain = domain.get('id', os.path.basename(os.path.dirname(f)))
        domain_concepts[domain] = {c['id'] for c in d.get('concepts', [])}

# Remove all game-qa links first
with open('data/seed/cross_sphere_links.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
data['links'] = [l for l in data['links'] if l.get('source_domain') != 'game-qa']

# Exact correct links with verified IDs
new_links = [
    {"source_domain": "game-qa", "source_id": "qa-ft-gameplay-testing", "target_domain": "game-design", "target_id": "core-loop-intro", "relation": "related", "strength": 0.8, "description": "玩法测试直接验证核心循环设计是否符合预期"},
    {"source_domain": "game-qa", "source_id": "qa-ft-economy-testing", "target_domain": "game-design", "target_id": "game-economy-intro", "relation": "related", "strength": 0.8, "description": "经济系统测试验证游戏经济设计的数值平衡"},
    {"source_domain": "game-qa", "source_id": "qa-pt-cpu-profiling", "target_domain": "game-engine", "target_id": "unity-profiler", "relation": "related", "strength": 0.8, "description": "CPU Profiling使用引擎内置Profiler进行性能分析"},
    {"source_domain": "game-qa", "source_id": "qa-pt-gpu-profiling", "target_domain": "game-engine", "target_id": "asset-profiling", "relation": "related", "strength": 0.7, "description": "GPU Profiling依赖引擎资源性能分析工具"},
    {"source_domain": "game-qa", "source_id": "qa-at-unit-testing", "target_domain": "software-engineering", "target_id": "se-tdd-intro", "relation": "related", "strength": 0.8, "description": "游戏单元测试基于TDD理论和测试框架"},
    {"source_domain": "game-qa", "source_id": "qa-at-ci-integration", "target_domain": "software-engineering", "target_id": "se-game-ci", "relation": "related", "strength": 0.9, "description": "QA自动化的CI集成直接依赖游戏CI/CD管线"},
    {"source_domain": "game-qa", "source_id": "qa-at-tdd-bdd", "target_domain": "software-engineering", "target_id": "se-tdd-intro", "relation": "related", "strength": 0.9, "description": "TDD/BDD实践源自软件工程方法论"},
    {"source_domain": "game-qa", "source_id": "qa-ft-ui-testing", "target_domain": "game-ui-ux", "target_id": "guiux-usability-overview", "relation": "related", "strength": 0.8, "description": "UI功能测试与可用性测试相辅相成"},
    {"source_domain": "game-qa", "source_id": "qa-ct-resolution-aspect", "target_domain": "game-ui-ux", "target_id": "guiux-platform-adaptive-layout", "relation": "related", "strength": 0.7, "description": "分辨率测试验证多平台UI自适应布局的效果"},
    {"source_domain": "game-qa", "source_id": "qa-ft-multiplayer-testing", "target_domain": "multiplayer-network", "target_id": "mn-na-client-server", "relation": "related", "strength": 0.8, "description": "多人游戏测试需要理解客户端-服务器架构"},
    {"source_domain": "game-qa", "source_id": "qa-pt-network-perf", "target_domain": "multiplayer-network", "target_id": "mn-ss-lag-compensation", "relation": "related", "strength": 0.7, "description": "网络性能测试需评估延迟补偿机制的有效性"},
    {"source_domain": "game-qa", "source_id": "qa-rt-dlc-regression", "target_domain": "game-live-ops", "target_id": "ops-uc-major-update", "relation": "related", "strength": 0.7, "description": "DLC回归测试配合运营大版本更新节奏"},
    {"source_domain": "game-qa", "source_id": "qa-bl-post-release-bugs", "target_domain": "game-live-ops", "target_id": "ops-uc-hotfix-process", "relation": "related", "strength": 0.8, "description": "上线后Bug处理流程直接关联运营热修复机制"},
    {"source_domain": "game-qa", "source_id": "qa-ft-compliance-testing", "target_domain": "game-publishing", "target_id": "pub-rc-esrb-basics", "relation": "related", "strength": 0.8, "description": "合规性测试验证游戏是否符合ESRB分级标准"},
    {"source_domain": "game-qa", "source_id": "qa-ct-console-cert", "target_domain": "game-publishing", "target_id": "pub-ro-legal-compliance", "relation": "related", "strength": 0.7, "description": "主机认证兼容测试关联法律合规要求"},
    {"source_domain": "game-qa", "source_id": "qa-ft-audio-testing", "target_domain": "game-audio-sfx", "target_id": "sfx-am-game-integration", "relation": "related", "strength": 0.7, "description": "音频功能测试验证音效中间件在游戏中的集成效果"},
    {"source_domain": "game-qa", "source_id": "qa-pt-render-pipeline", "target_domain": "technical-art", "target_id": "ta-shader-optimization", "relation": "related", "strength": 0.7, "description": "渲染管线性能分析与Shader优化直接相关"},
    {"source_domain": "game-qa", "source_id": "qa-pt-gpu-profiling", "target_domain": "computer-graphics", "target_id": "cg-deferred-rendering", "relation": "related", "strength": 0.6, "description": "GPU Profiling需要理解延迟渲染管线的性能特征"},
    {"source_domain": "game-qa", "source_id": "qa-lt-audio-loc", "target_domain": "game-audio-music", "target_id": "game-audio-music-theory-overview", "relation": "related", "strength": 0.5, "description": "音频本地化测试涉及配音替换与音乐适配验证"},
    {"source_domain": "game-qa", "source_id": "qa-lt-linguistic-qa", "target_domain": "narrative-design", "target_id": "nd-lo-pseudolocalization", "relation": "related", "strength": 0.8, "description": "语言质量测试与伪本地化技术紧密关联"},
    {"source_domain": "game-qa", "source_id": "qa-ft-tutorial-testing", "target_domain": "level-design", "target_id": "mechanic-introduction", "relation": "related", "strength": 0.7, "description": "新手引导测试验证关卡中的机制介绍流程"},
    {"source_domain": "game-qa", "source_id": "qa-at-visual-testing", "target_domain": "animation", "target_id": "anim-principles-overview", "relation": "related", "strength": 0.5, "description": "视觉回归测试可检测动画异常导致的视觉缺陷"},
    {"source_domain": "game-qa", "source_id": "qa-pt-scalability", "target_domain": "vfx", "target_id": "vfx-fb-optimization", "relation": "related", "strength": 0.6, "description": "可扩展性测试验证不同画质下特效的性能缩放表现"},
    {"source_domain": "game-qa", "source_id": "qa-lt-cultural-adapt", "target_domain": "concept-design", "target_id": "cd-style-intro", "relation": "related", "strength": 0.5, "description": "文化适配测试参考视觉风格指南确保文化一致性"},
]

# Validate all target IDs exist
for link in new_links:
    td = link['target_domain']
    tid = link['target_id']
    if td in domain_concepts and tid not in domain_concepts[td]:
        print(f"STILL BROKEN: {link['source_id']} -> {td}/{tid}")

data['links'].extend(new_links)

with open('data/seed/cross_sphere_links.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Replaced all game-qa links. Total: {len(data['links'])}")


