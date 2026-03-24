---
id: "async-loading"
concept: "异步加载"
domain: "game-engine"
subdomain: "resource-management"
subdomain_name: "资源管理"
difficulty: 2
is_milestone: false
tags: ["异步"]

# Quality Metadata (Schema v2)
content_version: 6
quality_tier: "pending-rescore"
quality_score: 40.8
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 异步加载

## 概述

异步加载（Asynchronous Loading）是游戏引擎资源管理中的一种技术策略：在不阻塞主线程（游戏逻辑与渲染循环所在线程）的前提下，将资源文件的读取、解压和初始化工作分派到后台工作线程执行。与同步加载不同，调用异步加载接口后函数会立刻返回，主线程继续推进游戏帧，资源就绪后通过回调（Callback）或轮询方式通知调用方。

这一技术的普及源于磁盘 I/O 速度与 CPU 速度之间的鸿沟。早期主机游戏（如 PS1 时代）大量使用同步加载，导致玩家看到频繁的"Now Loading"画面。进入 PS3/Xbox 360 世代后，引擎开始引入多核架构和专用 I/O 线程，异步加载成为主流。Unreal Engine 在 UE3 时期引入 `AsyncPackageLoader`，Unity 在 3.x 版本加入 `Resources.LoadAsync`，标志着商业引擎对该机制的标准化支持。

异步加载在开放世界游戏中价值尤为突出：玩家在一个区域游玩时，引擎后台悄无声息地预加载下一个区域的资源，使得场景切换无缝衔接。若缺少异步加载，每次跨区都需要硬性暂停整个游戏循环，帧率直接降至 0。

---

## 核心原理

### 后台线程与 I/O 调度

异步加载通常由一条或多条专用 **I/O 工作线程** 完成磁盘读取，另有 **解压线程** 负责对 zlib/LZ4 等格式的资源包进行解压。主线程仅提交加载请求并在后续帧检查状态，自身开销通常不超过 0.1 ms 每帧。

请求提交后，引擎内部维护一个 **异步请求队列**（AsyncRequest Queue），队列中每条记录至少包含：目标资源路径、优先级数值、目标内存地址指针、完成回调函数指针。工作线程从队列头部取出任务、执行 I/O、完成后将资源状态标记为 `Ready`，同时将回调推入主线程回调队列，等待下一帧统一派发。

### 优先级系统

异步加载请求并非先到先执行，而是按 **优先级（Priority）** 排序。典型的优先级划分分为三档：

- **Critical（0）**：玩家即将进入的区域、正在播放的过场动画音频，必须在数帧内完成。
- **Normal（1）**：当前场景可见范围外但预测会被需要的网格体与纹理。
- **Background（2）**：远距离环境音效、低频使用的 UI 图标。

Unreal Engine 5 的 `FAsyncLoadingThread` 将优先级映射为内部的 `EAsyncLoadPriority` 枚举，其中 `ASYNC_PRIORITY_HIGH = 100`，数值越大越优先出队。当一个低优先级任务正在 I/O 传输中途，新到达的高优先级请求不会强制中断该次传输（因为磁盘寻道代价更高），而是等当前扇区读取完毕后插队。

### 回调与状态轮询

资源就绪后，引擎提供两种通知机制：

1. **回调函数（Callback）**：调用方在提交请求时注册一个函数指针或 lambda，引擎在主线程安全时机调用它。Unity 中对应 `ResourceRequest.completed` 事件；Unreal 中对应 `FStreamableDelegate`。
2. **轮询（Polling）**：每帧主动查询 `request.isDone`（Unity）或 `AsyncHandle.HasLoadCompleted()`（UE5），适合需要在同一协程中顺序等待多个资源的场景。

回调的执行时机必须在主线程，因为大多数引擎 API（如实例化 GameObject、注册到场景图）都是非线程安全的。引擎通过"回调派发列表"保证这一约束——工作线程只写入列表，主线程在每帧 `Tick` 开始时消费列表。

---

## 实际应用

**开放世界地图分块加载**：将地图划分为若干 Chunk，玩家坐标进入某 Chunk 边界半径 200 米时，触发异步加载请求（优先级 Normal），进入 50 米时升级为 Critical。回调函数负责将加载完毕的静态网格体 Attach 到场景根节点。

**过场动画预加载**：剧情触发器激活时，立刻以 Background 优先级异步加载下一段过场的所有纹理和音频。过场真正开始前至少需要 3 秒缓冲，若 3 秒内未完成，引擎将优先级提升至 Critical 并显示一个模糊的 Loading 遮罩。

**武器/技能特效按需加载**：玩家解锁新技能时，使用异步加载获取粒子特效资源；回调中将资源引用（Asset Handle）存入角色组件的 `EffectPool` 字典，供后续帧零延迟取用，避免首次释放技能时出现卡帧。

---

## 常见误区

**误区一：回调函数可以在工作线程内直接操作场景**
许多初学者在回调中直接调用 `Instantiate()`（Unity）或 `SpawnActor()`（Unreal），结果触发线程竞争崩溃。正确做法是：工作线程只负责将数据拷贝到 CPU 可访问内存并设置完成标志，所有场景操作必须在主线程的派发阶段执行。

**误区二：优先级越高加载越快**
优先级只影响队列出队顺序，不影响 I/O 带宽分配。若后台同时有 20 个 Critical 请求竞争同一块 SSD，每个请求的实际完成时间仍由磁盘吞吐量（如 NVMe SSD 约 3500 MB/s）决定，而非优先级数值。

**误区三：异步加载可以替代资源引用管理**
异步加载描述的是"何时、如何把数据从磁盘读入内存"，但读入后资源的生命周期仍由引用计数或句柄系统管理（即资源引用机制）。若在回调触发前就丢弃了对应的 `AsyncHandle` 或 `ResourceRequest` 对象，某些引擎（如 Unity）会自动取消该请求，导致回调永远不执行。

---

## 知识关联

**前置概念——资源引用**：异步加载请求必须通过资源引用（Asset Reference / Asset Handle）来标识目标资源，而非裸文件路径字符串。只有持有有效引用，引擎才能在加载完成后正确更新引用计数并防止资源被提前回收。理解引用计数的工作方式是正确编写异步回调逻辑的前提。

**后续概念——流式系统（Streaming System）**：异步加载是流式系统的底层执行单元。流式系统在异步加载之上增加了"基于玩家位置自动决策哪些资源需要加载/卸载"的调度逻辑，并引入带宽预算（例如每帧最多提交 4 MB 的新异步请求）来防止 I/O 峰值导致帧时间抖动。可以说，异步加载解决了"怎么加载不卡帧"，而流式系统解决了"加载什么、什么时候加载"。
