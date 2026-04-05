---
id: "occlusion-culling"
concept: "遮挡剔除"
domain: "game-engine"
subdomain: "rendering-pipeline"
subdomain_name: "渲染管线"
difficulty: 3
is_milestone: false
tags: ["优化"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# 遮挡剔除

## 概述

遮挡剔除（Occlusion Culling）是渲染管线中的一项优化技术，其目标是在向GPU提交绘制调用之前，提前识别并丢弃那些被其他几何体完全遮住、不会出现在最终画面上的物体。与视锥剔除只检查物体是否在摄像机视野范围内不同，遮挡剔除需要判断可见物体之间的"遮挡关系"，因此计算代价更高，但在建筑室内场景或密集城市场景中可以减少60%~90%的绘制调用。

遮挡剔除的概念最早在1969年由Appel提出，称为"量化不可见性"（Quantified Invisibility）。真正在实时游戏引擎中大规模应用是在2000年代初期，《毁灭战士3》（Doom 3，2004年）的引擎通过Portal/Cell系统做了精确的可见性预计算，成为业界标志性实现。现代引擎（如Unreal Engine 5、Unity HDRP）则同时支持预计算、GPU查询和层次深度图等多种手段。

在GPU算力极为充足的今天，遮挡剔除仍然至关重要，因为Draw Call的CPU提交开销、顶点着色器的调用次数以及Early-Z阶段的压力，都会随着未被剔除的物体数量线性增长。一个正确实现的遮挡剔除系统可以将场景中的有效三角形数量从数亿降至数千万级别。

---

## 核心原理

### 1. 层次深度图（Hi-Z，Hierarchical Z-Buffer）

Hi-Z 是目前最主流的 GPU 端遮挡剔除方案。其核心数据结构是对当前帧（或上一帧）的深度缓冲区进行逐级向下采样，构建一个 Mipmap 链。每个 Mip 层级存储对应区域内**最大深度值（最远深度）**，因此第 k 级分辨率为原始深度图的 1/2^k。

剔除判断公式为：

> **若物体包围盒投影到屏幕后，其最小深度值（最近点）> 对应 Hi-Z Mip 层级存储的最大深度值，则该物体完全被遮挡。**

选择 Mip 层级时，以包围盒投影矩形的最大边长 `L_max` 为依据，取 `k = ceil(log2(L_max))` 层，保证单次读取4个纹素即可覆盖整个投影区域，使判断只需一次纹理采样。Hi-Z 每帧都从上一帧深度图重建，因此存在**单帧延迟**（one-frame lag）的幽灵遮挡问题，需要对快速移动的摄像机特别处理。

### 2. 软件遮挡剔除（Software Occlusion Culling，SOC）

软件遮挡剔除完全在 CPU 端运行，通常使用 SIMD 指令（SSE/AVX）对低分辨率软件深度缓冲（典型值为 320×180 或 512×288）进行光栅化。选定场景中面积大、覆盖率高的若干个"遮挡体"（Occluder），例如建筑墙面、地形，将其投影并写入软件深度缓冲，然后逐一测试其他物体的包围盒是否被遮挡。

英特尔在2015年开源了 **Intel Software Occlusion Culling** 库（基于 AVX2），可在单核上以约 1ms/帧完成 320×180 深度图的光栅化与测试，剔除率与 GPU Hi-Z 相近。SOC 的优势是结果当帧立即可用，不存在延迟问题；缺点是遮挡体需要美术手动标注或自动筛选，且 CPU 预算固定消耗。

### 3. GPU 遮挡查询（GPU Occlusion Query）

GPU 遮挡查询使用 OpenGL 的 `GL_SAMPLES_PASSED` 查询对象或 Direct3D 的 `D3D11_QUERY_OCCLUSION`，先渲染深度预通道（Depth Prepass），然后用简化包围盒发出查询，询问"有多少像素通过深度测试"。若结果为0，则物体不可见。

其致命缺陷在于**GPU→CPU 读回延迟**：查询结果需要至少 2~3 帧后才能安全读回，否则会造成 Pipeline Stall。常见的解决方案是"条件渲染"（Conditional Rendering，`glBeginConditionalRender`），让 GPU 自行根据查询结果决定是否执行后续绘制命令，完全不回读到 CPU，但调试极为困难。由于这些缺陷，GPU 遮挡查询在现代引擎中已逐渐被 Hi-Z Compute Shader 方案取代。

---

## 实际应用

**Unreal Engine 5 的 GPU Scene Culling**：UE5 的 Nanite 虚拟几何体系统在 Cluster 级别进行 Hi-Z 剔除，每个 Nanite Cluster（约128个三角形）都会被单独测试，而非以整个 Mesh 为单位。这使得一栋建筑只有朝向摄像机的那一面的 Cluster 被渲染，剔除粒度精确到 128 三角形级别。

**Unity HDRP 的 Occlusion Culling Baking**：对于静态场景，Unity 提供预计算遮挡剔除（Umbra 算法），将整个场景体素化为 PVS（Potentially Visible Set）查找表。运行时只需查表，无需任何实时计算，适合摄像机运动路径固定的关卡设计，但烘焙时间随场景复杂度指数增长，100万面的场景烘焙可能需要数小时。

**移动平台的 Tile-Based 遮挡**：在 PowerVR 等 TBDR 架构的移动 GPU 上，HSR（Hidden Surface Removal）机制在光栅化阶段自动丢弃被遮挡片段，因此传统遮挡剔除对这类 GPU 的收益主要体现在减少顶点处理阶段，而非片段着色阶段。

---

## 常见误区

**误区一：视锥剔除已经足够，遮挡剔除是多余的**

视锥剔除只能剔除摄像机视野之外的物体，而在室内场景、城市俯视场景中，视野内可能存在大量相互遮挡的物体。例如，一条街道上摄像机正前方的建筑可以遮挡其背后数十栋建筑，这些物体全部通过视锥剔除，却只有遮挡剔除能将其丢弃。两种技术剔除的物体集合几乎不重叠，应同时使用。

**误区二：Hi-Z 剔除结果总是100%正确**

由于 Hi-Z 使用上一帧深度图，当摄像机快速旋转或大型遮挡体突然移出视野时，本帧的 Hi-Z 数据可能已经失效，导致本应可见的物体被错误剔除（称为"鬼影剔除"，Ghost Culling）。正确的解决方案是对快速移动的物体保守估计（Conservative Depth Test），或对被错误剔除的物体在下一帧强制提交一次补偿绘制。

**误区三：遮挡剔除对所有场景都有收益**

在开阔地形场景（如赛车游戏的赛道俯视视角）中，地平线附近大量物体彼此不遮挡，遮挡剔除的查询开销甚至会超过其节省的渲染开销。这种场景更适合使用 LOD（Level of Detail）和距离剔除，而非遮挡剔除。

---

## 知识关联

**前置概念—渲染管线概述**：理解遮挡剔除需要明确它在管线中的位置——遮挡剔除发生在 CPU 提交 Draw Call 之前（CPU 端 SOC/预计算方案）或 GPU 深度预通道之后（Hi-Z/GPU Query 方案）。Early-Z 测试是 GPU 固定管线中的隐式遮挡剔除，但它在三角形已经提交后才生效，遮挡剔除则试图在更早阶段阻止提交。

**横向关联—LOD 系统**：遮挡剔除与 LOD 共同构成场景可见性管理体系。LOD 根据距离降低几何复杂度，遮挡剔除则完全消除不可见物体的绘制。Nanite 将两者统一为单一的 Cluster 可见性管线，消除了传统 LOD 切换时的跳变（Popping）伪影。

**延伸方向—GPU Driven Rendering**：现代 GPU Driven 渲染架构将遮挡剔除完全移入 GPU Compute Shader，通过 `DrawIndirect` / `ExecuteIndirect` 指令让 GPU 自行决定绘制哪些物体，彻底消除 CPU-GPU 读回延迟，是目前高端游戏引擎的主流演进方向。