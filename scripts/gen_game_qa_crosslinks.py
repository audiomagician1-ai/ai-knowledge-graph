#!/usr/bin/env python3
"""Add cross-sphere links for game-qa domain."""
import json, os

LINKS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "seed", "cross_sphere_links.json")

with open(LINKS_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

new_links = [
    # game-qa → game-design (testing game mechanics)
    {"source_domain": "game-qa", "source_id": "qa-ft-gameplay-testing", "target_domain": "game-design", "target_id": "core-loop", "relation": "related", "strength": 0.8, "description": "玩法测试直接验证核心循环设计是否符合预期"},
    {"source_domain": "game-qa", "source_id": "qa-ft-economy-testing", "target_domain": "game-design", "target_id": "game-economy-intro", "relation": "related", "strength": 0.8, "description": "经济系统测试验证游戏经济设计的数值平衡"},
    # game-qa → game-engine (testing engine features)
    {"source_domain": "game-qa", "source_id": "qa-pt-cpu-profiling", "target_domain": "game-engine", "target_id": "ue5-profiling-tools", "relation": "related", "strength": 0.8, "description": "CPU Profiling直接使用引擎内置性能分析工具"},
    {"source_domain": "game-qa", "source_id": "qa-pt-gpu-profiling", "target_domain": "game-engine", "target_id": "ue5-profiling-tools", "relation": "related", "strength": 0.8, "description": "GPU Profiling依赖引擎渲染调试和分析工具"},
    # game-qa → software-engineering (testing methodology)
    {"source_domain": "game-qa", "source_id": "qa-at-unit-testing", "target_domain": "software-engineering", "target_id": "se-unit-testing", "relation": "related", "strength": 0.9, "description": "游戏单元测试基于软件工程的单元测试理论和框架"},
    {"source_domain": "game-qa", "source_id": "qa-at-ci-integration", "target_domain": "software-engineering", "target_id": "se-game-ci", "relation": "related", "strength": 0.9, "description": "QA自动化的CI集成直接依赖游戏CI/CD管线"},
    {"source_domain": "game-qa", "source_id": "qa-at-tdd-bdd", "target_domain": "software-engineering", "target_id": "se-tdd-in-games", "relation": "related", "strength": 0.9, "description": "TDD/BDD实践源自软件工程方法论在游戏中的应用"},
    # game-qa → game-ui-ux (UI testing)
    {"source_domain": "game-qa", "source_id": "qa-ft-ui-testing", "target_domain": "game-ui-ux", "target_id": "guiux-usability-testing", "relation": "related", "strength": 0.8, "description": "UI功能测试与可用性测试相辅相成"},
    {"source_domain": "game-qa", "source_id": "qa-ct-resolution-aspect", "target_domain": "game-ui-ux", "target_id": "guiux-multi-platform-ui", "relation": "related", "strength": 0.7, "description": "分辨率测试验证多平台UI适配的实际效果"},
    # game-qa → multiplayer-network (network testing)
    {"source_domain": "game-qa", "source_id": "qa-ft-multiplayer-testing", "target_domain": "multiplayer-network", "target_id": "mn-na-network-models", "relation": "related", "strength": 0.8, "description": "多人游戏测试需要理解网络架构模型和同步机制"},
    {"source_domain": "game-qa", "source_id": "qa-pt-network-perf", "target_domain": "multiplayer-network", "target_id": "mn-ss-latency-compensation", "relation": "related", "strength": 0.7, "description": "网络性能测试需评估延迟补偿机制的有效性"},
    # game-qa → game-live-ops (live service testing)
    {"source_domain": "game-qa", "source_id": "qa-rt-dlc-regression", "target_domain": "game-live-ops", "target_id": "ops-uc-major-update", "relation": "related", "strength": 0.7, "description": "DLC回归测试配合运营大版本更新节奏"},
    {"source_domain": "game-qa", "source_id": "qa-bl-post-release-bugs", "target_domain": "game-live-ops", "target_id": "ops-uc-hotfix-process", "relation": "related", "strength": 0.8, "description": "上线后Bug处理流程直接关联运营热修复机制"},
    # game-qa → game-publishing (certification testing)
    {"source_domain": "game-qa", "source_id": "qa-ft-compliance-testing", "target_domain": "game-publishing", "target_id": "pub-platform-trc", "relation": "related", "strength": 0.9, "description": "合规性测试直接对应平台TRC/Lotcheck认证要求"},
    {"source_domain": "game-qa", "source_id": "qa-ct-console-cert", "target_domain": "game-publishing", "target_id": "pub-platform-trc", "relation": "related", "strength": 0.9, "description": "主机认证兼容测试是平台提审的必要条件"},
    # game-qa → game-audio-sfx (audio testing)
    {"source_domain": "game-qa", "source_id": "qa-ft-audio-testing", "target_domain": "game-audio-sfx", "target_id": "sfx-am-game-integration", "relation": "related", "strength": 0.7, "description": "音频功能测试验证音效中间件在游戏中的集成效果"},
    # game-qa → technical-art (performance validation)
    {"source_domain": "game-qa", "source_id": "qa-pt-render-pipeline", "target_domain": "technical-art", "target_id": "ta-perf-profiling", "relation": "related", "strength": 0.8, "description": "渲染管线分析与技术美术的性能优化直接相关"},
    # game-qa → computer-graphics (rendering test)
    {"source_domain": "game-qa", "source_id": "qa-pt-gpu-profiling", "target_domain": "computer-graphics", "target_id": "cg-rp-forward-vs-deferred", "relation": "related", "strength": 0.6, "description": "GPU Profiling需要理解渲染管线(前向/延迟)的性能特征"},
    # game-qa → game-audio-music (localization audio)
    {"source_domain": "game-qa", "source_id": "qa-lt-audio-loc", "target_domain": "game-audio-music", "target_id": "game-audio-music-composition-overview", "relation": "related", "strength": 0.5, "description": "音频本地化测试涉及配音替换与音乐适配验证"},
    # game-qa → narrative-design (localization story)
    {"source_domain": "game-qa", "source_id": "qa-lt-linguistic-qa", "target_domain": "narrative-design", "target_id": "nd-loc-overview", "relation": "related", "strength": 0.8, "description": "语言质量测试验证叙事内容的翻译准确性和语境适切性"},
    # game-qa → level-design (gameplay flow testing)
    {"source_domain": "game-qa", "source_id": "qa-ft-tutorial-testing", "target_domain": "level-design", "target_id": "ld-onboarding", "relation": "related", "strength": 0.7, "description": "新手引导测试验证关卡设计中的引导流程"},
    # game-qa → animation (visual testing)
    {"source_domain": "game-qa", "source_id": "qa-at-visual-testing", "target_domain": "animation", "target_id": "anim-state-machine", "relation": "related", "strength": 0.5, "description": "视觉回归测试可检测动画状态机异常导致的视觉缺陷"},
    # game-qa → vfx (performance impact)
    {"source_domain": "game-qa", "source_id": "qa-pt-scalability", "target_domain": "vfx", "target_id": "vfx-optimization-overview", "relation": "related", "strength": 0.6, "description": "可扩展性测试验证不同画质下特效性能的缩放表现"},
    # game-qa → concept-design (visual consistency)
    {"source_domain": "game-qa", "source_id": "qa-lt-cultural-adapt", "target_domain": "concept-design", "target_id": "cd-style-guide-overview", "relation": "related", "strength": 0.5, "description": "文化适配测试参考视觉风格指南确保文化一致性"},
]

data["links"].extend(new_links)

with open(LINKS_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Added {len(new_links)} cross-sphere links for game-qa. Total links: {len(data['links'])}")
