---
id: "ta-culling"
concept: "裁剪技术"
domain: "technical-art"
subdomain: "perf-optimization"
subdomain_name: "性能优化"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 裁剪技术

## 概述

裁剪技术（Culling）是指在渲染管线执行之前，将摄像机无法看见的物体从渲染队列中剔除，从而避免浪费GPU和CPU资源处理永远不会出现在屏幕上的几何体。其核心逻辑是：不画不可见的东西，而非画了再丢弃。这与光栅化阶段的深度测试不同——深度测试在像素已经被着色后才丢弃，裁剪技术在Draw Call提交之前就阻止了整个物体的渲染。

裁剪技术在早期3D游戏时代（1990年代）随着《毁灭战士》（Doom，1993年）等游戏的BSP树可见性算法诞生而成为工业标准。现代引擎（Unity、Unreal Engine）将多种裁剪手段叠加使用，每种针对不同场景下的不可见情况。在一个典型的开放世界场景中，场景内可能存在数万个网格物体，但摄像机视野内实际可见的往往不超过几百个；若不做裁剪，无效Draw Call数量可导致帧率下降数十倍。

## 核心原理

### 视锥体裁剪（Frustum Culling）

摄像机的可视范围是一个由Near Plane、Far Plane和四个侧面围成的六面体锥形体积，称为视锥体（View Frustum）。视锥体裁剪的判断方式是：将每个物体的轴对齐包围盒（AABB，Axis-Aligned Bounding Box）与视锥体的六个平面逐一做相交测试，若AABB完全位于任意一个平面的外侧，则该物体被判定为不可见并跳过提交。

判断AABB与平面的关系，使用以下点积公式：

> d = N · C + w

其中 **N** 是平面法线向量，**C** 是AABB的中心点坐标，**w** 是平面方程的偏移量。若 d < −r（r为AABB在法线方向上的半投影长度），则该盒子完全在平面外侧，物体被裁剪。Unity引擎中该过程在CPU端由Job System并行计算，每帧对场景中所有Renderer组件执行一遍。

### 遮挡裁剪（Occlusion Culling）

遮挡裁剪解决的是"在视锥体内，但被其他几何体完全挡住"的情况。Unity使用Umbra中间件实现静态遮挡剔除：在编辑器烘焙阶段，系统将场景划分为若干Cell，预计算每个Cell之间的可见性关系，存储为PVS（Potentially Visible Set，潜在可见集合）数据文件。运行时，引擎根据摄像机所在Cell查询PVS表，只渲染当前Cell标记为可见的物体集合，查询复杂度接近O(1)。

动态遮挡裁剪（如Unreal Engine 5的软件光栅化遮挡查询）则在每帧用一张低精度深度图（Hi-Z Buffer）从GPU回读，判断物体的包围盒是否被遮挡。由于GPU-CPU回读有1-2帧的延迟，快速移动物体可能出现短暂闪烁，这是该技术固有的时序代价。

### 距离裁剪（Distance Culling / LOD Distance Culling）

距离裁剪通过设定每个物体的最大绘制距离（Max Draw Distance）实现。当物体到摄像机的欧氏距离超过阈值时，直接从渲染队列移除。在Unity中，每个Renderer组件有`farClipPlane`参数；更精细的控制依赖`LODGroup`组件，其中Culled级别对应距离裁剪。Unreal Engine则通过`Cull Distance Volume`体积盒对区域内所有物体批量设置距离阈值，允许按物体尺寸自动计算合理的裁剪距离（小物体更早被剔除）。

距离裁剪的计算公式通常为：可视距离 ∝ 物体包围球半径 × 屏幕占比阈值系数。

## 实际应用

在Unity HDRP项目中，一个典型的城市场景优化流程是：首先在Editor中运行**Occlusion Culling Bake**，将场景划分为1~2米大小的Cell，生成OC数据；其次为远景建筑设置Max Draw Distance为500米、小道具设置为30米；对所有静态网格物体开启**Static**标志，使其进入视锥体裁剪的加速结构（BVH树）。完成上述配置后，典型城市场景的每帧Draw Call数量可从8000以上降低到1500以内。

在移动端（如Unity URP + Android平台），GPU性能较弱，遮挡裁剪的烘焙数据往往比PC端要求更激进：Cell尺寸缩小到0.5米、Smallest Occluder（最小遮挡体）设为1米，确保建筑物内部房间之间充分剔除，这对手机TileBasedRenderer架构的带宽节省尤其关键。

## 常见误区

**误区一：视锥体裁剪会处理遮挡问题**
视锥体裁剪只判断物体是否在摄像机可视锥体范围内，不考虑物体间的遮挡关系。一堵墙后面的几十栋房屋，视锥体裁剪认为它们都可见（因为它们在视锥体内），只有开启遮挡裁剪才能进一步剔除。两种技术解决的是完全不同的可见性问题，必须同时启用才能发挥最大效果。

**误区二：遮挡裁剪在动态场景中可以完全替代静态烘焙**
Unity的Umbra遮挡裁剪系统只对标记为**Occluder Static**的物体生效作为遮挡源；动态物体（如移动的车辆、角色）不会被纳入遮挡计算，它们不能作为遮挡体来剔除背后的物体。若场景中大量关键遮挡来自动态物体，需要改用GPU Hi-Z遮挡查询方案，但这会带来额外的GPU耗时（约0.3-0.8ms/帧）。

**误区三：裁剪掉的物体不消耗任何资源**
裁剪技术减少的是渲染线程的DrawCall提交和GPU的几何/像素处理，但被裁剪物体的**物理模拟、动画更新、脚本逻辑**仍然可能在CPU上运行。如果要连同逻辑一起停止，需要额外配合物体禁用（SetActive(false)）或ECS中的Chunk裁剪，裁剪技术本身不负责这些系统的激活状态。

## 知识关联

裁剪技术建立在**性能优化概述**所介绍的渲染管线概念之上——Draw Call的含义、CPU提交渲染指令的流程，是理解为什么裁剪必须在提交阶段之前完成的前提知识。视锥体裁剪的六平面测试依赖MVP变换矩阵（Model-View-Projection），而遮挡裁剪的PVS系统则与场景的空间数据结构（BVH、BSP、Octree）直接挂钩。

学习裁剪技术之后，下一个重要的优化话题是**阴影性能**。阴影渲染是裁剪技术最难处理的场景之一：即使一个物体本身被视锥体裁剪掉，它的阴影可能仍然投影在可见区域内，因此阴影渲染需要独立的"阴影视锥体裁剪"（Shadow Frustum Culling），使用光源视角而非摄像机视角的视锥体进行剔除，这一区别是阴影性能优化的核心起点。
