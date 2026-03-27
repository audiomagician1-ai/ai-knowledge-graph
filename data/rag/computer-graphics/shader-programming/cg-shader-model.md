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

Shader Model（着色器模型，简称 SM）是 Microsoft 在 DirectX 图形 API 中定义的一套规范，用于描述 GPU 可编程着色器所支持的指令集、寄存器数量、纹理采样能力及特定语言特性。每个 SM 版本本质上是硬件能力与驱动接口之间的契约：只要 GPU 声称支持某一 SM 版本，开发者就可以在 HLSL 中使用该版本所有的语法和内置函数，并保证在所有兼容硬件上行为一致。

Shader Model 的历史从 DirectX 8.0（2000年）引入 SM 1.0 开始，当时只有顶点着色器和像素着色器，且像素着色器指令数上限仅为 8 条。SM 2.0（DirectX 9.0c，2002年）将指令数提升到 96 条并引入流程控制分支；SM 3.0 增加了顶点着色器对纹理的读取能力（Vertex Texture Fetch）；SM 4.0（DirectX 10，2006年）带来了几何着色器和整型运算；SM 5.0（DirectX 11，2009年）加入计算着色器（Compute Shader）、曲面细分管线（Hull/Domain Shader）和无序访问视图（UAV）；而 SM 6.0+（DirectX 12，2015年起）则以波前操作（Wave Intrinsics）和网格着色器（Mesh Shader）重新定义了 GPU 编程范式。

理解 Shader Model 版本对于引擎开发者和技术美术都至关重要：选错 SM 版本会导致着色器在低端硬件上无法编译，或因未启用更高版本特性而造成性能浪费。Unreal Engine 5 默认要求 SM 5，而 Nanite 和 Lumen 特性则需要 SM 6.5 才能完整运行。

---

## 核心原理

### SM 5.0 的关键特性

SM 5.0 是目前使用最广泛的基准版本，对应 DirectX 11 和 NVIDIA Fermi（GTX 400 系列）、AMD GCN 第一代架构。其核心新增能力包括：

- **计算着色器（Compute Shader）**：完整支持 `RWStructuredBuffer`、`RWTexture2D` 等可读写资源，线程组大小最大为 `[numthreads(1024, 1, 1)]`（X 维最大 1024）。
- **曲面细分管线**：Hull Shader 定义控制点和细分因子（`SV_TessFactor`、`SV_InsideTessFactor`），Domain Shader 输出最终顶点位置，两者共同替代旧时 CPU 端的 LOD 策略。
- **UAV（Unordered Access View）**：像素着色器阶段最多绑定 8 个 UAV 槽位，允许对任意内存地址进行原子操作（`InterlockedAdd`、`InterlockedCompareExchange`），这是实现 OIT（顺序无关透明）算法的基础。
- **双精度浮点**：SM 5.0 开始可选支持 `double` 类型，但仅限计算着色器，像素着色器仍以 `float`（32 位）为主。

### SM 6.0–6.6 的演进路线

从 SM 6.0 起，DirectX 12 和 DXIL（基于 LLVM IR 的中间语言）取代了旧的 DXBC 字节码，这是底层编译管线的根本性变化。

| SM 版本 | 代表特性 | 典型硬件 |
|---------|---------|---------|
| 6.0 | Wave Intrinsics（`WaveActiveSum`、`WaveBallot`）| NVIDIA Pascal，AMD Polaris |
| 6.1 | SV_ViewID（多视图渲染，用于 VR）、Barycentric Semantics | NVIDIA Volta |
| 6.2 | float16 本机类型（`float16_t`）、int16_t | NVIDIA Turing 部分 |
| 6.4 | 整型点积加速（`dot4add_u8packed`，用于机器学习推理）| NVIDIA Turing，AMD RDNA |
| 6.5 | DXR 1.1（内联光线追踪，`TraceRayInline`）、Mesh Shader | NVIDIA Ampere，AMD RDNA 2 |
| 6.6 | 原生 int64 原子、采样器反馈（Sampler Feedback）| NVIDIA Ada，AMD RDNA 3 |

**Wave Intrinsics** 是 SM 6.0 最重要的创新：它将同一 warp/wavefront 内 32（NVIDIA）或 64（AMD）个线程的并行执行暴露给开发者。`WaveActiveSum(value)` 可以在一个指令周期内对整个 wave 的所有 lane 求和，在实现屏幕空间后处理、SPH 流体等算法时远比共享内存 reduce 高效。

**Mesh Shader**（SM 6.5）彻底重构了传统的 IA→VS→GS 管线，用 Amplification Shader + Mesh Shader 两个计算着色器阶段替代，允许在 GPU 上生成和裁剪三角形，每次 Mesh Shader 调用最多输出 256 个顶点和 512 个图元。

### 着色器模型与 HLSL 语言版本的对应

HLSL 语言版本（`#pragma target`）直接映射到 SM 版本。在 Unity 中：
- `#pragma target 5.0` → SM 5.0，支持 Compute Shader 和 Tessellation
- `#pragma target 6.5` → SM 6.5，支持 Mesh Shader 和内联光线追踪

在 HLSL 编译器（DXC）中使用 `-T cs_6_6` 这样的 profile 字符串指定目标着色器阶段和 SM 版本，其中 `cs` 表示 Compute Shader，`vs`/`ps`/`ms` 分别对应顶点/像素/网格着色器。

---

## 实际应用

**粒子系统与 GPU Culling（SM 5.0 Compute Shader）**：现代引擎的 GPU 粒子系统通过 Compute Shader 在 GPU 端完成粒子更新和死亡剔除，利用 `RWStructuredBuffer<Particle>` 和 `AppendStructuredBuffer` 动态管理粒子池，整个过程零 CPU 读回，依赖 SM 5.0 的 UAV 原子操作。

**VR 单通道立体渲染（SM 6.1 SV_ViewID）**：通过 `SV_ViewID` 语义，单次 Draw Call 可同时输出左眼和右眼的裁剪空间变换结果，GPU 驱动程序自动将输出路由到 Texture2DArray 的两个 slice，相比旧的双 Draw Call 方案减少约 40% 的驱动开销。

**Nanite 虚拟几何（SM 6.5 Mesh Shader）**：Unreal Engine 5 的 Nanite 系统在最终光栅化阶段使用 Mesh Shader，每个 Mesh Shader threadgroup 处理一个 Nanite cluster（128 个三角形），通过 Amplification Shader 的 `DispatchMesh()` 调用动态决定哪些 cluster 需要光栅化，从而实现 GPU 端的 cluster-level 可见性剔除。

---

## 常见误区

**误区一：认为 SM 版本越高性能一定越好**
SM 6.0 的 Wave Intrinsics 在某些架构上（如 AMD GCN 早期型号模拟 Wave64）实际上需要更多的寄存器压力，导致 occupancy 下降。使用 `WaveGetLaneCount()` 查询实际 wave 宽度并做条件分支是正确做法，盲目使用高 SM 特性并不总能提升性能。

**误区二：混淆 OpenGL GLSL 版本与 SM 版本**
GLSL 4.50 在功能上大致对应 SM 5.0，GLSL 4.60 对应部分 SM 6.x 特性（如多视图扩展 `GL_OVR_multiview`），但二者并非严格对应关系。WebGL 2.0 基于 OpenGL ES 3.0，其着色语言能力仅约等于 SM 4.0 子集——在 Web 环境中无法使用 Compute Shader（需要 WebGPU）。

**误区三：认为标注 SM 6.x 的 GPU 支持所有 6.x 子特性**
SM 6.x 的各子版本是可选的硬件能力集（Optional Feature），例如 SM 6.4 的 `dot4add` 指令在 Intel Gen11 上不可用（尽管驱动声称 SM 6.0 支持）。正确做法是通过 `CheckFeatureSupport(D3D12_FEATURE_D3D12_OPTIONS1)` 等 API 在运行时逐项查询，而非只检查最高 SM 版本号。

---

## 知识关联

**前置概念**：Shader 概述中介绍的顶点着色器/片元着色器概念，是理解 SM 版本引入新管线阶段（曲面细分、几何着色器、网格着色器）价值的基础——每个新增管线阶段都扩展了可编程点的范围。寄存器类型（`t`/`u`/`s`/`b` 寄存器槽位）的数量上限也随 SM 版本增加，SM 5.0 中每个着色阶段的 SRV 槽位从 SM 4.0 的 128 个增至 无限（实际受硬件描述符堆限制）。

**横向联系**：Vulkan 的 SPIR-V 和 Metal 的 MSL 均有自己的特性分层机制，但业界通常以