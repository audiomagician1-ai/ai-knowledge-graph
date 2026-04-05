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
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---



# 分块渲染

## 概述

分块渲染（Tile-Based Rendering，TBR）是一种将屏幕划分为若干小矩形区域（Tile），逐块完成光栅化和着色计算的渲染架构。与立即模式渲染（Immediate Mode Rendering，IMR）不同，TBR 在正式执行像素着色之前，先收集一帧内所有几何变换结果，再按 Tile 分批处理，从而大幅减少对外部 DRAM 的访问频次。这一特性使分块渲染成为移动端 GPU（ARM Mali、Qualcomm Adreno、Apple GPU）的主流架构基础。

分块渲染的思想最早可追溯至1990年代的 SGI 视频游戏芯片研究。真正推动其大规模落地的是移动设备对功耗的严苛要求：2000年代初期，PowerVR 系列 GPU 以 TBDR（Tile-Based Deferred Rendering）形式将其商业化，搭载于 iPhone 第一代（2007年）所使用的 Samsung S5L8900 芯片中的 PowerVR MBX Lite 核心。此后，ARM Mali-200（2008年）采用 TBR，Qualcomm Adreno 200（2008年）亦跟进类似设计，奠定了移动端 GPU 架构的基本格局。每个 Tile 的典型尺寸为 16×16 或 32×32 像素，GPU 为每个 Tile 在芯片内部分配一块高速 On-Chip Buffer（SRAM），所有深度测试、混合等读写操作优先在此缓冲区内完成，仅在 Tile 渲染完毕后才将最终结果刷写到主存 Framebuffer。

在 28nm 工艺节点下，一次 DRAM 读写消耗的能量约是片上寄存器访问的 200 倍、片上 SRAM 访问的 20 倍（参考 Dally 等人在《Digital Design Using VHDL》中对内存层次功耗的测量数据）。TBR 将深度测试、混合等操作限制在 On-Chip Buffer 内完成，可将 DRAM 带宽需求降低 50%–80%，直接决定了移动设备的续航表现与发热水平。

---

## 核心原理

### Tile 分块几何处理流程

分块渲染将渲染管线拆分为两个独立阶段，两阶段之间以 Parameter Buffer（参数缓冲区）为桥梁进行异步解耦。

**第一阶段（Geometry / Binning Pass）**：GPU 执行顶点着色器，将所有图元变换至裁剪空间，随后通过 Binning 操作计算每个三角形覆盖哪些 Tile，将三角形索引写入对应 Tile 的显存命令列表。这一阶段的输出仅包含索引和包围信息，数据量远小于完整几何数据，Binning Pass 的显存写出量通常不超过原始顶点数据的 10%–15%。

**第二阶段（Rendering Pass）**：GPU 逐 Tile 调度，将该 Tile 对应的几何子集读入 On-Chip Buffer，在片上完成光栅化、深度测试、像素着色和混合，最后一次性写出到主存 Framebuffer。整个过程的 DRAM 写入次数理论上等于屏幕像素总数（每像素一次最终颜色写出），而非渲染操作次数的总和。

这种两阶段设计的代价是 Geometry Pass 需要完整遍历场景几何，因此对顶点数量极多但可见三角形比例低的场景（例如密集植被的远景 LOD 未被剔除时），Binning Pass 本身会成为瓶颈。ARM 在其 Mali GPU 最佳实践文档（ARM, 2021, *Mali GPU Best Practices Developer Guide*）中建议将场景每帧提交的三角形数控制在 GPU 主频对应的几何吞吐量的 50% 以内，以确保 Binning Pass 不拖累 Rendering Pass 的调度节奏。

### HSR 与 TBDR 的隐藏面消除

PowerVR 的 TBDR 在第二阶段引入了 **Hidden Surface Removal（HSR）** 机制：在执行像素着色器之前，GPU 先对 Tile 内所有图元进行深度排序，只对最终可见像素调用一次片元着色器。这与传统 Early-Z 存在本质区别：Early-Z 依赖 Draw Call 的前后提交顺序（必须从前到后排序才能发挥效果），而 HSR 不依赖顺序，能保证每个不透明像素的片元着色器调用次数严格等于 1。

以一个典型移动端游戏场景为例，若场景 Overdraw 比率为 4×（即平均每个屏幕像素被 4 个三角形覆盖），在 IMR 架构下片元着色器的调用量为有效像素数的 4 倍，而在 TBDR 的 HSR 机制下，调用量仍等于有效像素数的 1 倍，着色开销节省 75%。这是 IMR 的 Early-Z 在随机绘制顺序下无法保证的。

值得注意的是，**半透明物体会打破 HSR 的工作条件**，因为透明渲染需要从后到前混合，GPU 无法提前判断"最终可见像素"。因此，在 PowerVR 和 Apple GPU 上，半透明 Draw Call 必须切换到传统 Overdraw 路径，开发者应尽量将透明物体的屏幕覆盖面积控制在 20% 以下，否则会显著劣化 HSR 的全局效率。

### On-Chip Buffer 的容量限制与 Tile 尺寸权衡

On-Chip Buffer 的大小直接影响 Tile 能支持的最大像素数与附件（Attachment）数量。以 Apple A15 GPU 为例，其片上缓冲区容量约为 64 MB（基于 Apple Silicon 架构技术白皮书中公开的数据），支持在单个渲染通道中同时保持颜色、深度、模板及多个 G-Buffer 附件，无需将中间结果回写到主存——这正是 Tile-Based Deferred Rendering 在移动端实现延迟着色（Deferred Shading）的物理基础。

对于标准 1920×1080 分辨率的屏幕，若 Tile 大小为 32×32 像素，则共划分 $\lceil 1920/32 \rceil \times \lceil 1080/32 \rceil = 60 \times 34 = 2040$ 个 Tile。每个 Tile 的 On-Chip Buffer 需求为：

$$
\text{Buffer}_{tile} = T_w \times T_h \times \sum_{i} B_i
$$

其中 $T_w = T_h = 32$（Tile 宽高，单位：像素），$B_i$ 为第 $i$ 个附件的字节深度（颜色缓冲 4 字节，深度+模板 4 字节，若开启 MSAA 4× 则乘以 4）。仅颜色+深度的最小配置下，每 Tile 需 $32 \times 32 \times 8 = 8192$ 字节（8 KB）。

---

## 关键公式与带宽量化

设屏幕分辨率为 $W \times H$，颜色缓冲字节数 $C = 4$（RGBA8），深度+模板字节数 $D = 4$，帧率 $F = 60$ fps，场景平均 Overdraw 倍率为 $k$。

**IMR 最坏情况 DRAM 带宽（每秒）**：

$$
BW_{IMR} = W \times H \times (C + D) \times k \times F
$$

**TBR 理论 DRAM 带宽（每秒，仅计最终写出）**：

$$
BW_{TBR} = W \times H \times C \times F + W \times H \times D \times F_{depth\_resolve}
$$

其中深度缓冲通常无需回写主存（若不需要深度附件复用），故 $F_{depth\_resolve} \approx 0$，则：

$$
BW_{TBR} \approx W \times H \times C \times F
$$

以 1080p、$k = 4$、60 fps 为例：
- $BW_{IMR} = 1920 \times 1080 \times 8 \times 4 \times 60 \approx 3.98 \text{ GB/s}$
- $BW_{TBR} = 1920 \times 1080 \times 4 \times 60 \approx 0.50 \text{ GB/s}$

带宽节省约 **87.5%**，这直接对应了功耗和发热量的等比例降低，是移动端电池寿命优化的核心量化依据。

---

## 实际应用：移动端延迟渲染（TBDR）

延迟渲染（Deferred Rendering）在 PC 端的 IMR 架构上需要将 G-Buffer（法线、反照率、金属度、粗糙度等）写出到主存，再在 Lighting Pass 读回，产生约 $W \times H \times G_{bytes} \times 2$ 的额外 DRAM 带宽消耗（读+写各一次）。以标准 PBR G-Buffer（共 64 字节/像素）和 1080p 为例，这相当于每帧额外 127 MB 的 DRAM 传输量。

而在 TBDR 架构上，G-Buffer 的所有附件可以全部驻留在 On-Chip Buffer 中，Geometry Pass 写入 G-Buffer 后，Lighting Pass 直接从片上读取，不产生任何主存往返流量。Apple 在 Metal API 中通过 **Programmable Blending** 和 **Tile Shaders**（Metal 2，2017年 WWDC 发布）将这一能力显式暴露给开发者，允许在 Tile Shader 阶段直接读写当前 Tile 的全部附件，实现真正零带宽的多 Pass 延迟渲染。

```metal
// Apple Metal Tile Shader 示例：在 On-Chip Buffer 上执行光照计算
kernel void lightingTileShader(
    imageblock<GBufferData> gBuffer [[imageblock_data]],
    constant LightData* lights [[buffer(0)]],
    ushort2 localCoord [[thread_position_in_threadgroup]])
{
    // 直接从 On-Chip Buffer 读取 G-Buffer，零 DRAM 访问
    GBufferData gbData = gBuffer.read(localCoord);
    float3 albedo   = gbData.albedo.rgb;
    float3 normal   = gbData.normal.xyz * 2.0 - 1.0;
    float  roughness = gbData.material.r;

    float3 lighting = evaluatePBR(albedo, normal, roughness, lights);

    // 写回结果依然在片上，仅 Tile 结束时才写出到 Framebuffer
    gbData.albedo = float4(lighting, 1.0);
    gBuffer.write(gbData, localCoord);
}
```

Qualcomm Adreno 的等效机制称为 **GMEM**（on-chip Graphics Memory），Vulkan 中通过 `VK_QCOM_render_pass_store_ops` 扩展控制 GMEM 的 Load/Store 行为；ARM Mali 通过 Vulkan 的 `VkRenderPass` 中 `loadOp = LOAD_OP_DONT_CARE` / `storeOp = STORE_OP_DONT_CARE` 来指示驱动将中间附件保留在片上，避免不必要的 Resolve 操作。

---

## 常见误区

**误区一：认为 TBR 可以无限叠加 G-Buffer 附件数量。**
On-Chip Buffer 的容量是固定的。当 G-Buffer 附件总字节数超过片上缓冲容量时，驱动会自动将部分附件 Spill 到主存，触发额外的 DRAM 读写，完全抵消 TBR 的带宽优势。ARM Mali-G78（2020年）的 On-Chip Buffer 约为 1 MB，若 Tile 大小为 16×16，每 Tile 可用空间为 $1\text{MB} / \text{Tile数量}$，开发者应使用 GPU 厂商提供的 Profiler（如 Arm Mobile Studio、Snapdragon Profiler）监控 "External Read Bandwidth" 指标，确认 G-Buffer 是否真正驻留片上。

**误区二：对 TBDR 使用 `glClear` 替代 `DONT_CARE`。**
在 OpenGL ES 中，若开发者在 `glBindFramebuffer` 后不调用 `glClear` 或不设置 `GL_EXT_discard_framebuffer`，驱动会在 Rendering Pass 开始时从主存加载上一帧的内容（Load 操作），产生不必要的 DRAM 读带宽。正确做法是在 Vulkan 中设置 `loadOp = LOAD_OP_CLEAR` 或 `LOAD_OP_DONT_CARE`，在 OpenGL ES 中调用 `glInvalidateFram