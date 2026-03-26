---
id: "vfx-pp-stencil"
concept: "模板缓冲应用"
domain: "vfx"
subdomain: "post-process"
subdomain_name: "后处理特效"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 44.9
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


# 模板缓冲应用

## 概述

模板缓冲（Stencil Buffer）是GPU帧缓冲区中的一个8位整数通道，每像素可存储0到255之间的整数标记值。在后处理特效管线中，模板缓冲充当空间选择器——它允许开发者在不同渲染Pass之间传递像素归属信息，从而让后处理着色器只对特定像素区域生效，而非盲目处理全屏幕4K分辨率的所有像素。

该技术最早在光栅化管线确立初期就作为硬件功能存在，但真正被广泛用于后处理选择性遮罩是在延迟渲染（Deferred Rendering）普及之后。延迟管线的GBuffer天然会执行几何Pass，这一Pass正好可以同步写入模板值，零额外带宽成本地为后续后处理Pass划分像素类别，例如UE4/UE5就在其延迟管线中将模板缓冲的特定比特位保留给头发、皮肤、自发光对象等材质类型。

模板缓冲后处理之所以重要，在于它能以硬件Early-Z/Early-Stencil机制提前剔除不需要处理的像素，从而大幅降低昂贵后处理着色器（如景深、辉光、SSAO）的实际执行像素数。若一个场景中角色仅占屏幕面积的15%，使用模板剔除后景深Pass的片元着色器调用量可降低约85%。

---

## 核心原理

### 模板缓冲的写入阶段

模板值写入发生在几何Pass中，通过设置`StencilOp`和`StencilWriteMask`控制。最常见的做法是在材质的渲染状态中指定`StencilRef`（参考值），并将写入操作设置为`REPLACE`，使通过深度测试的像素将其`StencilRef`值直接覆写到模板缓冲对应位置。例如，为皮肤材质指定`StencilRef = 2`，为金属材质指定`StencilRef = 4`，为植被指定`StencilRef = 8`。若需同时标记多类材质，可利用位掩码——`StencilRef = 3`（二进制`00000011`）同时表示两种属性的叠加。

模板测试函数由三个参数定义：比较函数（如`EQUAL`、`NOTEQUAL`、`ALWAYS`）、参考值（StencilRef）、读取掩码（StencilReadMask）。判断公式为：

```
通过条件：(StencilBufferValue & StencilReadMask) [CompareFunc] (StencilRef & StencilReadMask)
```

当`CompareFunc = EQUAL`、`StencilRef = 2`、`StencilReadMask = 0xFF`时，只有缓冲中值恰好为2的像素才会通过测试，其他像素被硬件直接丢弃，连片元着色器都不会执行。

### 多层次模板区域划分

8位模板缓冲可以通过位域（Bit Field）技术同时编码多种分类信息。Unity HDRP采用的一种典型分配方案是：
- Bit 0–1：光照模型类别（标准/次表面散射/各向异性）
- Bit 2–3：接收阴影类型
- Bit 7：是否参与屏幕空间反射

在后处理Pass读取时，通过不同的`StencilReadMask`来过滤目标像素——例如`StencilReadMask = 0x03`只读低两位来区分光照模型，`StencilReadMask = 0x80`只检查最高位来判断是否执行SSR。这样一次几何Pass写入的信息可在多个后处理Pass中被分别利用，避免重复渲染几何体。

### Early-Stencil 硬件剔除机制

现代GPU（如NVIDIA Maxwell架构后的所有显卡）在光栅化阶段实现了Early-Stencil测试，与Early-Z测试协同工作。当后处理全屏三角形（Full-Screen Triangle）的绘制调用到达光栅器时，GPU会在执行片元着色器之前就查询模板缓冲并剔除不满足条件的像素。这意味着被剔除的像素不仅跳过着色器执行，还避免了纹理采样、带宽消耗和ALU运算。实测数据表明，在4K分辨率下对占屏幕20%面积的区域执行SSAO，使用模板剔除比全屏SSAO节省约78%的GPU时间（根据目标区域复杂度有所浮动）。

---

## 实际应用

**角色专属轮廓描边**：在几何Pass中为所有角色网格写入`StencilRef = 1`。描边后处理Pass启用模板测试`EQUAL 1`，只在角色像素上执行Sobel边缘检测并叠加描边颜色。背景与UI像素完全不参与计算，避免产生误描边。

**局部景深与聚焦区域保护**：将玩家角色用`StencilRef = 3`标记，景深模糊Pass使用`NOTEQUAL 3`使角色像素跳过模糊采样，实现"角色始终清晰、背景虚化"的效果，无需额外的alpha混合Pass。

**次表面散射局部后处理**：皮肤材质写入`StencilRef = 2`，后处理阶段在模板测试为`EQUAL 2`的条件下执行高斯横向+纵向两Pass的次表面散射卷积。该卷积核宽度通常为15–25像素，仅在皮肤区域执行可避免将次表面颜色渗漏到背景像素。

**UI与3D场景的精确隔离**：在某些HUD层叠方案中，模板缓冲被设置为标记所有3D场景像素为`StencilRef = 255`，UI全屏后处理（如护盾受击全屏扭曲）使用`NOTEQUAL 255`仅在无3D内容的HUD区域叠加特效，防止游戏画面被UI特效污染。

---

## 常见误区

**误区一：认为模板缓冲可以无代价地无限细分区域**
8位模板缓冲总共只有256个可用整数值，且多个Pass共用同一模板缓冲，各系统必须提前协商好位域分配。如果Unity HDRP已占用前4位、自定义特效系统又独立占用全8位，两套系统会互相覆写导致渲染错误。实际工程中需要一套全局的StencilBit注册表来管理位域分配，否则难以维护。

**误区二：模板测试与深度测试完全等价，可以互换使用**
深度缓冲存储的是浮点深度值，而模板缓冲存储的是整数标记，两者服务于完全不同的目的。深度测试解决的是可见性（哪个物体更近），模板测试解决的是分类（这个像素属于哪种类别）。用深度范围来模拟模板分类不仅精度差，还会在物体重叠时产生错误归类，且无法实现位域多重分类。

**误区三：在前向渲染中模板后处理与延迟渲染完全相同**
前向渲染没有独立的GBuffer Pass，模板值必须在每个物体的正常渲染Pass中写入，且如果场景中物体绘制顺序混乱（如透明物体插入不透明物体之间），模板值可能被后续绘制调用错误覆写。相比之下，延迟渲染的GBuffer Pass天然是所有不透明物体的统一写入阶段，模板值更加可控，这是两种渲染路径在模板后处理工程实现上的本质差异。

---

## 知识关联

**依赖前置：自定义后处理**
模板缓冲后处理需要开发者掌握自定义后处理Pass的创建方式——包括如何通过`RenderStateBlock`或材质的`Stencil{}`块指定测试条件，以及如何在`ScriptableRenderPass`的`Execute`函数中通过`CoreUtils.SetRenderTarget`正确传递模板附件。若不理解自定义后处理的Pass注入机制，则无法在正确的时间节点读取几何Pass写入的模板值。

**衔接后续：TAA与时域滤波**
TAA（时域抗锯齿）在处理模板划定的局部区域时面临一个特殊挑战：当模板边界像素在相机运动时发生亚像素偏移，时域重投影会将来自不同模板区域的历史帧颜色混合，导致局部后处理（如SSS、轮廓描边）在边缘产生"鬼影"（Ghosting）。解决方案通常是在TAA的历史帧混合阶段加入模板一致性检查——仅当当前帧与历史帧对应像素的模板值相同时才进行时域混合，否则降低历史帧权重或直接使用当前帧颜色。这一策略是TAA与模板后处理系统联合设计的核心问题之一。