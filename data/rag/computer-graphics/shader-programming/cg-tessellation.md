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
content_version: 2
quality_tier: "B"
quality_score: 47.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.414
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 细分着色器

## 概述

细分着色器（Tessellation Shader）是GPU可编程管线中专门负责将低多边形网格动态细分为更密集几何体的着色器阶段，由DirectX 11（2009年发布）和OpenGL 4.0（2010年发布）引入到标准图形API中。与顶点着色器或片元着色器处理已有几何数据不同，细分着色器的核心职责是在渲染时实时"生成"新的顶点和三角形，使得一个仅有数百个三角形的模型能在不修改原始网格数据的情况下，渲染为拥有数万个三角形的平滑曲面。

细分着色器之所以重要，在于它直接解决了传统LOD（Level of Detail）技术中的离散跳变问题。传统LOD方案需要美术预先制作多套网格，并在距离切换时产生肉眼可见的突变。而细分着色器通过可编程的细分因子（Tessellation Factor），可以根据摄像机距离、屏幕空间投影面积或曲率等运行时参数，连续平滑地调整几何密度，实现所谓"自适应LOD"。

## 核心原理

### 三阶段流水线结构

细分着色器并非单一着色器，而是由三个阶段协同工作：**Hull Shader（外壳着色器）**、**Tessellator（固定功能细分器）**和**Domain Shader（域着色器）**，对应OpenGL中的Tessellation Control Shader（TCS）、固定功能Primitive Generator和Tessellation Evaluation Shader（TES）。

**Hull Shader** 以"patch"为输入单位，一个patch通常由3到32个控制点组成。Hull Shader的输出分为两部分：每个控制点的变换后坐标，以及最关键的**细分因子**。细分因子包含外部因子（Outer Tessellation Factor）和内部因子（Inner Tessellation Factor），分别控制patch边缘和内部的细分密度。以三角形patch为例，`SV_TessFactor[3]`控制三条边的细分段数，`SV_InsideTessFactor`控制内部网格密度，这些值均为浮点数，允许在1.0到64.0之间连续变化。

**固定功能细分器**读取Hull Shader输出的细分因子，在归一化的参数空间（UV空间或重心坐标空间）内生成对应密度的顶点位置，这一阶段不可编程，由硬件固定执行。

**Domain Shader** 针对细分器生成的每一个UV参数点被调用一次，负责将参数坐标映射回世界空间。开发者在此阶段使用重心插值或Bézier曲面公式计算实际的3D顶点位置，并可在此处采样位移贴图（Displacement Map）对顶点做高度偏移，这是细分着色器最常见的实际用途之一。

### 细分因子与自适应LOD

自适应LOD的核心公式通常基于屏幕空间投影尺寸：

```
TessFactor = clamp(TargetEdgeLengthPixels / ProjectedEdgeLengthPixels, MinLevel, MaxLevel)
```

其中`ProjectedEdgeLengthPixels`是patch某条边在当前帧投影到屏幕后的像素长度，`TargetEdgeLengthPixels`是目标细分粒度（通常设为8到16像素）。当某条边的屏幕投影长度仅有8像素时，细分因子为1；当投影长度为64像素时，细分因子自动升至8，保证每段边的屏幕占用保持在目标像素附近。相邻两个patch的共享边必须使用相同的外部细分因子，否则会在边界处产生"T形接缝"裂缝。

### PN Triangles与Phong Tessellation

当原始网格缺少高分辨率控制点时，细分着色器需要一套曲面近似方案。**PN Triangles（Point-Normal Triangles）** 是ATI在2001年提出的方案：利用三角形三个顶点的位置和法线，在Hull Shader中构造一个三次Bézier三角面片，共10个控制点，使细分后的曲面自动贴合原本凹凸不平的有机体形状。**Phong Tessellation** 则更为简单，在Domain Shader中沿每个细分顶点投影到其最近法线所定义平面上，计算量更低但效果接近。这两种方案均不依赖额外艺术资产，仅凭原始顶点数据即可产生平滑效果。

## 实际应用

**地形渲染**是细分着色器最经典的使用场景。虚幻引擎4的地形系统将地表划分为多个大型patch，Hull Shader根据摄像机到patch的距离动态输出细分因子，Domain Shader从16位高度图采样`heightmap`纹理并将顶点沿法线方向偏移，单次Draw Call即可渲染出从近处精细岩石到远处平滑山丘的过渡效果，相比预烘焙多套LOD网格节省了约60%的显存占用。

**角色皮肤与布料**同样受益于细分着色器。《使命召唤：现代战争》中的角色面部使用细分着色器配合法线贴图与置换贴图，在近距离特写时动态提升面部三角形数量，使皮肤皱纹产生真实的几何凹凸感，而非单纯依赖法线贴图带来的假3D光照错觉。

**海洋模拟**中，Gerstner波形通过细分着色器在Domain Shader阶段直接在GPU上计算波峰位置，避免了将大规模高分辨率网格上传至GPU的带宽瓶颈，典型实现中海面patch数量可从数十万减少到数千，同时动态细分至近处摄像机前方保持视觉精度。

## 常见误区

**误区一：细分因子设为更高就一定更好。**实际上，细分因子每增加一倍，三角形数量以二次方级别增长——对三角形patch而言，内部细分因子为N时，内部生成的三角形数量约为N²。将细分因子从8提升到32，三角形数量增加约16倍，若此时三角形的屏幕投影面积已小于单个像素（即"过细分"），GPU的光栅化效率会急剧下降，反而比不用细分更慢。一般将最大细分因子控制在64以内，且同时检测patch的屏幕占比是否足以支撑该密度。

**误区二：细分着色器可以完全替代法线贴图。**细分着色器通过位移贴图产生真实几何凹凸，确实比法线贴图在掠射角表现更好，但二者并非互斥。法线贴图处理肉眼难以分辨需要几何细节的高频纹理（如砖缝内的微小裂缝），而细分着色器适合处理影响轮廓线和阴影形状的中低频几何起伏。业界主流做法是细分着色器负责大尺度位移，法线贴图叠加高频表面细节。

**误区三：Hull Shader和Domain Shader可以互换职责。**Hull Shader只能访问整个patch的所有控制点，但其输出的细分因子在Domain Shader执行之前就由固定功能硬件读取——这意味着在Domain Shader中修改细分因子在该帧已经无效。任何需要决定"生成多少个顶点"的逻辑必须在Hull Shader中完成，而"生成的顶点放在哪里"的计算才属于Domain Shader的职责范围。

## 知识关联

**前置概念**：片元着色器处理的是光栅化后的像素，而细分着色器工作在光栅化之前的几何阶段。理解片元着色器中UV坐标插值的原理，有助于理解Domain Shader中重心坐标（Barycentric Coordinates，三个分量u、v、w满足u+v+w=1）如何对控制点属性进行插值，两者的数学机制高度一致但作用空间不同。

**横向关联**：几何着色器（Geometry Shader）同样可以在GPU上生成新顶点，但其每次调用仅能访问单个图元（最多6个顶点），而Hull Shader可访问整个patch的全部控制点（最多32个），这使得细分着色器在曲面近似方面具有几何着色器无法实现的全局连续性。对于需要参数化曲面（如Catmull-Clark细分曲面）的场景，细分着色器是唯一合适的实现路径。