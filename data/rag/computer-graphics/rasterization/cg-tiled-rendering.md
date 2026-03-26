---
id: "cg-tiled-rendering"
concept: "分块渲染"
domain: "computer-graphics"
subdomain: "rasterization"
subdomain_name: "光栅化"
difficulty: 3
is_milestone: false
tags: ["移动端"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.1
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


# 分块渲染

## 概述

分块渲染（Tile-Based Rendering，TBR）是一种将屏幕划分为若干小矩形区域（Tile），逐块完成光栅化和着色计算的渲染架构。与立即模式渲染（Immediate Mode Rendering，IMR）不同，TBR 在正式执行像素着色之前，先收集一帧内所有的几何变换结果，再按 Tile 分批处理，从而大幅减少对外部 DRAM 的访问频次。这一特性使得分块渲染成为移动端 GPU（如 ARM Mali、Qualcomm Adreno、Apple GPU）的主流架构基础。

分块渲染的思想最早可追溯至1990年代的 SGI 视频游戏芯片研究，但真正推动其大规模落地的是移动设备对功耗的严苛要求。2000年代初期，PowerVR 系列 GPU 以 TBDR（Tile-Based Deferred Rendering）形式将其商业化。每个 Tile 的典型尺寸为 16×16 或 32×32 像素，GPU 为每个 Tile 在芯片内部分配一块高速 On-Chip Buffer，所有读写操作优先在此缓冲区内完成，仅在 Tile 渲染完毕后才将结果刷写到主存 Framebuffer。

分块渲染之所以在移动端具有无可替代的地位，核心在于 DRAM 访问的能耗极高——在 28nm 工艺下，一次 DRAM 读写消耗的能量约是片上寄存器访问的 200 倍。TBR 将深度测试、混合等操作限制在 On-Chip Buffer 内完成，可将 DRAM 带宽需求降低 50%–80%，直接决定了设备的续航表现与发热水平。

---

## 核心原理

### Tile 分块几何处理流程

分块渲染将渲染管线拆分为两个独立阶段。**第一阶段（Geometry Pass）**：GPU 执行顶点着色器，将所有图元（三角形）变换至裁剪空间，并通过 Binning 操作（又称 Tiling Pass）计算每个三角形覆盖哪些 Tile，将三角形索引写入对应 Tile 的显存命令列表（Parameter Buffer）。**第二阶段（Rendering Pass）**：GPU 逐 Tile 调度，将该 Tile 对应的几何数据读入 On-Chip Buffer，在片上完成光栅化、深度测试、像素着色和混合，最后一次性写出到主存。整个过程的 DRAM 写入次数理论上等于像素总数，而非操作次数。

### HSR 与 TBDR 的隐藏面消除

PowerVR 的 TBDR 在第二阶段引入了 **Hidden Surface Removal（HSR）** 机制：在执行像素着色器之前，GPU 先对 Tile 内所有可见像素进行深度排序，只对最终可见的像素点调用一次片元着色器。这与传统 Early-Z 不同——Early-Z 依赖绘制顺序，而 HSR 不依赖 Draw Call 顺序，保证了每个屏幕像素的像素着色器调用次数严格等于 1（不透明物体场景下）。这意味着即使场景 Overdraw 比率达到 5× ，实际着色开销也与 1× 相同，这是 IMR 架构无法做到的。

### On-Chip Buffer 与 Bandwidth 节省的量化关系

设屏幕分辨率为 W×H，颜色深度 32 bit，深度+模板缓冲 32 bit，帧率 60 fps，则 IMR 在最坏情况（多次 Overdraw）下 DRAM 带宽需求为：

> **BW_IMR = W × H × (ColorBytes + DepthBytes) × Overdraw × FPS**

而 TBR 中深度缓冲完全驻留在 On-Chip Buffer，不参与 DRAM 读写，DRAM 写入仅为最终颜色输出：

> **BW_TBR ≈ W × H × ColorBytes × FPS**

以 1080p 60fps、4× Overdraw 为例，IMR 需要约 **3.96 GB/s** 的深度缓冲带宽，TBR 将其降至接近 **0**，仅保留约 **0.495 GB/s** 的颜色写出带宽。

---

## 实际应用

### Vulkan/Metal 中的 Render Pass 设计

Vulkan 的 `VkSubpassDependency` 和 Metal 的 `MTLRenderPassDescriptor` 中的 `loadAction`/`storeAction` 参数，正是为分块渲染架构量身设计的接口。将 `loadAction` 设为 `clear` 而非 `load`，将 `storeAction` 设为 `dontCare` 而非 `store`，可避免 TBR 在 Tile 开始时从 DRAM 加载旧数据，在 Tile 结束时不必要地写回临时缓冲。在 Metal 文档中明确指出，错误使用 `load/store` 会导致移动端 GPU 产生 **Resolve** 操作，引入额外 DRAM 带宽开销，这是移动端渲染优化中最常见的性能陷阱之一。

### Subpass 与 G-Buffer 的 Tile-Local 延迟渲染

在 Vulkan 的 Subpass 机制中，可以将延迟渲染的 G-Buffer（法线、反射率、深度）声明为 `transientAttachment`，使其完全驻留在 On-Chip Buffer，不写入主存 DRAM。第一个 Subpass 写入 G-Buffer，第二个 Subpass 直接读取同一 Tile 的 G-Buffer 数据进行光照计算，整个 G-Buffer 的生命周期不超出单个 Tile 的处理范围。这种方式在 Arm Mali GPU 上可节省高达 **3–4倍** 的 DRAM 带宽（相比朴素延迟渲染），是 Android 平台上实现延迟光照的标准做法。

---

## 常见误区

**误区一：认为分块渲染只是移动端的优化技巧，桌面端无关紧要。**  
实际上 Apple 的 M1/M2/M3 系列芯片同样采用 TBDR 架构，其 Metal API 在 macOS 上同样需要正确设置 `loadAction`/`storeAction`。随着 Apple Silicon 统一内存架构的普及，分块渲染的设计思路正向桌面级应用蔓延。

**误区二：认为 HSR 可以完全替代手动排序半透明物体。**  
HSR 仅对不透明（Opaque）渲染状态生效，一旦像素着色器中启用了 Alpha Blending 或 Alpha Test（`discard` 指令），GPU 无法提前确定可见性，必须退出 HSR 流程，按提交顺序着色。因此在 PowerVR 设备上，半透明物体仍须严格按照从后到前的顺序提交，否则会产生错误的混合结果。

**误区三：Tile 尺寸越大越好。**  
Tile 尺寸受到片上 SRAM 容量的硬性限制。若将 Tile 从 16×16 扩大到 32×32，On-Chip Buffer 需求增加 4 倍，超出 SRAM 容量后 GPU 将被迫将 Tile 数据溢出到 DRAM，完全抵消分块渲染的带宽优势，甚至因为额外的 Spill 操作性能倒退。

---

## 知识关联

**与延迟渲染的关系**：经典延迟渲染（Deferred Shading）在 IMR 架构上会产生巨大的 G-Buffer DRAM 带宽压力（一帧读写 G-Buffer 通常需要 10–20 GB/s），而 TBDR 通过 Subpass/Tile-Local 机制将 G-Buffer 限制在片上，使得延迟渲染在移动端变得可行。两者的结合体 TBDR 并非简单叠加，而是在架构层面重新设计了 G-Buffer 的生命周期管理。

**与光栅化管线的关系**：分块渲染并未改变光栅化的数学本质（重心坐标插值、深度计算公式），而是重构了数据在内存层次中的流动路径——将深度测试和颜色混合从 DRAM 访问变为 SRAM 访问，这一改变发生在光栅化管线的后端（ROP 阶段），对应用层的顶点/片元着色器编写逻辑影响有限，但对 Render Pass 结构设计影响深远。