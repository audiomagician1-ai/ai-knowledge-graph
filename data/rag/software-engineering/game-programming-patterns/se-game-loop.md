---
id: "se-game-loop"
concept: "游戏循环"
domain: "software-engineering"
subdomain: "game-programming-patterns"
subdomain_name: "游戏编程模式"
difficulty: 2
is_milestone: true
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.414
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 游戏循环

## 概述

游戏循环（Game Loop）是游戏程序持续运行的核心驱动机制：程序反复执行"处理输入→更新状态→渲染画面"三个阶段，直到玩家退出游戏。与普通的事件驱动程序不同，游戏即使在没有用户输入时也必须持续运行——敌人仍在移动、粒子仍在飘落、时间仍在流逝——因此游戏循环不依赖操作系统的消息队列来驱动执行，而是主动地、不停歇地轮询和更新。

游戏循环的概念随着1970年代街机游戏的兴起而形成。早期如《太空侵略者》（1978年）的程序直接以硬件扫描频率为节奏驱动逻辑，本质上就是一个与显示器刷新同步的无限循环。随着PC游戏在不同硬件上运行，开发者发现同一份《毁灭公爵》代码在快速机器上游戏节奏会加快，在慢速机器上又会变慢，这个问题直接催生了对游戏循环进行时间步长（Timestep）管理的需求。

理解游戏循环的时间步长策略对于制作表现稳定的游戏至关重要：它直接影响物理模拟的准确性、网络同步的可行性，以及游戏在不同帧率设备（如30fps手机与144fps显示器）上的一致性。选错时间步长策略可能导致子弹穿墙（隧穿效应）或在低端设备上物理行为完全失控。

## 核心原理

### 固定时间步长（Fixed Timestep）

固定时间步长让游戏逻辑以恒定的时间间隔推进，与实际经过的墙钟时间（Wall Clock Time）解耦。其基本实现如下：

```
double previous = getCurrentTime();
double lag = 0.0;
const double MS_PER_UPDATE = 16.0; // 约60次/秒

while (true) {
    double current = getCurrentTime();
    lag += current - previous;
    previous = current;

    processInput();

    while (lag >= MS_PER_UPDATE) {
        update(MS_PER_UPDATE);
        lag -= MS_PER_UPDATE;
    }

    render(lag / MS_PER_UPDATE); // 传入插值比例
}
```

`lag` 变量记录了"游戏逻辑欠实际时间多少毫秒"，每次循环补偿性地执行多步逻辑更新来消化这个欠量。物理引擎（如Box2D）通常要求固定时间步长，因为其碰撞检测算法依赖于 `Δt` 为常量的数值积分，推荐值为 `1/60` 秒或 `1/120` 秒。

固定时间步长的关键公式是速度积分：`position += velocity × MS_PER_UPDATE`，其中 `MS_PER_UPDATE` 是常量，保证了无论帧率如何波动，每次物理步进的行为都完全可重现，这是实现确定性网络同步的必要前提。

### 可变时间步长（Variable Timestep）

可变时间步长让每帧的逻辑更新时间 `Δt` 等于上一帧实际消耗的时间，实现简单：

```
double lastTime = getCurrentTime();
while (true) {
    double current = getCurrentTime();
    double deltaTime = current - lastTime;
    lastTime = current;

    processInput();
    update(deltaTime);
    render();
}
```

速度积分变为：`position += velocity × deltaTime`，理论上无论帧率是60fps还是30fps，物体在1秒内移动的距离相同。然而这种方案存在严重缺陷：当 `deltaTime` 很大时（例如调试暂停后恢复，`deltaTime` 突然为5秒），物体会瞬间飞出场景边界；同时浮点数在不同 `deltaTime` 下的累积误差不同，导致两次运行轨迹可能轻微不同，无法用于确定性回放或对战网络同步。

### 半固定时间步长（Semi-Fixed Timestep）

半固定方案是对可变步长的修补：设定一个最大允许的 `deltaTime` 上限（如 `0.25` 秒），若实际帧时间超过此值则截断。这防止了"死亡螺旋"（death spiral）——即游戏因帧率过低导致每帧需要处理的逻辑步数越来越多，反而更慢，形成正反馈崩溃。

半固定方案代码仅需在固定步长循环中加入一行限制：
```
lag = min(lag, MAX_FRAME_DURATION);
```
其中 `MAX_FRAME_DURATION` 通常设为250毫秒，即假设即使在最卡顿的情况下，游戏逻辑每帧最多补算4步（以60fps为基准）。

### 渲染插值

在固定/半固定时间步长下，逻辑更新与渲染频率不一致，会导致画面抖动（jitter）。解决方案是在渲染时传入当前 `lag` 在一个时间步内的占比 `alpha = lag / MS_PER_UPDATE`，使用线性插值计算渲染位置：

```
renderPosition = previousPosition * (1 - alpha) + currentPosition * alpha;
```

这让画面在逻辑帧之间平滑过渡，玩家看到的运动是流畅的，即使逻辑每秒只更新60次而显示器刷新144次。

## 实际应用

**Unity引擎**将游戏循环的两种策略显式分开：`Update()` 每渲染帧调用一次（可变步长），`FixedUpdate()` 以固定间隔调用（默认0.02秒，即50Hz），物理相关代码必须放在 `FixedUpdate()` 中。这正是固定+可变混合策略的工程落地。

**《守望先锋》**的服务器使用固定时间步长（每秒64tick），客户端进行预测和插值，正是依赖固定步长的确定性来实现状态回滚与重播。如果服务器逻辑使用可变步长，客户端预测回滚将产生不可接受的偏差。

**手机游戏**普遍面临30fps与60fps设备共存的问题。若使用可变步长且未设上限，在低端手机首帧加载时 `deltaTime` 可达2秒以上，导致玩家角色瞬间穿越整张地图。半固定时间步长的截断机制是解决此问题的标准做法。

## 常见误区

**误区一：可变步长乘以deltaTime就能保证帧率无关性。** 乘以 `deltaTime` 只在线性运动下成立。对于弹簧系统、空气阻力等二次及以上的物理计算，欧拉积分在不同 `deltaTime` 下结果差异很大，必须使用固定步长+高阶积分器（如RK4）才能保证稳定性。

**误区二：固定时间步长会导致游戏在高帧率显示器上看起来卡顿。** 这是未实现渲染插值时的表现。正确实现渲染插值（传入 `alpha` 值）后，固定时间步长的游戏在144Hz显示器上同样流畅，因为渲染帧在逻辑帧之间做了平滑插值。

**误区三：游戏循环的三个阶段必须在同一线程顺序执行。** 单线程顺序执行是最简单的实现，但现代游戏常将渲染提交到渲染线程，使GPU和CPU并行工作。理解单线程游戏循环是理解多线程游戏架构的基础，但不应将两者等同。

## 知识关联

**前置概念**：游戏编程模式概述中介绍了游戏程序区别于一般应用程序的主动驱动特性，游戏循环正是这一特性的具体实现机制。理解操作系统事件循环（如Windows的消息泵）有助于对比为何游戏不能直接使用系统事件队列。

**后续概念**：更新方法（Update Method）模式建立在游戏循环之上——游戏循环每帧调用场景中每个对象的 `update(deltaTime)` 方法，时间步长的选择直接决定了 `update` 方法接收的参数含义。游戏多线程架构则是将单线程游戏循环的各阶段拆分到不同线程，理解单线程循环的时序是分析多线程竞态条件的前提：例如渲染线程读取位置数据时，逻辑线程正在写入，就会产生数据竞争。
