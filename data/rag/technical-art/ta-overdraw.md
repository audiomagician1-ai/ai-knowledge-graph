---
id: "ta-overdraw"
concept: "Overdraw控制"
domain: "technical-art"
subdomain: "perf-optimization"
subdomain_name: "性能优化"
difficulty: 2
is_milestone: false
tags: ["核心"]

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
updated_at: 2026-04-01
---


# Overdraw控制

## 概述

Overdraw（过度绘制）是指屏幕上同一个像素在单帧渲染中被多次写入颜色值的现象。每当一个片元（fragment）通过了深度测试或混合测试并写入帧缓冲，就算一次绘制；若某像素被绘制了5次，该像素的Overdraw倍率就是5x。在移动端GPU（如Mali、Adreno系列）上，由于其基于Tile-Based架构，Overdraw对带宽和填充率（fill rate）的压力尤为突出，直接导致功耗上升和帧率下降。

Overdraw问题在早期移动游戏优化中被反复提及，约2012年前后随着Adreno 200/300系列GPU的大量普及而引起广泛重视。Unity与UE都提供了Overdraw可视化模式：Unity的Scene视图中选择"Overdraw"着色模式后，颜色越亮白表示该区域重绘次数越多；Unreal则通过`Optimization Viewmode > Shader Complexity`间接反映类似问题。一般认为移动端Overdraw倍率超过2.5x即需要介入优化。

透明物体、粒子特效和UI控件是产生Overdraw的三大主要来源，它们共同的特点是**不写入深度缓冲**或**强制关闭Early-Z剔除**，导致GPU无法在光栅化阶段提前丢弃被遮挡的片元，每一层都必须完整执行片元着色器。

---

## 核心原理

### 1. Early-Z与Overdraw的关系

现代GPU的渲染管线中存在Early-Z测试阶段：在片元着色器执行**之前**，硬件先比较该片元的深度值与深度缓冲中的已有值。若片元被遮挡，则直接丢弃，节省整个着色器的计算。公式如下：

> 有效节省 = 丢弃片元数 × 片元着色器单位开销

然而，透明物体（Alpha Blend模式）的渲染必须按照**从后向前（Painter's Algorithm）**的顺序提交，同时混合运算依赖已写入的颜色值，因此无法开启Early-Z。每一个透明层都会完整执行着色器并读写帧缓冲，这是透明物体高Overdraw的根本原因。

### 2. 透明物体的Overdraw累积机制

以一个由10层Alpha Blend粒子叠加的爆炸特效为例：假设每层粒子铺满屏幕的20%区域，理论上该区域Overdraw = 10x。若底层还有不透明场景的基础绘制，总Overdraw可达11x。在1080p屏幕上，20%区域约为414,720个像素，每帧这414,720个像素被写入11次，而在60fps下每秒产生约2.7亿次无效像素写入。

粒子系统的批次合并（Dynamic Batching）虽然能减少Draw Call，但**不会减少Overdraw**，因为Overdraw由几何覆盖关系决定，而非提交次数。这是很多开发者的混淆点。

### 3. UI的Overdraw特征

UI通常处于渲染管线的最末尾，叠加在三维场景之上。Canvas中的每一个Image、Text或RawImage组件都可能独立产生一层绘制。常见问题包括：全屏背景图压在三维场景上（即使场景已完整渲染），以及多个Panel的半透明背景互相叠加。Unity的Canvas合并机制（Canvas Batching）在同一Canvas内可以合并顶点，但跨Canvas或含有Mask组件的层级仍会打断合并，产生额外的Overdraw层。

`UI Profiler`或Frame Debugger可以逐Pass检查UI每一次DrawCall写入的像素范围，从而定位高Overdraw的UI控件。

---

## 实际应用

**粒子特效优化：** 将粒子贴图中透明像素占比超过60%的Sprite进行网格裁剪（Tight Mesh），Unity的Sprite Editor提供`Generate Mesh`功能可将矩形Quad替换为紧包围网格，减少透明区域参与光栅化的像素数量，通常可将单粒子有效覆盖面积降低40%~70%。

**透明物体排序与Alpha Test替代：** 对于硬边缘透明效果（如树叶、铁丝网），使用Alpha Test（clip()指令）代替Alpha Blend，可以将渲染队列从`Transparent`（3000）移至`AlphaTest`（2450），从而参与深度写入和Early-Z，消除该类型的Overdraw。代价是Alpha Test在某些PowerVR GPU上会触发HSR（Hidden Surface Removal）失效，需针对目标平台实测。

**UI层级重组：** 将全屏纯不透明背景面板改为摄像机的`Background Color`，直接消除一层DrawCall及其Overdraw；对于固定不动的UI元素设置`Static`并使用`Canvas.renderMode = ScreenSpaceCamera`配合专用UI摄像机，避免与三维场景共享深度缓冲。

**RenderDoc / Snapdragon Profiler抓帧：** 在Adreno GPU设备上使用Snapdragon Profiler的`Overdraw Heatmap`功能，可以精确输出每像素的绘制次数热力图，颜色从蓝（1x）到红（8x+）分级显示，是定位Overdraw热点最直接的工具。

---

## 常见误区

**误区1：关闭粒子的投影（Cast Shadow）就能解决其Overdraw。**
投影与Overdraw是两个独立问题。禁用Cast Shadow仅减少ShadowMap Pass中的顶点处理，对主摄像机Pass中粒子的透明叠加层数没有任何影响。Overdraw必须从减少透明层数量或缩小覆盖面积入手。

**误区2：减少Draw Call等同于减少Overdraw。**
Draw Call合并（Batching）将多个网格合并为一次提交，减少的是CPU提交开销和GPU状态切换。但若合并后的网格仍然在同一屏幕区域叠加覆盖，GPU依然需要为每一层执行片元着色器，Overdraw倍率不变。两者优化目标完全不同，需分开衡量。

**误区3：Overdraw只在移动端才需要关注。**
PC端独立显卡的填充率极高，Overdraw的直接性能影响确实远小于移动端。但在Nintendo Switch（Tegra X1）、主机平台的某些分辨率配置，以及VR设备（需要双眼渲染，有效填充率压力翻倍）中，Overdraw仍然是重要瓶颈。Meta Quest 2的GPU建议Overdraw目标控制在1.5x以内。

---

## 知识关联

**前置概念——性能优化概述：** Overdraw属于GPU性能瓶颈中**填充率（Fill Rate）瓶颈**的具体表现形式，与顶点处理瓶颈、带宽瓶颈并列，需要先掌握GPU渲染管线的基础分工才能理解为何透明排序会阻断Early-Z。

**后续概念——粒子性能优化：** 粒子系统是Overdraw最高发的场景，后续将专门讨论粒子LOD（Level of Detail）、粒子数量上限动态调节、粒子Shader简化（移除GrabPass、减少贴图采样层数）等针对粒子的专项策略，这些策略都以控制Overdraw为核心目标之一，是本概念在粒子领域的深化应用。