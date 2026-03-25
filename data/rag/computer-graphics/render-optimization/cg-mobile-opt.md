---
id: "cg-mobile-opt"
concept: "移动端优化"
domain: "computer-graphics"
subdomain: "render-optimization"
subdomain_name: "渲染优化"
difficulty: 3
is_milestone: false
tags: ["移动端"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 44.2
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.464
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 移动端优化

## 概述

移动端优化是针对移动GPU（如ARM Mali、Qualcomm Adreno、Apple GPU）所采用的**Tile-Based Deferred Rendering（TBDR）**架构而设计的一套渲染策略。与桌面GPU的立即模式渲染（Immediate Mode Rendering）不同，移动GPU将屏幕分割为若干16×16或32×32像素的瓦片（Tile），每个Tile的颜色、深度、模板数据在芯片内部的高速片上内存（On-Chip Memory）中完成读写，仅在Tile处理完毕后才将结果写回系统内存（DRAM）。这一架构的核心目的是大幅减少带宽消耗，因为移动设备上DRAM带宽极为有限且耗电量高。

这种架构最早在20世纪90年代的Imagination Technologies PowerVR系列GPU中得到完整实现，后来被ARM Mali（Midgard架构起）和Apple自研GPU广泛采用。Qualcomm Adreno则采用了Tile-Based架构的变体。理解TBDR是移动端图形优化的前提——几乎所有移动端独有的优化技巧都源于"如何让Tile处于最高效的工作状态"这一核心问题。

## 核心原理

### Tile-Based渲染流程与Early-Z剔除

TBDR的渲染分为两个阶段：**Binning Pass**（也称Tiling Pass）将所有图元按照其覆盖的Tile分类归档，写入一张Primitive List；**Rendering Pass**则逐Tile处理，将该Tile内所有图元的片元着色在片上内存中完成。由于整个Tile的深度缓冲常驻片上，GPU可以在执行片元着色器**之前**精确地完成深度测试（即HSR，Hidden Surface Removal，PowerVR的专有术语），从而完全跳过被遮挡的片元的着色计算，实现接近理想状态的Early-Z剔除，这与桌面GPU需要程序员主动排序不透明物体才能利用Early-Z的做法存在本质差异。

### 避免Tile Flush与framebuffer加载开销

移动端最昂贵的操作之一是**打断Tile的连续渲染流程**，强制GPU将片上数据写回DRAM，即"Tile Flush"。触发Tile Flush的常见原因包括：在一个Render Pass内部读取颜色缓冲（如屏幕空间折射）、使用`glCopyTexImage2D`截取当前帧缓冲、以及多个Render Pass之间未正确配置Load/Store Action。在Vulkan和Metal API中，开发者必须显式声明`loadOp`和`storeOp`：若当前Pass不需要保留上一Pass的内容，应设置`loadOp = DONT_CARE`（Metal中对应`MTLLoadActionDontCare`）；若渲染结果不需要写回系统内存（如中间的深度缓冲），应设置`storeOp = DONT_CARE`。错误配置这两个参数会导致每帧产生数十MB的无效DRAM读写。

### 带宽优化：压缩格式与Render Target格式

移动端对纹理和Render Target的格式选择极为敏感。使用**ASTC（Adaptive Scalable Texture Compression）**格式而非未压缩RGBA8可将纹理带宽降低75%以上；ASTC支持从4×4到12×12的多种块大小，其中ASTC 4×4的压缩率为8:1，ASTC 8×8约为32:1。对于Render Target，在移动端使用`R11G11B10F`（无Alpha）或`RGB565`（LDR场景）代替`RGBA16F`可节省约25%~50%的带宽。深度缓冲在不需要采样的情况下，应始终使用`D16`（16位深度）而非`D24S8`，可将深度Tile数据量减少33%。

### 渲染Pass合并与Subpass机制

Vulkan提供了**Subpass**机制，允许在同一个Render Pass内依次完成G-Buffer写入和光照合并，其中光照Pass通过`InputAttachment`直接读取同一Tile内的G-Buffer数据，完全绕过DRAM读回。这使得延迟渲染（Deferred Rendering）在移动端也具有可行性——传统的多Pass延迟渲染会在TBDR架构上产生巨大带宽惩罚，但基于Subpass的实现可将G-Buffer带宽开销降至接近于零。Metal API中对应的机制称为**Tile Shading**（通过`MTLRenderCommandEncoder`的`setTileTexture`实现），在Apple GPU上可获得类似收益。

## 实际应用

**后处理链优化**：在移动端实现Bloom效果时，不应使用独立的多个Render Pass进行下采样和上采样，而应将相邻分辨率的处理合并为单个Pass，或使用`Compute Shader`搭配`imageStore`直接写入多个Mip层级，减少Pass切换引发的Tile Flush次数。

**阴影贴图**：移动端Shadow Map的深度缓冲在完成阴影Pass后，若后续不需要作为纹理采样（如不做PCSS），应将其`storeOp`设为`DONT_CARE`，避免将整张2048×2048的深度图（约16MB，D16格式）写回DRAM。

**粒子与半透明排序**：由于TBDR的HSR仅对不透明几何体有效，半透明物体仍需从后往前排序（或使用OIT），且半透明Pass应尽量与主不透明Pass放在同一Render Pass的不同Subpass中，而非拆分为独立Pass。

## 常见误区

**误区一：认为移动端不适合延迟渲染**。许多开发者因知道延迟渲染需要读取G-Buffer而认为其在TBDR架构上性能差。实际上，如果使用Vulkan Subpass或Metal Tile Shading将G-Buffer读取限制在片上，延迟渲染的光照累积步骤不产生DRAM访问，性能完全可以接受，Apple在其GPU最佳实践文档中明确推荐此方案。

**误区二：认为Alpha Test（`discard`）在移动端没有性能影响**。在桌面GPU上，`discard`仅影响Early-Z的有效性；而在TBDR架构上，`discard`会破坏HSR的完整性——GPU无法在Binning Pass时预知某个片元是否会被discard，因此不得不保守地绕过部分HSR优化，导致更多片元进入着色阶段。建议在移动端将Alpha Test替换为Alpha to Coverage（配合MSAA使用），或将小面积镂空改为Alpha Blend。

**误区三：盲目开启MSAA认为会增加带宽**。实际上，TBDR架构因为多重采样数据（每Tile 4x/8x samples）可以完整存储在片上内存中，MSAA的resolve操作在片上直接完成，写回DRAM的仍然是1x分辨率的结果。在Tile足够大、MSAA sample count不超过4x的情况下，移动端开启MSAA的实际带宽增量远低于桌面端，Mali和Adreno的官方文档均证实了这一点。

## 知识关联

移动端优化以**渲染优化概述**中介绍的带宽、填充率、Draw Call三大性能瓶颈为分析框架，但其具体瓶颈的成因与桌面端完全不同：移动端的带宽瓶颈主要来自Tile Flush而非场景复杂度，填充率瓶颈被HSR大幅缓解，Draw Call的CPU开销则通过Vulkan/Metal的显式API得到控制。掌握移动端优化后，可自然延伸至**GPU驱动渲染（GPU-Driven Rendering）**在TBDR架构上的适配问题，以及**可变速率着色（VRS）**在Adreno和Apple GPU上的实现差异——这两个方向都依赖对TBDR Binning Pass机制的深入认识。
