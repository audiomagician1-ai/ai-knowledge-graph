---
id: "cg-virtual-texture"
concept: "虚拟纹理"
domain: "computer-graphics"
subdomain: "texture-techniques"
subdomain_name: "纹理技术"
difficulty: 4
is_milestone: false
tags: ["前沿"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 73.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 虚拟纹理

## 概述

虚拟纹理（Virtual Texturing），又称稀疏纹理（Sparse Texture），是一种将极大尺寸纹理拆分为小块（Tile/Page）并按需流式加载到GPU显存的技术。其核心思想来源于操作系统的虚拟内存机制——应用程序访问一个远大于物理内存的"虚拟地址空间"，而只有真正被访问的页面才驻留在物理内存中。在图形学中，虚拟纹理将同样的分页思想移植到纹理采样流程，使渲染引擎能够在不超出GPU显存限制的前提下，使用理论上可达128K×128K甚至更高分辨率的超大纹理。

这项技术由John Carmack在2000年代初期提出概念（"MegaTexture"），并在id Software的《雷神之锤战争》（Quake Wars, 2007）中首次商业应用，用于覆盖大型开放世界地形。现代图形API已将其标准化：OpenGL 4.3引入了ARB_sparse_texture扩展，DirectX 11.2/Direct3D 11.2引入了Tiled Resources，Vulkan则通过稀疏绑定（Sparse Binding）和稀疏图像（Sparse Image）提供原生支持。

虚拟纹理解决了开放世界游戏中最棘手的显存瓶颈问题。一张覆盖整个地形的4K分辨率纹理仅需约48MB（RGBA8），但若要实现每平方厘米地表都有独特细节的超大场景，同等密度的纹理需要数十GB。虚拟纹理允许美术人员以极高精度绘制整个世界，而运行时仅将玩家视野内、当前渲染距离所需的Mip层级对应Page加载到一个物理纹理图集（Physical Texture Atlas）中。

## 核心原理

### 页表与间接查找

虚拟纹理的核心数据结构是**页表纹理（Page Table Texture）**，它是一张低分辨率的2D查找纹理，每个像素存储一条记录：当前虚拟Page是否已驻留在物理Atlas中，若是则记录其在Atlas中的物理坐标（偏移量）。采样一张虚拟纹理时，着色器首先用虚拟UV坐标查询页表，取得物理偏移，再用修正后的UV去采样物理Atlas，整个过程称为**两级间接采样（Two-Level Indirection）**。

页表本身按Mip层级组织：一张65536×65536的虚拟纹理如果Page大小为128×128像素，则最细Mip层（Level 0）的页表分辨率为512×512，每个Entry对应一个128×128的Page。Mip Level 1的页表为256×256，以此类推，共需约10个Mip级别的页表。现代实现通常将所有Mip级别的页表打包进一张使用硬件Mipmap的RGBA纹理中，以GPU硬件Mip过滤代替手动级别选择。

### 反馈缓冲与流式调度

由于着色器无法直接触发CPU端的磁盘IO，虚拟纹理系统通过**反馈缓冲（Feedback Buffer）**机制通知CPU哪些Page需要加载。在每帧（或每N帧）渲染一个低分辨率的反馈Pass：着色器将当前像素所需的虚拟Page地址（虚拟纹理ID + Mip Level + Page XY坐标）写入一张小尺寸缓冲，常见分辨率为屏幕的1/8×1/8（如1920×1080场景下分辨率为240×135）。CPU端读回该缓冲，统计所有需求Page，与当前已驻留Page集合做差集，排列优先级队列后提交IO线程异步加载，加载完成后更新页表纹理和物理Atlas。

这套调度系统天然存在**加载延迟（Streaming Latency）**：玩家快速转向时，新视角所需的Page需要经历"反馈→读回→磁盘IO→解压→上传GPU"全流程，可能需要数帧甚至数十帧。因此实际系统会对Page进行预测性预取：根据相机运动方向和速度，预先请求预测视锥内的Page，并对较高Mip Level（低精度）的Page给予更高优先级，以快速提供粗糙但可见的细节，再异步替换为精细Page。

### 边界填充与Mip连续性

物理Atlas中相邻Page之间若发生纹理过滤，会在Page边界产生**接缝伪影（Seam Artifact）**。标准解决方案是为每个Page添加**边界填充（Border/Gutter）**，通常为4像素，即一个128×128的逻辑Page在Atlas中占据136×136（128+4×2）的物理空间。采样时通过坐标重映射确保过滤核心不会跨越Page边界采样到相邻Page的数据。

Mip Level跨越也是难点：当着色器需要在Level N和Level N+1之间做三线性插值时，两个Mip Level对应的物理Atlas存储位置完全独立，无法依赖硬件自动插值。常见做法是在着色器中手动计算Mip Level（使用dFdx/dFdy计算梯度），分别查询两级页表，分别采样后在着色器中线性混合，代价是每次采样需要4次纹理读取而非标准的1次。

## 实际应用

**开放世界地形系统**是虚拟纹理最典型的应用。《荒野大镖客：救赎2》使用了覆盖整个地图的超大虚拟纹理，将地表颜色、法线、粗糙度等多张纹理的Page打包入同一物理Atlas（称为Virtual Texture Stack），在保证每处地形独特外观的同时将显存峰值控制在预算内。

**UE4/UE5的Runtime Virtual Texture（RVT）**是引擎级别的标准化实现：UE将地形材质在运行时"烘焙"到虚拟纹理中，后续地物（草、道路贴花）直接采样该虚拟纹理而非重新混合，将复杂地形着色从每像素多层材质混合简化为单次虚拟纹理采样，大幅降低DrawCall复杂度。

**DirectX 12 Tiled Resources Tier 3**允许稀疏3D纹理，可用于体积云、体积雾的稀疏体素纹理存储，只为存在密度数据的体素分配物理页面，其余区域映射到单一"空Page"，节省大量显存。

## 常见误区

**误区一：虚拟纹理等同于纹理流送（Texture Streaming）。** 传统纹理流送以整张纹理或其整个Mip Level为粒度，当一张4096×4096的纹理只有角落一小块在视野中时，仍需加载整个Mip Level（约64MB RGBA8）。虚拟纹理以Page为粒度（如128×128），只加载实际可见的那几个Page，对大尺寸非重复纹理的显存节省是数量级的差异，而非渐进改善。

**误区二：只需提高Page分辨率就能提升质量。** Page尺寸越大，边界填充开销占比越小（效率更高），但同时意味着更粗的加载粒度——一块稍大区域进入视野就可能触发较大Page加载，增加峰值IO带宽需求。反之Page越小，IO请求数越多，反馈缓冲的聚合与调度开销越高。128×128像素是目前业界最常见的折中选择，DX11 Tiled Resources规范也将Tile尺寸固定为64KB（对应BC格式纹理约为128×128逻辑像素）。

**误区三：虚拟纹理完全消除了采样性能开销。** 相较于直接采样普通纹理，虚拟纹理每次采样至少增加一次页表查询（1次额外纹理读取），三线性插值时增至4次，并且着色器必须手动处理Mip Level计算与梯度，不能使用tex2D()等隐式Mip函数，在移动端等带宽敏感平台上此额外开销需要仔细评估。

## 知识关联

**纹理压缩**是虚拟纹理的直接前置知识：物理Atlas中存储的Page通常以BC1/BC3/BC7（DX系）或ASTC（移动端）等块压缩格式存储，Page的物理尺寸必须是压缩块大小（通常4×4像素）的整数倍，边界填充大小也需对齐到压缩块。磁盘上每个Page同样以压缩格式存储，IO线程加载后可直接上传GPU无需解压，这是块压缩格式相比JPEG等格式在虚拟纹理场景下的决定性优势。

虚拟纹理与**GPU驱动渲染（GPU Driven Rendering）**结合时，反馈Pass可以与可见性剔除Pass合并，在同一个Compute Shader中同时输出遮挡剔除结果和虚拟纹理反馈数据，消除独立反馈Pass的开销。理解虚拟纹理后，进一步研究Nanite（UE5几何体虚拟化）时会发现两者在分层LOD、按需流式加载、反馈驱动调度上共享完全相同的设计哲学，只是将纹理Page换成了几何体Cluster。