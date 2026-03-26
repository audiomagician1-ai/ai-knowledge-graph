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

自定义光照模型是指在着色器程序中绕过引擎内置的物理渲染（PBR）管线，由开发者手动编写光照计算公式，以实现卡通渲染（Toon Shading）、非真实感渲染（NPR, Non-Photorealistic Rendering）等风格化视觉效果的技术手段。与标准PBR模型使用Cook-Torrance BRDF方程不同，自定义光照模型可以任意干预漫反射、高光、阴影的计算逻辑，将光照值量化为离散色阶或扭曲为艺术风格所需的任何形状。

从历史背景来看，NPR渲染的学术研究可追溯至1990年代，1998年Gooch等人在SIGGRAPH发表的"A Non-Photorealistic Lighting Model for Automatic Technical Illustrations"论文正式奠定了冷暖色调光照模型（Gooch Shading）的理论基础，该模型将冷色系（蓝色）与暖色系（黄色）混合替代传统的明暗二值，为工业制图和游戏美术提供了大量参考。2006年《无主之地》和2009年《塞尔达传说：风之杖》的重制等商业游戏让卡通渲染进入主流视野，证明了自定义光照模型的商业价值。

自定义光照模型的重要性在于它赋予开发者对"光"的完整控制权。在Unity的Shader Lab或Unreal的HLSL材质函数中，开发者可以在片元着色器阶段替换光照计算，使同一个三维模型呈现出与真实物理光照截然不同的艺术风格，这是单纯依靠后处理滤镜无法精确实现的。

## 核心原理

### 漫反射的离散化：阶梯函数与Ramp贴图

标准Lambertian漫反射公式为 `diffuse = max(0, dot(N, L))`，其中 `N` 是顶点法线单位向量，`L` 是指向光源的单位向量，计算结果是0到1之间的连续浮点值。卡通渲染的核心操作是将这个连续值量化为若干个离散色阶。

最简单的二值化方式是使用`step`函数：`toonDiffuse = step(0.5, dot(N, L))`，即当光照强度超过0.5时才渲染为亮面，否则为暗面，产生硬边卡通感。更精细的做法是使用Ramp贴图（Ramp Texture）：将`dot(N, L)`的结果作为UV坐标的U值，采样一张1×256像素的渐变贴图，艺术家可以直接绘制该贴图来精确控制每个光照区间的颜色，例如在日式动漫风格中常见的蓝色阴影过渡。Unity中典型写法为：`half3 rampColor = tex2D(_RampTex, float2(NdotL * 0.5 + 0.5, 0.5)).rgb`。

### Rim光与轮廓增强

边缘光（Rim Light）是自定义光照模型中常用的风格化高光技术，计算公式为 `rim = 1.0 - saturate(dot(N, V))`，其中 `V` 是从片元指向摄像机的单位向量。当法线与视线垂直时（即模型边缘轮廓处），`dot(N, V)` 趋近于0，因此 `rim` 值趋近于1，产生轮廓发光效果。通过 `pow(rim, _RimPower)` 可以用指数参数控制光环的宽窄，`_RimPower` 值越大，光环越细越锐利，典型取值范围为2到8。这个计算完全独立于物理光照路径，是NPR风格中强调角色轮廓、增强立体感的专属手段。

### Gooch冷暖色调模型

Gooch光照模型用线性插值替代Lambertian的明暗分割：首先定义暖色调 `kWarm = kd + α * yellow`，冷色调 `kCool = kd + β * blue`，其中 `kd` 是物体本身颜色，`α` 和 `β` 是混合系数（论文原始值建议 α=0.45，β=0.55），然后用 `(1 + NdotL) / 2` 作为插值因子：`color = lerp(kCool, kWarm, (NdotL + 1.0) * 0.5)`。这个公式确保背光面呈冷色调、受光面呈暖色调，即使在完全背光的区域也不会出现纯黑，非常适合技术插图和工业设计可视化场景。

### 高光的风格化处理

NPR高光通常不使用PBR的GGX分布函数，而是使用Blinn-Phong的半角向量 `H = normalize(L + V)`，然后对 `pow(dot(N, H), _Shininess)` 应用`step`函数：`toonSpec = step(0.9, pow(NdotH, _Shininess))`，`_Shininess` 控制高光斑点的大小（典型值32到128），`step`的阈值（此处0.9）控制高光的硬度，使高光呈现出圆点状的卡通效果而非柔和渐变。

## 实际应用

**Unity中的卡通着色器实现**：在Unity URP管线中，开发者在`LitForwardPass.hlsl`中重写 `LightingFunction`，利用`GetMainLight()`获取主光源方向和颜色，将上述Ramp贴图采样结果乘以光源颜色，最后加上Rim光和一个固定的环境光底色。整个片元着色器的输出色彩不超过4个离散色阶，再结合描边Pass（使用顶点外扩法在背面渲染描边轮廓），即可还原《塞尔达传说：荒野之息》的标志性卡通视觉风格。

**Gooch模型用于CAD可视化**：在工程软件中，Gooch着色应用于机械零件预览，使设计师即便在未设置场景灯光的情况下，也能通过冷暖色直观判断曲面朝向和曲率变化，这比普通Lambertian渲染在无特定打光时要直观得多。

**多光源叠加的NPR处理**：当场景中有多盏点光源时，NPR模型对每盏灯独立执行Ramp采样后求和，而非像PBR那样在能量守恒框架下混合，这样可以让艺术家为不同光源设置不同Ramp贴图，为角色的受光区赋予截然不同的色彩倾向，实现漫画式的复杂打光。

## 常见误区

**误区一：认为自定义光照模型不需要考虑法线**  
部分初学者认为NPR渲染是纯粹的"假光照"因此法线不重要。事实上所有基于`dot(N, L)`的离散化操作都依赖高质量法线数据，低多边形模型的硬边法线会导致Ramp贴图采样产生明显的阶梯状穿帮。正确做法是在建模阶段为卡通角色专门烘焙"平滑法线"（Smoothed Normal），甚至使用将球形法线传递到切线空间的技术，确保Ramp贴图的色阶边界出现在艺术指定位置而非多边形棱角处。

**误区二：将Rim光公式中的V向量与L向量混淆**  
`rim = 1 - dot(N, V)` 中的 `V` 必须是视线向量（View Direction），而不是光源方向 `L`。如果误用 `L` 则计算的是菲涅尔近似效果，其高光区域随光源移动而移动，而真正的Rim光应该仅随摄像机角度变化——当摄像机绕模型旋转时轮廓光始终包裹在模型边缘，这是两者行为的本质区别。

**误区三：认为自定义光照模型与阴影贴图完全独立**  
NPR的自定义光照公式只替代了光照计算部分，阴影的接收仍然依赖引擎的ShadowMap采样结果。在Unity中需要显式调用`GetMainLight(shadowCoord)`才能让卡通角色接收到场景阴影投射，若遗漏此步骤，角色会在有阴影的场景中显示为始终受光状态，破坏画面一致性。

## 知识关联

自定义光照模型直接建立在**片元着色器**的基础上——片元着色器提供了逐像素执行任意计算的能力，`dot(N, L)`、`tex2D`采样、`step`量化等所有NPR运算均在这一阶段发生。理解了片元着色器中UV采样和插值变量的传递机制，才能正确实现Ramp贴图和Rim光的向量运算。

在横向关联上，自定义光照模型与**顶点着色器中的法线变换**密切配合：顶点阶段将法线从模型空间变换到世界空间（使用法线矩阵 `transpose(inverse(ModelMatrix))`），片元阶段才能用世界空间法线与世界空间光源方向进行正确的点积计算。同时，描边技术（Outline Pass）作为NPR渲染的标配伴侣，常与自定义光照模型组合使用，在同一角色材质球中通过多Pass渲染共同构成完整的卡通风格输出。