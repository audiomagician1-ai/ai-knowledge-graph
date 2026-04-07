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
quality_tier: "A"
quality_score: 76.3
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





# 子关卡管理

## 概述

子关卡管理（Sub-level Management）是虚幻引擎5关卡编辑器中用于将单一大型游戏世界拆分为多个独立 `.umap` 文件并集中调度的技术体系。其核心工作面板位于编辑器菜单 **Window → Levels**，在这个面板中，开发者可以看到持久关卡（Persistent Level）作为根节点，以及挂载于其下的所有子关卡列表。每个子关卡本质上是一个独立的 ULevel 资产，可单独保存、单独加载，并拥有各自的 Actor 集合。

这一机制最早在虚幻引擎3时代以 Streaming Level 的形式出现，UE5 中通过 World Partition 对其进行了补充，但传统子关卡工作流仍广泛应用于需要精细手工控制加载时机的项目，尤其是多人协作开发场景。当两名设计师同时工作于同一游戏世界时，将地形放入 `Level_Terrain.umap`、将建筑放入 `Level_Buildings.umap` 可彻底避免 `.umap` 文件的 Git 冲突。

子关卡管理对性能影响直接且可量化：通过将玩家当前视野范围内的区域对应的子关卡标记为"流送加载"，可将单帧内驻留内存的 Actor 数量控制在合理范围，而非一次性将整个世界加载进内存。

---

## 核心原理

### 子关卡的三种显示状态

在 Levels 面板中，每个子关卡右侧有三个状态图标，对应不同的编辑器可见性与运行时行为：

- **Visible（眼睛图标）**：该子关卡的 Actor 在视口中可见，但这仅影响编辑时预览，不影响打包后的加载逻辑。
- **Locked（锁头图标）**：锁定后该子关卡中的 Actor 无法被选中或修改，常用于将已完成的区域锁定防误操作。
- **Current Level（铅笔图标，蓝色高亮）**：任何新放置的 Actor 都会被写入当前激活的子关卡，而非持久关卡。初学者最常犯的错误就是忘记切换 Current Level，导致所有 Actor 堆积在持久关卡内。

### 加载方式：Always Loaded 与 Blueprint 流送

子关卡有两种根本性的加载策略，在 Levels 面板中通过右键菜单 **Change Streaming Method** 切换：

1. **Always Loaded**：随持久关卡一同加载，在内存中始终存在。适用于全局共用的系统性内容，例如游戏模式 Actor、全局光照设置子关卡（通常命名为 `Level_Lighting`）。

2. **Blueprint**（即 Level Streaming Volume / 蓝图控制）：通过节点 `Load Stream Level`（输入参数为子关卡名称字符串，如 `"Level_Zone_A"`）和 `Unload Stream Level` 在运行时动态装卸。`Load Stream Level` 节点有一个关键布尔引脚 **Make Visible After Load**，若设为 `false`，关卡会加载进内存但不渲染，可用于预热资源。

### 权限控制与版本管理

UE5 与 Perforce 或 Git LFS 集成后，子关卡的文件级独立性直接转化为权限控制粒度。在 Levels 面板中右键子关卡选择 **Check Out** 即可通过 Source Control Provider 锁定该 `.umap` 文件，其他协作者的编辑器会将该子关卡显示为只读并呈现锁头标记。这意味着关卡划分方案本身就是一种团队权限规划——一个 30 人团队通常将子关卡按功能域切分：`Level_Gameplay`、`Level_Audio`、`Level_VFX` 分别由对应职能人员持有编辑权。

---

## 实际应用

**多区域开放世界的分区加载**：假设制作一个包含 6 个独立区域的 RPG 世界，每个区域对应一个子关卡（如 `Zone_Forest`、`Zone_Desert`）。在过渡走廊处放置 Level Streaming Volume，当玩家的 Camera 进入该 Volume 时，引擎自动触发相邻区域子关卡的 `Load Stream Level` 调用，预计加载时间控制在 0.5 秒以内（取决于子关卡内 Actor 复杂度和磁盘 IO 速率）。

**光照子关卡的独立构建**：将所有光源和 Sky Atmosphere Actor 集中到一个独立的 `Level_Lighting.umap` 并设为 Always Loaded。这样在光照美术迭代时，只需对这一个 `.umap` 执行 **Build Lighting Only**，而不会因关卡加载顺序问题影响其他子关卡的光照贴图 ID 一致性。

**编辑器内的协作分工**：关卡设计师 A 持有 `Level_Blockout.umap` 的 Check Out，程序员 B 同时在 `Level_GameLogic.umap` 中放置 Trigger 和 Game Mode Override Actor，两人的修改完全独立，合并时不存在二进制冲突。

---

## 常见误区

**误区一：将所有 Actor 放入持久关卡**

新手常常忽略切换 Current Level，导致持久关卡积累了数百个本应归属各子关卡的 Actor。这不仅破坏了流送加载的效果（持久关卡永远不会被卸载），还会造成协作冲突。正确做法是持久关卡只保留 World Settings、Player Start 和流送控制蓝图，业务 Actor 一律分配至对应子关卡。

**误区二：混淆编辑器可见性与运行时加载状态**

在 Levels 面板中关闭一个子关卡的眼睛图标，仅隐藏其在编辑器视口中的显示，**不会**改变该子关卡在打包游戏中的加载策略。若子关卡被设为 Always Loaded，无论编辑器里是否可见，运行时它都会加载。这两个维度完全独立，必须分别配置。

**误区三：子关卡名称与路径的混用**

`Load Stream Level` 节点接收的是子关卡的**短名称**（不含路径和扩展名），如填入 `"/Game/Maps/Zone_Forest"` 会导致加载失败并在输出日志中打印 `Warning: Failed to find streaming level`。正确输入应为 `"Zone_Forest"`，与 Levels 面板中显示的名称完全一致。

---

## 知识关联

子关卡管理建立在 **UE5 关卡编辑器** 基础操作之上——需要熟悉 `.umap` 的保存机制、Outliner 中的 Actor 归属显示，以及 Source Control 集成的配置方法，这些前置知识决定了能否正确识别 Current Level 指示器和 Check Out 状态。

从子关卡管理出发，可以延伸至 **World Partition** 系统：后者是 UE5 对传统子关卡流送的自动化重构，将手动划分的子关卡替换为基于坐标网格的自动单元（Cell），流送决策由 World Partition Streaming Source 驱动。理解传统子关卡的手动加载/卸载逻辑，是评估何时应迁移到 World Partition、何时应保留手工子关卡控制的判断依据。此外，子关卡管理与 **Level Blueprint** 存在作用域绑定关系：每个子关卡拥有独立的 Level Blueprint，其中的事件和变量仅对本子关卡内的 Actor 生效，跨子关卡通信需借助 Game Instance 或 Event Dispatcher 实现。