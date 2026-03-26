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
content_version: 2
quality_tier: "B"
quality_score: 45.4
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


# 金属度工作流

## 概述

金属度工作流（Metallic-Roughness Workflow）是由迪士尼在2012年SIGGRAPH大会上发布的"迪士尼原则BRDF"（Disney Principled BRDF）中推广的一套PBR材质参数化方案，随后被Unreal Engine 4、Unity的Standard Shader以及glTF 2.0标准所采用，成为实时渲染领域最主流的工作流之一。它的核心思想是用两张（或三张）贴图——基础色（BaseColor）、金属度（Metallic）、粗糙度（Roughness）——来区分金属与非金属材质的渲染行为，并让美术人员无需手动输入折射率等物理参数即可获得物理正确的结果。

之所以称为"金属度工作流"，是因为它用一个0到1的灰度值来描述材质在金属与绝缘体（非金属）之间的过渡：0代表纯绝缘体，1代表纯金属，中间值通常只用于锈迹、氧化层等混合区域。这种设计大幅降低了美术制作的认知门槛，但要求制作者必须理解参数的物理含义才能避免错误。

## 核心原理

### BaseColor贴图的双重语义

在金属度工作流中，BaseColor贴图存储的含义随金属度值的不同而改变：当Metallic=0时，BaseColor代表漫反射反照率（Albedo），即材质的漫射颜色，数值应在sRGB空间下保持在50–240范围（约0.04–1.0线性空间），不应包含光照或AO信息；当Metallic=1时，BaseColor代表金属的F0镜面反射率，即在0度入射角时的反射颜色，铜的F0约为(0.955, 0.638, 0.538)，金的F0约为(1.0, 0.766, 0.336)。这种双重语义是金属度工作流与高光工作流最本质的差异——同一张贴图在不同材质区域扮演不同角色。

### 金属度参数的物理意义

金属度（Metallic）参数控制渲染器如何分配漫反射分量与镜面反射分量。对于Metallic=0的绝缘体，渲染器使用BaseColor作为漫反射颜色，同时使用固定的F0≈0.04（对应折射率约为1.5，覆盖大多数塑料、石材、木材）计算菲涅尔反射；对于Metallic=1的金属，渲染器将漫反射分量归零（金属没有次表面漫射），完全使用BaseColor作为彩色F0计算镜面高光。因此，在制作铁锈或脏污时，通常将锈蚀区域的Metallic值设为0，而非尝试改变高光颜色。

### 粗糙度参数与微表面模型

粗糙度（Roughness）直接映射到Cook-Torrance微表面BRDF中的α参数。α = Roughness²（UE4采用此平方映射以使感知线性化），NDF（法线分布函数）常用GGX/Trowbridge-Reitz模型：

**D(h) = α² / (π · ((n·h)²(α²−1)+1)²)**

其中h为半向量，n为表面法线，α为经过平方映射后的粗糙度。Roughness=0时表面为完美镜面，Roughness=1时高光完全扩散。一张8位灰度的Roughness贴图即可描述从抛光金属（0.0–0.1）到粗糙混凝土（0.8–0.95）的全范围变化。

## 实际应用

**金属材质制作**：制作不锈钢材质时，Metallic贴图使用纯白（1.0），BaseColor填写钢的F0颜色（约(0.56, 0.57, 0.58)线性空间），Roughness贴图在抛光区域填写0.1–0.2，划痕区域升高至0.5–0.7。注意BaseColor中不应出现偏黄或偏蓝的饱和色调，否则会产生不真实的彩色高光。

**混合材质（局部锈蚀金属）**：在Metallic贴图中，金属区域=1，锈蚀区域=0；BaseColor中金属区域写入铁的F0颜色(0.56, 0.57, 0.58)，锈蚀区域写入锈的漫反射颜色（红棕色）；Roughness中锈蚀区域设置为0.7–0.9。这样渲染器会在锈蚀区域自动切换为漫反射模式，产生物理正确的外观。

**glTF 2.0中的打包规范**：金属度工作流被glTF 2.0标准化，规定Metallic存储在通道B，Roughness存储在通道G，两者共用一张名为`metallicRoughnessTexture`的贴图，以节省纹理采样次数。这一打包方式是引擎间交换金属度工作流资产时必须遵守的规范。

## 常见误区

**误区一：金属度可以使用0.5等中间值来表示"半金属"材质**。实际上，自然界中不存在物理意义上的"半金属"表面，Metallic的中间值只适用于两种不同材质在像素层面发生混合的边界区域（如锈蚀边缘），或来自Metallic贴图的抗锯齿模糊。如果为整块材质设置Metallic=0.5，会导致漫反射颜色与F0颜色的双重错误，产生无法解释的灰色高光。

**误区二：BaseColor贴图可以包含烘焙好的AO或腔体光影**。金属度工作流的BaseColor必须是纯净的无光照反照率数据，混入AO会导致间接光照计算重复叠加，使材质在IBL（基于图像的光照）环境中显得过暗。AO信息应单独存入OcclusionTexture（在glTF中通道R）。

**误区三：粗糙度=1−光泽度（Glossiness）**。该转换关系成立于高光工作流（Specular-Glossiness），但两者的粗糙度/光泽度贴图的灰度倒置并不意味着视觉效果完全一致，因为金属度工作流中金属F0由BaseColor控制，而高光工作流中F0由独立的Specular贴图控制，直接反转通道会导致金属材质F0信息丢失。

## 知识关联

学习金属度工作流需要先建立PBR材质概述中的物理概念基础，特别是菲涅尔效应（Fresnel）和微表面理论——没有这些概念，就无法理解Metallic=0时为何F0固定为0.04，以及Roughness为何需要平方映射才能感知线性。完成金属度工作流的学习之后，高光工作流（Specular-Glossiness Workflow）的学习会更加清晰：两者渲染结果可以等价，但高光工作流用独立的Specular贴图替代了Metallic贴图和BaseColor的双重语义，给美术人员带来更多手动控制的灵活性，同时也带来了"能量守恒破坏"的更高风险。理解两种工作流的参数映射关系，是进行Substance Painter等工具中跨工作流材质转换的必要前提。