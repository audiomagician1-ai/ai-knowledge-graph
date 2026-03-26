---
id: "cg-custom-lighting"
concept: "自定义光照模型"
domain: "computer-graphics"
subdomain: "shader-programming"
subdomain_name: "Shader编程"
difficulty: 3
is_milestone: false
tags: ["风格化"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.2
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# 自定义光照模型

## 概述

自定义光照模型是指在着色器中绕过引擎内置的PBR（基于物理的渲染）管线，由开发者手动编写光照计算逻辑，从而实现卡通渲染（Toon Shading）、非真实感渲染（NPR，Non-Photorealistic Rendering）或其他风格化视觉效果的技术。与PBR依赖Cook-Torrance微表面模型不同，自定义光照模型允许将漫反射分量离散化为色阶、将高光锁定为硬边圆形，或完全基于视角向量计算边缘发光（Rim Light）。

这类技术的历史可追溯至2000年代初期游戏《塞尔达传说：风之杖》（2002年）所推广的卡通渲染风格。其核心数学原理来自Gooch等人于1998年提出的冷暖色调光照模型（Gooch Shading），该模型使用表面法线与光线夹角的余弦值将颜色在暖色调（如橙色）和冷色调（如蓝色）之间插值，彻底脱离了对"物理正确"的追求。

在游戏和动漫风格美术中，自定义光照模型的意义在于将光照变成一种**叙事性工具**而非物理模拟——一个角色的高光形状可以设计成星形，阴影边界可以硬切或带有手绘噪声，这些效果用PBR根本无法实现。

---

## 核心原理

### 1. 离散化漫反射（Cel Shading）

标准Lambertian漫反射公式为：

```
diffuse = max(0, dot(N, L)) * lightColor * albedo
```

其中 `N` 是表面法线，`L` 是指向光源的单位向量。卡通着色的关键改造是对 `dot(N, L)` 的结果进行**阶梯量化**，例如将0~1的连续值映射为两段或三段固定色阶：

```glsl
float NdotL = max(0.0, dot(N, L));
float toon = NdotL > 0.5 ? 1.0 : 0.3;  // 两阶卡通光照
diffuse = toon * lightColor * albedo;
```

更灵活的方案是用一张1D渐变纹理（Ramp Texture）对 `NdotL` 进行采样，美术可以直接在Photoshop中绘制该纹理来控制阴影形状，这是《原神》等现代动漫渲染游戏的常用手法。

### 2. 硬边高光（Stylized Specular）

PBR的高光由粗糙度连续控制宽度，而NPR高光通常需要一个直径固定的"圆形光斑"，这通过对Blinn-Phong高光做阈值截断实现：

```glsl
float NdotH = max(0.0, dot(N, H));  // H为半程向量
float spec = pow(NdotH, shininess);
float toonSpec = step(0.95, spec);   // step函数产生硬边
```

`step(edge, x)` 在GLSL中返回 `x < edge ? 0.0 : 1.0`，通过调整阈值（此处0.95）可以控制高光圆点大小。若想要带柔边的高光，可将 `step` 替换为 `smoothstep(0.93, 0.97, spec)`，在0.93到0.97之间平滑过渡。

### 3. 边缘光（Rim Lighting）

边缘光利用视线方向 `V` 与表面法线 `N` 的夹角来识别模型轮廓区域：

```glsl
float rim = 1.0 - max(0.0, dot(N, V));
float rimFactor = pow(rim, rimPower);  // rimPower典型值为2.0~4.0
vec3 rimColor = rimFactor * rimColorTint;
```

当 `dot(N, V)` 接近0时（即法线与视线垂直，对应模型边缘），`rim` 值接近1，产生边缘发光。这一效果在PBR中虽然存在（Fresnel项），但其强度与颜色完全受物理约束，而自定义模型中 `rimColorTint` 可以是任意颜色，如《蔚蓝》中角色使用的蓝白色冷光边缘。

### 4. 冷暖色调模型（Gooch Shading）

Gooch模型的核心公式：

```
color = (1 + dot(N, L)) / 2 * warmColor + (1 - dot(N, L)) / 2 * coolColor
```

其中 `warmColor` 通常为物体固有色与黄色的混合，`coolColor` 为物体固有色与蓝色的混合。这一模型即使在完全背光区域也保留可见度（颜色变为冷色调而非纯黑），特别适合技术插图和产品概念渲染。

---

## 实际应用

**Unity URP中的自定义Pass**：在Unity的Shader Graph或手写Shader中，将光照模型从`Lit`改为`Unlit`，然后手动获取主光源方向（通过 `_MainLightPosition`）和颜色（`_MainLightColor`），在片元着色器中执行上述卡通光照计算。Unity 2021以后推出的Custom Lighting Function节点允许在Shader Graph内嵌入HLSL函数来替换光照模型。

**《原神》风格角色渲染**：使用面部法线传输技术（将球形代理网格的法线烘焙到脸部法线贴图中），配合Ramp Texture采样，消除了面部卡通渲染时因几何体过于精细导致的不自然阴影碎裂问题。

**描边配合**：自定义光照模型通常与描边技术联合使用。最常见的方案是背面扩张描边（Back-Face Inflation），在顶点着色器中沿法线方向将背面顶点向外偏移0.01~0.05单位，渲染为纯黑色，正面渲染时即形成轮廓线效果。

---

## 常见误区

**误区1：认为NPR必须完全抛弃法线和光源方向**
实际上，卡通渲染的漫反射和高光计算仍然依赖 `dot(N, L)` 这一核心运算，只是对结果进行非线性映射。完全不使用法线的"平面着色"仅是NPR的一个极端子集，而非NPR的普遍特征。

**误区2：认为Ramp Texture只能做两阶卡通**
Ramp纹理本质上是一张对 `NdotL`（范围0~1）的1D查找表，美术可以在其中绘制任意数量的色阶、渐变带、彩虹色或条纹图案。将Ramp纹理做成2D版本（横轴为 `NdotL`，纵轴为材质ID），还可以实现不同材质区域（皮肤、头发、布料）拥有不同的阴影颜色。

**误区3：认为自定义光照模型会自动支持多光源**
引擎内置的PBR着色器已处理好多光源叠加逻辑，而手写的自定义光照模型默认只计算主光源。若需支持点光源和聚光灯，开发者必须手动遍历场景中的附加光源列表（在Unity URP中使用 `GetAdditionalLight(i, worldPos)` 循环），对每个光源重复执行卡通光照计算并累加结果。

---

## 知识关联

自定义光照模型的实现完全依托**片元着色器**——法线向量 `N`、光源方向 `L`、视线方向 `V` 均在片元着色器中以插值后的数值存在，所有阶梯化、`step`/`smoothstep` 调用都在每个像素独立执行。若未掌握片元着色器中 `varying`/`in` 变量的插值机制以及 `texture2D` 采样Ramp纹理的方法，则无法正确实现上述光照逻辑。

进阶方向上，自定义光照模型与**屏幕空间后处理**（如描边检测的Sobel算子边缘检测）、**顶点动画**（用于NPR风格的布料飘动）以及**多Pass渲染**（实现描边+主体的分离渲染）结合，构成完整的NPR渲染管线。若希望实现更复杂的面部渲染（如避免鼻子阴影穿帮），还需学习法线贴图烘焙和切线空间变换。