---
id: "physics-scene"
concept: "物理场景管理"
domain: "game-engine"
subdomain: "physics-engine"
subdomain_name: "物理引擎"
difficulty: 2
is_milestone: false
tags: ["架构"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.448
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 物理场景管理

## 概述

物理场景管理是游戏引擎中用于组织、调度和推进物理仿真世界的机制，具体体现为 PhysX 中的 `PxScene`、Bullet 中的 `btDiscreteDynamicsWorld`，以及 Unity 的 `Physics.Simulate()` 接口背后的那套生命周期控制系统。它的核心职责是：持有所有物理对象（刚体、碰撞体、约束），并以固定时间步长将它们的状态向前推进。

这一概念起源于 1990 年代末实时物理引擎的商业化进程。AGEIA 在 2004 年推出 PhysX SDK 时，首次以"Scene"作为顶层容器抽象，将碰撞检测、约束求解、睡眠管理统一封装在单个场景对象下，替代了此前各系统散装调用的方式。Unity 在 2008 年集成 PhysX 时继承了这一设计，并引入了多场景物理隔离（Physics Scene，2017 年的 Unity 2017.2 中正式开放 API）。

物理场景管理之所以重要，在于它直接决定了仿真的确定性与帧率无关性。若直接使用渲染帧时间（`deltaTime`）驱动物理，同一游戏在 30 fps 和 120 fps 设备上会产生不同的碰撞结果，导致不可重现的 bug。场景管理层通过固定时间步长机制隔离了渲染帧率与物理更新频率。

---

## 核心原理

### 固定时间步长与子步进（Substep）

物理场景并不以每帧的实际耗时（`deltaTime`）推进，而是将时间划分为固定大小的**物理步**（Fixed Step）。Unity 默认的固定物理步长为 **0.02 秒（50 Hz）**，PhysX 原生 SDK 的默认值也是相同量级。

子步进（Substep）是指在单帧渲染时间内，物理场景可能执行 **0 次、1 次或多次**固定步更新的机制。其逻辑如下：

```
accumulator += deltaTime
while accumulator >= fixedStep:
    scene.simulate(fixedStep)
    scene.fetchResults(block=true)
    accumulator -= fixedStep
```

当渲染帧耗时 0.05 秒（20 fps）时，accumulator 积累了 0.05 秒，会触发 **2 次** 0.02 秒的物理步。若帧耗时仅 0.008 秒（120 fps），则该帧可能**不触发**任何物理步，直到积累量超过阈值。这个机制保证了物理结果与帧率解耦，是确定性重播（Deterministic Replay）的前提之一。

**螺旋死亡（Spiral of Death）** 是子步进的已知风险：若单帧物理计算耗时超过 `fixedStep` 本身，每帧需要执行的步数会越来越多，导致帧耗时进一步增加，形成正反馈崩溃。解决方案是对 accumulator 设置上限（如最多执行 **3 次**子步），超出部分丢弃或降频。

### PxScene / btDiscreteDynamicsWorld 的生命周期

一个 PhysX `PxScene` 的典型帧循环分为三个阶段：

1. **simulate(dt)**：将场景状态向前推进 `dt` 秒，触发碰撞检测和约束求解，该调用**异步**返回（在独立工作线程中运算）；
2. **fetchResults(true)**：阻塞等待 simulate 完成，并将计算结果写回到 `PxRigidActor` 的 transform 中；
3. **读取状态**：游戏逻辑从已更新的 Actor 中读取位置、速度，并响应碰撞事件回调。

在 Bullet 中，`stepSimulation(timeStep, maxSubSteps, fixedTimeStep)` 将上述子步进逻辑内置：`maxSubSteps` 参数等价于对 accumulator 的上限控制，`fixedTimeStep` 默认为 **1/60 秒**。

### 多物理场景与隔离

PhysX 和现代游戏引擎均支持在同一进程内创建**多个独立场景**。Unity 的 `PhysicsScene` API 允许将不同 GameObject 分配到不同物理场景中，彼此之间碰撞查询（Raycast、OverlapSphere）完全隔离，互不干扰。这一能力常用于：

- **主菜单与游戏世界**：主菜单的 UI 物理动画与游戏主场景使用独立场景，避免相互影响；
- **网络预测回滚**：将"已确认服务器帧"和"客户端预测帧"维护在两个物理场景中，回滚时只需重置预测场景的状态。

---

## 实际应用

**Unity 固定步长调整**：对于射击游戏，子弹速度高（如 500 m/s），默认 50 Hz 的物理步在单步内子弹移动 10 米，极易穿透薄墙（Tunneling）。将 `Time.fixedDeltaTime` 从 0.02 秒改为 0.005 秒（200 Hz）或配合 CCD（Continuous Collision Detection），是物理场景层面的直接解决手段。

**PhysX GPU Scene**：PhysX 4.x 支持将场景计算卸载至 GPU（`PxSceneFlag::eENABLE_GPU_DYNAMICS`），当场景中刚体数量超过约 **1000 个**时，GPU 场景吞吐量显著高于 CPU 场景。这是一个场景级别的标志位，无法在运行时动态切换。

**Unreal Engine 的 `World->Tick()`**：Unreal 的物理更新通过 `UWorld::Tick()` 中的 `FPhysScene::TickPhysScene()` 调用，支持 `bSubstepping = true` 配置，最多允许 **6 个子步**，每子步上限 **33.3 ms**。超出限制时 Unreal 会在 Output Log 中打印警告 `Physics substepping limit reached`。

---

## 常见误区

**误区一：直接在 Update 中调用物理查询等于使用了最新物理状态**
许多开发者认为在 `Update()`（渲染帧）中调用 `Physics.Raycast()` 时，射线结果反映的是"当前帧"的物理状态。实际上，物理状态上次更新发生在 `FixedUpdate` 阶段，`Update` 读取的是上一个**已完成物理步**结束时的快照。在高帧率下，渲染帧与物理步之间存在时间差（即 accumulator 中的余量），这是物理插值（Physics Interpolation）要解决的正是这段误差，而不是 `Update` 调用时序的 bug。

**误区二：fixedDeltaTime 越小越精确，应尽可能调小**
降低固定步长确实提高了仿真精度，但约束求解器（Solver）的迭代收敛性与步长相关，步长过小（如低于 0.001 秒）在 PGS（Projected Gauss-Seidel）求解器下反而可能导致约束抖动（Jitter）。同时，更小的步长意味着每渲染帧需要更多子步，CPU 开销成倍增加，触发螺旋死亡的风险上升。PhysX 官方文档建议 `fixedStep` 不低于 **1/240 秒（约 4.17 ms）**。

**误区三：多物理场景可以实现并行物理加速**
多个 `PhysicsScene` 在 Unity 中默认仍在主线程顺序执行，并非并行运算。真正的物理并行需要通过 PhysX 的多线程调度器（`PxDefaultCpuDispatcher`，指定线程数）在**单个场景内部**并行处理，而非拆分为多个场景。

---

## 知识关联

**前置概念——物理引擎概述**：物理引擎概述介绍了刚体动力学和碰撞检测的基本流程，物理场景管理是这些流程的**调度容器**，理解了引擎在每步中执行哪些操作（积分、碰撞、求解），才能理解为何步长大小会影响精度与稳定性的权衡。

**后续概念——物理插值**：由于子步进机制使物理更新频率（如 50 Hz）低于渲染频率（如 120 Hz），渲染帧读取到的刚体位置是"过时"的。物理插值（Physics Interpolation）利用当前物理步与上一物理步之间的 accumulator 余量计算插值系数 `alpha = accumulator / fixedStep`，对位置进行线性混合，平滑视觉抖动。这一技术直接依赖场景管理层暴露的 accumulator 值。

**后续概念——物理多线程**：物理场景的 `simulate()` 与 `fetchResults()` 之间存在天然的异步窗口，物理多线程的核心思路是在此窗口内并行执行游戏逻辑的其他部分，或让 PhysX Dispatcher 将场景内部的碰撞岛（Island）分发给多个 CPU 线程并行处理。理解场景的 simulate/fetch 生命周期是利用多线程物理的先决条件。
