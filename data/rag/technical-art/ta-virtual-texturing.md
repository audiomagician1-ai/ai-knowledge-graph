---
id: "ta-virtual-texturing"
concept: "虚拟纹理"
domain: "technical-art"
subdomain: "material-system"
subdomain_name: "材质系统"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.2
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 虚拟纹理

## 概述

虚拟纹理（Virtual Texture，简称 VT）是一种将超大分辨率纹理按需加载到 GPU 显存的技术，其核心思想来源于操作系统的虚拟内存分页机制。传统纹理受限于显存容量，一张 16K×16K 的 RGBA8 纹理完整展开需要约 1 GB 显存；而虚拟纹理通过将纹理切割成固定大小的"页面"（Page，常见尺寸为 128×128 或 256×256 像素），仅将相机当前可见且需要的页面上传至 GPU，使得理论上可支持高达 1M×1M 分辨率的虚拟纹理集。

虚拟纹理的概念由 Sean Barrett 在 1999 年的 GDC 演讲中首次系统性提出，2012 年 id Software 在《RAGE》中以 MegaTexture 名称将其商业化落地，随后 Unreal Engine 4.23 版本将 Runtime Virtual Texture（RVT）和 Streaming Virtual Texture（SVT）作为正式功能集成进引擎。这一历史路径说明虚拟纹理并非学术概念，而是经过十余年工程迭代的生产级解决方案。

对于技术美术来说，虚拟纹理的价值在于彻底解耦"纹理艺术分辨率"与"运行时显存预算"之间的矛盾。制作团队可以在 Substance Painter 中以 8K 甚至 16K 精度绘制地形材质，部署时由虚拟纹理系统自动降级或按需流入，无需手动拆分图集或强制妥协画质。

---

## 核心原理

### 页表与间接纹理查找

虚拟纹理的寻址依赖两张关键纹理：**页表纹理**（Page Table Texture）和**物理缓存纹理**（Physical Cache Texture）。页表纹理中每一个像素记录了一个虚拟页面对应的物理位置坐标（偏移量 + 所在 Mip 层级），分辨率通常为虚拟纹理总分辨率除以页面大小。采样时 Shader 先读取页表获得物理地址，再用该地址从物理缓存纹理中取色，因此每次纹理采样实际包含两次纹理读取，这一开销是使用虚拟纹理的固定成本。

### 反馈缓冲区与页面调度

GPU 每帧通过渲染一张低分辨率的**反馈纹理**（Feedback Buffer，典型分辨率为屏幕 1/8 大小）来确定哪些虚拟页面被访问。该缓冲区记录每个屏幕像素的虚拟 UV 坐标和所需 Mip 级别，CPU 读回后由页面调度器（Page Scheduler）决定哪些页面需要从磁盘或内存异步加载，哪些已缓存页面需要被驱逐。这一过程类似 CPU 的 LRU（Least Recently Used）缓存淘汰算法。

反馈缓冲区的延迟是 1-2 帧，意味着快速摄像机移动时可能出现短暂的页面缺失（Page Fault），表现为纹理短暂降质显示更低 Mip 级别，这是虚拟纹理固有的视觉特征而非 Bug。

### UDIM 坐标系统

UDIM（U Dimension）是虚拟纹理在影视制作流程中的标准化形式，由 Mari 软件定义。UDIM 将 UV 空间分割为多个 1001~9999 编号的 UV Tile，编号规则为：`UDIM = 1001 + U方向偏移 + V方向偏移 × 10`。例如第二行第三列的 Tile 编号为 `1001 + 2 + 1×10 = 1023`。每个 Tile 对应一张独立纹理文件，分辨率可达 8K×8K，整个角色可使用 10×10 共 100 张 Tile，等效于 80K×80K 的虚拟纹理面积。技术美术在 UE5 中使用 UDIM 时，需在导入设置中开启 **Virtual Texture Streaming** 并确认 UV 坐标超过 0-1 范围不会被 Clamp 截断。

### 边界填充（Border Padding）

虚拟纹理分页后，相邻页面边界在 Mip 过滤时会产生接缝。解决方案是为每张物理页面增加 4~8 像素的**边界填充**（Border），填充内容来自相邻页面的数据。以 128×128 的页面大小、4 像素边界为例，物理缓存中存储的实际尺寸为 136×136，有效像素占比约为 88.7%，这一冗余是虚拟纹理物理缓存容量规划时必须计入的开销。

---

## 实际应用

**大世界地形混合**：UE5 的地形系统默认使用 Runtime Virtual Texture（RVT）将多层混合后的 Albedo、Normal、Roughness 缓存为虚拟纹理，地形上的静态网格体（石块、道路）通过采样同一张 RVT 实现无缝融合，避免了传统方法中为每个网格单独绘制底部遮罩的工作量。实际项目中一张 RVT 通常设为 4096×4096 虚拟分辨率，对应约 32 个物理页面常驻显存。

**影视级角色贴图**：在《蜘蛛侠：英雄无归》视效制作中，角色皮肤纹理采用 UDIM 工作流，单个角色使用 6×4 = 24 张 4K Tile，总像素量超过 390 MB（未压缩）。离线渲染器（如 Arnold、RenderMan）直接支持 UDIM 路径模式 `<UDIM>`，运行时按需加载对应 Tile，内存峰值仅为同时可见 Tile 数量之和。

**移动端降级策略**：移动平台通常不原生支持虚拟纹理，技术美术需在打包时将虚拟纹理烘焙为固定分辨率的常规纹理（UE5 中称为 Non-Virtual Fallback）。典型策略是为 PC 端保留 4K 虚拟纹理，为 Android 中端机型烘焙 2K 常规纹理，高低端资产通过 Device Profile 系统自动切换。

---

## 常见误区

**误区一：虚拟纹理等同于纹理流送（Texture Streaming）**
普通纹理流送（如 UE4 的 Texture Streaming）仅在 Mip 层级粒度上调度资源，最小加载单元是整个 Mip 级别；虚拟纹理的最小调度单元是单个页面（如 128×128 像素块），粒度更细 100 倍以上。两者可共存：在 UE5 中，非虚拟纹理走 Mip Streaming 管线，虚拟纹理走独立的 VT Page 管线，物理缓存池大小由 `r.VT.PoolSizeX/Y` 单独控制。

**误区二：虚拟纹理总是更节省显存**
物理缓存纹理、页表纹理、反馈缓冲区本身都占用显存。当场景中虚拟纹理的可见面积较小（例如仅一面墙），实际节省的显存可能不及这些固定开销（物理缓存默认 2048×2048，约 16 MB）。因此虚拟纹理适合超大面积地形或高分辨率角色，不适合大量小尺寸道具贴图，后者用传统图集（Texture Atlas）更高效。

**误区三：UDIM Tile 之间可以任意过渡采样**
UDIM 每张 Tile 是独立纹理文件，标准 UV 采样在 Tile 边界处会产生硬性接缝，因为 GPU 的双线性过滤无法跨越不同纹理对象读取像素。若需无缝跨 Tile 过渡，必须使用支持 UDIM 虚拟化的渲染器特性（如 MaterialX 的 UsdUVTexture 节点）或在制作阶段手动在 Tile 边界添加 4~8 像素的重叠绘制区域。

---

## 知识关联

虚拟纹理以**无缝贴图制作**为前提：页面边界的接缝问题与无缝贴图中的边界连续性问题同质同源，掌握无缝贴图的频率域拼接原理有助于理解 Border Padding 的必要性，以及为何虚拟纹理的物理缓存不能使用 Clamp 寻址而必须使用带边界的 Repeat 逻辑。

虚拟纹理直接驱动**资源流送**系统的设计。资源流送的页面调度器是虚拟纹理反馈分析的下游消费者——反馈缓冲区输出的页面请求列表进入流送系统的 I/O 队列，后者负责从磁盘读取压缩页面数据（通常为 BC7 或 ASTC 格式）并解压上传至物理缓存。理解虚拟纹理的页面生命周期（请求→加载→驻留→驱逐）是学习完整资源流送管线的基础入口。
