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
---
# System系统

## 概述

在ECS架构中，System（系统）是唯一负责执行游戏逻辑和业务规则的代码单元。Entity只是一个ID，Component只存储数据，而所有的"行为"——碰撞检测、AI决策、物理模拟、渲染指令提交——都由System实现。这种设计将数据与行为彻底分离，使得System可以独立测试、替换或禁用，而不影响数据本身的完整性。

System的概念由Adam Martin在2007年发表的"Entity Systems are the future of MMOG development"系列文章中首次系统化阐述。他明确提出：System是ECS三要素中唯一包含函数逻辑的部分，一个System应当只关心它所查询的Component类型，对其他数据保持无知（ignorant）。Unity DOTS（Data-Oriented Technology Stack）在2019年正式发布时，将这一原则落地为`ISystem`和`SystemBase`两个接口，强制要求开发者声明System所需的Component访问权限。

System的重要性在于它决定了ECS架构的性能上限。由于System通过查询（Query）批量处理同类Component数据，CPU缓存可以连续读取内存中紧密排列的Component数组，相比面向对象中分散在堆内存的对象引用，缓存命中率提升显著。在Unity DOTS的官方基准测试中，处理10万个移动实体时，基于System的批量处理比传统MonoBehaviour快约40倍。

## 核心原理

### System的查询机制（Query）

System通过声明**Component类型过滤条件**来获取它需要处理的Entity集合，这个过滤条件称为EntityQuery。一个典型的移动System会声明：需要同时拥有`Position`和`Velocity`两个Component的所有Entity。框架在每帧执行前，根据此查询在Archetype表中检索匹配的Chunk（内存块），将它们打包成一个迭代集合传给System。

在Unity DOTS的`IJobChunk`模式中，查询写法如下：

```csharp
// 声明查询：必须有Position(读写)和Velocity(只读)
EntityQuery query = GetEntityQuery(
    ComponentType.ReadWrite<Position>(),
    ComponentType.ReadOnly<Velocity>()
);
```

`ReadOnly`和`ReadWrite`的区分不是语法糖，而是并行调度的关键依据——两个System如果对同一Component类型都声明`ReadOnly`，调度器可以安全地让它们并行运行；只要有一方声明`ReadWrite`，调度器就会强制串行执行。

### System的生命周期方法

Unity DOTS中`SystemBase`提供三个核心生命周期回调：`OnCreate()`在System首次创建时调用一次，用于初始化EntityQuery和缓存ComponentTypeHandle；`OnUpdate()`每帧调用，是实际逻辑所在；`OnDestroy()`在System被销毁时调用，用于释放NativeArray等非托管内存。

一个最小化的移动System示例：

```csharp
public partial class MovementSystem : SystemBase {
    protected override void OnUpdate() {
        float dt = SystemAPI.Time.DeltaTime;
        Entities
            .ForEach((ref Position pos, in Velocity vel) => {
                pos.Value += vel.Value * dt;
            })
            .ScheduleParallel(); // 并行调度到Job线程
    }
}
```

注意`ref`表示读写访问，`in`表示只读访问，这直接映射到底层的`ReadWrite`/`ReadOnly`查询声明，编译器会自动生成对应的EntityQuery代码。

### System的执行顺序控制

多个System之间的执行顺序通过`[UpdateBefore]`、`[UpdateAfter]`和`[UpdateInGroup]`三个Attribute控制。ECS框架默认提供三个执行组：`InitializationSystemGroup`（帧初始化阶段）、`SimulationSystemGroup`（逻辑更新阶段）、`PresentationSystemGroup`（渲染提交阶段）。物理System通常注册在`FixedStepSimulationSystemGroup`中，以固定时间步长（默认60Hz，即约0.01667秒）运行，独立于渲染帧率。

## 实际应用

**弹幕游戏中的子弹移动System**：一个弹幕游戏可能同屏存在5000颗子弹，每颗子弹是一个拥有`BulletPosition`、`BulletVelocity`、`BulletLifetime`三个Component的Entity。`BulletMovementSystem`查询所有同时拥有这三个Component的Entity，在`OnUpdate`中用`ScheduleParallel`将位置更新分发到多个Job线程并行计算。`BulletLifetimeSystem`则在同一帧的稍后阶段（通过`[UpdateAfter(typeof(BulletMovementSystem))]`保证顺序）遍历所有子弹，将`Lifetime`递减，对归零的Entity调用`EntityCommandBuffer.DestroyEntity`标记销毁。

**状态机的System化实现**：敌人AI状态机可以拆分为`EnemyPatrolSystem`、`EnemyChaseSystem`、`EnemyAttackSystem`三个System，每个System通过查询特定的Tag Component（如`PatrolTag`、`ChaseTag`）来筛选当前处于对应状态的敌人。状态切换时只需在Entity上添加或移除对应Tag Component，即可自动改变下一帧哪个System会处理该Entity，无需在单个System内写大量`if/else`分支。

## 常见误区

**误区一：在System中存储可变状态**。有些开发者习惯在System类中定义成员变量来缓存计算中间结果，例如用一个`List<Entity>`成员收集本帧需要销毁的Entity。这破坏了ECS的无状态设计原则，导致System无法安全地并行运行，也使单元测试变得困难。正确做法是使用`EntityCommandBuffer`（一种线程安全的延迟命令队列）或将中间状态显式地存储为Singleton Component（即挂载在单一Entity上的Component）。

**误区二：一个System处理过多的Component类型**。初学者常常写出查询10种以上Component的"上帝System"，试图在一个`OnUpdate`中完成物理、AI、动画的所有逻辑。这不仅降低了代码可维护性，更重要的是，查询中包含的`ReadWrite` Component越多，与其他System产生调度冲突的概率越高，最终迫使调度器将大量System串行化，抵消了ECS并行化的优势。建议单个System的查询声明不超过5种Component类型。

**误区三：混淆System的查询过滤与运行时条件判断**。有开发者在`OnUpdate`内部用`if (HasComponent<DisabledTag>(entity))`逐个跳过不需要处理的Entity，而不是在EntityQuery层面用`.WithNone<DisabledTag>()`排除它们。前者仍然会把不需要处理的Entity纳入迭代循环，浪费CPU时间；后者让框架在构建迭代集合时直接跳过这些Archetype的Chunk，完全避免了无效遍历。

## 知识关联

学习System之前需要理解ECS架构的三元结构——特别是Component作为纯数据容器、Entity作为ID的角色定位，因为System的查询机制正是建立在"根据Entity所拥有的Component类型进行分组"这一基础之上的。

掌握System的基本工作方式后，下一步是学习**ECS查询系统**，深入了解EntityQuery的过滤选项（`WithAll`、`WithAny`、`WithNone`、`WithChangeFilter`），以及如何利用ChangeFilter避免对未发生变化的Component进行重复处理。另一个后续主题是**System调度**，涉及`SystemGroup`的自定义、依赖链（JobHandle dependency chain）的管理，以及如何诊断和解决多个System之间的调度冲突，这些是将ECS性能优势真正发挥出来的关键技术。
