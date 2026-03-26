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
quality_tier: "B"
quality_score: 45.0
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


# 贴花纹理

## 概述

贴花纹理（Decal Texture）是一种在已有材质表面叠加额外视觉信息的技术手段，常用于添加军徽、弹孔、油漆涂鸦、污渍划痕等局部细节，而无需重新绘制整张底层材质。其核心逻辑是：底层材质保持独立，贴花作为独立图层投影到特定区域，通过透明通道（Alpha）控制边缘融合，两者互不干扰。

贴花技术最早在工业设计渲染和影视特效中被广泛使用，进入游戏工业后随着延迟渲染管线（Deferred Rendering）的普及而得到标准化支持。Unreal Engine 4在2014年正式将Deferred Decal作为内置渲染节点纳入主流工作流，Substance Painter则在3.x版本中加入了专门的Decal图层类型，允许艺术家在PBR纹理绘制阶段直接摆放和调整贴花。

贴花纹理的价值在于模块化复用：一张弹孔贴花可以贴到金属墙壁、木箱、混凝土上，各自与底层材质混合，产生视觉各异的效果，而贴花本身只需绘制一次。这种方式显著节省了纹理内存，并让关卡美术师能够在引擎中实时调整贴花的位置、旋转与缩放，而无需每次改动都回到Substance Painter重新烘焙。

## 核心原理

### Alpha通道与混合模式

贴花纹理必须携带Alpha通道，用于定义贴花形状的硬边或软边过渡。Alpha值为0表示完全透明（显示底层材质），值为1表示完全覆盖。在Substance Painter中，贴花图层的混合模式通常设置为"Normal"叠加，此时贴花的颜色、粗糙度（Roughness）和法线（Normal）会按Alpha权重与下方图层混合。如果只想让贴花影响法线而不改变颜色（例如凹陷弹孔），可以单独为Normal通道启用贴花图层，同时关闭Base Color通道。

### PBR各通道的独立控制

一张完整的贴花通常包含4~6张子贴图，分别对应：Base Color（颜色信息）、Normal（表面微结构）、Roughness（光泽变化）、Metallic（金属度变化）以及Height（高度置换，可选）。以弹孔贴花为例，其Normal贴图应呈现向内凹陷的法线数据，Roughness贴图中弹孔边缘应比周围表面更粗糙（数值接近0.8~0.9），而Base Color可以只携带少量碳痕变色，这样贴花在不同底色材质上都能保持真实感，不会显得突兀。

### 投影方式：盒体投影与屏幕空间投影

在Substance Painter中，贴花以UV投影方式贴附在模型表面，艺术家可以通过移动、旋转、缩放Decal节点来精确控制贴花的位置和大小，贴花自动适配模型的曲面UV。而在Unreal Engine中，Deferred Decal使用**盒体投影（Box Projection）**：一个代表贴花体积的Box Actor沿其局部Z轴向前投影，凡是落在Box体积内的几何体都会接受贴花，投影深度由Box的Z轴缩放控制。这两种投影方式产生的结果在UV边界处理上存在差异，Substance Painter的结果更精确，引擎投影更灵活但在模型边角处可能出现拉伸。

### 贴花的图层堆栈顺序

在Substance Painter中，贴花图层的顺序遵循"上层覆盖下层"的规则。若需要在锈蚀图层之上叠加一张"禁止通行"标志贴花，需将Decal图层置于锈蚀图层之上；如果希望贴花受到锈蚀磨损影响（标志也跟着生锈），则需将贴花放在锈蚀图层之下，让锈蚀层通过遮罩方式在整个材质上统一叠加。这个顺序逻辑与Photoshop图层相同，但影响的是PBR的所有通道，而不只是颜色。

## 实际应用

**军事载具涂装**：在坦克或战机模型中，国旗、序列号、战斗记录标记均作为独立贴花图层存在，底层材质为橄榄绿金属漆，贴花图层仅改变局部的Base Color和Roughness（漆面贴花比金属底漆更光滑，Roughness约0.3~0.4）。这样换涂装方案时只需替换贴花图层，底层金属材质无需改动。

**场景道具损伤**：游戏中的弹孔、刀痕贴花通常制作为512×512或1024×1024的方形贴图，Alpha通道使用柔边笔刷绘制以避免硬边穿帮。一张弹孔贴花在场景中可复用数十次，每次随机旋转15°~45°并缩放5%~15%，即可避免明显的重复感。

**街头涂鸦与文字**：场景艺术师在Substance Painter中将涂鸦贴花放置到砖墙材质的特定区域，通过调整贴花投影的Tiling为1×1（不重复）、Offset精确对齐砖缝，最终烘焙进一张完整的纹理集，送入引擎时作为静态材质使用，不占用额外的Draw Call。

## 常见误区

**误区一：贴花颜色过于饱和，忽视与底层材质的色调统一**
初学者常将标志类贴花的Base Color设置为纯色（如纯白R:255 G:255 B:255），贴到带有颜色变化的底层材质后显得格格不入，缺乏真实感。正确做法是将贴花颜色的饱和度降低，并在Value上稍微偏向底层材质的色调，同时在贴花边缘用柔边Alpha过渡，让颜色自然融合。

**误区二：只修改颜色通道，不修改Roughness和Normal**
仅改变Base Color的贴花在PBR光照下依然看起来是"贴纸感"——因为贴花区域与周围表面的反光特性完全相同。真实的油漆标志比周围金属更光滑，弹孔边缘有金属翻卷的法线变化，这些信息必须通过同步修改Roughness和Normal贴花通道才能还原。

**误区三：混淆Substance Painter中的Decal图层与引擎中的Deferred Decal**
Substance Painter中的贴花操作最终会被烘焙进UV纹理集，成为静态数据；而Unreal引擎的Deferred Decal是运行时投影，修改位置无需重新烘焙。两者的使用场景不同：Substance Painter贴花适合固定位置的固有细节（如车身序列号），引擎贴花适合动态生成的损伤效果（如玩家射击产生的弹孔）。混淆两者会导致工作流程重复或遗漏内容。

## 知识关联

贴花纹理建立在Substance Painter图层系统的操作能力之上：掌握图层遮罩（Mask）和填充图层（Fill Layer）的使用后，才能理解Decal图层为何能在不影响底层材质的前提下叠加信息。贴花的Alpha绘制技能与普通遮罩绘制相通，但需要额外关注贴花边缘的柔化程度对最终融合效果的影响。

在学习完贴花纹理后，艺术家可以进一步研究Unreal Engine的Deferred Decal材质节点，了解如何在引擎中通过Material Domain设置为"Deferred Decal"、Blend Mode设置为"Translucent"来实现运行时贴花；也可以探索Substance Painter的Smart Material与贴花的结合使用——将贴花嵌入Smart Material预设中，实现一键在多个模型上应用带有统一损伤细节的完整材质方案。