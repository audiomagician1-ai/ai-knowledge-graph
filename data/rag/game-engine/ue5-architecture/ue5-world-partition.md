---
id: "ue5-world-partition"
concept: "World Partition"
domain: "game-engine"
subdomain: "ue5-architecture"
subdomain_name: "UE5架构"
difficulty: 3
is_milestone: false
tags: ["大世界"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 50.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# World Partition（世界分区）

## 概述

World Partition 是 Unreal Engine 5 引入的大世界关卡管理系统，于 2021 年随 UE5 早期访问版本正式发布，取代了 UE4 时代的 World Composition 方案。其核心机制是将一个巨大的持久关卡（Persistent Level）在编辑器层面自动划分为若干空间单元（Cell），并在运行时根据玩家位置动态流式加载和卸载这些单元，从而支持理论上无限延伸的开放世界地图。

在 UE4 的 World Composition 中，关卡设计师必须手动创建子关卡（Sub-Level）并指定其加载规则，跨关卡协作极易产生资源冲突。World Partition 打破了这一限制：所有 Actor 统一存放在一张地图文件里，编辑器通过 `HLOD`（Hierarchical Level of Detail）和 `Data Layer` 系统自动管理可见性与加载状态，使得数十人团队可以同时编辑同一张超大地图而无需手动分包。

World Partition 对《黑神话：悟空》《堡垒之夜 Chapter 4》等大型开放世界项目的地图制作流程产生了直接影响。理解这一系统能帮助开发者掌握 UE5 大世界项目的性能瓶颈定位方法，以及流式加载策略的调参思路。

---

## 核心原理

### 空间哈希分区（Spatial Hash Grid）

World Partition 在底层使用空间哈希网格将世界坐标系划分为固定尺寸的方形单元（Cell）。默认 Cell 大小为 **12800 × 12800 厘米**（即 128 米 × 128 米，与 UE 的 1cm = 1unit 约定一致）。每个 Cell 对应一组可独立加载的 Actor 集合。当玩家的 `World Partition Streaming Source`（通常附加在 PlayerController 或摄像机上）进入某个 Cell 的加载半径时，引擎发出异步 I/O 请求，将对应 Cell 的 Actor 数据从磁盘读入内存并完成序列化实例化。

加载距离由 `Streaming Source Priority` 和每个 Actor 的 `Runtime Grid` 属性共同决定。例如，将地形 Actor 的 `Runtime Grid` 设置为 `MainGrid`（加载半径 25600cm），将小道具设置为 `SmallGrid`（加载半径 6400cm），可以实现地形先于细节物件加载的分层策略。

### 数据层（Data Layer）

Data Layer 是 World Partition 独有的逻辑分组机制，与物理空间分区正交。一个 Actor 可以同时属于某个空间 Cell 和某个 Data Layer。Data Layer 有两种类型：

- **Editor Data Layer**：仅在编辑器内可见，用于隔离白盒阶段资产与最终资产。
- **Runtime Data Layer**：在运行时可通过蓝图或 C++ 调用 `UDataLayerSubsystem::SetDataLayerRuntimeState()` 切换加载状态，支持 `Unloaded → Loaded → Activated` 三个状态转换。

这使得日夜切换、剧情触发场景变更等需求无需额外关卡流关卡逻辑，直接通过 Data Layer 状态机驱动。

### HLOD 生成与层级管理

World Partition 的 HLOD 系统在烘焙时自动将远处 Cell 的 Static Mesh 合并为低多边形代理网格（Proxy Mesh），并以 Nanite Cluster 格式存储（UE5.1+ 起支持 Nanite HLOD）。每一个 HLOD Layer 对应一个降低细节等级的距离阈值，开发者在 `World Settings → World Partition → HLOD Layers` 中配置。关卡烘焙时，`WorldPartitionHLODsBuilder` 命令行工具（`UnrealEditor-Cmd.exe -run=WorldPartitionBuilderCommandlet`）会遍历所有 Cell 并批量生成 HLOD 资产，这一步骤在大型关卡中通常需要数小时，因此推荐接入 CI/CD 流水线定期执行。

---

## 实际应用

**开放世界地形流加载调优**：在一张 16km × 16km 的开放世界地图中，若将所有植被 Actor 保留在默认 `MainGrid` 下，会导致玩家周围同时存在大量实例化静态网格体（ISMC），引发渲染线程瓶颈。正确做法是将植被的 `Runtime Grid` 改为自定义小格（Cell Size 3200cm，加载半径 9600cm），并开启 `bIsSpatiallyLoaded = true`，使植被仅在近距离才实例化。

**多人协作大地图编辑**：团队使用 **One File Per Actor（OFPA）** 功能——该功能在 World Partition 关卡中默认启用，每个 Actor 的数据存储为 `__ExternalActors__` 目录下的独立 `.uasset` 文件。这样版本控制系统（如 Perforce 或 Git LFS）可以对单个 Actor 进行检出与合并，彻底消除多人同时编辑同一关卡文件的二进制冲突问题。

**运行时动态场景切换**：在主线剧情触发后，通过 `UDataLayerSubsystem::SetDataLayerRuntimeState(DestructionLayer, EDataLayerRuntimeState::Activated)` 将标记为"战后废墟"的 Data Layer 激活，同时将"战前完好"Data Layer 设为 `Unloaded`，实现不跳转关卡的场景状态切换，过渡延迟通常低于 200ms（取决于 Cell 内 Actor 数量）。

---

## 常见误区

**误区一：World Partition 会自动解决所有性能问题**

World Partition 只负责 Actor 的流式加载与卸载，不优化已加载 Actor 的渲染开销。若单个 Cell 内包含数千个高面数 Static Mesh 且未配置 Nanite，运行时仍会产生严重的 Draw Call 压力。World Partition 减少的是同时在内存中的 Actor 总量，而非单帧渲染代价。

**误区二：Data Layer 等同于 UE4 的 Level Streaming**

UE4 的 Level Streaming 以整个子关卡为单位进行加载，粒度粗且无法与空间分区交叉。Data Layer 是纯逻辑标签，可与任意空间 Cell 组合，且状态转换是增量式的（逐 Actor 异步激活），不会触发全关卡序列化。用 Level Streaming 的思维设计 Data Layer 切换逻辑会导致过度使用 `Activated` 状态，引发不必要的 CPU 序列化开销。

**误区三：OFPA 模式下合并关卡仍需人工处理冲突**

部分开发者误以为 OFPA 只是文件拆分，合并时仍需手动解决。实际上，只要不同开发者修改的是不同 Actor，各自的 `.uasset` 文件互不干扰，版本控制系统可以直接合并目录级变更，无需人工介入。冲突仅发生在多人修改同一 Actor 或修改关卡元数据文件（`*.umap`）的情况下。

---

## 知识关联

**前置概念——UE5 模块系统**：World Partition 的流式加载逻辑封装在 `Engine` 模块的 `WorldPartition` 子目录中（路径：`Engine/Source/Runtime/Engine/Private/WorldPartition/`），其 `UWorldPartition` 类继承自 `UObject`，并通过 `FWorldPartitionStreamingQuerySource` 结构体与引擎 Tick 系统对接。了解 UE5 模块的编译边界有助于在自定义插件中扩展 `IWorldPartitionStreamingSource` 接口。

**后续概念——场景管理概述**：World Partition 提供了关卡内 Actor 的空间索引与异步加载基础设施，而场景管理概述会在此基础上讨论如何协调 World Partition、Chaos Physics 物理场、Niagara 粒子系统与 PCG（Procedural Content Generation）之间的加载时序与内存预算分配，形成完整的大世界场景生命周期管理体系。