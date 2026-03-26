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

分块渲染（Tile-Based Rendering，TBR）是一种将屏幕划分为若干小矩形区域（称为"块"或"Tile"），逐块完成光栅化和着色计算的渲染架构。与传统的立即模式渲染（Immediate Mode Rendering，IMR）不同，TBR 不会在绘制每个图元时立即写回主内存，而是先将整帧的几何变换结果缓存，再逐 Tile 处理，从而大幅减少对外部 DRAM 的带宽需求。

这一架构最早由 Imagination Technologies 在 1990 年代中期随 PowerVR 系列 GPU 推广商用，随后 ARM 的 Mali 和高通的 Adreno GPU 也相继采用了 Tile-Based 或其变种架构。其诞生的直接驱动力是移动设备的功耗约束：在智能手机上，访问外部 DRAM 的能耗约为片上 SRAM 的 10 至 100 倍，而分块渲染通过将每个 Tile 的颜色缓冲与深度缓冲完全放入 GPU 的片上缓存（On-Chip Memory）来规避这一开销。

分块渲染之所以在移动端图形中占据主导地位，是因为它天然契合了移动 GPU 面积小、外部带宽贵、电池容量有限的硬件现实。理解 TBR 的工作原理，对于优化 iOS（使用 Apple GPU）和 Android（Mali、Adreno、PowerVR）应用的帧率与电量消耗至关重要。

---

## 核心原理

### 两阶段流水线

分块渲染将整个渲染管线分为两个明确的阶段。**第一阶段**是几何处理阶段（Binning Pass / Tiling Pass）：GPU 对场景中所有图元执行顶点着色器，计算每个三角形落在哪些 Tile 上，并将结果写入一张称为"Tile List"的数据结构，存储在主内存中。**第二阶段**是光栅化着色阶段（Rendering Pass）：GPU 逐 Tile 读取该 Tile 的 Tile List，将颜色缓冲、深度缓冲、模板缓冲全部加载到片上内存，完成光栅化、像素着色、混合等操作，最后仅将最终颜色结果写回主内存。整帧深度缓冲从不需要写入 DRAM，这是带宽节省的关键所在。

### Tile 尺寸与片上内存

典型 Tile 尺寸为 **16×16 像素**或 **32×32 像素**，具体数值因 GPU 型号而异（例如 Apple A 系列 GPU 使用 32×32 像素的 Tile，Mali G 系列常见 16×16）。以 1920×1080 分辨率、32×32 Tile 为例，屏幕被划分为 60×34 = 2040 个 Tile。每个 Tile 需要在片上存储 RGBA 颜色（4 字节/像素）+ 深度/模板（4 字节/像素），32×32 Tile 约需 8 KB 片上空间，而现代移动 GPU 片上缓存通常为 256 KB 至几 MB，可同时容纳多个 Tile 并行处理。

### TBDR：延迟渲染的融合

**Tile-Based Deferred Rendering（TBDR）**是 PowerVR 首创并由 Apple GPU 采用的进一步优化。在片上光栅化阶段，TBDR 通过**隐藏面消除（Hidden Surface Removal，HSR）**在像素着色之前完成可见性判断：GPU 先对所有图元进行光栅化并确定每像素的最终可见图元，**仅对可见像素执行一次片段着色器调用**，彻底消除了 Overdraw 的着色开销。这与传统延迟渲染（Deferred Rendering）需要额外 G-Buffer 的方案不同——TBDR 在 Tile 粒度内直接实现了零 Overdraw，无需 G-Buffer 即可达到类似效果。传统 IMR 架构做不到这一点，因为它的逐图元即时写入无法在不增加大量状态的情况下推迟着色。

---

## 实际应用

### 正确使用 Render Pass 的 Load/Store Action

在 Metal（iOS）和 Vulkan（Android）API 中，开发者可以显式控制 Tile 的加载和存储行为。将 Render Pass 的 `loadAction` 设置为 `clear`（而非 `load`）、`storeAction` 设置为 `dontCare`（对不需要保留的深度缓冲），可以避免 GPU 从 DRAM 读取或写入该缓冲，直接节省带宽。若一帧中深度缓冲在后续 Pass 中不再使用，将其 Store Action 设为 `dontCare` 可节省整帧的深度写回带宽，在 1080p 下约节省 4 MB/帧的 DRAM 写入。

### Subpass 与 Tile Memory 直接访问

Vulkan 的 **Subpass** 机制和 Metal 的 **Tile Shading** 特性允许在同一 Render Pass 的不同子阶段之间，通过片上内存直接传递数据，无需写回并重新读取 DRAM。这在移动端实现延迟光照（Deferred Lighting）时尤其有价值：G-Buffer 数据写入片上后，光照 Pass 直接从片上读取，整个 G-Buffer 从不触碰 DRAM。相比桌面端必须将 G-Buffer 写入多张 Render Target 然后再读取，移动端 TBDR 使用 Subpass 可将延迟渲染的带宽开销降低 60% 至 80%。

### 避免打断 Tile 流水线的操作

某些操作会强制 GPU 刷新（Flush）当前 Tile 到主内存，从而破坏 TBR 的带宽优势，包括：在同一帧内读回帧缓冲内容（`glReadPixels`）、使用 `glCopyTexImage2D` 从当前绑定的帧缓冲拷贝纹理、在 Render Pass 中途切换帧缓冲等。这类操作在 ARM Mali GPU 上会触发所谓的 **"Flush"**，导致性能突降，Mali Graphics Debugger 可以检测到这一现象并标记为"External Read"。

---

## 常见误区

**误区一：认为分块渲染只是移动端的"阉割版"渲染**。事实恰恰相反，TBDR 的 HSR 技术实现了真正意义上的零 Overdraw 着色，这是桌面 IMR 架构在不引入额外复杂度的情况下无法实现的。Apple M 系列芯片（用于 Mac 和 iPad）同样采用 TBDR 架构，并用于运行高负载的桌面级图形应用。将 TBR 与"低性能"画等号是对架构本质的误解。

**误区二：认为 Overdraw 在 TBDR 上没有任何开销**。TBDR 的 HSR 消除的是**像素着色阶段**的 Overdraw，但几何处理阶段（第一阶段）仍需对所有图元执行顶点着色器。若场景中存在大量被遮挡的复杂网格，其顶点计算开销在 TBDR 上同样存在。此外，Alpha 测试（`discard` 指令）和 Alpha 混合操作会破坏 HSR 的可见性推断，导致 TBDR 无法延迟这些像素的着色，从而退化为类 IMR 行为。

**误区三：直接将桌面端延迟渲染管线移植到移动端会自动获益**。若开发者不使用 Vulkan Subpass 或 Metal Tile Shading，而是用多个独立 Render Pass 实现 G-Buffer，则 G-Buffer 数据必须写回并重新读取 DRAM，完全丧失了 TBDR 片上内存的优势，实际带宽开销甚至高于原生前向渲染。

---

## 知识关联

分块渲染建立在**延迟渲染**的概念之上，但两者的实现层次不同：传统延迟渲染是软件层面的多 Pass 策略，而 TBDR 是硬件层面的片上调度机制。理解延迟渲染中 G-Buffer 的设计目的，有助于领会 TBDR 为何能在片上直接替代 G-Buffer 的 DRAM 往返。

在 API 层面，分块渲染的优化与 **Vulkan Render Pass / Subpass** 和 **Metal Render Pass Descriptor** 的设计哲学深度绑定——这两套 API 之所以要求开发者显式声明 Load/Store Action，正是为了让驱动程序能够利用 TBR 硬件特性。对于希望进入移动图形优化领域的开发者，理解 TBR 是读懂 ARM 的《Mali GPU Best Practices》和 Apple 的《Metal Performance Best Practices》文档的前提基础。