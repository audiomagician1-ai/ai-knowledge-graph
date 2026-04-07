---
id: "cg-vertex-transform"
concept: "顶点变换"
domain: "computer-graphics"
subdomain: "rasterization"
subdomain_name: "光栅化"
difficulty: 2
is_milestone: false
tags: ["数学"]

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



# 顶点变换

## 概述

顶点变换（Vertex Transformation）是光栅化管线中将3D几何体从其原始定义坐标系逐步转换到屏幕坐标系的完整变换链。每个三角形的三个顶点都要经历相同的矩阵乘法序列，最终得到可以被光栅器处理的二维像素坐标。这条变换链通常被称为"MVP变换"，即模型矩阵（Model Matrix）× 观察矩阵（View Matrix）× 投影矩阵（Projection Matrix）的连续乘积。

这一流程由Jim Clark等人在1970年代为几何管线建立理论基础，后来在OpenGL 1.0（1992年发布）中被固定功能管线正式实现为标准流程。理解顶点变换的意义在于：GPU每帧可能需要对数百万个顶点执行这一链式矩阵乘法，因此将MVP三个矩阵预乘为单一4×4矩阵`MVP = P × V × M`，是最基本的GPU性能优化手段之一。

## 核心原理

### 模型空间到世界空间：模型矩阵

模型空间（Model Space）也称为局部空间，是美术在建模软件中定义顶点坐标时所使用的坐标系。模型矩阵 **M** 是一个4×4的仿射变换矩阵，负责将顶点从局部坐标系变换到统一的世界坐标系，它编码了三种变换：
- **平移（Translation）**：将物体放置到世界中的指定位置
- **旋转（Rotation）**：使用旋转矩阵或四元数确定物体朝向
- **缩放（Scale）**：改变物体的大小比例

变换公式为 $\mathbf{v}_{world} = \mathbf{M} \cdot \mathbf{v}_{local}$。顶点坐标使用齐次坐标表示为4维向量 $(x, y, z, w)$，其中 $w=1$ 表示点，$w=0$ 表示向量（方向），这一区分使得平移操作可以用矩阵乘法统一表达。

### 世界空间到观察空间：观察矩阵

观察矩阵 **V**（View Matrix）将整个世界坐标系重新定位，使摄像机位于原点，且摄像机的观察方向与 $-Z$ 轴对齐（OpenGL约定）。这一变换等价于把"摄像机移动到场景前方"改写成"场景移动到摄像机前方"。

构造观察矩阵最常用的是 `LookAt` 算法：给定摄像机位置 $\mathbf{eye}$、目标点 $\mathbf{center}$ 和上向量 $\mathbf{up}$，计算出正交基向量 $\mathbf{f}=\text{normalize}(\mathbf{center}-\mathbf{eye})$、$\mathbf{r}=\text{normalize}(\mathbf{f} \times \mathbf{up})$、$\mathbf{u}=\mathbf{r} \times \mathbf{f}$，再组装成旋转矩阵与平移矩阵的乘积。变换公式为 $\mathbf{v}_{view} = \mathbf{V} \cdot \mathbf{v}_{world}$。

### 观察空间到裁剪空间：投影矩阵

投影矩阵 **P** 将观察空间中的顶点变换到裁剪空间（Clip Space）。透视投影矩阵将视锥体（由近裁剪面 $n$、远裁剪面 $f$、垂直视角 $fov_y$、宽高比 $aspect$ 定义）映射到一个标准化的裁剪立方体中。在OpenGL中该立方体为 $[-1,1]^3$，在Direct3D中深度范围为 $[0,1]$。

经过投影矩阵后，顶点的 $w$ 分量不再等于1，而是存储了原始的观察空间深度值（负的 $z_{view}$）。此时坐标 $(x_{clip}, y_{clip}, z_{clip}, w_{clip})$ 被称为裁剪坐标，硬件在此空间内执行视锥裁剪，再将坐标除以 $w_{clip}$（透视除法）得到NDC（归一化设备坐标）。

## 实际应用

**Unity中的MVP矩阵**：在Unity的HLSL Shader中，顶点着色器输入语义为 `POSITION`，开发者通过 `UnityObjectToClipPos(v.vertex)` 完成完整的MVP变换，其本质是执行 `mul(UNITY_MATRIX_MVP, v.vertex)`。Unity将 M、V、P 三个矩阵预乘好后上传GPU，节省了着色器内部的矩阵乘法开销。

**骨骼动画中的多级模型矩阵**：带蒙皮的角色模型中，每个顶点受多块骨骼影响。每块骨骼有独立的模型矩阵，顶点位置 = $\sum_{i} w_i \cdot \mathbf{M}_{bone_i} \cdot \mathbf{v}_{local}$，其中 $w_i$ 为蒙皮权重且各权重之和为1。这一操作在顶点着色器中完成，是顶点变换步骤的直接扩展。

**法线变换的特殊性**：顶点变换不仅作用于位置，还作用于法线向量。但法线不能直接乘以模型矩阵 **M**，当模型存在非均匀缩放时，必须使用法线矩阵 $\mathbf{N} = (\mathbf{M}^{-1})^T$（M的逆矩阵的转置）来变换法线，否则光照计算会产生错误。

## 常见误区

**误区一：矩阵乘法顺序可以任意调换**。MVP中矩阵乘法不满足交换律，$\mathbf{P}\mathbf{V}\mathbf{M} \neq \mathbf{M}\mathbf{V}\mathbf{P}$。顶点向量应从右往左与矩阵依次相乘：$\mathbf{v}_{clip} = \mathbf{P} \cdot \mathbf{V} \cdot \mathbf{M} \cdot \mathbf{v}_{local}$。混淆行向量/列向量约定（OpenGL用列向量，DirectX用行向量）是导致这类Bug的常见原因。

**误区二：裁剪空间坐标就是NDC坐标**。许多初学者将经过投影矩阵后的裁剪坐标直接当作NDC使用。实际上裁剪坐标还需要经过透视除法（每个分量除以 $w_{clip}$）才能得到NDC。顶点着色器输出裁剪坐标，透视除法由GPU硬件自动完成，这是着色器可编程阶段与固定功能阶段的边界。

**误区三：观察矩阵只是移动摄像机**。观察矩阵实际上是摄像机变换的逆矩阵——摄像机向右移动10个单位，等价于整个世界向左移动10个单位。因此 `LookAt` 函数生成的 **V** = $(RT)^{-1} = T^{-1}R^{-1}$，忽视这一逆变换关系会导致摄像机控制逻辑出现方向反转的问题。

## 知识关联

顶点变换依赖对**图形管线阶段**的理解，因为必须清楚顶点着色器是管线中第一个可编程阶段，MVP变换正是在这里以代码形式执行。顶点变换的输出直接送入**投影变换**阶段——透视投影矩阵的具体参数设置（$fov$、$n$、$f$）以及透视除法后深度值的精度分布问题，是投影变换的核心讨论内容。此外，理解裁剪空间坐标和齐次坐标 $w$ 分量的含义，是学习**透视正确插值**和**深度缓冲**的必要前提，因为深度值的非线性分布正是由透视除法引起的。