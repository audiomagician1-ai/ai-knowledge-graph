---
id: "vfx-pp-custom"
concept: "自定义后处理"
domain: "vfx"
subdomain: "post-process"
subdomain_name: "后处理特效"
difficulty: 4
is_milestone: false
tags: ["高级"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 44.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# 自定义后处理

## 概述

自定义后处理（Custom Post Processing Pass）是指在渲染管线的屏幕空间阶段，通过开发者自编写的着色器逻辑，对已完成光栅化的帧缓冲图像执行全屏变换操作。与内置后处理效果不同，自定义后处理允许开发者绕过预设参数限制，直接操控每个像素的颜色、深度或法线数据，实现引擎内置效果无法覆盖的视觉结果——例如基于自定义噪声函数的像素化溶解、非真实感渲染（NPR）的手绘描边，或逐帧累积的屏幕空间运动模糊变体。

在 Unreal Engine 5 中，自定义后处理通过两种主要方式实现：**Material 方式**使用后处理材质球（Post Process Material），将 `Blendable Location` 设置为 `Before/After Tonemapping` 等节点位置；**Compute 方式**则通过 `FScreenPassTexture` 和 `AddPass` 函数族在 C++ 渲染线程中调度 Compute Shader，以获得更精细的资源控制权。自 UE4.22 引入 Render Dependency Graph（RDG）框架后，两种方式的资源生命周期管理均需遵循 RDG 的 Pass 注册与执行模型。

掌握自定义后处理的意义在于：屏幕空间后处理的计算成本与场景复杂度完全解耦，一个全屏 Compute Pass 的开销仅取决于分辨率，而与场景中的三角面数无关。这使其成为实现高性价比视觉风格化的首选技术路径，尤其在移动端或主机平台需要固定帧率时，用后处理模拟三维效果是常见的性能优化策略。

---

## 核心原理

### Material 方式：后处理材质（Post Process Material）

创建后处理材质时，必须将材质域（Material Domain）设置为 `Post Process`，并将混合位置（Blendable Location）配置为以下五个阶段之一：`Before Translucency`、`Before Tonemapping`、`After Tonemapping`、`Replacing the Tonemapper`、`SSR Input`。选择阶段决定了材质读取到的 `SceneTexture` 是否已经过色调映射（Tonemapping），`After Tonemapping` 阶段的颜色值范围被压缩至 [0, 1]，而 `Before Tonemapping` 则保留 HDR 线性值（可超过 1.0）。

材质中使用 `SceneTexture` 节点获取屏幕图像，其 `Scene Texture Id` 参数可选择 `SceneColor`、`SceneDepth`、`GBufferA`（法线）、`GBufferB`（金属度/粗糙度）等。UV 采样使用 `ScreenPosition` 节点输出的视口 UV，偏移采样时需将像素偏移量换算为 UV 步长：`UV_offset = pixel_count / ViewportSize`，其中 `ViewportSize` 通过 `ViewProperty` 节点获取。将材质拖入 Camera 或 Post Process Volume 的 `Blendables` 数组后，引擎会自动在渲染管线对应阶段插入一个全屏 Quad Draw Call。

### Compute 方式：RDG Compute Shader

Compute 方式需要在 C++ 中声明一个继承自 `FGlobalShader` 的 Compute Shader 类，并通过 `IMPLEMENT_GLOBAL_SHADER` 宏绑定 `.usf` 文件中的 Kernel 入口函数（通常命名为 `MainCS`）。在渲染线程中，使用 `FRDGBuilder` 注册 Pass 的标准流程如下：首先调用 `GraphBuilder.CreateTexture()` 创建 `FRDGTextureRef` 输出纹理，然后声明 `FParameters` 结构体并填入 `SceneColorTexture`（`FRDGTextureSRVRef`）和 `OutputTexture`（`FRDGTextureUAVRef`），最后调用 `FComputeShaderUtils::AddPass()` 提交 Pass，传入 Dispatch 线程组数量。

线程组尺寸的选择直接影响 GPU 占用率（Occupancy）。对于全屏图像处理，常用的线程组配置为 `[numthreads(8, 8, 1)]`，总线程数 64 在大多数 GPU 架构（NVIDIA Ampere、AMD RDNA2）上能有效填满一个 Warp/Wavefront。Dispatch 数量公式为：`DispatchX = ceil(ViewportWidth / 8)`，`DispatchY = ceil(ViewportHeight / 8)`。在 `.usf` 文件中，通过 `SV_DispatchThreadID` 获取当前线程对应的像素坐标，并用 `Texture2D.SampleLevel()` 采样输入，用 `RWTexture2D[float4]` 的 `operator[]` 写入输出。

### Pass 插入位置与 Blendable Priority

无论哪种方式，多个自定义后处理 Pass 的执行顺序由 `Blendable Priority` 控制，数值越小越先执行（默认值为 0，内置 Bloom 约在优先级 100 附近）。在 C++ Compute 方式中，Pass 执行位置通过在 `FSceneRenderer` 子类的渲染函数（如 `RenderFinish` 或 `AddPostProcessingPasses`）内调用来手动指定，需要精确理解 UE 渲染管线中 `RenderVelocities → SSAO → Bloom → Tonemap → UI` 的流程顺序，错误的插入点会导致效果与预期阶段的图像数据不匹配。

---

## 实际应用

**NPR 手绘描边**：通过在 `Before Tonemapping` 阶段的后处理材质中，对 `SceneDepth` 和 `GBufferA`（世界法线）分别执行 Sobel 卷积（采样 8 个相邻像素），将深度梯度和法线梯度叠加后作为描边强度蒙版，与 SceneColor 合并。描边宽度通过调整 Sobel 采样步长（单位：像素）实时控制，无需修改场景中任何网格体。

**屏幕空间扫描线特效**：在 Compute Shader 中，根据 `SV_DispatchThreadID.y` 对 2 取模决定奇偶行，对奇数行像素亮度乘以系数 0.6，模拟 CRT 显示器的扫描线间隙。这种效果若用传统材质方式实现，需要通过 `fmod(ScreenUV.y * ScreenHeight, 2.0)` 达到相同目的，但 Compute 方式可以更直接地基于整数像素坐标判断，避免浮点精度误差导致的锯齿感。

**渐进式热浪扭曲**：结合 `Time` 节点驱动 UV 偏移，用 Noise 函数（`MF_SimpleNoise` 或自定义 FBM）生成每帧变化的扰动量，对 `SceneColor` 执行非均匀 UV 偏移采样。偏移量通常限制在 ±0.01 UV 单位（对应 1080p 下约 ±10 像素）以内，超出此范围会产生明显的纹理拉伸伪影。

---

## 常见误区

**误区一：在 After Tonemapping 阶段进行 HDR 运算**
部分开发者将需要保留高光溢出（Bloom 前）的效果错误地放置于 `After Tonemapping` 阶段。此阶段的 SceneColor 已被 ACES 或自定义 Tonemapper 压缩到 [0, 1]，对亮度超过 1.0 的光源区域进行的任何基于亮度阈值的处理（如提取高光区域）都会静默失效，因为该阶段根本不存在超出范围的亮度值。正确做法是将此类效果置于 `Before Tonemapping` 并直接操作 HDR 线性颜色值。

**误区二：Compute 方式不需要处理输入输出纹理格式**
使用 `RWTexture2D` 写入 SceneColor 时，必须确认目标纹理的像素格式（`PF_FloatRGBA` 对应 `float4`，`PF_B8G8R8A8` 对应 `unorm4`）与 UAV 声明类型完全匹配。将 HDR 浮点纹理的 UAV 声明为整数格式，在 DX12 下会触发 Validation Layer 报错，在部分移动端 GPU 上则会产生静默的颜色截断（Clamp）而非错误提示，极难排查。

**误区三：材质方式的性能开销可以忽略不计**
每个 Post Process Material 实例在对应渲染阶段都会触发一次独立的全屏 Draw Call，并强制刷新渲染状态（Render State）。在 1080p 分辨率下，一个简单的颜色校正材质的 GPU 时间约为 0.1～0.3ms，但若堆叠 10 个不同的后处理材质，累积开销可达 1～3ms，完全不可忽视。对于逻辑上可以合并的多步操作，应在单一材质中使用自定义 HLSL 节点（`Custom` 节点）串联处理，而非拆分为多个独立材质球。

---

## 知识关联

本概念建立在**镜头光晕**（Lens Flare）的基础上——镜头光晕本身就是一个后处理效果，其在 `SceneColor` 上叠加散射图案的机制揭示了后处理阶段图像合成的基本模式：读取