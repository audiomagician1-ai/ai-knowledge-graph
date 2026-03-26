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
quality_tier: "B"
quality_score: 45.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.433
last_scored: "2026-03-22"
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

混合模式（Blend Mode）是GPU渲染管线中控制新绘制像素（源像素）如何与帧缓冲区中已存在像素（目标像素）进行颜色合成的算法规则。其数学本质是一条公式：**最终颜色 = 源颜色 × 源因子 + 目标颜色 × 目标因子**，通过改变源因子（SrcFactor）和目标因子（DstFactor）的取值，可以得到完全不同的视觉效果。

混合模式的理论基础可以追溯到1984年Porter和Duff发表的论文《Compositing Digital Images》，该论文系统定义了Alpha合成的数学框架，其中"Over"操作正是今天游戏引擎中Alpha混合的原型。此后，图形硬件逐渐将这些混合方程以固定管线的形式内置于GPU中，开发者只需设置混合参数即可驱动硬件完成像素合成。

在Shader特效开发中，混合模式的选择直接决定特效的视觉外观、性能开销以及是否出现颜色错误。选错混合模式会导致半透明边缘出现黑边、加法叠加后颜色过曝、或者粒子排序问题，这些都是特效制作中最常见的视觉缺陷来源。

## 核心原理

### Alpha混合（Alpha Blending）

Alpha混合是最通用的透明度混合方式，对应参数设置为 **SrcFactor = SrcAlpha，DstFactor = OneMinusSrcAlpha**，公式展开为：

**最终颜色 = 源RGB × 源Alpha + 目标RGB × (1 - 源Alpha)**

当源Alpha为1时，完全覆盖目标像素；当源Alpha为0时，完全透明不影响目标。这种模式需要粒子或半透明物体**从后向前排序**（Back-to-Front，即Painter's Algorithm），否则后绘制的透明物体会错误地"盖住"已混合的前方物体。Alpha混合适合烟雾、云朵、玻璃等需要正确半透明效果的场景。

### 加法混合（Additive Blending）

加法混合参数为 **SrcFactor = SrcAlpha（或One），DstFactor = One**，公式为：

**最终颜色 = 源RGB × 源Alpha + 目标RGB × 1**

加法混合的核心特征是只会让画面变亮，不会遮挡背景，多层叠加会趋向纯白。这一特性天然适合火焰、闪电、激光、魔法光效等"自发光"类特效——这类效果在现实中也是将光线叠加到环境上的。加法混合无需深度排序，多个粒子系统互相叠加顺序不影响结果，因此性能友好。但在暗色背景上叠加多层时极易过曝，需配合粒子Alpha控制亮度上限。

### 预乘Alpha混合（Pre-multiplied Alpha Blending）

预乘Alpha的图像纹理中，RGB通道已提前乘以Alpha值（即存储的是 `RGB × Alpha`），对应混合参数为 **SrcFactor = One，DstFactor = OneMinusSrcAlpha**，公式为：

**最终颜色 = 源RGB（已预乘）× 1 + 目标RGB × (1 - 源Alpha)**

与普通Alpha混合相比，预乘Alpha可以同时模拟**加法和Alpha混合的中间效果**：纹理中Alpha=0但RGB不为0的区域表现为加法叠加，Alpha=1的区域则完全覆盖，这使得一张纹理就能同时表达"发光核心+半透明外晕"的复杂效果。Spine、Unity的URP/HDRP粒子系统均推荐使用预乘Alpha格式，因为它可以避免半透明纹理边缘的"黑边"伪影（该伪影是双线性采样时Alpha=0像素的黑色RGB值渗入边缘导致的）。

### 正片叠底与柔光（Multiply / Soft Light）

正片叠底参数为 **SrcFactor = DstColor，DstFactor = Zero**，效果是将源颜色与目标颜色相乘，结果只会比两者都暗。常用于实时阴影染色、压暗特效，如脚底阴影贴片或角色受击变暗效果。柔光等复杂混合模式在OpenGL ES 2.0硬件上无法直接用硬件混合实现，需要在Shader中手写合成逻辑并关闭硬件混合。

## 实际应用

**火焰粒子**通常使用加法混合（SrcFactor=SrcAlpha, DstFactor=One），粒子颜色从亮黄到暗红渐变，配合Alpha从1到0的生命周期曲线，在暗色场景中自然叠加出火焰体积感，同时不产生遮挡黑边。

**烟雾粒子**必须使用Alpha混合（SrcFactor=SrcAlpha, DstFactor=OneMinusSrcAlpha），并启用深度写入关闭、深度测试开启，再结合粒子系统的Distance Sort或View Space Z Sort确保后向前绘制顺序，否则相邻烟雾粒子会出现硬切边缘。

**UI光晕特效**在使用预乘Alpha贴图时，将混合设置为（One, OneMinusSrcAlpha），可以让美术在Photoshop中以正常图层方式绘制贴图后直接导出预乘格式，保留边缘的高光信息而不丢失任何渐变细节。

**受击白闪效果**短暂将角色材质切换至（One, One）全加法模式叠加一个纯白颜色，视觉上产生强烈的发光击打感，持续约0.1秒后切换回原混合模式。

## 常见误区

**误区一：加法混合与Alpha混合可以随意互换**。两者的本质差异在于对目标像素的处理：加法混合DstFactor=One，目标颜色完整保留并叠加；Alpha混合DstFactor=OneMinusSrcAlpha，目标颜色按源透明度被"压暗"。将烟雾从Alpha混合错误改为加法混合，背景会透过烟雾完全显现，烟雾丧失遮挡感，变成发光效果。

**误区二：普通Alpha混合与预乘Alpha混合的纹理可以混用**。若将未预乘的纹理（普通RGBA贴图）用于预乘Alpha混合参数（One, OneMinusSrcAlpha），RGB与Alpha分离计算会导致半透明区域过亮；反之，将预乘纹理用于普通Alpha混合参数（SrcAlpha, OneMinusSrcAlpha），会对RGB进行二次Alpha乘法，导致半透明区域整体变暗。纹理格式与混合参数必须严格对应。

**误区三：关闭深度写入就无需考虑绘制顺序**。关闭深度写入（ZWrite Off）只是防止透明物体污染深度缓冲区，并不能自动解决透明物体之间的排序问题。在使用Alpha混合的粒子系统中，若多个粒子的绘制顺序混乱，重叠区域会根据绘制先后计算出不同的混合结果，导致闪烁或颜色错误。

## 知识关联

学习混合模式前需要掌握**自定义数据（Custom Data）**的使用——粒子系统通过Custom Data向Shader传递每粒子的Alpha缩放、颜色乘数等参数，这些参数直接影响进入混合方程的源颜色值，是动态控制混合强度的标准手段。

掌握混合模式后，可以进入**PBR特效材质**的学习：PBR管线中透明物体的混合涉及Premultiplied Alpha与GBuffer兼容性问题，延迟渲染路径（Deferred）天然不支持透明混合，必须在Forward Pass中处理，这正是混合模式在PBR特效中的直接延伸。

混合模式还直接关联**Overdraw控制**：加法混合和Alpha混合的粒子都会产生Overdraw（同一屏幕像素被多次绘制），Overdraw成本与粒子的屏幕覆盖面积和层叠数量成正比，理解混合模式的叠加机制是评估和优化Overdraw的前提。