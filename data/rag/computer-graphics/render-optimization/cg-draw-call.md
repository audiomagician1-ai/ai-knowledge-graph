---
id: "cg-draw-call"
concept: "Draw Call优化"
domain: "computer-graphics"
subdomain: "render-optimization"
subdomain_name: "渲染优化"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 73.0
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


# Draw Call优化

## 概述

Draw Call（绘制调用）是CPU向GPU提交一次渲染命令的操作，具体对应OpenGL中的`glDrawElements`或`glDrawArrays`，以及Direct3D中的`DrawIndexed`等API调用。每次Draw Call需要CPU打包渲染状态、验证资源绑定并通过驱动层提交命令缓冲区，这一过程在PC平台上大约消耗0.1–0.5毫秒的CPU时间，在移动端可能更高。当场景中Draw Call数量达到数千次时，CPU端的提交开销便成为帧率瓶颈。

历史上，Draw Call瓶颈问题在DirectX 9时代（2002年前后）最为突出，因为当时驱动层验证开销极大。DirectX 12和Vulkan的设计目标之一正是通过显式命令缓冲区（Command Buffer）将提交开销降低一个数量级，但即便如此，过多的Draw Call仍会产生可观的CPU开销。Unity引擎的性能分析工具Profiler将"Batches"计数作为核心指标展示，正是因为这一数字直接反映了CPU端的Draw Call压力。

Draw Call优化的核心思路是**合并**：将多个对象的渲染命令合并为一次或少数几次提交，减少CPU到驱动层的调用次数，从而将CPU时间预算留给游戏逻辑、物理模拟等其他系统。

## 核心原理

### 静态批处理（Static Batching）

静态批处理在加载阶段（运行时或编辑期）将多个静止网格的顶点数据合并到一个大VBO（顶点缓冲对象）中，所有子网格共享同一套材质。合并后，原来N个Draw Call变为1次。Unity的静态批处理要求对象标记为`Static`，合并结果存储在额外的内存副本中；代价是顶点数据可能增加2–3倍内存占用。Unreal Engine的合并Actor（Merge Actors）工具原理相同，会在编辑器中预计算合并网格并保存为独立资产。

### GPU Instancing（实例化渲染）

GPU Instancing通过一次Draw Call绘制同一网格的多个实例，每个实例拥有独立的变换矩阵（Model Matrix）和可选的逐实例数据（颜色、UV偏移等），这些数据存储在一个**Instance Buffer**中。OpenGL对应`glDrawElementsInstanced(mode, count, type, indices, instanceCount)`，其中`instanceCount`即实例数量。顶点着色器通过内置变量`gl_InstanceID`（GLSL）或`SV_InstanceID`（HLSL）索引对应实例的变换数据。Instancing最适合场景中重复出现的对象：草丛、树木、粒子、人群——同一网格出现100次时，100次Draw Call变为1次。限制在于所有实例必须使用**完全相同的网格和材质**，且实例数量过多时Instance Buffer本身的带宽也需考虑。

### Indirect绘制（Indirect Draw / GPU-Driven Rendering）

Indirect绘制将Draw Call的参数（顶点数、实例数、偏移量等）存储在GPU端的一个**Indirect Buffer**，由GPU在Compute Shader中填充该Buffer，CPU只需调用一次`glMultiDrawElementsIndirect`或`ExecuteIndirect`（D3D12）即可提交整个帧的所有绘制命令。这一技术由育碧在《刺客信条：大革命》（2014年）开发期间系统化推广，可在CPU完全不参与剔除和LOD计算的情况下完成场景渲染。GPU-Driven Rendering的极端形式（如《荒野大镖客：救赎2》使用的Visibility Buffer方案）可将整帧的Draw Call数量压缩到个位数。

### 动态批处理（Dynamic Batching）

动态批处理在每帧运行时合并**顶点数量少于900个**（Unity的默认阈值）的动态网格，将它们的顶点坐标变换到世界空间后拼入临时缓冲区，再提交一次Draw Call。由于顶点变换发生在CPU端，动态批处理在网格顶点数较多或对象数量庞大时反而会增加CPU负担，因此通常只适用于粒子效果或少量小型UI元素。

## 实际应用

在移动端游戏开发中，建议将每帧Draw Call控制在**100–200次**以内（针对中端Android设备，如骁龙778G级别），否则GPU等待CPU提交的空闲时间将导致帧率抖动。具体操作：

- **合图集（Texture Atlas）+ 静态批处理**：场景中装饰物件如路灯、栅栏等共享同一图集材质后，可被静态批处理自动合并，数十个对象变为1次Draw Call。
- **材质变体（Material Property Block）**：Unity中通过`MaterialPropertyBlock`为Instancing对象设置逐实例颜色，既保留Instancing合批，又避免创建新材质实例打断批次。
- **LOD + Instancing联动**：Unreal的HISM（Hierarchical Instanced Static Mesh）组件同时处理LOD切换和Instancing，在大规模植被场景中可将Draw Call从数千降至数十。

在PC/主机平台，GPU-Driven方案更为激进：将场景所有Mesh的IndexBuffer打包进一个`MultiDrawBuffer`，用Compute Shader做Frustum Culling和Occlusion Culling，结果写入Indirect Buffer，最终一次`MultiDrawIndirect`完成整帧绘制。《地平线：零之曙光》的渲染团队在GDC 2017报告中详细描述了类似架构。

## 常见误区

**误区一：Draw Call越少越好，无条件合并所有对象。**
强行合并使用不同材质的对象并不能减少Draw Call，反而会导致超大纹理（Uber Texture）、overdraw增加以及遮挡剔除失效（合并后的大网格无法被部分剔除）。正确做法是仅合并**相同材质**的对象，并在合并前评估遮挡剔除的收益损失。

**误区二：GPU Instancing适用于所有重复对象。**
若场景中同一网格只出现2–3次，Instancing带来的Instance Buffer传输开销可能抵消Draw Call节省的收益。通常当同一网格实例数超过**5–10个**时，Instancing才开始产生净收益。此外，蒙皮动画（Skeletal Animation）的每个实例若骨骼姿态不同，骨骼矩阵数组会使Instance Buffer急剧膨胀，需要专门的GPU蒙皮+Instancing方案（如将骨骼矩阵打包进纹理）。

**误区三：Dynamic Batching是静态批处理的动态版本，效果相当。**
动态批处理的CPU顶点变换开销是静态批处理没有的额外代价，且Unity要求单网格顶点数＜900、顶点属性数＜225，限制极为苛刻。在顶点数接近阈值的网格上使用动态批处理，实测可能导致CPU耗时**反而上升**，因为变换900个顶点的时间已超过减少一次Draw Call的收益。

## 知识关联

Draw Call优化以**渲染管线概述**中的CPU–GPU提交流程为前提，理解驱动层（Driver）在`glDraw*`调用时的验证工作是计算优化收益的基础。

向前延伸，**状态排序（State Sorting）**与Draw Call优化直接协同：将相同材质的对象排列在一起不仅减少状态切换开销，也是静态/动态批处理能够合并的前提条件——批处理要求相邻Draw Call的渲染状态完全一致。**图集批处理（Texture Atlas Batching）**则是在纹理层面强制让不同视觉表现的对象共享同一材质，从而为批处理创造合并条件，是Draw Call优化在资产管线层面的延伸实践。