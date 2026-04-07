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
quality_tier: "S"
quality_score: 82.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
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

World Partition 是 Unreal Engine 5 中用于管理超大型开放世界的自动化流式加载系统，于 UE5.0 正式版（2022年4月发布）随《黑客帝国：觉醒》技术演示首次亮相。它取代了 UE4 时代需要手动切分子关卡的 World Composition 工作流，将整个游戏世界存储在单一的持久 World Map 中，由引擎自动负责运行时的区域加载与卸载决策。

World Partition 的核心价值在于打破了传统 Level Streaming 对关卡边界的人工依赖。在 UE4 的 World Composition 方案下，美术师必须手动规划每块子关卡的尺寸（通常为 1km×1km 或 2km×2km 的网格），并维护复杂的关卡引用关系。而 World Partition 引入了基于空间哈希网格（Spatial Hash Grid）的自动分区算法，将 Actor 按其三维坐标自动归入对应的单元格（Cell），开发者无需手动指定归属。

这套系统对《黑神话：悟空》《堡垒之夜》等采用 UE5 的大型项目至关重要。当世界尺寸达到数十平方公里时，传统方案的内存占用和加载卡顿问题会使游戏不可用，而 World Partition 可将同屏加载内存压缩至仅覆盖玩家周围若干 Cell 范围内的资产。

---

## 核心原理

### 空间哈希分区与 Cell 结构

World Partition 将世界空间划分为若干层级的正方形 Cell。默认情况下，UE5 的 Cell 边长为 **128 米**（可在 World Settings 中修改 `Cell Size` 参数）。每个 Cell 拥有独立的唯一标识符，并记录该 Cell 内所有 Actor 的引用列表。

分区的核心数据结构是 `UWorldPartitionRuntimeSpatialHash`，它在编译（Cook）阶段将 Actor 的世界坐标映射到对应 Cell，生成 `.uasset` 格式的 Cell 包文件。运行时，系统通过计算玩家所在位置到每个 Cell 中心的距离，决定是否触发流式加载，加载条件为：

```
distance(Player, Cell.Center) < Cell.LoadingRange
```

其中 `LoadingRange` 默认值为 **75 米**（针对 128 米 Cell），可按 Streaming Source 单独配置。

### Streaming Source 与加载优先级

World Partition 不依赖摄像机位置，而是依靠 **Streaming Source**（流式来源）来驱动加载。任何 Actor 都可挂载 `UWorldPartitionStreamingSourceComponent`，常见来源包括玩家 Pawn、载具、固定触发区域等。每个 Streaming Source 可配置：

- **Shape**：球形（Sphere）或盒形（Box）影响范围
- **Priority**：高优先级来源优先触发加载（0 为最高）
- **TargetGrids**：指定仅影响特定分区网格层

这套设计使多人游戏场景中不同玩家的加载区域可以独立计算，服务器端同样支持为每个玩家角色注册独立的 Streaming Source，按需维护各自的可见 Cell 集合。

### One File Per Actor（OFPA）

World Partition 强制启用 **One File Per Actor** 机制，每个 Actor 存储为独立的 `.uasset` 文件，而非传统的整个关卡文件共享一个 `.umap`。这一变化使多人协作时的版本控制冲突率大幅降低——两名设计师修改不同 Actor 不再会产生 `.umap` 文件锁定问题。

OFPA 文件存储在项目的 `Content/__ExternalActors__/` 和 `Content/__ExternalObjects__/` 目录下，路径由 Actor 的全局唯一 GUID 决定。构建时，Derived Data Cache（DDC）负责将这些分散文件打包为运行时可流式读取的 Cell 包。

### 数据层（Data Layers）

World Partition 内置 **Data Layers** 系统，允许将 Actor 分配到命名数据层（如 `DL_Day`、`DL_Night`），并在运行时通过 `UDataLayerSubsystem` 动态激活或停用整层，从而实现昼夜切换、剧情状态切换等效果，而无需卸载整个关卡。Data Layers 与空间 Cell 正交——同一 Cell 内的 Actor 可属于不同数据层，其加载由"空间条件 AND 数据层激活状态"共同决定。

---

## 实际应用

**开放世界 RPG 场景**：在一款地图尺寸为 16km×16km 的 RPG 中，使用默认 128 米 Cell 会产生约 16,384 个 Cell。配置 Streaming Source 半径为 600 米时，玩家周围同时加载约 176 个 Cell，相比加载全图节省超过 99% 的内存。

**World Partition Editor**：在编辑器的 Window → World Partition 面板中，可直观看到 Cell 网格覆盖在世界上，并可选择仅加载特定矩形区域进行编辑（Region Loading），避免打开包含数十万 Actor 的超大关卡时编辑器崩溃。

**HLOD（Hierarchical Level of Detail）集成**：World Partition 与 HLOD 系统深度集成，为每个 Cell 自动生成简化的 Proxy Mesh，当 Cell 处于未加载状态时，远处玩家看到的是该 Cell 的 HLOD 代理而非空白，消除视觉跳变。HLOD 的构建通过 `Build > Build World Partition HLODs` 命令触发。

---

## 常见误区

**误区一：World Partition 会自动处理所有 Actor 的流式加载**
实际上，被标记为 `bIsSpatiallyLoaded = false` 的 Actor 会始终加载，不受 Cell 分区影响。玩家控制器（Player Controller）、Game Mode、常驻管理器类的 Actor 默认即为非空间加载，开发者必须有意识地审查每类 Actor 的此属性设置，否则仍会出现全局常驻对象造成的内存泄漏。

**误区二：直接修改 Cell Size 越大越好**
增大 Cell Size 会减少同时激活的 Cell 数量，看似降低了系统开销，但每个 Cell 的加载粒度也随之粗化——玩家靠近边界时一次性加载的资产体积增大，反而导致明显的加载卡顿帧率波动。实践中建议 Cell Size 保持在 **128–256 米**区间，配合 HLOD 而非单纯扩大 Cell 来优化远景性能。

**误区三：World Partition 与 Level Streaming 完全不兼容**
World Partition 关卡仍然支持通过蓝图调用 `LoadStreamLevel` 加载传统子关卡，两者可共存。常见用法是将室内场景、过场动画关卡保持为传统 Level，仅室外开放区域使用 World Partition，以保留对特定关卡加载时机的精确控制。

---

## 知识关联

**前置概念——UE5 模块系统**：World Partition 的运行时管理由 `WorldPartition` 引擎模块提供，该模块在 `Engine.uplugin` 中默认启用。理解 UE5 模块的加载顺序有助于解释为何 World Partition 的初始化发生在 `GameInstance` 创建之后、第一个 World 的 `BeginPlay` 之前。`UWorldPartition` 对象作为 `UWorld` 的成员，随世界生命周期创建和销毁。

**后续概念——场景管理概述**：World Partition 是场景管理体系的物理基础层，它决定了哪些 Actor 在任意时刻处于激活状态。上层的场景管理逻辑（如触发器系统、环境查询 EQS、AI 感知系统）全部依赖 World Partition 已正确加载所需 Cell 才能正常运作。场景管理概述将在此基础上探讨如何通过 Gameplay 逻辑主动干预加载决策，例如预加载目标区域 Cell 以消除传送点的等待延迟。