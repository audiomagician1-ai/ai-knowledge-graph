---
id: "cg-early-z"
concept: "Early-Z优化"
domain: "computer-graphics"
subdomain: "rasterization"
subdomain_name: "光栅化"
difficulty: 3
is_milestone: false
tags: ["优化"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# Early-Z优化

## 概述

Early-Z优化是图形硬件在片段着色器执行**之前**就进行深度测试的一种技术。传统管线中，深度测试位于片段着色器之后（Late-Z），这意味着即使某个片段最终会被遮挡，GPU仍然会对其完整执行着色计算，造成大量无效工作。Early-Z将深度比较提前到光栅化阶段结束后、片段着色器启动前，从而跳过注定被丢弃的片段的着色计算。

这项技术最早随着可编程着色器硬件的普及而被引入商用GPU。NVIDIA在GeForce3（2001年发布，NV20架构）中开始集成Early-Z硬件支持，ATI在同期的Radeon 8500中也提供类似机制。由于现代场景中遮挡关系复杂，Early-Z在城市建筑、密集植被等场景中可将着色工作量削减50%甚至更多。

Early-Z之所以重要，在于片段着色器（Pixel Shader）通常是整个渲染管线中最耗时的阶段，而场景中大量片段因遮挡关系根本不会出现在最终画面上。提前剔除这些片段，能够直接提升GPU的有效吞吐率，是不需要修改算法逻辑即可获得性能收益的硬件级优化。

---

## 核心原理

### Early-Z测试的工作流程

在光栅化产生片段坐标 (x, y) 及其插值深度值 z_frag 后，硬件立即将 z_frag 与当前深度缓冲中存储的 z_buf(x,y) 进行比较。若比较失败（例如深度函数为 GL_LESS 时 z_frag ≥ z_buf），则该片段被直接丢弃，片段着色器**不会被调用**。完整的判断条件为：

```
若 depth_test(z_frag, z_buf) == FAIL → 丢弃片段，跳过片段着色器
若 depth_test(z_frag, z_buf) == PASS → 执行片段着色器，之后更新深度缓冲
```

这一流程要求硬件能在光栅化阶段与着色阶段之间插入一个独立的深度比较单元，并配备对深度缓冲的快速读取通道。

### Hi-Z（Hierarchical-Z）剔除

Hi-Z是Early-Z的层级化扩展，使用一个多级分辨率的深度缓冲金字塔来实现**图块（Tile）级别**的批量剔除。GPU将屏幕划分为若干8×8或16×16像素的图块，在Hi-Z缓冲的最高层级存储每个图块内的**最小深度值（z_min）**。对于一批即将光栅化的三角形，若其所有采样点的深度均大于对应图块的 z_min，则整批片段可以在进入逐像素测试之前就被整体剔除，无需逐片段比较。

Hi-Z的金字塔构建代价较低：每帧在渲染不透明物体后，硬件自动对深度缓冲进行降采样，每个上层级格子存储其覆盖的下层级中的最大深度（在Near-to-Far深度约定下为最近深度）。NVIDIA将此机制称为"Z-Cull"，AMD称为"Hierarchical Z"，虽名称不同，原理一致。

### Early-Z失效的条件

Early-Z并非在所有情况下都能工作。以下操作会**强制禁用**Early-Z，退回Late-Z模式：

1. **片段着色器中修改深度值**：若着色器写入 `gl_FragDepth`（GLSL）或 `SV_Depth`（HLSL），硬件无法在着色前知晓最终深度，Early-Z失效。
2. **Alpha测试（discard/clip）**：若着色器中含有 `discard` 指令，片段是否存活取决于着色结果，Early-Z无法预测，因此被禁用。部分现代API（如Vulkan的`conservativeRasterizationMode`）或硬件支持"保守Early-Z"，但覆盖率有限。
3. **深度写入被禁用**：若 `glDepthMask(GL_FALSE)`，深度缓冲不更新，Hi-Z的图块最小值可能失效。

---

## 实际应用

### 不透明物体的前向排序

利用Early-Z最直接的方法是将不透明物体按**从近到远（Front-to-Back）**顺序提交绘制。第一个绘制的最近物体会正常通过所有测试并写入深度缓冲；后续更远的物体在Early-Z阶段即被大量丢弃。这是无需更改着色器代码即可获益的调用顺序优化，许多游戏引擎（如Unreal Engine的静态网格排序）默认采用此策略。

### Z-Prepass（深度预通道）

一种主动利用Early-Z的技术：在正式渲染前，先用一个只输出深度、不执行复杂着色的简单Pass将所有不透明几何体的深度写入缓冲区（整个Pass关闭颜色写入）。随后正式渲染时将深度函数改为 `GL_EQUAL`（只通过深度完全相等的片段），此时Early-Z将以接近100%的效率剔除所有遮挡片段，复杂着色只在可见片段上执行。Z-Prepass在片段着色器极其复杂（如多灯光PBR材质）时效益显著，但代价是额外的几何体绘制开销，适合顶点处理廉价、像素处理昂贵的场景。

### 避免Early-Z失效的材质设计

对于使用透明度裁剪（Alpha Clip/Alpha Test）的材质，许多引擎允许单独为深度Pass关闭discard，仅在颜色Pass中启用。这样深度Pass可以享受Early-Z加速，颜色Pass中即使回退Late-Z，遮挡的大部分片段也已经被深度缓冲挡住。

---

## 常见误区

### 误区一：Early-Z等同于遮挡剔除（Occlusion Culling）

Early-Z和Hi-Z是**屏幕空间、像素/图块级别**的深度测试加速，它们在光栅化阶段内部工作，针对的是已经通过视锥剔除、已经提交给GPU的三角形的片段。而遮挡剔除（如CPU侧的PVS或GPU Query）针对的是整个网格对象，在提交绘制调用之前就决定是否绘制整个物体。两者作用层级不同，互为补充而非替代。

### 误区二：只要不写gl_FragDepth，Early-Z就一定开启

`discard`指令是另一个常被忽视的失效触发因素。许多开发者编写的植被或栅格材质在着色器中使用`discard`做Alpha测试，导致整个Drawcall的Early-Z全部失效，即便场景中存在大量几何遮挡也无法受益。解决方法是将Alpha测试材质的深度Pass与颜色Pass分离，或使用 `EarlyDepthStencil`（HLSL）属性强制启用——但后者在discard后仍会写深度，可能产生错误结果，需谨慎使用。

### 误区三：Front-to-Back排序对Early-Z没有实质帮助

部分开发者认为GPU硬件会自动处理遮挡，排序是多余的。实际上Early-Z只能剔除**已经写入深度缓冲的区域**对应的后续片段；如果绘制顺序完全随机，每个片段在提交时深度缓冲可能尚未被其遮挡物填充，Early-Z命中率极低，性能退化接近Late-Z水平。Front-to-Back排序是让Early-Z发挥最大效能的必要条件。

---

## 知识关联

Early-Z的正确理解依赖对**深度缓冲**的掌握：需要清楚深度缓冲存储的是NDC空间下的 z 值（范围[0,1]）、深度比较函数的语义（GL_LESS/GL_LEQUAL等），以及深度写入与读取的分离控制（glDepthMask）。

在渲染技术谱系中，Early-Z是光栅化阶段内的像素级优化。它与**遮挡剔除**（对象级）、**视锥体剔除**（对象级，CPU侧）形成三个层次的可见性剔除体系。理解了Early-Z失效条件后，自然引出对**延迟渲染（Deferred Rendering）**的理解：延迟渲染的Geometry Pass天然兼容Early-Z（无discard、无自定义深度），这正是延迟管线在复杂光照场景下性能表现优异的原因之一。此外，Hi-Z缓冲生成的深度金字塔在**屏幕空间反射（SSR）**和**HBAO**等后处理技术中也被复用，是连接光栅化优化与后处理技术的重要数据结构。