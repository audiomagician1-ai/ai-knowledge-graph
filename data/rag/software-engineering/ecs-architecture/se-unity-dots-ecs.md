---
id: "se-unity-dots-ecs"
concept: "Unity DOTS ECS"
domain: "software-engineering"
subdomain: "ecs-architecture"
subdomain_name: "ECS架构"
difficulty: 3
is_milestone: false
tags: ["Unity"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---


# Unity DOTS ECS

## 概述

Unity DOTS（Data-Oriented Technology Stack）ECS 是 Unity Technologies 于 2019 年开始正式推进、2022 年随 Unity 2022 LTS 趋于稳定的官方数据导向架构实现。它将经典 ECS 思想与 Unity 的 C# Job System 和 Burst 编译器深度整合，形成一套完整的高性能运行时框架。相比 Unity 传统的 MonoBehaviour 模式，DOTS ECS 在大规模实体场景下的 CPU 利用率可提升数倍至数十倍，官方 Demo 中曾展示同屏 10 万单位的实时模拟。

DOTS ECS 的包名为 `com.unity.entities`，其核心设计目标是让 C# 代码能够被 Burst 编译器编译成接近原生 C++ 甚至 SIMD 优化的机器码。这一目标直接决定了框架的诸多约束：Component 必须是 `unmanaged` 的值类型（struct），不允许包含托管引用，从而保证数据可以在连续内存块（称为 Archetype Chunk）中线性排列。

DOTS ECS 之所以重要，在于它是目前主流游戏引擎中唯一一个将 ECS、SIMD 并行化与主流脚本语言（C#）深度融合的生产级实现。开发者无需切换到 C++ 即可获得接近底层的运行时性能，这使得 Unity 生态在移动端和主机端的大规模模拟类游戏开发中具备独特竞争力。

---

## 核心原理

### Archetype 与 Chunk 内存模型

DOTS ECS 将所有拥有相同 Component 类型集合的 Entity 归入同一个 **Archetype**。每个 Archetype 下的实体数据存储在固定大小为 **16 KB** 的内存块（Chunk）中。以一个包含 `Position`（12 字节）和 `Velocity`（12 字节）的 Archetype 为例，每个 Chunk 最多存放约 **682** 个实体（16384 / 24 ≈ 682）。这种 SoA（Struct of Arrays）布局使 CPU 缓存行的利用效率极高，遍历时几乎不产生 cache miss。

当一个 Entity 新增或删除 Component 时，它会从原 Archetype 迁移到新 Archetype，涉及一次跨 Chunk 的数据拷贝。这一操作的成本是 DOTS ECS 结构变更（Structural Change）代价较高的根本原因，也是为何框架提供 `EnableableComponent` 接口来替代频繁增删组件的原因。

### SystemBase 与 ISystem 两套 API

DOTS ECS 提供两套系统编写方式：`SystemBase`（托管类，支持 Lambda 查询）和 `ISystem`（unmanaged struct，完全 Burst 化）。

使用 `ISystem` 配合 `[BurstCompile]` 标记时，系统的 `OnUpdate` 方法本身也会被 Burst 编译，从而消除 C# 托管层的调用开销。典型写法如下：

```csharp
[BurstCompile]
public partial struct MoveSystem : ISystem {
    public void OnUpdate(ref SystemState state) {
        foreach (var (transform, velocity) in
            SystemAPI.Query<RefRW<LocalTransform>, RefRO<Velocity>>()) {
            transform.ValueRW.Position += velocity.ValueRO.Value * SystemAPI.Time.DeltaTime;
        }
    }
}
```

`RefRW<T>` / `RefRO<T>` 明确区分读写权限，调度器据此自动推断 Job 依赖关系，避免数据竞争。

### Burst 编译器集成

Burst 编译器基于 LLVM 后端，能将满足 HPC# 子集限制的 C# 代码编译为高度优化的本地代码，包括自动向量化（AVX2/NEON 等 SIMD 指令集）。HPC# 的核心限制是：禁止托管对象引用、禁止虚函数调用、禁止抛出托管异常。

Burst 与 DOTS ECS 的结合点在于 **IJobChunk** 接口：开发者以 Chunk 为粒度编写批处理逻辑，Burst 可以对 Chunk 内的连续数组循环自动展开并向量化。官方基准测试显示，相同逻辑在 Burst 下比普通 C# 快 **4x–20x**，在开启 SIMD 的情况下最高可达 **50x**。

### World 与 SystemGroup 调度

DOTS ECS 中所有 Entity 和 System 归属于一个 **World** 实例。Unity 默认创建一个 `DefaultWorld`，也支持创建自定义 World 用于隔离模拟（如服务端逻辑与客户端逻辑分离）。系统以 `SystemGroup` 树形结构组织，内置三大根组为 `InitializationSystemGroup`、`SimulationSystemGroup`、`PresentationSystemGroup`，执行顺序通过 `[UpdateBefore]`/`[UpdateAfter]`/`[UpdateInGroup]` 属性声明式指定。

---

## 实际应用

**大规模 AI 单位模拟**：《Megacity Metro》是 Unity 官方 2023 年发布的 DOTS ECS 示范项目，包含超过 **10 万**个动态 NPC 单位在同一城市场景中同时寻路与渲染。每个 NPC 的位置、速度、动画状态均以 ECS Component 存储，寻路逻辑以 `IJobChunk` 实现并行化，整体帧率在主机端维持 60 FPS。

**物理驱动的粒子系统**：利用 `EntityCommandBuffer`（ECB）在 Job 内批量生成和销毁粒子 Entity，ECB 将结构变更延迟到主线程 Sync Point 统一执行，避免 Job 执行期间的并发写冲突。这是 DOTS ECS 处理动态数量实体的标准模式。

**网络同步（Netcode for Entities）**：Unity 官方网络包 `com.unity.netcode` 直接构建于 DOTS ECS 之上，使用 Ghost Component 标记需要同步的 Component 类型，服务端快照以 Chunk 粒度序列化，充分利用 SoA 内存布局的批量读取优势。

---

## 常见误区

**误区一：认为 DOTS ECS 是 MonoBehaviour 的简单替代**
DOTS ECS 不支持继承、不支持 Unity 协程（Coroutine）、不兼容大多数 Asset Store 插件。它是一套独立的运行时，与传统 GameObject 世界交互需要通过 `EntityManager.Instantiate` 将 Prefab 烘焙（Bake）成 Entity，且该烘焙过程发生在 Editor 阶段或加载阶段，而非运行时动态转换。将其视为"更快的 MonoBehaviour"会导致架构决策失误。

**误区二：所有 Component 都应该尽可能小**
虽然缓存友好确实重要，但过度拆分 Component 会增加 Archetype 数量，导致查询时需要匹配更多 Archetype，反而影响 `EntityQuery` 的遍历效率。实践建议是将**同一 System 频繁同时读写**的字段合并为一个 Component，而非按语义强行拆分。

**误区三：Burst 标记即可保证最优性能**
`[BurstCompile]` 只是编译优化的前提，若代码中存在随机内存访问（如通过 Entity 引用跳转到另一个 Archetype 的数据），Burst 无法消除由此产生的 cache miss。`IJobChunk` 的性能优势建立在**线性访问**模式上；引入 `ComponentLookup<T>`（旧称 `ComponentDataFromEntity`）做随机访问时，性能会显著下降，需要通过数据结构重设计来规避。

---

## 知识关联

**前置概念**：理解 **ECS 架构概述**中的 Archetype-Chunk 数据布局是使用 DOTS ECS 的必要前提，尤其是 SoA 内存模型与传统 AoS（Array of Structs）的性能差异。**Flecs 框架**提供了对比参照：Flecs 同样以 Archetype 为核心但运行于 C/C++ 原生环境，对比二者可以帮助理解 DOTS ECS 在 C# 托管运行时上为实现 Burst 兼容所做的诸多约束与取舍，例如禁止托管引用的规定在 Flecs 中并不存在。

**后续概念**：**UE5 Mass Entity** 是虚幻引擎对同类问题的解答，其 Fragment（等价于 Component）、Processor（等价于 System）与 DOTS ECS 的概念高度对应，但 Mass Entity 深度集成了 UE5 的 Niagara 粒子系统和 State Tree，适用场景侧重于群体 AI 而非通用 ECS。对比学习 Mass Entity 有助于理解不同引擎在 ECS 工程化实现上的差异化选择。