---
id: "cg-forward-plus"
concept: "Forward+"
domain: "computer-graphics"
subdomain: "rasterization"
subdomain_name: "光栅化"
difficulty: 3
is_milestone: false
tags: ["架构"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# Forward+ 渲染管线

## 概述

Forward+ 是由 Takahiro Harada、Jay McKee 和 Jason C. Yang 于 2012 年在 AMD 提出并发表（论文标题为 *Forward+: Bringing Deferred Lighting to the Next Level*）的一种渲染管线。它在传统 Forward 渲染基础上引入了**屏幕空间分块光源剔除（Tiled Light Culling）**步骤，将每帧的光源列表按屏幕瓦片（Tile）预先分组，使片元着色器只处理影响本瓦片的光源，从而突破传统 Forward 渲染在大量动态光源场景下的性能瓶颈。

与延迟渲染（Deferred Rendering）相比，Forward+ 不依赖 G-Buffer 存储几何信息，因此可以天然支持透明物体渲染、MSAA 抗锯齿以及多种材质混合，这些场景在延迟渲染中实现成本极高。Forward+ 的核心代价是一个独立的光源剔除计算通道（Compute Pass），但在现代 GPU 的 Compute Shader 支持下，这一开销通常远小于延迟渲染维护 G-Buffer 的带宽消耗。

该技术在 2012 年前后被多个主流游戏引擎采用，2014 年发布的《孤岛危机3》PC 版即使用了类似的分块光照策略。Unity HDRP 和 Unreal Engine 也在某些配置下使用 Forward+ 作为透明物体的光照路径。

## 核心原理

### 第一通道：深度预通道（Depth Prepass）

Forward+ 管线的第一步是渲染整个场景的深度缓冲，只写入深度值而不执行任何光照计算。此通道的目的是为后续光源剔除提供精确的深度范围（`z_min` 和 `z_max`），同时在正式着色通道中开启 **Early-Z** 优化，彻底消除过度绘制（Overdraw）带来的冗余着色开销。没有这一步，光源剔除的深度范围将无从确定，剔除精度大幅降低。

### 第二通道：分块光源剔除（Tiled Light Culling）

这是 Forward+ 最关键的阶段，通过 Compute Shader 执行。屏幕被均匀划分为若干 **Tile**，典型尺寸为 **16×16 像素**。对每个 Tile，GPU 线程组（Thread Group）执行以下操作：

1. 从深度缓冲中读取本 Tile 内所有像素的深度，归约（Reduce）得到 `z_min` 和 `z_max`，构造该 Tile 的**视锥体（Frustum）**。
2. 遍历场景中所有光源，对每个点光源执行**球体-视锥体相交检测**（Sphere vs. Frustum）：若光源影响半径的球体与 Tile 视锥体相交，则将该光源索引写入本 Tile 的光源列表。
3. 输出结果为两个缓冲区：`LightIndexList`（全局光源索引列表）和 `LightGrid`（每个 Tile 在列表中的偏移量与光源计数）。

Tile 数量计算公式为：
$$N_{tiles} = \lceil W / T_w \rceil \times \lceil H / T_h \rceil$$
其中 $W$、$H$ 为屏幕分辨率，$T_w$、$T_h$ 为 Tile 宽高（通常均为 16）。在 1920×1080 分辨率下，16×16 的分块产生 120×68 = 8160 个 Tile。

### 第三通道：带光源列表的正式着色通道

正式的前向渲染通道中，每个片元着色器通过像素坐标计算所属 Tile 编号，查询 `LightGrid` 获取该 Tile 的光源偏移和数量，仅对这些光源执行 BRDF 着色计算。相比传统 Forward 渲染对所有 N 个光源循环，每片元的有效光源数量从 N 降至平均数十个，使着色复杂度从 O(片元数 × 总光源数) 降低为 O(片元数 × 每Tile平均光源数)。

## 实际应用

**游戏场景中的大量点光源**：在地下城或城市夜景场景中，可放置数百个动态点光源（火把、霓虹灯）。使用 Forward+，每个 Tile 实际参与着色的光源通常仅 10-30 个，总光源数对帧率的影响从线性变为近似常数。

**透明物体与半透明特效**：粒子系统、玻璃、水面等透明物体在延迟渲染中无法直接存入 G-Buffer 而需要特殊处理，而 Forward+ 着色通道本质上是 Forward 渲染，透明物体直接受益于完整的分块光源列表，无需任何额外管线分支。

**VR 渲染**：VR 场景需要同时渲染双眼视图，G-Buffer 的存储带宽在此场景下翻倍。Forward+ 因无 G-Buffer 而在 VR 应用中内存带宽表现优于延迟渲染，Valve 的 SteamVR 渲染路径曾专门针对此做过对比测试。

## 常见误区

**误区一：Forward+ 与延迟渲染性能孰优孰劣是固定的**。实际上，二者的性能边界取决于场景中光源密度与透明物体比例。在光源极度密集、Tile 内光源数仍然很多（如超过 256 个）时，Forward+ 的着色通道性能会急剧下降；而延迟渲染在这一场景下表现更稳定。

**误区二：Forward+ 的分块剔除在深度不连续处没有问题**。这是错误的。当一个 Tile 内同时包含近处前景和远处背景（深度不连续，如窗口边缘），`z_min` 到 `z_max` 的范围会被拉得很大，导致该 Tile 错误地收纳大量本不影响前景或背景的光源，产生**假阳性（False Positive）**。这一问题正是后续**簇式渲染（Clustered Rendering）**将剔除维度从 2.5D 扩展至真正 3D 的直接动机。

**误区三：深度预通道是可选的**。省略深度预通道后，光源剔除阶段无法获取可靠的 `z_min`/`z_max`，视锥体深度范围将被设为 [0, far]，使剔除有效性几乎归零，等同于退化为普通 Forward 渲染。深度预通道虽引入约 10%-15% 的额外几何处理开销，但对 Forward+ 的正确性是强制性的。

## 知识关联

Forward+ 的学习以**延迟渲染**为前置背景：理解 G-Buffer 的构造和延迟光照通道的带宽瓶颈，才能理解 Forward+ 为何选择放弃 G-Buffer 而转向计算预处理；延迟渲染中每像素处理所有光源的问题，直接促成了分块剔除思想的诞生。

Forward+ 中暴露的**深度不连续导致假阳性剔除**问题，直接引出下一个演进技术——**簇式渲染（Clustered Shading）**。簇式渲染由 Olsson 等人于 2012 年提出，将屏幕空间分块扩展为视锥体空间三维分簇，彻底解决深度方向上的剔除精度问题，可视为 Forward+ 分块思想在 Z 轴方向的自然延伸。