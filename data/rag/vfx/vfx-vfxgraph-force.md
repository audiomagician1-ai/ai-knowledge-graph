---
id: "vfx-vfxgraph-force"
concept: "力与运动"
domain: "vfx"
subdomain: "vfx-graph"
subdomain_name: "VFX Graph"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 49.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.438
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 力与运动

## 概述

在 Unity VFX Graph 中，"力与运动"描述的是通过各类力场节点对粒子速度向量进行逐帧修改，从而产生物理感运动的机制。与传统粒子系统（Shuriken）依赖曲线编辑器的方式不同，VFX Graph 将力的计算下放到 GPU，每帧在 Update Context 中对每颗粒子独立执行向量运算，支持数百万粒子同时接受力的影响而不产生 CPU 瓶颈。

该机制的理论基础来自牛顿第二定律的离散化形式：在每个时间步 Δt 内，粒子速度的变化量等于合力除以质量（Δv = F/m × Δt），位置随之更新（Δx = v × Δt）。VFX Graph 通过内置的 **Integrate Forces** 与 **Update Position** 隐式流程，或手动连接 **Force** Block 节点，将上述积分过程显式地暴露给美术人员。

掌握力与运动对 VFX 工作流的重要性在于：绝大多数真实感特效（火焰上升、爆炸冲击波、烟雾飘散）都需要力的组合叠加，而不是简单的速度预设。理解各力节点的参数范围与叠加顺序，可以避免粒子出现不稳定震荡（数值积分发散），这是初学者最常踩的坑。

---

## 核心原理

### 1. Force Block：线性力的施加

**Force** Block 位于 VFX Graph 的 Update Context 中，向每颗粒子施加一个固定的世界空间或局部空间向量力。其参数 `Force (Vector3)` 直接累加到粒子的加速度缓冲区。典型用法是模拟重力：将 Y 分量设为 `-9.81` 即可获得标准地球重力加速度（单位 m/s²）。

需要注意的是，Force Block 默认假设粒子质量为 1 kg。若要模拟不同密度的粒子（如烟雾 vs. 火星），可在 Initialize Context 中为属性系统中的自定义 `Mass` 属性赋值，然后在 Update Context 中用 **Divide** 节点将力除以质量后再接入 Force Block，实现质量感差异。

### 2. Turbulence Block：湍流场驱动的随机运动

**Turbulence** Block 使用三维 Curl Noise（旋度噪声）生成无散度的速度场，确保粒子不会异常聚集或发散。其核心参数包括：

- `Intensity`：湍流速度强度，建议范围 0.1–5.0，超过 10 容易导致粒子跳出可见范围
- `Frequency`：噪声空间频率，值越高湍流细节越密集
- `Speed`：噪声场随时间滚动的速率，模拟风向变化
- `Octaves`（1–8）：叠加的噪声层数，每增加一层细节翻倍但 GPU 开销约增加 30%

Curl Noise 的数学本质是对标量噪声场 φ 取旋度（∇ × ∇φ），得到的向量场天然满足 ∇·v = 0（无散度条件），因此非常适合模拟烟雾、蒸汽等不可压缩流体的湍流效果。

### 3. Noise 节点族：自定义噪声驱动

除 Turbulence Block 外，VFX Graph 提供独立的噪声采样节点用于更细粒度的控制：

- **Sample Perlin Noise 3D**：输出 -1 到 1 的连续标量，适合调制粒子颜色或大小
- **Sample Cellular Noise**：生成泡沫状图案，适合模拟熔岩表面粒子分布
- **Sample Gradient Noise**：平滑过渡，适合宏观风场模拟

这些节点的输出可以直接乘以方向向量后接入 Force Block，实现噪声调制的定向力。例如，将 Perlin Noise 输出乘以 `(1, 0, 0)` 向量，即可制作左右随机漂移但不影响竖直方向的侧风效果。

### 4. 力的叠加顺序与数值稳定性

VFX Graph 的 Update Context 按 Block 从上到下顺序执行。多个 Force Block 的加速度在同一帧内累加，最终统一积分一次位置。这意味着力的排列顺序不影响当帧的结果，但若 Drag（阻力）Block 放置在 Force Block 之前，则阻力先于当帧新增力作用，会导致模拟结果与预期略有偏差。

数值稳定性的关键参数是 `Δt`（帧时间）。当帧率低于 20 FPS 时，Δt > 0.05s，Force × Δt 的乘积可能使速度在单帧内超过安全阈值，导致粒子瞬间飞出场景。解决方案是在 Update Context 中添加 **Clamp Velocity** Block，将速度上限限制在合理范围（如 50 m/s）。

---

## 实际应用

**爆炸冲击波粒子**：在 Initialize Context 中，通过 **Set Velocity from Direction & Speed** Block 将粒子速度初始化为径向向外（速度 20–80 m/s）。在 Update Context 中，依次叠加重力 Force Block（Y=-9.81）、Turbulence Block（Intensity=1.5, Frequency=0.3）以及 Drag Block（系数 0.85），产生粒子先快速扩散、中段受湍流扰动、后期因阻力减速坠落的三段式运动曲线。

**烟雾上升效果**：创建一个负值 Y 方向的 Drag（系数 0.98 仅作用于 XZ 平面）配合正 Y 方向 Force（+2.0 m/s²，模拟热浮力），再叠加 Turbulence（Intensity=0.8, Octaves=4），即可在不使用任何关键帧动画的前提下生成持续上升并自然扩散的烟柱。

**受风影响的落叶**：利用 **Sample Perlin Noise 3D** 对粒子世界坐标采样，输出值乘以 `(3, 0, 1)` 向量接入 Force Block，同时保留 Y 方向重力 -9.81。每片叶子因坐标不同采样到不同的噪声值，在宏观风力方向一致的前提下产生个体差异，避免所有叶子同步运动的机械感。

---

## 常见误区

**误区一：将 Turbulence 的 Intensity 调得越大越真实**
实际上 Intensity 超过 5.0 后，Curl Noise 产生的速度增量远超重力，粒子会呈现出无规律的高速乱窜，完全失去物理感。真实烟雾和火焰的湍流强度通常在 0.3–2.0 之间，宏观运动方向（浮力或初速度）仍然主导粒子轨迹，湍流只提供次级扰动。

**误区二：在 Initialize Context 中使用 Force Block**
Force Block 设计用于 Update Context（逐帧累加），若错误放入 Initialize Context，它只在粒子出生帧执行一次，效果等同于给粒子施加一个固定初速偏移，而不是持续力。这在 VFX Graph 中不会报错但行为完全不符合预期，调试时极难发现。

**误区三：Drag Block 可以完全替代 Force Block 的减速功能**
Drag Block 实现的是速度按比例衰减（v_new = v × drag_coefficient），这是指数衰减，粒子理论上永远不会停止。若需要粒子在特定距离内硬性停止（如地面弹跳前减速），必须配合 Clamp Velocity 或自定义速度阈值判断，单独使用 Drag 无法实现有限时间内的完全静止。

---

## 知识关联

**前置概念——属性系统**：力与运动中所有参数（速度、质量、自定义阻力系数）都存储在粒子属性缓冲区中。若未在 Initialize Context 的属性系统中声明 `Velocity (Vector3)` 或 `Mass (float)` 属性，Force Block 将找不到写入目标，导致节点报错或静默失效。理解属性的读写时序（Initialize 写入初值，Update 逐帧修改）是正确使用任何 Force 节点的前提。

**后续概念——碰撞与交互**：力驱动粒子到达边界后，需要碰撞系统提供法向反弹力或摩擦力，才能完成完整的物理模拟闭环。碰撞响应本质上是在检测到位置越界时，反向施加一个冲量（Impulse = -2 × (v·n) × n），其计算建立在本节速度向量运算的基础之上。

**后续概念——湍流与噪声**：本节介绍的 Turbulence Block 和 Noise 节点族是湍流与噪声专题的实践入口。进阶内容将涉及自定义噪声贴图（Flipbook Texture 作为向量场）、多层噪声混合的频谱分析，以及如何通过 HLSL Custom HLSL Block 实现 VFX Graph 内置节点不支持的 Simplex Noise 算法。