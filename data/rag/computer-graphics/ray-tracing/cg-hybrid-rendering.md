---
id: "cg-hybrid-rendering"
concept: "混合渲染管线"
domain: "computer-graphics"
subdomain: "ray-tracing"
subdomain_name: "光线追踪"
difficulty: 3
is_milestone: false
tags: ["架构"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 41.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.414
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 混合渲染管线

## 概述

混合渲染管线（Hybrid Rendering Pipeline）是一种将传统光栅化渲染与光线追踪技术结合的渲染架构，其核心思想是用光栅化处理主要可见性判断（Primary Visibility），用光线追踪专门计算反射、阴影、环境光遮蔽等需要全局光照信息的效果。这种分工并非随意为之——光栅化在处理不透明几何体的第一次"看到什么"时效率极高，而光线追踪在追踪光线反弹时具有物理正确性优势。

混合渲染管线的工程实践随NVIDIA在2018年发布RTX 20系列显卡（Turing架构）后迅速普及。Turing架构首次引入专用RT Core硬件，使得每秒光线-三角形相交测试可达10 Giga Rays/s，这让在实时帧率下运行部分光线追踪效果成为可能。在此之前，完全路径追踪对于实时渲染是不现实的，而纯光栅化又无法物理正确地模拟镜面反射和软阴影。混合架构正是在这一硬件能力边界上诞生的工程妥协方案。

对于图形学学习者而言，混合渲染管线的重要性在于它是目前（2023-2024年）游戏引擎（包括Unreal Engine 5、Unity HDRP）在实时渲染中的主流实现路径。理解它意味着理解为什么现代游戏既有实时阴影又有物理正确的反射，以及这两者如何共享同一个G-Buffer。

## 核心原理

### 光栅化阶段：生成G-Buffer

混合渲染管线的第一阶段与延迟渲染（Deferred Rendering）完全一致——通过光栅化将场景几何信息写入G-Buffer。G-Buffer通常包含以下通道：世界空间法线（Normal）、反射率（Albedo）、金属度（Metallic）、粗糙度（Roughness）、以及深度（Depth）。这一阶段的代价是每个像素恰好一次几何着色器调用，时间复杂度与屏幕分辨率成正比而与场景三角形数量弱相关（通过视锥剔除和遮挡剔除处理）。G-Buffer的数据将在后续光线追踪阶段作为光线起点和材质信息的来源，因此G-Buffer的精度（通常使用16-bit浮点格式）直接影响后续光线追踪的质量。

### 光线追踪阶段：次级光线计算

获得G-Buffer后，管线从每个像素的世界空间位置出发发射**次级光线（Secondary Rays）**，而非从摄像机重新追踪主光线。这是混合管线与纯路径追踪最本质的区别：主可见性（Primary Visibility）由光栅化给出，光线追踪只负责次级效果。常见的次级光线类型包括：

- **反射光线（Reflection Rays）**：从G-Buffer法线和粗糙度计算出反射方向，追踪场景中真实的镜面反射。对粗糙材质，需要按GGX分布采样多条光线并取均值（蒙特卡洛积分），样本数通常为1-4 spp（samples per pixel）。
- **阴影光线（Shadow Rays）**：从着色点向光源方向发射一条光线，仅判断是否被遮挡（Any-Hit着色器），不需要计算完整交点信息，因此比反射光线便宜约60-70%。
- **环境光遮蔽光线（AO Rays）**：在法线半球内随机采样若干方向，统计被遮挡比例，替代Screen Space AO（SSAO）的近似方案，解决SSAO的屏幕边缘信息缺失问题。

### 降噪与时序重用

由于实时预算限制，混合管线中的光线追踪每像素样本数极少（通常1 spp），产生的原始图像噪声极大。因此降噪器（Denoiser）是混合渲染管线不可分割的组成部分。工业界主流方案是**时序积累降噪（Temporal Accumulation）**，其核心公式为：

$$\hat{L}_t = \alpha \cdot L_t + (1-\alpha) \cdot \hat{L}_{t-1}$$

其中 $L_t$ 是当前帧原始噪声渲染结果，$\hat{L}_{t-1}$ 是上一帧的滤波后结果，$\alpha$ 通常取0.1（即混入10%新帧，保留90%历史），历史帧通过运动向量（Motion Vector）重投影到当前帧坐标系。NVIDIA的DLSS 3.5（Ray Reconstruction）用神经网络替代了传统时序滤波器，在细节保留上有显著改善。

## 实际应用

**《控制》（Control, 2019）**是混合渲染管线首批商业落地的案例之一。该游戏使用光栅化绘制主场景，用光线追踪实现地板和墙面的反射以及区域光软阴影。在RTX 2080 Ti上以1080p运行时，光线追踪阶段的反射效果约消耗4ms帧时间，配合时序降噪后，视觉效果接近离线渲染质量的镜面反射。

**Unreal Engine 5的Lumen系统**在硬件光线追踪模式下采用混合方案：近距离使用硬件光线追踪进行精确的全局光照计算，远距离退化为基于有向距离场（SDF）的软件光线追踪，两者通过距离阈值（默认200cm）无缝混合。这一设计使得即便在不支持RTX的显卡上也能运行，但精度有所下降。

**DirectX Raytracing（DXR）API**为混合管线提供了标准化接口。开发者在同一命令列表（Command List）中混用 `DrawIndexedInstanced`（光栅化调用）和 `DispatchRays`（光线追踪调用），两者共享相同的资源堆（Descriptor Heap）和加速结构（BVH，Bounding Volume Hierarchy），使得G-Buffer数据可以直接传递给光线追踪着色器。

## 常见误区

**误区一：认为混合管线中光线追踪替代了光栅化**。实际上混合管线中光栅化仍然负责每帧最重要的计算——确定所有可见像素的几何信息。光线追踪仅作为光照计算的辅助手段插入延迟渲染的光照阶段之后。如果去掉光线追踪，整个画面仍然可以正常渲染，只是缺少准确的反射和软阴影。

**误区二：认为1 spp的光线追踪质量必然不足**。在混合管线配合时序降噪的前提下，1 spp反射光线经过8-16帧积累后等效于8-16 spp的质量。当摄像机静止时，时序积累无限累积，最终收敛到无噪声的结果。问题仅在于快速运动或场景突变时历史帧失效，产生"鬼影"（Ghosting）瑕疵，这是混合管线尚未完全解决的工程挑战。

**误区三：认为BVH（加速结构）只在纯光线追踪中使用**。混合管线同样需要为场景构建BVH，且BVH的更新（针对动态物体）每帧都有代价。NVIDIA的建议是将动态物体（角色、车辆）放入底层加速结构（BLAS，Bottom-Level Acceleration Structure）单独重建，顶层结构（TLAS，Top-Level Acceleration Structure）每帧重建，以平衡精度与性能。

## 知识关联

混合渲染管线建立在**光栅化概述**和**RTX硬件加速**两个前置知识之上。光栅化概述提供了G-Buffer生成和延迟着色的概念基础，没有对延迟渲染的理解很难看懂为何主可见性由光栅化而非光线追踪处理。RTX硬件加速解释了为什么RT Core的存在使得次级光线的实时计算从理论走向工程实践——没有专用硬件加速BVH遍历，相同的混合渲染负载在着色器中软件模拟时帧时间会增加约8-10倍。

从技术演进角度，混合渲染管线是图形学从完全近似（纯光栅化的反射贴图、阴影贴图）向物理正确渲染（纯路径追踪）过渡的中间形态。随着GPU的RT Core算力按代际增长（从Turing到Ada Lovelace，RT Core算力提升约3倍），未来混合管线中光线追踪承担的比重将持续增加，直至某一代硬件使完全实时路径追踪成为可能。
