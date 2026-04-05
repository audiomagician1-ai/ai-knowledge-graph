---
id: "global-illumination"
concept: "全局光照"
domain: "game-engine"
subdomain: "rendering-pipeline"
subdomain_name: "渲染管线"
difficulty: 3
is_milestone: false
tags: ["光照"]

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

# 全局光照

## 概述

全局光照（Global Illumination，GI）是一类模拟光线在场景中经过多次反射、折射、散射后最终到达观察者眼睛的渲染算法总称。与局部光照（Local Illumination）只计算光源直接照射表面的单次交互不同，全局光照需要追踪光线在多个表面之间的间接传播路径，因此能够产生颜色渗透（Color Bleeding）、焦散（Caustics）、环境遮蔽（AO）以及漫反射间接光等真实感效果。

全局光照的理论基础是1986年由James Kajiya提出的**渲染方程（Rendering Equation）**：

$$L_o(\mathbf{x}, \omega_o) = L_e(\mathbf{x}, \omega_o) + \int_\Omega f_r(\mathbf{x}, \omega_i, \omega_o)\, L_i(\mathbf{x}, \omega_i)\, (\omega_i \cdot \mathbf{n})\, d\omega_i$$

其中 $L_o$ 是出射辐射率，$L_e$ 是自发光项，$f_r$ 是BRDF，$L_i$ 是来自方向 $\omega_i$ 的入射辐射率，$\mathbf{n}$ 是表面法线。该方程的递归性（$L_i$ 本身又依赖另一个 $L_o$）正是全局光照计算困难的根本原因。

在游戏引擎渲染管线中，全局光照直接决定场景是否具有真实感的环境氛围，纯局部光照模型会产生阴影部分完全黑暗的"塑料感"。现代引擎为此发展出光照贴图、光线追踪、DDGI等多种实现策略，各自在质量、性能和动态性之间做出不同权衡。

## 核心原理

### 光照贴图（Lightmap）

光照贴图是一种离线预计算全局光照的经典方案，将场景中静态几何体表面的间接光照信息烘焙到一张UV展开的纹理（Lightmap Texture）上。运行时只需采样这张纹理并叠加到直接光照结果之上，几乎不消耗运行时计算资源。

Lightmap的核心质量参数是**Texel密度**（通常以 texels/meter² 表示），Unreal Engine中高质量场景的角色周边地面可达 64 texels/m²，而远景墙面可低至 2 texels/m²。烘焙过程本质上是在GPU或CPU上运行路径追踪（Path Tracing），对每个Texel发射数百到数千条采样射线以收敛积分结果。Lightmap的最大限制是**只适用于静态物体**，动态物体和可移动光源无法获益，且场景修改后必须重新烘焙。

### 动态漫反射全局光照（DDGI）

DDGI（Dynamic Diffuse Global Illumination）由NVIDIA在2019年随DirectX Raytracing推广，核心思想是在场景中均匀布置**探针网格（Probe Grid）**，每个探针每帧通过少量射线（通常每探针128~512条）采样周围辐射率，将结果编码为**球谐函数（Spherical Harmonics，SH）**或**Irradiance Volume**。运行时场景中的任意动态表面都可以通过三线性插值（Trilinear Interpolation）从周围8个探针中获取间接光照估算值。

DDGI的关键改进在于**探针失效检测**：当探针位于几何体内部时，系统通过可见性射线检测并降低该探针的权重，避免光照漏光（Light Leaking）问题。整体显存开销约为每个探针一张 $6\times6$ 像素的Irradiance八面体贴图加一张相同尺寸的Depth贴图。

### 光线追踪全局光照（RT GI）

硬件加速光线追踪依赖NVIDIA Turing架构（2018年，RTX 20系列）以来的**RT Core**专用单元，在加速结构（BVH，Bounding Volume Hierarchy）上执行光线-三角形求交，使得每帧每像素追踪1~4条次级反射/漫反射射线成为实时可行的方案。

RT GI通常与**时序降噪（Temporal Denoising）**结合使用，利用历史帧数据（历史累积权重典型值约为0.1~0.3的指数移动平均）将每像素极少采样数的噪声输出平滑为可用结果。完整的路径追踪（每像素数千次采样）仍只能用于离线渲染，实时RT GI本质上是欠采样路径追踪加后处理降噪的组合。

### Irradiance与辐照度探针

辐照度（Irradiance，单位 W/m²）是全局光照运行时缓存系统中最常存储的物理量，因为漫反射表面对入射光方向的余弦权重积分可预先用低阶SH（通常L2阶，共9个系数，每个系数3个颜色通道，总计27个浮点数）来表示，重建误差对于粗糙漫反射表面可忽略不计。这是Lightmap、DDGI和Lumen Light Cache共同使用的基础表示形式。

## 实际应用

在**Unreal Engine 5**中，Lumen系统在近距离使用屏幕空间追踪（Screen Space Tracing），中远距离回退到软件光线追踪的**Signed Distance Field（SDF）**上，最终将结果注入Radiance Cache（即一种DDGI变体）中，使玩家可以在主机平台（PS5/Xbox Series X）上以30fps获得动态全局光照。

在**Unity HDRP**中，Adaptive Probe Volumes（APV，Unity 2023 LTS正式发布）允许开发者在物体密集区域增大探针密度，在开阔区域稀疏分布，解决了早期固定网格探针导致的显存浪费问题。

光照贴图至今仍是移动端（iOS/Android）项目的主流GI方案，因为移动GPU缺乏RT Core且运算能力有限，Unity的Enlighten和UE的GPU Lightmass均支持GPU加速烘焙，将原本数小时的离线烘焙压缩至数分钟。

## 常见误区

**误区一：认为环境光遮蔽（AO）等同于全局光照。**  
AO只计算几何遮挡对环境光的衰减（Zhukov等人1998年提出实时SSAO），不追踪任何光线的多次反射路径，无法产生颜色渗透或间接高光。将SSAO/HBAO+视为GI是对两类算法本质的混淆：AO输出的是0到1的标量遮蔽因子，而GI输出的是完整的辐射率或辐照度值。

**误区二：认为Lightmap烘焙质量只与采样数有关。**  
实际上Lightmap的最终质量还严格依赖UV展开的质量（每个Texel必须对应唯一且连续的表面区域，不能有UV重叠），以及Texel密度是否与表面在屏幕上的投影像素密度匹配。采样数足够高但UV拉伸严重的Lightmap仍然会出现明显的光照模糊或接缝。

**误区三：认为DDGI探针越密集结果越准确。**  
探针密度提升会增加显存和每帧的射线总量，但探针间距小于几何细节（如薄墙、窗框）时，反而会因为探针位于墙体两侧而导致插值混合错误光照（漏光）。DDGI的精度上限由每个探针的射线数和失效检测质量共同决定，而非单纯的空间密度。

## 知识关联

**前置概念**方面，延迟渲染（Deferred Rendering）为全局光照提供了G-Buffer中的法线、反照率、深度数据，这些数据是屏幕空间GI算法（SSGI、RTGI降噪）的必要输入；Lumen全局光照是Unreal Engine对多种GI技术的集成封装，理解Lumen的内部分层结构（屏幕空间→SDF追踪→Radiance Cache）需要先掌握本文所述的Irradiance探针和DDGI基本原理。

**后续概念**方面，引擎光线追踪在全局光照之上进一步扩展到镜面反射（Specular GI）、折射、半透明阴影和焦散等更高阶光传输效果，需要在掌握BVH结构、时序降噪和RT Core工作原理的基础上，将漫反射GI的探针采样扩展为完整的多次弹射路径追踪。