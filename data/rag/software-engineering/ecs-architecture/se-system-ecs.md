---
id: "se-system-ecs"
concept: "System系统"
domain: "software-engineering"
subdomain: "ecs-architecture"
subdomain_name: "ECS架构"
difficulty: 2
is_milestone: true
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 41.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.4
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# System系统

## 概述

在ECS架构中，System（系统）是唯一负责执行游戏逻辑的处理单元。Entity只是一个ID，Component只是纯数据，所有的行为和计算都集中在System中完成。一个System的典型职责是：每帧遍历所有满足特定Component组合条件的Entity，读取或修改其Component数据。这种"数据与逻辑分离"的设计使得逻辑代码高度集中且易于测试。

System的概念随着ECS架构的成熟而演化。2007年前后，Adam Martin在其博客系列文章中明确将System定义为ECS三要素之一，强调System本身不应持有任何游戏状态数据。2019年Unity正式发布DOTS（Data-Oriented Technology Stack）中的ECS实现时，将System进一步细化为`SystemBase`和`ISystem`两种基类，前者托管于C#对象，后者为非托管结构体，每帧调用`OnUpdate()`方法执行逻辑。

System的价值在于其极致的关注点分离：一个`MovementSystem`只处理位移计算，一个`DamageSystem`只处理伤害结算，它们之间不直接调用，而是通过Component数据间接协作。这种架构使得在一个拥有10万个Entity的场景中，新增或移除某个逻辑模块只需添加或禁用对应System，无需修改Entity或Component的定义。

## 核心原理

### 查询遍历：System的执行方式

System通过**查询（Query）**来获取目标Entity集合。查询条件本质上是一组Component类型的组合，例如"同时拥有`Position`和`Velocity`这两个Component的所有Entity"。在Unity ECS中，这通过`EntityQuery`对象表达：

```
EntityQuery query = GetEntityQuery(
    ComponentType.ReadOnly<Velocity>(),
    ComponentType.ReadWrite<Position>()
);
```

System每帧在`OnUpdate()`中对查询结果进行遍历，批量读写匹配Entity的Component数据。这与传统OOP中逐对象调用`Update()`方法不同——ECS的遍历是线性内存访问，因为同类型Component在内存中连续排列（Archetype Chunk机制），CPU缓存命中率极高。对于10万个Entity，ECS的遍历性能可比OOP方式快5到20倍。

### System的生命周期

一个System通常包含三个生命周期方法：
- `OnCreate()`：System首次创建时调用一次，用于初始化查询对象和资源。
- `OnUpdate()`：每帧调用，执行核心逻辑遍历。
- `OnDestroy()`：System销毁时调用，释放Native容器等非托管资源。

System本身不存储Entity数据，`OnUpdate()`内所有数据均来自对Component的读写操作。这意味着同一System在不同帧之间唯一合法的持久状态是算法参数（如重力加速度`9.8f`），而非任何Entity的状态快照。

### System的读写权限声明

System必须显式声明对每个Component的访问权限（ReadOnly或ReadWrite）。这个声明不只是文档注释，而是调度器进行并行安全检验的依据。若`MovementSystem`将`Velocity`声明为`ReadOnly`，而`PhysicsSystem`将`Velocity`声明为`ReadWrite`，调度器可以据此判断这两个System存在写依赖，必须串行执行；反之，两个都只读`Velocity`的System可以安全并行。Unity ECS的`ComponentSystemGroup`调度器正是基于此原理在多线程环境下自动排布System执行顺序。

## 实际应用

**移动系统示例**：一个`TranslationSystem`的完整逻辑是：查询所有同时拥有`LocalTransform`和`Velocity`的Entity，在`OnUpdate()`中用`SystemAPI.Query<RefRW<LocalTransform>, RefRO<Velocity>>()`遍历，将每帧`deltaTime × velocity`累加到`position`上。整个System的代码量通常在20行以内，且不需要引用任何具体GameObject。

**AI决策系统**：`EnemyAISystem`查询拥有`EnemyTag`、`PatrolData`和`Translation`三个Component的Entity，每帧计算每个敌人的下一步路径节点，并将结果写入`MoveTarget` Component。`MovementSystem`随后在同帧内读取`MoveTarget`执行实际移动。两个System通过`MoveTarget`这一Component传递数据，完全解耦，任一System可以独立替换。

**条件禁用**：通过`Enabled = false`可以在运行时禁用某个System，使其`OnUpdate()`停止被调用。这在实现游戏暂停、分阶段加载逻辑时非常实用，无需删除任何Entity或Component数据。

## 常见误区

**误区一：在System中缓存Entity引用**
部分初学者习惯在System字段中存储特定Entity的引用，如`Entity playerEntity`，以便在`OnUpdate()`中直接访问。这违反了System无状态的设计原则。正确做法是使用`Singleton Component`模式：将玩家数据存入唯一的单例Component，通过`SystemAPI.GetSingleton<PlayerData>()`在每帧查询时获取，而非缓存引用。

**误区二：System负责创建和销毁Entity**
System的核心职责是读写Component数据，而不是管理Entity的生命周期。在`OnUpdate()`中直接调用`EntityManager.CreateEntity()`或`DestroyEntity()`会导致结构性变更（Structural Change），强制中断当前正在进行的Chunk遍历并触发同步点（Sync Point），严重影响性能。正确做法是使用`EntityCommandBuffer`收集这些操作，在帧末统一回放执行。

**误区三：一个System处理多种不相关逻辑**
受传统`Update()`方法的影响，开发者容易将移动、动画、碰撞检测全部写入同一个System。这会导致查询条件过于复杂（需要Entity同时具备过多Component），使得原本不需要某个逻辑的Entity被错误地排除在外。ECS的最佳实践是单一职责：一个System只处理一种逻辑，通过细粒度的Component组合精确筛选目标Entity。

## 知识关联

学习System之前需要理解ECS架构概述中的Archetype和Chunk概念，因为System的查询遍历性能优势直接建立在Chunk线性内存布局之上——若不理解内存布局，则无法解释为何ECS的批量遍历比OOP快。

掌握System的基础后，下一步是学习**ECS查询系统**，深入了解如何构造带有`None`、`Any`等过滤条件的复杂EntityQuery，以及`IJobChunk`如何将System的遍历逻辑分发到Worker线程。随后的**System调度**主题将展示`ComponentSystemGroup`如何根据System的读写声明和显式`[UpdateBefore]`/`[UpdateAfter]`特性属性，在帧内构建有向无环图（DAG）来排定所有System的执行顺序。
