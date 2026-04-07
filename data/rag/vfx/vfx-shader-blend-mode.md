---
id: "vfx-shader-blend-mode"
concept: "混合模式"
domain: "vfx"
subdomain: "shader-vfx"
subdomain_name: "Shader特效"
difficulty: 2
is_milestone: false
tags: ["基础"]

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


# 混合模式

## 概述

混合模式（Blend Mode）是Shader特效中控制像素如何与已有帧缓冲内容进行叠加计算的机制。其核心公式为：**最终颜色 = 源颜色 × 源因子 + 目标颜色 × 目标因子**，其中"源"指当前绘制的像素，"目标"指帧缓冲中已存在的颜色。不同混合模式的本质差异，就在于选取不同的源因子（SrcFactor）和目标因子（DstFactor）组合。

混合模式的概念随着GPU可编程管线的普及而标准化，OpenGL在1.1版本（1997年）便引入了`glBlendFunc`接口，DirectX则通过`D3DBLEND`枚举提供对应功能。在Unity的ShaderLab语法中，通过`Blend SrcFactor DstFactor`一行指令即可完成配置。对于特效Shader而言，混合模式直接决定粒子、光晕、火焰等视觉元素如何与背景融合，是影响特效最终观感的最直接参数之一。

正确选择混合模式不仅影响视觉效果，还与渲染性能密切相关。错误的混合模式会导致颜色错误、边缘出现黑边或白边，甚至引发不必要的Overdraw开销，因此在特效制作流程中需要早期确定混合策略。

## 核心原理

### Additive（叠加混合）

Additive混合的因子组合为 **SrcFactor = One，DstFactor = One**，公式简化为：最终颜色 = 源颜色 + 目标颜色。这种模式下，特效像素的RGB值直接累加到背景上，颜色只会越叠越亮，永远不会变暗。因此它天然适合表现自发光效果：火焰、闪电、激光、魔法光效等在叠加时会让背景"发光"。

Additive模式有一个重要特性：纯黑色像素（RGB均为0）在叠加时对背景毫无影响，等同于完全透明。这意味着使用Additive特效时，贴图的黑色区域不需要额外的Alpha通道来实现透明，节省了纹理采样指令。但代价是无法表现"遮挡"关系——Additive粒子永远不能遮盖背景。

### Alpha混合（传统透明）

Alpha混合的标准因子为 **SrcFactor = SrcAlpha，DstFactor = OneMinusSrcAlpha**，公式为：最终颜色 = 源颜色 × α + 目标颜色 × (1 - α)。这是最常用的透明混合方式，烟雾、云朵、半透明玻璃通常采用此模式。

Alpha混合需要配合**正确的深度排序**才能得到准确结果，因为该混合不具有交换律：A粒子在前、B粒子在后的混合结果，与顺序颠倒时的结果不同。这正是透明粒子特效中常见"排序穿插"问题的根源。Unity中半透明队列（Transparent Queue，值为3000）的存在，正是为了保证从后往前的绘制顺序。

### Pre-multiplied Alpha（预乘Alpha混合）

预乘Alpha是指贴图在存储时已将RGB值乘以Alpha：**存储值 = 原始RGB × α**。使用时混合因子设置为 **SrcFactor = One，DstFactor = OneMinusSrcAlpha**。与标准Alpha混合相比，源因子从`SrcAlpha`改为`One`，因为颜色数据中已经包含了Alpha权重。

预乘Alpha能够消除传统Alpha混合在纹理过滤时产生的"黑边"问题。当Alpha = 0的边缘像素在双线性过滤时与相邻非零像素混合，传统Alpha模式会引入原始RGB值参与计算，导致深色边缘。而预乘Alpha在Alpha = 0时，RGB本身也已经是0，过滤后不会引入错误颜色。Photoshop导出PNG时的"预乘Alpha"选项，以及Unity纹理导入设置中的"Alpha Is Transparency"，均与此原理直接相关。

### Multiply（正片叠底）

Multiply混合的因子为 **SrcFactor = DstColor，DstFactor = Zero**，结果为源颜色 × 目标颜色。由于任何颜色与黑色相乘都得黑色，与白色相乘保持原色，该模式常用于制作阴影贴花（Decal Shadow）、污渍叠加等"只让画面变暗"的效果，在移动端也可作为实时阴影的轻量替代方案。

## 实际应用

**火焰粒子特效**：火焰的核心火苗使用Additive模式，通过颜色亮度控制发光强度；外层烟雾改用Alpha混合，表现遮挡感。同一个粒子系统常使用两层材质叠加，分别配置不同混合模式。

**UI光效**：在游戏UI的技能冷却光效、描边发光中，Additive是首选，因为UI层背景颜色变化大，Additive能自然融入任意背景色而不产生突兀边框。

**贴花（Decal）系统**：地面弹痕、血迹等贴花通常使用Alpha混合结合`ZWrite Off`（关闭深度写入），防止贴花影响后续透明物体的排序计算。

**软粒子与烟雾**：预乘Alpha在烟雾贴图的边缘过渡处表现优于传统Alpha混合，特别是在烟雾纹理分辨率较低（如64×64的噪波贴图）时，锯齿和黑边问题更为明显，此时应优先使用预乘Alpha工作流。

## 常见误区

**误区一：Additive粒子无法控制浓度**。许多开发者认为Additive粒子只能越叠越亮而无法调暗。实际上，通过降低粒子颜色的RGB亮度值（而非Alpha值）即可控制Additive粒子的视觉浓度，因为Additive混合使用的是RGB作为贡献量，Alpha在标准Additive中不参与叠加计算。

**误区二：预乘Alpha只是存储格式问题，混合因子无需修改**。这是使用预乘Alpha时最常见的错误。若贴图是预乘格式但Shader仍使用`Blend SrcAlpha OneMinusSrcAlpha`（传统Alpha因子），则颜色会被Alpha权重计算两次，导致整体偏暗。预乘Alpha必须配合`Blend One OneMinusSrcAlpha`才能正确还原颜色。

**误区三：所有透明特效都应关闭ZWrite**。Alpha混合特效通常需要关闭深度写入（`ZWrite Off`），但若特效使用Alpha Test（`clip()`指令做硬边裁切）而非Alpha Blend，则应保留`ZWrite On`，否则会导致被该特效遮挡的后续物体错误地渲染出来。

## 知识关联

混合模式的配置通常依赖**自定义数据（Custom Data）**传入逐粒子的颜色和Alpha值，自定义数据决定了源颜色的具体输入，而混合模式决定这个输入如何与帧缓冲结合——两者在Shader特效管线中紧密配合。

掌握混合模式后，学习**PBR特效材质**时会遇到一个关键矛盾：PBR的物理光照模型默认假定材质不透明，引入透明度和混合模式后需要额外处理菲涅尔、高光等项的混合正确性。而在**Overdraw控制**方向，混合模式的选择直接决定一个像素是否必须进入混合计算阶段——Additive模式下无法通过Early-Z剔除透明区域，理解这一点是优化半透明特效Overdraw的前提知识。