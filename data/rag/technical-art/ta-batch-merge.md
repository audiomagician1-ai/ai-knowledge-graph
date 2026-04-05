---
id: "ta-batch-merge"
concept: "网格合并"
domain: "technical-art"
subdomain: "perf-optimization"
subdomain_name: "性能优化"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 73.0
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


# 网格合并

## 概述

网格合并（Mesh Merging）是技术美术性能优化中一种通过将多个独立几何体合并为单一网格来减少场景中物体数量的技术手段。其核心目标是降低 CPU 向 GPU 提交绘制命令的次数——即 Draw Call 数量——从而减轻渲染管线的 CPU 瓶颈压力。合并后的网格在一次 Draw Call 中完成绘制，而非对每个子物体单独发起绘制请求。

网格合并的概念随着实时渲染对性能要求的提升而系统化。在 Unity 早期版本（Unity 3.x 时代）中，开发者已通过手动调用 `CombineMeshes()` API 实现运行时合并；而虚幻引擎（Unreal Engine）则在 4.14 版本中正式引入 Merge Actors 工具窗口，将这一流程工具化。现代 3A 游戏场景动辄包含数万个静态物体，若不进行合并优化，Draw Call 数量可轻易突破数千次，造成明显帧率下降。

网格合并之所以重要，在于它直接解决了小物体密集场景的渲染效率问题。一个包含 200 块独立砖块的墙面，合并后只需 1 次 Draw Call；未合并时则需要 200 次，即便这 200 块砖使用相同材质球，仍会产生 200 条独立的渲染状态切换指令。

---

## 核心原理

### 静态合批（Static Batching）

静态合批是引擎层面自动执行的网格合并策略，仅适用于标记为 **Static** 的游戏对象。在 Unity 中，勾选物体的 "Static" 标记后，引擎会在构建时（Build Time）或场景加载时将这些物体的顶点数据合并到一个共享顶点缓冲区（Vertex Buffer）中。运行时 GPU 从单一缓冲区读取数据，CPU 只需提交少量批次绘制命令。

静态合批的限制：要求参与合批的所有物体共享**完全相同的材质实例**（Material Instance），若材质参数存在任何差异则无法合批。此外 Unity 的静态合批会保留每个子网格的独立索引缓冲区（Index Buffer），因此内存占用会随物体数量线性增长——100 个使用相同网格的石头，合批后内存中存在 100 份顶点数据副本，而非共享 1 份。这与 GPU Instancing 的内存策略形成对比。

### HLOD（Hierarchical Level of Detail）

HLOD 是一种针对大型开放世界场景的分层网格合并方案，由虚幻引擎 4 引入并在 UE5 的 World Partition 系统中深度集成。其工作原理是：将空间上相邻的多个静态网格体在离线阶段（Editor 构建时）合并为一个低精度代理网格（Proxy Mesh），当摄像机距离超过设定阈值时，用这个代理网格替代原始细节网格组合，从而同时减少 Draw Call 和顶点数量。

HLOD 的层级结构通常设置为 2～3 层：第 0 层（HLOD0）对应最高细节的原始网格；第 1 层（HLOD1）为中距离代理网格，面数通常是原始总面数的 10%～30%；第 2 层（HLOD2）则为远距离极简代理，面数可低至原始的 1%。UE5 的 Nanite 系统虽然改变了传统 LOD 的部分需求，但 HLOD 在非 Nanite 物体（如植被、透明物体）上仍不可或缺。

### Merge Actors 工具（虚幻引擎）

虚幻引擎的 Merge Actors 工具（位于 Window > Developer Tools > Merge Actors）提供三种合并模式：**Merge**（完整合并为单一静态网格）、**Batch**（按材质分组合批）以及 **Approximate**（生成代理网格，类似 HLOD 代理）。执行 Merge 操作后，工具会将选中的多个 Static Mesh Actor 烘焙为一个新的 `.uasset` 静态网格资产并保存到内容浏览器，原始物体可选择是否保留。

Merge 过程中会自动进行 UV 图集化（UV Atlasing）：将各个子网格的纹理坐标重新布局到同一张合并纹理中，确保合并后的物体仍可使用单一材质球渲染，从而满足 Draw Call 合并的前提条件。合并纹理的分辨率上限默认为 4096×4096。

---

## 实际应用

**场景：城市街道场景优化**
一条游戏街道场景中包含：路灯 80 个、垃圾桶 60 个、电线杆 40 个、路障 120 个，共 300 个静态物体，产生约 300 次 Draw Call（假设各类型共享材质）。通过按类型分别执行 Merge Actors，可将其合并为 4 个网格，Draw Call 降至 4 次，CPU 渲染时间理论上减少约 98%。

**场景：手机游戏地形装饰物**
在面向移动端（目标帧率 60fps，Draw Call 预算通常控制在 100 以内）的游戏中，地面散布的石头、树根、杂草等装饰物是 Draw Call 超标的常见元凶。通过将同一区块内的同类装饰物在 Unity 中调用 `Mesh.CombineMeshes(CombineInstance[] combine, bool mergeSubMeshes, bool useMatrices)` 运行时合并，可将单个区块的装饰物 Draw Call 从数十次压缩至 1～3 次。

**注意点：合并物体失去独立剔除能力。** 合并前，遮挡剔除（Occlusion Culling）可以单独剔除被遮挡的子物体；合并后，只要合并网格的包围盒（Bounding Box）未被完全遮挡，整个合并体都会被提交渲染。因此不应将分布范围过大的物体合并为一个网格，通常建议合并范围控制在 10～20 米以内。

---

## 常见误区

**误区一：合并后材质数量可以不同**
许多初学者认为只要执行了合并操作，Draw Call 就一定会减少。实际上，若合并后的网格包含多个 Sub-Mesh（子网格材质槽），每个 Sub-Mesh 仍会触发独立的 Draw Call。只有将所有子网格烘焙为单一材质（通过 UV 图集合并纹理）才能真正实现 1 次 Draw Call 渲染。Merge Actors 的 "Merge Materials" 选项正是解决这一问题的关键开关。

**误区二：网格合并与 GPU Instancing 可以随意互换**
网格合并适用于**空间上位置不重复**的静态物体集合；GPU Instancing 适用于**同一网格在不同位置大量重复出现**的情形（如树木、草地）。若对 500 棵形态完全相同的树使用 Merge Actors 合并，会产生 500 倍顶点数据的单一超大网格，内存消耗灾难性增加，而 GPU Instancing 只需 1 份顶点数据加 500 条变换矩阵记录。两者解决的场景完全不同，不可混用。

**误区三：合并越多越好**
将整个场景合并为一个超级网格会导致：① 遮挡剔除完全失效，摄像机始终渲染场景中所有几何体；② 顶点数量极大，超出 GPU 单次绘制的高效处理范围（一般建议单个合并网格顶点数不超过 65535，即 16 位索引上限）；③ 物体无法再单独进行动画、物理或交互。网格合并需要在 Draw Call 数量与剔除效率之间寻找平衡点。

---

## 知识关联

**前置概念**：网格合并的价值建立在对 Draw Call 工作机制的理解之上。Draw Call 优化揭示了 CPU 批次提交的开销本质——每次 Draw Call 涉及状态设置、命令录制、驱动验证等固定开销，与三角面数量无关。正是这一特性决定了"将 100 个小物体合并为 1 个"能显著提升性能，即便合并前后总面数相同。

**关联技术**：网格合并通常与 LOD（Level of Detail）系统配合使用——先对单个网格设置 LOD 减面策略，再对相邻的多个低 LOD 网格执行合并，以获得距离感知的最优渲染开销。HLOD 本质上就是这两种技术的系统化整合方案。此外，合并过程中涉及的 UV 图集化与纹理烘焙，与光照贴图（Lightmap）的 UV 通道管理密切相关，需要为合并网格预留足够的 Lightmap UV 空间（通常在第 2 UV 通道 UV1 中单独保存）。