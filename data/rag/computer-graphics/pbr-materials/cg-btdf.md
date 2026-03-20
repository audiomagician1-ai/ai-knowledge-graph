---
concept: 透射BRDF
subdomain: PBR材质
domain: computer-graphics
difficulty: 4
---

# 透射BRDF

## 核心内容

BTDF与BSDF统一框架、微表面折射模型

## 关键要点

### 数学基础
- 理解透射BRDF背后的数学原理（线性代数/微积分/概率论等）
- 掌握从数学公式到GPU实现的转化思路
- 了解数值精度和性能之间的权衡

### 渲染技术
- 透射BRDF在实时渲染管线中的位置与作用
- 相关Shader实现要点与优化技巧
- 在游戏引擎(UE5/Unity)中的实际应用案例

## 常见误区

1. **忽视硬件限制**: 脱离GPU架构特性设计算法，导致性能瓶颈
2. **过度追求物理正确**: 在实时渲染中不加取舍地使用离线渲染算法
3. **孤立学习**: 不理解透射BRDF与渲染管线其他环节的协同关系

## 学习建议

- 使用ShaderToy或RenderDoc等工具动手实验透射BRDF效果
- 阅读GPU Gems/Real-Time Rendering等经典参考资料
- 在游戏引擎中观察和修改透射BRDF的实际实现
