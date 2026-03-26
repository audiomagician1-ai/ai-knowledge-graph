---
id: "3da-tex-opacity-mask"
concept: "透明度与遮罩"
domain: "3d-art"
subdomain: "texturing"
subdomain_name: "纹理绘制"
difficulty: 2
is_milestone: false
tags: ["技巧"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.5
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


# 透明度与遮罩

## 概述

透明度与遮罩是通过单独的灰度贴图（Opacity Map或Mask Map）来控制模型表面哪些像素可见、哪些像素完全透明的纹理技术。与BaseColor贴图记录颜色信息不同，Opacity/Mask贴图只存储0到255的灰度值，其中纯白（255）表示完全不透明，纯黑（0）表示完全透明，中间值则产生半透明效果（在Masked模式下中间值通常无意义）。

这种技术最早在2D精灵图时代就已普遍使用，进入3D渲染时代后被迁移用于解决树叶、铁丝网、头发等复杂轮廓物体"用简单几何体承载复杂形状"的核心需求。Unreal Engine和Unity等引擎分别将其实现为`Opacity`与`Opacity Mask`两个独立的材质输入槽，对应两种完全不同的渲染路径。

在游戏和影视制作中，一棵树的叶片如果全部用精确几何体建模，多边形数量会达到数十万甚至上百万，但借助Mask贴图，只需用几张矩形面片叠加，多边形数量可压缩到数百，同时视觉上完整还原叶片的锯齿轮廓，这使该技术成为植被、毛发系统不可替代的性能优化手段。

---

## 核心原理

### Masked模式与Opacity模式的本质区别

**Masked（不透明遮罩）模式**采用硬切断方式：引擎根据一个阈值（Clip Value，Unreal中默认为0.3333，即约85/255）判定每个像素是否渲染，低于阈值的像素直接丢弃（Discard），不写入深度缓冲，不产生半透明混合开销。树叶、栅栏铁丝、镂空花纹通常使用此模式，因为它支持正常的深度排序，且渲染成本仅略高于完全不透明材质。

**Opacity（半透明）模式**则将灰度值线性映射为Alpha混合系数，使用公式 `Final Color = Source Color × Alpha + Destination Color × (1 - Alpha)` 进行逐像素混合。烟雾、玻璃、皮肤散射常用此模式，但其代价是绕过深度写入，必须按"从后往前"顺序渲染（Painter's Algorithm），容易出现排序错误伪影，且GPU带宽消耗远高于Masked模式。

### 贴图通道的打包策略

Opacity/Mask信息是单通道数据（只需灰度），直接单独保存为一张贴图会浪费大量存储空间。工业标准做法是将Mask数据打包进其他贴图的Alpha通道（RGBA中的A通道），例如：

- BaseColor贴图的**A通道**存储Opacity Mask（Photoshop中新建通道后导出为TGA-32bit）
- 在Unreal中通过`Texture Sample`节点单独引出A通道连接至`Opacity Mask`输入槽

这种打包方式使一张512×512的TGA-32bit贴图同时承载颜色与遮罩信息，内存占用比两张单独贴图降低约40%。

### 树叶贴图的具体制作流程

以树叶为例，Mask贴图的制作分三步：第一步在Photoshop中将叶片照片抠图，得到透明背景的PNG；第二步将叶片图层的透明度信息（即内置Alpha）通过`Image > Apply Image`命令烘焙到独立的Alpha通道，并将该通道强化为纯黑白（Levels调整，使叶片边缘无灰色过渡）；第三步导出为TGA-32bit格式，送入引擎。叶脉等细节保留在BaseColor通道，轮廓信息保存在Alpha通道，两者共用同一UV空间，一张贴图完成全部工作。

头发Card（发片）技术同理：每张发片是矩形面片，Mask贴图将矩形中非发丝区域全部设为黑色（透明），发丝区域设为白色，从而用少量矩形面片叠加出蓬松发型的视觉效果。

---

## 实际应用

**铁丝网/栅栏**：在平面多边形上贴铁丝网纹理，Mask贴图中铁丝部分为白色，空隙部分为纯黑，启用Masked材质后空隙完全透空，玩家或光线可以穿透，而几何体本身只有4个顶点的矩形面片。Unreal中调整`Opacity Mask Clip Value`可以控制铁丝的粗细表现，将该值从0.1提高到0.5时铁丝显著变细（边缘被裁切更多）。

**树叶LOD（细节层次）**：距离相机较远时，引擎切换到低精度LOD，此时每个树冠LOD级别通常用6到8张面片组成，完全依赖Mask贴图维持叶片轮廓可信度。LOD0（最近距离）可能使用上千个面片，而LOD3（50米外）仅用8个面片，但因为Mask贴图不变，树形轮廓在视觉上仍然成立。

**半透明玻璃脏污**：窗玻璃材质通常将玻璃整体Opacity设为0.15（接近透明），污渍区域Opacity提升至0.6，通过一张Opacity贴图的灰度变化同时表达玻璃厚薄感和污渍分布，而无需建模玻璃厚度。

---

## 常见误区

**误区一：用Opacity模式替代Masked模式做树叶**。树叶使用Opacity（半透明）模式时，引擎无法为其写入深度，导致大量树叶之间排序混乱，出现近处叶片被远处叶片"吃掉"的穿帮现象，且大量半透明绘制调用（Translucent Draw Call）会严重拖慢帧率。正确做法是树叶始终使用Masked模式，Opacity模式仅用于真正需要渐变透明的对象。

**误区二：Mask贴图需要反锯齿过渡，边缘应保留灰色像素**。在Masked模式下，硬边锯齿是正确且期望的结果——Clip Value会将所有灰色像素直接归为透明或不透明，中间值在渲染结果中不存在。如果在Mask贴图边缘保留羽化或灰度过渡，不仅不会产生平滑效果，反而会因为不同设备、不同Clip Value设置下灰色像素被随机判定，导致叶片轮廓宽窄不一致。对于需要软边缘的情况，应切换为Opacity模式并接受其半透明渲染代价。

**误区三：Mask贴图与BaseColor贴图的分辨率必须一致**。实际上Mask数据往往只需要较低精度即可，在打包进BaseColor的A通道时自然继承相同分辨率，但如果Mask单独存储，可以使用低一档的分辨率（如BaseColor为2048×2048，Mask可用512×512），引擎会自动在UV采样时插值，视觉差异通常无法察觉，但内存节省显著。

---

## 知识关联

**前置概念——BaseColor贴图**：Opacity/Mask贴图几乎总是与BaseColor贴图共用同一套UV坐标，并且在实际工程中直接打包进BaseColor的A通道。理解BaseColor的UV布局方式（如0-1 UV空间中如何排列多张叶片）是高效组织Mask贴图的前提，例如一张2048的Texture Atlas中可以排列16种不同形状的叶片，每种叶片在Atlas中的矩形区域同时包含颜色和遮罩信息。

**延伸到材质混合模式**：掌握Opacity/Mask贴图之后，下一步学习方向是理解引擎材质系统中`Blend Mode`枚举（Opaque、Masked、Translucent、Additive）的完整体系，以及`Two Sided`（双面渲染）属性如何配合Masked材质解决树叶背面剔除问题——叶片面片在开启双面渲染后，从任意角度观察都能通过Mask显示叶片轮廓，而不会出现"看透面片背面"的穿帮。