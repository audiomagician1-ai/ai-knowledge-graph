---
id: "ta-mobile-perf"
concept: "移动端性能"
domain: "technical-art"
subdomain: "perf-optimization"
subdomain_name: "性能优化"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 移动端性能

## 概述

移动端性能优化是技术美术在手游开发中面临的核心挑战，其根本原因在于移动端GPU采用了与桌面端截然不同的**基于瓦片的渲染架构（Tile-Based Rendering，TBR）**，而非桌面GPU普遍使用的立即模式渲染（Immediate Mode Rendering，IMR）。这一架构差异导致桌面端的许多性能优化经验无法直接迁移到移动端，甚至会产生反效果。

TBR架构诞生的背景是移动设备的功耗限制。ARM Mali、Qualcomm Adreno、Apple GPU、Imagination PowerVR等主流移动端GPU均采用TBR或其变体TBDR（Tile-Based Deferred Rendering）。以2023年广泛使用的Adreno 740（搭载于骁龙8 Gen 2）为例，其片上缓存（On-Chip Memory）仅有数百KB，但通过将屏幕分割为16×16或32×32像素的瓦片（Tile），在每个瓦片的渲染过程中将数据保留在高速片上缓存中，从而大幅减少对带宽消耗极高的主内存（DRAM）读写操作，将整机功耗控制在手机散热可承受的范围内。

移动端性能问题直接决定玩家体验：帧率下降会触发系统的热降频机制，导致游戏后期帧率雪崩；带宽超标则会引发设备发热，反过来加速热降频。因此理解移动端GPU的工作机制是手游技术美术的基本功。

## 核心原理

### TBR架构与带宽优化

TBR渲染管线分为两个主要阶段：**几何处理阶段（Binning Pass）**和**渲染阶段（Rendering Pass）**。在Binning Pass中，GPU先遍历所有顶点，计算每个图元落在哪个Tile内，将这些信息写入显存。在Rendering Pass中，GPU逐Tile加载该Tile所需的几何信息，在片上缓存中完成全部光栅化和像素着色计算，最终一次性将结果写入帧缓冲（Framebuffer）。

这一机制带来的关键优化规则是：**避免打断Tile渲染流程**。任何导致GPU必须提前将当前Tile结果刷写（Flush）到主内存的操作都会产生巨大的带宽惩罚。最常见的触发场景包括：在同一帧内对同一张RenderTarget先写后读（如后处理读取场景颜色缓冲）、使用`glCopyTexImage2D`等接口强制同步GPU/CPU数据。Unity的`GrabPass`在移动端性能极差的根本原因就在于此——它强制GPU将当前帧缓冲Flush到主内存，然后才能被Shader读取，产生一次完整的带宽往返。

替代方案是使用`Framebuffer Fetch`扩展（iOS上对应`[[color(0)]]`输入，Android上对应`GL_EXT_shader_framebuffer_fetch`），该扩展允许Shader直接从片上缓存读取当前像素的已有颜色值，无需任何主内存读写，带宽开销近乎为零。

### 带宽（Bandwidth）量化与控制

移动端GPU的带宽预算非常有限。以中端机型为例，LPDDR5内存的带宽上限约为**50-60 GB/s**，而一张2560×1440分辨率的Framebuffer，若格式为RGBA8（4字节），以60fps渲染，仅读写Framebuffer本身就需要约 2560×1440×4×2（读+写）×60 ≈ **3.3 GB/s**，这还不包括纹理采样、顶点缓冲等其他带宽消耗。

减少带宽消耗的具体手段包括：
- **降低Framebuffer精度**：将HDR格式从RGBA16F（8字节/像素）降为R11G11B10F（4字节/像素），带宽直接减半。
- **启用MSAA而非后处理抗锯齿**：TBR架构下，MSAA的多重采样数据可以完全保留在片上缓存中，最终Resolve时只写出1倍分辨率的结果，实际带宽开销远低于TAA的多帧Framebuffer读写。
- **压缩纹理格式**：Android优先使用ASTC（可达6:1至12:1压缩率），iOS使用PVRTC或ASTC（A8芯片起支持），避免使用未压缩的RGBA32。
- **减少RenderPass数量**：每增加一个RenderPass就意味着一次Framebuffer的Load/Store操作，在Vulkan/Metal中明确设置`storeAction = DontCare`可告知驱动无需将Tile数据写回主内存。

### 热降频（Thermal Throttling）机制

热降频是移动端独有的性能杀手。当芯片温度超过阈值（通常为**80-85°C**）时，操作系统会主动降低GPU/CPU的工作频率，骁龙系列在严重过热时GPU频率可降至正常频率的**40%-60%**，导致帧率从60fps骤降至20fps以下。

热降频的根本诱因是持续高功耗，而高带宽和高Overdraw是移动端功耗的主要来源。技术美术可通过以下方式延缓热降频：
- 将目标帧率从60fps降为30fps并开启帧率锁定，功耗约降低40%，设备温升明显减缓。
- 使用Mali的**Streamline**或高通的**Snapdragon Profiler**工具监控`GPU Active Cycles`和`Tiler Active`指标，定位是几何复杂度还是填充率导致的高功耗。
- 避免粒子系统的Alpha Blend叠加层数超过3层，半透明物体的Overdraw对带宽和ALU功耗均有显著影响。

### TBDR与Early-Z的特殊交互

PowerVR和Apple GPU的TBDR架构在TBR基础上引入了**隐面消除（Hidden Surface Removal，HSR）**，在着色之前通过硬件确定每个像素的可见性，理论上可完全消除Overdraw。但这一特性有严格前提：像素着色器不能修改深度值（`gl_FragDepth`），也不能使用`discard`/`clip`指令，否则GPU无法提前判断可见性，HSR会退化失效。因此在移动端使用AlphaTest时，应将`clip()`操作移至片元着色器的**最后一行**而非最前，以最大化HSR的有效范围。

## 实际应用

**案例一：后处理管线优化。** 某手游的Bloom效果原本使用5次降采样+5次升采样，每次都产生独立的RenderTarget读写，在Adreno 630上带宽占用达到整体的35%。将管线改为双线性降采样3次，并合并最终升采样与UI合批为同一个RenderPass后，Bloom的带宽消耗降至12%，帧时间从18ms降至14ms。

**案例二：角色Shader中的Discard优化。** 某角色使用AlphaTest模拟头发透明，因Shader最前使用`clip()`导致Apple GPU的HSR完全失效，全屏头发区域Overdraw达4层。将`clip()`移至Shader末尾并加入Early-Z Pass后，GPU像素处理耗时减少约30%。

**案例三：阴影质量与带宽平衡。** 将ShadowMap格式从Depth24（3字节）改为Depth16（2字节），分辨率从2048降至1024，带宽节省约75%，在中低端机（Mali-G57）上帧率从27fps提升至34fps，视觉差异经测试在5%阈值内不可感知。

## 常见误区

**误区一：桌面端的Early-Z优化在移动端同样有效。** 在IMR架构的桌面GPU上，从前到后排序透明物体、利用Early-Z剔除是经典优化。但在TBR架构下，GPU已在Binning Pass中获取了完整的场景深度信息，不透明物体的绘制顺序对Early-Z的影响远小于桌面端。盲目在移动端做不透明物体排序，反而会破坏CPU端合批（Batching），增加DrawCall。

**误区二：MSAA在移动端很贵。** 许多开发者因桌面端经验而排斥移动端MSAA。实际上，4xMSAA在TBR架构下的额外带宽开销几乎可以忽略不计（多重采样数据驻留片上缓存），其功耗主要来自Rasterization阶段的ALU计算，通常比TAA的帧间读写开销更低。在Adreno 640上，4xMSAA相比TAA帧时间通常减少约1-2ms。

**误区三：减少DrawCall是移动端最重要的优化。** DrawCall优化在桌面端PC上至关重要，但移动端的性能瓶颈通常首先出现在带宽和填充率（Fillrate）上，而非DrawCall提交开销。在Mali-G76的典型场景测试中，将DrawCall从800减少到400，帧时间改善仅约0.5ms；而将Overdraw从4层降至2层，帧时间改善可达3-5ms。技术美术应优先使用Snapdragon Profiler或Mali Graphics Debugger确认瓶颈类型，而非默认套用桌面端优化思路。

## 知识关联

本概念建立在**GPU性能分析**的基础上：掌握GPU渲染管线各阶段（Vertex、Rasterization、Fragment、ROP）的功能划分，是理解TBR将哪些阶段移入