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
quality_tier: "S"
quality_score: 82.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---


# 虚拟纹理

## 概述

虚拟纹理（Virtual Texturing），又称稀疏纹理（Sparse Texture），是一种将极大尺寸纹理拆分为固定大小的小块（Tile/Page）并按需流式加载到GPU显存的技术。其核心思想直接借鉴自操作系统的虚拟内存分页机制——程序访问一个远大于物理RAM的"虚拟地址空间"，而只有被访问的页面才真正驻留在物理内存中。虚拟纹理将同样的分页思想移植到纹理采样流程，使渲染引擎能够在不超出GPU显存限制的前提下，使用理论上可达128K×128K甚至更高分辨率的超大纹理。

这项技术由John Carmack在2000年代初期提出原型概念，以"MegaTexture"为名在id Software内部开发，并于2007年随《星球大战：银河战场》系列精神后续作《Enemy Territory: Quake Wars》首次商业落地，用于以单张超大纹理覆盖整个开放地形，避免重复贴图（Texture Tiling）造成的视觉单调感。Sean Barrett随后于2008年在GDC演讲《Sparse Virtual Textures》（Barrett, 2008）中将该思路系统化并公开化，成为后续学术与工业实现的重要参考文献。现代图形API已将稀疏纹理能力标准化：OpenGL 4.3通过`ARB_sparse_texture`扩展提供支持；DirectX 11.2引入了Tiled Resources（Direct3D术语），将GPU显存管理粒度降低到64KB的Tile；Vulkan则通过稀疏绑定（Sparse Binding）和稀疏图像（Sparse Image）在驱动层提供最底层的原生访问。

虚拟纹理解决了开放世界游戏中最棘手的显存瓶颈问题。一张4096×4096、RGBA8格式的纹理未压缩时占用64MB；但若要让整个100km²的地形表面每平方分米都有独特的笔刷细节，等效分辨率纹理需要数百GB，远超任何GPU显存容量。虚拟纹理允许美术人员以极高精度绘制整个世界，而运行时仅将玩家当前视野内、对应Mip层级的数十个Page加载到一张常驻GPU的物理纹理图集（Physical Texture Atlas）中，典型Atlas大小为4096×4096或8192×8192，显存占用稳定在256MB～1GB区间内。

---

## 核心原理

### 页表与间接采样

虚拟纹理的核心数据结构是**页表纹理（Page Table Texture）**，它是一张低分辨率的2D查找纹理，每个像素（Entry）存储当前虚拟Page的驻留状态及其在物理Atlas中的物理坐标偏移。采样一张虚拟纹理时，着色器执行**两级间接采样（Two-Level Indirection）**：

1. 用虚拟UV坐标和计算出的Mip Level查询页表纹理，取得该Page在物理Atlas中的起始偏移 $(p_x, p_y)$；
2. 将虚拟UV对Page内的局部偏移 $(u_{local}, v_{local})$ 与物理偏移合并，计算出最终物理UV，再采样物理Atlas。

设虚拟纹理分辨率为 $V \times V$，Page大小为 $P \times P$ 像素，则Mip Level 0的页表分辨率为 $\frac{V}{P} \times \frac{V}{P}$。以65536×65536的虚拟纹理、128×128的Page尺寸为例，Level 0页表为512×512，Level 1为256×256，共需约10个Mip级别。物理UV的计算公式为：

$$UV_{phys} = \frac{(p_x, p_y) \cdot P + UV_{local} \cdot P}{A}$$

其中 $A$ 为物理Atlas的边长（像素数），$(p_x, p_y)$ 为页表查询得到的物理Page坐标（单位：Page格数），$UV_{local}$ 为虚拟UV在当前Page内的归一化偏移量（0～1）。

页表所有Mip级别通常打包进一张启用硬件Mipmap的RGBA16或RGBA8纹理，R/G通道存储物理偏移的X/Y坐标，B通道存储Mip层级差，以便GPU硬件三线性过滤自动在不同Mip级别的Entry之间插值，减少Mip边界处的跳变瑕疵。

### 反馈缓冲与流式调度

由于GPU着色器无法直接触发CPU端的磁盘IO，虚拟纹理系统通过**反馈缓冲（Feedback Buffer）**机制通知CPU哪些Page需要加载。每帧（或每N帧）执行一个低分辨率的专用Feedback Pass：着色器计算当前屏幕像素所需的虚拟Page地址——包含虚拟纹理ID、Mip Level和Page的XY坐标——并将其写入一张降采样的缓冲纹理，典型分辨率为屏幕的1/8×1/8（例如1920×1080屏幕对应240×135的Feedback Buffer，仅需约259KB）。

CPU端通过异步回读（Async Readback）取回缓冲数据，对所有像素写入的Page请求去重统计，与当前已驻留Page集合做差集，按照优先级（距离玩家越近、Mip Level越细的Page优先级越高）排列任务队列，提交IO线程从硬盘或网络流异步加载对应的压缩Page数据，解压后上传至GPU物理Atlas并更新页表纹理。整个管线典型延迟为2～5帧，对应30fps时约67～167ms。

这套调度系统天然存在**流式延迟（Streaming Latency）**：玩家快速转向时，新视角所需的Page须经历"反馈写入→CPU读回→差集计算→IO加载→GPU上传→页表更新"的完整链路，这期间着色器会回退到已驻留的低精度Mip Level Page进行渲染，表现为纹理从模糊逐渐变清晰的过渡效果（即Mip Fallback）。为缓解这一问题，工程实践中常预测玩家移动方向提前预加载（Prefetch），或保留1～2个额外Mip Level的缓冲余量。

### 物理Atlas管理与Page置换

物理Atlas是一块固定大小的GPU纹理，内部被划分为等大小的Page槽位（Slot）。当新的Page需要加载而Atlas已满时，系统需要执行Page置换（Eviction）。常用的置换策略是**LRU（Least Recently Used）**：CPU端维护一个Page访问时间戳表，将最久未被Feedback Buffer请求的Page从Atlas中驱逐，将其槽位分配给新Page，并将被驱逐Page对应的页表Entry标记为"未驻留"，使着色器自动回退到更粗粒度Mip Level。

实践中物理Atlas的Page槽位数量须经过仔细调优。Atlas过小导致频繁置换、IO压力激增；过大则浪费显存。Epic Games在虚幻引擎5的Nanite/VSM（Virtual Shadow Maps）文档中建议，对于典型AAA开放世界场景，物理Atlas应容纳屏幕像素数的1.5～2倍对应的Page数量，以保证98%以上帧的Page命中率（Epic Games, 2022）。

---

## 关键公式与着色器实现

虚拟纹理的核心采样逻辑可用GLSL伪代码表示如下：

```glsl
// 虚拟纹理采样函数（简化版）
// virtualUV: 原始虚拟纹理UV坐标 [0,1]
// pageTableTex: 页表纹理（所有Mip层级已打包）
// physAtlas: 物理纹理图集
// vtPageSize: 单Page边长（像素），如128
// vtVirtualSize: 虚拟纹理边长（像素），如65536
// atlasSize: 物理Atlas边长（像素），如4096

vec4 SampleVirtualTexture(vec2 virtualUV,
                          sampler2D pageTableTex,
                          sampler2D physAtlas,
                          float vtPageSize,
                          float vtVirtualSize,
                          float atlasSize)
{
    // 1. 计算需要的Mip Level（使用屏幕空间导数）
    float mipLevel = textureQueryLod(pageTableTex, virtualUV).y;

    // 2. 查询页表，取得物理Page坐标 (pageCoord.xy) 和存储的mip偏差
    vec4 pageEntry = textureLod(pageTableTex, virtualUV, mipLevel);
    vec2 physPageOrigin = pageEntry.xy; // 归一化物理Page坐标

    // 3. 计算Page内局部UV
    float pagesPerDim = vtVirtualSize / vtPageSize; // = 512 (for 65536/128)
    vec2 withinPageUV = fract(virtualUV * pagesPerDim);

    // 4. 将局部UV映射到物理Atlas中的最终UV
    float pageSizeInAtlas = vtPageSize / atlasSize; // = 128/4096 = 0.03125
    vec2 physUV = physPageOrigin + withinPageUV * pageSizeInAtlas;

    // 5. 采样物理Atlas（禁用硬件Mip，手动控制LOD）
    return textureLod(physAtlas, physUV, 0.0);
}
```

上述代码中，`physPageOrigin` 是从页表纹理读取的归一化坐标，直接对应物理Atlas中该Page槽位的左上角位置。注意步骤5中必须使用 `textureLod(..., 0.0)` 而非 `texture()` 自动Mip，否则GPU硬件会对物理Atlas再次计算LOD，产生错误的跨Page采样。

---

## 实际应用

### 开放世界地形渲染

虚拟纹理最典型的应用场景是开放世界地形。传统做法使用若干张1024×1024或2048×2048纹理瓦片（Terrain Tile）在地形上重复拼贴，即便混合多层材质也难以消除视觉重复感。虚拟纹理方案（如《刺客信条：奥德赛》的Ubisoft实现）将整个地形作为单一虚拟纹理域，允许美术在虚拟纹理画布上直接"绘制"地表细节——一块干裂的河床、一条被踏踩的小道、一个阵营的营地标记——每处细节在全局唯一，不会重复出现在地图其他位置。

案例：《赛博朋克2077》的夜之城场景总面积约17km²，地表材质纹理若以每像素2cm精度覆盖全地图则需约85000×85000分辨率，超过7.2GB（未压缩RGBA8）。虚拟纹理系统将其划分为每Page 128×128的块，物理Atlas维持在4096×4096（64MB），运行时仅加载玩家周围约500m范围内的Page，通常同时驻留约800个Page，实际显存占用控制在50MB以内。

### 虚拟阴影贴图（Virtual Shadow Maps）

虚拟纹理技术近年延伸到阴影贴图领域。虚幻引擎5的Virtual Shadow Maps（VSM）将单光源的阴影贴图虚拟分辨率设为16K×16K甚至更高，仅将视锥体内实际接受阴影计算的Page实例化到物理内存中，彻底解决了Cascaded Shadow Maps（CSM）在级联边界处的精度跳变问题（Epic Games, 2022）。VSM的Feedback Pass与颜色渲染的VT Feedback Pass可合并执行，减少额外的渲染开销。

---

## 常见误区

**误区一：Page越小越好**
减小Page尺寸（如从128×128降至32×32）会使同等物理Atlas面积内可驻留的Page数量增加16倍，看似能提升覆盖率，实则带来两个严重问题：①页表纹理尺寸按平方增长，65536×65536虚拟纹理配合32×32 Page需要2048×2048的Level 0页表，显存和带宽开销显著上升；②每次IO加载的粒度过细，磁盘读取效率低下（固态硬盘随机4KB读取与顺序读取吞吐量差距可达10倍以上）。工业标准Page大小通常为128×128或256×256像素。

**误区二：虚拟纹理消除了纹理压缩的必要性**
物理Atlas中存储的Page数据仍应使用GPU原生压缩格式（BC7/ASTC），而非未压缩数据。以BC7格式（压缩比约8:1）存储的128×128 Page仅需2KB，而未压缩RGBA8需16KB。物