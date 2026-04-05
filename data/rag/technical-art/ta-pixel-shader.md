---
id: "ta-pixel-shader"
concept: "片元着色器编写"
domain: "technical-art"
subdomain: "shader-dev"
subdomain_name: "Shader开发"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 82.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 片元着色器编写

## 概述

片元着色器（Fragment Shader，在HLSL/DirectX中称为Pixel Shader）是渲染管线中对每一个像素独立执行的可编程阶段，其输入来自顶点着色器输出经过光栅化插值后的数据，最终输出一个或多个颜色值写入渲染目标（Render Target）。与顶点着色器不同，片元着色器的执行频率极高——在1920×1080的全屏Pass中，单帧就可能触发超过两百万次调用，因此每一条指令的代价都会被放大数百万倍。

片元着色器的概念随可编程渲染管线的兴起而出现。2001年DirectX 8.0引入了Pixel Shader 1.0模型，最初只支持极少量的指令和寄存器；到了2002年DirectX 9.0/Shader Model 2.0，HLSL语言正式定型，片元着色器才具备了完整的条件分支、循环和浮点运算能力。如今Unity的URP/HDRP均基于Shader Model 4.5及以上，片元着色器可访问结构化缓冲区（StructuredBuffer）、进行原子操作，功能已极为丰富。

片元着色器是所有视觉效果的"最终裁决者"：无论几何形状如何精妙，法线如何精确，最终用户看到的颜色完全由片元着色器决定。光照模型、纹理混合、透明度、自发光、描边——全部在此阶段完成计算并输出。

---

## 核心原理

### 输入语义与插值数据

片元着色器接收的结构体由顶点着色器的输出结构体经GPU光栅化硬件插值而来。常见的输入语义包括：`SV_POSITION`（屏幕空间裁剪坐标，只读）、`TEXCOORD0`~`TEXCOORD7`（用户自定义插值量，如UV、世界法线、切线空间向量）、`COLOR0`（顶点色）。需要特别注意的是，`SV_POSITION`在片元着色器中的值已经是屏幕空间的像素坐标（xy分量为像素中心，z为深度），而非顶点着色器输出时的齐次裁剪空间坐标。如需在片元着色器中重建世界坐标，需要使用`SV_POSITION.xy`结合逆视图投影矩阵或单独传入世界空间位置插值量。

### 纹理采样与采样器状态

在HLSL中，纹理采样分为纹理对象（`Texture2D`）和采样器对象（`SamplerState`）两个独立部分。完整的采样调用形式为：

```hlsl
float4 color = _MainTex.Sample(sampler_MainTex, i.uv);
```

Unity的`tex2D(_MainTex, uv)`是对上述操作的封装，在旧版CG语法中广泛使用。采样函数族还包括`SampleLevel`（手动指定Mip级别，常用于特效中的模糊采样）、`SampleGrad`（传入ddx/ddy手动控制各向异性过滤）、`SampleBias`（对Mip等级施加偏移量）。在片元着色器中，GPU硬件会自动计算相邻像素的UV差分（ddx/ddy）来选择合适的Mip级别，这是在计算Shader中无法自动获得的特性。

### 颜色计算与光照模型

最基础的漫反射光照（Lambertian）计算公式为：

> **C_diffuse = albedo × max(0, dot(N, L)) × lightColor**

其中 `N` 为片元的世界空间法线（必须在片元着色器中归一化，因为顶点法线插值后模长不保证为1）、`L` 为归一化光源方向向量。Blinn-Phong高光项的计算引入半程向量 `H = normalize(L + V)`，高光强度为 `pow(max(0, dot(N, H)), _Shininess)`，其中 `_Shininess` 控制高光范围，通常在8到256之间取值。这类计算在片元着色器中按像素执行，相比在顶点着色器中插值光照结果（Gouraud Shading）能显著提升曲面高光的精确度。

### 输出控制与深度写入

片元着色器的输出使用 `SV_Target` 语义，可以同时输出多个渲染目标（MRT，Multiple Render Targets），例如延迟渲染的G-Buffer Pass会同时输出到 `SV_Target0`（Albedo）、`SV_Target1`（法线）、`SV_Target2`（自发光+Roughness）。若需手动输出深度，使用 `SV_Depth` 语义，但这会禁用GPU的Early-Z优化，导致性能下降，应谨慎使用。在Unity ShaderLab中，透明度测试（clip指令）用于剔除片元：`clip(alpha - _Cutoff)` 当alpha值低于阈值时直接丢弃片元，不写入颜色或深度，这是实现草木等AlphaTest效果的标准做法。

---

## 实际应用

**溶解效果**：利用一张噪声纹理采样值与 `_DissolveThreshold` 参数做差后调用 `clip()`，随着阈值从0增大到1，物体像素从边缘到中心逐渐被丢弃，形成溶解消失的效果。在 `clip` 前的边缘区域（如采样值在 `_Threshold` 到 `_Threshold + 0.05` 之间）叠加一个发光颜色，即可形成灼烧边缘。

**边缘光（Rim Light）**：在片元着色器中计算 `rimFactor = 1.0 - saturate(dot(N, V))`，其中V为摄像机方向向量。当法线与视线垂直时（模型边缘），dot接近0，rimFactor接近1，将此值乘以边缘光颜色叠加到最终输出，产生科幻感轮廓发光效果。通过 `pow(rimFactor, _RimPower)` 可控制边缘宽度，_RimPower越大边缘越窄越锐利。

**UV扰动采样**：先采样一张法线贴图获得扰动偏移量 `float2 offset = normalMap.rg * _DistortionStrength`，再用 `uv + offset` 对主纹理进行偏移采样，可实现热空气扭曲、水面折射等效果，此类技术在屏幕空间GrabPass中尤为常见。

---

## 常见误区

**误区一：认为法线插值后仍为单位向量**。顶点法线经过双线性插值后，模长会小于1（在两个不平行法线之间插值时结果向量更短），若不在片元着色器中调用 `normalize(i.normal)`，光照计算中的 `dot(N, L)` 结果将偏小，导致高曲率区域出现明显变暗的光照错误。这一问题在低多边形模型上尤为明显。

**误区二：滥用clip()实现半透明**。`clip()` 只能实现全透明或完全不透明的二值化剔除（AlphaTest），无法实现半透明混合。半透明效果必须依赖渲染队列（Transparent）配合混合方程（Blend SrcAlpha OneMinusSrcAlpha）在输出阶段由ROP硬件完成，二者是机制完全不同的透明方案，混淆会导致错误的排序或穿帮问题。

**误区三：在片元着色器中大量使用动态分支**。GPU采用SIMD架构，同一个Warp（通常32个线程）内所有片元必须执行相同的指令路径。当 `if` 语句的条件在同一Warp内不一致时，两个分支都会实际执行，不满足条件的线程被屏蔽（Masked），造成性能浪费。在片元着色器中应优先使用 `lerp`、`step`、`saturate` 等无分支的数学替代方案，仅在确认分支高度一致（如基于uniform参数的全局开关）时才使用动态 `if`。

---

## 知识关联

学习片元着色器编写需要具备HLSL基础，包括数据类型（`float4`、`half3`）、内置函数（`saturate`、`lerp`、`pow`）以及向量运算规则，这些是进行光照和颜色计算的直接工具。

在掌握基础片元着色器编写后，自然过渡到**自定义光照模型**，即将Lambertian/Blinn-Phong替换为更复杂的各向异性或卡通化模型，这需要对本文的漫反射/高光计算公式进行参数化扩展。**PBR材质基础**则将光照模型升级为基于物理的Cook-Torrance BRDF，其片元着色器结构与本文所述相同，但增加了金属度/粗糙度工作流的纹理采样逻辑。**Shader变体管理**处理的是当片元着色器需要支持多关键字（如`#pragma multi_compile _ _RECEIVE_SHADOWS`）时的编译策略问题。**Shader调试技巧**则直接服务于片元着色器开发中的颜色异常、采样错误等问题的排查。**屏幕空间效果**（如SSAO、SSR）将片元着色器从物体材质扩展到全屏后处理Pass，使用 `SV_Position` 重建世界坐标等技术正是片元着色器输入语义知识的进阶应用。