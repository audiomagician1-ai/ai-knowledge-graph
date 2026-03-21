---
id: "cg-velocity-buffer"
concept: "速度缓冲"
domain: "computer-graphics"
subdomain: "anti-aliasing"
subdomain_name: "抗锯齿"
difficulty: 2
is_milestone: false
tags: ["技术"]

# Quality Metadata (Schema v2)
content_version: 1
quality_tier: "C"
quality_score: 29.0
generation_method: "template-v1"
unique_content_ratio: 0.556
last_scored: "2026-03-21"
sources: []
---
# 速度缓冲

## 核心内容

Per-Pixel Velocity的计算与TAA/Motion Blur共享

## 关键要点

### 数学基础
- 理解速度缓冲背后的数学原理（线性代数/微积分/概率论等）
- 掌握从数学公式到GPU实现的转化思路
- 了解数值精度和性能之间的权衡

### 渲染技术
- 速度缓冲在实时渲染管线中的位置与作用
- 相关Shader实现要点与优化技巧
- 在游戏引擎(UE5/Unity)中的实际应用案例

## 常见误区

1. **忽视硬件限制**: 脱离GPU架构特性设计算法，导致性能瓶颈
2. **过度追求物理正确**: 在实时渲染中不加取舍地使用离线渲染算法
3. **孤立学习**: 不理解速度缓冲与渲染管线其他环节的协同关系

## 学习建议

- 使用ShaderToy或RenderDoc等工具动手实验速度缓冲效果
- 阅读GPU Gems/Real-Time Rendering等经典参考资料
- 在游戏引擎中观察和修改速度缓冲的实际实现
