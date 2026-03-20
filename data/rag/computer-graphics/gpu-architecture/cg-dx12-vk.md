---
concept: DX12/Vulkan基础
subdomain: GPU架构
domain: computer-graphics
difficulty: 3
---

# DX12/Vulkan基础

## 核心内容

现代图形API的命令缓冲/描述符堆/管线状态对象

## 关键要点

### 数学基础
- 理解DX12/Vulkan基础背后的数学原理（线性代数/微积分/概率论等）
- 掌握从数学公式到GPU实现的转化思路
- 了解数值精度和性能之间的权衡

### 渲染技术
- DX12/Vulkan基础在实时渲染管线中的位置与作用
- 相关Shader实现要点与优化技巧
- 在游戏引擎(UE5/Unity)中的实际应用案例

## 常见误区

1. **忽视硬件限制**: 脱离GPU架构特性设计算法，导致性能瓶颈
2. **过度追求物理正确**: 在实时渲染中不加取舍地使用离线渲染算法
3. **孤立学习**: 不理解DX12/Vulkan基础与渲染管线其他环节的协同关系

## 学习建议

- 使用ShaderToy或RenderDoc等工具动手实验DX12/Vulkan基础效果
- 阅读GPU Gems/Real-Time Rendering等经典参考资料
- 在游戏引擎中观察和修改DX12/Vulkan基础的实际实现
