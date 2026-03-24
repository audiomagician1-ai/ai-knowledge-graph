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
quality_tier: "pending-rescore"
quality_score: 41.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.407
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 关卡流式加载

## 概述

关卡流式加载（Level Streaming）是虚幻引擎中将大型游戏世界拆分为多个子关卡、在运行时按需动态加载或卸载这些子关卡的技术机制。它的本质是让玩家感知到的游戏世界是"无缝连续"的，而实际上引擎后台始终只保持一部分地图数据驻留在内存中。

该技术最早在虚幻引擎3时代以"Persistent Level + Streaming Level"的架构形式确立下来，并在UE4中通过Level Streaming Volume和蓝图接口得到系统化完善。其核心动机是突破单一关卡的内存上限——以PS4/Xbox One为参考平台，单帧可用内存约为5GB，而一款开放世界游戏的完整资产总量往往超过50GB，流式加载正是解决这一数量级差距的工程手段。

关卡流式加载对开放世界、大型城市场景及过场动画管理尤为关键。《堡垒之夜》的地图更新事件、《赛博朋克2077》的室内与室外切换，底层均依赖类似的流式分区机制来避免加载屏幕打断体验。

---

## 核心原理

### 持久关卡与流送关卡的层级结构

关卡流式加载强制要求存在一个**持久关卡（Persistent Level）**，它是始终保持加载状态的"容器"，本身通常只包含极少量几何体（如玩家出生点、全局光照设置），而将实际地形、建筑、敌人拆散到若干**流送关卡（Streaming Level）**中。在 Unreal Editor 的 Levels 面板（Windows > Levels）中，每个流送关卡都以独立的 `.umap` 文件存储，可单独编辑、版本管理，极大降低了多人协作时的文件冲突概率。

### 触发加载的两种控制方式

**方式一：Level Streaming Volume（关卡流体积）**  
在编辑器中放置 `ALevelStreamingVolume` Actor，将其关联到目标流送关卡。当玩家摄像机进入或离开该体积时，引擎自动触发 `LoadStreamLevel` 或 `UnloadStreamLevel`。这种方式零代码、直观，适合地形明显分隔的区域（如山谷两侧）。  
Volume 有两个关键属性：`Streaming Usage`（控制是加载用还是可见性用）和 `Editor Pre-Vis Only`（仅在编辑器预览中生效的调试标志）。

**方式二：蓝图 / C++ 直接调用**  
使用 `UGameplayStatics::LoadStreamLevel(World, LevelName, bMakeVisibleAfterLoad, bShouldBlockOnLoad, LatentInfo)` 接口。参数 `bShouldBlockOnLoad` 为 `true` 时会同步加载（阻塞主线程，会产生卡顿），为 `false` 时异步加载（推荐）。异步加载完成的时机通过 Latent Action 的 `OnCompleted` 回调获取，开发者可在此处做子关卡可见性切换或蒙太奇衔接。

### 加载状态机与可见性分离

流送关卡在引擎内部存在**三个独立状态**：
1. **未加载（Unloaded）**：资产不在内存中
2. **已加载但不可见（Loaded, Hidden）**：数据已在内存中，但渲染器跳过该关卡，碰撞仍然有效
3. **已加载且可见（Loaded, Visible）**：完全激活

这种三态设计使"预加载"策略成为可能：在玩家距离目标区域还有约 200–500 米时触发加载，等玩家真正抵达边界时，子关卡早已进入"已加载但不可见"状态，切换到可见仅需一帧，从而实现无缝衔接。`bMakeVisibleAfterLoad` 参数控制加载完成后是否直接跳过"隐藏"阶段。

---

## 实际应用

### 大地图分区的划分原则

以一个 4km × 4km 的开放世界为例，通常将其划分为 16 个 1km × 1km 的网格子关卡，再为每个网格添加 100–200 米的重叠边界以避免边缘突然弹出（Pop-in）。重叠区域内的静态网格体在两个相邻子关卡中都存放一份拷贝，以内存的轻微冗余换取视觉连续性。

### 过场动画的关卡切换

线性叙事游戏常在过场动画播放期间完成子关卡切换，利用摄像机聚焦角色、背景模糊的视觉遮挡窗口（通常 2–4 秒），用 `LoadStreamLevel` 以异步方式加载下一场景，动画结束帧恰好对应加载完成帧，玩家不会察觉切换发生。

### 多人协作关卡编辑

在 UE5 项目中，将城市的"道路网络""建筑群""灯光与特效"拆分为三个独立 `.umap` 文件，三名美术可以同时在同一持久关卡下分别签出各自的流送关卡，互不覆盖，合并时只需更新持久关卡的关卡列表引用。

---

## 常见误区

### 误区一：认为流送关卡坐标是相对于自身原点的

流送关卡内所有 Actor 的坐标仍然是**世界空间绝对坐标**，而不是相对于该子关卡原点的局部坐标。新手常犯的错误是在子关卡中把地形放在 (0,0,0)，导致加载后与持久关卡的其他元素位置错位。正确做法是在编辑器的 Levels 面板中为每个流送关卡设置 `Level Transform`，或直接在世界空间正确位置摆放资产后保存。

### 误区二：`bShouldBlockOnLoad=true` 更"安全"

同步加载虽然代码逻辑简单，但会在主线程阻塞期间冻结整个游戏循环，在移动平台上可能导致系统强制杀进程（iOS 看门狗机制超时阈值约为 20 秒）。正确实践是始终使用异步加载，配合加载进度 UI 或预加载缓冲区掩盖等待时间。

### 误区三：Level Streaming Volume 适用于所有场景

Level Streaming Volume 依赖摄像机（而非玩家 Pawn）的世界位置触发，在第三人称俯视角或自由摄像机模式下，摄像机可能提前进入体积范围，导致超出预期距离的子关卡被加载。对于摄像机移动范围与玩家移动不一致的项目，应改用蓝图监测 Pawn 坐标触发加载。

---

## 知识关联

学习关卡流式加载需要具备 **UE5 关卡编辑器**的操作基础，特别是 Levels 面板的使用、`.umap` 文件的创建与保存，以及 Actor 在世界坐标系中的摆放逻辑。没有这些前置操作经验，Streaming Level 的坐标错位问题将难以排查。

关卡流式加载是理解 **World Partition**（世界分区）系统的必要前提。World Partition 是 UE5 引入的新一代流式方案，它将手动划分子关卡的工作自动化——引擎根据 `World Partition` 组件自动生成流送单元（Runtime Grid Cell），每个 Cell 默认大小为 128m × 128m，并由 `Data Layers` 取代了传统的流送关卡文件。理解传统流式加载的三态状态机和预加载逻辑，有助于快速掌握 World Partition 中 `Streaming Source` 优先级和 `Data Layer` 加载策略的设计意图。
