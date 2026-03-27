---
id: "cg-clustered-rendering"
concept: "簇式渲染"
domain: "computer-graphics"
subdomain: "rasterization"
subdomain_name: "光栅化"
difficulty: 4
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 49.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 簇式渲染

## 概述

簇式渲染（Clustered Rendering）是一种将视锥体（View Frustum）划分为三维体素网格（称为"簇"，Cluster）的光照计算方法，由Ola Olsson等人于2012年在论文《Clustered Deferred and Forward Shading》中正式提出。与Forward+仅在屏幕XY平面上切分Tile的方式不同，簇式渲染额外在深度方向Z轴也进行分割，将视锥体切分为数百乃至数千个三维体积单元。

这种三维分簇策略直接解决了Forward+的深度复杂度（Depth Complexity）问题。在Forward+中，一个2D Tile内如果存在深度跨度极大的多层物体，该Tile对应的光源列表会包含所有深度上的光源，造成过度着色；而簇式渲染因为沿Z轴分层，每个簇仅包含真正与该空间体积重叠的光源，光源列表更精确。现代商业引擎如Unreal Engine 5的Lumen前身系统、Unity HDRP以及id Software的《DOOM Eternal》均采用了基于簇的光照裁剪。

## 核心原理

### 视锥体的三维分簇方案

簇式渲染最常见的做法是将屏幕XY轴均匀划分（如16×9个格子），而Z轴（深度方向）则采用指数分布划分。Z轴第 $k$ 个簇的近平面深度为：

$$z_k = z_{near} \cdot \left(\frac{z_{far}}{z_{near}}\right)^{k/K}$$

其中 $K$ 为Z轴总分层数，$z_{near}$ 和 $z_{far}$ 分别为相机的近裁剪面和远裁剪面距离。使用指数分布而非线性分布，是因为透视投影下近处物体在屏幕上占据更多像素，近处需要更密集的分层来保证光照精度，而远处稀疏分层即可。典型配置为 $16 \times 9 \times 24 = 3456$ 个簇，或 $32 \times 18 \times 64 = 36864$ 个更高精度的配置。

### 光源与簇的分配（光源裁剪阶段）

每一帧在GPU上运行一个计算着色器（Compute Shader），遍历场景中所有活跃光源，将每盏光源的包围体（点光源用球体，聚光灯用锥体）与每个簇的AABB（轴对齐包围盒）进行相交测试。通过测试的光源索引被写入一个全局光源索引列表（Global Light Index List），同时维护一张索引偏移表（Cluster Index Table），记录每个簇的光源列表在全局索引列表中的起始偏移量和数量。这两张表在着色阶段被绑定为着色器资源视图（SRV），像素着色器通过当前像素的深度和屏幕位置计算出所在簇编号，再从偏移表查询对应光源列表，只对这些光源计算光照贡献。

### Clustered Forward与Clustered Deferred的区别

Clustered Forward Shading直接在几何体前向渲染通道中使用簇索引查询光源列表，适合透明物体和MSAA（多重采样抗锯齿），因为它仍在单个Pass中完成着色。Clustered Deferred Shading则将几何信息先写入GBuffer（法线、反照率、金属度等），再在后处理的Lighting Pass中遍历屏幕像素查询对应簇的光源列表。Deferred变体的优势在于着色计算量与几何复杂度解耦，过深的场景不会重复执行昂贵的BRDF计算；但它无法直接支持透明物体着色，且GBuffer带宽开销显著，在移动端受限于内存带宽往往不适用。两者共用相同的簇构建和光源分配步骤，仅着色阶段不同。

## 实际应用

在《DOOM (2016)》中，id Software使用了 $16 \times 8 \times 24$ 的簇配置，场景中同屏支持超过300盏动态点光源而不显著降低帧率，这在Forward+时代很难实现，因为Forward+的Tile光源列表在室内场景深度复杂时会急剧膨胀。Unity HDRP的簇光照系统将每个簇的最大光源数上限设置为24盏，超出限制时按光源与簇中心距离排序后截断，确保GPU不会因单个簇的光源列表过长而引发寄存器溢出（Register Spilling）。

Unreal Engine 4的前向渲染器（Forward Renderer，非延迟路径）也采用了簇式结构，专门为VR场景服务。VR应用需要MSAA，而Deferred Shading与MSAA兼容性差，因此Clustered Forward是VR多光源场景的标准解决方案。其典型簇分辨率为屏幕空间 $8 \times 8$ 像素一格，Z轴32层，在HTC Vive分辨率（2160×1200）下约产生 $270 \times 150 \times 32 \approx 130$ 万个簇，但大量空簇（无几何体）会被Early-Out跳过。

## 常见误区

**误区一：簇越多越好**。增加簇的数量会成倍增大光源分配阶段的Compute Shader工作量，以及GPU需要维护的偏移表大小。当每个簇内平均光源数已经足够少（如1-3盏）时，继续细分只会增加构建开销而不减少着色开销。实践中Z轴超过64层后在大多数场景下收益递减。

**误区二：簇式渲染能完全消除过度绘制**。簇式渲染仅解决光源裁剪的精度问题，但一个簇内仍可能有多个不透明物体叠加（几何过度绘制）。消除几何过度绘制需要配合Pre-Z Pass或GPU驱动渲染（GPU Driven Rendering）中的遮挡剔除，而非簇本身的功能。

**误区三：簇编号可以直接从线性深度计算**。必须使用非线性的指数深度公式（即前述 $z_k$ 公式的逆变换）将当前像素的线性摄像机空间深度转换为簇Z索引，否则在透视投影下近处的簇索引计算会出现严重误差，导致像素被映射到错误的簇，产生光照突变的视觉瑕疵。正确的Z索引计算公式为 $k = \lfloor \log(z/z_{near}) / \log(z_{far}/z_{near}) \cdot K \rfloor$。

## 知识关联

簇式渲染是Forward+技术的直接三维扩展。Forward+将XY屏幕空间划分为2D Tile（通常16×16像素），簇式渲染在此基础上将Z轴也纳入划分维度，因此理解Tile光源列表的构建和Compute Shader光源裁剪流程是学习簇式渲染的直接前置。两者的光源分配Compute Shader逻辑高度相似，区别仅在于簇的几何形状由2D矩形变为3D锥台切片（Frustum Slice），相交测试从圆柱体裁剪变为球体与AABB的3D相交测试。

从图形学管线的更宏观视角看，簇式渲染可与虚拟阴影贴图（Virtual Shadow Maps）结合，以簇的范围决定哪些阴影贴图页面需要更新，这是Unreal Engine 5中Nanite与虚拟阴影贴图联动的底层机制之一。此外，簇的空间数据结构本身也被用于非光照用途，如体积雾（Volumetric Fog）的介质散射计算，每个簇存储该空间体积内的散射/吸收系数，与光源列表并行计算，实现高效的逐簇体积光照积分。