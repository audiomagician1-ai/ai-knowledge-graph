---
id: "ta-nanite"
concept: "Nanite虚拟几何"
domain: "technical-art"
subdomain: "lod-strategy"
subdomain_name: "LOD策略"
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
updated_at: 2026-03-26
---


# Nanite虚拟几何

## 概述

Nanite是Epic Games随虚幻引擎5（UE5）在2021年正式发布的虚拟化几何体系统，其核心目标是打破传统实时渲染中"多边形预算"的概念性约束。传统LOD工作流要求美术师手动制作4到8级减面网格，而Nanite允许直接导入影视级高模资产（数百万乃至数亿个三角形），由引擎在运行时自动决定每个像素对应多少几何细节。

Nanite最早在2020年UE5"Lumen in the Land of Nanite"技术演示中公开亮相，演示场景包含超过4300万个三角形的Quixel雕刻岩石资产，在PS5硬件上以实时速度运行，震动了整个游戏行业。这一演示直接宣告：过去二十年基于手工LOD链的技术美术工作流面临根本性改变。

Nanite之所以在LOD策略领域具有重要意义，在于它将几何复杂度管理从"美术手工决策"转变为"引擎算法决策"。对于技术美术而言，这意味着减少了大量重复性减面劳动，同时也带来了新的工作重心——识别哪些资产适合Nanite、哪些必须规避。

## 核心原理

### 层级簇（Hierarchical Cluster）结构

Nanite在导入阶段将静态网格体切分为若干由128个三角形组成的**簇（Cluster）**，再将相邻簇向上合并，形成树状层级结构。渲染时，引擎从根节点向下遍历这棵簇树，根据每个簇投影到屏幕的像素面积（即"屏幕尺寸误差"阈值，默认值对应约1像素的几何误差）决定在哪一层级截断细化。这与传统LOD离散切换（LOD0→LOD1→LOD2）截然不同，Nanite的细节变化是**连续且逐簇独立**的，同一个网格的不同区域可以同时处于不同精度层级。

### 软件光栅化（Software Rasterization）

对于屏幕占用极小的三角形（通常小于18像素），传统硬件光栅化管线效率极低，因为一个三角形可能覆盖不到一个完整像素。Nanite在GPU Compute Shader中自行实现了一套软件光栅化路径，专门处理这类"亚像素三角形"，而较大的三角形仍走标准硬件光栅化。这种**双轨光栅化**策略使得场景中数以亿计的微型三角形得以高效处理，这是Nanite在密集几何场景下性能优于传统管线的关键机制之一。

### 视锥与遮挡剔除

Nanite的剔除发生在簇粒度，而非整个对象粒度。引擎使用上一帧的HZB（Hierarchical Z-Buffer，层级深度缓冲）进行**两级遮挡剔除**：第一级快速排除明显不可见的簇，第二级对可能可见的簇做精确测试。这套机制让场景中有数十万个对象时，GPU每帧实际处理的三角形数量仍能控制在合理范围内，而不会随场景复杂度线性增长。

## 实际应用

**建筑与环境资产**：使用Nanite最典型的场景是导入Quixel Megascans的岩石、地形碎块、建筑构件等Sculpt高模，这些资产每个往往有200万到500万三角形，过去必须烘焙法线贴图并减面至数千三角形，现在可直接使用高模并启用Nanite（在静态网格体编辑器中勾选"Enable Nanite"即可）。

**植被密集场景**：UE5的植被系统支持Nanite实例化，大量重复的草丛、灌木、远景树木可通过Nanite自动管理细节，减少美术师维护多套植被LOD的工作量。

**ArchViz与影视预览**：从CAD或BIM软件（如Revit）导出的建筑模型通常含有数千万个未优化三角形，Nanite使这类资产无需预处理即可在UE5中实时浏览，大幅缩短了建筑可视化项目的美术准备周期。

## 常见误区

**误区一：Nanite可以取代所有LOD工作**。Nanite仅适用于**不透明的静态网格体**，动态骨骼网格体（角色、带有顶点动画的树木）、半透明材质、需要World Position Offset的材质（如布料模拟、植被随风摆动）均无法使用Nanite。因此技术美术依然需要为角色和动态植被维护传统LOD链。

**误区二：Nanite导入越高精度越好**。Nanite在导入阶段会按128三角形簇结构重新划分网格，若原始网格拓扑极度混乱（大量退化三角形、非流形几何），会导致导入时间暴增甚至失败。建议导入前用ZBrush的ZRemesher或Blender的四边形重新拓扑整理一遍，以128的倍数为目标面数导出，可显著提升导入效率。

**误区三：Nanite场景无需关注Draw Call**。Nanite确实将多边形成本压低，但每个独立Nanite对象仍会产生一定的CPU端提交开销。在移动端或低端PC上，数十万个Nanite对象的管理开销本身可能成为瓶颈，Nanite的最低推荐硬件为支持DirectX 12或Vulkan的独立显卡，目前官方明确不支持移动平台（截至UE5.3版本）。

## 知识关联

学习Nanite之前需要掌握**LOD概述**中的屏幕尺寸阈值、减面率、LOD切换距离等基础概念，因为Nanite的簇树遍历本质上是对这些概念的连续化和自动化实现——理解传统LOD的"为什么"才能看懂Nanite"如何改进"。

向前延伸，下一个重要主题是**Nanite限制**，重点研究哪些资产类型必须绕开Nanite（骨骼网格体、半透明材质、WPO材质、地形Landscape组件），以及如何在同一场景中混用Nanite与传统LOD资产，这是技术美术在实际项目中落地UE5工作流的核心判断能力。此外，Nanite与**Lumen全局光照**系统紧密配合：Nanite提供的像素级几何精度使Lumen的距离场和屏幕空间GI效果更为准确，两套系统共同构成UE5在高端平台的实时渲染基础。