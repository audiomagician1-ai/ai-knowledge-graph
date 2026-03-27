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
quality_tier: "B"
quality_score: 50.2
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.467
last_scored: "2026-03-22"
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

Early-Z优化是现代GPU在光栅化流水线中提前执行深度测试的硬件机制，核心思路是在片元着色器（Fragment Shader）执行**之前**完成Z值的比较和丢弃，而非传统流程中着色之后再做深度测试。这一改变使得被遮挡的片元在消耗着色器计算资源之前就被剔除，大幅减少无效的像素着色工作。

该优化最早在DirectX 9时代的GPU（约2001-2002年，如NVIDIA的NV25芯片）中以硬件形式普及。在Early-Z出现之前，标准OpenGL/D3D流水线强制规定深度测试在着色之后进行（Late-Z），导致被遮挡物体的着色计算全部白费。Early-Z将这一测试提前至光栅化阶段之后、着色阶段之前，从而节省了大量GPU计算周期。

Early-Z在场景遮挡关系复杂时效果最为显著。在一个典型的城市场景中，Near-to-Far排序下Early-Z可使像素着色调用量减少30%-70%，尤其对包含大量不透明几何体的场景（如第一人称射击游戏关卡），其收益远超其他传统深度优化手段。

## 核心原理

### 传统Late-Z流水线与Early-Z的对比

传统Late-Z流水线顺序为：顶点处理 → 图元装配 → 光栅化 → **片元着色** → 深度测试 → 写入帧缓冲。Early-Z则将深度测试提至片元着色之前：顶点处理 → 图元装配 → 光栅化 → **Early-Z测试** → 片元着色（仅通过测试的片元）→ 深度写入。两者的关键差别在于着色器何时获得执行机会，Early-Z模式下被遮挡片元从不进入着色阶段。

### Early-Z的自动失效条件

GPU硬件会在检测到以下任意条件时**自动关闭**Early-Z，退回Late-Z模式：

1. **着色器内修改深度值**：当片元着色器写入 `gl_FragDepth`（GLSL）或 `SV_Depth`（HLSL）时，硬件无法在着色前预知最终深度值，Early-Z失效。
2. **使用了丢弃指令**：着色器中包含 `discard`（GLSL）或 `clip()`（HLSL）语句时，片元有可能被着色器杀死，与Early-Z的"提前丢弃"逻辑冲突，硬件保守地关闭Early-Z。
3. **Alpha-to-Coverage或Alpha测试**：这类测试依赖着色器输出的透明度值，Early-Z无法提前得知结果。

因此，透明物体渲染几乎无法受益于Early-Z，这也是透明渲染性能成本高的根本硬件原因之一。

### Hi-Z（Hierarchical-Z）层次化深度剔除

Hi-Z是Early-Z的进阶扩展，使用一张分层的深度Mipmap结构存储深度的保守最大值（或最小值，取决于深度比较方向）。具体来说，GPU维护一个深度缓冲的降采样金字塔，每个更高层的纹素存储其对应区域内所有像素的最大Z值。

当渲染一个图元时，GPU先在Hi-Z金字塔的粗粒度层级上做范围测试：若该图元的**最小深度值**已经大于目标区域Hi-Z中存储的**最大深度值**（在"小Z值更近"约定下），则该图元所覆盖的全部片元都必然被遮挡，可一次性剔除整个图元或Tile，而无需逐像素测试。这使得单次Early-Z测试的剔除粒度从一个像素扩展到一个16×16乃至64×64的像素块（Tile），效率大幅提升。

Hi-Z的维护开销在每帧深度写入后自动触发增量更新，现代GPU（如AMD RDNA架构和NVIDIA Turing架构）将Hi-Z层级更新集成在ROP（Render Output Unit）硬件中完成，对应用层透明。

### 渲染顺序对Early-Z效率的影响

Early-Z的实际收益与绘制顺序强相关。若场景按照**从近到远（Front-to-Back）**顺序提交绘制调用，近处物体会率先填充深度缓冲，后续远处物体的片元在Early-Z阶段即可被大量剔除，超遮比（Overdraw Ratio）接近1.0。反之，若按从远到近绘制，Early-Z几乎无法剔除任何片元，因为深度缓冲中尚无更近的参考值。因此，游戏引擎通常在不透明物体渲染前按相机距离对绘制调用做升序排序，以最大化Early-Z收益。

## 实际应用

**Z-Prepass技术**：在主着色Pass之前，用一个仅写入深度、不执行任何颜色着色的PrePass完整渲染场景。这相当于人工构建最理想的深度缓冲初始状态，使主Pass的所有绘制调用完全依赖Early-Z，overdraw降为零。虚幻引擎（Unreal Engine）的Deferred Rendering管线默认开启Z-Prepass，代价是每个顶点多处理一次，适用于着色计算昂贵的场景，不适合顶点数量极多但着色简单的情况。

**遮挡剔除与Hi-Z结合**：一些引擎（如Unity HDRP）在CPU端遮挡剔除之外，额外在GPU端利用前一帧的Hi-Z金字塔做遮挡查询（Occlusion Query），剔除本帧被遮挡的绘制调用，进一步减少DrawCall数量，将Hi-Z从像素级剔除扩展到对象级剔除。

**透明物体的处理**：正因为透明物体无法使用Early-Z，引擎通常将透明物体排在不透明物体之后、从远到近渲染，并关闭深度写入（保留深度测试）。这是Early-Z优化直接决定渲染顺序约定的典型案例。

## 常见误区

**误区1：Early-Z总是自动生效，无需开发者干预。**  
实际上，只要着色器中存在 `discard` 或 `gl_FragDepth` 写入，硬件就会静默退回Late-Z模式，开发者可能完全不知情。使用RenderDoc或Nsight等GPU性能分析工具查看Early-Z命中率时，常会发现因为某一个着色器的 `discard` 导致整批次Early-Z被禁用的情况。对性能敏感的不透明材质，应显式避免这两类操作。

**误区2：Z-Prepass永远优于不做Prepass。**  
Z-Prepass的实际收益取决于着色成本与顶点处理成本之比。若场景中充满高细分曲面或超多顶点的几何体，额外的顶点处理Pass反而造成净性能损失。移动端GPU（如Mali、Adreno）的Tile-Based架构本身已内置高效的TBDR（Tile-Based Deferred Rendering）可见性解析，Z-Prepass在移动端几乎无益，甚至有害。

**误区3：Hi-Z与Early-Z是同一回事。**  
Early-Z是逐片元的提前深度测试，Hi-Z是基于层次化深度结构的大粒度剔除。Early-Z在所有支持硬件深度测试的GPU上均有实现；Hi-Z则是额外的硬件单元，部分低端或嵌入式GPU可能只有Early-Z而没有完整的Hi-Z层次结构。两者可同时工作，Hi-Z在图元/Tile粒度上先行剔除，Early-Z在通过Hi-Z的剩余片元上再做细粒度过滤。

## 知识关联

Early-Z优化直接建立在**深度缓冲**的概念之上——理解Z值的存储格式（线性深度 vs. 非线性NDC深度）和深度比较函数（`GL_LESS`、`GL_LEQUAL` 等）是理解Early-Z为何需要保守估计的前提。深度缓冲的精度（16位 vs. 24位 vs. 32位浮点）也直接影响Hi-Z层级的保守性误差大小。

从开发实践角度，Early-Z优化与**渲染状态排序**（State Sorting）、**遮挡剔除**（Occlusion Culling）以及**多Pass渲染架构**（Multi-Pass vs. Deferred）均有直接关联：这三个领域的技术决策都需要将Early-Z的失效条件和收益模型纳入考量，才能在实际工程中做出正确的性能权衡。