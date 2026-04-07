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

# 物理场景管理

## 概述

物理场景管理是指游戏引擎中负责创建、维护和推进物理仿真世界的核心机制，具体体现为 PhysX 的 `PxScene`、Bullet 的 `btDynamicsWorld`、或 Havok 的 `hkpWorld` 等对象的生命周期管理与每帧更新策略。物理场景本质上是一个独立的仿真容器，持有所有刚体（RigidBody）、碰撞形状（Shape）、约束（Constraint）及材质（Material）的引用，与渲染场景完全分离。

物理场景管理的概念随着 AGEIA PhysX 在 2006 年推出硬件加速物理处理单元（PPU）而被广泛重视。在此之前，物理对象的更新通常与渲染帧率直接耦合，导致帧率波动时仿真结果不稳定。NVIDIA 收购 AGEIA 后将 PhysX SDK 整合进 CUDA 并于 2008 年免费开放，使得规范化的场景管理模式（Scene-Step 模式）成为行业标准。

物理场景管理的核心价值在于将"仿真时间"与"渲染时间"解耦。游戏渲染帧率可能在 30fps 到 240fps 之间浮动，而物理仿真若以可变时间步长运行，会因浮点累积误差产生非确定性结果——同样的初始状态在不同帧率下得到不同的物理轨迹，造成联机游戏中的作弊漏洞或单机游戏中的"帧率影响游戏速度"问题（《黑暗之魂》PC 版早期即存在此缺陷）。

---

## 核心原理

### 固定时间步长与子步进（Sub-stepping）

物理仿真的标准更新公式为：

```
simulate(fixedDeltaTime)
accumulator += realDeltaTime
while (accumulator >= fixedDeltaTime):
    physicsWorld.step(fixedDeltaTime)
    accumulator -= fixedDeltaTime
```

其中 `fixedDeltaTime` 通常设为 `1/60`（约 16.67ms）或 `1/120`（约 8.33ms）秒。当一帧渲染耗时 33ms（对应 30fps）时，物理引擎在该帧内需执行 **2 次**固定步长仿真，这就是子步进（Sub-stepping）机制。PhysX 在 `PxScene::simulate(dt)` 中通过内部分割实现子步进，而 Unity 的 `Fixed Update` 循环则在引擎层将其暴露为 `Time.fixedDeltaTime` 参数。

子步进次数存在上限。PhysX 默认允许的最大子步数为 **1**（即每帧最多执行一次 `simulate`），这意味着如果渲染帧耗时超过 `fixedDeltaTime`，物理时钟会相对于真实时间减慢。Unity 默认的最大子步进次数为 **10**，可通过 `Physics.defaultMaxPhysicsDeltaTime`（默认值 `0.1` 秒）控制。超过上限后物理时间会"欠步"，产生所谓的"死亡螺旋"（Death Spiral）——CPU 越忙越慢，物理积压越来越多。

### PhysX Scene 的生命周期

在 PhysX 5.x 中，一个完整的物理场景管理流程包含以下阶段：

1. **创建阶段**：通过 `PxPhysics::createScene(PxSceneDesc)` 初始化场景，`PxSceneDesc` 指定重力向量（如 `PxVec3(0, -9.81f, 0)`）、宽相算法（BVH 或 MBP）及模拟过滤回调。
2. **填充阶段**：向场景添加 `PxRigidDynamic`（动态体）、`PxRigidStatic`（静态体）和 `PxArticulation`（关节链）。
3. **推进阶段**：调用 `scene->simulate(dt)` 开始异步计算，然后调用 `scene->fetchResults(true)` 阻塞等待结果写入。
4. **销毁阶段**：必须先移除所有 Actor 再调用 `scene->release()`，否则触发内存访问违规。

`simulate` 与 `fetchResults` 之间的间隔是 CPU 与物理线程并行执行渲染逻辑的黄金窗口，这是 PhysX 异步架构的核心设计意图。

### 多场景与场景隔离

一个游戏进程可同时维护多个独立的 `PxScene` 实例。常见用法包括：将**布料/破坏效果**放入独立的装饰性场景（Cosmetic Scene），使其不影响游戏性判定；以及使用**查询专用场景**（Query-Only Scene）缓存静态碰撞几何，避免重复宽相查询。不同场景之间默认无法进行碰撞检测，跨场景交互需要应用层自行同步对象位置。

---

## 实际应用

**Unity 中的固定步长配置**：在 `Edit > Project Settings > Time` 中，`Fixed Timestep` 默认为 `0.02`（即 50Hz），`Maximum Allowed Timestep` 默认为 `0.1` 秒（限制最大子步数约为 5）。角色控制器和载具物理通常需要将 `Fixed Timestep` 调整为 `0.01667`（60Hz）以提高响应精度。

**Unreal Engine 5 的 Chaos 物理场景**：UE5 弃用了 PhysX 转向自研 Chaos 物理引擎，其场景对象为 `FPhysScene_Chaos`，通过 `FPhysicsCommand::ExecuteWrite` 宏保证线程安全写入。Chaos 默认以 `30Hz` 固定步长运行（`p.Chaos.Solver.Iterations` 默认 8 次迭代），可在 `DefaultEngine.ini` 中通过 `AsyncPhysicsTickEnabled=true` 启用异步物理场景，将物理计算延迟一帧以换取渲染线程不阻塞。

**赛车游戏的高频物理场景**：车辆悬挂系统对时间步长极为敏感，`1/60` Hz 的标准步长会导致悬挂弹簧在高速碰撞时穿透。《极品飞车》系列和《Forza》系列的车辆物理模块通常以 `1/120` 甚至 `1/360` Hz 的子步长运行，而场景中的非车辆对象仍保持 `1/60` Hz，通过**分层子步进**（Layered Sub-stepping）实现性能平衡。

---

## 常见误区

**误区一：`fixedDeltaTime` 越小越精确，应尽量调小**。减小固定步长确实提升精度，但计算量与步长成反比线性增长。将步长从 `1/60` 改为 `1/240` 意味着每秒执行 4 倍数量的 `simulate` 调用，ContactSolver 迭代次数同步增加 4 倍，极易造成 CPU 瓶颈。PhysX 官方建议对大多数游戏场景使用 `1/60` Hz，仅对极端精度需求的子系统（如车辆、绳索）局部提高频率。

**误区二：`scene->simulate()` 调用后立即可以读取物理结果**。`simulate()` 仅触发异步任务提交，返回后物理线程仍在计算中。直接读取 `PxRigidBody::getGlobalPose()` 会返回**上一帧**的变换数据，而非本帧结果。只有调用 `fetchResults(true)` 完成后，本帧的物理状态才写入可读缓冲区。忽略这一点会导致渲染与物理出现一帧延迟的错位，表现为碰撞反馈"滞后"。

**误区三：物理场景与渲染场景共享同一坐标系不需要偏移处理**。在大世界（Open World）场景中，当玩家距离原点超过约 **10,000 米**时，`float` 精度（约 7 位有效数字）不足以表达厘米级位置差异，导致物理抖动（Jitter）。正确做法是使用"浮动原点"（Floating Origin）技术，定期将物理场景中所有对象平移回原点附近，PhysX 的 `PxScene::shiftOrigin(PxVec3)` 接口专为此设计，可在不重建场景的情况下整体偏移坐标系。

---

## 知识关联

物理场景管理建立在**物理引擎概述**所介绍的刚体动力学、碰撞检测流水线和约束求解器的基础上——理解"场景"为什么要维护宽相（Broad Phase）加速结构，需要先知道碰撞检测的两阶段架构。

物理场景管理直接引出**物理插值**的必要性：固定步长子步进导致物理状态更新频率低于渲染频率时，必须在两个固定步之间对对象变换进行线性插值（Lerp），才能避免物体运动"卡顿"，`accumulator / fixedDeltaTime` 即为插值因子 `α`。

在多核 CPU 上，**物理多线程**进一步扩展了场景管理的概念：PhysX 的 `PxScene` 支持通过 `PxCpuDispatcher` 将岛屿求解（Island Solving）和碰撞检测任务分发到线程池，此时 `simulate` 与 `fetchResults` 之间的并行窗口设计成为决定多线程利用率的关键参数。