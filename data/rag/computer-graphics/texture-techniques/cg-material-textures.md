---
id: "cg-material-textures"
concept: "材质纹理集"
domain: "computer-graphics"
subdomain: "texture-techniques"
subdomain_name: "纹理技术"
difficulty: 2
is_milestone: false
tags: ["实践"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 46.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# 材质纹理集

## 概述

材质纹理集（Material Texture Set）是PBR（基于物理的渲染，Physically Based Rendering）工作流中将描述同一表面物理属性的多张贴图打包为一个逻辑单元的组织方式。一套完整的材质纹理集通常包含五张核心贴图：漫反射颜色贴图（Albedo）、法线贴图（Normal Map）、粗糙度贴图（Roughness）、金属度贴图（Metallic）以及环境光遮蔽贴图（Ambient Occlusion，AO）。这五张贴图共同描述了一个表面在光照下的完整物理响应行为。

PBR材质纹理集的概念随着迪士尼（Disney）于2012年发布"Disney Principled BRDF"模型后开始在游戏和影视行业普及，Allegorithmic（现为Adobe Substance）的Substance Painter软件在2014年进一步将这套五贴图工作流标准化，使其成为实时渲染领域的行业标准。

在实际项目中，使用材质纹理集而非单张贴图的最大优势是工程可维护性：当需要修改砖墙材质的粗糙感时，只需更换Roughness贴图，不会影响颜色或法线数据，各通道职责分离使版本迭代效率提升明显。

---

## 核心原理

### Albedo贴图：纯色信息，剔除光照

Albedo贴图存储表面的固有颜色，与传统Diffuse贴图最关键的区别在于：**Albedo不应包含任何烘焙光影信息**。正确的Albedo贴图中，金属表面的sRGB亮度值范围应在0–70之间，非金属（绝缘体）表面的sRGB亮度值范围应在50–240之间。若Albedo中混入了AO或方向性阴影，PBR着色器会产生错误的光照叠加，在强光或暗光环境下材质会失真。

### Normal Map：切线空间法线编码

法线贴图将每个像素的表面法线方向编码为RGB颜色，其中R通道对应切线方向（X轴），G通道对应副切线方向（Y轴），B通道对应法线方向（Z轴）。标准OpenGL格式的法线贴图中，平坦表面的像素值为RGB(128, 128, 255)，对应归一化向量(0, 0, 1)。需要注意的是，DirectX格式与OpenGL格式在G通道上符号相反——DirectX格式需将G通道反转（G = 255 - G_opengl），两种格式混用是法线贴图出现"凹凸反转"问题最常见的原因。

### Roughness与Metallic：控制BRDF响应形状

粗糙度贴图（Roughness）是一张灰度图，0（黑色）代表完全光滑，1（白色）代表完全粗糙。金属度贴图（Metallic）同样是灰度图，通常应为纯黑（0，非金属）或纯白（1，金属），中间值仅用于描述金属表面氧化或污垢的过渡区域。这两张贴图共同驱动Cook-Torrance BRDF中的微表面分布函数（NDF）和菲涅耳项：高粗糙度会使高光扩散为大面积柔和光斑；高金属度会使镜面反射颜色染上Albedo的色调，同时漫反射分量趋近于零。

### AO贴图：静态遮蔽补偿

环境光遮蔽贴图存储的是表面上每个点对环境光的可见程度，0（黑色）表示被周围几何体完全遮挡，1（白色）表示完全暴露。AO贴图仅应应用于**间接光照（环境光）**乘法运算，公式为：`Final_Indirect = IndirectLight × AO`。若将AO乘以直接光照，则会产生物理上不正确的阴影，因为运行时光照已通过阴影贴图处理了直接遮蔽。

---

## 实际应用

**游戏资产制作流程示例：**
在Substance Painter中制作一个金属武器的材质纹理集时，美术师会在同一画布上分图层叠加以下信息：基础铁材质（Metallic=1, Roughness=0.3），边缘磨损层（仅在曲率高的区域降低Roughness至0.1，显示抛光金属），污垢层（在凹陷区域叠加棕色，同时将Metallic降至0，Roughness升至0.8），最终一键导出为五张2048×2048像素的PNG或EXR文件。

**引擎导入规范：**
在Unreal Engine 5中导入材质纹理集时，Albedo应设置为sRGB颜色空间，而Normal/Roughness/Metallic/AO这四张贴图必须设置为Linear颜色空间（取消勾选sRGB），否则引擎会对这些数据贴图应用错误的Gamma矫正（2.2次方），导致粗糙度计算偏差。

**纹理打包优化：**
为节省内存带宽，生产中常将Roughness、Metallic、AO三张灰度图合并打包进单张RGBA贴图的三个独立通道，这种贴图被称为"ORM贴图"（Occlusion-Roughness-Metallic）。这样原本需要读取3张贴图，现在只需采样1张，GPU纹理缓存命中率显著提升。

---

## 常见误区

**误区一：将旧式Diffuse贴图直接当作Albedo使用**
从非PBR工作流迁移时，许多人直接将含有烘焙光影的Diffuse贴图用作Albedo。这会导致光照方向被"双重叠加"——旧光影信息与实时渲染器计算的新光照同时存在，材质在换光环境时无法正确响应。正确做法是用Photoshop或Substance的"Remove Baked Lighting"滤镜提取纯净颜色数据。

**误区二：金属度贴图使用中间灰度值来表示"半金属"**
Metallic值0.5不代表"一半是金属"，在物理上不存在"半金属"状态。Metallic中间值的正确使用场景极为有限，仅限于描述同一纹素内金属与非金属材料之间像素级混合（例如生锈表面氧化层）时使用，而不是用来"柔化"金属外观。

**误区三：所有贴图必须使用相同分辨率**
材质纹理集中各贴图的分辨率可以不同。高频细节丰富的Normal Map通常使用2048×2048或4096×4096，而颜色变化平缓的AO贴图使用512×512完全足够，依据信息频率分配分辨率可以将贴图总内存占用降低30%–50%。

---

## 知识关联

**前置概念衔接：**
材质纹理集建立在纹理映射概述所介绍的UV坐标展开和纹理采样基础上——五张贴图共享同一套UV坐标，这意味着UV展开质量直接决定所有贴图的精度，UV岛屿拉伸会同时损害Albedo颜色均匀性和Normal Map的法线精度。

**后续概念准备：**
掌握五张贴图各自的物理含义后，才能进入纹理烘焙（Texture Baking）阶段的学习。烘焙的本质是将高多边形网格的几何细节（法线方向、遮蔽关系）"转录"为贴图数据——即为低多边形网格生成Normal Map和AO贴图的过程，这正是材质纹理集中Normal和AO两个通道数据的主要来源。