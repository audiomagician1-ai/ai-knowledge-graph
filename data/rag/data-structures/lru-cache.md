# LRU缓存

## 概述

LRU（Least Recently Used，最近最少使用）缓存是一种基于"时间局部性原理"的缓存淘汰策略：当缓存容量已满时，优先驱逐最久没有被访问的数据项。这一策略由操作系统研究者在1960年代末提出，最初用于虚拟内存页面置换算法（Silberschatz, Galvin & Gagne, 2018），如今广泛应用于CPU缓存管理、数据库缓冲池（如MySQL 8.0的InnoDB Buffer Pool默认采用改良版LRU，将缓冲池分为young区和old区，各占约5/8和3/8）以及分布式系统中的本地缓存层。

LRU缓存需要同时支持两种 $O(1)$ 时间复杂度的操作：`get(key)` 查询和 `put(key, value)` 插入或更新。单纯使用数组或普通链表无法满足这一要求——数组随机访问快但插入删除慢，链表插入删除快但查找慢。因此经典实现方案是**哈希表 + 双向链表**的组合结构，两者各自弥补对方的不足。

LRU缓存在AI工程场景中尤为重要：大语言模型推理时的KV Cache管理、Embedding向量的本地缓存、特征存储（Feature Store）中热点特征的加速访问，都依赖LRU或其变体来控制内存占用。LeetCode第146题"LRU缓存"是面试高频题，要求在 $O(1)$ 时间内完成所有操作，截至2025年该题通过率约为43%，属于中高难度设计题。

LRU策略的理论基础来自于Belady（1966）提出的最优页面置换算法（OPT/Belady算法）——该算法每次驱逐"未来最长时间内不会被访问"的页面，是理论上命中率最高的策略，但由于需要预知未来访问序列而无法实际实现。LRU则以"最近未使用"近似"未来最长未使用"，在工程上可实现的同时接近理论最优（Megiddo & Modha, 2003）。

> **思考问题**：如果系统的访问模式呈现明显的周期性扫描特征（例如每隔30秒顺序遍历全部10万条数据），LRU策略会出现什么问题？应该如何改进？

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

哈希表的选型同样影响整体性能：在Java实现中，`HashMap`在链表长度超过8时自动转为红黑树（Java 8+），最坏情况下单次查询退化为 $O(\log N)$；而Python的`dict`采用开放寻址法，平均 $O(1)$ 但在哈希冲突严重时性能下降。工程实践中可通过合理设置初始容量（建议为预期元素数量的1.5倍）来减少哈希冲突和扩容开销。

双向链表相比单向链表的决定性优势在于：删除任意节点时无需遍历查找前驱节点，直接通过`node.prev`拿到前驱，使删除操作从 $O(N)$ 降为 $O(1)$。这正是整个LRU设计能够实现全操作 $O(1)$ 的关键所在——哈希表负责 $O(1)$ 定位，双向链表负责 $O(1)$ 重排。

### get 与 put 操作的精确逻辑

**`get(key)` 操作**（$O(1)$）：
1. 在哈希表中查找key对应的节点，若不存在返回 $-1$。
2. 若存在，将该节点从链表当前位置**移到链表头部**（move_to_head）。
3. 返回节点的value。

**`put(key, value)` 操作**（$O(1)$）：
1. 若key已存在：更新节点value，并将节点移到链表头部。
2. 若key不存在且缓存未满（当前节点数 $< C$）：创建新节点，插入链表头部，并在哈希表中添加映射。
3. 若key不存在且缓存已满（当前节点数 $= C$）：**删除链表尾部节点**（dummy_tail.prev），同时从哈希表中删除对应key，再插入新节点到头部。

删除尾部节点时必须先通过节点的`key`字段反查哈希表并删除，这正是节点中需要存储`key`字段（而不仅仅是`value`）的原因。若省略`key`字段，则在淘汰时无法定位哈希表中对应的条目，导致哈希表与链表状态不一致，产生内存泄漏。

### 时间复杂度分析

| 操作 | 哈希表耗时 | 链表耗时 | 总计 |
|------|-----------|---------|------|
| get  | $O(1)$ | $O(1)$ 移到头部 | $O(1)$ |
| put（已有key） | $O(1)$ | $O(1)$ 移到头部 | $O(1)$ |
| put（新key，未满） | $O(1)$ 插 | $O(1)$ 插头 | $O(1)$ |
| put（新key，已满） | $O(1)$ 删+$O(1)$ 插 | $O(1)$ 删尾+$O(1)$ 插头 | $O(1)$ |

空间复杂度为 $O(C)$，即缓存容量上限。

---

## 关键公式与性能模型

### 缓存命中率的量化表达

设在 $N$ 次访问请求中，命中缓存（即`get`返回非 $-1$）的次数为 $H$，则缓存命中率定义为：

$$\text{Hit Rate} = \frac{H}{N} \times 100\%$$

例如，在100次访问中有75次命中，则命中率为75%。工程实践中，Redis官方建议生产环境LRU缓存命中率应保持在80%以上，低于60%通常意味着缓存容量设置不足或访问模式与LRU不匹配，需考虑扩容或切换至LFU策略。

### 访问模式与Zipf定律的关系

现实中大多数系统的访问频率遵循Zipf分布：排名第 $k$ 的数据项被访问的概率与 $\frac{1}{k^s}$ 成正比，其中 $s$ 为Zipf参数（通常接近1）。在Zipf分布下，LRU的理论命中率可估算为：

$$\text{Hit Rate}_{\text{LRU}} \approx 1 - \left(\frac{C}{N_{\text{total}}}\right)^{1-s}$$

其中 $C$ 为缓存容量，$N_{\text{total}}$ 为数据总量，$s$ 为Zipf参数。该公式揭示了一个重要规律：当访问分布越倾斜（$s$ 越大），LRU策略越能以较小的缓存容量实现较高的命中率；而当访问均匀分布（$s \to 0$）时，LRU效果接近随机淘汰。

**例如**：假设某电商平台有 $N_{\text{total}} = 100\text{万}$ 条商品数据，访问服从 $s=1$ 的Zipf分布（即标准Zipf律），仅缓存其中 $C = 1\text{万}$ 条（容量比例为1%），代入公式时由于 $s=1$ 导致指数 $1-s=0$ 需取极限，实际工程中 $s$ 略小于1时命中率可达70%~85%，这正是为什么电商平台用极少量缓存就能覆盖绝大多数流量的数学原因。

### 平均访问延迟的二级存储模型

假设缓存命中延迟为 $t_{\text{hit}}$（如内存访问约100纳秒），缓存未命中时需从后端存储加载，延迟为 $t_{\text{miss}}$（如数据库查询约10毫秒），则系统平均访问延迟为：

$$\bar{t} = \text{Hit Rate} \times t_{\text{hit}} + (1 - \text{Hit Rate}) \times t_{\text{miss}}$$

**案例**：若命中率为90%，$t_{\text{hit}} = 0.1\text{ms}$，$t_{\text{miss}} = 10\text{ms}$，则：

$$\bar{t} = 0.9 \times 0.1 + 0.1 \times 10 = 0.09 + 1 = 1.09\text{ms}$$

而若命中率从90%下降至70%，则平均延迟变为 $0.7 \times 0.1 + 0.3 \times 10 = 3.07\text{ms}$，增加近3倍。这一模型直观说明了维持高命中率对系统性能的关键意义。在高并发场景下（如每秒10万次请求），1.09ms与3.07ms的差距意味着系统吞吐量相差约2.8倍，直接决定服务器扩容成本。

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

### 操作序列完整追踪

**案例演示**：以容量为2的LRU缓存执行以下操作序列：`put(1,1)` → `put(2,2)` → `get(1)` → `put(3,3)` → `get(2)`。

- 执行`put(1,1)`后，链表为：`[1]`，哈希表：`{1→Node(1,1)}`
- 执行`put(2,2)`后，链表为：`[2,1]`（2最近使用，1最久未使用），哈希表：`{1→..., 2→...}`
- 执行`get(1)`后，节点1移至头部，链表为：`[1,2]`，返回值为1
- 执行`put(3