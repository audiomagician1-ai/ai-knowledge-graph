---
id: "ta-custom-lighting"
concept: "自定义光照模型"
domain: "technical-art"
subdomain: "shader-dev"
subdomain_name: "Shader开发"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.1
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

# 自定义光照模型

## 概述

自定义光照模型是指在Shader中绕过渲染引擎的默认PBR或Phong光照管线，由开发者手动编写光照计算函数，从而实现卡通渲染（Toon Shading）、各向异性高光（Anisotropic Specular）、布料光照、皮肤次表面散射等非标准视觉效果的技术。与引擎内置光照不同，自定义光照模型允许开发者完全控制漫反射、高光、阴影过渡的每一步数学运算，而非依赖BRDF（双向反射分布函数）的物理约束。

该技术的根源可以追溯到1998年日本动画游戏对"Cel Shading"的探索，以及1994年Greg Ward发表的各向异性反射模型论文。在Unity的Shader Lab体系中，自定义光照通过编写`Lighting<ModelName>`函数来替换内置光照；在Unreal Engine中，则通过Material的Custom Shading Model节点或修改`ShadingModels.ush`文件实现。这种技术在二次元风格游戏（如《原神》《崩坏：星穹铁道》）和写实向角色渲染中都有不可替代的应用价值。

## 核心原理

### Lambert漫反射的改造——Half Lambert与Toon阶梯化

标准Lambert漫反射公式为 `diffuse = max(0, dot(N, L))`，其中N为法线方向，L为光源方向。在自定义光照中最常见的第一步改造是Valve公司在《半条命2》中提出的Half Lambert：

```
halfLambert = dot(N, L) * 0.5 + 0.5
```

这将光照值从[-1, 1]重映射到[0, 1]，消除了背光面的全黑区域。在此基础上，Toon光照进一步将halfLambert值输入一张1D渐变贴图（Ramp Texture）或使用`step()`/`smoothstep()`函数进行阶梯化，例如：

```hlsl
float toon = smoothstep(0.45, 0.55, halfLambert);
```

通过调整`smoothstep`的两个边界参数（如0.45和0.55），可以精确控制明暗交界线的硬度，这是标准PBR流程无法直接实现的效果。

### 各向异性高光模型——Kajiya-Kay模型

各向异性高光用于模拟头发、金属拉丝、绸缎等沿单一方向排列微观结构的材质。最经典的实现是1989年由James T. Kajiya和Timothy Kay提出的Kajiya-Kay模型，其核心公式为：

```
specular = pow(sin(angle(T, H)), shininess)
```

其中T是切线方向（Tangent），H是半角向量（Half Vector = normalize(L + V)）。由于头发纤维没有固定法线朝向，该模型使用切线T代替法线N参与计算。在实际Shader实现中，通常在切线基础上叠加一张"漂移贴图"（Shift Texture）来扰动高光条带的位置，使其在头发的不同位置产生错开的双层高光，这也是《原神》等游戏角色头发高光的常见实现方式。

### Unity中的自定义光照函数接口

在Unity的Surface Shader体系中，声明自定义光照模型的语法格式为：

```hlsl
#pragma surface surf MyLighting
inline float4 LightingMyLighting(SurfaceOutput s, float3 lightDir, float atten) {
    float diff = dot(s.Normal, lightDir);
    // 自定义漫反射计算
    return float4(s.Albedo * _LightColor0.rgb * diff * atten, s.Alpha);
}
```

函数名必须以`Lighting`为前缀，后接`#pragma surface`中声明的模型名称。若需要视角方向参与计算（如高光），则函数签名需扩展为包含`viewDir`参数的四参数版本。此函数在每个接收光源时被调用一次，多光源情况下引擎会自动累加结果。

## 实际应用

**二次元角色渲染**：在《原神》风格的角色Shader中，自定义光照通常包含三层：使用Ramp贴图的阶梯漫反射、基于Kajiya-Kay的头发各向异性高光，以及通过读取面部SDF（有向距离场）贴图来控制脸部阴影形状，避免因法线问题产生的"脏脸"现象。面部SDF贴图通常是一张16个方向的预烘焙灰度图，在Shader中与`atan2(lightDir.x, lightDir.z)`的结果比较来决定阴影边界。

**布料光照（Oren-Nayar模型）**：标准Lambert对布料的模拟不准确，因为布料纤维会产生后向散射。1994年Michael Oren和Shree K. Nayar提出的模型引入了粗糙度参数σ（sigma），当σ=0时退化为Lambert，当σ增大时布料边缘会出现特征性的亮边效果。在Shader中需要额外计算视角方向V与光源方向L在切平面上的投影夹角，计算量比Lambert约增加3-5倍。

**描边与光照联动**：在NPR渲染中，自定义光照模型还可以将光照信息输出给后处理边缘检测pass，例如通过漫反射强度调制描边宽度——受光面描边细、背光面描边粗，这种效果需要在光照计算阶段将光照强度写入一个独立的RenderTarget通道。

## 常见误区

**误区一：认为自定义光照不需要处理多光源**。实际上Unity的Forward渲染路径中，场景内影响物体的像素光源数量受`Quality Settings`中`Pixel Light Count`限制（默认4个）。若自定义光照仅在Base Pass中编写，只有主方向光生效；点光源和聚光灯需要在Additional Pass中处理，或改用URP的自定义渲染特性（Custom Render Feature）才能正确累加多光源贡献。

**误区二：Toon Shading等于在颜色上做posterize（色调分离）**。色调分离是后处理操作，直接量化最终颜色，而Toon Shading的正确做法是对**光照强度值**在线性空间中做阶梯化，再用阶梯后的值调制颜色。如果在伽马空间对颜色做量化，阴影与高光的颜色饱和度会产生错误偏移，在HDR流程下表现尤其明显。

**误区三：各向异性高光只需要旋转高光椭圆**。部分开发者将各向异性简化为对GGX高光做椭圆拉伸，但这忽略了各向异性材质的切线连续性问题——在曲面上，切线方向必须通过UV展开或显式切线贴图来定义，否则高光会在模型接缝处出现明显的方向突变。正确做法是使用存储在顶点属性或切线贴图中的T/B/N三切空间向量。

## 知识关联

自定义光照模型的基础是**片元着色器编写**，需要熟练使用`dot`、`normalize`、`reflect`等HLSL内置函数，以及理解切线空间变换矩阵的构建方式。掌握自定义光照模型后，可以直接进入**皮肤材质**的学习——皮肤的次表面散射（SSS）本质上是在自定义漫反射计算中叠加一个模拟光线在皮肤内部散射的附加项，常见实现包括Pre-Integrated SSS（预积分次表面散射，2011年由Jorge Jimenez提出）和基于深度的屏幕空间模糊方法，两者都以本文介绍的自定义漫反射函数结构为起点进行扩展。