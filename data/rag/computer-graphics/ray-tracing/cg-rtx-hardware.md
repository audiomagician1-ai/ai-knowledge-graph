---
id: "cg-rtx-hardware"
concept: "RTX硬件加速"
domain: "computer-graphics"
subdomain: "ray-tracing"
subdomain_name: "光线追踪"
difficulty: 3
is_milestone: false
tags: ["硬件"]

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
updated_at: 2026-04-01
---


# RTX硬件加速

## 概述

RTX硬件加速是NVIDIA于2018年随Turing架构（RTX 20系列）推出的专用光线追踪硬件技术，其核心是在GPU芯片上集成专门的**RT Core**单元，使光线-三角形求交和BVH节点遍历能够在独立硬件单元上并行执行，而非占用传统CUDA着色器核心的计算资源。在RTX 2080 Ti中，RT Core数量为68个，每个RT Core能够每秒处理约100亿次光线-盒子（AABB）和光线-三角形求交测试，这一数字比同期纯软件实现快约30倍。

该技术的工业背景源于实时光线追踪长期以来的性能瓶颈：传统光栅化管线无法高效处理光线的递归求交逻辑，而在着色器中模拟BVH遍历会消耗大量ALU资源。NVIDIA通过将遍历与求交运算卸载（offload）到固定功能单元，释放了CUDA核心专注于着色计算。2020年的Ampere架构（RTX 30系列）将RT Core升级至第二代，性能相比Turing提升约1.7倍，并增加了对运动模糊（motion blur）的硬件加速支持。

理解RTX硬件加速的意义在于它重新定义了GPU内部的任务分工：一帧画面的渲染可以同时动用RT Core做求交、Tensor Core做降噪（DLSS）、CUDA Core做着色，三类专用硬件协同工作。开发者通过DXR（DirectX Raytracing）或Vulkan Ray Tracing扩展向这套硬件发出指令，而不是直接操控RT Core的微架构细节。

---

## 核心原理

### RT Core的工作机制

RT Core执行两类固定功能操作：**ray-AABB测试**（光线与轴对齐包围盒求交）和**ray-triangle测试**（光线与三角形求交，使用Möller-Trumbore算法的硬件实现）。当着色器调用`TraceRay()`函数后，光线参数被提交给RT Core，RT Core自动遍历已构建好的两级BVH结构（Top-Level Acceleration Structure，TLAS，和Bottom-Level Acceleration Structure，BLAS），在此过程中CUDA核心处于空闲或执行其他任务的状态。只有当RT Core确认命中某个三角形时，才会触发对应的**任意命中（Any Hit）**或**最近命中（Closest Hit）** shader，将控制权交还给CUDA核心执行着色逻辑。

### DXR API的着色器阶段划分

DXR将光线追踪管线拆解为五类专用着色器，每类均有明确的触发条件：

| 着色器类型 | 触发时机 |
|---|---|
| Ray Generation Shader | 每像素一次，主动发射光线 |
| Intersection Shader | 自定义图元（非三角形）求交时 |
| Any Hit Shader | 每次候选命中（可用于透明度测试） |
| Closest Hit Shader | BVH遍历结束后最近命中点 |
| Miss Shader | 光线未命中任何几何体时 |

其中Any Hit Shader可以被RT Core硬件在遍历过程中频繁调用，因此该着色器中放入复杂逻辑会严重破坏RT Core与CUDA Core的并行性，实践中应尽量保持Any Hit Shader极度轻量。

### 两级加速结构（TLAS/BLAS）与硬件的协同

RT Core遍历的BVH并非单层扁平结构，而是强制使用两级组织：BLAS存储单个网格的几何体，TLAS引用多个BLAS实例并附带变换矩阵。硬件在遍历TLAS时完成世界空间的粗筛，进入BLAS后在对象空间完成精确求交，变换矩阵的逆运算（将光线变换到对象空间）由RT Core自动处理。Vulkan Ray Tracing扩展（`VK_KHR_ray_tracing_pipeline`，于Vulkan 1.2正式纳入KHR标准）同样遵循这一两级结构要求，与DXR在此层面行为一致。

---

## 实际应用

**《赛博朋克2077》**中的光线追踪反射与全局光照实现了对RT Core的深度利用：游戏同时发射多束低采样数光线，利用Tensor Core驱动的DLSS 2.0对低分辨率光线追踪结果进行超分，使RTX 3080在4K分辨率下维持60fps左右的帧率，而纯路径追踪若无硬件加速则在该分辨率下每帧耗时超过2秒。

在**离线渲染向实时迁移**的工作流中，Chaos Group的V-Ray GPU引入了DXR后端，BVH构建阶段由CPU转移至GPU的`BuildRaytracingAccelerationStructure()`命令，BLAS的构建支持`FAST_TRACE`和`FAST_BUILD`两种标志位：`FAST_TRACE`优化BVH质量以加速遍历，适合静态场景；`FAST_BUILD`降低BVH质量但缩短构建时间，适合动态形变网格的每帧重建。

**NVIDIA Omniverse**的实时路径追踪器直接通过Vulkan `VK_KHR_ray_tracing_pipeline`驱动RTX硬件，将工业级产品可视化从渲染场（render farm）的数小时缩短至桌面端的交互级响应，单帧累积采样数从1到512可按需调整。

---

## 常见误区

**误区1：RT Core加速了整个光线追踪渲染过程**
RT Core仅加速BVH遍历和几何求交这两个步骤。光线的着色计算（Closest Hit Shader中的材质评估、纹理采样、光照积分）仍完全运行在CUDA核心上，与普通着色器无异。对于着色复杂的场景，CUDA核心的着色耗时可能远超RT Core的求交耗时，此时提升RT Core数量对帧率的边际收益很小。

**误区2：DXR/Vulkan RT直接控制RT Core的物理硬件**
开发者调用的`TraceRay()`或`traceRayEXT()`是驱动层抽象接口，在没有RT Core的旧GPU上，驱动会用CUDA着色器模拟遍历逻辑（性能大幅降低但功能正确）。RTX硬件的实际调度仍由驱动管理，开发者无法直接读写RT Core的内部寄存器或缓存。

**误区3：光线追踪中所有几何体均需构建BLAS**
DXR和Vulkan RT均支持**程序化图元（procedural geometry）**通过自定义Intersection Shader绕过三角形求交硬件。此类图元（如解析球体、SDF体积）不进入RT Core的triangle测试单元，而是在AABB命中后回调到CUDA核心执行求交逻辑，因此对RT Core的利用率为零，需权衡准确度与性能。

---

## 知识关联

**前置概念——BVH加速结构**：理解RTX硬件加速的前提是掌握BVH的节点结构（内部节点存AABB，叶节点存三角形）和遍历算法（栈式深度优先或迭代遍历），因为RT Core的固定功能单元本质上是BVH遍历状态机的硅化实现。TLAS/BLAS的两级划分直接对应BVH的层次化组织思路，但在硬件API层面强制将动态变换与静态几何分离。

**后续概念——混合渲染管线**：掌握RTX硬件加速后，自然进入混合渲染管线（Hybrid Rendering Pipeline）的设计空间：光栅化负责主要可见性判断（G-Buffer生成），光线追踪负责全局效果（软阴影、反射、全局光照），Tensor Core负责降噪与超分。这种分工的合理边界——哪些效果值得用光线追踪替换光栅化技巧——正是混合渲染管线设计的核心问题，而RT Core的吞吐量数据（如每秒支持多少条次级光线）是这一边界决策的量化依据。