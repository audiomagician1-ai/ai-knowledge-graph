---
id: "world-partition"
concept: "World Partition"
domain: "level-design"
subdomain: "level-editor"
subdomain_name: "关卡编辑器"
difficulty: 3
is_milestone: false
tags: ["UE5"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 48.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.414
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

World Partition 是 Unreal Engine 5 中引入的自动化大世界管理系统，它彻底取代了 UE4 时代手动维护的 World Composition 工作流。该系统于 2021 年随 UE5 早期访问版本发布，并在 UE5.0 正式版中成为所有新项目的默认关卡管理方式。其核心设计目标是让开发者能够在单个持久关卡（Persistent Level）中构建超大型开放世界，而无需手动划分子关卡或编写流式加载逻辑。

World Partition 将整个世界的地理空间划分为若干 Cell（单元格），每个 Cell 根据玩家位置和预设的加载距离（Loading Range）自动进行流式加载和卸载。Epic Games 官方演示《古代山谷》（Valley of the Ancient）所使用的地图面积约为 4 平方千米，整个场景完全运行在 World Partition 框架下，这证明了该系统处理大规模场景的实际能力。

对于关卡设计师而言，World Partition 最重要的意义在于它消除了"关卡边界"的概念约束——所有 Actor 直接放置在一张无限大的世界地图上，系统自动负责运行时的内存管理，设计师可以专注于内容本身而非技术分层。

## 核心原理

### 网格单元格划分（Runtime Grid）

World Partition 的运行时流式加载依赖于 Runtime Grid 的概念。开发者可以在 World Settings 中配置一个或多个 Runtime Grid，每个 Grid 定义了 Cell Size（单元格尺寸，默认值为 12800 厘米，即 128 米）和 Loading Range（加载半径）。当玩家在世界中移动时，系统以玩家位置为中心，在 Loading Range 半径内的所有 Cell 会被异步加载，超出该范围的 Cell 则被卸载。

一个世界可以拥有多个优先级不同的 Runtime Grid，例如为建筑内部细节设置一个 Cell Size 较小（如 6400 cm）、Loading Range 较短的 Grid，为地形和远景设置一个 Cell Size 较大（如 25600 cm）、Loading Range 更长的 Grid，从而实现差异化的 LOD 流式策略。

### Data Layer（数据层）

Data Layer 是 World Partition 中用于逻辑分组 Actor 的机制，功能上类似于传统的子关卡（Sub-Level），但实现方式完全不同。每个 Actor 可以被分配到一个或多个 Data Layer，Data Layer 的加载状态（Loaded / Activated / Unloaded）可以通过蓝图或 C++ 在运行时动态切换，用于实现剧情触发的场景变化、日夜交替的世界状态或多人游戏的实例化区域。

Data Layer 分为两种类型：**Runtime Data Layer**（运行时动态控制）和 **Editor Data Layer**（仅在编辑器内用于组织，不影响运行时行为）。通过 `UWorldPartitionRuntimeDataLayerInstance` 类，开发者可以精确查询和控制每个 Data Layer 的当前状态。

### HLOD（分层细节层次）

World Partition 内置了 HLOD（Hierarchical Level of Detail）生成管线，专门针对大世界远景渲染优化。系统会将同一 Cell 内的静态网格体自动合并为 HLOD Mesh，当该 Cell 超出玩家的加载范围但仍在视野内时，使用低面数的 HLOD Mesh 替代原始资产渲染，避免远处区域完全消失。HLOD 的生成通过编辑器菜单 **Build > Build World Partition HLODs** 触发，生成数据存储在 `__ExternalActors__` 和 `__ExternalObjects__` 文件夹中。

## 实际应用

在开放世界 RPG 项目中，典型的 World Partition 配置方案如下：地形和植被使用 Cell Size 为 25600 cm、Loading Range 为 51200 cm 的大 Grid；建筑物和道具使用 Cell Size 为 12800 cm、Loading Range 为 25600 cm 的中 Grid；NPC 和可交互对象仅在玩家 8192 cm 以内时加载。不同区域的白天/夜晚版本 Actor 被放入各自的 Runtime Data Layer，由游戏时间系统统一调度切换。

在多人游戏服务器架构中，World Partition 支持 **Server Streaming**（服务器流式加载）模式。通过配置 `AWorldPartitionReplay` 和设置服务器端的 Streaming Source，可以让服务器仅加载有玩家活动的区域，大幅降低无人区域的服务器内存占用，这对于支持 100 名以上玩家同服的大世界 MMO 尤为关键。

## 常见误区

**误区一：认为 World Partition 会自动处理所有 Actor 的流式加载**。事实上，被标记为 `bIsSpatiallyLoaded = false` 的 Actor 始终处于加载状态，不受 Cell 网格控制。游戏模式（Game Mode）、游戏状态（Game State）等全局管理类 Actor 默认就是非空间加载的。如果开发者误将大量内容密集的 Actor（如带有复杂组件树的建筑）设置为非空间加载，将导致这些 Actor 在整个游戏过程中永久占用内存。

**误区二：World Partition 与旧版 World Composition 可以在同一项目中混用**。实际上，在 UE5 项目中启用 World Partition 后，该关卡将完全脱离 World Composition 的管理体系，两者不能共存于同一关卡。从 UE4 迁移的项目需要使用 Epic 提供的 **World Partition Converter** 工具将旧的 World Composition 关卡一次性转换，转换过程会将所有子关卡中的 Actor 合并并写入 `__ExternalActors__` 目录。

**误区三：Cell Size 越小，加载精度越高，性能越好**。Cell Size 过小会导致同一时间需要管理的 Cell 数量急剧增加，流式加载系统的调度开销反而上升。在 1000 米半径的加载范围内，Cell Size 从 128 米缩小到 32 米会使活跃 Cell 数量增加约 16 倍，显著加重 I/O 和内存分配压力。

## 知识关联

World Partition 是关卡流式加载（Level Streaming）思想的系统化延伸。传统关卡流式加载需要设计师手动在蓝图中调用 `Load Stream Level` 节点并维护关卡引用，而 World Partition 将这一流程完全自动化，底层仍然依赖 UE 的异步 Package 加载机制（`FStreamableManager`），只是触发条件由空间距离系统自动计算替代了人工调用。理解流式加载的 Package 异步加载原理有助于排查 World Partition 中出现的加载卡顿（Hitch）和 Actor 闪烁问题。

Data Layer 的运行时状态机制与 UE 的 GameplayTag 系统结合使用时效果最佳——通过 GameplayTag 驱动 Data Layer 切换，可以构建出可扩展的世界状态管理框架，避免在蓝图中硬编码大量 Data Layer 名称字符串。