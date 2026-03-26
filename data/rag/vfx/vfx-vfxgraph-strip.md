---
id: "vfx-vfxgraph-strip"
concept: "Strip粒子"
domain: "vfx"
subdomain: "vfx-graph"
subdomain_name: "VFX Graph"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 46.5
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.467
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# Strip粒子

## 概述

Strip粒子（条带粒子）是VFX Graph中一种特殊的粒子输出类型，它将同一粒子系统中按生命周期顺序排列的粒子顶点连接成连续的四边形条带网格，而非独立渲染每个粒子精灵。这种连接机制使得每两个相邻粒子之间自动生成一个四边形面片，从而在视觉上形成平滑的轨迹、拖尾、丝带或闪电等效果。

Strip粒子的概念源自传统粒子系统中的"Trail Renderer"思路，但在VFX Graph中通过GPU实例化重新实现，性能大幅提升。Unity在VFX Graph 7.x版本（对应Unity 2019.3）中正式将`Output ParticleStrip`节点作为稳定功能推出，允许开发者在Shader Graph中访问条带的`stripIndex`和`particleIndexInStrip`等专属属性。

Strip粒子之所以在特效制作中具有独特价值，在于它能够保留粒子的运动历史——普通Quad粒子每帧独立绘制，而Strip粒子会将粒子在空间中走过的路径"物化"为几何体。这使得导弹尾焰、魔法能量束、刀光剑影等需要展现运动轨迹的特效成为可能，且所有运算均在GPU上完成。

## 核心原理

### 条带的拓扑结构与粒子容量（Capacity）

在VFX Graph中创建Strip系统时，必须在`Initialize Strip`上下文中设置`Strip Capacity`（条带容量）和`Particle Per Strip Capacity`（每条带粒子数）两个独立参数，而非普通系统中的单一Capacity值。每条Strip由最少2个粒子节点构成，N个粒子节点会生成`(N-1) × 2`个三角形。条带的宽度由每个粒子的`Size`属性控制，方向垂直于相机视角或由自定义切线向量决定。

### stripIndex与particleIndexInStrip属性

Strip粒子拥有两个专属内置属性：`stripIndex`标识当前粒子所属的条带编号（从0开始计数），`particleIndexInStrip`标识粒子在该条带内的序号位置。这两个属性可在`Output ParticleStrip`的Shader Graph材质中通过`VFXAttribute`节点访问，常用于实现沿条带的渐变效果。例如，将`particleIndexInStrip / (particlePerStripCount - 1)`的归一化值输入Alpha通道，可精确控制条带头部到尾部的透明度渐变，无需任何CPU干预。

### Update Strip上下文与粒子顺序

普通粒子系统的Update上下文可任意修改粒子属性而不影响渲染顺序，但Strip粒子的`Update Strip`上下文中粒子的**索引顺序直接决定条带的连接顺序**。粒子按照出生时间（age从小到大）在条带内排列，最新诞生的粒子位于条带"头部"（`particleIndexInStrip = 0`），最老的粒子在"尾部"。这意味着如果在Initialize阶段将所有粒子同时生成（burst模式），条带将退化为静态丝带形状，而非动态拖尾——必须使用`Constant Rate`或`Variable Rate`逐帧生成才能形成追踪轨迹。

### 纹理UV映射模式

`Output ParticleStrip`节点提供三种UV映射模式：`Stretch`（拉伸模式，纹理均匀铺满整条条带）、`RepeatPerSegment`（每段重复模式，纹理在每两个粒子之间完整重复一次）和`Custom`（自定义模式，由`texIndex`属性控制）。选择`Stretch`时，条带总长度变化会导致纹理随之压缩或拉伸，适合能量束类效果；`RepeatPerSegment`则保持单段纹理比例恒定，适合锁链或绳索效果。

## 实际应用

**刀光拖尾效果**：在`Initialize Strip`中设置Strip Capacity为1（单条带），Particle Per Strip Capacity为32。在`Update Strip`中添加`Age over Lifetime`节点驱动粒子Alpha衰减，并在Shader Graph中将`particleIndexInStrip`归一化值连接到Emission强度，使刀光头部最亮、尾部渐暗。配合`Orient: Along Velocity`朝向模式，条带宽度随速度变化而动态收窄。

**闪电链特效**：利用噪声函数（Perlin Noise）在`Update Strip`中每帧偏移粒子的Position属性，但仅对`particleIndexInStrip`在1到N-2范围内的中间粒子施加扰动（通过Step节点过滤首尾粒子），保持闪电两端锚点固定，中间段随机抖动，形成高频闪烁的放电视觉效果。

**角色运动残影**：将Strip粒子的生成位置绑定到角色骨骼的世界坐标（通过`Position (Skinned Mesh)`采样器），设置粒子生命周期为0.15秒，Constant Rate为60/秒，使残影条带密度与帧率一致，在高速移动时留下清晰的运动轨迹切片。

## 常见误区

**误区一：将Strip系统的Capacity理解为普通粒子总数**
Strip系统的容量由`Strip Capacity × Particle Per Strip Capacity`共同决定，总粒子槽位数等于两者之积。若设置Strip Capacity为10、Particle Per Strip Capacity为20，则系统支持最多10条独立条带，每条带最多20个粒子（共200个粒子槽），而非直接设置200个粒子。混淆这两个参数会导致条带数量超限后新条带无法生成，但不会有报错提示。

**误区二：在Output中修改Position来控制条带形状**
条带的几何形状完全由粒子在`Update Strip`上下文中的Position属性决定，在`Output ParticleStrip`的Shader Graph中修改顶点位置仅影响视觉偏移，不改变条带的物理骨架。很多初学者尝试在Output的Vertex Shader中做扭曲变形，发现条带宽度方向的扭曲正常，但条带走向无法改变，根本原因就在于骨架拓扑已在Update阶段固化。

**误区三：Strip粒子可以与粒子碰撞系统配合使用**
VFX Graph目前（Unity 2022 LTS）的碰撞块（Collide with Depth Buffer / Collide with Sphere等）仅对`Output Particle Quad`类型的标准粒子有效，`Output ParticleStrip`不支持内置碰撞响应。若要实现条带与场景几何体的交互，需通过C# Script读取碰撞信息后以`VFXEventAttribute`形式回传给VFX Graph，手动更新锚点粒子的位置。

## 知识关联

Strip粒子的随机形变效果高度依赖**噪声函数**——在Update Strip上下文中，Curl Noise或Value Noise节点为条带中间节点提供逐粒子的位置扰动，使原本笔直的条带呈现有机的弯曲感。没有对噪声函数采样频率和幅度的理解，Strip的形态控制将缺乏精确性。

Strip粒子系统的预烘焙输出与**Point Cache**工作流紧密相连：通过Point Cache Bake Tool可以将复杂Strip动画的关键帧粒子位置序列烘焙为`.pcache`文件，在运行时直接从缓存中驱动条带形态，彻底绕过实时物理计算，在移动端等性能受限平台上实现高质量拖尾特效。