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

子关卡管理（Sub-level Management）是 Unreal Engine 5 关卡编辑器中用于将单一持久关卡（Persistent Level）划分为多个独立 `.umap` 文件并进行组织、流送与权限控制的功能体系。每个子关卡都是一个完整的地图文件，可被独立加载、卸载或由多名设计师并行编辑，而不会造成版本冲突。

该功能体系的原型来自 UE3 时代的 World Composition 系统，在 UE5 中演化为 **Levels 面板**（菜单路径：Window → Levels）与 World Partition 的并行方案。对于体量较大的开放世界项目，子关卡管理提供了比单文件更细粒度的资产组织方式，尤其适合关卡美术、灯光师和关卡设计师三类角色在同一场景中同时作业的工作流。

子关卡管理之所以重要，原因在于 UE5 的 `.umap` 文件在多人协作时无法像代码那样合并差异（diff/merge），一旦两人同时修改同一文件就会产生不可调和的冲突。将场景按功能拆分为灯光子关卡、几何体子关卡、触发器子关卡等，可以让不同职能的团队成员各自持有各自文件的写入权限，彻底规避这类冲突。

---

## 核心原理

### 持久关卡与子关卡的父子关系

持久关卡（Persistent Level）是场景的"容器"，本身只负责持有对各子关卡的引用，不包含实际 Actor。子关卡以流送层级（Streaming Level）的形式挂载在持久关卡上，其挂载信息存储在持久关卡的 `UWorld::StreamingLevels` 数组中。在 Levels 面板中，每一行对应一个 `ULevelStreaming` 对象，该对象记录了子关卡的资产路径、流送类型（`Always Loaded` 或 `Blueprint`）以及当前的可见性状态。

### 流送类型与加载时机

子关卡有两种核心流送类型：

- **Always Loaded**：随持久关卡同步加载，适合游戏全程需要的逻辑关卡（如 GameMode 相关 Actor）。此类子关卡的 Actor 在编辑器与运行时均始终存在，不受流送体积（Streaming Volume）控制。
- **Blueprint Streaming**：由蓝图或 C++ 显式调用 `LoadStreamLevel` / `UnloadStreamLevel` 节点触发加载，适合需要按需切换的场景区域。`LoadStreamLevel` 节点包含 `Level Name`、`Make Visible After Load`（布尔）和 `Should Block on Load`（布尔）三个关键参数，其中 `Should Block on Load` 设为 `true` 会阻塞游戏线程直到加载完成，在大型子关卡中会引发明显卡顿，通常应保持 `false` 并配合 `Get Streaming Level → Is Level Loaded` 做异步检测。

### 可见性与锁定状态

Levels 面板为每个子关卡提供两个独立开关：**眼睛图标**（Visibility，仅控制编辑器视口中的显示）和**锁形图标**（Lock，控制写入权限）。锁定状态下，该子关卡内的所有 Actor 在编辑器中变为只读，鼠标选中时会显示橙色边框提示"关卡已锁定"。这一机制在配合源码控制（Perforce 或 Git LFS）使用时尤为关键：约定由资产所有者在 Checkout 文件后才解锁对应子关卡，可防止未签出即修改的情况。

### 当前关卡（Current Level）设置

Levels 面板中以**粗体**高亮显示的子关卡为当前活动关卡（Current Level）。在视口中放置新 Actor 时，该 Actor 将自动归属于 Current Level 对应的 `.umap` 文件。若未设置正确的 Current Level 就在视口中拖入静态网格，Actor 会被错误写入持久关卡，导致本应分离的资产被污染到主文件中。双击 Levels 面板中的子关卡行可快速将其设为 Current Level。

---

## 实际应用

**灯光子关卡工作流**：在中型项目（例如一个包含 3 个场景区域的关卡）中，通常创建专用的 `L_Zone01_Lighting` 子关卡，仅存放定向光、天空光及反射捕获 Actor。灯光师只需签出该文件，无需触碰几何体子关卡，场景美术师对静态网格的修改也不会影响灯光师的工作文件。

**按区域流送加载**：在大型室内场景中，为每个房间创建独立子关卡（如 `L_Corridor`、`L_BossRoom`），配合流送体积（Level Streaming Volume）在玩家进入特定区域时自动触发 `LoadStreamLevel`。当玩家离开时调用 `UnloadStreamLevel` 释放内存，控制运行时内存用量。实践中，一个标准的 `LoadStreamLevel` 蓝图调用后，应在 `Event Tick` 或 `Delay` 中轮询 `Get Streaming Level` 的 `Is Level Loaded` 返回值，确认为 `true` 后再执行后续逻辑（如开门动画）。

**多人协作签出规范**：在 Perforce 工作流中，团队通常在子关卡文件命名时加入职能后缀（`_Geo`、`_Light`、`_Logic`），并要求每位成员只能 Exclusive Checkout（P4 的 `+l` 锁定类型）自己职能对应的文件，从而在工具层面强制执行权限隔离。

---

## 常见误区

**误区一：认为子关卡可见性等同于运行时加载状态**  
在编辑器 Levels 面板中关闭子关卡的眼睛图标（设为不可见）仅影响编辑器视口显示，不代表运行时该关卡会被卸载。运行时的加载与卸载必须通过 `LoadStreamLevel` / `UnloadStreamLevel` 蓝图节点或 C++ `UGameplayStatics` 接口显式控制。许多初学者误以为隐藏后打包游戏就不会加载，但实际上 `Always Loaded` 类型的子关卡无论可见性如何都会在游戏启动时全部加载进内存。

**误区二：在持久关卡中直接放置游戏 Actor**  
将敌人 AI、可互动道具等 Actor 直接放入持久关卡（即 Current Level 指向持久关卡时在视口中放置），会导致这些 Actor 无法被单独卸载，始终占用内存和 CPU 时间。正确做法是将所有运行时 Actor 放入对应功能的子关卡，持久关卡仅保留 Game Mode、Player Start 等全局单例对象。

**误区三：混淆子关卡管理与 World Partition**  
World Partition 是 UE5 引入的新系统，适用于超大开放世界，使用基于距离的自动流送单元（Data Layer + Grid Cell）。传统子关卡管理通过手动挂载 `.umap` 文件实现，适用于中小型场景或需要精确控制加载时序的项目。两者在同一个 World 中只能启用其一：开启 World Partition 后，Levels 面板中的手动子关卡挂载功能即被禁用。

---

## 知识关联

子关卡管理建立在 UE5 关卡编辑器的基本操作之上，要求使用者熟悉 Levels 面板的位置、`.umap` 文件的保存路径规范以及视口中 Actor 的放置方式。没有这些前置操作经验，Lock 状态与 Current Level 的切换逻辑会令人困惑。

掌握子关卡管理后，自然延伸到 **Data Layer**（UE5 World Partition 的逻辑分层系统）和 **关卡流送体积（Level Streaming Volume）** 的高级配置，以及在 C++ 侧通过 `FLatentActionInfo` 结构体实现异步加载回调。此外，子关卡的命名与目录规范直接影响后续的构建（Build）和 Cook 效率，建议将所有子关卡统一放置在 `Content/Maps/SubLevels/` 目录下，以便打包系统识别依赖关系。