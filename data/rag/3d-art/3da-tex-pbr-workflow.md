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

PBR（Physically Based Rendering，基于物理的渲染）纹理工作流是一套基于真实世界光照物理规律的贴图制作规范，由迪士尼动画工作室于2012年在SIGGRAPH发表的论文《Physically-Based Shading at Disney》中正式提出并推广。该工作流的核心思想是：材质对光线的响应必须遵守能量守恒定律，即物体反射出的光能总量不能超过接收到的光能总量。

PBR工作流目前存在两大主流分支：**Metallic-Roughness（金属度-粗糙度）**工作流和**Specular-Glossiness（高光-光泽度）**工作流。前者由Allegorithmic（现为Adobe旗下）在Substance系列工具中主推，后者则源自Quixel Suite等工具的传统体系。两者在数学上可以相互转换，但贴图通道的组织方式完全不同，选错工作流会导致材质在引擎中出现明显的物理错误。

对3D美术工作者而言，理解这两种工作流的区别至关重要，因为虚幻引擎（Unreal Engine）默认使用Metallic-Roughness，而许多老项目和部分欧洲工作室的流水线仍沿用Specular-Glossiness，贴图交付前必须明确甲方的引擎需求。

---

## 核心原理

### Metallic-Roughness工作流的贴图结构

该工作流由三张核心贴图构成：**BaseColor（基础色）**、**Metallic（金属度）**和**Roughness（粗糙度）**。

- **BaseColor**：存储材质的固有色。对于非金属，BaseColor代表漫反射颜色，sRGB值通常限制在30-240之间（对应线性空间0.02-0.9），不能出现纯黑或纯白。对于金属材质，BaseColor存储的是金属的F0反射率颜色（即镜面反射颜色），铝的BaseColor约为（0.913, 0.921, 0.925）。
- **Metallic**：纯灰度贴图，0表示绝缘体，1表示导体（金属），中间值仅用于过渡区域（如生锈金属边缘），不建议大面积使用中间灰值。
- **Roughness**：纯灰度贴图，0代表完美镜面，1代表完全漫反射散射。Roughness在着色器中通常被平方后用于计算GGX微表面分布，因此视觉感受与线性值并不对应。

### Specular-Glossiness工作流的贴图结构

该工作流同样由三张核心贴图构成：**Diffuse（漫反射色）**、**Specular（高光色）**和**Glossiness（光泽度）**。

- **Diffuse**：仅存储非金属的漫反射颜色。对于金属区域，Diffuse必须填充为纯黑（0,0,0），因为导体没有漫反射分量，这是与Metallic-Roughness工作流最显著的操作差异。
- **Specular**：RGB贴图，直接存储F0（零角度菲涅耳反射率）。非金属的Specular值通常为4%（线性值0.04），对应sRGB约（60,60,60）；金属的Specular值则存储其实际反射颜色，如黄金约为（1.0, 0.766, 0.336）。
- **Glossiness**：与Roughness的关系为 `Glossiness = 1 - Roughness`，数值含义相反，255表示完全光滑。

### 两种工作流的等价转换公式

将Specular-Glossiness转换为Metallic-Roughness时，关键步骤如下：

1. 判断Specular值是否高于阈值0.04（线性）：若是，则该像素判定为金属，Metallic=1，BaseColor=Specular值；
2. 若Specular接近0.04，则判定为非金属，Metallic=0，BaseColor=Diffuse值；
3. `Roughness = 1 - Glossiness`（逐像素计算）。

反向转换同理，但精度会有损失，因此不建议频繁互转。

---

## 实际应用

**虚幻引擎5的材质节点接入**：UE5的M_Standard材质球直接暴露BaseColor、Metallic、Roughness三个输入槽，对应Metallic-Roughness工作流。若使用Specular-Glossiness的贴图资产直接接入，Specular贴图的RGB值会被引擎误读为高光强度（单通道），导致金属材质出现灰色高光而非彩色金属光泽，这是项目中最常见的贴图接错问题。

**Substance Painter的工作流设置**：新建工程时，Document Settings中的"Normal Map Format"和贴图模板（Template）必须与目标引擎一致。选择"PBR - Metallic Roughness"模板时，输出预设会自动打包贴图：Roughness、AO、Metallic三张灰度图会合并为一张RGB贴图（ORM贴图），其中R=Occlusion、G=Roughness、B=Metallic，以节省显存采样次数。

**游戏资产的数值规范**：根据Epic Games发布的PBR材质校准标准，非金属材质的BaseColor线性反射率应在2%至80%之间。木材约9%，混凝土约30%，新鲜雪地约80%。一旦超出这个范围，材质在IBL（基于图像的光照）环境下会显得不真实。

---

## 常见误区

**误区一：认为Metallic贴图可以使用大量中间灰值**

初学者常将Metallic贴图制作成渐变灰，以为可以表达"半金属"效果。实际上，现实世界中不存在物理上的"半导体"材质，Metallic值的中间灰只适合用于金属与非金属的边界过渡（宽度通常1-3像素），大面积使用中间灰会导致能量守恒计算错误，在PBR验证工具（如Marmoset Toolbag的PBR Validator）中会报告警告。

**误区二：混淆Specular-Glossiness中Diffuse和BaseColor的概念**

许多从传统Blinn-Phong流程转过来的美术会把Diffuse贴图与BaseColor等同对待，直接将Diffuse贴图接入BaseColor槽。但在Specular-Glossiness工作流中，金属区域的Diffuse必须为纯黑，如果将含有金属色信息的Diffuse直接当做BaseColor使用，则金属区域会同时产生漫反射和镜面反射，严重违背能量守恒，导致金属看起来像涂了颜色的塑料。

**误区三：Roughness和Glossiness只是数值相反，可以直接互换通道**

虽然 `Roughness = 1 - Glossiness` 在数学上成立，但如果只是将贴图通道接反而不做颜色反转（Invert）处理，引擎采样到的值与预期完全相反：原本粗糙的木材会变成镜面，光滑的金属会变成磨砂表面。这类错误肉眼极易识别，但在大型项目的LOD链中偶尔会因为脚本错误批量发生。

---

## 知识关联

学习PBR纹理工作流需要先掌握基础的**纹理绘制概述**知识，包括UV展开、贴图分辨率与mipmap的关系，以及sRGB与线性色彩空间的区别——BaseColor贴图存储在sRGB空间，而Metallic和Roughness必须存储在线性空间，引擎导入设置中对应"sRGB"复选框的勾选状态至关重要。

掌握两种工作流的区别后，可以直接进入**Substance Painter**的学习，该工具以图层和智能材质为核心，所有操作都基于Metallic-Roughness体系构建。同时，**BaseColor贴图**、**Roughness贴图**和**Metallic贴图**作为独立知识点，会进一步深入讲解各通道的具体绘制技巧、数值范围校验方法，以及如何使用Photoshop的颜色检查器进行PBR合规验证。