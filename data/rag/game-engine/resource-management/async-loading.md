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
quality_tier: "A"
quality_score: 76.3
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

# 异步加载

## 概述

异步加载（Asynchronous Loading）是游戏引擎资源管理中的一种技术，允许在游戏主线程继续运行的同时，由后台工作线程负责从磁盘或网络读取并解码资源文件。与同步加载（即调用即阻塞）不同，异步加载不会让玩家看到画面冻结或帧率骤降，因为 I/O 操作被转移到独立线程上执行。

该技术在 2000 年代初随 PlayStation 2 和 Xbox 等家用机的出现而普及，当时光驱读取速度极慢（约 1.5–4× CD-ROM，即 225–600 KB/s），开发者不得不在玩家行走过门洞的几秒内异步预取下一区域的资源。如今即使在 NVMe SSD 理论带宽超过 5 GB/s 的平台上，异步加载依然不可或缺，因为单帧 16.6 ms 的预算无法容纳任何大型资源的完整解析过程。

理解异步加载对游戏程序员至关重要，原因在于它直接决定了开放世界游戏是否出现"贴图弹出"（texture pop-in）和关卡切换时的卡顿问题。Unreal Engine 5 的 Nanite 和 Lumen 系统均深度依赖异步加载机制来按需流入几何体和光照数据。

---

## 核心原理

### 请求队列与工作线程

异步加载的基础是一个**请求队列（Request Queue）**，主线程向队列提交加载请求后立即返回，不等待结果。引擎通常维护 1–4 条专用 I/O 工作线程（Unity 默认使用 1 条，Unreal 可配置为 4 条），这些线程轮询队列、依次执行文件读取和资源解码操作。

请求对象通常包含以下字段：
- `path`：资源路径
- `priority`：优先级整数值（见下节）
- `callback`：加载完成后的回调函数指针或委托
- `status`：枚举状态（Pending / InProgress / Done / Failed）

### 优先级调度

当多个异步请求同时存在时，引擎不能按先进先出（FIFO）顺序处理，否则玩家正在看的物体反而比远处场景更晚加载。因此请求队列通常实现为**最小堆（Min-Heap）**，以优先级数值排序。

Unreal Engine 内部使用 0–100 的整数优先级，其中：
- **0**：最高优先级，用于玩家角色当前帧必需的资源（如武器换弹动画）
- **50**：中等优先级，用于视野内但非立即可见的物体
- **100**：最低优先级，用于后台预取（prefetch）的远景资源

开发者可通过 `FStreamableManager::RequestAsyncLoad()` 的第三个参数手动指定优先级，错误地将所有请求设为优先级 0 会导致调度退化为 FIFO，失去优先级管理的意义。

### 回调机制与生命周期管理

加载完成后，引擎通过**回调（Callback）**通知主线程资源就绪。回调存在两种主流模式：

**函数指针 / Lambda 回调**：适合简单场景，在 C++ 中写法如下：
```cpp
StreamableManager.RequestAsyncLoad(
    SoftRef.ToSoftObjectPath(),
    FStreamableDelegate::CreateLambda([this](){
        Mesh = Cast<UStaticMesh>(SoftRef.Get());
        SpawnActor();
    })
);
```

**Future / Promise 模式**：Unity 的 `AsyncOperation` 对象和 Unreal 的 `TFuture<T>` 均属此类，允许用协程（Coroutine）写法 `await` 异步结果，代码可读性更高。

回调中必须检查资源指针是否有效，因为在加载期间持有资源的对象可能已被销毁（即"悬空回调"问题），这是异步加载 bug 的最常见来源。

### 后台线程与主线程的同步点

I/O 线程完成读取后，资源对象的**最终初始化**（如上传 GPU 纹理数据、构建物理碰撞形状）通常必须回到主线程执行，因为图形 API（DirectX、Vulkan）的部分调用不支持多线程并发写入。Unreal 通过 `TGraphTask` 将该步骤提交到游戏线程任务队列；Unity 则在 `AsyncOperation.isDone` 变为 `true` 时，在下一帧主线程上完成对象激活。

---

## 实际应用

**开放世界区块流入**：《赛博朋克 2077》使用异步加载按距离和玩家移动速度动态加载街区资源包（chunk），当玩家以步行速度（~5 m/s）移动时，引擎在其到达某区块边界 200 米前就发出低优先级预加载请求；若玩家驾车加速到 ~50 m/s，则将该请求优先级提升至最高级别强制立即处理。

**关卡过渡的异步预热**：在出现"正在加载"界面的游戏（如《艾尔登法环》的传送）中，异步加载并非在玩家点击确认后才开始，而是在玩家靠近传送点时就已以低优先级后台启动，使加载界面停留时间缩短 30–60%。

**动态音频流**：背景音乐文件体积大（往往超过 50 MB），不适合一次性同步加载。引擎使用异步加载以固定 4096 字节的音频缓冲块为单位持续后台读取，保证回放不中断，这也是流式音频系统的基础实现方式。

---

## 常见误区

**误区一：以为异步加载"零耗时"**
异步加载仍然消耗 CPU 和 I/O 带宽，只是不占用主线程帧预算。如果在同一帧内提交数百个高优先级异步请求，工作线程的 I/O 带宽会饱和，后续请求反而比少量同步加载更慢完成。正确做法是根据帧预算限制每帧提交的请求数量（Unreal 的推荐阈值是每帧不超过 10–20 个新请求）。

**误区二：回调里直接操作 UI 或物理对象**
回调可能在工作线程上下文中触发（取决于引擎实现），此时直接修改 UI 文本或添加物理 Actor 会造成数据竞争。必须通过消息队列或线程安全的委托将操作派发回主线程，而不是在回调体内直接执行。

**误区三：认为资源引用（软引用）本身会触发加载**
`TSoftObjectPtr` 或 Unity 的 `AssetReference` 仅存储路径字符串，持有引用并不会启动任何异步加载。必须显式调用 `RequestAsyncLoad()` 或 `LoadAssetAsync()` 才会向请求队列提交任务，混淆"引用"与"加载"是初学者最频繁的错误。

---

## 知识关联

**前置概念——资源引用**：异步加载的输入参数正是软资源引用（Soft Reference）所存储的路径信息。硬引用（Hard Reference）在对象构造时触发同步加载，而软引用将加载时机的决定权交给开发者，从而允许异步加载流程介入。没有软引用机制，就无法在不实际加载资源的情况下描述"将来需要什么"。

**后续概念——流式系统**：异步加载是流式系统（Streaming System）的底层执行原语。流式系统在异步加载之上增加了基于距离、可见性、内存预算的自动调度逻辑，让引擎无需手动调用就能持续维护世界状态。可以将异步加载理解为单次的手动请求，而流式系统是持续运行的自动化管理器，两者的关系类似于"单个 HTTP 请求"与"HTTP 连接池管理器"。