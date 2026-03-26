---
id: "ray-tracing-engine"
concept: "引擎光线追踪"
domain: "game-engine"
subdomain: "rendering-pipeline"
subdomain_name: "渲染管线"
difficulty: 3
is_milestone: false
tags: ["光追"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 44.8
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---



# 引擎光线追踪

## 概述

引擎光线追踪是指在游戏引擎渲染管线中，通过微软DXR（DirectX Raytracing）或Khronos Vulkan Ray Tracing扩展（VK_KHR_ray_tracing_pipeline）等硬件加速API，将传统光线追踪算法集成到实时渲染流程中的技术体系。与离线渲染中每帧耗费数小时的光线追踪不同，引擎光线追踪依赖NVIDIA Turing架构（2018年发布的RTX 20系列）引入的RT Core硬件单元，将BVH（包围盒层次结构）遍历和光线-三角形求交运算卸载到专用硬件，使每帧毫秒级别的实时光追成为可能。

DXR于2018年随DirectX 12的更新首次公开，引入了全新的渲染管线状态对象——光线追踪管线（RTPSO），以及五类着色器：光线生成着色器（Ray Generation Shader）、最近命中着色器（Closest Hit Shader）、任意命中着色器（Any Hit Shader）、未命中着色器（Miss Shader）和相交着色器（Intersection Shader）。这套管线与传统光栅化管线并行存在，引擎需要在同一帧内调度两者协同工作。

引擎光线追踪的重要性在于，它为长期依赖预计算或屏幕空间技巧的实时全局光照提供了物理正确的替代路径。《赛博朋克2077》《控制》《战地5》等游戏正是依托此技术，实现了传统光栅化管线难以企及的动态阴影、真实反射和间接光照效果。

## 核心原理

### 加速结构：BVH的构建与更新

引擎光线追踪的性能基础是加速结构（Acceleration Structure），在DXR中分为两级：底层加速结构（BLAS，Bottom-Level Acceleration Structure）和顶层加速结构（TLAS，Top-Level Acceleration Structure）。BLAS存储单个网格的几何数据及其内部BVH树，TLAS存储场景中所有BLAS实例的变换矩阵。这种两级设计允许引擎在角色移动时只更新TLAS，而静态几何体的BLAS无需重建，大幅降低每帧的CPU/GPU加速结构更新开销。

对于骨骼动画角色，引擎必须每帧重建或重装（Refit）对应BLAS，因为顶点位置在GPU蒙皮后发生了变化。DXR提供`D3D12_RAYTRACING_ACCELERATION_STRUCTURE_BUILD_FLAG_ALLOW_UPDATE`标志，允许在原有BVH基础上进行增量更新（Refit），速度比完整重建快约3倍，但BVH质量会逐渐退化，引擎通常每隔数帧触发一次完整重建以恢复遍历效率。

### 混合渲染架构

现代引擎并不以纯光线追踪替代光栅化，而是采用混合渲染（Hybrid Rendering）架构：光栅化负责G-Buffer生成（位置、法线、材质ID等），光线追踪仅用于计算特定效果——例如从G-Buffer中每个可见像素发射1至4条阴影测试光线，或发射少量反射光线采样环境。虚幻引擎5的Lumen系统在硬件光追模式下，会从世界空间探针和屏幕像素同时发射短距离光线，结合屏幕空间缓存，将单帧光线数量控制在GPU预算内。

引擎中的光线追踪效果通常包括：硬件光线追踪阴影（RT Shadows）、反射（RT Reflections）、环境光遮蔽（RTAO）、全局光照（RTGI）和半透明（RT Translucency）。每种效果可独立启用，允许开发者根据目标平台的性能预算灵活组合。

### 着色器绑定表与材质系统

DXR通过着色器绑定表（SBT，Shader Binding Table）将场景中每个几何体实例与其对应的命中组着色器关联。SBT本质上是GPU内存中的一段连续布局，每个记录包含着色器标识符（32字节）加上用户自定义的本地根签名数据。引擎在构建TLAS时，需要为每个实例计算其在SBT中的偏移量`InstanceContributionToHitGroupIndex`，确保光线命中某个实例时调用正确的材质着色器。这一机制使引擎的材质系统与光追管线之间需要建立专门的映射层，是集成DXR时代码量最大的工程工作之一。

Vulkan的对应机制称为着色器绑定表（同名），通过`vkCmdTraceRaysKHR`命令指定`VkStridedDeviceAddressRegionKHR`结构体数组，分别描述光线生成、命中、未命中三组着色器在缓冲区中的起始地址和步长。

## 实际应用

**虚幻引擎5中的硬件光追集成**：UE5在Project Settings中将硬件光追划分为独立的功能开关。启用后，引擎自动为场景中的Static Mesh组件构建BLAS，并在每帧PrePass阶段完成TLAS更新。Lumen的硬件光追模式将近场（0~200cm）和远场分别用软件SDF追踪和硬件BVH追踪处理，避免短距离高频光线消耗宝贵的RT Core带宽。

**《控制》（Control）的实现方案**：Remedy Entertainment在2019年发布的《控制》中，采用DXR实现了全局光照、反射和阴影的混合光追方案。该游戏在RTX 2080 Ti上以1080p运行时，纯光栅化约130fps，开启全套光追效果后降至约45fps，清晰展示了光追效果与性能成本之间的权衡关系，成为业界评估引擎光追实际开销的标杆案例。

**移动端与主机平台的差异**：PlayStation 5和Xbox Series X均支持硬件光追（基于AMD RDNA 2架构），但其RT性能约为PC高端GPU的1/3至1/2，因此主机引擎集成时更倾向于仅启用RTAO或低采样率的软阴影光追，而非PC平台的完整光追反射链路。

## 常见误区

**误区一：光线追踪可以完全取代光栅化G-Buffer阶段**。实际上，在当前硬件条件下，仅用光线追踪生成所有可见像素的颜色（路径追踪模式）需要在4K分辨率下每帧发射超过830万条主光线，再加上每像素4~16条次级光线，总计数亿条光线，远超当前GPU实时预算。引擎中的光追始终作为光栅化的补充层，而非替代者。

**误区二：引擎只需调用光追API即可自动获得正确的间接光照**。事实上，光追API仅负责求交计算；着色结果、降噪处理、时间累积（Temporal Accumulation）和去噪滤波（如NVIDIA的DLSS Ray Reconstruction或NRD降噪库）需要引擎自己实现。未经降噪的每像素1spp（每像素一次采样）光追图像充满噪点，完全无法直接使用，降噪算法的质量直接决定最终光追效果的可用性。

**误区三：BLAS一经创建无需关注**。对于含有顶点动画、破坏系统或程序化生成几何体的场景，BLAS必须随几何数据变化而更新，忽略这一点会导致光线与实际几何体位置不符，产生错误的阴影漏光或反射幽灵（Ghost Artifact）。

## 知识关联

引擎光线追踪建立在全局光照理论的数学基础之上——渲染方程（Rendering Equation，由James Kajiya于1986年提出）描述的积分运算，正是光追通过蒙特卡洛采样逐步逼近的目标。理解半球积分、重要性采样和低差异序列（如Halton序列、Sobol序列）有助于解释为何1spp光追噪点严重，以及为何时间积累能够收敛到正确结果。

在管线层面，引擎光线追踪与延迟渲染管线高度耦合——G-Buffer提供了命中着色所需的材质信息，反过来光追结果（如AO、阴影遮蔽因子）又以纹理形式反馈回光照计算阶段。掌握延迟渲染管线的数据流结构，是理解混合光追架构中数据如何在光栅化与光追两条通路之间传递的前提。