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
content_version: 3
quality_tier: "A"
quality_score: 88.5
generation_method: "ai-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v2"
  - type: "academic"
    author: "Silberschatz, A., Galvin, P. B., & Gagne, G."
    year: 2018
    title: "Operating System Concepts (10th Edition)"
    publisher: "Wiley"
  - type: "academic"
    author: "Megiddo, N., & Modha, D. S."
    year: 2003
    title: "ARC: A Self-Tuning, Low Overhead Replacement Cache"
    publisher: "USENIX FAST"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-06
---


# LRU缓存

## 概述

LRU（Least Recently Used，最近最少使用）缓存是一种基于"时间局部性原理"的缓存淘汰策略：当缓存容量已满时，优先驱逐最久没有被访问的数据项。这一策略由操作系统研究者在1960年代末提出，最初用于虚拟内存页面置换算法（Silberschatz et al., 2018），如今广泛应用于CPU缓存管理、数据库缓冲池（如MySQL 8.0的InnoDB Buffer Pool默认采用改良版LRU，将缓冲池分为young区和old区，各占约5/8和3/8）以及分布式系统中的本地缓存层。

LRU缓存需要同时支持两种 $O(1)$ 时间复杂度的操作：`get(key)` 查询和 `put(key, value)` 插入或更新。单纯使用数组或普通链表无法满足这一要求——数组随机访问快但插入删除慢，链表插入删除快但查找慢。因此经典实现方案是**哈希表 + 双向链表**的组合结构，两者各自弥补对方的不足。

LRU缓存在AI工程场景中尤为重要：大语言模型推理时的KV Cache管理、Embedding向量的本地缓存、特征存储（Feature Store）中热点特征的加速访问，都依赖LRU或其变体来控制内存占用。LeetCode第146题"LRU缓存"是面试高频题，要求在 $O(1)$ 时间内完成所有操作，截至2025年该题通过率约为43%，属于中高难度设计题。

---

## 核心原理

### 数据结构设计：哈希表 + 双向链表

LRU缓存维护两个结构：
- **哈希表**（`HashMap<key, Node*>`）：实现 $O(1)$ 的键值查找，存储key到链表节点的指针映射。
- **双向链表**：按访问时间排序，链表头部（head.next）存放**最近使用**的节点，链表尾部（tail.prev）存放**最久未使用**的节点。

每个链表节点包含四个字段：`key`、`value`、`prev`指针、`next`指针。使用**虚拟头尾节点**（dummy head 和 dummy tail）可以消除边界判断，大幅简化插入和删除逻辑。结构示意如下：

```
[dummy_head] <-> [最近使用] <-> ... <-> [最久未使用] <-> [dummy_tail]
```

若缓存容量为 $C$，则哈希表中最多维护 $C$ 个键值对，双向链表中最多包含 $C$ 个数据节点加上2个虚拟节点，总空间开销为 $O(C)$。

### get 与 put 操作的精确逻辑

**`get(key)` 操作**（$O(1)$）：
1. 在哈希表中查找key对应的节点，若不存在返回 $-1$。
2. 若存在，将该节点从链表当前位置**移到链表头部**（move_to_head）。
3. 返回节点的value。

**`put(key, value)` 操作**（$O(1)$）：
1. 若key已存在：更新节点value，并将节点移到链表头部。
2. 若key不存在且缓存未满（当前节点数 $< C$）：创建新节点，插入链表头部，并在哈希表中添加映射。
3. 若key不存在且缓存已满（当前节点数 $= C$）：**删除链表尾部节点**（dummy_tail.prev），同时从哈希表中删除对应key，再插入新节点到头部。

删除尾部节点时必须先通过节点的`key`字段反查哈希表并删除，这正是节点中需要存储`key`字段（而不仅仅是`value`）的原因。

### 时间复杂度分析

| 操作 | 哈希表耗时 | 链表耗时 | 总计 |
|------|-----------|---------|------|
| get  | $O(1)$ | $O(1)$ 移到头部 | $O(1)$ |
| put（已有key） | $O(1)$ | $O(1)$ 移到头部 | $O(1)$ |
| put（新key，未满） | $O(1)$ 插 | $O(1)$ 插头 | $O(1)$ |
| put（新key，已满） | $O(1)$ 删+$O(1)$ 插 | $O(1)$ 删尾+$O(1)$ 插头 | $O(1)$ |

空间复杂度为 $O(C)$，即缓存容量上限。双向链表相比单向链表的优势在于：删除任意节点时无需遍历查找前驱节点，直接通过`node.prev`拿到前驱，使删除操作从 $O(N)$ 降为 $O(1)$。

### 缓存命中率的量化表达

设在 $N$ 次访问请求中，命中缓存（即`get`返回非 $-1$）的次数为 $H$，则缓存命中率定义为：

$$\text{Hit Rate} = \frac{H}{N} \times 100\%$$

例如，在100次访问中有75次命中，则命中率为75%。工程实践中，Redis官方建议生产环境LRU缓存命中率应保持在80%以上，低于60%通常意味着缓存容量设置不足或访问模式与LRU不匹配，需考虑扩容或切换至LFU策略。

---

## 实现示例

### Python手写双向链表实现

以下为Python完整实现，对应LeetCode 146题：

```python
class DLinkedNode:
    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCache:
    def __init__(self, capacity: int):
        self.cache = {}          # 哈希表：key -> 节点
        self.capacity = capacity
        self.size = 0
        # 虚拟头尾节点，消除边界判断
        self.head = DLinkedNode()
        self.tail = DLinkedNode()
        self.head.next = self.tail
        self.tail.prev = self.head

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._move_to_head(node)   # 更新访问时序
        return node.value

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            node = self.cache[key]
            node.value = value
            self._move_to_head(node)
        else:
            node = DLinkedNode(key, value)
            self.cache[key] = node
            self._add_to_head(node)
            self.size += 1
            if self.size > self.capacity:
                tail = self._remove_tail()
                del self.cache[tail.key]  # 必须用tail.key反查并删除
                self.size -= 1

    def _add_to_head(self, node):
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def _remove_node(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _move_to_head(self, node):
        self._remove_node(node)
        self._add_to_head(node)

    def _remove_tail(self):
        node = self.tail.prev
        self._remove_node(node)
        return node
```

例如，以容量为2的LRU缓存执行以下操作序列：`put(1,1)` → `put(2,2)` → `get(1)` → `put(3,3)` → `get(2)`。

- 执行`put(1,1)`后，链表为：`[1]`
- 执行`put(2,2)`后，链表为：`[2,1]`（2最近使用）
- 执行`get(1)`后，节点1移至头部，链表为：`[1,2]`，返回1
- 执行`put(3,3)`时缓存已满，驱逐尾部节点2，链表为：`[3,1]`
- 执行`get(2)`时key=2已不在缓存，返回 $-1$

### Python OrderedDict简洁实现

Python标准库提供了`collections.OrderedDict`，可大幅简化代码（约10行），约定末尾为最近使用：

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)   # 必须更新位置，否则顺序错误
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)  # 弹出最旧（头部）元素
```

---

## 实际应用

### AI推理中的KV Cache管理

大语言模型（如GPT-4、LLaMA-3系列）在自回归解码时会缓存每层Transformer的Key-Value矩阵以避免重复计算。以LLaMA-3 70B模型为例，单条序列的KV Cache在FP16精度下约占用数百MB显存。当并发请求数超过GPU显存容量时，推理框架vLLM（2023年由加州大学伯克利分校开源）使用基于LRU的PagedAttention策略：将KV Cache切分为固定大小的内存块（block），以块为单位进行LRU驱逐，相比传统方案将GPU显存利用率从约30%提升至接近100%，吞吐量提升2到4倍。

### Redis中的LRU近似实现

Redis 7.x的`maxmemory-policy allkeys-lru`配置启用全局LRU淘汰。但Redis并未使用严格的双向链表LRU，而是**近似LRU**：每个key存储一个24位的最近访问时间戳（`lru`字段，精度为秒），淘汰时随机采样默认5个key（由`maxmemory-samples`控制，范围1到10），驱逐其中时间戳最旧的那个。这一近似方案将内存开销从 $O(N)$ 降至每个key仅多占3字节，在`maxmemory-samples=10`时其效果已非常接近严格LRU。Redis 4.0起还引入了`allkeys-lfu`策略，使用Morris计数器以8位存储访问频率。

### MySQL InnoDB Buffer Pool中的改良LRU

MySQL InnoDB的Buffer Pool（默认128MB，生产环境通常设为物理内存的70%到80%）使用改良版LRU链表：将链表分为**young区**（前5/8，存放热数据）和**old区**（后3/8，存放新载入页）。新页面首先进入old区头部，只有在old区停留时间超过`innodb_old_blocks_time`（默认1000毫秒）后再次被访问，才会晋升至young区头部。这一设计有效抵御了全表扫描导致的缓存污染问题。

### Python functools.lru_cache装饰器

Python 3.2起内置的`functools.lru_cache`装饰器内部使用循环双向链表实现，其`maxsize`参数即缓存容量（默认128，设为`None`时关闭淘汰）。`@lru_cache(maxsize=256)`可将任意纯函数的计算结果缓存，在AI特征工程中常用于缓存重复调用的特