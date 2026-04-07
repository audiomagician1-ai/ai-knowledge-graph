---
id: "ta-tessellation-shader"
concept: "曲面细分着色器"
domain: "technical-art"
subdomain: "shader-dev"
subdomain_name: "Shader开发"
difficulty: 3
is_milestone: false
tags: ["进阶"]

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


# 曲面细分着色器

## 概述

曲面细分着色器（Tessellation Shader）是DirectX 11和OpenGL 4.0于2009-2010年引入的可编程管线阶段，专门负责在GPU上动态增加网格的三角形数量，从而在运行时提升几何细节。与离线烘焙的高模不同，曲面细分着色器可以根据摄像机距离、屏幕像素密度等条件实时调整细分级别，使同一个低面模型在近处呈现出极高的几何精度。

该阶段由两个独立的着色器程序构成：**Hull Shader（壳着色器）**和**Domain Shader（域着色器）**，中间夹着一个固定功能的**Tessellator（细分器）**硬件单元。三者共同构成完整的曲面细分管线，缺一不可。在DirectX的术语体系中，Hull Shader对应HLSL的`hull`关键字，Domain Shader对应`domain`关键字；在OpenGL中则称为Tessellation Control Shader（TCS）和Tessellation Evaluation Shader（TES）。

曲面细分着色器的核心价值在于**位移贴图（Displacement Mapping）**的实现——通过在Domain Shader中采样高度图并沿法线方向偏移顶点位置，可以将贴图中存储的几何细节还原为真实的三维顶点，使岩石、地形、皮肤等表面呈现出视差效果无法实现的真实轮廓遮挡。

---

## 核心原理

### Hull Shader的职责

Hull Shader每个调用处理一个**Patch**（图元块），默认Patch为三角形，但也可以设置为4点四边形Patch（`quad`）或最多32点的等参Patch（`isoline`）。Hull Shader的输出分为两部分：

1. **逐控制点输出**：对输入的每个控制点进行变换，输出新的控制点数据，通常直接透传或做世界空间转换。
2. **Patch常量输出**：通过`[patchconstantfunc]`属性标记的函数计算**细分因子（Tessellation Factor）**，包括内部细分因子`InsideTessFactor`和边缘细分因子`EdgeTessFactor`。

在HLSL中，细分因子封装在`SV_TessFactor`和`SV_InsideTessFactor`系统语义中。边缘细分因子决定三角形每条边被分割成多少段，内部细分因子决定三角形内部的细分密度。当任意一条边的`SV_TessFactor`设置为0时，该Patch会被完全剔除，这是曲面细分视锥剔除优化的基础。

### 固定功能Tessellator的工作

固定功能的Tessellator根据Hull Shader输出的细分因子，在**参数空间（Parametric Space）**内生成新的顶点坐标`(u, v, w)`，对于三角形Patch使用重心坐标，满足`u + v + w = 1`。细分因子的有效范围在DirectX 11中为**1到64的浮点数**，支持小数值以实现平滑过渡。Tessellator自身不可编程，但其分割模式可以在Hull Shader中通过`[partitioning]`属性选择：`integer`（整数取整）、`fractional_odd`（奇数分数）或`fractional_even`（偶数分数），其中`fractional_odd`和`fractional_even`可避免细分级别切换时的几何跳变。

### Domain Shader的职责

Domain Shader对Tessellator生成的每个新顶点执行一次，接收重心坐标`(u, v, w)`和原始Patch的控制点，通过插值计算出该顶点的最终世界坐标。最常见的插值方式是**线性插值**（Phong Tessellation使用的是法线空间插值），公式为：

```
P = u * P0 + v * P1 + w * P2
```

其中P0、P1、P2为原始三角形的三个顶点坐标。在此基础上叠加位移：

```
P_displaced = P + N * (height_map.Sample(...) * displacement_scale)
```

`N`为插值后的法线，`displacement_scale`为位移强度系数，通常在0到1之间调节，对应贴图中高度值的实际偏移量（单位：引擎世界单位）。Domain Shader输出裁剪空间坐标`SV_Position`，随后进入光栅化阶段。

---

## 实际应用

**地形渲染**是曲面细分着色器最典型的应用场景。UE4的Landscape系统在PC平台上使用曲面细分将地形基础网格（通常为每块8×8顶点）细分至数百个三角形，配合16位精度的高度图进行顶点位移，实现公里级地形的厘米级表面细节，同时不需要在内存中存储高密度静态网格。

**角色皮肤与布料**中，使用PN Triangles（Point-Normal Triangles）算法的Hull Shader可以基于顶点法线构建曲面控制点，使低面模型的硬边轮廓在细分后弯曲成光滑曲面，人物肩膀、脸颊等位置的锯齿感显著减少，这一技术在AMD的TressFX技术文档（2012年）中有详细描述。

**海浪模拟**中，Domain Shader结合Gerstner Wave函数对水面Patch进行实时位移，细分因子根据与摄像机的距离从1动态变化至64，波谷与波峰处形成真实的几何遮挡与折射效果，而非单纯依赖法线贴图的视觉欺骗。

在Unity（HDRP）中，开启曲面细分需要在Shader的SubShader中添加`#pragma hull hs_main`和`#pragma domain ds_main`，并将Topology设置为Patch拓扑模式（`topology Triangles`不够，需专用Patch Input Layout）。

---

## 常见误区

**误区一：曲面细分着色器等同于法线贴图的升级**。法线贴图仅欺骗光照计算，在轮廓处会暴露出平坦的几何体；曲面细分配合位移贴图是真实移动顶点，在所有视角下（包括轮廓、阴影投射）都有正确的几何形状。两者面向的问题层次不同，并非简单的替代关系。

**误区二：细分因子越高性能越好只要硬件够强**。过高的细分因子会导致细分后的三角形面积小于单个像素（亚像素三角形），此时光栅化效率急剧下降，因为每个微小三角形仍消耗完整的光栅化开销。业界经验表明，细分后的单个三角形覆盖像素数不应低于8-16个，否则应降低细分因子或切换至普通网格。

**误区三：Hull Shader和Domain Shader可以独立使用**。两者在管线中必须成对存在——有Hull Shader就必须有Domain Shader，且中间的固定功能Tessellator无法跳过。如果只需要Hull Shader的Patch处理能力而不想细分，需将所有细分因子设置为1（而非0，因为0会触发剔除）。

---

## 知识关联

**前置知识（顶点着色器编写）**：Hull Shader的控制点处理逻辑与顶点着色器的顶点变换高度相似——都在处理顶点的位置、法线、UV，但Hull Shader的输入为Patch内的控制点数组，而非单个顶点。Domain Shader的插值输出同样需要送往像素着色器，UV坐标、切线空间法线的插值方式与顶点着色器到像素着色器的插值规则一致。理解顶点着色器中`SV_Position`的语义，有助于正确在Domain Shader的最后阶段完成MVP矩阵变换。

**后续概念（曲面细分LOD）**：当前的固定细分因子会在不同距离下表现出效率浪费或质量不足，曲面细分LOD正是在Hull Shader的`[patchconstantfunc]`函数中引入基于**屏幕空间投影尺寸**的自适应因子计算，使近处细分因子接近64、远处降至1，并处理相邻Patch边缘细分不匹配导致的**T形缝（T-junction）**裂缝问题，这是曲面细分实用化的关键工程步骤。