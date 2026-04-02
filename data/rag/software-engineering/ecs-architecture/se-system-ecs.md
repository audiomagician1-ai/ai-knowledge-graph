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
content_version: 4
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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# System系统

## 概述

在ECS架构中，System（系统）是唯一负责执行逻辑的单元。与Entity（实体）只是ID、Component（组件）只是纯数据不同，System不持有任何数据，它的唯一职责是：**遍历符合条件的组件集合，读写数据，产生行为**。一个典型的System可以描述为"找到所有同时拥有Position和Velocity组件的实体，每帧将Velocity加到Position上"。

System的设计思想起源于1998年前后Dungeon Siege引擎开发期间，工程师Scott Bilas在GDC 2002上正式介绍了基于组件的实体系统，其中System作为独立处理层的思路得到推广。Unity DOTS从2019年起将System正式纳入其C# Job System与Burst编译器体系，此时System的"无状态、可并行"特性才被主流引擎大规模工程化。

System之所以重要，在于它将**数据与行为彻底分离**。传统OOP中一个`Character`类既存数据又含`Update()`逻辑，导致继承链臃肿、缓存命中率低。System则让数据（Component）连续排列在内存中，System批量扫描时CPU缓存一次可加载数十个组件，实测在10万实体场景下比OOP方式提速3～10倍。

---

## 核心原理

### 查询（Query）：System的输入门控

System不会处理世界中所有实体，它通过**组件查询**筛选目标。查询本质是一个组件类型的过滤器，语义为：

```
Query = With<A, B> AND Without<C>
```

例如一个MovementSystem的查询为 `With<Position, Velocity> Without<Frozen>`，World在每帧返回满足条件的Entity列表。Bevy引擎的Rust实现中，这条查询写作：

```rust
fn movement_system(mut query: Query<(&mut Position, &Velocity), Without<Frozen>>) {
    for (mut pos, vel) in &mut query {
        pos.x += vel.x;
        pos.y += vel.y;
    }
}
```

查询在编译期或World初始化时就被解析为Archetype索引，运行时直接按内存块迭代，无需哈希查找。

### 无状态原则与副作用限制

标准ECS理论要求System本身**不持有成员变量状态**。System的所有输入来自Component，所有输出写回Component或通过事件/命令队列提交。这一限制保证同一组输入数据，System每次执行结果完全一致（幂等性）——这是后续System并行调度的理论前提。

若确实需要System级别的状态（例如累计帧数、随机数种子），ECS框架提供**Resource**机制：将状态存为单例Resource，System通过`Res<T>`或`ResMut<T>`参数访问，而非存为System的字段。

### 执行体（OnUpdate）与调度钩子

每个System对应一个执行函数，在游戏循环的特定阶段被调度器调用。Unity DOTS定义了若干默认阶段：`InitializationSystemGroup → SimulationSystemGroup → PresentationSystemGroup`，开发者可将System注册到指定Group。Bevy则使用`app.add_systems(Update, my_system)`语法，默认在每帧`Update`阶段执行。

System的时间复杂度与匹配实体数量N成正比：O(N)。因此设计System时应尽量使查询精确，避免`With<>` 为空导致遍历全部实体。

---

## 实际应用

**案例1：物理移动System**
一个2D射击游戏中，BulletMoveSystem查询 `With<Position, Velocity, Bullet>`，每帧执行 `pos += vel * delta_time`，并检查Position是否超出屏幕边界，超出则写入`Despawn`标记组件。整个System约15行代码，不包含任何与子弹以外逻辑的耦合。

**案例2：伤害计算System**
DamageSystem查询同时拥有`Health`和`PendingDamage`组件的实体，执行 `health.value -= pending.amount`，然后移除`PendingDamage`组件。"移除组件"操作在Bevy中通过`Commands::remove::<PendingDamage>(entity)`延迟提交，避免在遍历中修改Archetype结构造成迭代器失效。

**案例3：渲染同步System**
RenderSyncSystem查询 `With<Position, Sprite>`，将ECS中的Position数据写入渲染线程的Transform缓冲区。该System注册在`PresentationSystemGroup`（Unity DOTS命名），确保在物理和逻辑System执行完毕后才同步渲染数据，避免撕裂（Tearing）。

---

## 常见误区

**误区1：System可以直接在遍历中增删组件**
在大多数ECS实现中，System遍历Query期间不能直接修改Archetype结构（增删组件会导致实体迁移到不同Archetype块）。正确做法是将变更存入**命令缓冲区（CommandBuffer / Commands）**，在当前System执行结束后统一Apply。直接修改会导致迭代器跳过实体或访问越界。

**误区2：一个System可以处理多种不相关逻辑**
开发者有时把"移动+动画+音效"写进一个System，认为减少了函数调用开销。实际上这破坏了System的单一职责，使查询条件膨胀（`With<Position, Velocity, AnimationState, AudioSource>`），命中率下降，并且阻碍了后续System并行调度（多个System共享越多组件类型，调度器能并行的可能性越低）。

**误区3：System数量越少性能越好**
每个System的调度开销约为微秒级，现代ECS框架（如Bevy或Flecs）可轻松支持数百个System并行调度。过度合并System带来的维护成本和并行损失，远大于减少System数量带来的调度收益。正确的性能瓶颈通常在Query遍历的内存带宽，而非System数量。

---

## 知识关联

**前置依赖：**
- **ECS架构概述**定义了Entity-Component-System三者的角色分工；在理解System之前必须明确Component只存数据、不含行为，才能理解为什么System需要主动"查询"而非被动"调用"。
- **Component组件**的Archetype存储布局直接决定了System查询的性能特征：同一Archetype的组件在内存中连续存放，System遍历时CPU预取效率极高；不同Archetype间切换则会引发缓存失效。

**后续拓展：**
- **ECS查询系统**深入讲解Query过滤器的`Changed<T>`、`Added<T>`等增量标记，以及QueryFilter的组合规则，是System能力的直接延伸。
- **System调度**基于System声明的Query读写依赖自动推导并行关系——两个System若查询的组件集合无写冲突，调度器可将其分配到不同线程同帧并行执行，这是ECS相对传统游戏循环的核心性能优势所在。