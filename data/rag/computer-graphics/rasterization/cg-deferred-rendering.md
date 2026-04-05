---
id: "cg-deferred-rendering"
concept: "延迟渲染"
domain: "computer-graphics"
subdomain: "rasterization"
subdomain_name: "光栅化"
difficulty: 3
is_milestone: false
tags: ["架构"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# 延迟渲染

## 概述

延迟渲染（Deferred Rendering，又称 Deferred Shading）是一种将几何处理与光照计算分离为两个独立渲染阶段的光栅化技术。与前向渲染在每个几何 Pass 中直接计算光照不同，延迟渲染先将所有不透明物体的表面属性写入一组中间缓冲区（G-Buffer），再在屏幕空间对每个像素统一执行光照计算，从而彻底切断"几何复杂度 × 光源数量"的耦合关系。

该技术的实用化可追溯到 1988 年 Michael Deering 等人在 SIGGRAPH 上发表的论文，但因早期显卡带宽不足而长期停留于学术领域。直至 2004 年前后，随着可编程着色器与多渲染目标（MRT, Multiple Render Targets）硬件能力的普及，延迟渲染才在游戏引擎中广泛落地——《孤岛危机》（Crysis，2007）和 Unreal Engine 3 的后续版本均采用了这一架构。

延迟渲染最重要的工程价值在于：光照计算的成本从 O(几何片元数 × 光源数) 下降到 O(屏幕像素数 × 光源覆盖像素数)，使场景中存在数百乃至数千个动态光源成为可能，这是前向渲染在不引入额外剔除结构时无法达到的规模。

---

## 核心原理

### G-Buffer 架构

G-Buffer（Geometry Buffer）是延迟渲染的数据核心，由多张全屏纹理组成，每张纹理存储一类表面属性。典型的 G-Buffer 布局包含以下通道：

| 缓冲区 | 格式 | 内容 |
|---|---|---|
| GBuffer0 | RGBA8 | 漫反射颜色（RGB）+ 高光遮蔽（A） |
| GBuffer1 | RGBA8 | 世界法线（RGB，编码为 [0,1]）+ 粗糙度（A） |
| GBuffer2 | RGBA8 | 金属度（R）+ 自发光遮罩（G）+ ... |
| Depth | D24S8 | 深度 + 模板 |

在几何 Pass（G-Pass）期间，场景中的每个不透明物体只写入上述缓冲区，不执行任何光照计算。顶点着色器输出裁剪空间坐标，片元着色器输出 PBR 材质参数，整个阶段对 GPU 而言是高度并行的纯写操作。

### 光照 Pass 与光源体积

G-Pass 完成后，延迟渲染对每个光源单独执行一个屏幕空间 Pass。点光源通常以球体（Sphere Mesh）代理几何体的形式提交，聚光灯以锥体提交，从而利用深度测试和模板测试将光照计算限制在光源影响范围内的像素上，避免全屏计算的冗余开销。

光照 Pass 的着色器从 G-Buffer 中重建世界坐标（通过深度缓冲与逆视口投影矩阵：`P_world = inv(ViewProj) * vec4(uv * 2 - 1, depth, 1)`），再执行 Cook-Torrance BRDF 或其他光照模型计算，最终将结果叠加到 HDR 颜色缓冲区。

### 带宽消耗与存储开销

G-Buffer 的显存带宽是延迟渲染最显著的性能代价。以 1920×1080 分辨率、4 张 RGBA8 缓冲区为例，每帧 G-Pass 的写入量约为 1920 × 1080 × 4 × 4 ≈ **31.6 MB**，读取量在光照 Pass 中相当，总带宽压力接近 **63 MB/帧**。在移动 GPU 上，由于 TBDR（Tile-Based Deferred Rendering）架构的片上内存通常仅有 256–512 KB，经典延迟渲染需要特别适配，否则带宽瓶颈将严重拖累帧率。

---

## 实际应用

**大规模动态光源场景：** 《战地 3》（Battlefield 3，2011，Frostbite 2 引擎）使用延迟渲染支持同屏超过 **1000 个** 动态点光源，这在前向渲染下需要对每个光源进行额外剔除 Pass 才能达到接近性能。

**Unreal Engine 的 GBuffer 扩展：** UE4/UE5 将 G-Buffer 扩展至最多 **5 张** MRT 附件，额外存储次表面颜色、次表面轮廓 ID 和各向异性方向向量，以支持皮肤、毛发等复杂材质的延迟光照计算。

**模板光照优化：** 对于点光源，渲染引擎通常分两步绘制球体代理：第一步仅写入模板缓冲（标记光源影响像素），第二步利用模板测试跳过不受影响的像素再执行光照计算，将每个点光源的像素着色调用量减少约 30–60%（取决于场景遮挡情况）。

---

## 常见误区

**误区一：延迟渲染天然支持透明物体**
延迟渲染的 G-Pass 只能处理不透明几何体，因为 G-Buffer 每个像素只能存储一层表面属性，透明物体的混合需要正确的前后顺序和 Alpha 合成，这与 G-Buffer 的单层存储模型根本冲突。实际引擎的处理方式是：透明物体在延迟光照完成后，以**前向渲染回退（Forward Pass）**单独绘制并叠加到最终颜色缓冲。

**误区二：G-Buffer 越多精度越高越好**
增加 G-Buffer 通道数量或提升精度（如从 RGBA8 升级到 RGBA16F）会成倍增加带宽压力，并非越高越好。例如将法线缓冲从 RGBA8 升级到 RG16F（使用 Octahedron 编码压缩法线）反而可以在更小占用下获得更高的法线精度，同时将该缓冲的带宽降低约 50%。工程中需要根据实际材质需求精细设计 G-Buffer 布局。

**误区三：延迟渲染等同于延迟光照（Deferred Lighting）**
延迟光照（又称 Light Pre-Pass）是延迟渲染的变体：它只在 G-Buffer 中存储法线和深度，光照 Pass 仅输出漫反射和高光辐照度，最后再做一次几何 Pass 将材质颜色与辐照度合并。这一流程支持更丰富的材质多样性（因为材质计算在最终 Pass 中执行），但代价是需要两次完整的几何 Pass，GPU 绘制调用（Draw Call）数量翻倍。

---

## 知识关联

**前序概念——前向渲染：** 前向渲染中每个片元直接访问光源列表并累加光照，光照复杂度为 O(片元 × 光源)。延迟渲染正是针对这一耦合的直接改进，理解前向渲染中 per-light shader permutation 的膨胀问题，有助于把握延迟渲染拆分阶段设计的动机。

**后续概念——Forward+（分块前向渲染）：** Forward+ 通过计算着色器将屏幕划分为 16×16 像素的 Tile 并为每个 Tile 建立光源列表，在前向渲染框架内实现接近延迟渲染的光源扩展性，同时天然支持透明物体和 MSAA，是对延迟渲染透明度缺陷的直接回应。

**后续概念——可见性缓冲（Visibility Buffer）：** 可见性缓冲将 G-Buffer 进一步压缩为仅存储三角形 ID 和重心坐标，表面属性在光照 Pass 中按需从顶点缓冲区动态获取。这一架构将带宽消耗从 G-Buffer 的 30+ MB/帧降至约 8 MB/帧，是延迟渲染在高分辨率与复杂材质场景下的现代演进方向。

**后续概念——屏幕空间反射（SSR）：** SSR 的光线步进完全依赖 G-Buffer 中已有的深度和法线数据，是延迟渲染 G-Buffer 副产物的典型二次利用场景，也解释了为何 SSR 在前向渲染管线中实现成本更高。