---
id: "render-graph"
concept: "渲染图(RDG)"
domain: "game-engine"
subdomain: "rendering-pipeline"
subdomain_name: "渲染管线"
difficulty: 3
is_milestone: false
tags: ["架构"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 41.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.414
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 渲染图（RDG）

## 概述

渲染图（Render Dependency Graph，简称 RDG）是现代游戏引擎中用于描述一帧渲染工作流的有向无环图（DAG）结构。每个图节点代表一个渲染通道（Render Pass），每条有向边代表通道之间的资源依赖关系，例如某个通道写入的纹理必须在另一个通道读取之前完成。RDG 的核心价值在于将"渲染工作的声明"与"渲染工作的执行"解耦，引擎代码只需声明每个通道需要读写哪些资源，调度系统负责自动推导执行顺序与资源生命周期。

RDG 概念在 2017 年 GDC 上由 Frostbite 引擎团队（DICE）以"FrameGraph"形式正式提出，之后 Unreal Engine 4.22 在 2019 年引入了自己的 RDG 实现，Epic Games 将其命名为 `FRDGBuilder`。同年，业界多款 AAA 引擎纷纷跟进类似架构，包括 id Software 在《毁灭战士：永恒》中使用的帧图系统。

RDG 解决的根本问题是手工管理 GPU 资源屏障（Resource Barrier）的复杂性。在没有 RDG 的传统渲染管线中，程序员必须手动插入 `D3D12_RESOURCE_BARRIER` 或 Vulkan 的 `vkCmdPipelineBarrier`，一旦遗漏或顺序错误便导致渲染错误或 GPU 崩溃。RDG 通过图拓扑自动生成这些屏障，并在此基础上进行资源别名（Aliasing）和通道裁剪（Pass Culling）优化。

## 核心原理

### 有向无环图的构建

RDG 在每帧开始时由 CPU 侧代码构建。开发者通过 `AddPass` 接口注册渲染通道，每个通道声明其输入资源（`SRV/CBV/TexRead`）和输出资源（`RTV/UAV/TexWrite`）。系统将这些读写声明转换为图边：若通道 B 读取通道 A 写入的资源 `GBuffer_A`，则图中存在边 A→B，表示 B 依赖 A。整个帧的渲染意图由此形成一张 DAG，Unreal Engine 的 RDG 在 `FRDGBuilder::Compile()` 阶段对该图进行拓扑排序，生成线性执行序列。

### 通道裁剪与资源别名

拓扑排序完成后，RDG 对图执行**反向可达性分析**：从最终输出（通常是 `FRDGTextureRef` 对应的 Swapchain 纹理）出发向后遍历，凡是不影响最终输出的通道标记为"已裁剪（Culled）"，不会提交给 GPU，这一机制在延迟渲染中可跳过大量条件性调试通道，节省 0.5–2ms 的 GPU 时间。

资源别名利用**资源生命周期不重叠**的事实，允许两个 RDG 资源在物理内存上共用同一块分配。以 Unreal Engine 为例，`FRDGAllocator` 在 `Execute()` 阶段扫描每个虚拟资源的首次写入通道和最终读取通道，若两个资源的活跃区间不相交，则它们共享同一 `D3D12Heap` 或 Vulkan `VkDeviceMemory`，典型场景下可节省帧缓冲区总内存的 30%–40%。

### 自动屏障推导

RDG 在图执行前遍历每条边，根据两端通道对资源的访问类型（读/写）及管线阶段（Pixel Shader / Compute / Copy），自动插入最小必要的资源状态转换。例如，GBuffer 写入阶段资源状态为 `D3D12_RESOURCE_STATE_RENDER_TARGET`，当 Deferred Lighting 通道读取它时，RDG 自动插入转换至 `D3D12_RESOURCE_STATE_PIXEL_SHADER_RESOURCE` 的屏障，并尽量将屏障批处理到单次 `ResourceBarrier` 调用以减少 CPU-GPU 通信开销。

### 异步计算调度

RDG 支持将标记为 `AsyncCompute` 的通道提交至 GPU 的异步计算队列（Async Compute Queue）。系统通过图中的同步信号（Fence/Semaphore）节点保证图形队列与计算队列之间的依赖，例如 SSAO 计算可与后续阴影图生成并行执行，在 PlayStation 5 和 Xbox Series X 上这一重叠策略可带来约 15%–20% 的帧时间压缩。

## 实际应用

**延迟渲染管线**：在标准延迟渲染中，GBuffer 通道、Deferred Lighting 通道、后处理通道形成一条线性依赖链。使用 RDG 后，开发者无需手工管理 GBuffer 各分量（Albedo、Normal、Roughness 纹理）的状态转换，仅需在 Lighting 通道的 `PassParameters` 结构中声明 `RDGTextureSRV(GBufferA)` 即可，Unreal Engine 的 `FDeferredShadingSceneRenderer` 完全基于此模式实现。

**Temporal AA（TAA）资源管理**：TAA 需要访问当前帧和上一帧的颜色缓冲。RDG 通过 `FRDGTextureRef` 的 `ExternalTexture` 接口将跨帧持久化纹理（Persistent Texture）纳入图中管理，既能参与屏障推导，又不受单帧生命周期限制，解决了历史帧资源状态不一致导致的"闪烁"问题。

**移动端瓦片渲染优化**：在 Arm Mali 和 Apple A 系列 GPU 上，RDG 可识别写后立即读的纹理访问模式，将其优化为 Metal 的 `Memoryless Attachment` 或 Vulkan 的 `TRANSIENT_ATTACHMENT`，使数据留在 GPU 瓦片缓存中而不写入主存，节省带宽最高达 50%。

## 常见误区

**误区一：RDG 会消除所有 GPU 同步开销。** RDG 只能优化*帧内*资源依赖，对于跨帧资源（如 TAA 历史帧纹理、流式加载的纹理）仍需开发者手动管理同步点。若将持久资源错误地以普通 `CreateTexture` 而非 `RegisterExternalTexture` 纳入 RDG，RDG 无法感知其帧间状态，可能在错误的初始状态上插入屏障，产生验证层报错甚至 GPU 挂起。

**误区二：通道裁剪会自动优化所有冗余工作。** Pass Culling 仅裁剪那些输出资源未被任何未裁剪通道消费的通道。如果某个调试可视化通道的输出被错误地注册为帧的最终输出之一，它将永远不会被裁剪，即便该可视化功能已在运行时关闭。正确做法是用条件判断阻止将该通道加入图，而非依赖 RDG 的裁剪逻辑。

**误区三：RDG 资源生命周期等同于 C++ 对象生命周期。** `FRDGTextureRef` 是一个轻量句柄，其指向的物理 GPU 内存在 `FRDGBuilder::Execute()` 之前根本未分配。若在 `AddPass` 的 Lambda 外部（即编译阶段）尝试访问纹理实际数据，将访问空指针，这是 Unreal Engine RDG 迁移过程中最常见的崩溃原因之一。

## 知识关联

RDG 以 GPU 驱动渲染（GPU-Driven Rendering）为前提知识：理解 GPU 命令缓冲（Command Buffer）的录制与提交机制、资源状态机（Resource State Machine）以及同步原语（Barrier/Fence），是读懂 RDG 自动屏障推导逻辑的必要基础。具体而言，Vulkan 的 `VkImageLayout` 状态转换规则和 D3D12 的 `D3D12_RESOURCE_STATES` 枚举直接对应 RDG 内部的资源状态追踪表。

掌握 RDG 之后，自然引出 **GPU 性能分析**这一后续主题：RDG 的通道结构天然对应 GPU 性能捕获工具（如 RenderDoc 的 Event Tree、PIX 的 Timing Captures）中的事件层级，每个 RDG 通道在工具中表现为一个独立的 Marker 区段。理解 RDG 如何调度通道、何时插入屏障、哪些通道并行执行，是解读 GPU 时间线（Timeline View）和定位性能瓶颈的直接依据。
