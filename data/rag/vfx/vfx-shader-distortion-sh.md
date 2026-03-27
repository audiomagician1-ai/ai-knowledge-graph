---
id: "vfx-shader-distortion-sh"
concept: "折射扭曲"
domain: "vfx"
subdomain: "shader-vfx"
subdomain_name: "Shader特效"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 49.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.433
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 折射扭曲

## 概述

折射扭曲（Refraction Distortion）是一种通过在Shader中采样场景颜色缓冲并对UV坐标施加偏移，模拟光线穿越折射介质（如玻璃、水面、热浪）时产生视觉弯曲的屏幕空间特效技术。其核心机制依赖于**GrabPass**（Unity）或**Scene Color节点**（Unreal Engine）获取当前帧的屏幕渲染结果，再将该纹理以扭曲后的UV重新采样，从而输出错位的背景图像。

该技术最早在2001年前后随着可编程GPU的普及而进入实时渲染领域。早期实现依赖多遍渲染（Multi-Pass）将背景先绘制到离屏纹理，再由前景Shader采样；现代引擎中GrabPass和Scene Color节点将这一流程封装为单一接口，大幅降低了实现成本。Unreal Engine 4在其水体系统中大量使用Scene Color折射，Unity的URP/HDRP则通过`Opaque Texture`设置暴露类似功能。

折射扭曲广泛应用于水面、玻璃、传送门、热浪（Heat Haze）、隐形斗篷等场景。其物理意义来源于斯涅尔定律（Snell's Law）：`n₁·sin(θ₁) = n₂·sin(θ₂)`，其中n₁、n₂为两种介质的折射率，θ₁为入射角，θ₂为折射角。常见材质折射率：真空/空气为1.0，水为1.33，玻璃为1.5，钻石为2.42。

---

## 核心原理

### 1. GrabPass与Scene Color的工作机制

GrabPass在Unity中以`GrabPass { "_GrabTexture" }` 语法声明，触发GPU将当前帧颜色缓冲复制到名为`_GrabTexture`的渲染纹理。关键限制是：**GrabPass发生在不透明物体渲染完毕之后，半透明队列（Transparent Queue，Queue=3000）之前**，因此折射物体必须置于半透明渲染队列，且无法折射同一队列中排在后面的其他半透明对象。Unreal Engine的Scene Color节点存在类似时序约束，默认仅捕获不透明Pass的渲染结果。

在URP管线下，GrabPass已被废弃，需在Camera设置中启用`Opaque Texture`，并在Shader中用`_CameraOpaqueTexture`代替，采样时使用`SampleSceneColor`函数。HDRP则通过`Distortion`材质类型内置了折射扭曲支持，无需手动实现GrabPass。

### 2. UV偏移计算与法线贴图驱动

折射扭曲的核心计算公式为：

```
screenUV_distorted = screenUV + normalXY * _DistortionStrength
```

其中`normalXY`是法线贴图采样后解码的切线空间XY分量（范围从[0,1]重映射到[-1,1]），`_DistortionStrength`为可调参数，通常取值范围在0.01到0.1之间——过大会产生不真实的撕裂感。屏幕UV的计算方式为将顶点的裁剪空间坐标（Clip Position）除以W分量并做`* 0.5 + 0.5`的变换，即：

```
screenUV = (clipPos.xy / clipPos.w) * 0.5 + 0.5;
```

法线贴图通常是流动的（借助UV滚动技术叠加两层反向滚动的法线图），以制造动态折射效果。两层法线的XY分量直接相加后再乘以强度系数，即可驱动屏幕UV偏移。

### 3. 深度感知折射修正

朴素的折射扭曲存在一个严重问题：当折射物体（如水面）后方存在近距离几何体时，偏移后的屏幕UV可能采样到折射物体**前方**的像素，导致水面前方的物体"漏进"水中产生穿帮。解决方案是深度感知修正（Depth-Aware Refraction）：

1. 采样场景深度缓冲，获取偏移坐标处的深度值`depthDistorted`
2. 将其与当前折射面的深度`depthSurface`比较
3. 若`depthDistorted < depthSurface`（偏移处比折射面更近），则将扭曲UV回退到未偏移的screenUV

该修正在Unity中需要采样`_CameraDepthTexture`，在Unreal中使用`SceneDepth`节点实现。

---

## 实际应用

### 热浪（Heat Haze）效果

热浪是折射扭曲最典型的应用之一。实现方式：将一个屏幕对齐的全屏Quad或粒子放置于场景中，使用单通道噪声纹理（如Perlin Noise）驱动UV偏移，`_DistortionStrength`设置为约0.02到0.05，噪声纹理以0.3到0.8 UV/秒的速度垂直向上滚动。不加颜色混合，仅输出扭曲后的背景采样，即可实现可信的热浪涌动感。

### 玻璃与折射水面

玻璃材质通常结合菲涅尔效果使用：掠射角区域增强反射权重，垂直视角区域增强折射权重。折射UV偏移量乘以`(1 - fresnel)`使正视方向折射效果更明显。水面折射则额外需要对偏移量乘以水深遮罩——浅水区折射强度衰减，深水区折射强度保持最大值。

### 传送门与扭曲护盾

传送门效果要求折射扭曲的偏移方向呈径向向外（从中心到边缘），可通过计算像素到传送门中心的方向向量`dir = normalize(uv - center)`，将其替代法线XY作为偏移驱动，叠加时间动画的旋转扰动，制造旋涡状扭曲。护盾击打波纹则使用运动矢量输出扭曲强度的衰减图，配合折射扭曲实现能量波扩散时的屏幕变形。

---

## 常见误区

### 误区一：GrabPass可以捕获同队列半透明对象

许多初学者期望水面能"透过"另一个半透明粒子系统。实际上GrabPass仅在不透明Pass结束后拍摄快照，同为Transparent Queue的半透明粒子不会出现在GrabTexture中。若需折射半透明物体，必须将其渲染到独立的RenderTexture并手动传递，代价是额外的DrawCall。

### 误区二：偏移强度越大越真实

将`_DistortionStrength`设置为0.3以上时，采样UV会大幅偏移至屏幕边缘外，造成纹理坐标超出[0,1]范围。GrabTexture默认Clamp模式下会产生边缘颜色重复的拉伸瑕疵，Repeat模式则会出现屏幕另一侧的画面"折射进来"。物理上，折射率为1.5的玻璃在垂直入射时的实际像素偏移量极小，0.02到0.05的强度已足够真实。

### 误区三：折射扭曲不需要考虑渲染顺序

在多个折射物体叠加的场景（如水下再透过玻璃罩）中，每个折射物体需要独立的GrabPass，且必须按正确的渲染顺序排列Queue值。若两个折射材质共享同一Queue值，它们将采样同一张GrabTexture，导致后渲染的物体无法折射先渲染的折射物体的结果，出现错误的叠加关系。

---

## 知识关联

**前置概念衔接**：UV滚动技术直接为折射扭曲提供动态法线驱动——双层反向滚动法线图是热浪和水面折射的标配实现方案，若不理解UV坐标的时间偏移计算，法线流动动画将无从实现。运动矢量（Motion Vector）则用于在TAA（时序抗锯齿）开启时对扭曲UV进行历史帧重投影修正，防止折射区域出现鬼影（Ghosting），同时也用于传送门护盾等需要程序化扭曲强度场的效果中驱动折射偏移的衰减权重。

**后续概念展开**：菲涅尔效果（Fresnel Effect）是折射扭曲的天然配对技术——斯涅尔定律决定了折射量，菲涅尔方程决定了在折射与反射之间如何分配光能。掌握折射扭曲的屏幕UV采样机制后，菲涅尔项（`pow(1 - dot(N, V), 5)`近似公式）将作为混合权重，控制反射Cubemap与折射SceneColor之间的插值，从而合成完整的物理可信水面或玻璃材质。