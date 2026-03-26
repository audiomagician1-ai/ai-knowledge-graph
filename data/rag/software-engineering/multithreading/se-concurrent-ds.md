---
id: "se-concurrent-ds"
concept: "并发数据结构"
domain: "software-engineering"
subdomain: "multithreading"
subdomain_name: "多线程"
difficulty: 3
is_milestone: false
tags: ["数据结构"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.5
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

# 并发数据结构

## 概述

并发数据结构是专门设计用于多线程环境中、允许多个线程同时安全访问和修改共享数据的容器类型。与普通数据结构不同，并发数据结构在设计层面内置了线程安全保证，通过分段锁、CAS原子操作或无锁算法等机制消除竞态条件，使得多线程程序无需在每次访问时手动加互斥锁。

并发数据结构的系统性研究始于1990年代。1996年，Maged Michael和Michael Scott发表了著名的无锁队列论文，提出了基于CAS的Michael-Scott Queue算法，这是现代Java `LinkedBlockingQueue`和`ConcurrentLinkedQueue`的理论基础。Java 5（JDK 1.5，2004年发布）引入`java.util.concurrent`包，将`ConcurrentHashMap`、`CopyOnWriteArrayList`等并发数据结构带入工程实践主流。

并发数据结构的核心价值在于吞吐量与正确性的同时保证。以`ConcurrentHashMap`为例，相比完全同步的`Hashtable`，在16线程读写测试中吞吐量可提升10倍以上，原因在于它将整个哈希表分割为多个独立锁段，极大减少了锁争用。

## 核心原理

### ConcurrentHashMap的分段锁与Node锁机制

Java 7的`ConcurrentHashMap`使用16个`Segment`（默认值，可通过`concurrencyLevel`参数调整），每个Segment继承自`ReentrantLock`，不同Segment上的写操作互不阻塞。Java 8彻底重构了实现：取消Segment，改为对单个哈希桶（链表头节点或红黑树根节点）加`synchronized`锁，配合CAS完成无锁读操作。`get()`操作全程无锁，因为`Node`的`val`和`next`字段被声明为`volatile`，保证可见性。写操作若目标桶为空则用CAS插入，桶非空才加锁处理冲突。这种设计使锁粒度从段级降至桶级，理论上并发度从16提升至数组长度（默认初始16，可扩至`Integer.MAX_VALUE`量级）。

### ConcurrentLinkedQueue的无锁实现

`ConcurrentLinkedQueue`基于Michael-Scott算法，维护`head`和`tail`两个`volatile`指针，入队和出队均通过`compareAndSwapObject`（即CAS）完成，完全不使用锁。入队时，线程先读取`tail`，尝试将`tail.next`从`null` CAS为新节点；若CAS失败（说明其他线程已插入），则重试。`tail`指针允许滞后一个节点，即`tail`不一定指向真正的尾节点，这是一个有意的优化：减少对`tail`的更新频率，降低CAS竞争。出队时通过将`head`的`item`字段CAS为`null`来标记消费，而非立即移除节点，同样减少结构修改频次。

### ConcurrentSkipList的概率平衡结构

`ConcurrentSkipList`（对应`ConcurrentSkipListMap`和`ConcurrentSkipListSet`）使用跳表替代红黑树实现有序并发集合。跳表通过多层索引加速查找：底层是完整有序链表，每个节点以概率`p=0.5`晋升到上一层，期望层数为`log₂(n)`，使查找、插入、删除的期望时间复杂度均为`O(log n)`。并发实现的关键在于：插入节点时先将新节点原子地连接到底层链表，再自底向上构建各层索引，删除时先将节点的`value`字段标记为特殊的`null`（逻辑删除），再物理移除链接。这种两阶段策略使整个操作无需全局锁，多个线程可以同时在跳表的不同区域修改数据。

### BlockingQueue的阻塞语义

`ArrayBlockingQueue`和`LinkedBlockingDeque`实现了阻塞语义，这是纯无锁结构不具备的功能。`ArrayBlockingQueue`内部使用一把`ReentrantLock`加两个`Condition`（`notFull`和`notEmpty`），`put()`在队列满时调用`notFull.await()`挂起线程，`take()`在队列空时调用`notEmpty.await()`挂起，由`offer()`/`poll()`成功后分别调用`notEmpty.signal()`/`notFull.signal()`唤醒等待者。容量为1的`SynchronousQueue`则是一种极端形式：每次`put()`必须等待对应的`take()`才能完成，实现线程间的直接数据交接。

## 实际应用

**高并发缓存场景**：使用`ConcurrentHashMap`作为本地缓存时，可利用其`computeIfAbsent(key, loader)`方法原子地完成"查询-不存在则加载-插入"三步操作，避免缓存击穿时多线程重复计算。Guava Cache的底层实现正是基于`ConcurrentHashMap`的分段思想构建的。

**生产者-消费者队列**：消息队列中间件的本地缓冲通常使用`LinkedBlockingQueue`。例如Java线程池`ThreadPoolExecutor`的工作队列默认类型就是`LinkedBlockingQueue`，线程池源码中任务提交调用`workQueue.offer()`，工作线程调用`workQueue.take()`阻塞等待任务，实现了解耦生产消费速率的效果。

**实时排行榜**：游戏服务器中的实时积分排行榜需要频繁更新和范围查询，使用`ConcurrentSkipListMap`可在保证线程安全的同时，调用`subMap(fromKey, toKey)`高效截取名次区间，而`TreeMap`的等价操作在多线程环境下需要外部加锁，导致所有读写串行化。

## 常见误区

**误区1：ConcurrentHashMap完全消除了复合操作的竞态**
`ConcurrentHashMap`只保证单次操作的原子性，`get()`后再`put()`这样的复合操作仍然存在竞态条件。例如"先检查key不存在再put"的模式必须改用`putIfAbsent()`或`computeIfAbsent()`，而非`if(!map.containsKey(k)) map.put(k,v)`，后者在高并发下会导致值被覆盖。

**误区2：无锁结构一定比有锁结构快**
在低竞争场景下，`ConcurrentLinkedQueue`的CAS重试开销有时反而高于`LinkedBlockingQueue`的锁操作。当CAS失败率高时，线程会不断自旋重试，消耗CPU资源；而锁机制会将线程挂起进入等待，释放CPU。JDK源码注释本身指出`ConcurrentLinkedQueue`适合高竞争场景，低并发或需要阻塞语义时应优先考虑`BlockingQueue`。

**误区3：CopyOnWriteArrayList适合高频写场景**
`CopyOnWriteArrayList`每次写操作（`add`/`remove`）都会复制整个底层数组，写操作的时间和内存开销是`O(n)`。它专为读远多于写的场景设计（如事件监听器列表），若应用中写操作频繁，应改用`ConcurrentLinkedDeque`或有界的`ArrayBlockingQueue`。

## 知识关联

并发数据结构建立在无锁编程的CAS原子操作之上：`ConcurrentLinkedQueue`和`ConcurrentHashMap`（Java 8）的核心写路径直接调用`Unsafe.compareAndSwapObject()`，没有CAS语义就无法实现无锁的线程安全更新。理解`volatile`的内存可见性保证是读懂`ConcurrentHashMap.get()`无锁实现的前提，因为`Node.val`声明为`volatile`确保了写操作对后续读的即时可见。

并发数据结构的选型直接影响上层并发模式的设计：`BlockingQueue`天然适配生产者-消费者模式，`ConcurrentSkipListMap`使无锁有序集合操作成为可能，而理解这些结构的锁粒度和争用特性，是进行多线程性能调优（如减少锁争用、优化线程池队列策略）的必要基础。掌握这些结构的内部机制，能让工程师根据读写比例、有序性需求、阻塞语义需求等约束条件，在十余种JDK内置并发容器中做出准确选型。