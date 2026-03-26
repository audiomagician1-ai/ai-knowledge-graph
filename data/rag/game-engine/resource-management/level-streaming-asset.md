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
quality_tier: "B"
quality_score: 45.5
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

# 关卡流式加载

## 概述

关卡流式加载（Level Streaming）是一种将游戏世界分割为若干独立子关卡（Sub-level），并根据玩家位置在运行时动态加载或卸载这些子关卡的技术。与一次性将整个游戏世界加载进内存的传统方式不同，关卡流式加载允许引擎仅保留玩家当前区域及其邻近区域的几何体、灯光和碰撞数据在内存中，其余区域则保持卸载状态。这一机制使得开发者能够构建远超单块关卡内存上限的超大型开放世界。

该技术在虚幻引擎中经历了显著演进。虚幻引擎3时代已引入手动子关卡流式概念，开发者通过放置`Level Streaming Volume`或蓝图调用`Load Stream Level`节点来精确控制加载时机。虚幻引擎5推出的**World Partition**系统则将这一过程自动化：引擎以512×512单位（默认值，可配置）的网格单元（Cell）为最小调度粒度，根据玩家与每个Cell的距离自动触发异步加载或卸载，无需开发者手动划分子关卡边界。

关卡流式加载的重要性体现在它直接决定了游戏的可见内存占用（RSS）与I/O带宽消耗之间的平衡。若加载半径设置过大，GPU显存和系统内存会被大量非当前可见网格体占用；若加载半径过小，玩家移动时会频繁触发磁盘读取，造成明显的卡顿（Stutter）。针对PS5和Xbox Series X等次世代主机的SSD I/O速度（约5.5 GB/s raw），开发者可以使用更激进的卸载策略，这与上一世代HDD时代必须提前数秒预加载的做法截然不同。

---

## 核心原理

### 子关卡的状态机

每个流式子关卡在引擎内部维护一个严格的状态机，包含以下几个离散状态：**Unloaded（未加载）→ Loading（异步加载中）→ Loaded（已加载但不可见）→ MakingVisible（可见化处理中）→ Visible（完全可见）**，以及反向的卸载路径。Loaded状态与Visible状态的分离至关重要：关卡可以在内存中完成几何体和碰撞数据的构建，但延迟一帧或数帧再切换为可见，避免在同一帧内同时承受I/O完成、渲染命令构建和物理世界更新三重开销导致的帧率尖峰。

### World Partition的Cell调度算法

World Partition将世界坐标系划分为三维网格。每个Cell记录其包含的Actor引用列表（而非Actor本身）。引擎每帧执行`UWorldPartitionRuntimeCell::UpdateStreamingState()`，计算所有Streaming Source（默认为玩家控制的Pawn）到每个Cell中心的距离，并与该Cell配置的**加载距离（Loading Range）**和**可见距离（Visibility Range）**阈值比较。当距离小于Loading Range时，该Cell进入异步加载队列；距离超过Loading Range乘以一个Hysteresis系数（默认1.2）时，才触发卸载——这一滞回（Hysteresis）设计防止玩家在边界附近来回移动时反复触发加载/卸载抖动。

### 异步加载与主线程同步

关卡流式加载的实际文件读取发生在专用的异步加载线程（Async Loading Thread, ALT）上，与游戏逻辑主线程并行执行。在虚幻引擎中，`FlushAsyncLoading()`调用会强制主线程等待ALT完成所有待处理包（Package）的加载，这在关卡初始化时可能导致长达数百毫秒的冻结。因此，流式加载的设计原则是**永远不在运行时调用`FlushAsyncLoading()`**，而是依靠足够大的预加载半径保证异步工作总能在玩家抵达之前完成。`IsLevelVisible()`和`GetNumAsyncPackages()`等API可在运行时查询当前加载状态，供过场动画或传送逻辑使用。

### HLOD与流式加载的协作

远距离的未加载Cell不会显示为空白区域，而是由**Hierarchical LOD（HLOD）**代理网格体填充视觉空缺。World Partition会为每个Cell自动烘焙一个简化的HLOD Actor，该Actor始终保持加载状态（内存占用极低），在真实Cell几何体加载完成后无缝切换。HLOD 0层代理通常将Cell内所有网格体合并为单个网格体并降低面数至原始的5%~10%，从而实现千米级别的视距而不触发真实几何体的流式加载。

---

## 实际应用

**《堡垒之夜》大地图管理**：Epic在《堡垒之夜》Chapter 4迁移至World Partition后，将原本手动维护的数十个子关卡边界文件替换为自动Cell网格，关卡编辑器中的合并冲突（Merge Conflict）数量下降约80%，因为每个Actor独立存储为单独文件而非集中于同一关卡包。

**过场动画触发加载**：在玩家按下开门按钮后，游戏通常播放一段3~5秒的开门动画。这段时间正是预加载门后区域子关卡的窗口期。开发者在门的Blueprint中调用`Load Stream Level(LevelName, MakeVisibleAfterLoad=false)`，使目标关卡在后台完成加载但保持不可见，动画结束时再调用`Set Level Visibility(true)`，实现零感知延迟的无缝切换。

**多人游戏的服务器/客户端分离加载**：在多人游戏中，服务器需要加载所有玩家视野覆盖的Cell，而每个客户端只需加载本地玩家周围的Cell。虚幻引擎的`APlayerController`默认作为Streaming Source，但服务器端可以注册多个Streaming Source（每个在线玩家一个），确保玩家A所在区域的服务器碰撞逻辑在玩家B的客户端不可见时仍保持有效。

---

## 常见误区

**误区一：加载半径越大越安全**。许多开发者为了避免加载延迟，将World Partition的Loading Range设为极大值（如10000单位），结果导致内存中同时存在过多Cell的几何体和Actor，触发内存超限（OOM）或大量Actor的Tick调用拖慢主线程。正确做法是结合目标平台的可用内存预算，使用`World Partition > Debug > Show Cells`可视化工具监测实际加载Cell数量，并针对不同质量等级（PC高/中/低，主机/移动端）分别配置Loading Range。

**误区二：子关卡加载完成即可立即使用其中的Actor引用**。在蓝图中缓存跨子关卡的Actor引用后，若目标关卡被卸载，该引用会变为悬空指针（Stale Reference），访问时不会立即崩溃但会返回无效数据或触发断言。正确模式是在使用前调用`IsValid(ActorRef)`检查，或改用`UGameplayStatics::GetAllActorsOfClass()`在需要时动态查询，而非持久缓存。

**误区三：World Partition与手动Level Streaming可以混用**。在同一个World中同时启用World Partition并手动创建Persistent Level下的Streaming Level，会导致两套系统的Actor所有权冲突和GC引用计数异常。虚幻引擎5官方文档明确指出，启用World Partition的World应完全依赖其自动Cell调度，不应再添加传统的`ULevelStreamingKismet`实例。

---

## 知识关联

关卡流式加载建立在**流式系统**的异步I/O和包（Package）生命周期管理基础之上——理解`FAsyncLoadingThread`如何处理`.umap`包的序列化反序列化，是排查关卡加载卡顿问题的前提知识。具体而言，关卡流式加载是流式系统在"地理空间数据"这一特定类型资产上的专项应用，其调度依据是空间距离而非通用的引用计数。

在资源管理体系中，关卡流式加载与**纹理流式加载（Texture Streaming）**和**Nanite虚拟几何体**并列为三大运行时内存控制手段，但三者调度的资产类型和粒度完全不同：纹理流式加载以Mip层级为单位管理GPU显存，Nanite以Cluster为单位管理几何体细节，而关卡流式加载以整个Actor集合为单位管理世界状态（包括碰撞、AI NavMesh片段、光照数据等）。掌握这三者的协同关系，是构建次世代开放世界游戏内存预算方案的必要技能。