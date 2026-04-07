---
id: "level-streaming-asset"
concept: "关卡流式加载"
domain: "game-engine"
subdomain: "resource-management"
subdomain_name: "资源管理"
difficulty: 3
is_milestone: false
tags: ["关卡"]

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
updated_at: 2026-03-26
---


# 关卡流式加载

## 概述

关卡流式加载（Level Streaming）是游戏引擎中将一个大型游戏世界拆分为多个子关卡（Sub-level），在运行时根据玩家位置动态加载和卸载这些子关卡的技术。这种机制让开发者无需将整个游戏世界的所有资源同时驻留在内存中，而是让世界的不同区域按需进出内存。例如在虚幻引擎5中，一张完整的开放世界地图可能被划分为数百个 512×512 米的子关卡格子，但同一时刻内存中只有玩家周边半径约 3 个格子范围内的内容处于激活状态。

该技术的雏形出现在虚幻引擎3时代（约2006年），当时开发者通过在编辑器中手动创建 Persistent Level 与多个 Streaming Level，用 `LoadStreamLevel` 和 `UnloadStreamLevel` 蓝图节点控制加载行为。虚幻引擎5的 World Partition 系统在2021年随《堡垒之夜》章节4的地图改造正式量产化，将子关卡的划分和调度逻辑完全自动化，开发者只需设定 Cell Size 和 Loading Range，引擎自动生成并管理数以千计的数据单元。

关卡流式加载对于超过 4GB 资源总量的开放世界游戏来说几乎是不可或缺的：主机端 GPU 显存通常只有 8–16 GB，如果不做流式调度，一张大型开放世界的 Static Mesh 和 Texture 总量就可以轻易超出硬件上限。

## 核心原理

### 流式单元的划分策略

关卡流式加载的基础单元在旧式 Level Streaming 中是人工划分的 `.umap` 子关卡文件，而在 World Partition 中称为 Runtime Cell（运行时单元），由引擎根据设定的 `World Partition Cell Size`（默认值通常为 12800 厘米，即 128 米）在编辑器内自动生成网格。每个 Runtime Cell 是一个独立的异步加载单位，拥有自己的包文件，包含该格子范围内所有 Actor 的序列化数据。

子关卡的空间索引依赖 **2D 网格哈希**（Spatial Hash Grid），引擎将玩家坐标 `(x, y)` 映射到格子下标 `i = floor(x / CellSize), j = floor(y / CellSize)`，从而以 O(1) 时间确定哪些单元需要加载，避免逐一遍历全部格子的开销。

### 加载状态机与优先级队列

每个流式关卡在引擎内部维护一个包含 5 个状态的状态机：`Unloaded → Loading → Loaded → MakingVisible → Visible`，以及反向的 `Visible → MakingInvisible → Unloaded`。从 `Loading` 到 `Loaded` 由异步 I/O 线程完成磁盘读取，从 `Loaded` 到 `MakingVisible` 则需要在渲染线程完成 GPU 资源上传。两个阶段分开设计，是为了让资源在完全 GPU 就绪之前不会被渲染器看到，防止出现缺少材质的白模闪烁。

优先级方面，引擎为每个待加载单元计算一个优先级分数，公式简化为：
```
Priority = (1 / Distance²) × LoadingRangeWeight × CameraFacingBonus
```
摄像机正前方的格子优先级高于身后的格子，`CameraFacingBonus` 通常在 1.0–1.5 之间，确保玩家奔跑时前方内容先于侧方和后方完成加载。

### 流式距离与内存预算

`Loading Range`（加载半径）是关卡流式加载中最直接影响内存占用的参数。以虚幻引擎5为例，在 `WorldSettings` 中可以分别设置 `Loading Range`（触发磁盘读取的距离）和 `HLod Distance`（切换到合并 Mesh 代理的距离）。当格子中心到玩家的 XY 平面距离超过 `Loading Range` 时，引擎发出卸载请求，但并非立即释放内存——引擎会维持一个 **短时缓存（Short-time Cache）**，通常持续 2–5 秒，防止玩家在区域边界反复横跳导致同一格子频繁加载卸载（即"乒乓问题"）。

## 实际应用

在《黑神话：悟空》（2024年）这类采用虚幻引擎5的开放场景游戏中，World Partition 将美术资产密集的山地场景拆分为若干 Cell，地形（Landscape）作为特殊类型以更大的 Cell Size（通常 256 米）单独划分，而密集植被（Foliage）则以独立的 HLOD 层级在远处替换为合并网格，只有玩家进入 50 米以内时才加载原始高精度模型。

在多人游戏中，服务器与每位玩家都会独立维护各自的流式加载状态。《堡垒之夜》使用 World Partition 后，服务器需要为 100 名玩家的位置集合取并集，确保任意玩家可见范围内的格子都已在服务器端加载，这一逻辑称为 **Server Streaming Source**，由专用的 `APlayerController` 自动注册到 World Partition 的加载源列表。

调试关卡流式加载时，虚幻引擎提供 `wp.Runtime.ToggleDrawRuntimeHash2D` 控制台命令，可在视口中叠加显示每个 Runtime Cell 的加载状态颜色（绿色为 Visible，黄色为 Loading，灰色为 Unloaded），帮助开发者直观识别加载空洞（Loading Hole）问题。

## 常见误区

**误区一：将 Loading Range 设置得越大越安全**
一些开发者出于担心加载空洞，将 `Loading Range` 设置到 20000 厘米（200 米）以上，导致同时激活的格子数量从约 9 个急增至约 49 个，内存占用成倍增长。正确做法是配合 HLOD 系统：远处格子用合并的低精度代理覆盖视觉，而非用高精度原始资源填满视野。

**误区二：认为子关卡加载是同步完成的**
旧版 `LoadStreamLevel` 节点若不勾选 `Make Visible After Load`，蓝图在下一帧就能拿到"已加载"的回调，但此时关卡中的 Actor 仍处于 `Loaded` 而非 `Visible` 状态，直接访问其组件可能读取到未完成 GPU 上传的资源。正确做法是监听 `OnLevelShown` 事件，而不是 `OnLevelLoaded`。

**误区三：World Partition 可以完全取代手动关卡流式**
World Partition 的自动网格化对需要精确边界控制的场景（如室内/室外切换的洞穴入口）并不理想，此时仍应使用传统的 `Level Streaming Volume` 配合手动划分的子关卡，由 Volume 边界精确触发加载，而不是依赖距离阈值。

## 知识关联

关卡流式加载建立在**流式系统**的基础异步 I/O 调度机制之上：流式系统提供了将任意资源包异步读入内存的底层能力，而关卡流式加载则在此之上增加了**空间感知的调度层**——它决定"哪些包需要加载"，流式系统负责"如何高效读取这些包"。两者分工明确：流式系统不感知玩家位置，关卡流式加载不感知磁盘布局。

关卡流式加载与 **HLOD（Hierarchical Level of Detail）** 系统紧密协作：HLOD 为尚未加载的远距离格子生成代理网格，填补视觉空洞，是关卡流式加载在视觉表现上的"补偿机制"。此外，**Data Layer**（数据层）系统可以在 World Partition 的格子之上叠加按游戏逻辑（如昼夜、剧情进度）过滤 Actor 的能力，两者共同构成了虚幻引擎5大世界管理的完整方案。