---
id: "cg-mobile-gpu"
concept: "移动端GPU"
domain: "computer-graphics"
subdomain: "gpu-architecture"
subdomain_name: "GPU架构"
difficulty: 3
is_milestone: false
tags: ["移动端"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# 移动端GPU

## 概述

移动端GPU是专为智能手机、平板电脑等电池供电设备设计的图形处理器，其核心设计约束是在严格的功耗限制（通常TDP不超过3-5瓦）下提供可用的图形性能。与桌面GPU动辄200-400瓦的功耗预算不同，移动端GPU必须在热设计功耗极低的条件下运行，这直接催生了与桌面GPU截然不同的架构思路。

移动端GPU的主流架构方向——Tile-Based Deferred Rendering（TBDR）——最早由Imagination Technologies在PowerVR系列中系统性实现，随后ARM的Mali系列和高通的Adreno系列也各自发展出类似的Tile-Based Rendering（TBR）变体。Mali架构在2006年随ARM Mali-55首次商用，Adreno则起源于AMD收购ATI后剥离给高通的移动图形技术，Adreno这个名字本身即是"Radeon"的字母重组。

移动端GPU的Tile-Based架构之所以重要，是因为它从根本上改变了带宽消耗模式。移动设备不存在独立的GDDR显存，GPU直接使用共享的LPDDR内存，带宽既昂贵又耗电——每次访问外部内存都会消耗可观的能量。TBDR/TBR通过将渲染工作分解为小块（Tile）在片上SRAM中完成，将绝大多数像素级读写操作限制在芯片内部，从而大幅降低外部内存带宽需求。

## 核心原理

### Tile分块与片上缓存机制

TBDR架构将屏幕划分为若干固定大小的矩形Tile，Mali和Adreno的典型Tile尺寸为16×16像素或32×32像素。渲染流程分为两个阶段：第一阶段（Binning Pass / Geometry Pass）遍历所有几何体，记录每个Tile包含哪些图元；第二阶段（Rendering Pass）逐Tile将对应几何体和像素着色完整执行，结果写入Tile Buffer。

Tile Buffer是位于GPU芯片内部的高速SRAM，容量通常在256KB到数MB之间。当一个Tile的所有像素计算完毕后，最终颜色、深度值才被写回到主内存的帧缓冲区（Resolve操作）。如果Tile Buffer足够容纳颜色+深度+模板的全部数据，整个Tile的中间过程完全不访问外部内存，带宽节省效果显著。

以Mali-G710为例，其片上tile buffer可以保存颜色、深度和模板数据，当使用MSAA（多重采样抗锯齿）时，采样数据同样存储在片上，Resolve完成后才输出，避免了MSAA在桌面GPU上造成的巨量带宽膨胀。

### Deferred渲染与HSR/Early-Z

PowerVR的TBDR在Rendering Pass中加入了Hidden Surface Removal（HSR）机制：在执行像素着色之前，先对Tile内所有图元执行可见性判断，仅对最终可见的像素运行Fragment Shader。这意味着即使场景中存在大量Over-draw（多边形叠加），被遮挡的片段也不会消耗着色器执行资源。

Mali的TBR（非Deferred）采用类似Early-Z的机制，但不如TBDR的HSR彻底——不透明物体如果按从前到后顺序提交，可以获得良好的Early-Z剔除效果；一旦渲染顺序混乱或出现Alpha测试，Early-Z便会失效退化为Late-Z，导致Over-draw重新出现。因此在Mali硬件上，开发者被强烈建议将不透明物体按从前到后排序，而在PowerVR上这一排序对性能影响相对较小。

### Geometry Pass的代价与Varying数据存储

TBDR的Binning阶段会将顶点着色器结果（Position + Varying变量）暂存到主内存中，等待Rendering Pass读回。这意味着：顶点数量过多或每顶点Varying变量过多，都会增加Binning Phase的内存写入量。以Adreno 6系列为例，其LRZ（Low Resolution Z）技术在Binning Pass中额外生成低分辨率深度图，用于Rendering Pass的快速遮挡剔除，但这也带来了额外的内存写入。

这一特性使得移动端GPU在处理细分曲面（Tessellation）和几何着色器时效率低下——每增加一个顶点，都需要更多Binning Pass的存储与读取，而这些操作直接消耗带宽和能量。Unity和Unreal的移动渲染管线均默认禁用这些功能。

## 实际应用

**Framebuffer Fetch与延迟着色**：TBDR架构支持Framebuffer Fetch操作，允许Fragment Shader直接读取当前像素的已有颜色值而无需采样贴图，因为该数据仍在Tile Buffer中。Vulkan的VK_EXT_raster_order_groups和Metal的framebufferFetch均利用此特性。利用这一能力可以在移动端高效实现延迟着色（Deferred Shading），GBuffer数据不需要写回主内存再读回，全程保留在Tile Buffer中完成光照计算，节省了数倍带宽。

**Render Pass中间体的Transient Attachment**：在Vulkan中，如果深度缓冲仅在一个Render Pass内部使用（不需要在Pass结束后保留），可以将其标记为TRANSIENT，配合LAZILY_ALLOCATED内存类型，告知驱动此缓冲无需Resolve到主内存。这在Mali和Adreno上可节省深度缓冲写入的全部带宽，通常可降低10%-30%的总内存带宽消耗。

**避免Render Pass中断**：在Metal和Vulkan中，在一个Render Pass内执行glReadPixels或vkCmdCopyImage等操作会强制Tile数据提前Resolve，导致Tile Buffer内容写回主内存再读回，完全破坏了TBDR的带宽优势。iOS和Android的GPU分析工具（Xcode GPU Frame Capture、Adreno Profiler）均会专门标记此类"Render Pass Break"事件。

## 常见误区

**误区一：移动端GPU的性能瓶颈与桌面GPU相同**。许多开发者将桌面端的优化经验直接移植到移动端，例如不关注Render Pass结构，或在场景中大量使用Tessellation。实际上移动端GPU的首要瓶颈往往是带宽和Tile数据管理，而非单纯的着色器算力。在桌面端无害的glBlitFramebuffer操作，在移动端可能触发完整的Resolve-Reload周期，耗费与Tile大小正相关的带宽。

**误区二：Tile-Based架构天然支持高效延迟着色**。虽然TBDR的Framebuffer Fetch功能为延迟着色提供便利，但如果GBuffer贴图数量过多（例如超过4张MRT），单个Tile需要存储的数据量可能超出片上Tile Buffer容量，迫使驱动将部分数据Spill到主内存，反而抵消了架构优势。实践中移动端延迟着色的GBuffer设计需要严格控制每像素数据量，通常压缩到128位以内。

**误区三：PowerVR、Mali、Adreno的Tile-Based行为完全一致**。三家架构在Binning/Rendering分离时机、HSR深度、片上缓存大小、Varying Spill策略上均存在差异，同一个渲染管线在三个平台上的性能特征可能截然不同。Adreno的Flex Render模式允许动态切换IMR和TBR，而Mali的Bifrost/Valhall架构则针对可见性测试做了专用硬件加速。

## 知识关联

学习移动端GPU之前需要掌握GPU架构概述中的渲染管线基础，理解顶点着色、光栅化、片段着色在传统IMR（Immediate Mode Rendering）管线中的顺序执行方式，才能体会TBDR插入Binning Pass和延迟Rendering Pass的本质差异。

移动端GPU的Tile-Based原理直接影响Vulkan和Metal API的设计决策：Vulkan的Render Pass、Subpass和Transient Attachment等概念均是为了将TBDR的硬件行为暴露给开发者，OpenGL ES的glInvalidateFramebuffer同样是为此而设计的接口，调用它可以提示驱动跳过Tile数据的Resolve写回，在不需要保留深度缓冲的场景中节省约30%的帧缓冲带宽。