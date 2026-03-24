---
id: "cg-voxel-gi"
concept: "体素全局光照"
domain: "computer-graphics"
subdomain: "global-illumination"
subdomain_name: "全局光照"
difficulty: 4
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 41.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.4
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 体素全局光照

## 概述

体素全局光照（Voxel Global Illumination，简称 VXGI）是一种将场景几何体离散化为三维体素网格，再利用锥形光线追踪（Cone Tracing）在体素空间中模拟光的多次弹射的实时全局光照算法。该方法由 NVIDIA 的 Cyril Crassin 等人于 2011 年在论文《Interactive Indirect Illumination Using Voxel Cone Tracing》中正式提出，其核心思想是以可接受的精度换取远优于路径追踪的实时性能。

VXGI 的前身是基于稀疏八叉树（Sparse Voxel Octree，SVO）的体素化思路。Crassin 在 2010 年的 GigaVoxels 工作中首次探索了利用 CUDA 流式加载稀疏体素的渲染方法，VXGI 则将其延伸至动态全局光照领域。Epic Games 随后在 Unreal Engine 4 中集成了 SVOGI（Sparse Voxel Octree Global Illumination）的简化变体，并最终演化为 Lumen 系统的早期基础。SVOGI 在 UE4 的早期开发版本（约 2013 年）中出现，但因运行时开销过高而被移除并替换为更轻量的方案。

该技术的重要性在于，它是第一批在消费级 GPU 上以接近实时帧率（30fps 以上）实现间接漫反射和间接镜面反射的算法之一，弥补了屏幕空间环境光遮蔽（SSAO）无法处理大范围遮挡和彩色渗色的根本缺陷。

## 核心原理

### 场景体素化

VXGI 的第一阶段是将几何体和材质信息烘焙进三维体素网格。通常采用两级结构：粗粒度的 **稀疏八叉树（SVO）** 存储整体场景，叶节点分辨率常设为 128³ 至 512³ 体素。体素化过程通过 GPU 的几何着色器（Geometry Shader）将三角形投影到 X、Y、Z 三个轴向，对每个轴取最大投影面积的方向进行光栅化，确保薄面几何体也能被正确覆盖——这种技术称为**保守体素化（Conservative Voxelization）**。

每个体素存储的信息包括：归一化后的辐射度（Radiance）、法线方向（通常编码为球谐函数 L1 级别，即 4 个系数）以及不透明度（Opacity）。辐射度注入（Radiance Injection）阶段将阴影贴图中已计算好的直接光照结果写入对应的体素，完成从直接光到体素空间的数据桥接。

### Clipmap 结构与 Mipmap 滤波

为了兼顾近处细节和远处大范围遮挡，VXGI 使用 **Voxel Clipmap** 替代单一分辨率网格。Clipmap 是一种以摄像机为中心的分层网格：最内层 Clip Level 0 覆盖约 5–10 米范围，分辨率最高；每向外一级，覆盖范围翻倍而体素尺寸也翻倍，通常设置 5–6 层。这类似于纹理 Mipmap，但在三维空间中随摄像机移动而滑动更新。

体素数据的各向异性 Mipmap 预滤波是保证锥追踪精度的关键。VXGI 为每个体素的 6 个轴向（±X、±Y、±Z）分别存储一个辐射度值，在锥追踪时根据锥的主方向插值混合这 6 个方向分量，从而模拟各向异性散射效果，避免因单一各向同性值导致的光照方向模糊问题。

### 锥形追踪（Voxel Cone Tracing）

在着色阶段，对于屏幕上每个像素，VXGI 沿着半球方向发射若干条**虚拟锥（Virtual Cone）**。每条锥由一个起点、一个方向和一个半角（Aperture Angle）定义。锥随着传播距离 $t$ 的增大而张开，采样半径为：

$$r(t) = t \cdot \tan(\theta / 2)$$

其中 $\theta$ 为锥的半角。在追踪过程中，每步根据当前锥半径 $r(t)$ 选择对应的 Mipmap 级别（级别 = $\log_2(r / \text{voxelSize})$），从体素结构中三线性采样辐射度和不透明度，累积公式与光线行进（Ray Marching）的前向散射积分相同：

$$L_{\text{out}} = \sum_{i} L_i \cdot (1 - \alpha_{\text{acc}}) \cdot \alpha_i, \quad \alpha_{\text{acc}} \mathrel{+}= (1 - \alpha_{\text{acc}}) \cdot \alpha_i$$

漫反射间接光通常发射 **4–8 条** 半角约为 60° 的宽锥，覆盖整个上半球；镜面间接光发射 **1–2 条** 半角对应材质粗糙度的窄锥（粗糙度为 0 时近似退化为单条光线）。典型实现中每像素锥追踪步数为 16–32 步。

## 实际应用

在游戏引擎中，VXGI 最典型的落地案例是 NVIDIA GameWorks VXGI SDK（2015 年发布），该 SDK 集成于 Unreal Engine 4，能在 GTX 980 上以 1080p 分辨率实现约 8–12ms 的全局光照开销，包含间接漫反射和间接镜面反射两个分量。

建筑可视化和影视预览渲染领域也使用 VXGI 作为实时预览工具。相比离线路径追踪，VXGI 可将数小时的渲染时间压缩至毫秒级，代价是忽略超过 6 级 Clipmap 范围（通常 >100 米）之外的间接光贡献，以及在高频几何细节处产生漏光（Light Leaking）瑕疵。

动态场景处理上，VXGI 支持每帧局部更新体素网格：仅对移动物体所占据的 Clipmap 区域重新体素化，其余区域复用上一帧数据，这使得有限数量的动态物体（如角色、小型道具）不会导致全帧体素化的开销。

## 常见误区

**误区一：认为体素分辨率越高精度越高且开销线性增长。** 实际上体素存储和 Mipmap 预滤波的内存占用随分辨率呈三次方增长：512³ 的体素网格在每体素存储 RGBA16F 六面各向异性数据时约需 6 × 512³ × 8 字节 ≈ 6 GB，远超显存上限。因此生产环境中实际分辨率受到严格约束，128³ 至 256³ 加 Clipmap 分层才是实用方案。

**误区二：认为锥追踪能精确还原尖锐镜面反射。** 锥追踪的精度受限于体素的最小分辨率，当锥半角小于体素角分辨率时（约对应粗糙度 < 0.1），无法区分来自不同体素的高频镜面信息，结果会产生块状模糊。此类情况需与屏幕空间反射（SSR）混合或改用光线追踪补充，这也是 VXGI 在实际管线中通常不单独承担镜面反射的根本原因。

**误区三：将 SVOGI 等同于完整 VXGI。** SVOGI 是 UE4 对 VXGI 的简化实现，它省去了各向异性六面存储，改用单一各向同性辐射度，并限制仅计算间接漫反射而忽略间接镜面。两者在效果和内存布局上存在实质性差异，不可互换概念。

## 知识关联

**前置概念——光传播体积（LPV）** 同样将直接光注入三维网格并向外扩散，但 LPV 使用迭代传播方程（通常 8 次迭代）在固定网格上传递球谐光照，而 VXGI 则通过锥追踪直接从多级 Mipmap 中读取已预积分的辐射度，跳过了迭代传播步骤。这使得 VXGI 的间接镜面反射质量显著优于 LPV，但体素化和 Mipmap 构建的预处理开销高于 LPV 的注入阶段。

**后继概念——Lumen 系统** 是 Unreal Engine 5 对 VXGI 思路的大幅重构：Lumen 引入了有符号距离场（SDF）加速结构替代稀疏八叉树，并将屏幕空间与全局体素两套结构混合使用，还引入了表面缓存（Surface Cache）将辐射度存储在物体表面而非空间体素中，解决了 VXGI 在薄壁几何体处漏光的顽固问题。

**横向关联——混合 GI 方案** 通常将 VXGI 负责的大范围低频间接漫反射与 SSR 负责的屏幕空间镜面反射、以及光照探针负责的天空光照合并，通过权重融合填补各自的盲区，这是现代实时渲染管线中 VXGI 最主要的集成形式。
