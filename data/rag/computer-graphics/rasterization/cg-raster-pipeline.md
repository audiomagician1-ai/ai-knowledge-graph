---
id: "cg-raster-pipeline"
concept: "图形管线阶段"
domain: "computer-graphics"
subdomain: "rasterization"
subdomain_name: "光栅化"
difficulty: 1
is_milestone: false
tags: ["基础"]

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

# 图形管线阶段

## 概述

图形管线（Graphics Pipeline）是将三维场景数据转换为二维屏幕像素的标准化处理流程，由应用阶段（Application Stage）、几何阶段（Geometry Stage）、光栅化阶段（Rasterization Stage）和像素阶段（Pixel Stage）四个主要阶段依次构成。每个阶段接收上一阶段的输出并产生下一阶段的输入，形成数据单向流动的"管线"结构。

这一流程的概念体系最早由Foley、van Dam等人在1990年出版的《Computer Graphics: Principles and Practice》中系统阐述，此后随着实时渲染硬件的发展，由Akenine-Möller等人在《Real-Time Rendering》中进一步精炼为现代通用表述。现代GPU（如NVIDIA的Turing架构）在硬件层面将这四个阶段的大部分步骤以并行流水线形式实现，使得不同图元的不同阶段可以同时执行。

理解图形管线阶段的意义在于：每个阶段操作的数据类型和空间完全不同——应用阶段处理的是世界中的几何对象，几何阶段处理的是三维顶点，光栅化阶段生成的是屏幕上的片元（Fragment），像素阶段最终写入的是帧缓冲中的颜色值。弄清楚每一步的"输入是什么、输出是什么"是理解渲染程序行为的基础。

---

## 核心原理

### 应用阶段：CPU端的场景准备

应用阶段完全运行在CPU上，其核心任务是将场景中需要渲染的几何体、材质、光源信息打包，通过Draw Call提交给GPU。这一阶段负责视锥剔除（Frustum Culling）——判断哪些物体完全在摄像机视锥之外从而跳过渲染，这是唯一可以在整体物体粒度上剔除几何数据的阶段。应用阶段的输出是一批顶点缓冲（Vertex Buffer）和索引缓冲（Index Buffer），以及与之关联的着色器程序和状态参数。现代引擎中Draw Call数量是该阶段性能的关键瓶颈，过多的Draw Call会导致CPU到GPU的通信开销成为瓶颈。

### 几何阶段：顶点的空间变换

几何阶段在GPU上运行，以**单个顶点**为处理单位，将顶点从模型局部坐标系经由世界空间、相机空间最终投影到裁剪空间（Clip Space）。这一流程中最关键的变换链为：

$$P_{clip} = M_{proj} \cdot M_{view} \cdot M_{model} \cdot P_{local}$$

其中 $M_{model}$ 为模型矩阵，$M_{view}$ 为观察矩阵，$M_{proj}$ 为投影矩阵，$P_{local}$ 为顶点在局部坐标系中的齐次坐标。几何阶段还包含图元装配（Primitive Assembly）步骤，将独立顶点重新组合为三角形、线段或点等图元，以及针对视锥的裁剪操作，将跨越裁剪平面的三角形切割为新三角形。

### 光栅化阶段：三角形到片元的离散化

光栅化阶段接收经过透视除法后处于NDC（Normalized Device Coordinates）空间中的三角形，判断屏幕上哪些像素位置被该三角形覆盖，并为每个被覆盖的像素生成一个**片元（Fragment）**。这一判断使用重心坐标（Barycentric Coordinates）：对屏幕上任意点 $(x, y)$，计算其相对于三角形三个顶点 $v_0, v_1, v_2$ 的重心坐标 $(\lambda_0, \lambda_1, \lambda_2)$，当且仅当三者均在 $[0, 1]$ 范围内且之和为1时该点在三角形内部。重心坐标同时用于对顶点属性（如法线、纹理坐标、颜色）进行透视正确插值，这是光栅化阶段最核心的计算任务。

### 像素阶段：片元到最终颜色的计算

像素阶段（在Direct3D中称Pixel Shader Stage，在OpenGL中称Fragment Shader Stage）以逐片元为单位执行可编程的着色计算，输入为光栅化阶段插值得到的片元属性，输出为该片元的最终颜色值和深度值。在着色计算完成后，片元还要依次经过：深度测试（Depth Test，使用Z-buffer比较当前片元深度与缓冲中已有值）、模板测试（Stencil Test）、混合（Blending，用于透明效果，公式为 $C_{out} = \alpha \cdot C_{src} + (1-\alpha) \cdot C_{dst}$）。只有通过所有测试的片元才会最终写入帧缓冲，呈现在屏幕上。

---

## 实际应用

**延迟渲染对管线阶段的重组**：在延迟渲染（Deferred Rendering）中，渲染被拆分为两个Pass。第一个Pass的像素阶段不执行光照计算，只将法线、漫反射颜色、粗糙度等几何信息写入G-Buffer（Geometry Buffer，通常由4张或更多全屏纹理组成）。第二个Pass则完全跳过几何阶段中的复杂物体，改为渲染一个全屏四边形，在像素阶段读取G-Buffer并完成所有光照计算。这种做法将光照计算的复杂度从 $O(几何体数量 \times 光源数量)$ 降低为 $O(像素数量 \times 光源数量)$，正是对四阶段流程深度理解后的工程优化。

**移动端的Tile-Based渲染**：ARM Mali、Apple A系列GPU等移动端GPU采用Tile-Based Deferred Rendering（TBDR）架构，将光栅化阶段和像素阶段的处理单位改为屏幕上固定大小的Tile（通常16×16或32×32像素）。几何阶段的输出先被排列到各Tile的图元列表中，再逐Tile执行光栅化和像素着色，使得整个Tile的操作数据可以全部驻留在片上高速缓存中，极大减少了对主内存的带宽消耗。

---

## 常见误区

**误区一：光栅化阶段等同于整个渲染管线**。初学者常将"光栅化渲染"这一术语与四阶段管线混淆，认为"光栅化"就是全部流程。实际上"光栅化渲染"是相对于"光线追踪渲染"的技术路线名称，其内部仍然包含完整的四个阶段。"光栅化"单独作为阶段名称时，仅指三角形离散化为片元这一特定步骤，是整个管线中的第三个阶段。

**误区二：四个阶段严格串行，前一阶段完成后才开始下一阶段**。真实GPU实现中，管线是流水线化（Pipelined）的：当第一个三角形的顶点正在执行像素阶段时，第二个三角形的顶点已经在执行几何阶段，第三批顶点可能正在被应用阶段提交。正是这种重叠执行使GPU吞吐量远高于顺序处理。

**误区三：应用阶段在管线中作用微小，只是"数据准备"**。应用阶段是唯一运行在CPU上、可以访问完整场景逻辑的阶段，因此只有在这里才能执行AI驱动的LOD（Level of Detail）切换、基于物理模拟的骨骼动画更新、以及复杂的空间加速结构（如BVH）遍历。这些计算若放在GPU的几何阶段或像素阶段中执行，将面临严重的数据访问限制。

---

## 知识关联

学习图形管线阶段需要以**光栅化概述**中"屏幕空间离散化"的基本概念为前提，理解为何三维世界需要被转换为二维像素阵列，以及片元与像素的区别。

在此基础上，各阶段可以进一步深入展开：**顶点变换**专注于几何阶段中的矩阵运算链，**裁剪**专注于几何阶段末期的视锥裁剪算法，而**前向渲染**则是以四阶段管线为基础、对像素阶段中光照计算组织方式的具体技术方案。理解了管线的完整结构，才能判断某一渲染技术的优化属于哪个阶段，以及其瓶颈为何出现在CPU或GPU的特定单元上。