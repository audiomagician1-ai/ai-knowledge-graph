---
id: "level-streaming"
concept: "关卡流式加载"
domain: "level-design"
subdomain: "level-editor"
subdomain_name: "关卡编辑器"
difficulty: 3
is_milestone: false
tags: ["技术"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 关卡流式加载

## 概述

关卡流式加载（Level Streaming）是一种将大型游戏世界拆分为多个子关卡（Sublevel），并在运行时根据玩家位置动态加载与卸载这些子关卡的技术。其本质是通过异步加载机制，让玩家在移动过程中感知不到关卡边界的存在，从而实现"无缝大世界"的游戏体验。

该技术最早在虚幻引擎3时代作为正式工具链引入，彼时开发者需手动在编辑器中划定关卡边界并配置 `LevelStreamingVolume`。进入UE4与UE5后，关卡流式加载的编辑工作流被整合进 **World Outliner** 与 **Levels面板**，并新增了基于距离的自动触发机制，大幅降低了手动配置的复杂度。

它的核心意义在于突破内存限制：一张完整的开放世界地图可能占用数十GB资产，但同一时刻玩家可见范围内只需加载其中约200MB至500MB的内容。关卡流式加载正是解决这一矛盾的直接手段，而非仅仅是优化技巧。

---

## 核心原理

### 持久关卡与子关卡的层级结构

关卡流式加载的基础是**持久关卡（Persistent Level）**加**N个流式子关卡（Streaming Sublevels）**的双层结构。持久关卡始终保持加载状态，承载全局GameMode、玩家出生点和关卡流式控制器（`ALevelStreamingVolume` Actor）。子关卡则按需加载，每个子关卡本质上是一个独立的 `.umap` 文件，与主关卡共享同一个世界空间坐标系。

在UE5编辑器中，通过菜单 **Window > Levels** 打开Levels面板，点击「+」号即可将已有的 `.umap` 文件注册为子关卡，并为其指定加载方式为 `Blueprint`（蓝图控制）或 `Always Loaded`（始终加载）。

### 两种触发机制：Volume触发与蓝图触发

**LevelStreamingVolume触发**：在持久关卡中放置 `ALevelStreamingVolume` Actor，并将其关联到指定子关卡。当玩家的相机进入该Volume时，引擎自动调用异步加载；离开后延迟卸载。该方式适合线性关卡或固定区域边界清晰的场景。Volume的 `StreamingUsage` 属性需设置为 `SVB_Loading`（仅加载）、`SVB_LoadingAndVisibility`（加载并显示）或 `SVB_BlockingOnLoad`（阻塞式加载，用于过场动画）三种之一。

**蓝图/代码触发**：通过调用 `UGameplayStatics::LoadStreamLevel` 函数（C++）或蓝图节点 `Load Stream Level`，传入关卡名称字符串、是否可见（`bMakeVisibleAfterLoad`）以及是否阻塞主线程（`bShouldBlockOnLoad`）三个核心参数。该方式适合程序化触发，例如剧情触发点或传送门切换。对应卸载函数为 `UGameplayStatics::UnloadStreamLevel`。

### 异步加载的时序与LOD过渡

加载一个子关卡分为三个阶段：**请求加载（Request）→ 内存就绪（Loaded）→ 可见（Visible）**。从请求到内存就绪通常耗时数帧至数百毫秒不等，取决于关卡资产体积。开发者常见做法是设置**预加载距离**大于**可见距离**：例如设定玩家距边界500米时开始加载，200米时才将子关卡设为可见，中间300米的缓冲确保加载完成后无闪烁。

为避免子关卡出现时产生视觉突变，通常配合**HLOD（Hierarchical Level of Detail）**使用：远处显示HLOD代理网格体，玩家靠近后流式加载完成、HLOD隐藏、真实几何体可见，过渡平滑。

---

## 实际应用

**开放世界区域划分**：以《黑神话：悟空》类型的线性开放区域为例，设计师通常将每个大场景（如"黑风山""黄风岭"）设为独立子关卡，在过渡走廊（洞穴、山道）处放置 `LevelStreamingVolume`，利用玩家穿越走廊的数秒时间完成后台加载，确保进入新区域时子关卡已完全就绪。

**多人联机场景中的注意事项**：在联机游戏中，服务器与每个客户端的流式关卡加载状态需保持同步。UE5的 `AWorldSettings` 中有 `bForceNoPrecomputedLighting` 等参数会影响联机时的关卡可见性同步，开发者应使用 `NetMode` 判断后再调用加载逻辑，避免客户端与服务器关卡状态不一致导致的碰撞丢失问题。

**编辑器工作流实践**：在Levels面板中为子关卡分配不同颜色标签，可让多位设计师并行编辑不同子关卡而不产生 `.umap` 文件冲突。这是大型项目中关卡流式加载带来的版本控制优势，也是拆分关卡的直接动机之一。

---

## 常见误区

**误区一：认为`bShouldBlockOnLoad=true`是安全的默认选项**。阻塞式加载会冻结主线程直到关卡完全加载，在资产较多时会造成数秒卡顿。该参数仅应在过场动画、Loading界面覆盖的场景中使用。日常开发中应始终使用异步加载并通过回调委托（`FLatentActionInfo`）处理加载完成事件。

**误区二：子关卡与持久关卡可以随意共享同一组Actor引用**。子关卡卸载后，其内部Actor的指针变为悬空指针（Dangling Pointer）。若持久关卡中的蓝图直接保存了对子关卡Actor的硬引用，卸载时会触发访问违规崩溃。正确做法是通过软引用（`TSoftObjectPtr`）或广播事件接口来跨关卡通信。

**误区三：关卡流式加载与World Partition可以并存随意混用**。World Partition是UE5对关卡流式加载的架构级重构，启用World Partition后传统的Levels面板子关卡工作流被禁用，两者在同一地图中互斥。在迁移项目时，必须明确当前地图使用哪种方案，不可混用。

---

## 知识关联

**前置知识**：掌握UE5关卡编辑器的基本操作（Levels面板、World Outliner、`ALevelStreamingVolume` 的放置方式）是配置关卡流式加载的必要条件。不熟悉 `.umap` 文件与持久关卡结构的学习者在操作Levels面板时会遭遇关卡层级混乱的问题。

**后续概念——World Partition**：World Partition是UE5.0正式引入的下一代流式加载系统，它将关卡流式加载中手动划定子关卡边界的工作自动化，改由引擎以固定网格单元（默认单元尺寸为`256m × 256m`）自动切分世界并管理加载。理解传统关卡流式加载的Volume触发机制与异步加载三阶段时序，是理解World Partition为何能降低配置成本、以及其内部Data Layer系统如何替代子关卡分层的直接基础。