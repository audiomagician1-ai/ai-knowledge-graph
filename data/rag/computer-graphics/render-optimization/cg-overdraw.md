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
quality_tier: "A"
quality_score: 76.3
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


# Overdraw分析

## 概述

Overdraw（过度绘制）是指屏幕上同一像素在单帧内被多次写入颜色值的现象。当一个不透明物体被另一个物体完全遮挡，GPU仍然对被遮挡物体的像素执行片元着色器并写入帧缓冲区，这个无效的写入操作就构成了Overdraw。Overdraw率通常用"倍数"表示：1x表示每像素仅绘制一次（理想状态），2x表示每像素平均绘制两次，现代移动端游戏的Overdraw超过2.5x往往会引发明显的性能瓶颈。

Overdraw的性能代价在不同架构的GPU上表现差异显著。桌面端GPU通常采用立即渲染模式（Immediate Mode Rendering），Overdraw直接造成带宽和ALU算力浪费；移动端GPU普遍采用基于瓦片的延迟渲染（Tile-Based Deferred Rendering，TBDR），其架构虽然通过HSR（Hidden Surface Removal）机制自动消除部分Overdraw，但粒子系统、半透明UI等仍会产生严重的带宽压力。

Overdraw分析之所以重要，是因为片元着色器的计算成本远高于顶点着色器——在复杂的PBR材质管线中，单个片元可能需要执行数百条指令，若该像素最终被其他物体覆盖，这些计算全部白费。在一个分辨率为1920×1080的场景中，若Overdraw达到4x，GPU每帧实际处理的像素数量超过800万，而最终呈现到屏幕的有效像素仅约200万。

## 核心原理

### Overdraw的度量方法

量化Overdraw的标准方法是使用**Stencil Buffer累加技术**：将Stencil测试配置为每次通过时加1，禁用深度写入并将深度测试设为Always，然后正常渲染场景。最终Stencil Buffer中每个像素的数值即为该像素被绘制的次数。Unity的Frame Debugger、RenderDoc的Pixel History功能，以及Android GPU Inspector均提供了可视化Overdraw的工具，通常用热力图展示——蓝色代表低Overdraw，红色代表高Overdraw（4x以上）。

Overdraw率的计算公式为：

**Overdraw率 = 总片元着色调用次数 ÷ 屏幕像素总数**

例如，屏幕分辨率为1080P（约207万像素），若一帧内片元着色器总调用次数为620万次，则Overdraw率约为3x。

### Overdraw的主要来源

**粒子系统与半透明物体**是Overdraw最大的来源。由于半透明物体必须按从后到前（Back-to-Front）的顺序渲染以保证混合结果正确（Alpha Blending依赖下层颜色值），无法利用Early-Z测试在片元着色器之前剔除，因此每个粒子都会无条件写入带宽。一个包含500个粒子、每个粒子面积覆盖200像素的效果，在高峰时刻可产生高达10万次的额外片元调用。

**场景几何体的渲染顺序不合理**同样会造成严重Overdraw。若渲染管线按照资产加载顺序提交Draw Call，远处物体可能在近处物体之前绘制。例如，先渲染一栋100米外的楼房，再渲染玩家脚下的地板，楼房的像素就会被地板覆盖，形成无效绘制。

**UI层叠**在移动游戏中也是常见的Overdraw来源。全屏背景图、装饰性底板、文字描边阴影等多层UI元素叠加，可轻易在局部区域制造5x至8x的Overdraw。

### Front-to-Back排序原理

Front-to-Back（由近及远）渲染排序是针对不透明物体消除Overdraw最有效的手段，其核心依赖GPU的**Early-Z（提前深度测试）**机制。当不透明物体按由近及远排序后，第一个写入深度缓冲的是最近的物体；渲染后续更远的物体时，Early-Z在片元着色器执行之前就能判断该片元被遮挡并丢弃，避免了无效的着色计算。

排序的依据通常是物体包围盒中心点到摄像机的距离。具体实现时，CPU端在每帧将不透明渲染队列按距离升序排列后提交给GPU。这一操作的CPU排序成本为O(N log N)，当场景中不透明物体数量N超过数千时，排序本身的开销需要与Overdraw节省之间做权衡——通常在N < 2000时Front-to-Back排序总体收益为正。

## 实际应用

**Unity中的渲染队列设置**：Unity通过`RenderQueue`数值控制渲染顺序，不透明物体的默认队列值为2000，透明物体为3000。开发者应避免将不透明物体的`RenderQueue`设为高于2000的值，否则会破坏引擎内置的Front-to-Back排序逻辑。可通过`Camera.SetReplacementShader`将所有材质替换为纯色叠加着色器，直观观察Overdraw热点区域。

**粒子效果优化**：将粒子贴图的Alpha通道尽可能紧凑地裁切，使用Tight Mesh（紧密网格）代替默认的Quad形状，可减少40%至60%的透明区域片元调用。在Unity Particle System中启用"Render Alignment: Local"并手动编辑Renderer的Mesh可实现这一优化。

**移动端UI优化**：在UGUI中，将同一层级不重叠的UI元素合并到同一Canvas，并对全屏遮罩使用`RectMask2D`代替`Mask`组件——`Mask`使用Stencil会产生额外的Draw Call且无法裁剪Overdraw，而`RectMask2D`通过矩形裁剪直接跳过矩形外的片元计算。

## 常见误区

**误区一：认为开启深度测试就能自动消除所有Overdraw**。深度测试（Depth Test）默认在片元着色器之后执行（Late-Z），只有在Early-Z生效时才能提前剔除片元。若片元着色器中包含`discard`语句（如AlphaTest），或写入了`gl_FragDepth`，GPU会被迫禁用Early-Z，退回到Late-Z模式，使Front-to-Back排序的优化效果完全失效。这是使用AlphaTest材质时Overdraw较高的根本原因，因此应尽量用Alpha Blend替代AlphaTest，或将AlphaTest物体单独放入专门的渲染Pass。

**误区二：认为Overdraw只影响填充率（Fill Rate）受限的场景**。在现代GPU上，带宽（Memory Bandwidth）往往比ALU算力更先成为瓶颈。每次片元写入不仅消耗ALU，还要读写帧缓冲区（Framebuffer）和深度缓冲区，在移动端LPDDR5内存带宽约68 GB/s的限制下，高Overdraw场景的帧缓冲读写流量可轻易占满带宽预算的30%以上。

**误区三：认为Overdraw分析只在低端设备上才有价值**。在使用了延迟渲染（Deferred Rendering）管线的高端项目中，GBuffer的写入同样存在Overdraw问题——GBuffer通常包含4至5张全分辨率贴图，每张8至16 bytes，Overdraw产生的重复写入对带宽压力是普通前向渲染的数倍。

## 知识关联

Overdraw分析建立在渲染优化概述中介绍的GPU管线流程之上，特别是深度缓冲（Z-Buffer）的工作机制和片元着色阶段的成本概念。理解Early-Z的触发条件（无discard、无自定义深度输出）是正确运用Front-to-Back排序的前提。

Overdraw问题与Draw Call优化存在天然的权衡关系：合并Mesh可减少Draw Call，但合并后的大型Mesh往往难以按Front-to-Back顺序排序，且更难进行视锥体剔除（Frustum Culling）；反之，拆分物体有利于排序和剔除，却增加了Draw Call数量。在实际优化工作中，需要结合GPU Profiler的帧时数据，判断当前瓶颈在于Overdraw还是Draw Call，再针对性地选择优化方向。