---
id: "deque"
concept: "双端队列"
domain: "ai-engineering"
subdomain: "data-structures"
subdomain_name: "数据结构"
difficulty: 4
is_milestone: false
tags: ["线性"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 41.2
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 双端队列

## 概述

双端队列（Deque，全称 Double-Ended Queue）是一种允许在**两端同时进行插入和删除**操作的线性数据结构。与普通队列只能从队尾入队、队头出队不同，双端队列的队头和队尾均可执行 push 和 pop 操作，使其兼具栈和队列的所有功能。

双端队列的概念由 E.J. Dijkstra 在1960年代的算法研究中正式提出，并被收录于 Knuth 的《计算机程序设计艺术》第一卷。1998年，C++ STL 将 `std::deque` 纳入标准库，Python 则在 2.4 版本（2004年）通过 `collections.deque` 提供了官方支持，其 `appendleft` 和 `popleft` 操作均保证 O(1) 时间复杂度。

在 AI 工程中，双端队列的价值体现在滑动窗口处理、BFS 层次遍历的变种算法（如0-1 BFS）以及强化学习经验回放缓冲区的实现上。Python 的 `collections.deque` 支持 `maxlen` 参数，当队列满时自动从另一端丢弃元素，天然适合固定容量的经验回放池（Replay Buffer）设计。

---

## 核心原理

### 操作接口与时间复杂度

双端队列定义了四个核心操作：

| 操作 | 含义 | 时间复杂度 |
|------|------|-----------|
| `push_front(x)` | 从队头插入元素 x | O(1) |
| `push_back(x)` | 从队尾插入元素 x | O(1) |
| `pop_front()` | 从队头删除并返回元素 | O(1) |
| `pop_back()` | 从队尾删除并返回元素 | O(1) |

注意：普通队列的 `push_front` 是**不被允许**的操作，而双端队列将其合法化。这四个操作全部是 O(1)，是双端队列区别于数组的关键优势——数组的头部插入/删除是 O(n)。

### 底层存储结构：块状链表

CPython 的 `collections.deque` 采用**固定大小块（block）组成的双向链表**实现，每个块存储 64 个指针（在 64 位系统上）。这种设计让双端的 O(1) 操作得以实现，同时避免了单纯链表的内存碎片问题。C++ STL 的 `std::deque` 则使用分段连续内存（segmented array），通过一个中央映射数组管理多个固定大小的内存块，随机访问复杂度为 O(1)，但常数因子大于 `std::vector`。

用数组手动实现双端队列时，通常采用**循环数组**技巧：维护 `head` 和 `tail` 两个指针，初始化时 `head = tail = 0`，插入时对数组长度取模防止越界：

```
push_back:  data[tail] = x; tail = (tail + 1) % capacity
push_front: head = (head - 1 + capacity) % capacity; data[head] = x
```

这样队列中的元素数量始终为 `(tail - head + capacity) % capacity`。

### 双端队列与栈、队列的关系

双端队列是栈和队列的**超集**：仅使用 `push_back` + `pop_back` 退化为栈；仅使用 `push_back` + `pop_front` 退化为普通队列；仅使用 `push_front` + `pop_front` 也退化为栈。正因如此，LeetCode 641题"设计循环双端队列"要求同时实现 `insertFront`、`insertLast`、`deleteFront`、`deleteLast` 四个方法，本质上就是用循环数组实现一个完整的 Deque。

---

## 实际应用

### 滑动窗口最大值（单调双端队列的前驱）

在处理时序特征时，经常需要对长度为 k 的滑动窗口计算最大值。暴力做法是 O(nk)，而借助双端队列可以降到 O(n)：维护一个存储**下标**的双端队列，保证队列中对应的值单调递减。当新元素到达时，从队尾弹出所有小于新元素的下标（`pop_back`），然后将新下标从队尾插入（`push_back`）；当队头下标已滑出窗口时，从队头弹出（`pop_front`）。这种用法正是单调队列的直接基础。

### 强化学习中的经验回放缓冲区

DQN（Deep Q-Network，2013年 DeepMind 提出）的关键组件是 Replay Buffer，存储 `(s, a, r, s')` 四元组。Python 实现中：

```python
from collections import deque
replay_buffer = deque(maxlen=100000)  # 固定容量 10万条经验
replay_buffer.append((state, action, reward, next_state))
```

当缓冲区满时，`maxlen=100000` 的设置会自动从队头丢弃最旧的经验，同时从队尾追加新经验，整个过程无需手动管理内存，时间复杂度 O(1)。

### 0-1 BFS（双端队列优化的最短路）

在边权只有0和1的图上，传统 Dijkstra 需要 O((V+E)logV)，而使用双端队列可实现 O(V+E)：遇到权重为0的边，将邻节点从队头插入（`push_front`）；遇到权重为1的边，从队尾插入（`push_back`）。这样始终保证队头是当前最小距离的节点，无需优先队列。

---

## 常见误区

### 误区一：认为双端队列的随机访问与数组等价

`std::deque` 虽然支持 `operator[]` 随机访问且复杂度为 O(1)，但其常数因子远大于 `std::vector`——因为每次访问需要先查中央映射表定位块，再计算块内偏移。实测中，遍历 100万元素时 `std::deque` 比 `std::vector` 慢约 2-3 倍。Python 的 `collections.deque` 更不支持 O(1) 随机访问，`deque[k]` 是 O(k) 操作，**不能**用下标随机访问替代列表。

### 误区二：混淆双端队列与双向链表

双向链表的每个节点都持有前驱和后继指针，任意位置的插入删除都是 O(1)（已知节点指针的情况下），但查找是 O(n)。双端队列**只支持两端操作**，不支持任意位置插入，但其内存局部性远优于双向链表，实际性能更好。将 `collections.deque` 当作双向链表在中间插入元素（使用 `insert` 方法）是 O(n) 操作，这是错误用法。

### 误区三：忽略 `maxlen` 的覆盖方向

当 `collections.deque(maxlen=N)` 满载后，从**队尾** `append` 新元素时，自动丢弃的是**队头**最旧元素；而从**队头** `appendleft` 新元素时，自动丢弃的是**队尾**元素。混淆覆盖方向会导致经验回放缓冲区丢弃错误的历史数据。

---

## 知识关联

**前置概念——队列**：普通队列只暴露 `enqueue`（队尾）和 `dequeue`（队头）两个方向，是双端队列的受限版本。理解队列的 FIFO 语义和循环数组实现，是手写双端队列的直接基础。

**后续概念——单调队列**：单调队列并不是一种独立的数据结构，而是**在双端队列上施加单调性约束**的算法模式。滑动窗口最大值问题中，"从队尾弹出破坏单调性的元素"这一操作直接复用了双端队列的 `pop_back` 接口。没有双端队列的两端操作能力，单调队列的 O(n) 滑动窗口算法就无法实现。

**横向关联——优先队列**：当滑动窗口最大值问题的窗口不固定，或需要第 k 大而非最大值时，需要切换到堆（优先队列）；但固定窗口最大/最小值场景下，单调双端队列的 O(n) 优于堆的 O(n log k)，应优先选择双端队列方案。