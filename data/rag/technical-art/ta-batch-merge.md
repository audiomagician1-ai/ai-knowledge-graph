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
quality_tier: "B"
quality_score: 45.2
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
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

网格合并（Mesh Merging）是将场景中多个独立的静态网格对象在几何层面合并为单一网格的技术，目的是将多个 Draw Call 压缩为一次 Draw Call，从而降低 CPU 向 GPU 提交渲染命令的频率。与材质合批（Material Batching）不同，网格合并发生在顶点/索引缓冲区层面，最终产物是一个拥有更多顶点但绘制次数更少的新网格资产。

这一技术在实时渲染管线中出现较早，DirectX 9 时代的开发者就已手动在 DCC 软件（如 3ds Max）中合并模型以节省 API 调用。Unreal Engine 4 在 2014 年引入 Merge Actors 工具，UE5 则进一步集成了 HLOD（Hierarchical Level of Detail）系统，将网格合并与细节层级管理结合，使超大型开放世界场景的优化成为可能。

网格合并对 CPU-bound 场景的改善尤为显著。当场景中存在数百个仅使用同一材质的小型装饰物时，每个物体在未合并状态下对应至少一次 Draw Call；合并后整批物体只占用一次 Draw Call，CPU 每帧节省的状态切换开销可使帧时间下降 10%–30%，具体收益取决于原始 Draw Call 数量与目标硬件。

---

## 核心原理

### 顶点缓冲区合并与坐标变换

合并操作的本质是将各子网格的顶点坐标从其本地空间（Local Space）变换到统一的世界空间或合并基准空间，再写入同一个顶点缓冲区（Vertex Buffer）。设有 N 个子网格，第 i 个子网格的顶点位置为 **v**，其世界矩阵为 M_i，则合并后该顶点的新坐标为：

> **v'** = M_i · **v**

合并完成后，这个新网格不再携带独立的变换矩阵，即 **失去了单独移动某个子对象的能力**。这是网格合并区别于 GPU Instancing 的根本特征——GPU Instancing 保留各实例的变换数据，网格合并则将变换"烤"进顶点坐标。

### 材质槽与子网格分段

合并时若所有子网格共享同一材质，最终产物为单材质槽网格，Draw Call 降至 1 次。若子网格使用不同材质，合并工具（如 UE 的 Merge Actors）会按材质分段生成多个 Sub-Mesh Section，每个 Section 对应一次 Draw Call。因此，**合并前务必统一材质**，否则合并后的 Draw Call 数量等于合并前各不同材质的数量之和，并不会减少。实践中常配合 Texture Atlas（纹理图集）将多张贴图打包为一张，再合并网格，才能真正将 Draw Call 压至 1。

### HLOD（分层细节层级）合并

HLOD 是网格合并的层级化扩展，核心思路是：当相机距离某个簇（Cluster）超过设定阈值时，该簇内所有原始网格被替换为预先生成的低多边形合并代理网格（Proxy Mesh）。UE5 的 HLOD 系统以 World Partition 为基础，将场景划分为若干 HLOD Layer，每层可设置独立的 Screen Size 阈值（默认值约为 0.15，即占屏幕面积 15%）和简化率。代理网格通过 Simplygon 或 UE 内置的 Mesh Reduction 算法生成，顶点数通常为原始簇的 10%–30%。相机拉远时，数百个高精度网格瞬间被一个几千三角形的代理网格替代，Draw Call 与顶点负载同时降低。

---

## 实际应用

**UE5 Merge Actors 工具**：在编辑器中选中多个 StaticMeshActor，执行 Window → Developer Tools → Merge Actors，可选择生成合并网格资产并保存到内容浏览器。合并后的 Actor 替换原始 Actor，原始 Actor 可选择性删除。对于城市场景中数百个路灯底座、路牌支架等重复装饰物，此操作可将相关 Draw Call 从 300+ 压缩至个位数。

**Unity 静态合批（Static Batching）**：在 Unity 中将 GameObject 标记为 Static 后，引擎在构建时（Build Time）或运行时调用 `StaticBatchingUtility.Combine()` 合并共享材质的网格。合并后数据存储在一个大型 Combined Mesh 中，运行期只提交一次顶点缓冲区上传，渲染时按 Sub-Mesh 索引范围分段提交，共享材质的部分合并为单次 Draw Call。需要注意的是，Static Batching 会显著增加内存占用，因为每个合批实例的顶点数据均被复制而非共享。

**手游场景优化案例**：某移动端 MMORPG 的城镇场景包含 1200 个静态道具，优化前 Draw Call 为 980 次（部分对象已做实例化）。将所有道具按材质归类后使用 4 张 2048×2048 Texture Atlas 合图，再执行网格合并，最终 Draw Call 降至 47 次，该帧 CPU 渲染线程耗时从 12.3ms 降至 3.1ms，在目标机型（骁龙 778G）上成功达到稳定 60fps 目标。

---

## 常见误区

**误区一：网格合并总是越多越好**

合并会导致合并体的包围盒（Bounding Box）膨胀为所有子网格的联合包围盒。当摄像机视锥体（Frustum）仅能看到合并体的一小部分时，GPU 仍然会处理整个合并网格中落入视锥体的三角形，Occlusion Culling 也因巨大包围盒难以剔除。因此，跨越场景不同区域、空间上不连续的网格不应合并在一起；合理的做法是按空间局部性（通常以 10m–20m 为一个合并单元格）划分合并范围。

**误区二：合并网格与 GPU Instancing 效果相同，可以互相替代**

GPU Instancing 通过一次 Draw Call 渲染同一网格的多个实例，每个实例保留独立变换矩阵，单个实例可被独立剔除（Per-Instance Culling）；而网格合并将多个不同网格的顶点拼合后失去各自的 Transform，无法对单个原始对象做可见性剔除或动态移动。对于需要运行时动态出现/消失的对象，应优先选择 Instancing；对于完全静态、永不改变的装饰物，网格合并更彻底地减少内存中的对象数量。

**误区三：合并后必然减少内存占用**

Unity Static Batching 会复制每个实例的顶点数据，100 个相同网格（每个 1000 顶点）合并后产生 100,000 顶点的 Combined Mesh，而 GPU Instancing 情况下 GPU 内存中只有原始的 1,000 顶点。在重复实例极多的场景（如森林中的同款树木），Static Batching 的内存代价可能高于 Instancing 方案数十倍。

---

## 知识关联

网格合并是在掌握 **Draw Call 优化**原理之后自然延伸出的几何层面手段——理解了 CPU 每次提交绘制命令的开销，才能理解合并为何有效。网格合并与 **纹理图集（Texture Atlas）** 高度配合：图集解决材质统一问题，合并解决对象数量问题，两者协同才能将 Draw Call 压至最低。合并后的大型网格如需按距离切换精度，则进入 **LOD（Level of Detail）** 系统的范畴；HLOD 正是将网格合并与多级 LOD 结合的进阶形态，是大型开放世界项目性能优化的标准工具链。