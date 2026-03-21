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
content_version: 1
quality_tier: "A"
quality_score: 72.3
generation_method: "ai-batch-v1"
unique_content_ratio: 1.0
last_scored: "2026-03-21"
sources: []
---
# LRU缓存

## 核心概念

LRU（Least Recently Used）缓存是一种固定容量的缓存淘汰策略。当缓存已满需要插入新元素时，淘汰最久未被使用的元素。LRU缓存要求get和put操作都在O(1)时间内完成。

## 数据结构设计

LRU缓存由两个数据结构组合实现：
- **哈希表**: O(1)查找键是否存在
- **双向链表**: O(1)移动/删除/插入节点，维护使用时间顺序

```
哈希表: key → 链表节点指针
双向链表: head ← ... ← 最近使用 ← ... ← 最久未使用 → tail
```

## 操作

### get(key)
1. 哈希表查找 key
2. 未命中 → 返回 -1
3. 命中 → 将节点移到链表头部（标记为最近使用），返回值

### put(key, value)
1. key已存在 → 更新值，移到链表头部
2. key不存在 → 
   a. 缓存已满 → 删除链表尾部节点（最久未使用），从哈希表移除
   b. 创建新节点，插入链表头部，加入哈希表

## 实现示例

```python
# Python: LRU Cache
class Node:
    def __init__(self, key=0, val=0):
        self.key = key
        self.val = val
        self.prev = None
        self.next = None

class LRUCache:
    def __init__(self, capacity):
        self.cap = capacity
        self.map = {}
        # 哨兵节点简化边界处理
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev
    
    def _add_front(self, node):
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node
    
    def get(self, key):
        if key not in self.map:
            return -1
        node = self.map[key]
        self._remove(node)
        self._add_front(node)
        return node.val
    
    def put(self, key, value):
        if key in self.map:
            self._remove(self.map[key])
        node = Node(key, value)
        self._add_front(node)
        self.map[key] = node
        if len(self.map) > self.cap:
            lru = self.tail.prev
            self._remove(lru)
            del self.map[lru.key]
```

⚠️ 注意：Python内置`functools.lru_cache`装饰器提供了现成的LRU缓存，但面试/竞赛中通常要求手动实现。Java可使用`LinkedHashMap`。

## 复杂度

| 操作 | 时间 | 空间 |
|------|------|------|
| get | O(1) | - |
| put | O(1) | - |
| 总空间 | - | O(capacity) |

## 相关缓存策略

- **LFU**: Least Frequently Used，淘汰使用频率最低的
- **FIFO**: First In First Out，淘汰最早加入的
- **TTL**: Time To Live，按过期时间淘汰

## 与哈希表和链表的关系

LRU缓存是哈希表和双向链表的经典结合应用。哈希表提供O(1)查找，双向链表提供O(1)的有序维护。理解两种数据结构是实现LRU的前提。
