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
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 体素全局光照

## 概述

体素全局光照（Voxel-based Global Illumination，VXGI）是一种将场景几何体离散化为三维体素网格，再通过锥形光线追踪（Cone Tracing）在体素结构中近似计算间接光照的实时全局光照技术。其核心思想由NVIDIA研究员Cyril Crassin等人在2011年提出，发表于SIGGRAPH论文《Interactive Indirect Illumination Using Voxel Cone Tracing》，该技术最初称为SVOGI（Sparse Voxel Octree Global Illumination），通过稀疏八叉树（Sparse Voxel Octree）压缩三维体素数据的存储开销。

VXGI区别于屏幕空间技术（如SSAO、SSGI）的根本在于它维护了一份全屏幕外的三维辐射度缓存，因此相机转动或物体从屏幕边缘离开视锥时，间接光照不会出现突然消失的"边缘失效"问题。NVIDIA在2015年的Maxwell架构显卡上随UE4的VXGI插件将此技术推向工业实践，典型体素分辨率为128³或256³，在GTX 980级别GPU上可实现30fps以上的帧率。

该技术之所以重要，在于它以远低于离线路径追踪的计算代价同时捕获漫反射间接光照、高光间接光照（镜面间接光照）以及软阴影效果，尤其适合动态光源和动态物体频繁改变的游戏场景。

## 核心原理

### 场景体素化

VXGI的第一阶段将场景三角形网格通过GPU几何着色器（Geometry Shader）光栅化为填充三维纹理的体素数据。具体做法是沿X、Y、Z三个主轴分别执行正交投影，对每个体素存储其包含的表面法线（压缩为球谐或方向八面体编码）、反照率（Albedo）以及存储直接光照结果的自发光项。体素化的空间分辨率通常在64³至512³之间，较低分辨率会导致几何细节丢失，较高分辨率则使填充三维纹理的显存占用急剧上升（256³的RGBA8格式需占用64MB）。

体素化完成后还需要构建Mipmap金字塔：将相邻8个体素通过各向异性过滤合并为父级体素，沿光锥方向扩张时可以采样不同LOD层级，这样在锥追踪步进距离增大时自动切换到更粗的体素层级，避免欠采样走样。各向异性体素（Anisotropic Voxels）方案将每个体素拆分为±X、±Y、±Z共6个方向的辐射度分量，保证斜向锥追踪时的方向性正确，代价是显存翻6倍。

### 锥形光线追踪

给定着色点 **p** 和半球方向，VXGI沿半球均匀分布若干根锥射线（漫反射通常使用5～8根，高光使用1根）进行步进积分。每一步的采样距离 **d** 与锥半角 **θ** 满足关系式：

> **r = d · tan(θ)**

其中 **r** 为当前步进位置处的锥截面半径，对应选取的Mipmap层级为 **log₂(2r / voxelSize)**。每步读取体素颜色 **C** 和透明度 **α**，采用前到后的Alpha合成（Front-to-Back Compositing）累积辐射度：

> **C_out = C_out + (1 - α_out) · C**
> **α_out = α_out + (1 - α_out) · α**

当 **α_out** 接近1或步进距离超过最大追踪距离（通常为场景包围盒直径的1/4到1/2）时停止步进。漫反射锥的半角约60°，高光锥的半角由表面粗糙度决定，粗糙度越小则锥越细，逼近镜面反射行为。

### 注入阶段与动态更新

直接光照的计算结果需要"注入"到体素结构中，才能作为间接光照的一次弹射来源。注入分两类：静态光源可预先烘焙，动态光源（包括阴影贴图采样）每帧重新注入。为降低每帧全量体素化的开销，Unreal Engine的VXGI插件引入了裁剪体素网格（Clipmap Voxel Grid），类似层叠阴影贴图（CSM）的思路，以摄像机为中心维护多个嵌套分辨率的体素簇，距离摄像机越远的区域体素尺寸越大（通常每级放大2倍），仅对摄像机附近的体素执行高频更新。

## 实际应用

在《孤岛危机3》（Crysis 3）的PC版本中，Crytek早期实验性地集成了体素锥追踪原型，验证了实时漫反射间接光照对湿润植被表面的效果。NVIDIA GameWorks的VXGI SDK曾在《彩虹六号：围攻》的光照预研阶段使用，室内场景中能看到红色地毯的红色溢色（Color Bleeding）投射到相邻白色墙壁上，这一效果用传统光照贴图需数小时烘焙，而VXGI可实时响应破坏性环境的几何变化。

在Unreal Engine 4中，VXGI作为插件版本（基于NVIDIA驱动扩展）提供，需要额外配置`r.VXGI.Enable=1`并指定体素网格分辨率参数`r.VXGI.VoxelizationBrickDim`。与光传播体积（LPV）相比，VXGI在高光间接光照的质量上优势明显，代价是GPU计算开销约高出40%～60%（同等场景规模下），因此在主机平台上鲜有采用，主要见于中高端PC配置的视觉化项目。

## 常见误区

**误区一：体素分辨率越高效果一定越好。** 实际上，体素分辨率提高会带来体素化阶段的几何走样加剧（细薄物体如栏杆可能完全丢失），同时Mipmap金字塔的层级压缩误差也不会随分辨率提高而消失。漏光（Light Leaking）问题通常源于体素尺寸大于被遮挡物的厚度，提高全局分辨率不如针对性地使用各向异性体素或调整锥起点偏移量（Cone Offset）来缓解。

**误区二：VXGI与路径追踪的单次弹射效果等价。** VXGI的锥追踪积分是近似的：它仅读取体素中存储的来自直接光照的平均辐射度，而非真实地在空间中追踪光子路径；体素的各向异性压缩会丢失高频方向信息。因此VXGI不能正确模拟焦散（Caustics）或超过一次弹射的多重间接光照，它的物理正确性受限于体素化的空间分辨率和方向精度。

**误区三：VXGI可以完全替代光照贴图。** VXGI的体素分辨率决定了其空间精度上限（例如256³体素覆盖100米场景时，每个体素约39cm³），对于小尺寸的接触阴影（Contact Shadow）或精细缝隙漏光，精度远不及离线烘焙的2cm分辨率光照贴图。实践中VXGI通常与静态光照贴图配合，前者负责动态对象的间接光照，后者承担静态精细阴影。

## 知识关联

**前置概念——光传播体积（LPV）**：LPV同样将场景划分为三维网格并传播辐射度，但它通过迭代扩散方程（Propagation Pass）传播光照，而非锥追踪。LPV的网格单元使用二阶球谐（9个系数）存储方向性辐射度，VXGI则通过各向异性6方向分量存储，二者在表示精度上的权衡不同。理解LPV的RSM（反射阴影贴图）注入流程有助于理解VXGI注入阶段的设计动机。

**后续概念——Lumen系统**：UE5的Lumen系统可以视为VXGI思路的工程化演进，它同样维护体素场景表示（Global SDF + Surface Cache），但用有向距离场（SDF）替代体素八叉树进行光线步进，用Radiance Cache替代直接锥追踪读取，大幅改善了中远距离的间接光照质量和性能。对比VXGI的固定Clipmap层级，Lumen的Surface Cache以屏幕适应性更新，解决了VXGI在大型开放世界中体素精度不足的问题。

**后续概念——混合GI方案**：工业界主流选择是将VXGI或类似体素技术与屏幕空间反射（SSR）、辐射度探针（Radiance Probe）叠加使用，VXGI负责近场动态间接光照，探针负责中远场低频环境光，SSR负责屏幕内可见几何的高频反射，三者分工合作构成混合GI管线。