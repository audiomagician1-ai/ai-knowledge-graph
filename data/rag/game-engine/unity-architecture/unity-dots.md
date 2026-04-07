---
id: "unity-dots"
concept: "DOTS/ECS架构"
domain: "game-engine"
subdomain: "unity-architecture"
subdomain_name: "Unity架构"
difficulty: 3
is_milestone: false
tags: ["ECS"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# DOTS/ECS架构

## 概述

DOTS（Data-Oriented Technology Stack）是Unity Technologies于2018年开始推出的一套面向数据编程的技术栈，正式稳定版本于2022年随Unity 2022.2发布。它彻底颠覆了Unity传统的GameObject-Component面向对象模型，转而以"数据的内存布局"为设计核心，使CPU缓存命中率最大化，从而在大规模对象模拟中实现数量级的性能提升。

DOTS由三个互相协作的子系统构成：**ECS（Entity Component System）**负责组织数据与逻辑、**Job System**负责多线程并发执行、**Burst Compiler**负责将C#代码编译为高度优化的本机代码。本文聚焦于其中的核心架构——ECS。ECS将传统"对象拥有行为"的OOP思想替换为"系统处理数据"的DOP思想：Entity是纯ID，Component是纯数据结构体，System是纯逻辑处理器。

ECS架构的实际意义在于解决Unity传统方案在大批量对象（如10万个敌兵单位）下的性能瓶颈。MonoBehaviour的Update调用涉及大量虚函数分派和散乱内存访问，而ECS将同类型Component的数据连续排列在称为**Archetype Chunk**的内存块中，每块固定16KB，使CPU在遍历数据时能充分利用L1/L2缓存，避免缓存缺失（Cache Miss）带来的数百个时钟周期的惩罚。

## 核心原理

### Entity与Archetype机制

在ECS中，Entity本质上是一个64位整数ID（包含32位索引和32位版本号），它本身不存储任何数据。一个Entity拥有哪些Component类型，决定了它的**Archetype（原型）**。例如，同时拥有`Translation`、`Rotation`、`PhysicsVelocity`三种Component的所有Entity共享同一Archetype，它们的数据被集中存入同一组Chunk中。

当给Entity添加或移除Component时，Unity会将该Entity从旧Archetype的Chunk迁移到新Archetype的Chunk，这一操作被称为**Structural Change（结构变更）**。结构变更的代价较高，因此ECS提供了`EnabledComponent`机制（Unity 1.0正式引入）允许在不触发结构变更的情况下逻辑性地启用/禁用Component，替代原有的频繁Add/Remove操作。

### Chunk内存布局与SOA排列

每个Archetype Chunk固定占用**16384字节（16KB）**内存，这与主流CPU的L1缓存大小对应。Chunk内部采用**SOA（Structure of Arrays，数组结构体）**而非AOS（Array of Structures）排列：同一Component类型的所有实例字段连续存储。例如，若一个Chunk存储100个Entity的`Translation`数据，则所有100个`float3 Value`字段是连续的内存地址，System在遍历时CPU预取机制能高效加载整个缓存行。

相比之下，传统MonoBehaviour的Transform等数据分散在堆内存各处，遍历10万个Transform意味着10万次不连续内存访问。

### System执行模型与Query

ECS的System继承自`SystemBase`或实现`ISystem`接口（后者为非托管结构体，无GC开销）。System通过**EntityQuery**声明所需Component类型，运行时ECS框架自动筛选匹配的Archetype和Chunk。核心调度方法`Entities.ForEach`或`IJobChunk`会将处理逻辑分发至Job System执行。

System之间的执行顺序通过`[UpdateBefore]`、`[UpdateAfter]`、`[UpdateInGroup]`特性声明，并归属于`SimulationSystemGroup`、`PresentationSystemGroup`等分组，形成有向无环图（DAG）式的确定性执行顺序，这与MonoBehaviour脚本执行顺序难以控制形成了鲜明对比。

### ComponentData类型约束

ECS的Component必须实现`IComponentData`接口，且**只能包含值类型（blittable types）字段**，不允许含有托管引用（如string、class引用）。这一约束保证了数据可被Burst编译器直接处理，也是Chunk内存布局连续性的前提。若确需引用类型，需使用`ManagedComponentData`，但此类Component无法受益于Burst优化。

## 实际应用

**大规模粒子/单位模拟**：Megacity Metro（Unity官方演示项目，2023年更新）在单场景中渲染超过10万个动态单位，包含AI导航、动画状态更新、物理检测，实现60fps运行，这是传统GameObject架构无法达到的规模。

**RTS游戏单位管理**：在实时战略游戏中，数千个单位每帧需要进行移动、攻击范围检测、伤害计算。将`UnitHealthComponent`、`UnitPositionComponent`分离为独立Component，`DamageSystem`通过EntityQuery仅读取生命值数据，`MovementSystem`仅读写位置数据，两个System可并行执行互不干扰，充分利用多核CPU。

**数据驱动的关卡生成**：使用ECS的`Baking`工作流（Unity DOTS 1.0正式引入），设计师在编辑器中摆放传统GameObject，发布时自动"烘焙"为ECS Entity数据，实现工具链兼容性与运行时高性能的兼顾。

## 常见误区

**误区一：ECS只是把MonoBehaviour改名**。许多初学者将ECS的System等同于MonoBehaviour脚本，将Component等同于Unity原有的Component类。实际上ECS的Component是纯数据结构体（相当于C语言的struct），不含任何方法；System是无状态逻辑处理器，不与任何特定Entity绑定。将方法写进`IComponentData`结构体会导致编译错误或绕过Burst优化。

**误区二：所有项目都应迁移至DOTS**。ECS架构的收益在对象数量超过数千时才显著体现。对于UI密集型、对话驱动、关卡设计复杂但单位数量少的游戏，ECS引入的心智负担远超性能收益。Unity官方文档明确指出DOTS适用于"simulation-heavy"场景，中小型项目继续使用GameObject-MonoBehaviour完全合理。

**误区三：Structural Change可以在System主逻辑中随意调用**。在`Entities.ForEach`迭代过程中直接调用`EntityManager.AddComponent`会导致运行时异常，因为修改Chunk结构会使当前迭代的指针失效。正确做法是使用`EntityCommandBuffer`（ECB）记录延迟命令，在迭代结束后的同步点统一执行。

## 知识关联

**与GameObject-Component的关系**：ECS并非对GameObject-Component系统的迭代改进，而是并行存在的替代方案。`Baking`系统（原SubScene Conversion）允许两套系统在同一项目中共存：编辑器工作流保留GameObject，运行时转换为Entity，开发者可渐进式地将性能瓶颈部分迁移至ECS，而无需整体重写项目。

**通向Burst编译器**：ECS的`IComponentData`强制使用blittable值类型这一约束，正是Burst编译器能够对System逻辑生成高度优化SIMD指令的前提。学习ECS后，理解Burst对`[BurstCompile]`的具体要求（禁止托管异常、禁止静态可变状态等）将变得顺理成章，因为这些限制在ECS Component设计阶段已经被部分内化。

**通向Job System**：ECS的System本身不直接执行多线程，它依赖Job System调度`IJobChunk`等Job类型。ECS的EntityQuery天然包含读写依赖信息（`ReadOnly`/`ReadWrite`标注），Job System据此自动推断Job之间的依赖关系，生成安全的并行执行计划。理解ECS的数据流向是正确使用Job System避免竞态条件的基础。