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
quality_tier: "pending-rescore"
quality_score: 42.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.406
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 片元着色器编写

## 概述

片元着色器（Fragment Shader）是 GPU 渲染管线中负责逐像素颜色计算的可编程阶段，在 HLSL 中以 `float4 frag(v2f i) : SV_Target` 为标准签名。与顶点着色器处理几何变换不同，片元着色器的输入是光栅化后的插值数据（如 UV 坐标、法线、世界坐标），输出是写入渲染目标的最终颜色值（RGBA 四通量）。

片元着色器在 DirectX 9 时代被称为"像素着色器"（Pixel Shader），从 Shader Model 2.0（2002年）起成为图形管线的标配可编程单元。Unity 的 ShaderLab 框架将其封装在 `CGPROGRAM` 或 `HLSLPROGRAM` 块内，开发者通过编写 `frag` 函数直接干预每个像素的最终外观。

片元着色器对游戏画面质量的影响极为直接：屏幕上每一帧渲染的每个像素都必须经过它的计算。在一块 1080p 分辨率的屏幕上，单帧就有约 207 万个像素需要独立执行片元着色器，这使得其 ALU 指令数和纹理采样次数成为影响帧率的关键性能瓶颈。

---

## 核心原理

### 输入结构体与插值数据

片元着色器通过结构体接收来自顶点着色器传递的插值数据，该结构体通常命名为 `v2f`（vertex to fragment）。常见字段包括：

```hlsl
struct v2f {
    float4 pos    : SV_POSITION;  // 裁剪空间坐标（不可读取）
    float2 uv     : TEXCOORD0;    // 纹理坐标
    float3 normal : TEXCOORD1;    // 世界空间法线
    float3 worldPos : TEXCOORD2;  // 世界空间位置
};
```

`SV_POSITION` 语义在片元阶段是只写的系统值，实际上无法在 `frag` 中读取屏幕坐标；若需要屏幕坐标，应在顶点着色器中用 `ComputeScreenPos()` 额外传入 `TEXCOORD` 槽位。插值类型默认为线性透视矫正插值，可使用 `nointerpolation` 或 `noperspective` 修饰符改变此行为。

### 纹理采样

Unity HLSL 中最常用的纹理采样函数是 `tex2D(sampler2D tex, float2 uv)`，返回 `float4` 的 RGBA 颜色值。对应的 DX11 风格写法为 `_MainTex.Sample(_MainTex_Sampler, i.uv)`，二者在移动端（OpenGL ES 3.0 以上）均可使用。

采样时涉及两个独立的声明，缺一不可：

```hlsl
sampler2D _MainTex;          // 纹理对象（含采样器状态）
float4 _MainTex_ST;          // Tiling 和 Offset，x=TilingX, y=TilingY, z=OffsetX, w=OffsetY
```

UV 变换使用宏 `TRANSFORM_TEX(uv, _MainTex)`，等价于 `uv * _MainTex_ST.xy + _MainTex_ST.zw`。法线贴图解包需要 `UnpackNormal(tex2D(_NormalMap, uv))`，此函数内部执行 `normal.xy = normal.xy * 2 - 1; normal.z = sqrt(1 - dot(normal.xy, normal.xy))` 的还原运算。

### 光照模型计算

Blinn-Phong 是片元着色器中实现最频繁的经典光照模型，其高光部分公式为：

$$\text{Specular} = K_s \cdot \max(0, \hat{n} \cdot \hat{h})^{\text{shininess}}$$

其中 $\hat{h} = \text{normalize}(\hat{l} + \hat{v})$ 是半角向量，$K_s$ 是镜面反射系数，`shininess` 通常取 32～256 之间的幂次值。在 Unity 内置管线中，环境光通过 `UNITY_LIGHTMODEL_AMBIENT` 宏获取，主方向光方向通过 `_WorldSpaceLightPos0.xyz` 访问（点光源时为位置而非方向，需手动计算方向向量）。

漫反射分量使用 Lambert 模型：`diffuse = max(0, dot(normal, lightDir)) * _LightColor0.rgb`。将漫反射、镜面反射和环境光三项叠加后，乘以基础颜色纹理采样值，即构成标准 Phong 着色的完整片元着色器输出。

### 输出控制与混合

`frag` 函数的返回值类型为 `float4`，语义为 `SV_Target`（即 Render Target 0）。Alpha 通道（第 4 分量）在不透明渲染路径中被 GPU 忽略，但在透明混合模式下用于控制混合权重。Unity ShaderLab 的混合命令 `Blend SrcAlpha OneMinusSrcAlpha` 对应标准 Alpha 混合方程：

$$C_{out} = \alpha \cdot C_{src} + (1 - \alpha) \cdot C_{dst}$$

MRT（多渲染目标）输出需要将返回类型改为结构体并标注 `SV_Target0`、`SV_Target1` 等多个语义，Deferred Rendering 的 G-Buffer 填充阶段正是利用此机制在单次 Draw Call 中同时写入 Albedo、Normal、Specular 等多张缓冲区。

---

## 实际应用

**溶解效果**：采样一张噪声纹理的 R 通道值，与材质属性 `_DissolveThreshold`（范围 0～1）做比较，使用 `clip(noiseValue - _DissolveThreshold)` 丢弃满足条件的片元。`clip(x)` 在 x < 0 时丢弃当前片元，不向 RT 写入任何值，配合边缘颜色叠加可实现火焰灼烧风格的溶解边缘。

**Rim Light（边缘光）**：在片元着色器中计算视线方向与法线的点积，`rimFactor = 1.0 - saturate(dot(normalize(viewDir), normalize(normal)))`，当视线与表面趋于垂直时 `rimFactor` 接近 1，将其乘以边缘光颜色叠加即可实现角色轮廓发光效果，无需额外 Pass。

**UV 动画水面**：对时间变量 `_Time.y`（Unity 内置，单位秒）进行利用，对水面纹理 UV 做 `uv += _Time.y * _FlowSpeed` 偏移，再叠加两层不同频率的法线贴图采样结果，可以零运行时开销地模拟水面流动，实现仅靠单 Pass 片元着色器完成的动态水效。

---

## 常见误区

**误区一：认为 `SV_POSITION` 可以在片元着色器中读取屏幕坐标**。实际上，`SV_POSITION` 在片元阶段由系统填写为像素中心坐标，但在 DX9/OpenGL ES 2.0 的部分实现中此值不可靠或不可读。正确做法是在顶点着色器中用 `ComputeScreenPos()` 计算并通过 `TEXCOORD` 语义额外传递，在 `frag` 中使用 `i.screenPos.xy / i.screenPos.w` 获取归一化屏幕坐标。

**误区二：在片元着色器中对法线直接使用顶点插值结果而不归一化**。顶点法线经过插值后长度会偏离 1（两个单位向量的线性插值不再是单位向量），直接参与光照计算会导致高光形状错误、边缘过渡不自然。务必在使用前执行 `normalize(i.normal)`，这是片元着色器法线处理的必要步骤而非可选优化。

**误区三：混淆 `tex2D` 中采样器状态与纹理对象的职责**。`sampler2D` 同时封装了纹理数据与采样器状态（Filter 模式、Wrap 模式），修改 Unity Inspector 中纹理的 Filter 设置会影响该 `sampler2D` 的采样结果。而在 DX11 风格的分离式声明中，`Texture2D` 和 `SamplerState` 是独立对象，可以用一个 `SamplerState` 对多张纹理进行采样，理解这一区别对跨平台 Shader 开发至关重要。

---

## 知识关联

片元着色器编写以 **HLSL 基础**为直接前置，要求掌握 `float4`、`saturate`、`lerp`、`dot` 等内置函数，以及结构体声明与语义绑定语法。本文档中的 Blinn-Phong 实现是进入**自定义光照模型**的起点，后者将扩展至基于物理的 Cook-Torrance BRDF；掌握多纹理采样与 Alpha 控制后，可直接进入**屏幕空间效果**（后处理中 `_GrabTexture` / `_CameraOpaqueTexture` 的采样逻辑与普通纹理采样完全一致）。**PBR 材质基础**中的金属度/粗糙度工作流依赖片元着色器中法线、视线、光线向量的精确计算，正是本文档光照模型部分的直接延伸。**Shader 变体管理**要求对片元着色器的条件分支进行 `#pragma multi_compile` 拆分，调试问题时配合**Shader 调试
