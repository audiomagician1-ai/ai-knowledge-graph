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

LRU（Least Recently Used，最近最少使用）缓存是一种根据时间局部性原理实现的缓存淘汰策略：当缓存空间已满时，优先淘汰最长时间未被访问的数据项。这一策略基于"近期被访问的数据在不久的将来更可能被再次访问"这一假设，在实际场景中命中率表现优秀。

LRU策略由L.A. Belady在1966年的研究中正式分析，与最优页面置换算法（OPT）相比虽存在差距，但因其无需预知未来访问序列而成为操作系统页面置换、数据库缓冲池管理、CDN节点缓存的标准实现之一。Linux内核的页面缓存、Redis的maxmemory-policy配置项均提供LRU或近似LRU策略。

LRU缓存的工程价值在于：朴素的"查找最久未使用项并删除"若用数组实现需要O(n)时间，而结合**哈希表与双向链表**的经典设计可将`get`和`put`操作均压缩至O(1)时间复杂度，使其在高频读写场景下具备实用价值。

---

## 核心原理

### 数据结构选型：哈希表 + 双向链表

LRU缓存用两种数据结构协同工作：

- **哈希表**（`HashMap<key, Node>`）：提供O(1)的键值查找，键映射到双向链表中的节点指针。
- **双向链表**：维护访问顺序，链表头部（head.next）表示最近访问的节点，链表尾部（tail.prev）表示最久未访问的节点。使用**虚拟头尾节点**（dummy head/tail）避免边界判断。

双向链表（而非单向链表）的必要性在于：删除链表中任意节点需要同时修改其前驱节点的`next`指针和后继节点的`prev`指针。若只有单向链表，找到目标节点后仍需O(n)时间遍历找到其前驱，无法实现O(1)删除。

### get 操作（时间复杂度 O(1)）

```
get(key):
  若 key 不在哈希表中，返回 -1
  否则：
    从哈希表取出对应节点 node
    将 node 移动到链表头部（move_to_head）
    返回 node.value
```

`move_to_head` 分解为两步原子操作：`remove(node)`（调整前后节点指针，O(1)）+ `add_to_head(node)`（插入虚拟头节点之后，O(1)）。这两步均只涉及固定数量的指针修改，与缓存容量无关。

### put 操作（时间复杂度 O(1)）

```
put(key, value):
  若 key 已存在：
    更新节点 value，移动到链表头部
  否则：
    创建新节点，加入哈希表，插入链表头部
    若当前节点数 > capacity：
      删除链表尾部节点（tail.prev）
      同步从哈希表中删除对应 key
```

关键细节：淘汰时必须**同步删除哈希表中的条目**，否则哈希表与链表状态不一致，后续`get`会命中已被淘汰的键。这是实现中最常见的遗漏点。

### 节点结构定义

标准节点包含四个字段：

```python
class Node:
    def __init__(self, key=0, val=0):
        self.key = key      # 删除尾节点时需用 key 反查哈希表
        self.val = val
        self.prev = None
        self.next = None
```

`key`字段看似冗余，实则是从链表尾部反向删除哈希表条目的必要依据——若节点不存储`key`，淘汰时将无法以O(1)完成哈希表的同步删除。

---

## 实际应用

**LeetCode 146题（LRU Cache）** 是该数据结构的标准考题，要求在O(1)时间内实现`get`和`put`，Python的`collections.OrderedDict`因维护插入顺序可直接模拟，但面试中通常要求手动实现底层结构。

**Redis近似LRU**：Redis（3.0版本前）并非实现严格LRU，而是在每次淘汰时随机采样`maxmemory-samples`个键（默认值为5），从中淘汰最久未使用的，以降低维护全局LRU链表的内存与CPU开销。Redis 3.2起引入了更精确的LFU策略作为替代选项。

**CPU多级缓存替换**：现代CPU的L1/L2缓存行替换策略采用伪LRU（pseudo-LRU）树形结构，因硬件电路中维护严格LRU的路数（ways）会随组相联度指数增长，8路组相联的严格LRU需要log₂(8!) ≈ 15.3位状态，而伪LRU仅需7位。

**AI推理服务的KV Cache管理**：大语言模型推理中，Attention机制的Key-Value缓存（KV Cache）可能占用数十GB显存，vLLM等推理框架使用PagedAttention结合LRU策略管理显存中的KV Cache页面，当新请求到来而显存不足时，按LRU淘汰非活跃序列的缓存块。

---

## 常见误区

**误区1：认为put时只需更新链表，不需要更新哈希表**  
当一个已存在的key执行put（更新value）时，必须同时更新哈希表对应节点的`val`字段和链表中节点的位置（移至头部）。只移动链表位置而不更新value会导致读取到旧数据；只更新value而不移动链表位置则违背了"访问即刷新"的LRU语义。

**误区2：使用单向链表加头部哨兵，认为能实现O(1)删除**  
单向链表的O(1)删除只能做到"删除当前节点的下一个节点"（将next.val复制过来再跳过next节点），但LRU需要删除链表中**任意位置**的节点（get操作后将其移到头部），这种"复制值"的技巧在节点被哈希表指针直接引用时会导致指针失效，必须使用双向链表。

**误区3：混淆LRU与LFU的淘汰目标**  
LRU淘汰的是**时间最久未访问**的项（如某个key一小时前访问了1000次，一秒前未访问，LRU会淘汰它），而LFU（Least Frequently Used）淘汰的是**访问频率最低**的项。两者在热点数据短暂不被访问时行为差异显著，LFU对周期性访问模式的适应性更强，LRU实现更简单且对突发性新数据友好。

---

## 知识关联

**哈希表**是LRU实现的查找基础：LRU的O(1) `get`依赖哈希表将键映射到链表节点的内存地址，哈希冲突处理方式（链式或开放寻址）影响最坏情况性能，LRU通常要求哈希表平均O(1)的前提成立。

**双向链表**是LRU实现的顺序维护基础：与普通链表相比，双向链表新增的`prev`指针使任意节点的删除从O(n)降为O(1)，这是LRU整体时间复杂度保证的必要条件，虚拟头尾节点的设计模式也源自链表操作的边界简化技巧。

LRU是缓存淘汰策略族的入门实现，掌握其哈希表+双向链表的组合设计思路后，可进一步研究LFU（需维护频率桶的双重链表结构）、ARC（Adaptive Replacement Cache，同时维护LRU和LFU两个链表）等更复杂的缓存策略，它们均在LRU的结构基础上扩展了额外的计数或历史信息维护机制。