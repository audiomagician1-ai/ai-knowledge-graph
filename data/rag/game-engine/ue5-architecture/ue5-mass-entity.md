---
id: "ue5-mass-entity"
concept: "Mass Entity Framework"
domain: "game-engine"
subdomain: "ue5-architecture"
subdomain_name: "UE5架构"
difficulty: 3
is_milestone: false
tags: ["ECS"]

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


# Mass Entity Framework

## 概述

Mass Entity Framework（简称 Mass）是 Unreal Engine 5 中引入的一套基于数据导向设计（Data-Oriented Design, DOD）的大规模实体处理系统，专门用于同屏管理数以万计的游戏实体。它在 UE5.0 首次公开亮相，并在《黑客帝国觉醒》技术演示中用于驱动街道上大量行人与车辆的 AI 行为模拟。Mass 并不是对传统 Actor 系统的替代，而是专门针对"大量同类实体"场景的补充方案，当 Actor-Component 模型因为堆内存碎片和 Blueprint 虚函数调用产生性能瓶颈时，Mass 通过连续内存布局和批量处理提供数量级的性能提升。

Mass 的设计哲学来源于 Entity Component System（ECS）架构，但 Epic 在实现上做了符合 UE 工作流的本土化改造。与纯 ECS 框架不同，Mass 将数据容器称为 **Fragment**，将逻辑单元称为 **Processor**，并通过 **Archetype** 的概念将相同 Fragment 组合的实体聚合到同一块连续内存中，使得 CPU 缓存命中率极大提升。在 UE5.1 之后，Mass 与 StateTree、ZoneGraph 和 Smart Objects 深度集成，成为构建大规模 AI 群体行为的官方推荐技术栈。

## 核心原理

### Fragment、Tag 与 Archetype 的内存模型

Mass 中的实体本身只是一个轻量索引句柄（`FMassEntityHandle`），由 32 位的 Index 和 32 位的 SerialNumber 组成，总共 8 字节。实体的数据存储在 **Fragment** 中，Fragment 必须继承 `FMassFragment`，本质上是普通的 UStruct。例如定义一个位置 Fragment：

```cpp
USTRUCT()
struct FTransformFragment : public FMassFragment {
    GENERATED_BODY()
    FTransform Transform;
};
```

**Tag** 是不携带数据的零大小标记（继承 `FMassTag`），用于分类筛选。**Archetype** 则是指拥有完全相同 Fragment+Tag 组合的实体集合，它们的数据被存储在名为 **Chunk** 的连续内存块中，每个 Chunk 默认大小为 128KB。这种布局使得遍历同一 Archetype 的实体时，CPU 预取机制可以高效工作，相比随机访问 Actor 对象指针的方式，L1 缓存命中率提升可达 10 倍以上。

### Processor 的执行管线

**Processor**（继承 `UMassProcessor`）是 Mass 中执行逻辑的单元。每个 Processor 通过 `FMassEntityQuery` 声明它需要读写的 Fragment 类型，系统据此在 Processor 之间自动推导数据依赖并生成并行执行图。例如一个移动 Processor 只需声明对 `FTransformFragment` 的写权限和对 `FVelocityFragment` 的读权限，系统便可以将它与其他不访问这两个 Fragment 的 Processor 安全地并行执行。

Processor 的 `Execute` 函数接收 `FMassEntityManager` 和 `FMassExecutionContext`，通过 `EntityQuery.ForEachEntityChunk()` 对每个 Chunk 批量迭代，而非逐实体调用虚函数。这意味着一次函数调用可以处理 Chunk 中所有实体（通常数百个），彻底消除了 Actor Tick 中每帧对每个对象调用 `Tick()` 虚函数的开销。Processor 可以通过 `ExecutionOrder` 宏指定执行阶段，内置阶段包括 `PrePhysics`、`PostPhysics`、`FrameEnd` 等。

### 与 Actor 的桥接机制

Mass 提供了 `UMassAgentComponent`，可以挂载在普通 Actor 上，实现 Mass 实体与 Actor 之间的双向数据同步。这个机制称为 **Mass-Actor 桥接（Mass-Actor Bridge）**，在《黑客帝国觉醒》演示中，近景的高细节 NPC 使用 Actor 渲染，远景的大量人群使用 Mass 实体配合 LOD 降级为简单网格体。桥接时，位置数据每帧从 Mass Fragment 同步回 Actor 的 Transform，避免了直接用 Actor 管理海量实体时 `USceneComponent` 的层级遍历开销。

## 实际应用

在 UE5 的城市人群模拟场景中，Mass 配合 **Mass Crowd** 插件可以在单帧内稳定处理 50,000+ 个行人实体。每个行人实体携带 `FMassVelocityFragment`、`FMassForceFragment`、`FAgentRadiusFragment` 等 Fragment，Processor 链按顺序执行：`UMassSteeringProcessor` 计算转向力 → `UMassMovementProcessor` 积分速度和位置 → `UMassObstacleAvoidanceProcessor` 处理碰撞回避。整个链条在多核 CPU 上并行分发，单帧处理时间可控制在 2ms 以内。

在 RTS 游戏的单位管理中，开发者可以用 Mass 管理数千个士兵单位的移动与攻击逻辑，仅在单位被玩家选中时才动态附加 `UMassAgentComponent` 提升细节交互，其余时间以纯 Mass 实体形式存在，内存占用比等效 Actor 方案减少约 70%。

## 常见误区

**误区一：Mass 是 UE5 中 Actor 的替代品。** Mass 实体默认不具备渲染能力、物理碰撞响应或网络同步等 Actor 内置功能。它没有 `USceneComponent`，本身不可见，必须配合 `UMassRepresentationProcessor` 和 ISM（Instanced Static Mesh）才能渲染。试图用 Mass 完全替换具有复杂交互的主角或关键 NPC 会导致大量功能需要手动重新实现。

**误区二：直接修改 Fragment 数据是线程安全的。** 在 `ForEachEntityChunk` 回调外部随意修改 Fragment 会破坏 Mass 的并行执行模型。修改实体的 Fragment 组合（例如添加或删除 Fragment）必须通过 `FMassCommandBuffer` 提交延迟命令，在当前帧执行完毕后统一应用，直接调用 `EntityManager.AddFragmentToEntity()` 在多线程执行期间是不安全的。

**误区三：Archetype 数量越少越好，应尽量统一所有实体的 Fragment 组合。** 强行将不需要某个 Fragment 的实体也加入该 Fragment 会浪费内存，且导致 Chunk 中有效数据密度降低，反而影响缓存效率。正确做法是为不同行为阶段的实体使用 Tag 切换或 Fragment 增减来自然分化 Archetype，接受 Archetype 数量在合理范围内（通常数十个）增长。

## 知识关联

掌握 **Actor-Component 模型**是学习 Mass 的必要前提，因为理解 Actor 在对象层级、垃圾回收和蓝图系统中的开销，才能真正理解 Mass 在哪些场景下能够替代或补充 Actor。Actor 的 `Tick` 机制与 Mass 的 `Processor` 执行管线形成直接对比：前者是面向对象的逐对象虚函数分发，后者是数据导向的批量 Chunk 迭代，两者的 CPU 访问模式截然不同。

Mass 在 UE5 技术栈中向上与 **StateTree**（层级状态机）和 **ZoneGraph**（路径感知图）紧密集成：StateTree 通过 `FMassStateTreeFragment` 驱动 Mass 实体的高层决策，ZoneGraph 为 Mass Crowd 提供大规模寻路的轻量车道数据。理解 Mass 的 Fragment-Processor 数据流模型，是后续使用这套完整 AI 群体行为工具链的基础。