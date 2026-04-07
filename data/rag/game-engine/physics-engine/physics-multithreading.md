# 物理多线程

## 概述

物理多线程是游戏引擎物理系统利用多核CPU并行执行物理计算任务的核心技术，在NVIDIA PhysX框架中通过`PxDefaultCpuDispatcher`与任务图（Task Graph）机制实现。其本质是将单帧物理更新中可独立执行的计算单元——宽相碰撞剔除、窄相接触生成、孤岛约束求解、刚体积分——识别为有向无环图（DAG）中的节点，在保证拓扑顺序的前提下，将无依赖的节点分发至线程池并行执行。

物理多线程的历史背景直接影响了其设计哲学。PhysX 2.x时代（Ageia硬件PhysX卡，2006年前后）物理计算依赖专用PPU（Physics Processing Unit），其并行化以SIMD指令为主，任务级并行能力有限。NVIDIA收购Ageia后，PhysX 3.0（2010年发布）进行了架构性重写，引入任务图调度系统，将单线程串行物理管线重构为多线程可调度的DAG，这一架构延续至今日的PhysX 5.x。Coumans等人的Bullet物理引擎同期也引入了类似的Island并行求解机制（Coumans, 2015，*Bullet Physics SDK Manual*），二者在孤岛并行化策略上具有高度相似性。

实际工程中，物理多线程的线程数配置有严格约束。PhysX官方建议工作线程数设为**逻辑核心数减1**（为渲染主线程保留1个核心），在8核机器上即设置7个物理工作线程。现代开放世界游戏同时模拟的刚体可达数万个（如《荒野大镖客：救赎2》据Rockstar技术报告披露其物理系统峰值同时激活约40000个物理对象），单线程在16.67毫秒帧预算内根本无法完成计算，多线程并行是工程硬需求而非性能优化选项。

---

## 核心原理

### PhysX任务图调度机制

PhysX将单帧物理更新拆解为若干继承自`PxTask`（或轻量级`PxLightCpuTask`）的任务对象。每个任务通过`addReference()`增加引用计数，声明其必须等待的前置任务数量；当所有前置任务完成并调用`release()`使引用计数归零时，该任务被提交至`PxCpuDispatcher`的工作队列。工作线程池以**工作窃取（Work Stealing）**策略从队列取任务执行，避免线程饥饿。

任务图的典型拓扑结构如下：

```
[模拟开始] 
    → [宽相 BroadPhase]
        → [孤岛生成 IslandGen]
            → [Island_0 窄相+求解] ─┐
            → [Island_1 窄相+求解] ─┤→ [刚体积分 Integration] → [模拟结束]
            → [Island_N 窄相+求解] ─┘
```

物理引擎内部以**孤岛（Simulation Island）**为并行粒度：凡是通过接触点或约束（关节）彼此连接的刚体属于同一孤岛，不同孤岛之间无任何数据共享，其窄相接触生成与约束求解过程可在不同线程上完全独立并行执行。孤岛的动态合并与分裂由`IslandManager`在每帧宽相完成后执行，其时间复杂度为 $O(N \cdot \alpha(N))$，其中 $\alpha$ 为反阿克曼函数（Union-Find数据结构的复杂度），在实践中接近 $O(N)$。

### 宽相并行碰撞检测（MBP算法）

宽相的目标是以 $O(N \log N)$ 或更低复杂度剔除不可能相交的AABB对，向窄相传递"潜在碰撞对（Broad Phase Pair）"列表。PhysX提供三种宽相实现：

- **SAP（Sweep And Prune）**：沿三轴维护排序列表，更新代价为 $O(N \cdot k)$（$k$为帧间移动对象数），天然单线程。
- **MBP（Multi Box Pruning）**：将世界AABB划分为最多256个**Region**，每个Region独立维护SAP列表，不同Region间的测试完全无数据竞争，可分配至不同线程并行执行。
- **GPU Broad Phase**：PhysX 5.x新增，将AABB树构建与重叠测试迁移至GPU CUDA kernel。

MBP的并行加速比在对象数量超过**5000个**时开始显著，低于此阈值时Region管理的线程同步开销（每帧需汇总跨Region的新增/删除对）反而导致性能不及SAP。Region划分建议依据游戏地图密度动态调整，稠密区域分配更多Region以平衡线程负载。

### 窄相并行接触生成

窄相对宽相输出的每一个潜在碰撞对精确计算接触流形（Contact Manifold），包含接触点位置、法线方向和穿透深度。不同碰撞对之间无数据依赖，属于**尴尬并行（Embarrassingly Parallel）**计算。PhysX将接触生成任务按碰撞对类型（Box-Box、Sphere-Convex、Convex-Mesh等）分批，以SIMD批处理方式在多个工作线程上并行执行。

每个接触流形的生成结果写入线程私有缓冲区（Thread-Local Buffer），避免锁竞争，最终在汇聚阶段合并为全局接触流形列表。这一设计使窄相的并行效率极高，在256核模拟服务器上的加速比接近线性（Macklin et al., 2019，*Small Steps in Physics Simulation*，SIGGRAPH 2019）。

### 约束求解的并行化（TGS求解器）

约束求解（Constraint Solver）是物理多线程中数据依赖最复杂的环节。PhysX 4.0引入**TGS（Temporal Gauss-Seidel）**求解器，在传统PGS（Projected Gauss-Seidel）基础上按时间步细分迭代，提升了关节链（Joint Chain）的收敛速度，同时保留了孤岛级并行结构。

PGS迭代一次约束 $i$ 的速度修正量公式为：

$$\Delta \lambda_i = \frac{-(J_i \mathbf{v} + b_i)}{J_i M^{-1} J_i^T + \varepsilon} $$

其中 $J_i$ 为约束雅可比矩阵，$\mathbf{v}$ 为速度向量，$M$ 为质量矩阵，$b_i$ 为偏置项（含Baumgarte稳定化项），$\varepsilon$ 为正则化参数。同一孤岛内的约束迭代需串行（因共享刚体速度 $\mathbf{v}$），但不同孤岛可完全并行。TGS在每个子步内执行此迭代，关节链误差收敛速度相比PGS快约2-4倍（Macklin et al., 2019）。

---

## 关键方法与配置参数

### 初始化线程池

```cpp
// 创建工作线程数为核心数-1的调度器
PxU32 numThreads = PxThread::getNbPhysicalCores() - 1;
PxDefaultCpuDispatcher* dispatcher = 
    PxDefaultCpuDispatcherCreate(numThreads);

PxSceneDesc sceneDesc(physics->getTolerancesScale());
sceneDesc.cpuDispatcher = dispatcher;
sceneDesc.broadPhaseType = PxBroadPhaseType::eMBP; // 启用多线程宽相
sceneDesc.filterShader  = PxDefaultSimulationFilterShader;
PxScene* scene = physics->createScene(sceneDesc);
```

### 配置MBP区域划分

```cpp
// 为100m×100m地图划分4×4=16个Region
PxBroadPhaseRegion region;
for (int x = 0; x < 4; x++) {
    for (int z = 0; z < 4; z++) {
        region.bounds = PxBounds3(
            PxVec3(x*25.0f - 50.0f, -10.0f, z*25.0f - 50.0f),
            PxVec3((x+1)*25.0f - 50.0f, 50.0f, (z+1)*25.0f - 50.0f));
        scene->addBroadPhaseRegion(region);
    }
}
```

### 孤岛分裂阈值控制

PhysX通过`PxSceneFlag::eENABLE_STABILIZATION`和休眠阈值控制孤岛激活状态。睡眠阈值（Sleep Threshold）设置为：

$$E_{sleep} = \frac{1}{2} m v_{threshold}^2$$

当刚体动能低于 $E_{sleep}$ 持续 $N_{frames}$（默认为4帧）后进入休眠，从孤岛中移除，减少活跃孤岛数量，间接提升多线程调度效率。

---

## 实际应用案例

**案例：《地平线：零之曙光》破坏系统的物理多线程实践**

Guerrilla Games在GDC 2017技术分享中披露，《地平线》的植被破坏系统需同时处理约8000个动态物理碎块。他们将地图按20m×20m网格划分MBP Region，确保玩家周围活跃的碎块始终落在4-9个Region内，保证宽相并行粒度。约束求解层面，破坏碎块间的铰链约束被刻意设计为短链（长度≤3），避免形成超大孤岛导致并行度骤降，使8线程配置下的物理更新时间从单线程的11.2ms降至1.9ms（接近理论6倍加速比的7倍以内），帧时间节省约9.3ms。

**例如**：在Unity ECS架构下使用DOTS Physics（基于Havok Physics for Unity），开发者可通过`PhysicsStep`系统的`MultiThreaded = true`参数启用多线程，内部同样采用孤岛并行策略，但Unity将线程调度集成进Job System（基于Work Stealing的`IJobParallelFor`），与PhysX的手动`CpuDispatcher`在API层面有显著差异，但底层并行化原理完全一致。

---

## 常见误区

**误区1：线程数越多物理性能越好**

物理多线程的加速比受限于孤岛并行度（Amdahl定律）。若场景中所有刚体通过关节链形成单一巨大孤岛（如大型机械臂模拟），则孤岛内约束求解强制串行，额外线程完全空转。实测表明，在单孤岛为主的场景中，从4线程提升至16线程的物理性能增益不足3%，而线程创建和上下文切换开销反而略微增加帧时间。

根据Amdahl定律，若物理计算中串行比例为 $f$（孤岛内串行部分），则 $N$ 线程最大加速比为：

$$S(N) = \frac{1}{f + \frac{1-f}{N}}$$

当 $f = 0.3$（30%串行）时，即使 $N \to \infty$，最大加速比也仅为 $\frac{1}{0.3} \approx 3.33$。

**误区2：物理多线程与渲染线程完全隔离**

PhysX `simulate(dt)` 调用是异步的，`fetchResults(true)` 才是同步点。若渲染线程在`fetchResults`前访问刚体变换数据（`PxRigidBody::getGlobalPose()`），会发生数据竞争（Data Race），导致渲染位置与物理位置不一致的"鬼影"瑕疵。正确做法是使用PhysX的**双缓冲变换缓存**（`PxSceneFlag::eENABLE_ACTIVE_ACTORS` + 回调机制），或在`fetchResults`完成后统一同步变换数据至渲染层。

**误区3：MBP总比SAP快**

MBP的Region管理引入了跨Region对象迁移的同步开销。当场景中对象高频跨Region移动（如快速飞行的导弹），Region边界检测和重新分配的代价超越了并行加速收益，此时SAP反而更优。经验规则：静态或低速动态对象占多数（>70%）时优先MBP；高速小型对象密集场景考虑SAP或GPU Broad Phase。

---

## 知识关联

物理多线程与以下概念存在深度关联：

- **刚体积分（Rigid Body Integration）**：多线程环境下积分步骤须在所有孤岛求解完成后统一执行，积分本身亦可并行但需保证写入不同刚体的内存无重叠（Cache Line False