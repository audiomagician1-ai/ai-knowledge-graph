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
quality_tier: "pending-rescore"
quality_score: 41.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.407
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# Job System

## 概述

Job System 是 Unity 引擎中用于多线程并行计算的作业调度框架，于 Unity 2018.1 版本随 DOTS（面向数据的技术栈）一同正式引入。其核心设计目标是让开发者能够安全地在工作线程（Worker Thread）上执行计算密集型任务，同时自动处理线程安全问题，避免竞态条件（Race Condition）。

Job System 的诞生源于 Unity 传统 MonoBehaviour 架构的单线程瓶颈。大量逻辑只能在主线程执行，导致 CPU 多核利用率极低。Job System 通过将工作分解为独立的"Job"单元分发到线程池（Thread Pool），使 8 核或 16 核 CPU 的算力得以充分利用。Unity 内部测试数据表明，在粒子物理模拟等场景中，使用 Job System 后性能提升可达 **10 倍以上**。

Job System 与 Burst Compiler 和 ECS 共同构成 DOTS 体系。Job System 负责调度与并发安全，Burst 负责将 Job 内的 C# 代码编译为高效本机代码，二者组合是 Unity 高性能计算路线的基础设施。

---

## 核心原理

### Job 结构体与 IJob 接口

每个 Job 必须是一个实现了特定接口的 `struct`（值类型），而非 `class`。Unity 提供多种 Job 接口：

- `IJob`：执行单次操作
- `IJobFor`：对一个范围内的索引并行执行相同逻辑（类似 `for` 循环的并行版本）
- `IJobParallelFor`：功能与 `IJobFor` 相似，但调度方式略有不同
- `IJobParallelForTransform`：专用于并行处理 `Transform` 数组

使用 `struct` 而非 `class` 是有意为之：值类型数据会被**复制**到 Job 中，杜绝了多线程同时访问同一内存地址的可能，这是 Job System 实现线程安全的基础机制之一。

```csharp
struct MyJob : IJobFor
{
    public NativeArray<float> results;
    public float multiplier;

    public void Execute(int index)
    {
        results[index] = index * multiplier;
    }
}
```

### JobHandle 与依赖链管理

调度一个 Job 后，`Schedule()` 方法返回一个 `JobHandle`。这个句柄代表该 Job 的"完成凭证"，可以传递给后续 Job 的 `Schedule()` 调用，形成**依赖链（Dependency Chain）**。

```csharp
JobHandle jobA = jobA_instance.Schedule();
JobHandle jobB = jobB_instance.Schedule(jobA); // jobB 等待 jobA 完成后才开始
JobHandle combined = JobHandle.CombineDependencies(jobA, jobB); // 合并多个依赖
```

Unity 运行时会基于这些依赖关系构建一张**有向无环图（DAG）**，自动推断哪些 Job 可以并行执行，哪些必须串行。开发者无需手动管理线程锁（mutex），依赖关系声明即隐式保证了内存访问顺序的正确性。

调用 `jobHandle.Complete()` 会将主线程阻塞，直到目标 Job 及其所有依赖均完成，通常在需要从主线程读取结果时调用。

### NativeContainer 与内存安全

Job 内部**不能**使用托管类型（如 `List<T>`、普通数组），只能使用 `NativeContainer` 系列类型，包括：

| 类型 | 用途 |
|---|---|
| `NativeArray<T>` | 定长数组 |
| `NativeList<T>` | 动态列表（需 Allocator.Persistent 或 TempJob）|
| `NativeHashMap<K,V>` | 键值对映射 |
| `NativeQueue<T>` | 先进先出队列 |

`NativeContainer` 内部通过**原子操作（Atomic Operation）**和**安全句柄（AtomicSafetyHandle）**在 Editor 模式下追踪读写冲突。若两个 Job 同时写入同一 `NativeArray`，Unity 会在 Editor 中抛出异常，帮助开发者在开发期发现并发错误。`[ReadOnly]` 和 `[WriteOnly]` 属性标注可放宽并发限制，允许多个 Job 同时读取同一数据。

分配 `NativeContainer` 时需指定 **Allocator** 类型：
- `Allocator.Temp`：仅当帧内有效，最快
- `Allocator.TempJob`：最长存活 4 帧，适合跨帧 Job
- `Allocator.Persistent`：长期存活，须手动调用 `.Dispose()`

### 批处理大小（Batch Size）与调度开销

`IJobParallelFor` 的 `Schedule(arrayLength, innerLoopBatchCount)` 中，`innerLoopBatchCount` 指定每个工作线程每次领取的最小任务数量。该值过小（如 1）会造成频繁的任务分发开销；过大（如与数组等长）则退化为单线程执行。典型推荐值为 **64 或 128**，但实际最优值需根据 Execute 方法的计算量通过 Profiler 测定。

---

## 实际应用

**大规模 AI 路径查询**：游戏中有 5000 个敌人单位需要每帧更新寻路方向向量。使用 `IJobParallelFor` 将 5000 次向量计算分散到所有工作线程，主线程仅负责提交 Job 和读取结果，帧时间从 12ms 降至约 1.5ms。

**流体/布料物理模拟**：顶点位置更新属于纯数学运算（无随机写冲突），适合用 `IJobFor` 并行化。每个 Execute(index) 计算第 index 个顶点在弹簧力下的新位置，写入独立的 `NativeArray<float3>`，天然满足无竞争条件。

**ECS System 内的 Job 调度**：在 Unity ECS 中，`SystemBase` 的 `OnUpdate()` 使用 `Entities.ForEach().ScheduleParallel()` 本质上是自动生成并调度 `IJobChunk`。Job System 的 `Dependency` 属性在各 System 间自动传递，保证组件数据的访问顺序正确。

---

## 常见误区

**误区一：认为 `Complete()` 越早调用越安全**

很多开发者在 Schedule 后立刻调用 `Complete()`，实际上这使 Job 与主线程完全串行，丧失了并行价值。正确做法是在当帧尽可能晚地调用 `Complete()`——理想情况是在同帧最后需要读取结果的地方才调用，让 Job 在主线程处理其他逻辑的同时在后台运行。

**误区二：在 Job 内部 new 托管对象**

Job 的 `Execute()` 方法中绝对不能执行 `new List<T>()`、字符串拼接等产生 GC 分配的操作，因为工作线程上的托管内存分配行为未被 Unity 支持，轻则产生 GC 压力，重则崩溃。所有数据须在 Schedule 前通过 `NativeContainer` 准备好。

**误区三：混淆 `IJobFor` 与 `IJobParallelFor` 的调度机制**

`IJobFor` 通过 `ScheduleParallel(length, batchSize, dependency)` 调度，Unity 的线程调度器会自动按批次分配给工作线程；而 `IJobParallelFor` 使用 `Schedule(length, batchSize, dependency)`。二者接口几乎相同，但 `IJobFor` 是更新的 API（2020.1+），在某些情况下调度效率更优，新项目建议优先使用 `IJobFor`。

---

## 知识关联

**前置概念——ECS 架构**：Job System 中的 `NativeArray<T>` 与 ECS 中 ComponentData 的内存布局（SoA，Structure of Arrays）高度契合。ECS 中 Chunk 内的组件数据本身就是连续内存块，可直接作为 `IJobChunk` 的输入，无需额外拷贝。理解 ECS 的 Archetype 和 Chunk 机制有助于写出真正零拷贝的 Job。

**协同概念——Burst Compiler**：Job System 决定"在哪个线程执行"，Burst Compiler 决定"执行的机器码质量"。一个 `IJobFor` 加上 `[BurstCompile]` 属性后，Burst 会对 `Execute()` 内的数学运算进行 SIMD 向量化（如将 4 次 float 运算合并为单条 SSE 指令），在 Job System 并行化的基础上再叠加单线程指令级加速。

**对比参考——C# async/await**：Job System 与 C# 原生异步模型本质不同。`async/await` 基于任务延续（Continuation），主要用于 I/O 异步，运行在线程池但无强制内存安全约束；Job System 面向 CPU 密集型计算，通过 `NativeContainer` 和依赖声明提供编译期与运行期双重安全保障，是专为游戏帧循环设计的确定性调度系统。
