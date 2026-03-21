---
id: "cg-taa-ghosting"
concept: "TAA鬼影"
domain: "computer-graphics"
subdomain: "anti-aliasing"
subdomain_name: "抗锯齿"
difficulty: 3
is_milestone: false
tags: ["问题"]

# Quality Metadata (Schema v2)
content_version: 1
quality_tier: "C"
quality_score: 30.6
generation_method: "template-v1"
unique_content_ratio: 0.6
last_scored: "2026-03-21"
sources: []
---
# TAA鬼影

## 核心内容

Ghosting的成因——遮挡/去遮挡与对策

## 关键要点

### 数学基础
- 理解TAA鬼影背后的数学原理（线性代数/微积分/概率论等）
- 掌握从数学公式到GPU实现的转化思路
- 了解数值精度和性能之间的权衡

### 渲染技术
- TAA鬼影在实时渲染管线中的位置与作用
- 相关Shader实现要点与优化技巧
- 在游戏引擎(UE5/Unity)中的实际应用案例

## 常见误区

1. **忽视硬件限制**: 脱离GPU架构特性设计算法，导致性能瓶颈
2. **过度追求物理正确**: 在实时渲染中不加取舍地使用离线渲染算法
3. **孤立学习**: 不理解TAA鬼影与渲染管线其他环节的协同关系

## 学习建议

- 使用ShaderToy或RenderDoc等工具动手实验TAA鬼影效果
- 阅读GPU Gems/Real-Time Rendering等经典参考资料
- 在游戏引擎中观察和修改TAA鬼影的实际实现
