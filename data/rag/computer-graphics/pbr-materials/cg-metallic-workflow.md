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

金属度工作流（Metallic-Roughness Workflow）是由Epic Games在2012年推广、随后被Khronos Group纳入glTF 2.0标准的PBR材质制作规范。它将材质的物理特性压缩为三张关键贴图：基础色（Base Color）、金属度（Metallic）和粗糙度（Roughness），用统一的物理参数描述金属与非金属两类材质。这种工作流目前是Unreal Engine、Unity HDRP、Blender Cycles以及glTF格式的默认PBR方案。

金属度工作流之所以在游戏与实时渲染领域占主导地位，是因为它将材质参数的物理意义直接映射到可感知的视觉属性上：金属度贴图是一张非0即1的二值图（过渡区仅出现在边缘氧化层等特殊情况），粗糙度贴图直接控制高光波瓣的宽窄，基础色贴图在金属区域充当F0反射率、在非金属区域充当漫反射颜色。三张贴图职责清晰，美术人员不需要在两套参数之间换算。

## 核心原理

### 金属度参数（Metallic）的物理含义

金属度贴图是一张灰度图，数值范围0到1，但在物理上只有0（非金属绝缘体）和1（纯金属导体）两种有意义的状态。当Metallic = 0时，材质的F0反射率被强制固定在4%左右（即线性空间的0.04），漫反射颜色直接读取Base Color；当Metallic = 1时，漫反射分量被清零，Base Color的RGB值被直接解释为导体的F0复折射率，用于驱动Fresnel方程的有色镜面高光。中间值（如0.5）在物理上没有实际对应物，通常只用于污垢、锈迹覆盖金属表面的混合过渡边缘，宽度通常不超过3至5个像素。

### 粗糙度参数（Roughness）的微表面关系

粗糙度值α与微表面法线分布函数（NDF，通常采用GGX/Trowbridge-Reitz模型）直接挂钩。GGX分布公式为：

$$D(h) = \frac{\alpha^2}{\pi \left[(n \cdot h)^2(\alpha^2 - 1) + 1\right]^2}$$

其中α即粗糙度值（部分引擎使用α = roughness²的感知线性映射）。Roughness = 0对应理想镜面，高光波瓣极度收窄；Roughness = 1对应完全漫射表面，高光完全散开。Unreal Engine 4内部使用的是roughness²作为GGX的α输入，因此在0.3至0.7之间的粗糙度变化在视觉上呈现接近线性的感知变化。

### 基础色贴图（Base Color）的双重角色

Base Color在金属度工作流中承担两种截然不同的物理角色，取决于同一像素位置的Metallic值。对于非金属区域（Metallic = 0），Base Color存储漫反射反照率，其亮度范围应控制在sRGB 50–240之间（约线性0.03–0.9），绝对黑与绝对白在自然材质中几乎不存在。对于金属区域（Metallic = 1），Base Color存储F0镜面反射率，纯金的F0约为(1.0, 0.782, 0.344)，铜的F0约为(0.955, 0.638, 0.538)，铝约为(0.913, 0.922, 0.924)。这两种物理含义在同一张贴图中混用，是金属度工作流区别于高光工作流的最大特征，也是初学者最容易混淆的地方。

## 实际应用

**枪械材质制作**是展示金属度工作流优势的典型案例。枪管、枪机等钢制部件的Metallic值设为1，Base Color存储钢铁的F0（约灰度0.56，线性空间约0.3）；护木、握把等聚合物部件的Metallic设为0，Base Color存储漆面或橡胶的漫反射颜色。两种材质可以绘制在同一套贴图上，只需切换Metallic通道的值即可无缝过渡。

**glTF 2.0格式**将Metallic和Roughness打包进同一张纹理的不同通道：Roughness存于G通道，Metallic存于B通道，R通道留给遮蔽贴图（AO）。这种打包方式将三张独立贴图合并为一张，减少了GPU的纹理采样次数，是该工作流在Web和移动端渲染中被广泛采用的工程原因。

**Substance Painter**导出预设中，"Metallic Roughness"模板直接对应此工作流，导出时Base Color、Metallic、Roughness分别输出为独立PNG文件，其中Base Color应勾选sRGB选项，而Metallic和Roughness必须保存为线性（非sRGB）空间，否则引擎读取时会因Gamma校正引入错误的中间值。

## 常见误区

**误区一：金属度可以用中间灰度表示"半金属"材质**。许多初学者会将脏污金属的Metallic值设为0.5，认为这代表"50%金属"。实际上现实中不存在介于导体与绝缘体之间的材质状态，0.5的Metallic值会导致漫反射和镜面反射同时存在，形成物理上不正确的双重高光。正确做法是在纯金属区域（Metallic = 1）的Base Color上叠加深色污垢遮罩，或在Metallic图上只在腐蚀区域绘制0值。

**误区二：金属的Base Color可以设为任意颜色**。导体的F0反射率受真实光学常数约束，绝大多数金属的线性亮度值在0.5–1.0之间，且具有特定色调。若将铁的Base Color设为饱和蓝色（线性约0.01–0.03），不仅物理不正确，在IBL光照下高光也会呈现错误色相。Substance Designer内置的金属F0参考库列出了约30种常见金属的准确Base Color值可供参考。

**误区三：Roughness贴图应与金属度贴图保持相同的值域范围**。两者虽然都是0–1灰度图，但Roughness = 0的镜面金属在实时渲染中会产生极度收窄的高光，对反射探针精度要求极高；而Roughness = 1的金属在物理上接近于粉末状金属（如铝粉），并非简单的"哑光"。实际资产制作中，打磨金属的Roughness一般在0.1–0.3之间，而生锈金属在0.6–0.8之间，极少触及0或1两端。

## 知识关联

学习金属度工作流需要对PBR材质概述中的微表面理论有基本了解，特别是F0（垂直入射反射率）的概念——它是区分Metallic = 0与Metallic = 1时Base Color物理含义的关键。在掌握金属度工作流之后，学习**高光工作流**（Specular-Glossiness Workflow）时会发现后者将F0单独存储在Specular贴图中，绕开了金属度的二值约定，代价是需要额外控制Specular贴图的能量守恒。两种工作流最终驱动的是同一套Cook-Torrance BRDF方程，只是输入参数的打包方式不同，因此在支持glTF的引擎中存在双向转换工具（如Khronos提供的glTF-Toolkit）可以在两者之间互转。