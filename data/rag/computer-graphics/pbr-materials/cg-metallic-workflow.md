---
id: "cg-metallic-workflow"
concept: "金属度工作流"
domain: "computer-graphics"
subdomain: "pbr-materials"
subdomain_name: "PBR材质"
difficulty: 2
is_milestone: false
tags: ["实践"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 82.5
generation_method: "ai-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v2"
  - type: "academic"
    citation: "Burley, B. (2012). Physically-Based Shading at Disney. SIGGRAPH 2012 Course: Practical Physically Based Shading in Film and Game Production."
  - type: "academic"
    citation: "Karis, B. (2013). Real Shading in Unreal Engine 4. SIGGRAPH 2013 Course: Physically Based Shading in Theory and Practice."
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-06
---


# 金属度工作流

## 概述

金属度工作流（Metallic-Roughness Workflow）是由迪士尼研究院的Brent Burley在2012年SIGGRAPH大会上发布的"迪士尼原则BRDF"（Disney Principled BRDF）中系统推广的一套PBR材质参数化方案。该方案随后被Epic Games的Unreal Engine 4（2012年发布，2014年引擎开源）、Unity的Standard Shader（Unity 5.0，2015年3月正式发布）以及Khronos Group制定的glTF 2.0标准（2017年6月正式发布）所采用，成为实时渲染领域最主流的工作流之一。

它的核心思想是用两张（或三张）贴图——基础色（BaseColor）、金属度（Metallic）、粗糙度（Roughness）——来区分金属与非金属材质的渲染行为，并让美术人员无需手动输入折射率（IOR）等物理参数即可获得物理正确的结果。之所以称为"金属度工作流"，是因为它用一个0到1的灰度值来描述材质在金属与绝缘体（非金属）之间的过渡：0代表纯绝缘体，1代表纯金属，中间值通常只用于锈迹、氧化层等混合区域。这种设计大幅降低了美术制作的认知门槛，但要求制作者必须理解参数的物理含义才能避免错误。

## 核心原理

### BaseColor贴图的双重语义

在金属度工作流中，BaseColor贴图存储的含义随金属度值的不同而改变：当Metallic=0时，BaseColor代表漫反射反照率（Albedo），即材质的漫射颜色，数值应在sRGB空间下保持在50–240范围（约0.04–1.0线性空间），不应包含光照或AO信息；当Metallic=1时，BaseColor代表金属的F0镜面反射率，即在0度入射角时的反射颜色。以下为常见金属F0参考数值（线性空间RGB）：

- 铜（Copper）：约 $(0.955,\ 0.638,\ 0.538)$
- 金（Gold）：约 $(1.000,\ 0.766,\ 0.336)$
- 铁（Iron）：约 $(0.560,\ 0.570,\ 0.580)$
- 铝（Aluminum）：约 $(0.913,\ 0.922,\ 0.924)$

这种双重语义是金属度工作流与高光工作流（Specular-Glossiness Workflow）最本质的差异——同一张贴图在不同材质区域扮演不同角色。

### 金属度参数的物理意义

金属度（Metallic）参数控制渲染器如何分配漫反射分量与镜面反射分量。对于Metallic=0的绝缘体，渲染器使用BaseColor作为漫反射颜色，同时使用固定的 $F_0 \approx 0.04$（对应折射率约为1.5，覆盖大多数塑料、石材、木材）计算菲涅尔反射；对于Metallic=1的金属，渲染器将漫反射分量归零（金属不存在次表面漫射现象），完全使用BaseColor作为彩色F0计算镜面高光。

菲涅尔反射率的近似计算采用Schlick公式（Christophe Schlick，1994年提出）：

$$F(\theta) = F_0 + (1 - F_0)(1 - \cos\theta)^5$$

其中 $\theta$ 为入射光线与表面法线的夹角，$F_0$ 为0度入射角时的反射率。对于绝缘体，$F_0 \approx 0.04$；对于金属，$F_0$ 由BaseColor直接提供。因此，在制作铁锈或脏污时，通常将锈蚀区域的Metallic值设为0，而非尝试改变高光颜色。

### 粗糙度参数与微表面模型

粗糙度（Roughness）直接映射到Cook-Torrance微表面BRDF中的 $\alpha$ 参数。UE4采用平方映射以使感知线性化，即：

$$\alpha = \text{Roughness}^2$$

NDF（法线分布函数）常用GGX/Trowbridge-Reitz模型（Walter et al., 2007年正式引入图形学），其公式为：

$$D(\mathbf{h}) = \frac{\alpha^2}{\pi \cdot \left[(\mathbf{n} \cdot \mathbf{h})^2(\alpha^2 - 1) + 1\right]^2}$$

其中 $\mathbf{h}$ 为半向量，$\mathbf{n}$ 为表面法线，$\alpha$ 为经过平方映射后的粗糙度。Roughness=0时表面为完美镜面，Roughness=1时高光完全扩散。一张8位灰度的Roughness贴图即可描述从抛光金属（0.0–0.1）到粗糙混凝土（0.8–0.95）的全范围变化。

## 实际应用示例

**例如：不锈钢材质制作**
制作不锈钢材质时，Metallic贴图使用纯白（1.0），BaseColor填写钢的F0颜色（约 $(0.56,\ 0.57,\ 0.58)$ 线性空间），Roughness贴图在抛光区域填写0.1–0.2，划痕区域升高至0.5–0.7。注意BaseColor中不应出现偏黄或偏蓝的饱和色调，否则会产生不真实的彩色高光。此外，在Substance Painter 2023版本中，可以直接在金属度工作流通道中预览物理校正过的F0值，方便对照参考数据校准颜色。

**例如：混合材质（局部锈蚀金属）**
在Metallic贴图中，金属区域=1，锈蚀区域=0；BaseColor中金属区域写入铁的F0颜色 $(0.56,\ 0.57,\ 0.58)$，锈蚀区域写入锈的漫反射颜色（红棕色，约 $(0.45,\ 0.18,\ 0.08)$ 线性空间）；Roughness中锈蚀区域设置为0.7–0.9。这样渲染器会在锈蚀区域自动切换为漫反射模式，产生物理正确的外观，无需额外编写自定义着色器逻辑。

**glTF 2.0中的打包规范**：金属度工作流被glTF 2.0标准化，规定Metallic存储在纹理通道B，Roughness存储在通道G，两者共用一张名为`metallicRoughnessTexture`的贴图，以节省纹理采样次数。OcclusionTexture单独存储，其数值写入通道R。这一打包方式是引擎间交换金属度工作流资产时必须遵守的规范，Blender 3.x、Unreal Engine 5以及Three.js均原生支持该格式。

## 常见误区与错误排查

**误区一：金属度可以使用0.5等中间值来表示"半金属"材质。**
实际上，自然界中不存在物理意义上的"半金属"表面，Metallic的中间值只适用于两种不同材质在像素层面发生混合的边界区域（如锈蚀边缘），或来自Metallic贴图的抗锯齿模糊。如果为整块材质设置Metallic=0.5，会导致漫反射颜色与F0颜色的双重错误，产生无法解释的灰色高光。

**误区二：BaseColor贴图可以包含烘焙好的AO或腔体光影。**
金属度工作流的BaseColor必须是纯净的无光照反照率数据，混入AO会导致间接光照计算重复叠加，使材质在IBL（基于图像的光照）环境中显得过暗。AO信息应单独存入OcclusionTexture（在glTF中通道R）。

**误区三：粗糙度=1−光泽度（Glossiness）直接等效。**
该转换关系成立于高光工作流（Specular-Glossiness），但两者的粗糙度/光泽度贴图的灰度倒置并不意味着视觉效果完全一致，因为金属度工作流中金属F0由BaseColor控制，而高光工作流中F0由独立的Specular贴图控制，直接反转通道会导致金属材质F0信息丢失。Adobe在2022年发布的Substance转换工具中已针对此问题提供了专用的跨工作流烘焙选项。

## 思考与练习

**问题1**：在金属度工作流中，若一块材质的BaseColor为纯红色 $(1.0,\ 0.0,\ 0.0)$，Metallic=1，Roughness=0.05，在白色点光源照射下，其镜面高光的颜色应当是什么？为什么？

**问题2**：若要将一套高光工作流（Specular-Glossiness）的材质迁移至金属度工作流，对于非金属区域（如木材、石材），应当如何从Specular贴图推算出对应的Metallic值和BaseColor值？这个推算过程中会损失哪些信息？

**问题3**：当一张Roughness贴图从8位精度压缩为BC4格式（每通道4位等效精度）时，Roughness值为0.1的抛光金属区域与Roughness值为0.9的粗糙混凝土区域，哪一个区域对量化误差更敏感？结合 $\alpha = \text{Roughness}^2$ 的平方映射关系分析原因。

## 知识关联

学习金属度工作流需要先建立PBR材质概述中的物理概念基础，特别是菲涅尔效应（Fresnel Effect）和微表面理论（Microfacet Theory）——没有这些概念，就无法理解Metallic=0时为何F0固定为0.04，以及Roughness为何需要平方映射才能感知线性。Burley（2012）在其原始论文中指出，直接使用线性Roughness会导致感知上粗糙度变化集中于高端，平方映射能使美术调节更加直觉化，这一结论随后被Karis（2013）在UE4的实现中进一步验证和采用。

完成金属度工作流的学习之后，高光工作流（Specular-Glossiness Workflow）的学习会更加清晰：两者渲染结果在理论上可以等价，但高光工作流用独立的Specular贴图替代了Metallic贴图和BaseColor的双重语义，给美术人员带来更多手动控制的灵活性，同时也带来了"能量守恒破坏"的更高风险。高光工作流目前主要见于Autodesk的遗留项目以及部分欧洲影视制作管线，而金属度工作流在游戏引擎生态中占据绝对主导地位。理解两种工作流的参数映射关系，是进行Substance Painter等工具中跨工作流材质转换的必要前提，也是从事游戏资产外包交付时经常需要面对的实际问题。

## 参考文献

- Burley, B. (2012). Physically-Based Shading at Disney. *SIGGRAPH 2012 Course: Practical Physically Based Shading in Film and Game Production*. Disney Animation Studios.
- Karis, B. (2013). Real Shading in Unreal Engine 4. *SIGGRAPH 2013 Course: Physically Based Shading in Theory and Practice*. Epic Games.
- Walter, B., Marschner, S. R., Li, H., & Torrance, K. E. (2007). Microfacet Models for Refraction through Rough Surfaces. *Proceedings of the 18th Eurographics Conference on Rendering Techniques (EGSR