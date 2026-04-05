---
id: "cg-pbr-intro"
concept: "PBR材质概述"
domain: "computer-graphics"
subdomain: "pbr-materials"
subdomain_name: "PBR材质"
difficulty: 1
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# PBR材质概述

## 概述

PBR（Physically Based Rendering，基于物理的渲染）是一套基于真实光物理规律来描述材质与光照交互的渲染方法论。与传统的 Phong 或 Blinn-Phong 着色模型不同，PBR 不允许美术人员随意调整高光颜色与漫反射颜色的相互组合——所有参数都必须在物理约束范围内运行。这意味着一个材质在室内弱光、室外正午阳光、霓虹灯下都应当呈现出一致且正确的视觉结果。

PBR 的概念并非突然出现。迪士尼研究院在 2012 年 SIGGRAPH 上发表了著名的"Disney Principled BRDF"论文（Burley, 2012），将学术界已有的物理渲染理论系统性地整合为美术人员可用的直觉参数，这篇论文被普遍视为 PBR 在游戏与电影行业大规模落地的起点。此后 Unreal Engine 4（2014 年发布）和 Unity 5（2015 年发布）相继将 PBR 作为默认渲染管线，使其成为实时渲染领域的行业标准。

PBR 之所以重要，是因为它将"材质"从一组经验数值提升为对真实物理属性的量化描述：金属度（Metallic）描述导体还是绝缘体，粗糙度（Roughness）量化微表面起伏程度，基础色（Base Color / Albedo）表示物体本征颜色。这三张贴图构成金属度工作流的核心三角，让不同引擎、不同光照环境中的材质可以"移植"并保持视觉一致性。

---

## 核心原理

### 能量守恒定律

PBR 的第一条硬性约束是**能量守恒（Energy Conservation）**：材质反射出去的光能总量不能超过入射光能。用公式表达为：

$$f_{diffuse} + f_{specular} \leq 1$$

其中 $f_{diffuse}$ 是漫反射分量，$f_{specular}$ 是镜面反射分量。传统 Phong 模型可以让美术人员将漫反射颜色设为纯白（1, 1, 1）同时让高光系数极高，这在物理上是不可能的——白色漫反射意味着入射光已全部被散射，没有能量留给高光。PBR 通过 Fresnel 方程自动调节这一比例，使高光增强时漫反射自动减弱。

### 微表面理论（Microfacet Theory）

PBR 的第二个支柱是微表面模型。任何宏观表面在微观尺度上都是由无数朝向随机分布的微小镜面（微表面法线，microfacet normal）构成的。粗糙度参数 $\alpha$ 控制这些微表面法线的分布宽度——$\alpha = 0$ 表示所有微表面法线与宏观法线完全对齐（完美镜面），$\alpha = 1$ 表示微表面法线均匀分布于半球（完全漫反射）。

微表面 BRDF 的完整形式为：

$$f(l, v) = \frac{D(h) \cdot F(v, h) \cdot G(l, v, h)}{4(n \cdot l)(n \cdot v)}$$

- $D(h)$：**法线分布函数（NDF）**，如 GGX/Trowbridge-Reitz，描述有多少微表面朝向半角向量 $h$
- $F(v, h)$：**Fresnel 方程**，描述在特定观察角度下反射与透射的比例
- $G(l, v, h)$：**几何遮蔽函数**，描述微表面之间相互遮挡（shadowing）与自遮蔽（masking）的比例
- 分母 $4(n \cdot l)(n \cdot v)$ 是归一化因子

### Fresnel 效应

Fresnel 效应规定：当视线与表面夹角趋近于 90°（掠射角）时，几乎所有材质——无论导体还是绝缘体——都会呈现接近 100% 的镜面反射。绝缘体（如塑料、木材）在正视角的反射率（F0）通常在 **2%~5%** 之间，对应折射率约为 1.5；而金属的 F0 往往高达 **60%~100%**，且具有有色反射（铜的 F0 约为 (0.95, 0.64, 0.54)）。Schlick 近似公式简化了 Fresnel 计算：

$$F_{Schlick}(v, h) = F_0 + (1 - F_0)(1 - v \cdot h)^5$$

这个公式是实时渲染中最常用的 Fresnel 近似，误差在工程上可接受。

---

## 实际应用

**游戏材质制作流程**：在 Substance Painter 中，美术人员导出的标准 PBR 贴图集包含 Base Color、Roughness（0 = 镜面，1 = 粗糙）、Metallic（0 = 绝缘体，1 = 导体）和 Normal Map 四张。将同一套贴图导入 Unreal Engine 5 和 Unity URP，在相同 HDR 光照下应呈现几乎一致的外观——这种一致性在 Phong 模型下根本无法实现。

**环境光遮蔽与 IBL**：PBR 材质通常配合基于图像的光照（Image-Based Lighting, IBL）使用。IBL 将环境光分离为漫反射 Irradiance Map 和镜面 Radiance Map（通过预过滤 + 预积分 BRDF LUT 实现），金属材质在 IBL 下能正确呈现有色环境反射，而绝缘体高光则保持白色——这正是 Fresnel F0 物理意义的直接体现。

**影视级渲染**：Arnold、RenderMan 等离线渲染器同样基于 PBR 原则，但使用更精确的多次散射 GGX（Multi-scattering GGX）来修正单次散射模型在高粗糙度下损失能量的问题，这一修正在 2017 年后逐渐成为高端渲染器的标准配置。

---

## 常见误区

**误区一：Metallic = 1 的材质没有漫反射**
这是正确的物理描述，但初学者常常忘记设置金属材质的 Base Color，将其保留为黑色。金属的 Base Color 定义了其 F0（有色反射），如黄金 Base Color 应为暖黄色。设置为黑色的金属材质在任何角度下都显示为黑色，这是参数理解错误，而非 PBR 系统的 Bug。

**误区二：粗糙度（Roughness）与光泽度（Glossiness）是同一参数**
两者互为反数关系（Glossiness = 1 - Roughness），但在具体 NDF 计算中，不同引擎对 Roughness 的映射方式不同。Unreal Engine 将 Roughness 映射为 $\alpha = roughness^2$（感知线性化），而某些旧版引擎直接使用线性值，导致同一张粗糙度贴图在不同引擎中外观不一致，这是跨引擎迁移材质时最常见的失真来源。

**误区三：PBR 只适用于写实风格**
PBR 的物理约束保证了能量守恒，但 Base Color 和 Roughness 的具体数值完全可以超出自然界材质范围（如纯度极高的饱和色）。《风格化 PBR》（Stylized PBR）在《原神》《赛博朋克 2077》等作品中广泛应用，它们保留了 PBR 的光照响应一致性，但使用经过艺术处理的参数值，这并不违反 PBR 的框架。

---

## 知识关联

学习 PBR 材质概述后，下一步应深入 **BRDF 基础**——本文中的微表面公式 $f(l,v) = DFG / 4(n \cdot l)(n \cdot v)$ 中每一项（NDF、Fresnel、几何遮蔽）都需要展开理解其具体数学形式，例如 GGX NDF 的完整推导和 Smith 几何遮蔽函数的分离形式。

**金属度工作流**是 PBR 两大贴图工作流（金属度/粗糙度 vs 高光/光泽度）中更主流的一套，它将本文中 Metallic 与 Roughness 参数的物理含义转化为美术制作的具体规范——例如绝缘体 Base Color 的亮度值不应超过 240 sRGB，金属 Base Color 亮度不应低于 180 sRGB，这些规范都直接来源于 Fresnel F0 的物理约束。