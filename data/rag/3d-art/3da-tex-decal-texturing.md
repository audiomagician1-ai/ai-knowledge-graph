---
id: "3da-tex-decal-texturing"
concept: "贴花纹理"
domain: "3d-art"
subdomain: "texturing"
subdomain_name: "纹理绘制"
difficulty: 2
is_milestone: false
tags: ["技巧"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---



# 贴花纹理

## 概述

贴花纹理（Decal Texture）是一种将独立图层的细节元素——如战术标志、弹孔、锈蚀斑痕、涂鸦字样——叠加到已有材质表面的纹理技术。与直接在基础材质上绘制不同，贴花采用独立的Alpha蒙版通道控制覆盖范围，使细节元素可以在不破坏底层材质的前提下自由摆放、缩放和旋转。

贴花技术最早广泛应用于20世纪90年代末的游戏引擎，彼时主要用于模拟弹孔和血迹，以避免为每一种受损状态单独制作一套完整纹理集。现代工作流中，Substance Painter的贴花功能在3.x版本后得到显著强化，支持将贴花作为独立的"Decal Layer"直接投射到模型表面，并可驱动Height、Roughness、Metallic等多个通道，而非仅仅覆盖颜色。

贴花纹理的核心价值在于资源复用和非破坏性编辑：同一个弹孔贴花可以在不同位置多次实例化，极大节省了纹理空间；同时，删除或修改某个贴花层不会影响底层的Base Color或Normal Map，满足了游戏资产后期迭代的高频需求。

## 核心原理

### Alpha蒙版与通道驱动

贴花文件通常是一张32位PNG或TGA图像，其中RGB通道存储颜色/法线/粗糙度信息，第四个Alpha通道定义贴花的形状边界。Alpha值为255（纯白）的区域完全覆盖底层纹理，Alpha值为0（纯黑）的区域完全透明，中间灰度值则产生半透明混合效果。在Substance Painter中，贴花层的混合模式默认为"Normal"，但切换为"Multiply"可以实现污渍类贴花的自然融合，颜色公式为：Output = Base × Decal_Color。

### 投射方式：三平面投射与UV投射

贴花在3D软件中主要有两种投射方式。**三平面投射（Triplanar Projection）**沿X、Y、Z三个世界轴分别投射纹理并混合，适合表面曲率较大或没有干净UV的模型，例如地形石块；混合权重基于各轴法线点积的幂次计算，幂次值越高，轴间过渡越硬。**UV投射**则将贴花直接映射到模型展开的UV空间，精度更高，适合武器或载具上需要精确对位的标志贴花。Substance Painter的"Projection"工具本质上是三平面投射的简化版，通过笔刷半径和旋转角度控制贴花落点。

### 法线混合：Reoriented Normal Mapping

当贴花包含独立的法线信息（如突出的铆钉或凹陷的划痕）时，不能直接叠加底层法线贴图，否则会产生错误的光照结果。正确做法是使用**重定向法线混合（RNM，Reoriented Normal Mapping）**，其公式为：

**n_result = normalize( n_base + n_detail × vec3(-1,-1,1) )**

即将底层法线的XY分量与贴花法线的XY分量相加后归一化，确保二者的切线空间方向正确叠加。Substance Painter在内部自动处理这一运算，但在导出到虚幻引擎或Unity手动混合时需要艺术家在材质蓝图中显式实现RNM节点。

### Roughness与Metallic通道的贴花覆盖

除颜色和法线外，贴花可以单独修改材质的Roughness（粗糙度）和Metallic（金属度）通道。例如，一个油漆喷涂贴花需要将Metallic设为0（非金属）、Roughness提高到0.85，覆盖底层金属底板的Metallic=1.0数值。在Substance Painter中，Decal Layer的每个通道可以独立启用或禁用，艺术家可以只勾选"Color"和"Roughness"，保持底层"Normal"通道不受影响。

## 实际应用

**军事载具涂装**：坦克或战斗机的机身编号、国籍标志通常作为贴花处理，而非烘焙进基础纹理。一架战斗机的机翼徽章贴花尺寸通常为512×512像素，Alpha边缘需要2~4像素的羽化过渡以避免锯齿，然后在游戏引擎中使用Decal Component叠加到已有材质表面，这样同一个机身模型可以通过替换贴花快速生成不同势力的变体版本。

**弹孔与受损状态**：第一人称射击游戏中，场景墙壁和地板的弹孔普遍采用实时贴花系统生成。典型的弹孔贴花资产包含三张512×512贴图：一张颜色贴图（黑色烧灼边缘）、一张法线贴图（中心凹陷、周围碎裂凸起）和一张Roughness贴图（焦痕区域粗糙度约0.9），合计贴图内存约为1MB，可以在运行时动态投射到任意几何体表面。

**道具污渍与磨损叠加**：在Substance Painter中为武器道具绘制使用痕迹时，将磨损贴花放置在专用的"Decal"层组内，可以与底层的"Metal_Base"层和"Paint_Layer"层保持完全独立，方便关卡美术在后期根据游戏叙事需要调整武器的新旧程度，而无需重新烘焙任何贴图。

## 常见误区

**误区一：将贴花直接合并进底层纹理**
部分初学者习惯在Substance Painter中将Decal Layer与下方层组"向下合并（Merge Down）"，导致贴花细节永久烘焙进基础纹理。一旦后续需要调整贴花位置或删除某个标志，就必须重新绘制底层被覆盖的区域。正确做法是在整个制作周期内保持贴花层的独立性，仅在最终导出时由软件自动合并输出。

**误区二：忽略贴花的LOD衰减**
在游戏引擎中使用实时贴花时，开发者常常忘记为贴花资产设置LOD距离衰减。弹孔贴花在距离摄像机超过15米时通常已不可见，但仍会占用绘制调用（Draw Call）。虚幻引擎的Decal Actor提供"Fade Screen Size"参数，建议将弹孔贴花的淡出值设置在0.01~0.02之间，防止场景内大量贴花导致性能下滑。

**误区三：贴花法线与底层法线直接混合**
如前文所述，将贴花Normal直接以"Add"模式叠加到底层Normal会破坏切线空间的单位向量长度，在掠射角光照下产生明显的异常高光。正确方法是使用RNM算法，或在贴花法线强度较低（Intensity < 0.3）时可近似使用"Overlay"混合模式作为快速替代方案，但需要艺术家自行验证在极端光照条件下的视觉效果。

## 知识关联

贴花纹理建立在**Substance Painter基础操作**之上：熟悉图层堆栈、混合模式和通道遮罩是使用贴花层的前提，特别是Alpha通道的导入与管理直接决定贴花边缘质量。此外，理解切线空间法线贴图的坐标系约定（OpenGL Y轴向上 vs DirectX Y轴向下）对于贴花法线在不同引擎间的正确迁移至关重要——Substance Painter默认导出DirectX格式，而Unity HDRP默认使用OpenGL格式，混用会导致贴花划痕的凹凸方向完全相反。

贴花纹理技术也与**程序化纹理生成**密切相关：在Substance Designer中可以制作参数化的贴花母版（如可控制弹孔数量和散布范围的弹痕生成器），输出后作为贴花素材库导入Substance Painter，形成完整的程序化损伤制作管线，大幅提升团队在同类型资产上的批量生产效率。