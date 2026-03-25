---
id: "3da-uv-unwrap-tools"
concept: "展开工具"
domain: "3d-art"
subdomain: "uv-unwrapping"
subdomain_name: "UV展开"
difficulty: 2
is_milestone: false
tags: ["工具"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 44.4
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# 展开工具

## 概述

展开工具是指三维软件中将三维网格表面"剥开"展平为二维UV坐标的算法集合。其核心任务是在展开过程中尽可能保留面积比例或角度关系，以减少贴图在模型表面的拉伸和压缩。不同算法对"保留什么"有不同的侧重：有的优先保角（Conformal），有的优先保面积（Area-Preserving），有的在两者之间做权衡（LSCM、ABF等）。

自动展开算法的发展始于1990年代末的学术研究。2002年Bruno Lévy等人在SIGGRAPH上发表了LSCM（Least Squares Conformal Maps）算法，首次将最小二乘法引入UV展开领域，使大规模自动展开成为生产可行的技术。此后，ABF（Angle-Based Flattening）和ABF++算法由Alla Sheffer等人于2005年发布，进一步提升了角度保真度。这些学术成果随后被集成进Maya、3ds Max、Blender以及专业工具RizomUV等软件。

理解各展开工具的差异对美术师至关重要，因为算法选择直接决定贴图拉伸的分布方式和手动修正的工作量。错误的算法选择可能导致角色脸部出现45%以上的面积畸变，而正确的算法则能在相同时间内交付质量更高的UV布局。

## 核心原理

### LSCM（最小二乘保角映射）

LSCM将UV展开问题转化为线性方程组求解。其目标函数为最小化保角能量：

**E_LSCM = Σ |∂u/∂x - ∂v/∂y|² + |∂u/∂y + ∂v/∂x|²**

其中u、v为UV坐标，x、y、z为三维坐标分量。该公式要求UV坐标的偏导满足柯西-黎曼方程，本质是寻找一个尽量"保角"的映射。LSCM需要用户手动指定至少两个"钉住"顶点（Pin Points）作为约束，否则方程组欠定。Blender的"展开（Unwrap）"选项默认使用LSCM，适合有明确接缝且需要低拉伸的有机模型。

### ABF / ABF++（基于角度的展平）

ABF算法以三角面的内角作为优化变量，而非直接操作顶点位置。对于每个三角形的三个内角α，算法求解满足以下约束的最优角度集合：每个三角形内角之和等于π，每个顶点周围角度之和等于2π（对于内部顶点）。ABF++在ABF基础上引入了分层线性化求解，将计算复杂度从O(n²)降低至近线性，可处理数十万面的高精度网格。ABF++的角度失真通常比LSCM低15%~30%，但计算时间更长，适合需要高精度UV的角色头部或武器贴图。

### GU（Geometry Unwrap）与投影对比

部分软件（如3ds Max的"快速剥皮"Quick Peel）使用基于几何曲率的贪心展开，沿曲率最小路径自动切割并逐块展开。这与《投影展开》中的平面/圆柱投影有本质区别：投影展开将三维坐标直接投影到某个几何面，不做优化迭代，速度极快但对复杂曲面产生严重拉伸；而GU/LSCM/ABF都属于迭代优化类算法，需要更多计算时间，但拉伸分布更均匀。对于一个标准2048×2048贴图，投影展开产生的拉伸误差可高达200%，而LSCM通常控制在20%以内。

### Conformal与Area-Preserving的取舍

保角映射（Conformal）保留局部角度，贴图上的图案形状不会变形，但面积可能缩放；保面积映射（Area-Preserving）保证贴图分辨率均匀，但形状会产生剪切。游戏角色贴图通常偏向保角，因为法线贴图的切线空间计算对角度失真更敏感；而地形或布料等需要均匀纹素密度的表面则更适合保面积映射。Houdini的UV Flatten SOP提供了一个"Blend"参数（0=保角，1=保面积），可在两者之间连续插值调整。

## 实际应用

**角色头部UV展开**：在Maya中对人脸模型使用"展开UV"命令，默认调用LSCM算法。美术师先在耳后和头顶手动切割接缝，再执行LSCM展开，最后用"优化UV"（Optimize UVs，基于ABF++的Maya内置优化器）迭代200次，可将角度误差从初始的18°降低至约4°。

**硬表面武器展开**：对于机械零件，由于大量平面和圆柱面存在，直接对各子部件使用投影展开后，再通过RizomUV的"ZRemesh Unfold"（基于LSCM变体）统一优化整体UV，可节省约40%的手动调整时间。

**Blender实操对比**：在Blender 3.6中，同一个球体模型分别使用"展开（LSCM）"和"智能UV投影（Smart UV Project）"。LSCM在有接缝的情况下拉伸近乎为零，而Smart UV Project会将球体切成约12块投影，块内拉伸低但接缝数量多，总边界长度增加3倍，浪费更多UV空间在接缝边距（Texel Padding）上。

## 常见误区

**误区一：认为自动展开算法越"保角"越好**。实际上，纯保角映射会导致模型上面积差异悬殊的区域（如耳廓与面颊）在UV空间中面积比例严重失调，使耳廓贴图分辨率远低于面颊。正确做法是展开后使用"UV拉伸可视化"工具（Blender中的Stretch Overlay，绿色=低拉伸，红色=高拉伸）检查面积比，必要时手动缩放局部UV岛。

**误区二：认为算法选择与接缝位置无关**。LSCM对钉住点和接缝极度敏感：接缝切割在高曲率区域会给LSCM创造短小的UV岛，导致方程组病态（ill-conditioned），输出结果出现翻转面（Flipped Face，UV面积为负值）。ABF++对接缝位置的敏感性较低，但处理含有极点（Pole，如六条边汇聚的顶点）的网格时依然需要将极点放置在接缝边上。

**误区三：混淆"优化UV"与"展开UV"操作**。展开UV是初次计算UV坐标，优化UV（如Maya的Optimize UVs或Blender的Minimize Stretch）是对已有UV进行迭代松弛，两者底层算法不同。对一个已经严重错误展开的UV做100次优化迭代，结果仍然不如重新正确展开一次。

## 知识关联

学习展开工具之前，需要掌握《投影展开》的平面、圆柱、球形投影概念，因为LSCM/ABF等算法通常以投影结果作为初始解（Initial Solution），再进行迭代优化——理解投影展开的局限性有助于解释为何自动展开算法的迭代过程有时会收敛到局部最优。

掌握展开工具的算法差异后，可进入《RizomUV工作流》的学习，RizomUV集成了自研的Unfold3D算法（LSCM的工程优化版本），其Mosaic打包和多线程展开依赖于对各算法参数的精确控制。同时，《自动UV展开》主题将在此基础上探讨如何通过脚本批量调用这些算法处理场景中数百个资产，涉及Maya的`pymel.core.polyAutoSeams()`和Blender的`bpy.ops.uv.unwrap()`接口调用。