---
id: "unity-jobs"
concept: "Job System"
domain: "game-engine"
subdomain: "unity-architecture"
subdomain_name: "Unity架构"
difficulty: 3
is_milestone: false
tags: ["多线程"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# Job System（作业系统）

## 概述

Job System 是 Unity 引擎中用于多线程并行计算的调度框架，随 Unity 2018.1 正式引入稳定版本，是 Unity DOTS（面向数据的技术栈）三大支柱之一（另外两个为 ECS 和 Burst Compiler）。它允许开发者将计算任务拆分为离散的"作业（Job）"单元，由 Unity 的内部工作线程池（Worker Thread Pool）自动调度执行，从而充分利用多核 CPU 的并行处理能力。

与传统 `MonoBehaviour` 中所有逻辑必须在主线程运行不同，Job System 通过严格的数据所有权规则（借鉴自 Rust 的借用检查思想）来保证线程安全，无需手动加锁（mutex）。开发者声明一个 struct 并实现 `IJob` 接口，将所需数据以 `NativeArray<T>` 等原生容器形式传入，系统便能安全地在任意工作线程上执行该作业。

Job System 解决的核心问题是：Unity 早期版本的物理模拟、动画蒙皮、粒子系统均在主线程串行执行，导致帧时间（Frame Time）居高不下。启用 Job System 后，以 Unity 官方公布的 MegaCity 示例为例，场景中超过 400 万个游戏对象的更新可维持在 60 FPS，这在传统 GameObject 架构下几乎不可能实现。

---

## 核心原理

### 作业类型与接口定义

Job System 提供多种作业接口以适配不同并行模式：

- **`IJob`**：最基础的单任务接口，实现 `Execute()` 方法，整个作业只执行一次。
- **`IJobParallelFor`**：并行 For 循环接口，`Execute(int index)` 方法针对数组的每个索引并行调用，Unity 会将索引范围自动分批（batching）分配给不同工作线程，批大小（innerloopBatchCount）需由开发者指定，典型值为 32 或 64。
- **`IJobParallelForTransform`**：专用于 `Transform` 组件的并行读写，避免频繁访问主线程 Transform 的性能损耗。
- **`IJobChunk`**（配合 ECS 使用）：以 ECS Archetype Chunk 为处理单元，每次 `Execute()` 处理一整块内存连续的实体数据。

```csharp
struct MyParallelJob : IJobParallelFor
{
    public NativeArray<float> results;
    public void Execute(int index)
    {
        results[index] = math.sqrt(index);
    }
}
```

### 依赖链与 JobHandle

Job System 使用 `JobHandle` 结构体来管理作业间的依赖关系。调度一个作业时，`Schedule()` 方法返回一个 `JobHandle`，后续作业可以将该 Handle 作为依赖参数传入，从而形成有向无环图（DAG）式的依赖链。

```csharp
JobHandle handleA = jobA.Schedule();
JobHandle handleB = jobB.Schedule(handleA); // B 依赖 A 完成后才执行
handleB.Complete(); // 阻塞主线程直到 B 完成
```

多个依赖可通过 `JobHandle.CombineDependencies(handleA, handleB)` 合并，允许 C 同时等待 A 和 B 完成后再执行，这是实现扇入（fan-in）模式的标准方式。`Complete()` 调用会将控制权交回主线程，若过早调用则会抵消并行收益，Unity Profiler 中会将此标记为"WaitForJobGroupID"耗时。

### NativeContainer 与内存安全

Job 内部不能直接访问托管堆（managed heap）上的 C# 数组或 List，必须使用 `NativeContainer` 系列类型，这些类型分配在非托管内存（unmanaged memory）上，支持跨线程访问：

| 容器类型 | 特点 |
|---|---|
| `NativeArray<T>` | 固定长度，读写均支持 |
| `NativeList<T>` | 可变长度，需 `[NativeDisableParallelForRestriction]` 属性才可并行写入 |
| `NativeHashMap<TKey, TValue>` | 键值对，并行写不同键时安全 |
| `NativeQueue<T>` | 并行版本为 `NativeQueue<T>.ParallelWriter` |

所有 NativeContainer 必须手动调用 `.Dispose()` 释放内存，否则在 Unity Editor 中会触发内存泄漏警告（生产构建则静默泄漏）。使用 `Allocator.TempJob` 分配器时，Unity 要求该容器必须在 4 帧内被释放，违反此规则会在 Editor 中抛出异常。

### 安全检查机制

Unity 的安全系统通过"AtomicSafetyHandle"在 Editor 模式下对每个 NativeContainer 实例进行读写冲突检测。若同一个 `NativeArray` 被两个没有依赖关系的作业同时写入，系统会在 `Schedule()` 时立即抛出 `InvalidOperationException`，而不是在运行时出现不确定性的数据竞争。此检查仅在 Editor 和 Development Build 中启用，Release Build 中被剥离以提升性能。

---

## 实际应用

**群体行为模拟（Boids）**：数千只 AI 实体的速度、位置更新逻辑通过 `IJobParallelFor` 并行处理。每帧调度一次，将所有实体位置存于 `NativeArray<float3>`，计算邻近实体的分离/对齐/聚合力向量，总计算量从主线程 12ms 降低至 1.5ms（8 核机器上的典型数据）。

**程序化地形生成**：Perlin 噪声采样可对地形高度图的每个像素点独立计算，使用 `IJobParallelFor` + Burst Compiler 组合，512×512 高度图的生成时间可从约 80ms 降至约 2ms。

**物理射线检测批处理**：Unity 提供 `RaycastCommand` 和 `BatchRayCastCommand` 配合 Job System 使用，可在一帧内并行发射数千条射线，Unity 文档标注该方式比逐条 `Physics.Raycast` 快约 **10 倍**以上。

---

## 常见误区

**误区一：认为 `Complete()` 应该紧跟 `Schedule()` 调用**
许多初学者在调度后立即调用 `Complete()`，这使作业与主线程串行执行，完全失去并行收益。正确做法是在帧的早期（如 `Update` 开始时）调度作业，在帧的后期（如 `LateUpdate` 或下一帧开始时）才调用 `Complete()`，给工作线程足够的时间并发执行。

**误区二：在 Job 内部访问 Unity 托管对象**
`IJob` 的 struct 实现中不能持有对 `GameObject`、`Component`、`Mesh` 等托管类型的引用，编译器或运行时会报错。需要将所需数据提前提取到 `NativeArray` 等原生容器中再传入 Job，而非在 Job 内部调用 Unity API。

**误区三：混淆 `NativeArray` 的 `Allocator` 类型导致性能损耗**
`Allocator.Persistent` 分配速度最慢但生命周期不限，`Allocator.TempJob` 速度居中适用于跨帧作业，`Allocator.Temp` 速度最快但只能在同一帧内使用且不能传入 Job。错误地对每帧创建的临时数组使用 `Persistent` 分配器，会因频繁的慢速分配显著拖慢性能。

---

## 知识关联

**前置概念：ECS/DOTS 架构**
Job System 的 `IJobChunk` 接口直接消费 ECS 中 Archetype 的内存块（Chunk），所有 ComponentData 均以 struct 形式存储于连续内存，满足 Job System 对非托管数据的要求。若不使用 ECS，纯 Job System 也可独立运行，但需要开发者自行管理 NativeContainer 的生命周期。

**协同概念：Burst Compiler**
Job System 的性能收益在与 Burst Compiler 结合时才能最大化。为 Job struct 添加 `[BurstCompile]` 特性后，Burst 会将 `Execute()` 方法编译为高度优化的原生代码，并自动利用 SIMD 向量化指令（如 SSE4、AVX2），在数学密集型计算中可额外获得 4~8 倍加速。

**配套工具：Unity Profiler 的 Timeline 视图**
开发者可在 Profiler 的 Timeline 视图中直观看到各工作线程（Worker 0 ~ Worker N）上的作业执行时间段，识别依赖等待气泡（dependency bubble），据此调整 `CombineDependencies` 拓扑结构或 `innerloopBatchCount` 参数以优化并行效率。