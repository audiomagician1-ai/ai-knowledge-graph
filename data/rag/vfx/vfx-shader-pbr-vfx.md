---
id: "vfx-shader-pbr-vfx"
concept: "PBR特效材质"
domain: "vfx"
subdomain: "shader-vfx"
subdomain_name: "Shader特效"
difficulty: 4
is_milestone: false
tags: ["高级"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.5
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# PBR特效材质

## 概述

PBR（Physically Based Rendering，基于物理的渲染）特效材质是将能量守恒方程应用于折射、透射和半透明效果的着色器技术。与不透明PBR材质不同，特效PBR材质必须同时处理光线的**反射**、**折射**和**吸收**三种物理行为，其核心挑战在于如何在实时渲染中用可近似的计算模拟这些复杂的光学现象。

该技术在游戏引擎中的广泛采用始于2013年前后，Disney的Brent Burley发布了"Physically Based Shading at Disney"报告，奠定了现代PBR工作流的基础。此后Unreal Engine 4（2014年）和Unity的HDRP管线将折射与透射纳入PBR材质体系，使开发者能够用统一的参数集（金属度、粗糙度、IOR）描述从玻璃瓶到火焰烟雾的各类特效材质。

在特效制作中，PBR特效材质的重要性体现在物理正确性上：一块用旧方法制作的玻璃在强光下会产生明显错误的高光，而PBR玻璃材质因遵循菲涅尔方程，在掠射角（接近90°）时反射率自动趋近于1，在正视角时则呈现正确的透射颜色，从而在不同光照条件下都保持视觉可信度。

---

## 核心原理

### 菲涅尔效应与IOR参数

PBR特效材质中，折射率（Index of Refraction，IOR）是决定材质光学行为的基础参数。菲涅尔反射率公式的简化版本（Schlick近似）为：

**F(θ) = F₀ + (1 - F₀) × (1 - cosθ)⁵**

其中 **F₀ = ((n₁ - n₂) / (n₁ + n₂))²**，n₁和n₂分别为入射介质和折射介质的折射率。对于常见特效材质：水的IOR约为1.33，玻璃为1.45–1.52，钻石为2.42，火焰气团约为1.0003。当特效材质的IOR设置为1.0时，菲涅尔效应消失，F₀趋近于0，材质表现为完全透明的空气，这是制作热浪扭曲特效的理论依据。

### 透射与Beer-Lambert衰减

PBR半透明材质的颜色吸收遵循**Beer-Lambert定律**：

**T = e^(-σ_a × d)**

其中 σ_a 是吸收系数，d 是光线穿透材质的厚度。这意味着光线穿透厚度翻倍时，透射率不是减半而是平方级下降。在实际Shader中，通常用一张**厚度贴图（Thickness Map）**来近似表示每个像素点的材质厚度，配合自定义的吸收颜色（Absorption Color）参数，实现薄边缘颜色较浅、厚中心颜色较深的物理正确效果——例如翡翠雕像的边缘近乎透明而内部呈深绿色。

### 次表面散射（SSS）与半透明特效

PBR框架下的半透明特效材质使用**次表面散射**来模拟光线在材质内部多次弹射的现象。其核心参数包括：**散射半径（Scatter Radius）**控制光线在材质内扩散的空间范围；**散射颜色（Scatter Color）**决定哪些波长的光被保留（皮肤材质通常红色散射半径最大，约10mm，蓝色最小）。对于特效中的魔法光球、发光史莱姆等效果，SSS散射半径参数往往被夸张地放大至正常皮肤的5–10倍，以制造光线从内部穿透的发光感，同时必须保持能量守恒——即反射光+透射光+吸收光的能量之和不超过入射光能量。

### 折射向量偏移与屏幕空间近似

实时渲染中精确计算折射光路代价极高，PBR特效材质通常采用**屏幕空间折射（Screen Space Refraction）**近似：用法线贴图的xy分量乘以一个由IOR导出的偏移强度，对后缓冲（Back Buffer）进行采样偏移。偏移量公式近似为：

**offset = normal.xy × (IOR - 1.0) × thickness**

此方法的局限在于当折射对象被其他不透明物体遮挡时，会采样到错误的像素，因此通常需要配合**折射深度校验**或限制最大偏移像素值（一般不超过屏幕宽度的5%）来避免穿帮。

---

## 实际应用

**游戏中的玻璃瓶特效**：使用PBR特效材质时，玻璃瓶需要同时设置折射率（IOR=1.5）、低粗糙度（Roughness ≈ 0.05）以产生清晰折射，以及薄膜Thickness Map来实现瓶底厚重处的绿色吸收色调。在Unity HDRP中，此类材质选择"Transparent"渲染队列并启用"Refraction Model: Sphere"来模拟球形折射体的变形效果。

**火焰与热浪扭曲**：热浪效果本质上是IOR接近1.0的极低折射率材质，通过流动的法线贴图（用UV动画或顶点动画驱动）来实现画面的实时扭曲。该材质不需要厚度贴图，但需将混合模式设为Additive或Alpha Blend，并关闭深度写入（ZWrite Off），以正确与场景混合。

**魔法护盾与能量罩**：将PBR半透明材质与菲涅尔边缘光结合，在视线垂直于曲面处（cosθ=1）几乎全透明，在掠射角处（cosθ≈0）显示高反射率的光晕，产生"边缘发光+中心透明"的能量罩视觉。通常在Shader中用`pow(1 - dot(N, V), 3.0)`来控制菲涅尔边缘强度的指数衰减。

---

## 常见误区

**误区一：将特效材质的Opacity直接控制折射强度**
许多开发者认为降低Opacity参数可以让材质"更透明地折射"，但实际上Opacity控制的是Alpha混合中的覆盖程度，与IOR驱动的折射偏移是两个独立通道。正确做法是保持Opacity用于控制材质整体可见度，用单独的Refraction Intensity或IOR参数控制折射扭曲强度。将两者混用会导致在半透明边缘出现折射效果突然消失的错误。

**误区二：忽略能量守恒导致材质异常发光**
PBR框架要求反射率+透射率≤1。当开发者同时设置高Emissive、高Albedo和高Transmission时，材质在某些光照条件下会产生"自发光"的错误效果，尤其在HDR渲染管线中会触发Bloom过曝。检验方法是将材质放置在纯白（1,1,1）光照环境中，出射总亮度不应超过入射亮度。

**误区三：半透明特效材质可以不关心渲染排序**
不同于不透明PBR材质，使用Alpha Blend混合模式的PBR特效材质必须从后到前（Back-to-Front）渲染，否则会因深度测试顺序错误导致穿插闪烁（Z-Fighting）。这在粒子系统中尤为突出——多个使用PBR折射材质的粒子叠加时，若不按深度排序，前方粒子可能采样到后方粒子的错误颜色。

---

## 知识关联

**前置知识——混合模式**：PBR特效材质直接依赖混合模式决定最终合成方式。折射材质通常使用Alpha Blend（`SrcAlpha, OneMinusSrcAlpha`）以正确混合透射颜色，而发光特效（火焰、魔法粒子）则使用Additive混合（`One, One`）来叠加光能。混合模式的选择决定了PBR参数在哪个通道发挥作用：Additive模式下Transmission参数失效，因为没有"减去背景"的混合操作。

**延伸方向——光线追踪折射**：当渲染平台支持硬件光线追踪（如DXR、Vulkan Ray Tracing）时，PBR特效材质可以从屏幕空间折射升级为真实的光线弯折路径计算，IOR参数将直接驱动Snell定律（n₁sinθ₁ = n₂sinθ₂）来计算精确折射方向，彻底解决屏幕空间近似的遮挡采样错误问题。理解本文介绍的IOR与Beer-Lambert基础，是迁移至光追折射工作流的必要前提。
