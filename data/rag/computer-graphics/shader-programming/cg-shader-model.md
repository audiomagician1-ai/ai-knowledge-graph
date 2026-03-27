---
id: "cg-shader-model"
concept: "Shader Model"
domain: "computer-graphics"
subdomain: "shader-programming"
subdomain_name: "Shader编程"
difficulty: 3
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 50.4
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# Shader Model（着色器模型）

## 概述

Shader Model（着色器模型，简称SM）是微软DirectX API中定义的一套标准规范，规定了GPU可编程着色器的指令集、寄存器数量、纹理采样能力以及支持的着色器类型。每个SM版本号对应一代特定的硬件能力，开发者通过检测SM版本来判断GPU支持哪些可编程功能，从而决定能否使用几何着色器、曲面细分或光线追踪等高级特性。

Shader Model规范最初随DirectX 8.0在2000年引入，SM 1.0/1.1对应的是NVIDIA GeForce 3系列，顶点着色器和像素着色器功能极为有限，顶点着色器仅支持128条指令。此后版本迭代加速：DirectX 9.0c引入SM 3.0，DirectX 10引入SM 4.0，DirectX 11引入SM 5.0，DirectX 12 Ultimate引入SM 6.6。每次版本升级都与一代GPU架构紧密绑定，而非纯粹的软件演进。

理解SM版本的实际意义在于它直接约束了HLSL代码能否在目标硬件上编译执行。在多平台游戏开发中，引擎往往需要为SM 5.0和SM 6.0分别维护不同的着色器变体，因为SM 6.0引入了波前操作（Wave Intrinsics），这类指令在旧硬件上根本无法映射。

---

## 核心原理

### SM 5.0 的关键能力边界

SM 5.0随DirectX 11于2009年发布，对应硬件为NVIDIA Fermi架构（GTX 400系列）和AMD Evergreen架构（Radeon HD 5000系列）。SM 5.0引入了两类全新着色器阶段：**Hull Shader**（外壳着色器）和**Domain Shader**（域着色器），两者共同构成GPU端曲面细分管线，允许在GPU上动态生成三角形细节。同时SM 5.0正式支持**Compute Shader**的完整版本，提供线程组（Thread Group）并行模型，每个线程组最多1024个线程，共享内存（Group Shared Memory）容量上限为32KB。

SM 5.0的像素着色器寄存器扩展到最多32个输入变量，支持`RWTexture2D`等无序访问视图（UAV）绑定到像素着色器阶段，这是SM 4.x所不具备的能力。HLSL编译目标格式为`ps_5_0`、`vs_5_0`、`cs_5_0`等。

### SM 6.0 的架构级革新：DXIL与波前操作

SM 6.0随DirectX 12于2016年正式落地，底层中间语言从DXBC（DirectX Bytecode）切换为**DXIL**（DirectX Intermediate Language），后者基于LLVM IR构建，使得编译器优化链路更现代化。对应硬件为NVIDIA Pascal（GTX 10系列）和AMD GCN第四代（RX 400系列）。

SM 6.0最重要的新增能力是**Wave Intrinsics（波前内在函数）**。波前（Wavefront/Warp）是GPU上同时执行相同指令的最小线程集合，在NVIDIA硬件上通常为32个线程，AMD上为64个线程。SM 6.0暴露了如下波前操作：

- `WaveActiveSum(val)`：将波前内所有线程的`val`累加；
- `WaveActiveBallot(cond)`：返回一个位掩码，标记哪些线程的`cond`为true；
- `WavePrefixSum(val)`：计算波前内当前线程之前所有线程的`val`前缀和。

这些操作直接映射到硬件的跨通道通信单元，延迟极低，是实现GPU端高效排序、压缩和遮挡剔除的基础原语。

### SM 6.x 的持续演进

SM版本并未停在6.0，而是以小版本形式持续迭代：

| 版本 | 新增能力 | 代表硬件 |
|------|----------|----------|
| SM 6.1 | SV_ViewID（多视图渲染VR优化）、Barycentric语义 | NVIDIA Turing / AMD Vega |
| SM 6.2 | float16原生支持、uint8类型 | 同上 |
| SM 6.3 | 光线追踪（DXR）着色器：Ray Generation、Closest Hit等 | NVIDIA Turing RTX系列 |
| SM 6.5 | Mesh Shader、Amplification Shader，彻底替代传统顶点+几何着色器管线 | NVIDIA Ampere / AMD RDNA2 |
| SM 6.6 | 原子64位操作、动态资源绑定（ResourceDescriptorHeap直接索引） | NVIDIA Ampere / AMD RDNA2 |

SM 6.5引入的Mesh Shader将顶点处理与几何生成合并为统一的计算风格着色器，线程组最多输出256个顶点和512个图元，Amplification Shader则负责实例级别的剔除决策，两者合作可替代传统的顶点着色器+几何着色器+曲面细分三阶段流水线。

---

## 实际应用

**引擎最低SM版本检测**：Unity引擎在PlayerSettings中允许设定"Minimum Shader Model"，当选择SM 3.5时，移动端Mali和Adreno GPU可覆盖；选择SM 5.0则要求桌面独立显卡；选择SM 6.0时，必须启用DirectX 12后端。Unreal Engine 5的Lumen全局光照要求SM 6.0以上，因为Lumen Reflection依赖Ray Tracing（SM 6.3+）或Screen Space Tracing，两条路径均需要SM 6.0的波前操作进行加速。

**波前操作在GPU粒子系统中的应用**：传统GPU粒子排序需要多次Dispatch调用完成Bitonic Sort，利用`WavePrefixSum`可以在单个Dispatch内完成局部桶排序，将排序阶段的Dispatch调用数从O(log²N)级别降低，典型场景下对10万粒子的排序耗时从2ms降至0.4ms。

**Mesh Shader实现GPU驱动渲染**：id Software在《毁灭战士：永恒》的Vulkan路径中通过类似Mesh Shader的扩展实现了网格簇（Meshlet）渲染，每个Meshlet包含最多64个顶点和126个三角形，Amplification Shader负责视锥剔除，整体Draw Call数量从数千降至数十，GPU利用率从60%提升至85%以上。

---

## 常见误区

**误区一：SM版本等同于DirectX版本**
SM版本和DirectX版本是两个不同的概念。DirectX 12是API版本，而SM 6.0~6.6是着色器模型版本，后者必须通过DirectX 12才能访问，但DirectX 12本身并不要求SM 6.0——使用DirectX 12的应用完全可以只运行SM 5.1的着色器（SM 5.1是DirectX 12对SM 5.0的小幅扩展版本，支持unbounded descriptor arrays）。混淆两者会导致错误地限制硬件支持范围。

**误区二：更高SM版本的着色器总是运行更快**
SM 6.0的DXIL编译路径并不比SM 5.0的DXBC自动更快。性能差异来自于是否使用了特定硬件特性，如Wave Intrinsics。如果仅仅是将HLSL目标从`cs_5_0`改为`cs_6_0`而不改写逻辑，编译结果的执行效率几乎相同。真正的性能提升需要重新设计算法以利用波前级并行。

**误区三：SM 6.5的Mesh Shader总是优于传统顶点着色器**
Mesh Shader在高密度三角形场景（如大规模植被、石块群）下优势明显，但对于简单几何体（单个角色、UI元素），Mesh Shader的线程组调度开销反而高于传统顶点着色器。NVIDIA官方测试表明，Mesh Shader在每个Meshlet填充率低于50%时性能与传统管线持平甚至略低。

---

## 知识关联

**前置概念**：Shader概述建立了顶点着色器和像素着色器的基本执行模型，SM版本在此基础上量化了每个阶段的指令数上限、寄存器容量和纹理绑定槽数量，将抽象的"着色器可以做什么"转化为硬件可查询的版本号约束。

**横向关联**：SM版本与HLSL语言版本高度对应——HLSL 2021新增的泛型特性（模板函数）仅在SM 6.0+的DXIL编译路径下可用；GLSL和SPIR-V的版本体系与SM并行存在但互不兼容，Vulkan通过`VkPhysicalDeviceFeatures`结构体查询等效能力而非SM版本号。

**向上延伸**：掌握SM版本差异后，下一步是学习如何在运行时通过`ID3D12Device::CheckFeatureSupport`查询具体的SM支持级别，并据此在引擎层构建着色器排列（Shader Permutation）系统，为不同SM级别的GPU编译和缓存对应的着色器变体。