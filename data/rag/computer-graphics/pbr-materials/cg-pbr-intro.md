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
quality_tier: "B"
quality_score: 47.4
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.484
last_scored: "2026-03-22"
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

PBR（Physically Based Rendering，基于物理的渲染）是一套以真实物理定律为基础建立的材质与光照渲染体系，于2010年代初在游戏和电影工业中逐步普及，Disney于2012年在SIGGRAPH发表的"Physically-Based Shading at Disney"论文标志着该体系进入主流实时渲染领域。PBR材质并不是单一算法，而是一套遵循**能量守恒**和**微表面理论**的参数化材质描述框架。

PBR之所以重要，在于它解决了传统Phong/Blinn-Phong光照模型中"高光随光源强度任意增亮"的物理错误问题。在传统模型里，美术调整高光强度时完全依赖经验，同一材质在不同光照环境下外观不一致；而PBR材质的参数（粗糙度、金属度、基础色）在任意光照条件下都能给出物理上自洽的结果，极大提升了美术资产的跨场景复用性。

## 核心原理

### 能量守恒定律

能量守恒是PBR材质最根本的物理约束：一个表面反射出去的光能量，不能超过照射到该表面的入射光能量。用公式表达为：

> **反射光能量 ≤ 入射光能量**
> 即：漫反射能量 + 镜面反射能量 ≤ 1（归一化单位下）

在实现中，这意味着当表面的镜面反射（Specular）比例升高时，漫反射（Diffuse）比例必须相应降低。传统Phong模型中可以随意将漫反射系数设为0.8、高光系数也设为0.8，两者之和超过1.0，这在物理上是不可能发生的。PBR通过菲涅耳方程自动处理两者之间的能量分配，使美术无需手动平衡这一关系。

### 微表面理论（Microfacet Theory）

微表面理论认为，任何真实表面在微观尺度上都由无数朝向各异的微小镜面（microfacet）组成，宏观的光照行为是这些微表面统计效果的总和。材质的**粗糙度（Roughness）**参数描述的正是这些微表面法线方向的离散程度：粗糙度为0时所有微表面法线完全对齐（产生锐利高光），粗糙度为1时微表面法线随机分布（产生完全漫射的高光）。

微表面模型的核心公式（Cook-Torrance BRDF的镜面反射项）为：

$$f_r = \frac{D(h) \cdot F(\mathbf{v}, h) \cdot G(\mathbf{l}, \mathbf{v}, h)}{4(\mathbf{n} \cdot \mathbf{l})(\mathbf{n} \cdot \mathbf{v})}$$

其中：
- **D**（Normal Distribution Function）：描述微表面法线分布，常用GGX/Trowbridge-Reitz函数
- **F**（Fresnel）：菲涅耳方程，描述不同观察角度下反射率的变化
- **G**（Geometry/Shadowing-Masking）：描述微表面之间互相遮挡导致的能量损失

### 菲涅耳效应

菲涅耳效应描述了反射率随观察角度变化的规律：所有材质在掠射角（光线与表面接近平行，约80°~90°）时反射率趋近于1.0，而在正面观察时反射率取决于材质本身。导体（金属）的正面反射率（F0值）通常在0.5~1.0之间，例如铝的F0约为0.96；绝缘体（非金属）的F0通常在0.02~0.05之间，例如常见塑料约为0.04（折射率约1.5）。PBR使用Schlick近似公式高效计算菲涅耳值：

$$F(\theta) = F_0 + (1 - F_0)(1 - \cos\theta)^5$$

## 实际应用

**游戏引擎中的落地**：Unity（从5.0版本起，2015年）和Unreal Engine（从4.0版本起，2014年）均内置了基于微表面理论的PBR材质系统。美术制作PBR材质时，通常提供4张贴图：基础色（BaseColor）、金属度（Metallic）、粗糙度（Roughness）、法线（Normal），引擎在渲染时自动根据上述公式计算光照结果。

**与传统材质的直观对比**：在Blinn-Phong模型中，一块磨损的铁板需要美术手动绘制高光贴图来模拟光泽变化；而在PBR材质中，美术只需调整粗糙度贴图（0=光滑有光泽，1=粗糙无光泽），引擎自动计算出在各种光照（点光、方向光、IBL环境光）下正确的高光形状与强度。同一套PBR材质参数在室内暖光和室外日光环境下均能给出视觉可信的结果，不需要分别调整。

**电影级离线渲染**：Arnold、RenderMan等离线渲染器同样采用PBR框架，区别在于可以使用更精确的多重散射GGX（Multiple Scattering GGX，2017年由Heitz等人提出）来消除高粗糙度材质偏暗的能量损失错误。

## 常见误区

**误区1：PBR等于高质量渲染**
PBR描述的是材质参数的物理合理性，与渲染精度无关。一个粗糙度固定为0.5的单色PBR材质，在低分辨率阴影和无全局光照的场景中仍然会显得廉价。PBR保证的是"光照变化时材质行为正确"，而不是"画面一定好看"。

**误区2：粗糙度为0等于完全镜面**
粗糙度为0时，GGX分布函数收敛为δ函数（理想镜面），但菲涅耳效应仍然存在。对于非金属材质（F0≈0.04），即使粗糙度为0，正面观察时仍有96%的光会折射进入材质内部发生漫反射，而非全部镜面反射。因此"粗糙度=0的非金属材质"仍然不是镜子，只是有非常锐利的高光。

**误区3：PBR材质参数没有范围限制**
PBR材质的金属度只能取0（绝缘体）或1（导体），现实中不存在"半金属"的物质状态；基础色的明度对于非金属不应低于0.02（sRGB约30/255）或高于0.9（sRGB约229/255），超出此范围的材质在物理上是不合理的，会破坏能量守恒。

## 知识关联

掌握PBR材质概述后，下一步需要学习**BRDF基础**（Bidirectional Reflectance Distribution Function），BRDF是描述光在表面如何分布反射的数学函数，上述Cook-Torrance公式正是一种具体的BRDF实现；同时还需要学习**金属度工作流**，理解金属度参数如何在着色器内部控制F0值的计算方式——金属材质的F0直接来自基础色贴图的RGB值，而非金属材质的F0固定为0.04，基础色则用于漫反射颜色，这一区分是PBR材质实际使用时最重要的操作逻辑。