---
id: "vfx-vfxgraph-context"
concept: "Context系统"
domain: "vfx"
subdomain: "vfx-graph"
subdomain_name: "VFX Graph"
difficulty: 2
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# Context系统

## 概述

VFX Graph中的Context系统是粒子生命周期管理的骨架结构。每个粒子效果都必须且只能通过三种固定类型的Context来组织其逻辑：**Initialize Context**（初始化）、**Update Context**（更新）和**Output Context**（输出）。这三者在编辑器中以深色矩形卡片的形式呈现，可以通过右键菜单或空格键弹出的节点创建面板添加到图表中。

Context系统的设计来自Unity在2018年引入VFX Graph时对GPU粒子管线的根本性重构。传统粒子系统（如Shuriken）在CPU上逐粒子运算，而VFX Graph将逻辑编译为HLSL着色器并在GPU上并行执行——Context正是这套编译单元的分界点，每个Context对应一段独立的GPU计算通道（Compute Pass）或渲染通道（Render Pass）。

理解Context系统的实际意义在于：Block节点只能挂载在兼容的Context内部，不同Context内的数据不能随意共享，因此选错Context会导致效果逻辑失效甚至编译报错。掌握三种Context的职责边界，是在VFX Graph中写出任何有效粒子行为的前提。

## 核心原理

### Initialize Context：粒子诞生的一次性写入

Initialize Context在每个粒子**刚被生成的那一帧**执行，且在该粒子的完整生命周期内只执行一次。它的典型工作是为粒子的属性分配初始值，例如设置起始位置、初速度、随机颜色或初始生命周期（Lifetime）。

Initialize Context依赖上方连接的**Spawn Context**提供粒子生成信号——Spawn Context控制每秒生成粒子的数量（Rate）或爆发数量（Burst），而Initialize Context接收这批新粒子并写入其初始状态。需要注意的是，Initialize Context**不能读取粒子当前属性然后修改**，因为粒子属性在此刻刚被分配内存，读取未写入的值是无意义的。

### Update Context：粒子存活期间的逐帧运算

Update Context在粒子存活的**每一帧**都执行，是实现粒子运动、物理模拟和属性随时间变化的核心场所。例如，"Turbulence"Block（湍流）、"Conform to Signed Distance Field"Block（SDF约束）等依赖逐帧积分的操作都必须放在Update Context中。

Update Context隐含一个时间变量 `deltaTime`，大量物理Block内部使用公式 `velocity += force × deltaTime` 进行欧拉积分。Update Context还负责递减粒子的剩余寿命（`age += deltaTime`），当 `age ≥ lifetime` 时粒子被标记为死亡并在下一帧回收到缓冲池。如果一个VFX Graph中没有Update Context，粒子将在生成后静止在初始位置，直到寿命耗尽。

### Output Context：粒子的视觉呈现定义

Output Context不执行物理逻辑，而是定义粒子**如何被渲染**。VFX Graph提供多种Output Context类型，包括：
- **Output Particle Quad**：最常用，将粒子渲染为朝向摄像机的四边形面片
- **Output Particle Mesh**：为每个粒子实例化一个3D网格
- **Output Particle HDRP Lit**：支持HDRP光照模型的粒子输出
- **Output Particle Point**：以GPU点云形式输出

Output Context内可以设置混合模式（Blend Mode，如Alpha Blend或Additive）、指定材质纹理，以及通过Block修改粒子在屏幕上的最终颜色和大小。一个系统中可以存在**多个Output Context**并行工作，这使得单一粒子系统同时输出面片和网格成为可能。

### Context之间的连接规则

三种Context通过垂直的**Flow连接线**按照固定顺序链接：Spawn → Initialize → Update → Output。这条连接线传递的不是数据值，而是粒子系统的"控制流"信号。如果Initialize和Update之间没有Flow连线，Update Context将不会处理从该Initialize Context创建的粒子。一个VFX Asset内可以存在多条独立的Context链，每条链管理一类独立的粒子群（System）。

## 实际应用

**制作爆炸效果的典型Context配置：**
在Initialize Context中，使用"Set Velocity Random"Block将初速度设为方向随机、大小在5到20单位之间的向量，同时用"Set Lifetime Random"Block设置1.5秒到3秒的随机生命周期。在Update Context中，添加"Gravity"Block施加向下的重力加速度（默认 -9.81 m/s²），再添加"Turbulence"Block增加飘散感。在Output Particle Quad Context中，设置Blend Mode为Additive使粒子叠加发光，并连接一张烟雾Flipbook纹理，通过"Flipbook Player"Block实现帧动画。

**多Output Context并联：** 制作带火花的燃烧效果时，可以将同一个Initialize → Update链同时连接到两个Output Context——一个Output Particle Quad输出软体火焰面片，另一个Output Particle Mesh输出小石子网格，两者共享同一套运动逻辑，只是视觉表现不同。

## 常见误区

**误区一：把逐帧变化的逻辑放进Initialize Context**
一个常见错误是将"Scale over Lifetime"（随生命周期缩放）这类Block放入Initialize Context。由于Initialize只执行一次，该Block只会在粒子诞生时读取一个固定比例，不会产生任何动画效果。正确做法是将此类Block放入Update Context，它才会在每帧重新计算当前缩放值。

**误区二：认为可以跨Context直接传递粒子属性**
Context之间不能通过连线直接传递粒子级别的属性（per-particle attribute）。如果需要在Output Context中使用一个在Update Context中计算出的中间值，必须先将其写入粒子的某个属性槽（如Custom Attribute），再在Output Context中读取该属性。直接在两个Context之间拖连线传递粒子数据是不被支持的。

**误区三：混淆System数量与Context数量**
VFX Graph中一个"System"指的是一条完整的Spawn→Initialize→Update→Output链。一个VFX Asset内添加了3个Initialize Context并不意味着有3个System——只有当每个Initialize Context都有自己独立的Spawn Context和Output Context相连时，才构成3个独立System。孤立的Context不会被编译进运行时逻辑。

## 知识关联

学习Context系统需要先了解**VFX Graph概述**中介绍的GPU粒子管线概念，特别是"粒子缓冲区"和"Compute Shader"的基本工作方式，这样才能理解为何Initialize只执行一次而Update逐帧执行的设计是由底层GPU计算通道决定的，而非任意设定。

掌握Context系统之后，下一步是学习**Block与节点**——Block是嵌套在Context内部的功能单元，每个Block对应一段具体的粒子行为逻辑（如受力、碰撞或颜色变化）。了解哪些Block只能挂载在Initialize Context、哪些只能挂载在Update Context、哪些在两者中都可用，是深入使用VFX Graph构建复杂特效的关键技能。