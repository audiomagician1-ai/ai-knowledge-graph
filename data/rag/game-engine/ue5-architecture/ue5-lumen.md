---
id: "ue5-lumen"
concept: "Lumen全局光照"
domain: "game-engine"
subdomain: "ue5-architecture"
subdomain_name: "UE5架构"
difficulty: 3
is_milestone: false
tags: ["渲染"]

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
updated_at: 2026-03-26
---


# Lumen全局光照

## 概述

Lumen是虚幻引擎5（Unreal Engine 5）中内置的全动态全局光照与反射系统，由Epic Games于2022年随UE5正式版发布。它能够实时计算间接漫反射光照、天空遮蔽以及高质量镜面反射，无需预烘焙光照贴图或手动放置反射捕获球。Lumen的诞生直接解决了UE4时代开发者必须依赖Lightmass烘焙静态光照的工作流瓶颈，使得动态时间循环、可破坏环境等场景的全局光照变得可行。

Lumen采用"软件光追"与"硬件光追"两条路径的混合架构。软件光追基于有向距离场（Signed Distance Field，SDF）和屏幕空间技术，可在不支持DXR扩展的GPU上运行，最低适配DirectX 11显卡；硬件光追则调用DXR（DirectX Raytracing）API，利用GPU的RT Core单元获得更精确的几何细节与玻璃材质支持。两种路径可以在同一项目的不同平台配置中独立启用，开发者通过`r.Lumen.HardwareRayTracing 1`控制台变量切换。

Lumen的重要意义在于它将全局光照的"即时反馈"带入了编辑器工作流——设计师移动一盏灯或修改材质反照率，场景光照会在数帧内收敛到新的稳定状态，而非等待数分钟乃至数小时的烘焙。

## 核心原理

### 场景表示：Lumen场景与距离场

Lumen维护了一套独立于UE5渲染管线的"Lumen场景（Lumen Scene）"缓存，其中包含网格体的**有向距离场（Mesh Distance Fields）**和**表面缓存（Surface Cache）**。表面缓存以卡片（Card）的形式存储网格体六个轴向投影的辐射度、法线和材质属性，每张Card的默认分辨率为128×128纹素。Lumen会根据摄像机距离对Card执行LOD降级，远处网格体的Card分辨率可低至16×16，以控制显存占用。

软件光追模式下，光线从屏幕上的着色点出发，首先在屏幕空间内步进2~4步，若未命中则切换至全局SDF（Global Distance Field）加速结构，以较大步长快速穿越空旷区域，最终在距离场梯度接近0时判定命中并查询表面缓存中的辐照度。

### 辐照度缓存：探针与时间累积

Lumen在场景中自动放置**辐照度探针（Radiance Cache Probes）**，以`64×64×64`的世界空间体素网格分布，每个探针存储半球面辐照度的球谐系数（2阶SH，共9个系数×3通道）。每帧仅更新探针总数的约1/8，通过时间累积（Temporal Accumulation）在多帧间平摊计算开销，这是Lumen能够在实时帧率下运行的关键策略。当摄像机或光源快速移动时，探针的历史权重被削减，收敛速度加快，但代价是短暂出现闪烁（Flickering）。

### 屏幕空间与Lumen的协作

Lumen并不孤立运行，它与UE5的**屏幕空间全局光照（SSGI）**协同工作。对于屏幕内可见的近距离几何细节，SSGI以像素精度补充短距离间接光，而Lumen辐照度探针负责处理超出屏幕范围或被遮挡的中远距离间接光照。两者的混合阈值由`r.Lumen.ScreenProbeGather.ScreenSpaceReconstruction`系列参数控制。反射方面，Lumen在软件光追模式下使用**反射捕获**与光线步进的混合体，硬件光追模式则可追踪真实镜面光线，支持多层玻璃和液体材质的焦散近似。

### 硬件光追路径的额外能力

启用硬件光追后，Lumen可以对**实例化静态网格体（Instanced Static Mesh）**的实际三角形执行精确命中测试，消除SDF在薄壁结构（如铁网、叶片）上的漏光伪影。硬件光追路径还支持**World Position Offset（WPO）动画**的精确遮挡，这对植被随风摆动时的自遮蔽计算有明显改善，代价是每帧TLAS（顶层加速结构）重建的额外GPU开销约为0.5~2ms（视场景复杂度）。

## 实际应用

**动态时间循环场景**：在开放世界游戏中，太阳位置每帧变化，Lumen的探针更新机制使天空光照的间接弹射在约8~16帧内完成收敛，玩家几乎察觉不到过渡延迟。《黑神话：悟空》和Epic官方演示《Valley of the Ancient》均采用Lumen实现昼夜动态光照。

**室内场景的颜色渗色**：传统烘焙光照贴图若物体移动则渗色失效，Lumen的表面缓存与探针系统会实时重新计算红色地毯对白色墙壁的颜色出血（Color Bleeding），开发者无需额外设置任何参数。

**控制台平台适配**：PlayStation 5和Xbox Series X支持Lumen软件光追路径；Nintendo Switch等移动/低端平台则自动降级为UE5内置的**屏幕空间全局光照**，通过`Scalability`配置文件中的`r.Lumen.Supported 0`彻底禁用Lumen并回退到传统方案。

## 常见误区

**误区一：Lumen软件光追等于路径追踪**。Lumen软件光追本质上是基于距离场的近似光线步进，加速结构是SDF而非BVH三角形，因此无法准确处理凹面体内部的反射细节，也不支持透明材质的折射。真正的路径追踪需要在UE5中另外启用`Path Tracer`模式，两者互不替代。

**误区二：硬件光追一定优于软件光追**。硬件光追提供更准确的几何命中，但TLAS重建与着色成本使其在高多边形场景中反而慢于软件路径。Epic官方建议仅在目标平台GPU具备RT Core（Nvidia Turing架构/AMD RDNA 2以上）且场景存在明显薄壁漏光问题时才切换至硬件光追，否则软件路径的性能/质量比更优。

**误区三：Lumen可以完全取代静态光照贴图**。Lumen的间接光照噪点和时间稳定性在强烈明暗对比下仍不及高质量烘焙光照贴图，对于VR等对帧率和稳定性极为敏感的应用，以及移动平台，静态烘焙依然是更可靠的选择。

## 知识关联

学习Lumen前需理解**UE5模块系统**，特别是渲染模块（`Renderer`模块）如何通过`ILumenSceneSubsystem`子系统注册Lumen场景数据，以及`RDG（Render Dependency Graph）`如何调度Lumen的各阶段Pass。Lumen的SDF生成依赖`DistanceField`模块在网格体导入时自动构建的离线资产，这一过程受`Build Settings > Generate Mesh Distance Field`选项控制。

Lumen是学习**全局光照**大类概念的一个具体工程实现案例。掌握Lumen后，开发者可以对比路径追踪（Path Tracing）、辐射度缓存（Radiance Cache）等理论方法，理解Lumen在精度与实时性之间所做的具体工程权衡：例如用2阶球谐（9系数）替代完整光谱分布、用SDF步进替代精确三角形相交测试，以及用时间累积替代每帧全量采样。这些取舍共同构成了Lumen能够在消费级GPU上以30~60fps运行的技术基础。