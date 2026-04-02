---
id: "cg-occlusion-culling"
concept: "遮挡剔除"
domain: "computer-graphics"
subdomain: "render-optimization"
subdomain_name: "渲染优化"
difficulty: 3
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 遮挡剔除

## 概述

遮挡剔除（Occlusion Culling）是一种渲染优化技术，其核心目标是在GPU光栅化之前，提前识别并丢弃被其他不透明几何体完全遮住、在最终画面中不可见的物体，从而避免对这些物体进行无效的顶点处理和片元着色。与视锥剔除仅检查物体是否在相机视锥体范围内不同，遮挡剔除进一步判断视锥体内的物体是否真正对相机可见。

该技术的系统性研究始于1990年代中期，Hanan Samet等人对空间数据结构的研究和Sekiguchi等人对可见性判断的工作为其奠定了理论基础。1997年，Tomas Möller和Eric Haines在其著作《Real-Time Rendering》中对遮挡剔除算法进行了系统分类。在现代3D游戏引擎（如Unreal Engine 5和Unity）中，遮挡剔除是CPU侧提交Draw Call前的必要优化步骤，对于包含大量建筑物的城市场景，启用遮挡剔除可将Draw Call数量减少60%~90%。

遮挡剔除之所以重要，根本原因在于GPU的渲染管线无法自动跳过被遮挡的物体——即使一栋建筑完全挡住了后面的街道，驱动层依然会逐一处理所有提交的Draw Call。遮挡剔除将可见性判断提前到CPU阶段（或借助GPU异步查询），从源头减少渲染负载。

---

## 核心原理

### 层次深度缓冲（Hierarchical Z-Buffer，HZB）

HZB是当前引擎中最主流的硬件加速遮挡剔除方案。其构建过程分两步：首先以上一帧的深度缓冲（Depth Buffer）为输入，逐层构建Mip链，每一级Mip存储其对应4个子像素中的**最大深度值（far depth）**；完整Mip链通常包含log₂(max(width, height))层，对于1920×1080的视口约需11级。

测试一个物体是否被遮挡时，将其包围盒投影到屏幕空间，计算包围盒覆盖区域在HZB中对应的Mip层级（选取覆盖范围恰好为2×2像素的那一级），读取该层级的深度值。若包围盒的**最小深度（离相机最近的角点深度）大于**HZB对应层级的最大深度，则该物体一定被完全遮挡，可以安全剔除。

HZB查询存在一帧延迟（使用上一帧深度图），相机快速移动时会出现**Ghost Occluder**问题（上一帧遮挡物已离开，但当前帧仍错误剔除了后方物体），Unreal Engine通过维护一个"保守包围盒扩展"和每帧重新提交被剔除物体的验证Pass来缓解此问题。

### Software Rasterization遮挡剔除

软件光栅化遮挡剔除（Software Occlusion Culling）在CPU上用简化的软光栅器绘制场景中的**大型遮挡体（Occluder）**，生成一张低分辨率深度图（通常256×128或512×256），随后用这张CPU深度图对其他物体（Occludee）做可见性测试，全程不依赖GPU，避免了CPU-GPU同步等待。

Intel在2014年发布的开源库**Masked Software Occlusion Culling（MSOC）**将此技术推广开来，其核心创新是使用AVX2 SIMD指令同时处理8个三角形的光栅化，在256×128分辨率下的完整遮挡图生成耗时通常低于1ms（在现代x86 CPU上）。MSOC使用一个每像素8位的"覆盖掩码"表示三角形是否完全覆盖对应像素块，从而避免逐像素写入开销。

软件光栅化剔除的精度低于HZB，但完全在CPU上运行，不产生GPU-CPU回读延迟，适合CPU驱动的剔除管线（如Unreal的Nanite Cluster Culling前期阶段）。

### 硬件遮挡查询（Hardware Occlusion Query）

OpenGL通过`GL_SAMPLES_PASSED`查询、DirectX通过`D3D11_QUERY_OCCLUSION`提供硬件遮挡查询接口：先以无色无深度写入方式绘制物体的包围盒，然后查询通过深度测试的片元数量，若为0则判定物体不可见。由于查询结果存在1~2帧的GPU-CPU管线延迟，实际使用时常采用**条件渲染（Conditional Rendering）**将判断留在GPU端，用`glBeginConditionalRender`令GPU自行根据查询结果决定是否执行后续Draw Call，完全避免CPU回读。

---

## 实际应用

**城市场景中的建筑遮挡**：在《地铁：离去》等第一人称游戏中，室内走廊的墙壁是天然的强遮挡体，软件光栅化遮挡剔除可将走廊外的全部城市建筑剔除，仅保留走廊内可见物体，场景复杂度从数千个Draw Call降至数十个。

**Unreal Engine 5的Lumen与HZB集成**：UE5的Hardware Lumen在追踪屏幕空间反射时，使用HZB提供的深度层级快速判断反射光线是否命中场景，HZB在此不仅作为遮挡剔除工具，还作为一种紧凑的场景深度表示用于光线步进（Ray Marching）。

**移动平台的Tile-Based遮挡**：由于移动GPU采用Tile-Based Deferred Rendering（TBDR）架构，PowerVR等GPU原生支持HSR（Hidden Surface Removal），在片元着色前硬件自动丢弃被遮挡片元，但这仍需要渲染管线按**从前到后（Front-to-Back）**顺序提交Draw Call才能充分发挥效益，这正是遮挡剔除排序的直接意义所在。

---

## 常见误区

**误区1：遮挡剔除与背面剔除（Backface Culling）混为一谈**。背面剔除基于三角面法线与视线方向的点积（`dot(N, V) < 0`即剔除），只能丢弃背向相机的单个三角形面，无法判断一个完整物体是否被另一个物体遮住。遮挡剔除工作在物体包围盒层级，解决的是物体间的深度遮挡关系，二者作用层级完全不同。

**误区2：HZB剔除结果绝对准确**。HZB使用的是上一帧的深度图，属于**保守估计（Conservative）**——它只会将"一定被遮挡"的物体剔除（False Negative不存在），但当相机快速旋转时，遮挡关系变化剧烈，HZB可能漏剔本应被遮挡的物体（即出现漏判），导致性能不如预期而非产生画面错误。

**误区3：场景中遮挡体越多效果越好**。遮挡剔除的效益取决于"遮挡率"而非遮挡体数量。若场景开阔（如赛车游戏的户外赛道），物体间几乎无遮挡，强行开启HZB反而增加每帧构建Mip链的开销（约0.1~0.3ms GPU时间），得不偿失。

---

## 知识关联

**前置概念——视锥剔除**：遮挡剔除是视锥剔除的下一道过滤关卡。视锥剔除先剔除视锥体外的物体，使遮挡剔除的候选集合大幅缩小；HZB构建本身也只需要视锥体内的深度数据，两者在引擎管线中顺序执行，共同构成CPU侧的几何剔除链条。

**后续概念——GPU剔除**：遮挡剔除的查询与判断逻辑可以整体迁移到GPU上，借助Compute Shader对数十万个物体并行执行包围盒深度测试，并通过`DrawIndirect`/`ExecuteIndirect`机制将通过测试的物体直接生成Draw Call，无需回传CPU，这即是GPU Driven Rendering中GPU剔除的核心思路，是对本文HZB原理的硬件并行化扩展。