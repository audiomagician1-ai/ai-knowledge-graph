---
id: "ta-draw-call"
concept: "Draw Call优化"
domain: "technical-art"
subdomain: "perf-optimization"
subdomain_name: "性能优化"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# Draw Call优化

## 概述

Draw Call（绘制调用）是CPU向GPU发出的一条渲染指令，命令GPU使用当前绑定的材质和网格数据绘制一批几何体。每次Draw Call发生时，CPU必须完成状态切换、参数验证、驱动层翻译等一系列工作，在DirectX 11及之前的API中，单次Draw Call的CPU开销约为0.1ms量级，当场景中存在数千个Draw Call时，CPU成为明显的渲染瓶颈。

这一问题在移动端尤为突出。ARM Mali等移动GPU的驱动层比PC更厚重，单次Draw Call的驱动开销是PC的2到5倍。Unity官方文档建议移动端场景将Draw Call控制在100以下，而PC端通常可以承受1000至2000个。Draw Call数量的限制本质上是**CPU提交瓶颈**，与GPU的并行计算能力无关——GPU可能处于空闲状态，而CPU却忙于打包渲染指令。

Draw Call优化的目标是减少CPU向GPU提交的指令数量，核心思路分为三类：**合批（Batching）**将多个物体合并为一次提交，**实例化（Instancing）**复用同一份网格数据多次绘制，**间接渲染（Indirect Rendering）**将指令生成工作转移到GPU端，彻底绕过CPU瓶颈。

## 核心原理

### 静态合批（Static Batching）

静态合批在构建阶段或运行时启动阶段将标记为`Static`的物体网格顶点合并进一张大型顶点缓冲区。Unity的静态合批要求物体共享同一材质，合并后生成一个新的组合Mesh，运行时用单次Draw Call渲染整组物体。其代价是**内存占用翻倍**：原始网格数据和合并后的大Mesh同时驻留在内存中。对于一栋包含500个相同石砖物件的建筑，静态合批可以将500次Draw Call压缩到1次，但需要额外消耗这500个网格总顶点数乘以顶点数据大小的内存。

### 动态合批（Dynamic Batching）

动态合批在每帧运行时由CPU完成，引擎自动将**顶点数低于900个**（Unity中的限制，且顶点属性通道数影响此上限）、共享材质的动态物体网格临时合并。动态合批的CPU合并操作本身有计算成本，当参与合批的物体顶点总数过多时，合批CPU时间可能超过节省的Draw Call时间，反而造成性能下降。因此动态合批适合大量小型粒子、UI元素等场景，而不适合复杂角色模型。

### GPU实例化（GPU Instancing）

GPU实例化通过一次Draw Call传入同一网格的多份变换矩阵（以及其他per-instance数据如颜色），让GPU内部循环绘制N个实例，而非CPU提交N次独立Draw Call。在Shader代码层面，需要使用`UNITY_INSTANCING_BUFFER_START`宏声明实例化属性块，`UNITY_ACCESS_INSTANCED_PROP`宏读取每实例数据。实例化对**相同网格、相同材质但不同Transform**的物体效果最佳，典型场景是草地（数万株草使用同一Mesh）或士兵群体。OpenGL ES 3.0及以上、Metal、Vulkan、DirectX 11及以上均支持此特性。

### 间接渲染（Indirect Rendering）

间接渲染使用`DrawMeshInstancedIndirect`（Unity）或Vulkan的`vkCmdDrawIndirect`等API，将绘制参数（实例数量、索引偏移等）存储在GPU端的Buffer中，由Compute Shader在GPU上动态决定绘制什么、绘制多少个，CPU只需调用一次间接绘制指令。这完全消除了CPU逐物体遍历和剔除的开销，GPU Driven Pipeline即基于此思路，在《最后生还者 Part II》（2020年）等项目中，数万个植被实例通过间接渲染在GPU端完成剔除和提交，CPU帧时间节省超过30%。

## 实际应用

**城市场景道路标线**：数百个箭头标线Mesh完全相同，仅位置和旋转不同，启用GPU实例化后从400次Draw Call降至1次，且每实例颜色（白线/黄线）通过实例化Buffer传入Shader，无需多材质切换。

**UI系统图集合批**：将所有HUD图标打包进同一张Texture Atlas（图集），确保同一Canvas层级下的图标元素共享一个材质，Unity的UI Canvas会自动将它们合并为单次Draw Call。图集生成工具（如TexturePacker）将不同图标打包时需设置相同的压缩格式（如ASTC 4x4），否则材质不同导致合批失败。

**地形植被**：使用`DrawMeshInstancedIndirect`配合Compute Shader，在GPU端执行视锥剔除（Frustum Culling）和遮挡剔除（Hi-Z Occlusion Culling），只将可见实例的矩阵写入Instance Buffer，再触发间接绘制。此方案在地形含10万棵树的场景中，CPU植被渲染帧时间可从8ms降至0.3ms以下。

## 常见误区

**误区一：合批一定能提升性能。** 动态合批的CPU合并操作有实际成本。若每帧合批对象频繁变化（如物体不停加入/离开合批组），CPU需要每帧重建合并Buffer，当顶点数超过阈值时合批反而更慢。正确做法是通过Unity的Frame Debugger确认合批确实生效，并用Profiler对比合批前后的CPU帧时间，而不是默认开启了合批就等于优化了性能。

**误区二：减少Draw Call数等于减少渲染时间。** Draw Call优化解决的是**CPU提交瓶颈**，若场景的瓶颈在GPU（如过度绘制、复杂Shader的ALU压力），减少Draw Call对帧率几乎没有帮助。需要先用RenderDoc或Xcode GPU Frame Capture区分CPU Bound还是GPU Bound，再决定是否应优先做Draw Call优化。

**误区三：GPU实例化与静态合批可以叠加使用。** 被标记为Static并已参与静态合批的物体，其网格已合并为组合Mesh，Unity无法再对其应用GPU实例化。两者是互斥的优化路径，静态合批适合不同网格混合的静态场景，GPU实例化适合大量重复使用同一网格的动态对象。

## 知识关联

学习Draw Call优化需要先了解**渲染管线概述**中CPU与GPU的分工模型，以及**材质与Shader基础**中材质实例（Material Instance）如何影响合批条件——两个物体即便使用同一Shader，若材质属性不同（非实例化情况下），也无法合批。

Draw Call优化是进入**GPU实例化**深度学习的直接前置，GPU实例化章节将展开Instancing Buffer的内存布局、per-instance数据的Shader编写规范以及SRP Batcher与传统实例化的区别。**网格合并**章节则从资产制作角度讨论如何在建模阶段预合并网格以辅助静态合批，并分析合并网格与LOD（细节层次）系统的协同策略。