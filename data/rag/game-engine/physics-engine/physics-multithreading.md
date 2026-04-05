---
id: "physics-multithreading"
concept: "物理多线程"
domain: "game-engine"
subdomain: "physics-engine"
subdomain_name: "物理引擎"
difficulty: 3
is_milestone: false
tags: ["性能"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
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


# 物理多线程

## 概述

物理多线程是游戏引擎物理系统利用多核CPU并行执行物理计算任务的技术方案。在PhysX中，这一机制通过`PxDefaultCpuDispatcher`实现，开发者在初始化时可指定工作线程数量（通常设为逻辑核心数减1，为渲染线程保留资源），从而将碰撞检测、约束求解、刚体积分等任务分散至多个线程同时执行。

物理多线程的需求源于游戏场景复杂度的爆炸式增长。早期3D游戏中的物理对象数量仅有数十个，单线程足以应对；而现代开放世界游戏中同时模拟的刚体、布料、粒子可达数万个，单线程物理更新在16.67毫秒帧预算内无法完成。PhysX 3.x版本开始系统性引入任务图（Task Graph）架构，将原本串行的物理管线重构为可并行的有向无环图，这一设计至今仍是PhysX 5.x的基础骨架。

物理多线程之所以复杂，在于物理计算存在严重的数据依赖性：约束求解必须在碰撞检测完成后进行，位置积分必须在约束求解后执行。因此物理多线程并非简单的"把所有工作分给多个线程"，而是在保证计算顺序正确的前提下，识别并行机会并高效调度。

---

## 核心原理

### PhysX任务图与调度器

PhysX将单帧物理更新拆解为若干`PxTask`对象，每个任务声明其前置依赖（通过`addReference()`增加引用计数），当引用计数归零时任务被提交给`CpuDispatcher`执行。调度器维护一个工作队列，线程池中的工作线程持续从队列取任务执行，执行完成后调用`release()`触发后继任务的引用计数递减，形成级联触发。

```
[BroadPhase任务] → [MidPhase任务] → [NarrowPhase任务] → [Solver任务] → [Integration任务]
                                 ↗ 并行N个Island任务 ↘
```

任务图中可并行的最大宽度取决于场景拓扑结构，PhysX内部以**孤岛（Island）**为单位进行并行分组：不存在约束连接关系的刚体组合属于不同孤岛，各孤岛的求解过程完全独立，可在不同线程上同时进行。

### 宽相（Broad Phase）的并行碰撞检测

宽相负责剔除不可能发生碰撞的对象对，PhysX默认采用**SAP（Sweep And Prune）**算法或**MBP（Multi Box Pruning）**算法。MBP专为多线程设计，将世界空间划分为多个区域（Region），不同Region的AABB重叠测试可在不同线程上完全独立执行，互不共享写入数据。配置方法如下：

```cpp
PxBroadPhaseDesc bpDesc(PxBroadPhaseType::eMBP);
// 最多256个Region，建议按游戏地图密度划分
physics->createScene(sceneDesc); // sceneDesc中指定broadPhaseType
```

MBP在对象数量超过**5000个**时相较SAP有明显并行加速效益，对象数量较少时分区管理的开销反而会使性能下降。

### 窄相（Narrow Phase）的并行接触生成

窄相计算精确的接触点和接触法线，是物理帧中计算量最密集的阶段。PhysX对每一对"潜在碰撞对"（来自宽相输出）独立生成接触流形，由于各碰撞对之间没有数据依赖，这一过程天然适合并行：工作线程从接触对队列中批量取用（默认batch size为**16对**），执行GJK/EPA算法后将结果写入各自私有的接触缓冲区，最终由主线程合并。

### 约束孤岛与TGS求解器的并行策略

PhysX 4.0引入**TGS（Temporal Gauss-Seidel）求解器**，相较旧版PGS具有更好的约束稳定性，同时保持了孤岛级并行能力。同一孤岛内部的约束求解迭代**不可并行**（因为迭代间存在顺序依赖），但不同孤岛的求解批次可并行。开发者可通过`PxSceneDesc::solverBatchSize`控制孤岛合并到单批次的阈值（默认值为**128个约束**），较小的批次大小意味着更多并行批次，但线程同步开销更高。

---

## 实际应用

**工作线程数量配置**：在PC平台8核CPU上，推荐`PxDefaultCpuDispatcher`配置为**3～5个**工作线程。配置过多线程会导致与渲染线程、音频线程争抢CPU时间片；配置1个线程在拥有16个逻辑核的机器上会浪费75%的并行潜力。移动平台（如骁龙888，8核异构架构）通常只为物理分配大核中的2个线程。

**动态场景中的孤岛碎片化问题**：当大量刚体通过关节链相互连接（如布娃娃系统），整个角色形成单一超大孤岛，该孤岛内部无法并行，帧率会出现瓶颈。解决方案是限制关节链深度或将布娃娃中不活跃的关节断开，人为制造孤岛分裂以恢复并行度。

**与游戏引擎线程模型的集成**：在Unreal Engine 5中，PhysX（或Chaos）的物理任务被提交给引擎的`TaskGraph`系统，`FPhysScene::StartFrame()`将物理tick封装为`FPhysicsCommand`，与渲染准备任务并行执行，物理结果通过`FetchResults()`在游戏线程同步栅栏处取回，确保本帧逻辑使用的物理状态完整一致。

---

## 常见误区

**误区一：线程数越多，物理性能越好**
物理多线程的加速比受阿姆达尔定律限制。PhysX内部仍有约束求解的串行部分（尤其是大孤岛场景），即使配置32个线程，加速比也很难超过6～8倍。过多线程还会造成内存带宽争用和缓存失效，实测中从8线程增至16线程往往只带来5%提升甚至性能下降。

**误区二：`simulateCollisionDetection()`和`simulate()`可以随意并行调用**
PhysX场景对象不是线程安全的，在调用`PxScene::simulate()`期间，任何对场景的外部修改（如`setGlobalPose()`、`addActor()`）都必须在`simulate()`开始前或`fetchResults()`之后进行。PhysX提供`PxScene::lockRead()`和`PxScene::lockWrite()`用于多线程读取，但写锁期间所有物理任务会挂起，误用会产生死锁。

**误区三：并行碰撞检测消除了碰撞结果的不确定性**
由于各工作线程的执行顺序不固定，浮点运算的归并顺序不同，多线程物理的仿真结果在不同帧、不同机器上可能产生微小差异，导致录像回放或网络同步时的物理状态逐帧累积发散。需要确定性物理的场合（如格斗游戏帧同步）必须强制单线程或使用固定执行顺序的确定性求解器。

---

## 知识关联

物理多线程依赖**物理场景管理**中建立的对象层次结构：场景中`PxRigidActor`的空间分布直接影响MBP分区效果，而孤岛划分则完全取决于场景中约束（`PxConstraint`/`PxJoint`）的拓扑连接方式。不理解场景的孤岛分割逻辑，就无法分析多线程利用率低的根本原因。

掌握物理多线程后，下一个学习目标是**物理性能优化**，涵盖PhysX SDK中的`PxPvdSceneClient`性能分析接口（PhysX Visual Debugger）、`PxSimulationStatistics`结构体中的`nbBroadPhasePairs`/`nbNarrowPhasePairs`指标解读，以及通过调整`sleepThreshold`减少活跃对象数量、降低并行任务总量的策略。物理多线程解决"怎么并行"，而性能优化解决"并行什么、并行多少"。