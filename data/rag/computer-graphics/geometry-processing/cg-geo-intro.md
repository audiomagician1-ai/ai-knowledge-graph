---
id: "cg-geo-intro"
concept: "几何处理概述"
domain: "computer-graphics"
subdomain: "geometry-processing"
subdomain_name: "几何处理"
difficulty: 1
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.419
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 几何处理概述

## 概述

几何处理（Geometry Processing）是计算机图形学的一个分支领域，专门研究如何在计算机中**表示、分析、转换和渲染三维几何形状**。其研究对象是三维物体的形状数据，包括顶点坐标、拓扑连接关系、法线、纹理坐标等几何属性，以及对这些数据执行的一系列操作。

几何处理的正式研究起源可追溯至1990年代。1994年Hoppe等人发表的网格简化论文（Progressive Meshes的前身）和1997年正式提出的渐进网格（Progressive Meshes）标志着几何处理作为独立研究方向的成熟。在游戏与实时渲染领域，GPU渲染管线中几何着色器（Geometry Shader）的引入（Direct3D 10，2006年）使得在GPU端直接处理几何数据成为可能，进一步推动了实时几何处理技术的发展。

几何处理的重要性体现在**三维数据链条的每个环节**：从3D扫描仪采集的原始点云需要重建为网格，游戏引擎需要根据距离动态降低模型复杂度以保证帧率，影视特效中的布料和流体模拟需要每帧更新数百万个几何顶点。若没有高效的几何处理算法，现代实时渲染无法在每秒60帧的约束下处理包含数千万三角形的复杂场景。

## 核心原理

### 几何表示的四类主要方法

三维几何形状在计算机中有四种主流表示方式，各有适用场景：

1. **边界表示（Boundary Representation, B-Rep）**：用三角网格或多边形面描述物体表面，是实时渲染最常用的格式。一个标准三角网格由顶点列表（Vertex Buffer）和索引列表（Index Buffer）构成，每个三角形由3个顶点索引定义。
2. **隐式表示（Implicit Surface）**：用函数 $f(x,y,z) = 0$ 定义表面，例如符号距离场（Signed Distance Field, SDF）。球体可表示为 $f(x,y,z) = x^2 + y^2 + z^2 - r^2 = 0$。
3. **参数表示（Parametric Surface）**：通过参数方程 $\mathbf{P}(u,v)$ 映射到三维空间，Bézier曲面和NURBS曲面属于此类，广泛用于CAD建模。
4. **点云（Point Cloud）**：仅存储三维采样点坐标，无拓扑连接信息，是激光雷达（LiDAR）和深度相机的直接输出格式。

### 几何处理管线的标准阶段

实际工程中，一条完整的几何处理管线通常包含以下阶段，顺序如下：

- **数据采集/建模**：通过3D扫描或美术建模生成原始几何数据，此阶段往往产生含有噪声、孔洞或自相交的"脏网格"。
- **网格修复与清理**：检测并修复非流形边（Non-manifold Edge）、孤立顶点、退化三角形（面积为0的三角形）等问题，使网格满足流形（Manifold）条件。
- **几何优化**：包括网格简化（将百万面模型降至数千面）、网格重网格化（Remeshing，使三角形分布均匀）、曲面光顺（Smoothing）等操作。
- **运行时处理**：在渲染前对几何数据进行视锥体剔除（Frustum Culling）、LOD选择、骨骼蒙皮（Skeletal Skinning）等实时操作。

### 欧拉公式与网格的拓扑约束

网格的拓扑结构受欧拉公式约束：对于一个亏格（Genus）为 $g$ 的封闭流形网格，顶点数 $V$、边数 $E$、面数 $F$ 满足：

$$V - E + F = 2 - 2g$$

球体的亏格 $g=0$，故 $V - E + F = 2$；甜甜圈形状（Torus）的亏格 $g=1$，故 $V - E + F = 0$。这一公式在网格修复和有效性检测中被直接使用，用于判断网格是否满足封闭流形条件。

## 实际应用

**游戏资产管线**：在Unreal Engine或Unity中，美术制作的高模（High-poly，数百万面）经由烘焙（Baking）将细节转移到法线贴图，再配合经过简化的低模（Low-poly，数千面）在运行时渲染。这一流程的核心就是网格简化与LOD构建。

**三维重建**：使用iPhone或iPad的LiDAR扫描仪采集点云后，需要通过泊松表面重建（Poisson Surface Reconstruction，Kazhdan等，2006年提出）算法将离散点云转换为连续三角网格，整个过程涉及法线估计、隐式函数拟合和Marching Cubes等多个几何处理步骤。

**角色动画**：蒙皮网格动画中，每个顶点的最终位置由线性混合蒙皮（Linear Blend Skinning, LBS）公式计算：$\mathbf{v}' = \sum_{i} w_i \mathbf{M}_i \mathbf{v}$，其中 $w_i$ 是骨骼权重，$\mathbf{M}_i$ 是骨骼变换矩阵。这是实时角色渲染中每帧必须执行的几何处理操作。

## 常见误区

**误区一：网格顶点数越少性能一定越好。** 实际上，顶点数只是影响GPU性能的因素之一。顶点属性（法线、多套UV坐标、顶点色）每增加一个通道就增加额外带宽，而过度简化导致法线贴图无法正确采样，反而可能需要额外的Pass来修正。性能瓶颈更多出现在Draw Call数量和纹理采样上，而非单纯的顶点数。

**误区二：点云和网格可以随意互换使用。** 点云不包含拓扑连接信息，无法直接用于光栅化渲染管线（因为光栅化需要三角形图元）。将点云转换为网格是一个非平凡的重建问题，会引入重建误差，且不同重建算法（如Ball Pivoting算法 vs 泊松重建）对噪声的处理方式差异显著。

**误区三：隐式表示（SDF）不适合实时渲染。** SDF在传统光栅化中确实不直接使用，但现代实时渲染广泛采用SDF：Lumen全局光照系统用SDF加速光线步进，字体渲染用MSDF（多通道SDF）实现任意缩放的清晰轮廓，Nanite虚拟几何系统也在可见性判断中使用类SDF的距离数据结构。

## 知识关联

**后续概念的分工**：本概念建立了几何处理的整体框架，后续各专题分别深入其中一个方向：**网格表示**专门讲解半边数据结构等用于高效存储和遍历三角网格拓扑的数据结构；**LOD系统**深入探讨网格简化算法（如Quadric Error Metrics，Garland & Heckbert 1997）和运行时LOD切换策略；**参数曲面**详细讲解Bézier、B-Spline和NURBS的数学原理；**点云处理**聚焦法线估计、降噪和表面重建算法；**实例化渲染**解决如何用单一几何数据高效绘制大量相同物体的问题。

几何处理与图形管线的关系：几何处理主要发生在CPU端的资产管线和顶点着色器之前，但现代图形API（Vulkan、DirectX 12）提供的**网格着色器（Mesh Shader）**已将网格剔除和LOD选择推入GPU，使得几何处理与渲染管线之间的界限进一步模糊。