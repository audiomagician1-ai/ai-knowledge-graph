---
id: "ta-lightmap-opt"
concept: "光照贴图优化"
domain: "technical-art"
subdomain: "perf-optimization"
subdomain_name: "性能优化"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.8
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# 光照贴图优化

## 概述

光照贴图（Lightmap）是将场景中静态物体的光照信息预先烘焙并存储在一张纹理贴图中的技术，运行时直接采样该贴图而无需实时计算漫反射全局光照。与实时光照相比，光照贴图可以将复杂的间接光照、阴影和环境光遮蔽计算成本几乎降至零，代价是增加内存占用和磁盘空间。这种时间换空间的策略在移动端和主机平台上尤为关键——在 Quest 2 等移动 VR 平台上，实时全局光照可能直接导致帧率跌破 72Hz 的最低可用标准。

光照贴图技术最早在 Quake（1996）中以"lightmap"形式出现，当时每个多边形面独立存储一张低分辨率光照贴图。现代引擎如 Unity 的 Enlighten / Progressive Lightmapper 和 Unreal Engine 的 Lightmass 系统将多个物体的光照信息打包进同一张图集（Atlas），从而大幅减少采样所需的纹理绑定次数。优化光照贴图不仅影响渲染性能，还直接影响包体大小和加载时间，因此技术美术需要在画质与资源开销之间精确平衡。

## 核心原理

### 光照贴图分辨率的选择

光照贴图分辨率决定了每单位世界空间面积分配多少贴图像素，通常用"Texel per Unit"（或"Texel per Meter"）来衡量。Unity 中默认值为 40 texels/unit，Unreal Engine 的 Lightmass 默认为 2（以厘米为单位）。过低的分辨率会导致光照细节模糊，出现明显的块状漏光（light bleeding）；过高则导致内存浪费和烘焙时间指数级增长。

正确设置分辨率的原则是按物体的视觉重要性分级处理：主角站立区域的地面、墙面等高频接触区域可设 4096×4096 的光照图集，而远景建筑外墙可降至 512×512 甚至 256×256。一块 4096 光照贴图在 ETC2 压缩后约占 8MB，而同等面积的 1024 贴图仅占 0.5MB，因此每降低一个分辨率档位可节省约 4 倍内存。

### 光照贴图图集打包（UV Packing / Atlas）

光照贴图打包是将场景中多个物体的展开 UV（Lightmap UV，即 UV1 通道）尽量紧密地排布在同一张贴图中的过程。打包效率直接影响贴图利用率——若图集利用率低于 60%，意味着超过 40% 的内存被浪费在空白像素上。

高效打包的关键技术点有三个：① UV 岛屿（UV Island）之间须保留 2~4 像素的间距（Padding/Gutter），防止 Mipmap 采样时产生边缘渗色（bleeding）；② 对称几何体（如左右对称建筑）应开启 UV 重叠，让两侧共享同一块 UV 空间，但前提是光照方向相同；③ 物体的 Lightmap UV 不能与 Albedo UV（UV0）共享，必须保证每个三角形在 UV 空间中无重叠、无翻转。Unity 提供了"Generate Lightmap UVs"选项自动展开，但对复杂模型（多于 2000 个三角面）建议在 DCC 软件（如 Houdini 或 Blender）中手动展开以保证质量。

### Indirect Lighting Cache（间接光照缓存）

间接光照缓存（ILC）是专门为场景中**动态物体**提供间接光照信息的技术，解决了动态物体无法采样烘焙光照贴图的问题。Unreal Engine 的 ILC 在空间中均匀放置一组采样点（Sample Point），每个点存储一个三阶球谐（Spherical Harmonics, SH）系数——共 27 个浮点数，描述该位置的全方向间接光照。动态物体运行时在这些采样点之间进行三线性插值，获得所在位置的近似间接光照颜色。

Unity 中对应的技术称为**Light Probe**（光照探针）。两者的核心区别在于采样密度控制方式：Unreal ILC 自动均匀分布，分辨率由 `r.Cache.LightingCacheDimension` 控制（默认值为 32，即 32³ = 32768 个采样点）；Unity Light Probe 则由美术手动摆放，能在光照变化复杂区域（如从室外进入室内的过渡处）集中放置探针。若动态物体在穿越明显光照边界时出现突变，通常是因为该区域探针密度不足。

## 实际应用

**移动端场景优化案例：** 在一个典型的手游街道场景中，总光照贴图预算控制在 4 张 1024×1024（ETC2 压缩，共 2MB）以内是常见目标。实现方法是将场景按视觉区域分块，主街道路面、建筑正面使用独立高分辨率光照贴图（1024），屋顶及背面合并进低分辨率图集（512），门窗等细节构件若无明显光影可直接禁用 `Cast Shadows` 并排除出烘焙计算。

**大型室内场景的 ILC 设置：** 在 Unreal Engine 开发的室内展厅场景中，角色从玻璃天窗下的明亮区域走向展柜暗处时，若不在过渡走廊密集放置 Light Probe / ILC 采样点，角色身上的间接光照会产生约 0.5 秒的滞后感（因为引擎在采样点稀疏时使用了更大范围的插值）。标准做法是在光照梯度变化超过 30% 的区域将探针间距缩减至 50cm 以内。

## 常见误区

**误区一：光照贴图分辨率越高越好。** 许多初学者默认将全场景物体的光照贴图分辨率设置到最大，但这会导致总内存超出平台预算（iOS 设备总纹理预算通常在 256MB~512MB 之间），触发系统自动降级采样，反而出现运行时画质劣化。正确做法是根据物体的屏占比和光照复杂度分配不同分辨率。

**误区二：动态物体只要加了 Light Probe 就能匹配静态光照。** Light Probe 存储的是三阶球谐（L2 SH），最多能表示低频漫反射光照，无法重建镜面反射和高频阴影细节。当角色站在有明显定向阴影的地面时，静态地面有正确的接触阴影，而角色底部却没有对应阴影，这是 Light Probe 的原理性局限，需要额外使用**阴影胶囊体（Capsule Shadow）**或 PCSS 实时阴影弥补。

**误区三：光照贴图 UV 可以复用 Albedo UV。** Albedo UV 通常使用平铺（Tiling）模式，同一张贴图在多个三角面上重叠采样；而光照贴图 UV 要求每个三角面在 0~1 空间内唯一、无重叠，否则多个面会将烘焙光照信息写入同一像素导致叠加错误（称为"UV Overlap Artifact"）。

## 知识关联

光照贴图优化依赖对**性能优化概述**中建立的"CPU/GPU 瓶颈分析"框架，因为判断是否值得提升光照贴图分辨率需要首先通过 GPU 帧分析工具（如 Xcode Metal Debugger 或 RenderDoc）确认当前瓶颈在纹理采样而非顶点处理。光照贴图的内存计算方法（分辨率² × 每像素字节数）与纹理内存管理的知识直接相关，在此基础上才能准确制定全场景光照贴图预算表，确保各平台不超出硬件纹理缓存上限。