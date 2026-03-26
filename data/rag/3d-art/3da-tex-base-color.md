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
quality_tier: "B"
quality_score: 46.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.452
last_scored: "2026-03-22"
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

BaseColor贴图（基础颜色贴图）是PBR（基于物理的渲染）工作流中定义物体固有色的纹理通道，它存储的是材质在完全均匀白光照射下、去除所有光照影响后的纯粹颜色信息。BaseColor贴图使用sRGB色彩空间编码，在引擎中会自动转换为线性空间参与光照计算，这一特性决定了它的制作标准与传统Diffuse贴图截然不同。

BaseColor这一概念随着迪士尼2012年发布的《Physically-Based Shading at Disney》论文及随后各大引擎普及PBR工作流而正式确立。在此之前的Diffuse贴图允许包含明暗烘焙信息，但这种做法在PBR体系下会导致重复计算光照、破坏物理一致性。BaseColor的出现将固有色与光照信息彻底分离，使同一张贴图能在任意光照环境下呈现正确结果。

BaseColor贴图之所以重要，在于它是PBR着色器中乘以光照结果的起点数据。如果BaseColor中混入了AO（环境光遮蔽）或高光烘焙，引擎的实时GI和光照系统就会在其基础上再次叠加同类信息，导致物体在强光下过暗、在暗部区域颜色失真的双重错误。

---

## 核心原理

### 无光照信息原则

BaseColor贴图中绝对不能包含以下任何信息：方向光明暗过渡、环境光遮蔽烘焙阴影、高光热点（Specular Hotspot）、接触阴影（Contact Shadow）。这些信息必须由引擎的PBR光照模型或独立的AO贴图通道负责。判断BaseColor是否"干净"的实用方法是：将贴图导入引擎后，在一个完全均匀的球形光照环境（称为Matcap球或灰色天空盒）下预览，物体表面应只呈现颜色差异，不应出现任何与模型法线或几何体无关的明暗变化。

### 色彩范围限制

BaseColor并非可以使用任意颜色。根据Allegorithmic（现Substance官方团队）发布的PBR指南，非金属（Dielectric）材质的BaseColor亮度值（线性空间）应控制在**0.04（约10 sRGB）到0.9（约235 sRGB）**之间。低于0.04意味着该材质在物理上会吸收几乎所有可见光，现实中极少存在；高于0.9（约235 sRGB）则意味着接近纯白，同样超出真实材质范围。对于金属（Metallic）材质，BaseColor存储的是金属的反射率（F0值），其亮度通常集中在**0.5到1.0（线性空间）**即约180~255 sRGB之间，且金属BaseColor往往带有明显色相，如金（Au）约为(255, 200, 80)、铜（Cu）约为(255, 175, 120)。

### 色彩空间与通道位深

BaseColor贴图必须以**sRGB模式**导出和导入，而非线性RGB。如果将BaseColor误设置为线性空间导入，引擎会跳过Gamma矫正，导致实际渲染颜色比设计颜色更暗（人眼感知的Gamma约为2.2，线性导入会使颜色显得约暗2.2倍）。位深方面，大多数情况下BaseColor使用**8位/通道（24位RGB）**即已足够，但对于需要精细颜色渐变的皮肤或天空等材质，可选用**16位/通道**格式以避免色带（Banding）。BaseColor贴图通常不需要Alpha通道，如需透明度则独立使用Opacity/Mask贴图处理。

### 材质类别对BaseColor的影响

金属度工作流（Metallic-Roughness Workflow，UE5、Unity默认采用）中，BaseColor的含义随Metallic贴图的值而改变：当Metallic=0时，BaseColor代表漫反射颜色；当Metallic=1时，BaseColor代表镜面反射颜色（F0）。这意味着同一块铁锈金属表面，锈迹区域（非金属）的BaseColor应是偏红褐色的较暗色值，而露出的金属光泽区域的BaseColor则应是铁的物理F0颜色（约(180, 180, 180)的中高亮度灰色）。

---

## 实际应用

**人物皮肤BaseColor制作**：皮肤属于次表面散射材质，其BaseColor应只包含皮肤固有色调（如东亚人皮肤偏(210, 170, 140)左右的sRGB值），绝不能在BaseColor中烘焙面部的光影轮廓或眼眶阴影。皮肤的血管次表面颜色变化（耳朵透光的红色、嘴唇的深粉色）是固有色差异，可以在BaseColor中体现，但这些颜色本身不应带有任何方向性明暗渐变。

**地面材质的BaseColor处理**：石砖地面的颜色变化（每块砖之间的色调微差、整体的颜色噪波）属于固有色，可以在BaseColor中表现。但砖缝处因几何凹陷产生的接触阴影不可以出现在BaseColor中——砖缝的暗部信息应该由法线贴图驱动引擎实时计算，或存储在单独的AO贴图通道里。

**Substance Painter中的BaseColor输出设置**：在Substance Painter导出时，BaseColor通道对应输出预设中的`$mesh_BaseColor`，导出格式应选择**sRGB**，不勾选Linear选项。如果项目使用Specular-Glossiness工作流（如部分HDRP项目），此通道对应的是Diffuse/Albedo而非BaseColor，其色彩范围规则略有差异（非金属F0已被统一固定为0.04，不通过贴图控制）。

---

## 常见误区

**误区一：BaseColor就是以前的Diffuse贴图**
许多从非PBR流程转型的美术会将旧项目的Diffuse贴图直接复用为BaseColor，但Diffuse贴图往往包含了大量手工绘制的光影信息（如Phong模型时代烘焙进去的高光和AO）。将这类Diffuse直接用作BaseColor会导致PBR渲染结果出现"双重AO"和"假高光"。正确做法是将Diffuse贴图的明暗信息提取出来单独存储，再将色调均匀化后才能用作BaseColor。

**误区二：BaseColor越鲜艳、对比越强越好**
部分初学者认为BaseColor应该尽量色彩丰富，饱和度推到最高才显得精细。但根据上文提到的物理亮度范围，极高饱和度的颜色（如纯红R=255, G=0, B=0的sRGB值）会超出真实材质的物理反射范围，在HDR光照环境下导致材质"发光"一样过曝。真实材质的固有色饱和度在多数情况下相当克制，树叶的绿色约为(80, 120, 60)而非(0, 255, 0)。

**误区三：金属材质的BaseColor应该是黑色或白色**
金属WorkFlow初学者常误以为金属的漫反射为零所以BaseColor应填充黑色（0,0,0）。实际上金属的BaseColor存储的是该金属的镜面反射颜色，黄金的BaseColor是金黄色、铜的BaseColor是橙铜色，用黑色填充会使金属在PBR光照下呈现完全无反射的"黑洞"效果。

---

## 知识关联

学习BaseColor贴图需要先掌握**PBR纹理工作流**中Metallic-Roughness通道的分工逻辑，因为BaseColor的含义本身随Metallic值变化而改变，脱离Metallic通道讨论BaseColor容易产生歧义。同时需要理解sRGB与线性色彩空间的Gamma差异（Gamma 2.2），这直接影响BaseColor的导入设置和色值判断。

掌握BaseColor之后，**自发光贴图（Emissive Map）**是自然的延伸：自发光贴图同样存储颜色信息，但它不受PBR光照乘算影响，直接叠加到最终输出颜色上，其色值范围可以超出0-1（使用HDR值驱动Bloom效果），这与BaseColor必须限制在物理范围内的规则形成鲜明对比。另一个后续概念**透明度与遮罩贴图**则将介绍如何利用Alpha通道配合BaseColor实现镂空和半透明效果，两者在材质球设置层面紧密配合。