---
id: "3da-bake-best-practices"
concept: "烘焙最佳实践"
domain: "3d-art"
subdomain: "baking"
subdomain_name: "烘焙"
difficulty: 3
is_milestone: true
tags: ["规范"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 46.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.414
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# 烘焙最佳实践

## 概述

烘焙最佳实践是3D美术领域中，将高模细节转移至低模贴图时所遵循的一套系统化工业流程规范。这套规范并非凭空而来，而是游戏和影视行业历经多年项目踩坑与工具迭代后积累的经验总结——尤其在2010年代PBR（Physically Based Rendering）工作流普及之后，行业对烘焙质量的要求大幅提升，这套实践也随之系统化成型。

这套流程的核心价值在于：规避法线贴图的接缝错误、减少AO（Ambient Occlusion）溢色污染、提高UV空间利用率，并确保贴图在不同渲染器间的可移植性。以Marmoset Toolbag 4和Substance Painter 9.x为代表的现代烘焙工具，已将许多最佳实践内化为默认工作流，但理解其背后的原理仍是避免失误的根本。

对于难度3/9的学习阶段，掌握烘焙最佳实践意味着能够系统地消除此前学习中遇到的各类瑕疵，并为进入Substance Painter进行贴图绘制打下干净的贴图底层。

---

## 核心原理

### 1. 硬边与UV接缝的强制对齐原则

法线贴图烘焙中最常见的接缝错误，根源在于低模的硬边位置与UV切缝位置不对齐。正确做法是：**低模上每一条硬边（Hard Edge）必须在UV展开时对应一条切缝（UV Seam）**，反之亦然——每条UV切缝也必须对应硬边。这条"硬边=UV切缝"规则在Maya、Blender、3ds Max等主流软件中均适用，违反此规则将导致切线空间（Tangent Space）法线贴图在硬边处产生黑色错误条纹。

具体操作时，可以在Maya中使用"Harden/Soften Edge"配合UV展开工具，先切边再展UV；Blender中则使用Edge Split修改器或手动标记Sharp Edge后展开。软边区域不需要切缝，但必须确保该区域UV岛内的法线过渡是连续的。

### 2. 高低模配对与Cage的精确控制

烘焙时高模与低模之间的投影距离（Ray Distance / Cage Distance）设置直接决定细节捕获的准确性。Marmoset Toolbag中推荐使用"Bake Groups"功能，将场景中不同部件分组烘焙，每组单独设置Max Frontal Distance和Max Rear Distance，避免相邻部件之间的法线信息互相污染——这种污染在距离小于模型总尺寸1%时极易发生。

Cage法烘焙（Cage Baking）相比简单的Ray Distance法具有更强的控制力：通过为低模创建一个略微膨胀的Cage网格，射线从Cage向内投射，彻底解决凹陷区域射线打空的问题。在ZBrush中导出高模前，建议以低模面数的4到8倍作为高模减面后的输出面数，保留足够的曲面细节同时控制烘焙计算量。

### 3. UV布局的密度均匀与填充率优化

UV空间利用率（UV Density Utilization）直接影响烘焙贴图的有效分辨率。行业标准要求同一套贴图集（Texel Density）内所有UV岛的每单位面积像素密度差异不超过10%，否则贴图在不同区域的清晰度差异将在烘焙结果中被放大。

实操时，使用Texel Density Checker插件（Maya/Blender均有免费版本）可快速检测UV岛密度一致性。对于2048×2048分辨率的贴图，行业常用10.24像素/厘米（约等于26像素/英寸）作为游戏角色的标准Texel Density参考值，高频细节区域（如手部、面部）可在独立贴图集中设置2倍密度。UV岛之间至少保留4像素的间距（Padding），以防止在贴图压缩（如BC1/DXT1格式）后产生岛边漏色（Bleeding）。

### 4. 烘焙顺序与贴图通道规范

多通道烘焙时，执行顺序应严格遵循：**法线贴图 → AO → Curvature → Thickness → Position**。法线贴图必须最先烘焙，因为Substance Painter和其他工具的智能遮罩（Smart Mask）依赖法线数据生成AO和曲率；若AO先烘焙，则无法利用法线增强细节层次。

DirectX（DX）与OpenGL（GL）法线贴图格式在绿通道（Y轴方向）上是相反的，DX格式绿通道向下，GL格式绿通道向上。Unreal Engine 5默认使用DX法线，Unity默认使用GL法线。在Marmoset或Substance Painter中导出时，必须根据目标引擎勾选对应选项，否则所有曲面的凹凸方向将全部反转。

---

## 实际应用

**游戏角色武器烘焙案例**：制作一把硬表面枪械时，首先将枪管、枪身、握把、弹匣划分为4个独立Bake Group；枪管因为有明显硬边造型，需要在低模上对所有折角边执行Harden Edge操作并同步切UV缝；弹匣与枪身重叠部分设置独立Cage，将Max Rear Distance设为0.03（单位为模型最大边长的3%），防止弹匣法线投影到枪身上产生错误阴影。最终4张2048贴图集的UV填充率应达到75%以上，低于65%则需要重新合并UV岛或降低贴图分辨率节约内存。

**建筑场景模块烘焙**：对于可平铺（Tileable）的建筑模块，AO贴图应关闭"Self-Occlusion Only"选项，改为开启"Multi-Mesh AO"，确保模块拼接后接缝处的阴影关系与实际场景遮挡一致，而非仅基于单个模块自身几何体计算。

---

## 常见误区

**误区一：认为平滑组（Smoothing Groups）可以替代硬边/UV切缝的对应操作**
平滑组在3ds Max中是软件层面的法线平均标记，导出FBX至其他软件后其行为取决于导出设置。若不显式设置硬边并切缝，仅依赖平滑组，在Marmoset或Substance Painter中重新计算切线空间时，原有的平滑组信息可能被忽略，导致接缝错误复现。正确做法是始终在模型阶段完成硬边与UV切缝的对应关系，而非依赖下游软件的插值行为。

**误区二：认为烘焙分辨率越高越好，总是选择4096×4096**
4096分辨率并非总是最优选择：对于UV填充率低于50%的贴图集，使用4096的实际有效像素密度与使用2048高填充率贴图集接近，却消耗4倍内存（4096×4096 RGBA = 64MB未压缩）。行业惯例是先优化UV布局使填充率超过70%，再决定分辨率，而非直接用高分辨率掩盖UV利用率不足的问题。

**误区三：烘焙完成后不检查切线空间一致性便直接进入Substance Painter**
法线贴图在Substance Painter中默认以MikkTSpace切线空间算法显示，若烘焙时使用的是其他切线空间算法（如3ds Max的Per-Vertex切线），则在Substance Painter视口中法线贴图会出现光影错误，但这并非烘焙失败，而是切线空间不匹配。解决方法是在Marmoset或Substance Painter中统一选择MikkTSpace算法烘焙和显示，这也是当前行业最广泛支持的切线空间标准。

---

## 知识关联

**与烘焙瑕疵的关系**：烘焙瑕疵（法线接缝、AO漏光、Cage穿插等）是具体的错误现象，而本文所述的最佳实践是系统消除这些现象的预防性方案。掌握瑕疵的成因（如切线空间不匹配导致接缝）后，最佳实践中的"硬边=UV切缝"规则便有了直接的问题对应关系，而非抽象的操作步骤。

**通向Substance Painter的准备**：进入Substance Painter后，软件将直接消费此处烘焙的法线、AO、Curvature贴图作为智能遮罩的数据源。法线贴图的DX/GL格式设置错误、Curvature贴图的高频噪点、AO的溢色，都会在Substance Painter的Generator层中被放大表现为不自然的磨损效果或错误的遮罩边界。因此烘焙阶段输出的贴图质量直接决定了Substance Painter中材质绘制的起点质量。