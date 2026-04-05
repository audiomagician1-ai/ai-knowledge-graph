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
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---

# PBR特效材质

## 概述

PBR特效材质是将基于物理的渲染（Physically Based Rendering）工作流应用于折射、透射、半透明等视觉特效场景的材质系统。与标准PBR不透明材质不同，特效材质需要同时处理光线穿透物体的行为，这要求着色器必须追踪光线在介质边界处的折射率变化（IOR，Index of Refraction）以及光能在介质内部的散射与吸收。

PBR特效材质的理论基础建立在1941年Fresnel方程和1977年Cook-Torrance反射模型之上。在Unreal Engine 4引入"Subsurface"和"Translucent"着色模型之后，PBR工作流在特效材质领域才真正系统化落地，使美术师能够用统一的物理参数描述玻璃、火焰、皮肤发光等多样效果。

特效材质之所以比普通PBR材质更复杂，根本原因在于它必须在渲染管线中同时解决两套光照方程：一套处理表面反射（遵循Cook-Torrance BRDF），另一套处理光线穿透（遵循BTDF，双向透射分布函数）。当两者合并时，能量守恒公式要求反射率R与透射率T满足 R + T = 1（忽略吸收时），这一约束直接决定了参数调节的方法论。

---

## 核心原理

### Fresnel效应与透射权重

PBR特效材质最关键的参数是折射率IOR。空气的IOR为1.0，水为1.333，玻璃约为1.5，钻石高达2.42。着色器利用Schlick近似公式计算每个像素的Fresnel反射率：

```
F(θ) = F0 + (1 - F0)(1 - cosθ)^5
F0 = ((n1 - n2) / (n1 + n2))²
```

其中 `n1` 和 `n2` 分别是入射侧和透射侧的折射率，`θ` 是光线入射角。对于水面材质，F0 ≈ 0.02，意味着法线入射时仅反射2%的光能，其余98%透射进入水体；而以掠射角观察时，Fresnel项趋近于1.0，水面几乎变成完美镜面。这个现象是湖面边缘比中心更亮的物理原因。

### 透明度混合与深度排序问题

PBR特效材质必须使用混合模式（Blend Mode），不能走标准的不透明渲染管线，这是它与普通PBR材质在技术实现上最根本的差异。在Unreal Engine中，透明材质默认禁用深度写入（Depth Write），导致多层半透明物体叠加时出现排序错误（OIT，Order Independent Transparency问题）。

解决方案有两类：一是在材质中开启"Translucency Sort Priority"并手动排序；二是使用Dithered Temporal AA（DTAA）将半透明模拟为像素级噪声抖动，换取深度缓冲写入能力。后者在Niagara粒子特效中广泛应用，因为粒子数量庞大时逐粒子排序的CPU开销不可接受。

### 体积吸收与Beer-Lambert定律

特效材质中的彩色玻璃、毒液、深海水体等效果需要模拟光线在介质内部传播时的颜色衰减。物理上这遵循Beer-Lambert定律：

```
I(d) = I0 × e^(-μ × d)
```

其中 `I0` 是入射光强，`d` 是光线在介质中的穿透深度，`μ` 是材质的吸收系数（单位：1/cm）。在Shader中，`d` 通过场景深度与当前像素深度的差值近似（SceneDepth - PixelDepth），然后对每个颜色通道分别施加指数衰减，红色衰减慢则呈现红色调，蓝绿色衰减慢则呈现海水般的蓝绿色。这是Unreal的"Refraction"材质输入节点背后的计算逻辑。

### 次表面散射（SSS）的PBR实现

皮肤发光、玉石、蜡烛等半透明特效依赖次表面散射模型。Unreal Engine使用基于预积分的SSS近似：将入射光在表面下方的散射距离用"Subsurface Color"和"Opacity"两个参数共同控制。散射半径（Scatter Radius）在实践中通常设为0.1cm到1.5cm之间（对应皮肤的真实散射数据），超出此范围会破坏能量守恒，导致特效看起来像自发光而非透光。

---

## 实际应用

**火焰与爆炸粒子**：爆炸火球的外焰使用Additive混合模式，Emissive Color驱动HDR亮度值（通常超过1.0，最高可达50.0 nit以上模拟物理亮度），内焰使用Translucent模式配合Particle Color节点控制生命周期内的颜色温度变化（从白热3500K渐变为橙红色1800K）。

**玻璃破碎特效**：破碎玻璃碎片材质需要同时表达IOR=1.5的折射扭曲、Roughness驱动的模糊折射（磨砂玻璃效果），以及边缘Fresnel高光。折射扭曲量在Unreal材质中由Refraction输入控制，值为1.0表示无扭曲，1.5对应标准玻璃折射强度，数值过高（>2.0）会产生非物理的过度扭曲，在运动时暴露为明显的屏幕空间采样边界瑕疵。

**毒液/酸液泼溅**：结合Beer-Lambert深度吸收（绿色通道衰减系数μ最小，其余通道μ较大），配合Opacity由深度差值驱动（物体完全浸入时Opacity=1，表面薄层时趋近0），实现越厚越不透明、边缘越薄越透明的物理正确效果。

---

## 常见误区

**误区一：直接调高Opacity来增强半透明感**。Opacity参数在Translucent材质中控制的是表面最终与背景的Alpha混合比例，与物理上的光线透射量并非同一概念。提高Opacity实际上是减少透射（让材质更不透明），正确的做法是降低Opacity并同时调整Fresnel F0以及Roughness来控制视觉上的"轻薄感"。

**误区二：认为PBR特效材质不需要考虑能量守恒**。特效材质的自发光（Emissive）部分确实不受能量守恒约束，但Specular与Transmission部分仍然必须满足R + T ≤ 1。常见错误是将Specular设为1.0同时保持高透射，这会产生比入射光更亮的反射，使特效在HDR场景中爆光失真。

**误区三：将Subsurface材质误用于薄片半透明**。Subsurface着色模型适用于具有真实体积厚度的物体（皮肤、蜡、玉石），若用于薄片树叶或花瓣的半透明特效，应改用"Two Sided Foliage"或"Thin Translucent"着色模型，后者在Unreal 4.26版本后专门提供，能正确处理薄层介质中几乎无散射的直接透射。

---

## 知识关联

PBR特效材质直接依赖**混合模式**的理解，因为不同混合模式（Additive、Translucent、Modulate）决定了特效材质与场景颜色缓冲的合成方式，而这一合成操作发生在PBR光照计算之后。选错混合模式会导致Fresnel计算结果正确但最终画面出现颜色倍增或HDR曝光异常。

在更广的Shader特效体系中，PBR特效材质的折射扭曲技术（SceneTexture采样偏移）是实现水面、热浪、传送门等屏幕空间变形特效的基础实现手段，而体积吸收中使用的深度差值采样逻辑，同样是软粒子（Soft Particle）和景深（Depth of Field）特效的核心着色器构件。