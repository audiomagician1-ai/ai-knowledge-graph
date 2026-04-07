---
id: "se-ue5-mass"
concept: "UE5 Mass Entity"
domain: "software-engineering"
subdomain: "ecs-architecture"
subdomain_name: "ECS架构"
difficulty: 3
is_milestone: false
tags: ["UE5"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 82.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---


# UE5 Mass Entity

## 概述

UE5 Mass Entity 是 Unreal Engine 5 中以数据驱动方式处理大规模实体的 ECS 框架，正式随 UE5.0 在 2022 年发布，并在《黑客帝国：觉醒》技术演示中首次公开展示，该演示在 PS5/XSX 上实时渲染了超过 35,000 个具备完整 AI 行为的行人。Mass Entity 并非对传统 UE `AActor` 系统的替代，而是专门为"需要数量但不需要完整 Actor 功能"的对象群体设计的轻量级并行计算层。

与 Unity DOTS ECS 从零构建不同，Mass Entity 必须与现有 UE 生态（GameplayAbility、NavMesh、Niagara）协作，因此它引入了 **Traits**、**Fragments**、**Processors** 三个独立于 Actor 的概念层，并通过 `UMassEntitySubsystem` 作为全局单例管理所有实体生命周期。这种"寄生"架构使迁移成本降低，但也带来了与 Actor 通信的桥接开销。

Mass Entity 的核心价值在于其**内存连续性**：同类型实体的 Fragment 数据被存储在连续的内存块（Archetype Chunk）中，每个 Chunk 默认容量为 128 个实体（可通过 `GetChunkReserveSize()` 修改），这使 CPU Cache 命中率相比散列的 Actor 对象有数量级的提升。

## 核心原理

### Fragment 与 Archetype

**Fragment** 是 Mass Entity 中最小数据单元，必须继承自 `FMassFragment` 结构体，例如：

```cpp
USTRUCT()
struct FMyVelocityFragment : public FMassFragment {
    GENERATED_BODY()
    FVector Velocity = FVector::ZeroVector;
};
```

多个 Fragment 的组合定义了 **Archetype**（原型）。当一个实体同时拥有 `FTransformFragment` 和 `FMyVelocityFragment` 时，它被归入对应 Archetype 的 Chunk 中。当实体增减 Fragment 时（例如添加 `FMassStateTreeFragment`），它会**迁移至新 Archetype 的 Chunk**，这一操作涉及内存拷贝，是 Mass Entity 中性能敏感的操作点。

除 Fragment 外，**Tag** 继承自 `FMassTag`，占用零字节内存，仅用于 Archetype 分类过滤（如 `FMassMovingTag`）；**Shared Fragment** 继承自 `FMassSharedFragment`，被同 Archetype 内的所有实体共享，适合存储配置数据。

### Processor 的执行模型

**Processor** 继承自 `UMassProcessor`，通过 `FMassEntityQuery` 声明所需 Fragment，引擎在多线程环境下将匹配的 Chunk 分批分发给各 Processor。一个典型的 Processor 结构如下：

```cpp
void UMyMovementProcessor::Execute(FMassEntityManager& EntityManager,
                                    FMassExecutionContext& Context) {
    EntityQuery.ForEachEntityChunk(EntityManager, Context,
        [](FMassExecutionContext& Context) {
            auto Velocities = Context.GetMutableFragmentView<FMyVelocityFragment>();
            auto Transforms = Context.GetMutableFragmentView<FTransformFragment>();
            for (int32 i = 0; i < Context.GetNumEntities(); ++i) {
                Transforms[i].GetMutableTransform().AddToTranslation(
                    Velocities[i].Velocity * Context.GetDeltaTimeSeconds());
            }
        });
}
```

Processor 通过 `ExecutionOrder` 的 `ExecuteBefore`/`ExecuteAfter` 声明依赖关系，由 **Processing Phase** 系统（分为 `PrePhysics`、`StartPhysics`、`EndPhysics`、`PostPhysics`、`FrameEnd` 五个阶段）决定并行调度策略。

### Traits 与 UE Gameplay 集成

**Trait** 继承自 `UMassEntityTraitBase`，是 Mass Entity 与 UE Gameplay 系统的桥梁。例如 `UMassStateTreeTrait` 将 UE5 的 StateTree（状态机）绑定到 Mass 实体上，使每个轻量实体无需成为 Actor 即可运行完整 AI 逻辑。`UMassLODTrait` 则基于距离动态切换实体的 Fragment 组成——远处实体只保留 Transform，近处实体增加动画、碰撞 Fragment，实现自动 LOD。

`UMassAgentComponent` 是 Actor 与 Mass 实体之间的同步组件：将它挂载在 Actor 上后，Actor 的 Transform 变化会自动同步至对应的 Mass 实体 Fragment，反之亦然，这是 Mass Entity 复用现有 Actor 逻辑的标准路径。

## 实际应用

**大规模 NPC 群体**：在开放世界游戏中，城市行人使用 Mass Entity 管理，每个行人实体携带 `FMassTransformFragment`、`FMassVelocityFragment`、`FMassNavigationEdgesFragment` 等约 8-12 个 Fragment。当玩家接近时，`UMassLODTrait` 自动为该实体生成 Skeletal Mesh 的可视化表示（通过 Niagara 或 ISM），而远处行人仅作为数据在 Mass Processor 中移动，GPU 无任何对应消耗。

**弹药与抛射物**：子弹、箭矢等短生命周期大量对象是 Mass Entity 的理想场景。相比为每颗子弹生成 `AActor`（涉及 `SpawnActor`、GC 开销），Mass 实体的创建通过 `UMassEntitySubsystem::BatchCreateEntities()` 批量完成，单帧可创建数千实体而不触发 GC Spike。

**RTS 单位管理**：策略游戏中的兵种群体可将寻路指令存入 `FMassSharedFragment`（同阵营共享目标点），配合 Mass Avoidance Processor 实现群体回避，无需为每个单位维护独立的 `PathFollowingComponent`。

## 常见误区

**误区一：Mass Entity 可以完全替代 AActor**。Mass 实体天生不支持蓝图事件图（Event Graph）、不参与 `UWorld::LineTraceSingleByChannel` 的默认碰撞响应、无法直接挂载 `UActorComponent`。对于需要响应 Gameplay Events、拥有复杂交互逻辑的角色，仍需使用 Actor；Mass 的价值在"量大但逻辑简单"的对象。

**误区二：Fragment 可以像 Actor 属性一样频繁增删**。每次 Fragment 的增删都会触发 Archetype 迁移（内存拷贝），若每帧对数千实体动态增删 Fragment，性能损耗反而超过普通 Actor。正确做法是用 **Tag** 替代状态 Fragment，或用 Fragment 内部的枚举字段表示状态切换，将 Archetype 迁移控制在初始化或低频事件时进行。

**误区三：Mass Entity 自动处理网络同步**。Mass Entity 本身不内置 Replication 机制，`FMassFragment` 不继承自任何可复制结构。网络同步需要额外通过 `UMassReplicationSubsystem`（实验性）或手动将 Mass 数据桥接回 Actor 的 `UPROPERTY(Replicated)` 字段来实现，这是当前 Mass Entity 生产环境落地的主要障碍之一。

## 知识关联

**前置概念**：理解 ECS 架构概述中 Component 连续内存布局对 Cache 效率的影响，是理解 Mass Entity 的 Archetype Chunk 为何设计为128实体固定容量的直接依据。Unity DOTS ECS 的 `IJobChunk` 与 Mass Entity 的 `ForEachEntityChunk` 在设计哲学上高度相似——两者都将多线程并行粒度定为 Chunk 而非单个实体——但 Mass 的 Processor 依赖声明（`ExecuteBefore`/`ExecuteAfter`）比 DOTS 的 Job dependency handle 更语义化。

**后续概念**：ECS 网络同步是 Mass Entity 当前最薄弱的环节。`UMassReplicationSubsystem` 的设计思路是将 Mass 实体的状态变化打包为差量（Delta），通过 UE 的 NetDriver 批量发送，避免为每个实体生成独立的 RPC 调用。掌握 Mass Entity 的 Fragment 结构和 Processor 执行时序，是理解如何在 ECS 网络同步中设计最小化复制集的直接前提。