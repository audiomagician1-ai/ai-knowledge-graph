---
id: "se-sparse-set"
concept: "Sparse Set"
domain: "software-engineering"
subdomain: "ecs-architecture"
subdomain_name: "ECS架构"
difficulty: 3
is_milestone: false
tags: ["存储"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.2
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# Sparse Set（稀疏集合）

## 概述

Sparse Set 是一种专为整数集合设计的数据结构，能在 O(1) 时间复杂度内完成查找、添加和删除操作，同时支持以连续内存方式遍历所有有效元素。它由 Briggs 和 Torczon 于 1993 年在论文 *An Efficient Representation for Sparse Sets* 中正式提出，最初用于编译器优化中的活跃变量分析。

在 ECS（Entity-Component-System）架构中，Sparse Set 被广泛用作组件存储的底层数据结构。每个实体（Entity）通常用一个整数 ID 表示，而 Sparse Set 恰好能以该整数 ID 作为键，直接完成 O(1) 的组件关联与访问。相比哈希表，Sparse Set 不存在哈希碰撞，也不需要额外的桶结构，内存布局更加紧凑，缓存命中率显著更高。

Sparse Set 之所以在游戏引擎和高性能 ECS 实现（如 EnTT、Bevy ECS）中大量采用，根本原因在于它同时满足了两个看似矛盾的需求：通过实体 ID 快速随机访问单个组件，以及对所有拥有某组件的实体做连续内存迭代。这对于每帧需要处理数万乃至数十万实体的游戏系统至关重要。

---

## 核心原理

### 双数组结构

Sparse Set 由两个数组构成：

- **sparse（稀疏数组）**：长度等于实体 ID 的最大值域，`sparse[entity_id]` 存储该实体在 dense 数组中的下标。未被使用的位置填充一个无效标记值（通常为 `UINT32_MAX` 或 `-1`）。
- **dense（密集数组）**：仅存储当前已加入集合的有效实体 ID，元素紧密排列，无空洞。

两者的关系满足以下不变式：若实体 `e` 在集合中，则：

```
dense[sparse[e]] == e
```

这一双向验证不仅是查找的依据，也是防止 sparse 数组"脏数据"误判的机制。

### 查找、添加与删除的具体步骤

**查找**（has）：检查 `sparse[e]` 是否是有效下标，且 `dense[sparse[e]] == e`，整个过程只需两次数组访问，严格 O(1)。

**添加**（add）：将 `e` 追加到 dense 末尾（下标设为 `n`），同时令 `sparse[e] = n`，集合大小 `n` 加一，同样 O(1)。

**删除**（remove）：这是 Sparse Set 最精妙的操作。设待删除实体为 `e`，其在 dense 中的下标为 `i = sparse[e]`。将 dense 末尾元素 `last = dense[n-1]` 移到位置 `i`，更新 `sparse[last] = i`，然后将 `n` 减一。整个过程不移动大量数据，仍是 O(1)，但会改变 dense 中元素的相对顺序。

### 与组件数据的配对存储

在实际 ECS 实现中，Sparse Set 通常与一个平行的组件数据数组（`components[]`）配合使用，两者下标严格对齐：`components[i]` 始终对应 `dense[i]` 所指的实体。删除时，组件数据数组也执行相同的"末尾元素填补"操作。这样，系统在遍历某类组件时，可以直接对 `components[]` 做线性扫描，充分利用 CPU 缓存预取，避免随机内存跳转。

EnTT 库（截至 v3.x）的每种组件类型各自维护一个独立的 Sparse Set 实例，sparse 数组按页（page）分配（默认每页 4096 个槽），以避免实体 ID 域过大时造成的内存浪费。

---

## 实际应用

### 游戏引擎中的组件查询

在一个拥有 100,000 个实体的场景中，假设只有 3,000 个实体拥有 `HealthComponent`。使用 Sparse Set 存储时，dense 数组只有 3,000 个元素，每帧遍历所有 `HealthComponent` 只需线性扫描这 3,000 个紧凑条目，而通过实体 ID 查询某实体是否有血量时仍是 O(1)。若改用普通数组按实体 ID 索引，则遍历需扫描 100,000 个槽位，其中绝大多数为空。

### 多组件系统联合查询

当一个系统需要同时处理拥有组件 A 和组件 B 的实体时，ECS 框架会选取两个 Sparse Set 中元素较少的那个进行遍历，并对每个候选实体在另一个 Sparse Set 上执行 O(1) 的 has 检查。这种"遍历小集合 + O(1) 成员查询"的组合策略，比逐一查找两个哈希表的交集效率更高且更可预测。

### 实体销毁时的快速清理

当实体被销毁时，引擎需要从其所有组件的 Sparse Set 中删除该实体。由于每次删除均为 O(1)，即使一个实体拥有 20 种组件，整个清理过程也只需固定时间，不会随实体总数增长而变慢。

---

## 常见误区

### 误区一：sparse 数组越大越浪费内存

初学者常认为 sparse 数组必须与实体 ID 上限等长，因此担心内存开销。实际上，现代 ECS 实现普遍采用分页（paging）策略：sparse 数组被分割为固定大小的页，只在对应页中存在实体时才分配该页的内存。EnTT 默认页大小为 4096 个 `uint32_t`，即每页仅占 16 KB，只有实际被使用的页才会分配，空洞不占用物理内存。

### 误区二：删除操作破坏迭代顺序，因此不能在遍历中删除

Sparse Set 的删除确实会将末尾元素移到被删位置，若在正向遍历 dense 数组时删除当前元素，被移过来的末尾元素将被跳过。正确做法是**反向遍历**（从 `n-1` 到 `0`）时执行删除，或在遍历结束后统一处理删除队列（deferred deletion）。许多 ECS 框架在系统执行期间自动采用延迟删除机制正是出于这一原因。

### 误区三：Sparse Set 等价于 bitset

Bitset 每个位只能表示"是否存在"，无法直接关联组件数据，且遍历有效元素需要逐位扫描（O(N/64)）。Sparse Set 的 dense 数组直接存储有效实体 ID，遍历复杂度为 O(k)（k 为实际元素数），且天然携带组件数据的紧凑布局能力，两者用途和性能特征存在本质差异。

---

## 知识关联

**前置概念——Component 组件**：Sparse Set 存储的是组件实例与实体 ID 之间的映射关系。理解组件是附着在实体上的纯数据结构（无逻辑），有助于理解为何 Sparse Set 要将 dense 实体数组与平行的组件数据数组严格对齐。组件的类型多样性也解释了为何每种组件类型需要独立的 Sparse Set 实例，而非共享一个通用容器。

**衍生方向——Archetype 与 Sparse Set 的对比**：Archetype ECS（如 Unity DOTS）将具有相同组件组合的实体存入同一内存块，对固定组合的批量遍历极为高效，但组件增减时需要移动实体数据。Sparse Set ECS 在组件频繁增删的场景下更有优势，因为删除始终是 O(1) 且只在单个集合内操作。了解 Sparse Set 的具体行为，是评估和选择 ECS 实现方案时的重要判断依据。