---
id: "se-archetype"
concept: "Archetype存储"
domain: "software-engineering"
subdomain: "ecs-architecture"
subdomain_name: "ECS架构"
difficulty: 3
is_milestone: false
tags: ["存储"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 48.2
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.429
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# Archetype存储

## 概述

Archetype存储是ECS（Entity-Component-System）架构中用于管理实体的一种内存组织策略：将拥有**完全相同组件类型集合**的实体归入同一个Archetype（原型），并在该Archetype内部以连续内存块（Chunk）存储所有这些实体的组件数据。例如，同时拥有`Position`、`Velocity`、`Health`三个组件的实体全部归属于`{Position, Velocity, Health}`这一Archetype，而只有`Position`和`Velocity`的实体则属于另一个独立的Archetype。

这一概念最早被Unity的DOTS（Data-Oriented Technology Stack）框架在2018年前后系统化推广，其底层实现即为`ArchetypeChunk`——每个Chunk默认大小为16KB。Archetype存储解决了传统稀疏组件存储（每类组件单独存放，通过实体ID索引）带来的缓存未命中问题，将同类实体的组件数据紧密排列，使CPU预取机制能够高效工作。

Archetype存储之所以重要，在于它同时实现了两个目标：其一，查询时无需遍历所有实体，只需遍历拥有目标组件集合的Archetype；其二，同一Archetype内的组件数据具备空间局部性，满足现代CPU对连续内存访问的偏好，可将批量组件查询的性能提升一个数量级以上。

---

## 核心原理

### 组件类型集合作为分类键

每个Archetype由其包含的组件类型集合唯一标识，通常以排序后的类型ID列表或位掩码（Bitmask）表示。例如，若系统共定义了8种组件类型，每种类型分配一个比特位，则`{Position=bit0, Velocity=bit1}`对应的Archetype标识为二进制`00000011`。ECS运行时维护一张全局的Archetype注册表，当实体添加或移除组件时，运行时会计算新的类型集合，在注册表中查找或新建对应Archetype，并将该实体迁移（Move）到新Archetype中。

### Chunk内存布局

在Archetype内部，数据以固定大小的Chunk为单位管理。以Unity DOTS为例，每个Chunk固定为16384字节（16KB），与L1缓存行大小对齐。Chunk内部采用列式（Column-wise）排布：同一Chunk内同类组件的数据连续存放，不同组件类型之间依次追加。设一个Archetype包含组件A（8字节/实体）和组件B（12字节/实体），则每个Chunk能容纳的实体数量为：

$$N = \left\lfloor \frac{16384}{8 + 12} \right\rfloor = \left\lfloor \frac{16384}{20} \right\rfloor = 819 \text{（实体）}$$

Chunk内布局示意为：`[A₀, A₁, …, A₈₁₈][B₀, B₁, …, B₈₁₈]`，其中下标代表对应的实体槽位编号。

### 实体迁移机制

当实体的组件集合发生变化（如调用`AddComponent<Shield>(entity)`），Archetype存储必须执行以下步骤：
1. 在目标Archetype（`{Position, Velocity, Shield}`）中分配新槽位；
2. 将源Chunk中该实体的所有组件数据逐字节复制到目标Chunk；
3. 用源Chunk中最后一个实体填补空出的槽位（Swap-and-remove策略），避免产生碎片；
4. 更新全局实体-位置映射表（EntityIndex → ArchetypeID + ChunkIndex + SlotIndex）。

这一迁移操作的时间复杂度为 O(C)，其中C为该实体拥有的组件数量，通常远小于实体总数，因此迁移成本可控。

---

## 实际应用

**游戏中的子弹生命周期管理**：子弹实体初始拥有`{Position, Velocity, Damage, Lifetime}`四个组件，归属同一Archetype。当子弹命中目标后需移除`Velocity`并添加`ExplosionEffect`组件，整批具有相同组合的子弹实体统一迁移到新Archetype`{Position, Damage, Lifetime, ExplosionEffect}`。System在处理"移动逻辑"时只需查询含`Position`和`Velocity`的Archetype，可直接跳过已爆炸的子弹，无需逐实体检查标志位。

**大规模NPC批处理**：一款含有10万个NPC的开放世界游戏中，若8万个NPC同属`{Position, AIState, Health}`这一Archetype，其所有`Health`数据连续排布在约97个16KB Chunk中（每Chunk约819个实体）。AI系统在执行批量伤害计算时，97次Chunk迭代即可完成，内存访问几乎全部命中L1/L2缓存，相比逐实体随机访问稀疏数组可减少80%以上的缓存未命中率（实测数据来源于Bevy ECS 0.12版本Benchmark报告）。

**编辑器工具中的静态实体**：纯静态场景物件（如树木、石块）仅拥有`{Position, RenderMesh}`组件，与动态实体完全分离在不同Archetype中。渲染System只需遍历该Archetype的Chunk，天然实现了静态批处理（Static Batching），无需额外标记。

---

## 常见误区

**误区一：组件添加顺序不同会产生不同Archetype**
事实上，Archetype的唯一标识是组件类型的**集合**，而非有序序列。`AddComponent<A>`再`AddComponent<B>`与先加B后加A，最终得到的是同一个`{A, B}` Archetype。运行时在构建标识键时会对类型ID排序，因此顺序无关。

**误区二：Archetype数量越少越好**
Archetype数量的合理范围取决于实际业务场景。若强行将组件合并以减少Archetype数量，反而会导致单个Archetype内存储大量无关数据，增大每实体的内存占用，降低每个Chunk能容纳的实体数量（N值下降），适得其反。真正需要控制的是**频繁的组件添加/移除**操作所引发的迁移开销，而非Archetype总数本身。

**误区三：Archetype存储等同于SoA布局**
Archetype存储描述的是"按组件组合分类实体并分配Chunk"的管理策略，而SoA（Structure of Arrays）描述的是单个Chunk内部各组件数组的排列形式。前者是组织层面的决策，后者是内存布局层面的实现；Archetype存储在Chunk内部采用SoA，但二者不是同一概念。

---

## 知识关联

**前置概念——Component组件**：理解Archetype存储的前提是明确Component是纯数据结构（无行为逻辑），Archetype正是以Component的类型集合为分类依据。Component的内存大小直接决定公式中的分母，影响每个Chunk能容纳的实体数量N。

**后续概念——SoA数据布局**：Archetype存储天然催生了对Chunk内部排布方式的进一步优化。SoA布局是Chunk内部对同类组件数组连续存放的具体实现形式，使SIMD指令（如AVX2一次处理8个float）能够对同一组件的多个实体数据进行向量化计算。掌握Archetype存储后，学习SoA布局的重点在于理解列式访问模式如何与CPU的SIMD宽度（128/256/512位）对齐。