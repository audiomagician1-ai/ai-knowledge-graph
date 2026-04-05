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
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
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

World Partition 是 Unreal Engine 5 引入的自动化大世界管理系统，于 UE5.0（2022年4月）正式发布，取代了此前需要手动管理子关卡的 World Composition 工作流。它将整个游戏世界存储在**单一持久关卡**中，并通过运行时自动的单元格（Cell）加载卸载机制，使开发者无需手动划分子关卡即可构建超大型开放世界。

World Partition 的设计动机来自于 AAA 开放世界项目（如《堡垒之夜》Chapter 4 和《黑神话：悟空》的部分场景）的实际需求——传统 World Composition 要求策划手动切割地图并维护大量子关卡引用，在团队协作时极易产生冲突。World Partition 通过将 Actor 数据以网格坐标作为键值直接写入单一 .umap 文件，从根本上解决了多人协作中的合并冲突问题。

对于关卡设计师而言，World Partition 最直接的价值在于：设计师可以在**无限尺寸**的单一视口中自由放置 Actor，系统会在后台自动决定哪些区域应当在运行时被加载，而这一决策完全基于配置好的流式加载距离（Streaming Distance）参数，无需任何手动触发逻辑。

---

## 核心原理

### 单元格网格划分（Cell Grid）

World Partition 将世界坐标系划分为固定尺寸的正方形单元格。默认情况下，运行时网格（Runtime Grid）的单元格大小为 **12800 厘米（128 米）**。每个 Actor 根据其边界框中心点坐标被分配到对应的单元格。当玩家进入某个单元格的流式加载半径范围内，该单元格内的所有 Actor 会自动流式加载进内存。

每个 Runtime Grid 可独立配置三个关键参数：
- **Cell Size**：单元格的边长，影响加载粒度
- **Loading Range**：以单元格为单位的加载半径
- **Priority**：多个网格叠加时的加载优先级

开发者还可以创建多个 Runtime Grid 并为不同类型的资产（建筑、植被、动态 AI）指定不同网格，从而精细控制各类资产的加载时机与卸载距离。

### HLOD（分层细节）与 World Partition 的集成

World Partition 内置了 **Hierarchical Level of Detail（HLOD）** 生成流程。当某个单元格处于卸载状态时，系统可以用该单元格对应的低精度 HLOD 网格替代，保持远处场景的视觉完整性。HLOD 数据在编辑器的 HLOD Builder 中通过批处理离线生成，并与各单元格的 Cell Hash 绑定。这意味着地形和建筑在数公里外仍能以极低的 Draw Call 数量呈现轮廓，而非简单消失。

### 数据层（Data Layers）

Data Layers 是 World Partition 中替代旧版"关卡可见性"功能的机制，允许将 Actor 归入具名层，并在运行时通过 `UDataLayerSubsystem` API 动态激活或停用。例如，将昼夜交替的不同道具集分别放入 `DayLayer` 和 `NightLayer`，然后在 Blueprint 中调用：

```
GetSubsystem<UDataLayerSubsystem>()->SetDataLayerRuntimeState(
    DayLayer, EDataLayerRuntimeState::Activated);
```

Data Layers 也可设置为**编辑器专用（Editor Only）**，用于组织场景而不影响运行时行为，这对于大团队中不同职能成员（环境美术、游戏设计师）管理各自资产极为实用。

### One File Per Actor（OFPA）

与 World Partition 配套的 **One File Per Actor** 机制将每个 Actor 的数据存储在 `__ExternalActors__` 子目录下的独立文件中，文件路径由 Actor 的 GUID 哈希生成。这使得源代码控制（如 Perforce 或 Git）中多名开发者可以同时编辑同一关卡而不产生二进制合并冲突，因为每次提交仅涉及各自修改的 Actor 文件。

---

## 实际应用

**大型开放世界关卡搭建**：在《堡垒之夜》迁移至 UE5 的过程中，关卡团队利用 World Partition 将整张岛屿地图放入单一关卡，并针对建筑物（Cell Size 6400 cm，Loading Range 2）、植被（Cell Size 12800 cm，Loading Range 1）和地形（HLOD 常驻）分别配置了三套 Runtime Grid，实现了 20 km² 尺寸地图的流畅流式加载。

**任务触发区域管理**：利用 Data Layers，关卡设计师可以将某个支线任务涉及的所有 Actor（NPC、道具、障碍物）放入一个 `Quest_Layer_03`，仅当玩家接受该任务时通过 `SetDataLayerRuntimeState` 将其激活。任务完成后再停用，避免无关 Actor 常驻内存。

**编辑器分区视图**：World Partition 编辑器窗口（`Window > World Partition`）提供了俯视图可视化界面，用不同颜色显示已加载/未加载的单元格区域，设计师可以直接框选区域强制加载到编辑器视口中，而无需在场景中实际移动摄像机到该位置。

---

## 常见误区

**误区一：World Partition 会自动解决所有性能问题**
World Partition 只管理 Actor 的**存在性**（是否在内存中），而非渲染性能。一个被加载进来的单元格如果包含数百个高面数网格体，仍然会造成 GPU 瓶颈。Cell Size 和 Loading Range 的配置不当（例如将 Loading Range 设为过大数值）会导致同时加载的 Actor 数量激增，反而拖慢性能。

**误区二：所有 Actor 都应使用 Is Spatially Loaded = true**
World Partition 中每个 Actor 都有 `Is Spatially Loaded` 属性。Game Mode、全局 Game State、常驻音频管理器等全局性 Actor **必须设置为 false**，确保它们在游戏开始时始终存在。误将全局管理 Actor 设为空间加载会导致玩家移动到某些区域时系统逻辑丢失，这类 bug 极难复现。

**误区三：World Partition 与传统子关卡（Level Streaming）互斥**
实际上，World Partition 关卡仍然可以使用 `Load Stream Level` 节点加载传统子关卡，两套机制可以共存。例如室内场景（洞穴、建筑内部）因其独立的遮挡剔除需求，仍适合使用传统流式子关卡，由 World Partition 的 World Partition Stream Level Actor 触发加载。

---

## 知识关联

World Partition 建立在**关卡流式加载（Level Streaming）**的基础机制之上——流式加载定义了"异步将关卡数据从磁盘读取至内存"的底层行为，而 World Partition 则在此之上提供了空间坐标驱动的自动化调度层。理解流式加载中 Async Loading Thread 和 Package 异步序列化的原理，有助于诊断 World Partition 在大型场景中出现的加载卡顿（Hitch）问题。

在更大的技术栈中，World Partition 与 **Nanite**（虚拟化几何体）和 **Lumen**（全动态全局光照）共同构成 UE5 的大世界渲染基础：Nanite 解决了高密度网格体的渲染效率，Lumen 解决了动态光照的重计算成本，而 World Partition 解决了超大场景的内存管理——三者协同才能支撑现代 AAA 级别的开放世界项目规模。