---
id: "3da-tex-pbr-workflow"
concept: "PBR纹理工作流"
domain: "3d-art"
subdomain: "texturing"
subdomain_name: "纹理绘制"
difficulty: 2
is_milestone: true
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 50.4
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.412
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# PBR纹理工作流

## 概述

PBR（Physically Based Rendering，基于物理的渲染）纹理工作流是一套以真实物理光照模型为基础的贴图制作规范，于2012至2014年间由迪士尼（Disney）研究院和Epic Games等公司相继推广，彻底改变了游戏与影视行业的材质制作方式。其核心思想是通过测量真实材质的反射率和粗糙度等物理属性，将这些数据以贴图形式存储，使模型在任意光照环境下都能呈现出物理正确的外观。

PBR工作流目前在游戏引擎（Unreal Engine 4/5、Unity HDRP）和DCC软件（Substance 3D、Marmoset Toolbag）中全面普及，成为游戏美术、影视特效和产品可视化领域的行业标准。与旧式的Diffuse/Specular工作流相比，PBR材质的参数含义清晰、可预测性强，美术师无需猜测光照环境就能制作出正确的贴图。

## 核心原理

### Metallic-Roughness工作流

Metallic-Roughness（金属度-粗糙度）是目前最主流的PBR工作流，由Allegorithmic（现Adobe）在Substance系列软件中大力推广，Unity和Unreal Engine默认均采用此方案。该工作流使用三张核心贴图：**BaseColor**（基础色）、**Metallic**（金属度）和**Roughness**（粗糙度）。

Metallic贴图是一张黑白图，其中纯黑（0）表示非金属介质，纯白（1）表示金属。物理上讲，非金属材质的菲涅耳反射率（F0）固定约为0.04（即4%），而金属材质的F0则直接从BaseColor贴图中读取，通常在70%～100%之间。这意味着在Metallic-Roughness工作流中，Metallic贴图的值在实际项目中应严格为0或1，中间灰值仅用于表达氧化层或混合过渡区域，不应大面积使用。

### Specular-Glossiness工作流

Specular-Glossiness（高光度-光泽度）工作流由Allegorithmic与Arnold渲染器等离线渲染方向共同使用，在旧版游戏引擎和部分影视管线中仍然存在。该工作流使用**Diffuse**（漫反射色）、**Specular**（高光颜色）和**Glossiness**（光泽度）三张贴图，其中Glossiness与Roughness的关系为：Glossiness = 1 − Roughness。

Specular贴图是RGB彩色图，可直接定义材质的F0反射颜色，给美术师更多手动控制权，但代价是更容易犯物理错误。例如，将非金属材质的Specular值设得过高（超过0.08即8%），会产生明显不真实的塑料感，这是该工作流的常见陷阱。

### 能量守恒与线性空间

两种工作流都遵循能量守恒定律，即材质反射的光能不得超过接收的光能。实现这一点的技术前提是所有贴图必须在**线性颜色空间**中参与计算。具体规则是：BaseColor和Specular贴图存储在sRGB空间（Gamma 2.2），导入引擎时需标记为sRGB以进行自动校正；而Roughness、Metallic和Normal贴图存储的是线性数据，导入时必须标记为Linear（非颜色数据），否则粗糙度和金属度的计算结果会严重偏差。

## 实际应用

**角色皮甲制作**：制作一套金属盔甲时，Metallic工作流下金属部分的BaseColor应绘制金属本身的反射色（如钢铁的深灰色RGB约为180,180,180），Metallic值填1；皮质部分BaseColor绘制皮革固有色，Metallic值填0，Roughness值设为0.6至0.8之间模拟皮革的漫散射感。

**虚幻引擎材质实例**：在Unreal Engine 5中，将上述三张贴图连接至M_Master材质的对应插槽后，模型在Lumen全局光照下无需任何额外调整即可在室内、户外、HDR天光等不同场景保持正确的视觉效果，这正是PBR物理正确性的直接体现。

**贴图转换**：在某些旧项目升级中，需要将Specular-Glossiness工作流贴图转换为Metallic-Roughness工作流。Substance 3D Painter提供了专用转换算法：对于非金属区域，Metallic填0，BaseColor直接使用Diffuse贴图；对于金属区域，将Specular贴图的亮度值作为Metallic的参考，并从Specular颜色反算BaseColor。

## 常见误区

**误区一：Metallic贴图可以使用大量灰色过渡**
许多初学者误以为Metallic贴图应该像AO贴图一样绘制丰富的灰度细节。实际上，真实世界中材质要么是金属要么是非金属，Metallic值的灰色区域（如0.2到0.8）在物理上没有对应的真实材质，大量使用会导致渲染结果出现明显的虚假质感。过渡灰值只应出现在金属与非金属的交界边缘1到2像素范围内。

**误区二：两种工作流可以随意混用**
Metallic-Roughness和Specular-Glossiness的贴图不能直接互换使用。将Specular-Glossiness工作流的Diffuse贴图直接当作Metallic-Roughness的BaseColor使用会导致金属部分过亮，因为Specular工作流的Diffuse在金属区域接近纯黑，而Metallic工作流的BaseColor在金属区域应包含反射色信息。

**误区三：Roughness值越低效果越好**
部分美术师追求"高光锐利"的视觉效果，将几乎所有材质的Roughness值设到0.05以下。真实材质中即便是高度抛光的金属表面，Roughness值也通常在0.05到0.15之间，玻璃约为0.0到0.05，而普通漆面金属约在0.2到0.4之间。过低的Roughness值会使材质显得"像镜面"，失去材质本身的质感层次。

## 知识关联

学习PBR纹理工作流需要先掌握**纹理绘制概述**中的贴图类型（Diffuse、Normal等）和UV展开基础，因为PBR的BaseColor和Roughness贴图同样依赖正确的UV坐标才能正确投影到模型表面。

掌握两种工作流的区别后，后续学习**Substance Painter**时会直接接触到其项目设置中的工作流选择界面（File → New → Document Settings中的Template选项），理解Metallic-Roughness与Specular-Glossiness模板的本质差异将帮助正确配置导出预设。进一步学习**BaseColor贴图**、**Roughness贴图**和**Metallic贴图**时，本文建立的物理数值范围认知（F0值、Metallic的0/1规则、Roughness的真实参考值）将直接指导贴图的绘制决策，避免产生物理上错误的材质。