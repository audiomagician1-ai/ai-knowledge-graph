---
id: "3da-tex-base-color"
concept: "BaseColor贴图"
domain: "3d-art"
subdomain: "texturing"
subdomain_name: "纹理绘制"
difficulty: 2
is_milestone: false
tags: ["核心"]

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


# BaseColor贴图

## 概述

BaseColor贴图（基础颜色贴图）是PBR（基于物理的渲染）工作流中定义物体固有色的纹理通道，存储的是材质在完全均匀白色光照下、移除所有光影信息后的纯色彩数据。它以线性色彩空间编码存储（在引擎中通常需要标记为sRGB以进行Gamma校正），每个像素记录的是材质对漫反射光线的反射率与金属材质的镜面反射颜色。

BaseColor概念随着迪士尼在2012年发表的"Physically-Based Shading at Disney"论文而普及，取代了传统Phong着色流程中Diffuse（漫反射）贴图的地位。两者的本质区别在于：旧流程的Diffuse贴图允许包含烘焙好的阴影、AO（环境遮蔽）和高光，而BaseColor必须严格剔除这些光照信息，因为PBR引擎会实时计算这些效果。

这一区分至关重要：一张带有手绘阴影的BaseColor贴图，在引擎的实时光照下会产生"双重阴影"——原本烘焙进贴图的固定阴影与引擎计算的动态阴影叠加，导致材质在不同光照环境（白天/夜晚/室内）下观感严重失真。

## 核心原理

### 色值范围限制

BaseColor的明度值受到严格的物理约束。根据PBR理论，自然界中几乎没有完全吸收光线（纯黑）或完全反射光线（纯白）的材质。在0-255的8位通道中，非金属材质（介电质）的BaseColor明度范围通常限制在**50至240之间**（sRGB空间），换算为线性反射率约为0.04至0.9。木材、混凝土等暗色材质约在50-100区间，雪、白纸等亮色材质约在210-240区间。违反这一范围会导致材质在PBR引擎中出现能量不守恒的渲染错误。

### 金属与非金属的差异存储逻辑

BaseColor在金属工作流（Metallic/Roughness Workflow）中承载了双重功能。当金属度（Metallic）贴图对应像素为0（非金属）时，BaseColor存储的是漫反射颜色；当金属度为1（纯金属）时，BaseColor存储的是金属的镜面反射颜色（F0值），例如金的BaseColor约为(255, 197, 85)，铁约为(196, 199, 199)。这意味着金属材质的BaseColor明度通常集中在**180至255**之间，因为真实金属对可见光的反射率极高。

### 色彩空间与Gamma校正

BaseColor贴图必须在DCC软件（如Substance Painter、Photoshop）中以sRGB色彩空间创作，但导出后在引擎（如Unreal Engine 5、Unity）中需将纹理类型标记为"Color"或"sRGB"，引擎会自动在着色器中对其进行Gamma 2.2校正，将其转换为线性空间参与光照计算。若误将BaseColor标记为线性（如同法线贴图的处理方式），颜色将显著偏暗，因为线性空间的中灰值(0.5)在显示器上会显示为约0.73亮度而非0.5。

### 不可包含的信息类型

以下信息**禁止**出现在BaseColor中：定向光阴影、烘焙AO、高光热点（Specular Highlight）、次表面散射的红边效果（这些由SSS贴图单独处理）。可以允许的是：固有色变化（如木纹的深浅）、轻微的自然颜色噪点（增加真实感），以及对于非常粗糙的材质，极其轻微的、非方向性的明暗变化（但业内有争议）。

## 实际应用

**皮肤材质制作**：人体皮肤的BaseColor应只包含皮肤底色、雀斑、色素变化等固有颜色信息，明度范围约在100-180之间（因人种而异）。鼻头、耳朵等部位的红润感属于固有颜色特征，可以保留；而由光线在皮下散射形成的红色轮廓效果不应画入BaseColor，应通过引擎的次表面散射材质实现。

**混合材质边缘处理**：制作磨损金属（如带掉漆痕迹的铁门）时，BaseColor贴图需要在原始油漆颜色区域（非金属，明度约120-200）与裸露金属区域（高明度，约180-240）之间进行过渡绘制。这种过渡的形状和分布与Metallic贴图的对应区域需严格对齐，但两者的明度分布逻辑相反——金属区域在Metallic贴图中为白色（值255），而其BaseColor值同样偏高。

**地面材质拼接**：游戏场景中的地面BaseColor贴图（如Tiling材质）绝对不能包含定向阴影，因为Tiling纹理的阴影方向会与场景主光源方向冲突，在运行时暴露出明显的重复拼接感。

## 常见误区

**误区一：将旧流程Diffuse贴图直接当作BaseColor使用**
许多从传统手绘流程转型的美术师会将包含手绘阴影和高光的Diffuse贴图直接用于PBR材质的BaseColor通道。结果是在PBR引擎实时渲染下，贴图内的"假阴影"与引擎计算的真实阴影完全不匹配，物体在旋转或光源移动时阴影异常明显。正确做法是重新绘制贴图，或使用Photoshop的"高反差保留"等方法剥离光照信息。

**误区二：认为BaseColor越接近纯黑/纯白越好**
部分初学者认为黑色材质（如轮胎橡胶）的BaseColor应该填充纯黑(0, 0, 0)。但纯黑在物理上意味着材质100%吸收所有光线，自然界不存在这样的材质。轮胎橡胶的BaseColor实测约为(30-50, 30-50, 30-50)，在PBR校验工具中显示为深灰而非纯黑。使用纯黑会导致材质在任何光照下都完全无法显现表面细节，丢失Roughness纹理所定义的微表面信息。

**误区三：将BaseColor与Albedo等同**
Albedo严格指材质的漫反射反射率（仅非金属部分），而BaseColor在金属工作流中同时编码了金属的镜面反射色（F0）。在Substance Painter中导出"BaseColor"通道与导出"Albedo"通道会得到不同结果——Albedo输出会将金属区域的镜面反射色乘以(1-Metallic)并加入漫射贡献，是供Spec/Gloss工作流使用的合并通道，不能与BaseColor互换使用于金属/粗糙度工作流。

## 知识关联

学习BaseColor贴图需要先掌握**PBR纹理工作流**的基本框架，特别是金属/粗糙度工作流中各通道的职责划分——理解Metallic贴图如何影响BaseColor的解读方式，是正确绘制BaseColor中金属区域颜色的前提。

在掌握BaseColor之后，**自发光贴图（Emissive Map）**是自然的延伸学习方向：自发光贴图同样不含光照信息，但其色值范围不受0-255的物理上限约束，可以超过1.0（HDR值）来驱动引擎的Bloom效果，这与BaseColor的物理约束范围形成鲜明对比。此外，**透明度与遮罩**贴图（Alpha Channel / Opacity Mask）有时会与BaseColor合并存储在同一张RGBA纹理中（A通道存透明度），理解BaseColor的RGB通道结构有助于掌握这种合并存储的规范操作。