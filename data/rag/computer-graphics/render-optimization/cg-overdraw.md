---
id: "cg-overdraw"
concept: "Overdraw分析"
domain: "computer-graphics"
subdomain: "render-optimization"
subdomain_name: "渲染优化"
difficulty: 2
is_milestone: false
tags: ["实践"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 50.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.452
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# Overdraw分析

## 概述

Overdraw（过度绘制）是指屏幕上同一个像素在单帧渲染过程中被多次写入颜色值的现象。当场景中存在多个不透明物体相互遮挡时，位于后面的物体的像素虽然最终不可见，却依然消耗了片元着色器的计算资源。Overdraw率被定义为：**总绘制像素数 ÷ 屏幕分辨率像素数**，当这个比值为1时表示每个像素恰好绘制一次（无Overdraw），实际场景中这个值常常达到2～5，移动端UI密集场景甚至可以超过10。

Overdraw问题在早期固定管线时代并不突出，因为片元着色器计算量很低。随着2000年代可编程着色器的普及，片元着色器变得越来越复杂（PBR材质、屏幕空间反射等），同一像素被重复着色的代价急剧上升。Unity引擎在Scene视图中专门提供了Overdraw可视化模式，越亮的区域表示Overdraw越严重；Adreno GPU也在其Snapdragon Profiler工具中将Overdraw热力图作为首要性能指标之一。

对于移动端GPU而言，Overdraw的危害尤为突出。Tile-Based渲染架构（如ARM Mali、Imagination PowerVR）会将屏幕分成16×16或32×32的小块分别处理，过高的Overdraw会导致每个Tile内的像素处理量超出片上缓存容量，触发额外的带宽消耗，直接影响功耗和帧率。

## 核心原理

### Overdraw的产生机制

GPU在默认状态下按照DrawCall的提交顺序依次绘制物体。在深度测试（Depth Test）通过之前，片元着色器已经完成了颜色计算，这种模式称为**Late-Z**（延迟深度测试）。Late-Z意味着即使后续深度测试判定该片元被遮挡并丢弃，其着色计算已经白白消耗完毕。以一个100万像素的屏幕为例，若Overdraw率为3，则实际执行了300万次片元着色，其中200万次的结果被深度测试丢弃，利用率仅33%。

现代GPU提供了**Early-Z**机制：在片元着色器执行之前先进行深度测试，提前剔除必然被遮挡的片元。但Early-Z有一个关键前提——片元着色器中不能包含`discard`指令或对深度值的修改（`gl_FragDepth`），否则GPU无法提前判断深度结果，会自动退回到Late-Z模式。这意味着即使硬件支持Early-Z，使用了Alpha Test的材质也会破坏这一优化。

### Front-to-Back排序

解决Overdraw最直接的方法是将不透明物体按照**由前到后（Front-to-Back）**的顺序提交DrawCall。当靠近摄像机的物体先被绘制并写入深度缓冲后，后续更远的物体即可被Early-Z大量剔除，彻底避免这些片元进入着色阶段。

Front-to-Back排序通常基于物体包围盒（AABB或包围球）的中心点到摄像机的距离进行近似排序，计算公式为：

**d = (Object_Center - Camera_Position) · Camera_Forward**

其中`Camera_Forward`为摄像机前方向的单位向量，使用点积投影可以比完整的欧氏距离运算更快速（避免了开方操作）。Unity的SRP（Scriptable Render Pipeline）在渲染不透明物体时默认启用`SortingCriteria.CommonOpaque`，其中就包含了Front-to-Back的深度排序。

与不透明物体相反，半透明物体**必须**采用Back-to-Front（由后到前）顺序绘制，以保证Alpha Blending的正确性，这也是为什么半透明物体的Overdraw几乎无法通过排序优化消除。

### Overdraw的测量方法

**方法1：着色器计数法**
创建一个特殊的调试材质，在片元着色器中输出固定的半透明白色（如`float4(0.1, 0.1, 0.1, 0.1)`），并使用Additive混合模式替换场景所有材质。最终屏幕上越亮的区域累积的绘制次数越多，通过像素亮度可直接反推Overdraw层数。

**方法2：GPU性能计数器**
高端GPU分析工具（如RenderDoc、NSight Graphics、Snapdragon Profiler）可以直接读取硬件的`FRAG_SHADER_INVOCATIONS`计数器，与实际解析的唯一像素数相除即得精确Overdraw率，无需修改任何着色器。

**方法3：引擎内置可视化**
Unity的Overdraw场景视图模式、Unreal Engine的`r.EarlyZPass`相关统计命令均可实时展示热力图，适合快速定位问题区域，但精度低于GPU计数器方法。

## 实际应用

**粒子系统Overdraw优化**：粒子效果是移动端Overdraw的重灾区。一个全屏爆炸特效可能叠加30～50层半透明粒子，单帧Overdraw贡献超过整个场景的60%。常见解决方案是降低粒子的屏幕覆盖面积（缩小粒子尺寸或减少数量），以及将大粒子拆分为多个较小粒子以减少单像素的层叠次数。

**UI渲染中的Overdraw**：在手机游戏UI中，多层面板叠加是典型Overdraw来源。例如背景图→底框→图标→文字→高光层这5层UI元素叠加，导致中心区域Overdraw达到5。解决方案包括：合并静态UI层为一张离屏渲染纹理（Render Texture），以及通过`Canvas.ForceUpdateCanvases()`配合裁剪遮罩限制绘制区域。

**植被与树木渲染**：密集植被场景中，叶片的Alpha Test材质会禁用Early-Z，使得树冠区域Overdraw问题同时叠加了排序失效和Alpha Test退化两个因素。针对这种情况，可以使用Depth Pre-Pass（深度预通道）单独写入深度缓冲，再在正式着色通道中启用Equal深度测试（`ZTest Equal`），强制所有片元先经过精确深度裁剪后再着色。

## 常见误区

**误区一：Overdraw高一定代表性能差**
Overdraw是性能开销的指示器，但其实际影响取决于片元着色器的复杂度。若片元着色器只有简单的纹理采样（如UI背景），即使Overdraw为5也可能对帧率影响甚微；而Overdraw为2但每层都含有实时阴影计算和多光源PBR时，开销可能远超前者。优化时应结合GPU Bound分析，确认瓶颈确实来自片元着色阶段后，再针对Overdraw下手。

**误区二：Front-to-Back排序对所有物体都有效**
Front-to-Back排序的收益完全依赖Early-Z机制，而Alpha Test材质、带`discard`的着色器、写入`gl_FragDepth`的着色器均会禁用Early-Z。在角色身上有大量Alpha Test服装的场景中，盲目相信排序能解决Overdraw问题会导致优化方向错误。此外，GPU的三角形级别Early-Z只能以三角形为粒度剔除，即使排序正确，同一三角形内不同片元的遮挡情况依然无法被提前剔除。

**误区三：Depth Pre-Pass总是值得的**
Depth Pre-Pass通过额外一次几何体绘制（只写深度不写颜色）来换取正式通道的Early-Z精确剔除。当场景Overdraw率较低（低于1.5）时，Pre-Pass增加的几何体处理开销可能大于节省的片元着色开销，得不偿失。Depth Pre-Pass通常只在场景几何复杂度适中但着色复杂度极高时才能体现正向收益。

## 知识关联

Overdraw分析建立在渲染管线的**片元着色阶段**和**深度测试**机制之上，理解Late-Z与Early-Z的区别是分析Overdraw代价的基础。排序优化（Front-to-Back）与剔除技术（视锥体剔除、遮挡剔除）相辅相成——剔除减少进入GPU的DrawCall数量，而排序优化进入GPU之后的着色效率，两者共同构成减少无效像素计算的完整方案。Overdraw分析的结论会直接指导**批处理策略**（合并半透明物体以控制层叠数量）以及**LOD系统设计**（远处物体的低面数模型同时也意味着更少的像素覆盖面积），是渲染优化流程中衔接"减少DrawCall"和"优化着色复杂度"两个方向的关键分析手段。