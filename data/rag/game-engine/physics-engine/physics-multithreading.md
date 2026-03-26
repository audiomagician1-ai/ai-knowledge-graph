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
quality_tier: "B"
quality_score: 48.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
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

物理多线程是指在游戏引擎物理模拟中，将碰撞检测、约束求解、刚体积分等计算任务分配到多个CPU线程并行执行的技术机制。以NVIDIA PhysX为例，其多线程架构自PhysX 3.x版本起完全重构，引入了基于任务图（Task Graph）的调度系统，使物理计算能够充分利用现代多核处理器的并行能力。

物理多线程的必要性来源于物理场景的计算瓶颈：一个包含10,000个动态刚体的场景，单线程每帧碰撞检测可能耗时8-15毫秒，远超16.67毫秒的帧时间预算。PhysX通过将场景划分为空间岛屿（Island），每个岛屿独立分配给工作线程，理论上N个岛屿可由N个线程同时处理，从而将碰撞检测时间压缩到2-4毫秒量级。

该技术在AAA级游戏开发中不可或缺。《荒野大镖客：救赎2》的布料模拟与《赛博朋克2077》的大规模人群物理均依赖多线程物理调度。对于独立开发者而言，正确配置PhysX线程数量与调度策略，可在不修改物理场景逻辑的前提下，获得2x至4x的性能提升。

---

## 核心原理

### PhysX任务调度架构

PhysX的多线程调度以`PxCpuDispatcher`接口为核心。开发者创建`PxDefaultCpuDispatcher`时需指定线程数量，通常设置为`CPU逻辑核心数 - 1`，为渲染线程预留一个核心。PhysX内部将物理步进（`simulate()`调用）拆解为一系列`PxBaseTask`子任务，形成有向无环图（DAG）。每个子任务声明其前置依赖完成后，才会被推入工作队列，由调度器分发给空闲线程执行。

PhysX任务调度的关键数据结构是`LightCpuTask`，每个轻量任务的执行成本控制在微秒级，避免单个任务占用线程过长导致负载不均衡。当某线程完成当前任务时，会主动从共享队列中"偷取"（Work Stealing）其他线程的待执行任务，这是PhysX保证多线程负载均衡的核心机制。

### 并行碰撞检测的分区策略

PhysX的碰撞检测分为宽相（Broad Phase）和窄相（Narrow Phase）两个阶段，二者均支持多线程并行。

**宽相并行**：PhysX默认使用SAP（Sweep and Prune）算法的多线程变种`PxBroadPhaseType::eABP`（Adaptive Broad Phase）。ABP将空间划分为网格单元，不同单元的轴对齐包围盒（AABB）重叠测试可完全并行执行，互不依赖。

**窄相并行**：碰撞对（Contact Pair）的精确几何相交测试是窄相的主要工作。PhysX将所有待检测碰撞对均匀分配给工作线程，每个线程独立计算接触点（Contact Point）的位置、法线和穿透深度，结果写入线程私有缓冲区，最后合并。这一过程不存在线程间数据竞争，因为每个碰撞对的几何数据在检测期间是只读的。

### 岛屿系统与约束并行求解

PhysX的**模拟岛屿（Simulation Island）**机制是物理多线程的关键优化。系统通过并查集（Union-Find）算法，将所有通过关节约束或接触约束相互连接的刚体归入同一岛屿，岛屿内的刚体状态更新必须串行处理，但不同岛屿之间完全独立，可并行计算。

约束求解器采用TGS（Temporal Gauss-Seidel）算法，其迭代求解公式为：

**v_{n+1} = v_n + M⁻¹ · Jᵀ · λ**

其中`M`为质量矩阵，`J`为雅可比矩阵，`λ`为约束冲量。不同岛屿的TGS迭代完全并行，同一岛屿内的迭代步骤则按约束优先级串行展开。PhysX默认执行4次位置迭代和1次速度迭代。

---

## 实际应用

### Unity中配置PhysX线程数

在Unity引擎中，通过`Edit > Project Settings > Physics`的`Default Solver Iterations`配置约束迭代次数，但线程数量由Unity运行时根据平台自动决定。若需手动控制，可通过PhysX C++ SDK的`PxSceneDesc.cpuDispatcher`字段注入自定义调度器。在PC平台（8核CPU）上，推荐设置6个PhysX工作线程；在主机平台（PS5/Xbox Series X的8核Zen 2）上，PhysX通常分配5个核心。

### 并行布料模拟的典型场景

角色服装的布料模拟使用`PxCloth`（PhysX 4及以前）或APEX Clothing系统。一个含500个顶点的布料网格，在单线程下每帧求解约需1.2毫秒；多线程模式下，布料粒子被分为若干独立区块，4线程情况下可将求解时间降至约0.4毫秒。多个角色的布料对象天然映射为独立岛屿，多角色场景中的线性加速比接近于线程数量。

### 避免线程同步开销的写法

在PhysX中，错误地在物理步进期间调用`scene->addActor()`或`scene->removeActor()`会触发内部锁，打断并行流水线。正确做法是将Actor的增删操作推迟到`fetchResults()`完成之后、下一次`simulate()`调用之前的时间窗口内执行，确保不打断工作线程的任务执行流。

---

## 常见误区

### 误区1：线程数越多性能越好

许多开发者认为为PhysX分配尽可能多的线程能最大化性能，实际上当PhysX线程数超过物理场景中的岛屿数量时，多余线程会空转等待，反而因线程创建和上下文切换引入约0.1-0.3毫秒的额外开销。场景中只有30个独立岛屿时，使用8个线程的效果与使用4个线程基本相同，正确做法是根据`PxScene::getNbActors()`返回的活跃刚体数量动态评估最优线程数。

### 误区2：多线程物理保证确定性结果

浮点运算的多线程执行顺序不固定，导致PhysX在多线程模式下每次运行的碰撞检测结果可能存在微小差异。对于需要网络同步的多人游戏物理（如《火箭联盟》的球体物理），通常强制使用单线程物理或启用PhysX的确定性模式（通过`PxSceneFlag::eENABLE_PCM`和固定线程数实现），以牺牲约15-20%的性能换取跨客户端的结果一致性。

### 误区3：碰撞回调在工作线程中执行

`onContactModify`和`onTrigger`等碰撞回调函数并非在PhysX工作线程中调用，而是在`fetchResults()`内部于调用线程（通常是主线程）中顺序执行。若在碰撞回调中执行耗时的游戏逻辑（如加载资源、修改场景图），不会与物理工作线程产生竞争，但会直接阻塞主线程，导致帧率下降——这是一个与多线程物理无关但常被混淆的性能陷阱。

---

## 知识关联

**与物理场景管理的关系**：物理场景管理建立的`PxScene`对象是多线程调度的载体。场景中刚体的空间分布直接影响岛屿的划分数量，进而决定多线程并行度的上限。场景中刚体过于密集导致岛屿合并（例如大量相互接触的堆叠物体），会显著降低多线程效率，理解场景结构是理解线程效率的前提。

**通往物理性能优化的路径**：物理多线程是性能优化的基础手段之一，但其效果受制于物理场景的数据结构质量。后续学习物理性能优化时，将进一步涉及如何通过静态刚体分区减少岛屿合并、如何使用`PxPruningStructureType::eDYNAMIC_AABB_TREE`优化宽相查询、以及如何利用GPU物理加速（`PxSceneFlag::eENABLE_GPU_DYNAMICS`）将约束求解完全迁移至GPU，绕开CPU线程数量的限制。