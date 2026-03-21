---
id: "perf-regression"
concept: "性能回归检测"
domain: "game-engine"
subdomain: "performance-profiling"
subdomain_name: "性能剖析"
difficulty: 3
is_milestone: false
tags: ["CI"]

# Quality Metadata (Schema v2)
content_version: 1
quality_tier: "C"
quality_score: 22.0
generation_method: "template-v1"
unique_content_ratio: 0.455
last_scored: "2026-03-21"
sources: []
---
# 性能回归检测

## 核心内容

CI性能基线/自动报警/Blame

## 关键要点

### 基本原理
- 理解性能回归检测的核心定义与在游戏引擎中的作用
- 掌握其与其他引擎子系统的关联关系
- 了解UE5和Unity中的具体实现差异与设计取舍

### 工程实践
- 性能影响：了解性能回归检测的CPU/GPU/内存开销及优化策略
- 调试方法：掌握引擎Profiler和调试工具的使用
- 版本兼容：注意不同引擎版本中的API变化

## 常见误区

1. **只会调API不懂原理**: 仅停留在蓝图/编辑器层面，不理解底层算法与数据结构
2. **忽视性能代价**: 添加功能时不评估帧时间影响，导致运行时性能问题
3. **孤立看待子系统**: 不考虑与其他子系统的数据流和依赖关系

## 学习建议

- 在引擎中动手实践性能回归检测的核心功能并用Profiler验证性能影响
- 对比UE5和Unity对性能回归检测的不同实现，理解设计取舍
- 阅读引擎源码或官方文档，深入理解性能回归检测的底层机制
