---
id: "cg-cube-mapping"
concept: "立方体贴图"
domain: "computer-graphics"
subdomain: "texture-techniques"
subdomain_name: "纹理技术"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "A"
quality_score: 85.2
generation_method: "intranet-llm-rewrite-v3"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v3"
  - type: "academic"
    author: "Greene, Ned"
    year: 1986
    title: "Environment Mapping and Other Applications of World Projections"
    venue: "IEEE Computer Graphics and Applications, Vol. 6, No. 11, pp. 21–29"
  - type: "academic"
    author: "Ramamoorthi, Ravi & Hanrahan, Pat"
    year: 2001
    title: "An Efficient Representation for Irradiance Environment Maps"
    venue: "ACM SIGGRAPH 2001 Proceedings, pp. 497–500"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v3
updated_at: 2026-04-06
---

# 立方体贴图

## 概述

立方体贴图（Cubemap）是一种由6张正方形纹理图像组成的特殊纹理类型，这6张图像分别对应一个虚拟立方体的六个面：正X（+X）、负X（−X）、正Y（+Y）、负Y（−Y）、正Z（+Z）、负Z（−Z）。采样时不使用传统的二维UV坐标，而是使用一个从立方体中心出发的三维方向向量，GPU根据该向量的最大分量确定采样哪个面，再将剩余两个分量换算为该面上的二维坐标。这种采样机制使立方体贴图天然适合表达"从某一点向四面八方观察"的全向信息。

立方体贴图最早在1986年由Ned Greene在论文《Environment Mapping and Other Applications of World Projections》（IEEE Computer Graphics and Applications, Vol. 6, No. 11）中系统提出，作为球面映射的替代方案。与球面贴图相比，立方体贴图在极点处不存在严重的像素拉伸问题，且可以用标准双线性过滤进行平滑采样。OpenGL在1.3版本（2001年）将立方体贴图纳入核心规范（`GL_TEXTURE_CUBE_MAP`），此后它成为实时渲染中最基础的全向纹理形式。DirectX 8.0同年也将其列为`D3DRTYPE_CUBETEXTURE`类型，进一步确立了其跨API的标准地位。

立方体贴图之所以重要，在于它用6张共计 $6N^2$ 个像素的图像，以较低的存储代价近似编码了场景中某点的完整球面视野，直接支撑了天空盒渲染、实时环境反射和动态漫反射辐照度等多项核心技术。

---

## 核心原理

### 方向向量到面坐标的映射

给定一个三维方向向量 $\mathbf{r} = (r_x, r_y, r_z)$，GPU首先找到绝对值最大的分量，设其绝对值为 $m = \max(|r_x|, |r_y|, |r_z|)$。若 $|r_x|$ 最大且 $r_x > 0$，则采样+X面；以此类推共6种情形。随后，另两个分量被线性映射到 $[0,1]$ 区间，计算公式为：

$$u = \frac{1}{2}\left(\frac{s_c}{m} + 1\right), \quad v = \frac{1}{2}\left(\frac{t_c}{m} + 1\right)$$

其中 $s_c$、$t_c$ 是与该面对应的另两个分量（各面的 $s_c/t_c$ 映射方向在OpenGL规范附录F中有精确定义）。这一步骤完全在硬件纹理单元（TMU）中完成，开发者只需向片元着色器传入方向向量即可，无需手动做坐标变换。

**例如**：若方向向量为 $\mathbf{r} = (0.8, 0.3, -0.5)$，则 $|r_x| = 0.8$ 最大，采样+X面，$m = 0.8$，此时 $s_c = -r_z = 0.5$，$t_c = r_y = 0.3$，代入公式得 $u = 0.5 \times (0.5/0.8 + 1) = 0.8125$，$v = 0.5 \times (0.3/0.8 + 1) = 0.6875$，即在+X面纹理上的采样坐标。

### 存储规模与分辨率权衡

设立方体贴图每面分辨率为 $N \times N$，则总像素数为：

$$P_{\text{cube}} = 6N^2$$

与之对比，覆盖相同角分辨率的等距柱状全景图（Equirectangular Panorama）的常用分辨率为 $2N \times N$，总像素数为：

$$P_{\text{equirect}} = 2N^2$$

两者之比 $P_{\text{cube}} / P_{\text{equirect}} = 3$，说明立方体贴图总像素数是等距柱状图的3倍。然而等距柱状图在极点处存在严重冗余（角分辨率极不均匀），有效信息量与立方体贴图相当，这是两种格式各有适用场景的根本原因。

### 天空盒渲染原理

天空盒利用立方体贴图模拟无限远的天空背景。实现时，以摄像机位置为中心绘制一个单位立方体，顶点着色器中**去除观察矩阵的平移分量**（只保留旋转部分，即取 `mat4` 的左上 `mat3` 子矩阵），使天空盒始终跟随摄像机旋转而不随平移产生视差。片元着色器将顶点的本地坐标直接作为方向向量采样立方体贴图。深度缓冲写入需设为 `gl_FragDepth = 1.0`，或将天空盒安排在所有不透明几何体之后渲染（Early-Z剔除），确保实体几何体像素覆盖天空盒区域，避免过度绘制（Overdraw）带来的额外带宽消耗。

### 镜面环境反射

对一个反射型表面，片元着色器用入射视线向量 $\mathbf{v}$（指向表面）和表面法线 $\mathbf{n}$ 计算反射向量：

$$\mathbf{r} = \mathbf{v} - 2(\mathbf{v} \cdot \mathbf{n})\,\mathbf{n}$$

即GLSL内置函数 `reflect(v, n)` 的展开形式。用 $\mathbf{r}$ 采样立方体贴图即得该像素"看到"的环境颜色。该技术称为**环境映射（Environment Mapping）**，单次纹理采样即可近似镜面反射，计算代价远低于光线追踪或屏幕空间反射（SSR）。代价在于立方体贴图是预烘焙的静态快照，无法反映动态物体，且隐含假设光源无限远（反射向量不随表面位置发生视差偏移）。

### 动态立方体贴图与漫反射辐照度

动态场景中可将摄像机放置于物体中心，朝6个坐标轴方向各用90°视场角（FOV = 90°，宽高比 = 1:1）渲染一帧，结果写入实时立方体贴图，逐帧或按需更新。此操作每帧需额外6次完整绘制调用（Draw Call），代价高昂，在2023年典型移动端GPU（如Apple A16）上约消耗0.5–2 ms，通常仅对场景中最重要的一两个反射对象执行，或降低动态更新频率（如每隔4帧更新一次）。

另一个进阶用途是将高频镜面立方体贴图通过球谐函数（Spherical Harmonics，SH）压缩为低频漫反射辐照度表示。Ramamoorthi & Hanrahan（2001）在SIGGRAPH论文中证明，漫反射辐照度在球面上变化极为平滑，仅需**L2阶共9个SH系数**（每个颜色通道）即可以99%以上的精度重建，每个系数是一个RGB三元组，整体存储量仅为27个浮点数，远小于一张完整的辐照度立方体贴图。这9个系数经由对原始HDR立方体贴图的球面积分卷积运算预计算得到，用于PBR材质的环境漫反射项（Irradiance）计算。

---

## 实际应用

**天空盒**是立方体贴图最直接的应用，几乎所有3D游戏和实时渲染引擎均采用此方案。Unity中将6张图片设置为 `Cubemap` 资源类型后，直接赋予天空盒材质（`Skybox/Cubemap` shader）即可；Unreal Engine 5的 `SkyAtmosphere` 系统也可与立方体贴图天空盒结合使用，前者负责大气散射物理计算，后者负责远景云层与星空细节叠加。

**汽车漆面与镜面材质**通过环境映射立方体贴图实现高质量反射效果。游戏《极品飞车：最高通缉》（Need for Speed: Most Wanted，2005）率先在主机平台上大规模使用预烘焙立方体贴图为车漆提供廉价但高质量的反射，此后成为赛车游戏的行业标准做法。在WebGL应用中，Three.js（r150版本及之后）的 `CubeCamera` 类封装了动态立方体贴图的6面渲染流程，开发者可直接调用 `CubeCamera.update(renderer, scene)` 触发更新。

**IBL（基于图像的照明，Image-Based Lighting）**中，HDR格式的立方体贴图（通常由 `.hdr` 或 `.exr` 格式的等距柱状全景图转换而来，分辨率典型值为 $2048 \times 1024$）作为环境光源。经过对不同粗糙度 $\alpha$ 的预过滤（Split-Sum Approximation，由Epic Games的Brian Karis在2013年SIGGRAPH课程中提出），结果存储在立方体贴图的不同Mipmap层级，称为Pre-filtered Environment Map（预过滤环境贴图）。UE4的Lumen全局光照系统出现之前（UE5, 2022年），IBL是实时PBR渲染管线中环境光照的主流解决方案，广泛应用于影视级离线渲染（如Pixar的RenderMan）和游戏引擎的实时渲染路径。

**点光源阴影**也是立方体贴图的重要应用场景。Shadow Cubemap（阴影立方体贴图）将同样的6面渲染思路应用于阴影深度图生成：以点光源为中心向6个方向各渲染一张深度图，合成完整的全向阴影信息。OpenGL 4.6的几何着色器（Geometry Shader）支持在单个Draw Call内通过 `gl_Layer` 内置变量同时输出到立方体贴图的6个面，将原本6次绘制调用缩减为1次，显著降低CPU端驱动开销。

---

## 常见误区

**误区一：立方体贴图6张图的接缝会导致可见裂缝**
早期实现中，相邻面边缘像素采样确实存在接缝问题，但OpenGL 3.2（2009年）引入了 `GL_TEXTURE_CUBE_MAP_SEAMLESS` 标志，启用后GPU会在面边界处执行跨面双线性过滤，彻底消除接缝。开发者需要主动调用 `glEnable(GL_TEXTURE_CUBE_MAP_SEAMLESS)`，忘记启用是出现接缝的最常见原因。Vulkan中等效功能由 `VkSamplerCreateInfo` 结构体的 `flags` 字段中 `VK_SAMPLER_CREATE_NON_SEAMLESS_CUBE_MAP_BIT_EXT` 的**缺省状态**（即默认开启无缝采样）实现。

**误区二：采样立方体贴图的向量必须先手动归一化**
许多教程要求手动 `normalize(r)` 后再采样，但这并非必要——GPU在执行立方体贴图采样时使用向量方向（最大分量符号决定面选择，除以 $|m|$ 做归一化），未归一化的向量只要方向正