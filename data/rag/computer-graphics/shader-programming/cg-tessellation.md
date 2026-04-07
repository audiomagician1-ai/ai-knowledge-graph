---
id: "cg-tessellation"
concept: "细分着色器"
domain: "computer-graphics"
subdomain: "shader-programming"
subdomain_name: "Shader编程"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "S"
quality_score: 91.4
generation_method: "ai-rewrite-v3"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v3"
  - type: "academic"
    author: "Nießner, M., Loop, C., Meyer, M., & DeRose, T."
    year: 2012
    title: "Feature Adaptive Subdivision for Displacement Mapping"
    venue: "ACM SIGGRAPH Asia 2012"
  - type: "academic"
    author: "Vlachos, A., Peters, J., Boyd, C., & Mitchell, J. L."
    year: 2001
    title: "Curved PN Triangles"
    venue: "ACM Symposium on Interactive 3D Graphics"
  - type: "book"
    author: "Pettineo, M."
    year: 2013
    title: "Introduction to 3D Game Programming with DirectX 11"
    venue: "Mercury Learning and Information"
  - type: "book"
    author: "Luna, F."
    year: 2016
    title: "Introduction to 3D Game Programming with DirectX 12"
    venue: "Mercury Learning and Information"
  - type: "book"
    author: "Shreiner, D., Sellers, G., Kessenich, J., & Licea-Kane, B."
    year: 2013
    title: "OpenGL Programming Guide: The Official Guide to Learning OpenGL, Version 4.3"
    venue: "Addison-Wesley Professional"
  - type: "academic"
    author: "Catmull, E., & Clark, J."
    year: 1978
    title: "Recursively generated B-spline surfaces on arbitrary topological meshes"
    venue: "Computer-Aided Design, 10(6), 350-355"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v3
updated_at: 2026-04-06
---


# 细分着色器

## 概述

细分着色器（Tessellation Shader）是Direct3D 11与OpenGL 4.0分别于2009年和2010年正式引入的可编程管线阶段，专门负责在GPU上动态增加几何体的三角形密度。与顶点着色器每次处理一个顶点不同，细分着色器以**图元补丁（Patch）**为操作单位，将一个粗糙的低多边形补丁细分成大量小三角形，实现无需修改CPU端网格数据的动态几何细化。OpenGL 4.0规范于2010年3月由Khronos Group正式发布，NVIDIA GeForce 400系列（Fermi架构，2010年3月发布）是最早全面支持该规范的消费级GPU；AMD Radeon HD 5000系列（Evergreen架构，2009年发布）则是最早支持Direct3D 11细分功能的消费级显卡。

该技术的直接动机是解决3D模型的LOD（Level of Detail）困境：传统做法需要美术预先制作多套精细度不同的模型，而细分着色器允许引擎存储一套低面数基础网格，在渲染时根据相机距离、屏幕投影面积等实时条件自适应地增加三角形数量。Valve的Source 2引擎和Unreal Engine 4均采用该技术实现地形与角色的动态曲面细分，在镜头拉近时自动呈现更丰富的几何细节，而无需CPU端参与任何LOD切换逻辑。此外，DirectX 12与Vulkan的引入进一步降低了驱动层开销，使细分着色器在移动平台（如搭载Apple M系列GPU的设备，从M1 Pro起支持Metal着色语言的细分功能）也逐步具备实用价值。

**问题引入**：为什么不直接在CPU端生成高精度网格，而要在GPU上动态细分？在一个包含1000个地形补丁的场景中，若每帧在CPU端根据相机距离重新生成网格，将消耗大量CPU带宽并产生严重的内存分配压力；而细分着色器将这一计算完全卸载到GPU，CPU仅需传递粗糙的控制点数据即可，这是细分着色器设计的根本出发点。更进一步地思考：**当细分因子从32提升至64时，三角形数量增加约4倍，但视觉改善往往不足10%——如何在质量与性能之间找到最优平衡点，是每位图形工程师必须掌握的核心能力？**

## 核心原理

### 三阶段流水线结构

细分功能由三个连续阶段共同完成，缺一不可：

**1. Hull Shader（外壳着色器）**：每个补丁执行一次，输出**细分因子（Tessellation Factor）**——具体包含外部边因子（决定补丁边缘划分数）和内部因子（决定补丁内部划分数）。以四边形（Quad）补丁为例，共输出6个浮点数：4个边缘因子（对应4条边各自的细分段数）+ 2个内部因子（分别控制水平与垂直方向的内部网格密度）。以三角形补丁为例，则输出3个边缘因子 + 1个内部因子，共4个浮点数。Hull Shader同时透传或修改每个控制点的属性数据（位置、法线、UV坐标等）供Domain Shader使用。在Direct3D 11 HLSL中，Hull Shader以 `[domain("quad")]`、`[partitioning("fractional_odd")]`、`[outputtopology("triangle_cw")]` 等属性标注其细分模式。

需要特别注意的是，一个补丁（Patch）可最多包含32个控制点（Direct3D 11规范限制），控制点数量与细分因子完全解耦——即便只有3个控制点的三角形补丁，也可以被细分至因子64，生成约4096个小三角形。Hull Shader在Direct3D 11中分为两个子函数：**常量函数（Constant Hull Shader）**专门计算细分因子，每补丁执行一次；**控制点函数（Control Point Hull Shader）**对每个控制点执行一次，用于修改或透传控制点属性。两者的分离设计使GPU驱动可以提前剔除细分因子为0的补丁，无需浪费资源执行控制点变换。

**2. 固定功能细分器（Tessellator）**：这一阶段不可编程，由GPU硬件依据Hull Shader输出的因子，在归一化参数空间 $(u, v) \in [0,1]^2$ 中生成均匀（integer）、奇数分式（fractional_odd）或偶数分式（fractional_even）分布的参数坐标集合，并输出细分后的索引连接关系。细分因子范围通常为1.0～64.0的浮点数：等于1时不产生任何新顶点，等于4时四边形补丁产生约25个顶点，等于64时单个四边形补丁可细分产生约4225个顶点（即65×65网格）。fractional_even分区模式会在因子从偶数过渡到下一偶数时平滑地插入新顶点，从而避免LOD切换时出现突变的几何跳变（popping artifact）。

三角形补丁的细分器在参数空间中使用重心坐标 $(\lambda_1, \lambda_2, \lambda_3)$ 描述新顶点，而四边形补丁使用 $(u, v)$ 双参数坐标。Open-GL对应阶段称为**曲面细分控制着色器（Tessellation Control Shader, TCS）**和**曲面细分评估着色器（Tessellation Evaluation Shader, TES）**，功能上与HLSL的Hull/Domain Shader一一对应（Shreiner et al., 2013）。

**3. Domain Shader（域着色器）**：对固定功能细分器生成的每个新参数坐标 $(u, v)$ 执行一次，利用重心坐标或双线性插值将参数坐标映射为实际三维世界空间坐标。位移贴图（Displacement Map）的采样通常在此处进行——读取一张高度纹理，将新顶点沿法线方向偏移，从而真正隆起几何细节而非仅靠法线贴图欺骗光照。Domain Shader的输出格式与顶点着色器完全相同，后续管线（几何着色器、光栅化）对此无感知差异。

值得注意的是，Domain Shader中**不可以**调用 `tex2D`（隐式LOD采样），必须使用 `SampleLevel` 或 `SampleGrad` 等显式LOD版本，因为细分阶段处于管线的几何处理期，GPU无法自动推算屏幕空间导数来确定mipmap级别。这是初学者最容易遭遇的编译错误之一。

### 细分因子的自适应计算

Hull Shader的核心任务是计算**自适应细分因子**，常见策略是基于屏幕空间边长估算。设某条补丁边的世界空间长度为 $L$（单位：米），屏幕高度像素数为 $H$（单位：像素），垂直视场角为 $\theta$（单位：弧度），相机到补丁边中点的距离为 $d$（单位：米），则使该边在屏幕上每段约占 $p$ 像素的理想细分因子为：

$$T = \text{clamp}\!\left(\frac{L \cdot H}{2d \cdot \tan(\theta/2) \cdot p},\ T_{\min},\ T_{\max}\right)$$

其中 $T_{\min}$ 通常设为1，$T_{\max}$ 通常设为64（Direct3D 11硬件上限）。此公式保证屏幕上每段边长稳定在约 $p$（常取8～16）像素，镜头近时因子高，远时因子低，避免过度绘制造成GPU浪费。

**例如**，在一个分辨率为1920×1080、垂直FOV为60°（$\theta = \pi/3$）、目标像素段长 $p=8$ 的场景中，一条世界空间长度为2米的补丁边，相机距离为5米时，理想细分因子为：

$$T \approx \frac{2 \times 1080}{2 \times 5 \times \tan(30°) \times 8} = \frac{2160}{2 \times 5 \times 0.5774 \times 8} \approx \frac{2160}{46.19} \approx 46.8$$

钳制后取46；当相机退至80米时，$T \approx 2.9$，即细分为约3段，贴近实际渲染需求。另一种策略是球形包围盒视锥体裁剪：若整个补丁的球形包围盒在视锥体外，直接将所有细分因子设为0，GPU将丢弃该补丁，无需光栅化任何三角形。

还有一种基于曲率的自适应策略：对控制点法线夹角进行估算，曲率越大的区域分配更高的细分因子。设相邻控制点的法线夹角为 $\alpha$（弧度），补丁的基础细分因子为 $T_{\text{base}}$，曲率增益系数 $k_c$ 通常在1.0～3.0之间调节：

$$T_{\text{curve}} = T_{\text{base}} \cdot \left(1 + k_c \cdot \frac{\alpha}{\pi}\right)$$

此策略使平坦区域以最低细分因子渲染，尖锐弯曲处自动获得更密集的三角网格，是Unreal Engine的地形系统在4.22版本之后采用的混合策略之一。

### Phong曲面细分与PN三角形

Domain Shader中最基础的插值是线性（重心坐标）插值，但这会保留原网格的锋利折痕，使细分后的网格仍然呈多面体外观。**Phong Tessellation**利用控制点的法线将新顶点向切平面投影再混合（Vlachos et al., 2001），具体分两步：

首先计算线性插值位置 $P_{\text{linear}}$，再将其投影到以每个控制点 $P_i$ 为切点、$N_i$ 为法线的切平面上得到 $\Pi_i(P)$：

$$\Pi_i(P) = P - \left[(P - P_i) \cdot N_i\right] N_i$$

最终位置为线性插值位置与投影位置的加权混合：

$$P_{\text{smooth}} = \text{lerp}\!\left(P_{\text{linear}},\ \sum_i \lambda_i \cdot \Pi_i(P_{\text{linear}}),\ \alpha\right)$$

其中 $\lambda_i$ 为重心坐标分量，$\alpha$ 通常取0.75，过高的 $\alpha$ 会导致网格在小角度折痕处