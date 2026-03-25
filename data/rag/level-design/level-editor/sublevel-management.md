---
id: "sublevel-management"
concept: "子关卡管理"
domain: "level-design"
subdomain: "level-editor"
subdomain_name: "关卡编辑器"
difficulty: 2
is_milestone: false
tags: ["管理"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 44.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.433
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---




# 子关卡管理

## 概述

子关卡管理（Sub-level Management）是UE5关卡编辑器中将单个持久关卡（Persistent Level）拆分为多个可独立加载的子关卡（Sub-level）并对其进行组织、控制加载状态与协作权限的工作流体系。其核心数据结构体现在 `.umap` 文件中，每个子关卡本质上是一个独立的地图文件，通过持久关卡的 World Composition 或 Level Streaming 机制动态关联。

子关卡概念最早在UE3时代以"Level Streaming"名义引入，目的是突破单关卡Actor数量上限以及解决大世界加载瓶颈。进入UE5之后，World Partition系统在一定程度上自动化了流式加载，但对于需要精细手工控制加载边界、团队多人协作或保留UE4工作流的项目，传统子关卡管理依然是首选方案。

在实际项目中，子关卡管理的价值体现在三个层面：其一是**内存控制**，可按需加载局部场景资产；其二是**协作隔离**，不同美术或关卡设计师各自持有独立的 `.umap` 文件，避免多人编辑同一文件时的版本冲突；其三是**逻辑分层**，例如将地形、植被、音效触发体、Gameplay Actor分别放置于独立子关卡，便于按类别管理与调试。

---

## 核心原理

### 子关卡的层级结构与 Levels 面板

UE5编辑器中通过菜单 **Window → Levels** 打开关卡管理面板。面板以树状列表显示持久关卡及其挂载的所有子关卡。每个子关卡条目左侧有一个眼睛图标（控制编辑器视口可见性）和一把锁图标（控制写入权限）。持久关卡始终常驻内存，子关卡可被标记为以下四种流式加载类型：

- **Always Loaded**：随持久关卡同步加载，不可在运行时卸载；
- **Blueprint**：由蓝图或 `UGameplayStatics::LoadStreamLevel()` 函数手动触发加载；
- **Level Streaming Volume**：通过放置在场景中的 `ALevelStreamingVolume` Actor，当玩家摄像机进入/离开体积时自动触发加载或卸载；
- **World Partition**（UE5新增）：由系统自动管理，通常不与传统子关卡混用。

子关卡在 `UWorld` 对象内部以 `TArray<ULevelStreaming*>` 形式存储，每个 `ULevelStreaming` 实例维护自身的加载状态机，状态值包括 `Unloaded`、`Loading`、`Loaded`、`MakingVisible`、`LoadedVisible` 和 `Unloading`，状态转换在帧间异步完成。

### 子关卡的加载与卸载流程

调用 `UGameplayStatics::LoadStreamLevel(WorldContextObject, LevelName, bMakeVisibleAfterLoad, bShouldBlockOnLoad, LatentInfo)` 时，引擎会在后台线程启动 `.umap` 包的异步反序列化，完成后在主线程执行 Actor 的 `BeginPlay` 并触发 `OnLevelLoaded` 委托。参数 `bShouldBlockOnLoad` 若设为 `true`，则在同一帧阻塞完成加载，适用于过场动画切换等场景，但会造成明显卡顿。

对应的卸载函数为 `UGameplayStatics::UnloadStreamLevel()`，该调用不会立即释放内存，引擎会等待当前帧渲染完毕、确认无引用残留后，在垃圾回收（GC）周期内才真正释放资产。因此在卸载后立刻查询子关卡状态仍可能返回 `Loaded`，需监听 `OnLevelUnloaded` 委托而非轮询。

### 协作权限控制：Checkout 与锁定机制

当项目接入 Perforce 或 Git LFS 等版本控制系统后，Levels 面板中每个子关卡右键菜单会出现 **Check Out** 选项，成功 Checkout 后锁图标变为解锁状态，该设计师方可移动或修改该子关卡内的 Actor。未被 Checkout 的子关卡默认处于只读状态，尝试修改时编辑器会弹出警告"Level is read-only"并拒绝写入。

在无版本控制的本地协作场景中，可在子关卡右键菜单选择 **Make Current Level** 将其设为活跃编辑目标，再通过 **Lock** 功能手动锁定其他子关卡，防止误操作。活跃子关卡的名称会以**粗体**显示在 Levels 面板中，新放置的 Actor 将自动归属于当前活跃子关卡。

---

## 实际应用

**开放世界场景分区加载**：以一张2km×2km的城镇地图为例，可将地图划分为16个500m×500m的网格子关卡，配合 `ALevelStreamingVolume` 设置触发半径为750m，确保玩家移动时周围3×3格子区域始终保持加载，其余区域卸载。这种方案在UE4时代被广泛采用，在UE5中仍适用于不开启World Partition的项目。

**多人协作分层管理**：在一个有5名关卡设计师的项目中，通常按以下子关卡命名约定分工：`L_Town_Terrain`（地形负责人）、`L_Town_Props`（场景美术）、`L_Town_Lighting`（灯光美术）、`L_Town_Gameplay`（关卡设计师）、`L_Town_Audio`（音频设计师）。每个子关卡单独提交Perforce，日常合并冲突率可降低至接近零。

**编辑器调试用临时子关卡**：开发阶段可创建名为 `L_Debug_Overlay` 的专用子关卡，将碰撞可视化辅助线、导航网格可视化Actor统一放入其中，在打包发布前将该子关卡设为 `Always Loaded = false` 并从持久关卡引用中移除，实现零侵入式调试资产管理。

---

## 常见误区

**误区一：认为子关卡坐标是独立的**
部分初学者以为每个子关卡拥有自己的本地坐标系，实际上所有子关卡共享同一个世界空间（World Space），子关卡内的Actor坐标均为世界坐标。`ULevelStreaming` 提供了 `LevelTransform` 属性可整体偏移子关卡，但这是平移整个关卡的工具，不代表子关卡有独立坐标原点。误用此属性会导致碰撞与视觉位置错位。

**误区二：Always Loaded 等同于直接放入持久关卡**
将子关卡设为 `Always Loaded` 后，该子关卡仍然以独立 `.umap` 文件存在，在编辑器协作、版本控制和内容分析（Reference Viewer）层面依然与持久关卡保持分离。与直接将Actor放入持久关卡相比，`Always Loaded` 子关卡的Actor在运行时略晚一帧完成初始化，若在 `GameMode::InitGame` 中直接查询这些Actor可能返回空指针。

**误区三：子关卡卸载后资产立即释放**
调用 `UnloadStreamLevel` 后立刻检查内存，会发现显存和内存占用并未下降。UE5的资产引用计数机制要求垃圾回收运行后才释放纹理和网格体。若需要强制立即释放，需在卸载委托触发后手动调用 `GEngine->ForceGarbageCollection(true)`，但这会导致当帧卡顿，生产环境中应谨慎使用。

---

## 知识关联

**前置知识**：使用子关卡管理需要熟悉UE5关卡编辑器的基本操作，包括Outliner面板中Actor的层级管理、持久关卡的创建流程，以及 `.umap` 与 `.uasset` 文件在Content Browser中的组织方式。没有这些基础，难以理解为何子关卡之间的Actor引用（Cross-Level Reference）需要特别注意——跨关卡引用会导致被引用关卡无法单独卸载，形成隐式依赖。

**延伸方向**：掌握子关卡管理后，可进一步学习UE5的 **World Partition** 系统——它本质上是对传统子关卡流式加载的自动化封装，以HLOD（Hierarchical Level of Detail）和Data Layers替代了手工划分的子关卡网格。此外，**Level Instance**（关卡实例）特性允许将子关卡以实例化方式多次放置于场景中，是传统子关卡管理体系的重要补充，适用于可复用的模块化场景单元（如重复出现的房间或关卡段落）。