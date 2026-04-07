---
id: "cg-ray-intersection"
concept: "光线求交"
domain: "computer-graphics"
subdomain: "ray-tracing"
subdomain_name: "光线追踪"
difficulty: 2
is_milestone: false
tags: ["数学"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "A"
quality_score: 79.6
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

# 光线求交

## 概述

光线求交（Ray Intersection）是光线追踪渲染流程中的核心计算步骤，指给定一条参数化光线，判断该光线是否与场景中的几何体相交，并求出最近交点的位置、法线及表面参数。没有精确的求交计算，光线追踪就无法确定哪个物体被"看见"，渲染图像中的每一个像素颜色都依赖至少一次求交运算。

光线求交算法的系统性研究始于1980年代。Turner Whitted在1980年发表的开创性论文《An Improved Illumination Model for Shaded Display》中，首次将递归光线追踪与几何求交结合，正式奠定了现代光线追踪的框架。此后，针对三角形、球体、样条曲面的专用求交算法陆续被提出，成为图形学文献中被引用最多的算法类别之一。

光线求交的计算量直接决定渲染帧率。在无加速结构的暴力遍历中，每条光线需要与场景中所有几何体逐一测试，复杂度为 O(n)（n 为场景图元数量）。现代实时光追场景动辄包含数百万个三角形，每帧需要追踪数亿条光线，因此求交算法的效率直接影响是否需要 BVH 等加速结构。

---

## 核心原理

### 光线的参数化表示

所有求交算法的前提是将光线表示为参数方程：

$$\mathbf{P}(t) = \mathbf{O} + t \cdot \mathbf{D}$$

其中 $\mathbf{O}$ 为光线原点（origin），$\mathbf{D}$ 为单位方向向量（direction），$t$ 为沿方向行进的距离参数。约定 $t > 0$ 表示光线正方向，通常设置有效范围为 $t \in [t_{\min}, t_{\max}]$（例如 $[0.001, +\infty)$），$t_{\min}$ 的偏移量（称为 epsilon offset，典型值约 $10^{-4}$）用于避免自相交伪影（Self-Intersection Artifact）。在所有求出的正 $t$ 值中，取最小值对应的交点即为最近可见交点。

### 光线与球体求交

设球心为 $\mathbf{C}$，半径为 $r$。将光线方程代入球方程 $|\mathbf{P} - \mathbf{C}|^2 = r^2$，展开得到关于 $t$ 的一元二次方程：

$$|\mathbf{D}|^2 t^2 + 2(\mathbf{D} \cdot (\mathbf{O} - \mathbf{C})) t + |\mathbf{O} - \mathbf{C}|^2 - r^2 = 0$$

令 $\mathbf{oc} = \mathbf{O} - \mathbf{C}$，则系数为：
- $a = \mathbf{D} \cdot \mathbf{D}$
- $b = 2(\mathbf{D} \cdot \mathbf{oc})$
- $c = \mathbf{oc} \cdot \mathbf{oc} - r^2$

判别式 $\Delta = b^2 - 4ac$：若 $\Delta < 0$ 则无交点；$\Delta = 0$ 则相切（一个交点）；$\Delta > 0$ 则两个交点 $t_{1,2} = (-b \pm \sqrt{\Delta}) / (2a)$，取正的较小值。交点处的法线为 $\mathbf{n} = (\mathbf{P} - \mathbf{C}) / r$，方向朝外。实践中常用 $b' = b/2$ 简化公式，避免乘以 2 的冗余运算。

### 光线与三角形求交

三角形是现代实时渲染中最主要的图元格式。Möller–Trumbore 算法（1997年由 Tomas Möller 和 Ben Trumbore 提出）是目前工业界最常用的三角形求交算法，完全避免了预计算平面方程。设三角形顶点为 $\mathbf{V}_0, \mathbf{V}_1, \mathbf{V}_2$，定义：

$$\mathbf{E}_1 = \mathbf{V}_1 - \mathbf{V}_0, \quad \mathbf{E}_2 = \mathbf{V}_2 - \mathbf{V}_0, \quad \mathbf{s} = \mathbf{O} - \mathbf{V}_0$$

则求解线性方程组：

$$\begin{pmatrix} t \\ u \\ v \end{pmatrix} = \frac{1}{\mathbf{D} \times \mathbf{E}_2 \cdot \mathbf{E}_1} \begin{pmatrix} (\mathbf{s} \times \mathbf{E}_1) \cdot \mathbf{E}_2 \\ (\mathbf{D} \times \mathbf{E}_2) \cdot \mathbf{s} \\ (\mathbf{s} \times \mathbf{E}_1) \cdot \mathbf{D} \end{pmatrix}$$

交点有效的条件为：$t > 0$，$u \geq 0$，$v \geq 0$，$u + v \leq 1$。其中 $u, v$ 是重心坐标（Barycentric Coordinates），可直接用于插值法线、纹理坐标等顶点属性。

### 光线与平面求交

设平面由法线 $\mathbf{n}$ 和平面上一点 $\mathbf{Q}$ 定义，平面方程为 $\mathbf{n} \cdot (\mathbf{P} - \mathbf{Q}) = 0$。代入光线方程得：

$$t = \frac{\mathbf{n} \cdot (\mathbf{Q} - \mathbf{O})}{\mathbf{n} \cdot \mathbf{D}}$$

当分母 $|\mathbf{n} \cdot \mathbf{D}| < \epsilon$（光线与平面近似平行）时，无交点或交线（忽略）。平面求交是三角形求交的退化版本，常用于地板、镜面、切割面等无限平面场景。

---

## 实际应用

**软件光线追踪渲染器**：Peter Shirley 的《Ray Tracing in One Weekend》系列教程以球体求交为入门示例，场景中所有对象存储在 `hittable_list` 中，每条摄像机光线依次调用每个对象的 `hit()` 函数，传入有效 $t$ 范围，返回最近命中记录。这是理解求交流程的最直观实现方式。

**GPU 硬件加速**：NVIDIA RTX 系列 GPU（自 Turing 架构，2018年）引入了专用的 RT Core，其核心功能就是在硬件级别加速光线-AABB（轴对齐包围盒）和光线-三角形求交测试。开发者通过 DirectX Raytracing（DXR）或 Vulkan Ray Tracing 扩展调用这些硬件单元，三角形求交吞吐量相比纯 Shader 实现提升约10倍。

**法线贴图配合求交结果**：Möller–Trumbore 算法输出的重心坐标 $(u, v)$ 可用于在三个顶点的法线之间插值，得到平滑的着色法线（Shading Normal），这是 Phong 着色模型和 PBR 材质系统的必要输入。

---

## 常见误区

**误区一：忽略 $t_{\min}$ 的 epsilon 偏移导致自相交**  
在着色点发射阴影光线时，如果不设置最小 $t$ 阈值，求交函数会将光线起点所在的三角形本身检测为交点（$t \approx 0$），导致大面积"阴影痤疮"（Shadow Acne）。解决方法是将 $t_{\min}$ 设为约 $10^{-4}$，而不是严格的 $0$。不同场景的合适 epsilon 值与场景几何尺度相关，使用固定值在极大或极小尺度场景中会失效。

**误区二：混淆几何法线与着色法线**  
求交时计算的法线是几何法线（Geometric Normal），由三角形实际边叉积得到。但渲染时使用的着色法线是由重心坐标插值的顶点法线。当光线从背面击中三角形时，几何法线与光线方向点积为正，需要翻转法线方向。错误地将几何法线用于光照计算会导致背面出现错误高光。

**误区三：球体求交中分母未归一化**  
Möller–Trumbore 算法中不要求方向向量 $\mathbf{D}$ 是单位向量，但球体求交公式中的 $a = \mathbf{D} \cdot \mathbf{D}$，若 $\mathbf{D}$ 已归一化则 $a = 1$，可简化为 $t = (-b \pm \sqrt{b^2 - 4c}) / 2$。若光线方向未归一化（如在某些坐标变换后），直接套用简化公式会导致错误的 $t$ 值和误判。

---

## 知识关联

**前置概念——光线生成**：光线生成阶段为每个像素产生一条从摄像机出发的光线，给出 $\mathbf{O}$ 和 $\mathbf{D}$ 的具体数值。光线求交正是对这些光线逐一进行几何测试的阶段，两者共同构成光线追踪的"可见性判断"环节。

**后续概念——BVH 加速结构与 KD-Tree**：当场景包含海量三角形时，对每