---
id: "lru-cache"
concept: "LRU缓存"
domain: "ai-engineering"
subdomain: "data-structures"
subdomain_name: "数据结构"
difficulty: 5
is_milestone: false
tags: ["设计", "缓存"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 49.4
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.452
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# LRU缓存

## 概述

LRU（Least Recently Used，最近最少使用）缓存是一种基于"时间局部性原理"的缓存淘汰策略：当缓存容量已满时，优先驱逐最久没有被访问的数据项。这一策略由操作系统研究者在1960年代提出，最初用于虚拟内存页面置换算法，如今广泛应用于CPU缓存管理、数据库缓冲池（如MySQL的InnoDB Buffer Pool）以及分布式系统中的本地缓存层。

LRU缓存需要同时支持两种O(1)时间复杂度的操作：`get(key)` 查询和 `put(key, value)` 插入或更新。单纯使用数组或普通链表无法满足这一要求——数组随机访问快但插入删除慢，链表插入删除快但查找慢。因此经典实现方案是**哈希表 + 双向链表**的组合结构，两者各自弥补对方的不足。

LRU缓存在AI工程场景中尤为重要：大语言模型推理时的KV Cache管理、Embedding向量的本地缓存、特征存储（Feature Store）中热点特征的加速访问，都依赖LRU或其变体来控制内存占用。LeetCode第146题"LRU缓存"是面试高频题，要求在O(1)时间内完成所有操作。

---

## 核心原理

### 数据结构设计：哈希表 + 双向链表

LRU缓存维护两个结构：
- **哈希表**（`HashMap<key, Node*>`）：实现O(1)的键值查找，存储key到链表节点的指针映射。
- **双向链表**：按访问时间排序，链表头部（head.next）存放**最近使用**的节点，链表尾部（tail.prev）存放**最久未使用**的节点。

每个链表节点包含四个字段：`key`、`value`、`prev`指针、`next`指针。使用**虚拟头尾节点**（dummy head 和 dummy tail）可以消除边界判断，大幅简化插入和删除逻辑。

```
[dummy_head] <-> [最近使用] <-> ... <-> [最久未使用] <-> [dummy_tail]
```

### get 与 put 操作的精确逻辑

**`get(key)` 操作**（O(1)）：
1. 在哈希表中查找key对应的节点，若不存在返回-1。
2. 若存在，将该节点从链表当前位置**移到链表头部**（move_to_head）。
3. 返回节点的value。

**`put(key, value)` 操作**（O(1)）：
1. 若key已存在：更新节点value，并将节点移到链表头部。
2. 若key不存在且缓存未满：创建新节点，插入链表头部，并在哈希表中添加映射。
3. 若key不存在且缓存已满：**删除链表尾部节点**（dummy_tail.prev），同时从哈希表中删除对应key，再插入新节点到头部。

删除尾部节点时必须先通过节点的`key`字段反查哈希表并删除，这正是节点中需要存储`key`字段（而不仅仅是`value`）的原因。

### 时间复杂度分析

| 操作 | 哈希表耗时 | 链表耗时 | 总计 |
|------|-----------|---------|------|
| get  | O(1)      | O(1)移到头部 | **O(1)** |
| put（已有key） | O(1) | O(1)移到头部 | **O(1)** |
| put（新key，满） | O(1)删+O(1)插 | O(1)删尾+O(1)插头 | **O(1)** |

空间复杂度为O(capacity)，即缓存容量上限。双向链表相比单向链表的优势在于：删除任意节点时无需遍历查找前驱节点，直接通过`node.prev`拿到前驱，使删除操作降为O(1)。

---

## 实际应用

### AI推理中的KV Cache管理

大语言模型（如GPT系列）在自回归解码时会缓存每层Transformer的Key-Value矩阵以避免重复计算。当并发请求数超过GPU显存容量时，推理框架（如vLLM）使用LRU策略驱逐最久未被续写的序列缓存块，从而在有限显存下服务更多并发请求。

### Redis中的LRU近似实现

Redis的`maxmemory-policy allkeys-lru`配置启用全局LRU淘汰。但Redis并未使用严格的双向链表LRU，而是**近似LRU**：每个key存储一个24位的最近访问时间戳（`lru`字段），淘汰时随机采样5个key（由`maxmemory-samples`控制），驱逐其中时间戳最旧的那个。这一近似方案将内存开销从O(N)降至每个key仅多占3字节。

### Python实现示例

Python标准库中的`functools.lru_cache`装饰器内部使用循环双向链表实现，其`maxsize`参数即缓存容量。`@lru_cache(maxsize=128)`可将任意纯函数的计算结果缓存，在AI特征工程中常用于缓存重复调用的特征计算函数。

---

## 常见误区

**误区1：用Python的`OrderedDict`替代手写双向链表时忘记"移到末尾"**

使用`collections.OrderedDict`实现LRU时，约定末尾为最近使用。`get`操作查到key后，必须调用`self.cache.move_to_end(key)`将其移至末尾，否则顺序不更新，淘汰逻辑会出错。许多初学者只更新了value，遗漏了位置更新步骤。

**误区2：链表节点不存储key导致无法删除哈希表项**

设计节点结构时，有人认为节点只需存储`value`即可，`key`由哈希表维护。但淘汰尾部节点时，需要通过`tail_node.key`去哈希表中删除对应条目。若节点不含`key`字段，则无法在O(1)内完成哈希表的清理，被迫遍历哈希表（O(N)），破坏整体复杂度。

**误区3：将LRU等同于LFU，混淆"最近"与"最常"**

LRU（Least Recently Used）驱逐**最久未访问**的项，一次访问即可将该项"救活"置于头部。LFU（Least Frequently Used）驱逐**访问次数最少**的项，单次访问只增加频次计数1。一个长期不用的热门数据在LRU下会被驱逐，在LFU下因历史频次高而保留。两者适用于不同的访问模式，混淆会导致缓存命中率的错误估计。

---

## 知识关联

**前置知识衔接**：LRU缓存直接依赖**哈希表**的O(1)查找能力（冲突处理、load factor控制）和**双向链表**的O(1)节点插入删除能力。哈希表提供key→节点地址的映射，双向链表维护访问时序——任何一个结构单独都无法同时满足O(1) get和O(1) put的要求。

**延伸方向**：LRU是缓存淘汰策略家族的基础形态。工程中常见的变体包括：LRU-K（需被访问K次才进入主缓存，抵抗偶发性大扫描）、ARC（Adaptive Replacement Cache，自适应平衡LRU和LFU，被ZFS文件系统采用）、CLOCK算法（用循环队列近似LRU，降低维护开销）。理解了哈希表+双向链表的LRU实现，这些变体的数据结构改造点会变得清晰可辨。