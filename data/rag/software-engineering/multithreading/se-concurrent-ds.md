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
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
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

并发数据结构是专门设计用于多线程环境下安全访问与修改的数据结构，其核心挑战是在保证线程安全的同时最大化并发吞吐量。与单线程数据结构不同，并发数据结构必须处理写-写冲突、读-写冲突，以及多核CPU缓存一致性问题（如伪共享）。Java标准库中的`java.util.concurrent`包自JDK 1.5（2004年）起提供了一整套生产就绪的并发数据结构实现。

并发数据结构的演化路线清晰：最早的实现依赖全局锁（如`Hashtable`对每个方法加`synchronized`），这种方式简单但并发度极低；第二代引入分段锁（Segment Locking），典型代表是JDK 7中的`ConcurrentHashMap`默认16个分段；第三代（JDK 8+）彻底转向CAS（Compare-And-Swap）无锁操作与细粒度桶锁，并发度从16个分段提升至桶数量级。

并发数据结构的重要性在于，正确使用它们可以避免程序员手动加锁时常见的死锁、优先级反转和锁竞争问题。以`ConcurrentHashMap`替代`HashMap+synchronized`，在16核机器上的读操作吞吐量可提升8-12倍，因为`ConcurrentHashMap`的读操作在JDK 8中完全无锁。

---

## 核心原理

### ConcurrentHashMap：分桶锁与无锁读

JDK 8的`ConcurrentHashMap`底层使用`Node<K,V>[]`数组，每个数组槽位（桶）独立加锁，锁粒度从JDK 7的16个`Segment`细化到`n`个桶。写入时通过`synchronized(桶头节点)`加锁，读取时利用`volatile`修饰的`val`字段实现无锁读。当链表长度超过8且数组长度超过64时，链表自动转为红黑树，使最坏查找时间从O(n)降至O(log n)。

`size()`方法不使用全局锁，而是通过分布在多个`CounterCell`中的计数器求和得出，这与`LongAdder`的实现原理相同——通过减少多核争用同一内存地址来降低CAS失败率。

扩容时采用多线程协同迁移（`transfer()`方法），每个线程认领一段桶区间（最小步长16），迁移完成的桶位置填入`ForwardingNode`作为标记，其他线程读写时检测到`ForwardingNode`即知道需要跳转至新数组。

### ConcurrentLinkedQueue：Michael-Scott无锁队列

`ConcurrentLinkedQueue`实现了Michael & Scott于1996年发表的无锁队列算法（MS Queue），其核心是维护`head`和`tail`两个`AtomicReference`节点指针。入队操作使用两步CAS：先CAS将新节点链接到`tail.next`，再CAS推进`tail`指针。这两步不是原子的——`tail`可能落后实际队尾一个节点，其他线程检测到`tail.next != null`时会先帮助推进`tail`，再执行自己的入队，这一"帮助机制"（Helping）是无锁数据结构的典型模式。

出队操作同样使用CAS将`head`推进到`head.next`，被移除的头节点其`next`指向自身（`p.next = p`），这是一个哨兵标记，防止迭代器在并发修改下进入死循环。`ConcurrentLinkedQueue`不支持`size()`的O(1)操作，调用`size()`需遍历整个链表，时间复杂度O(n)，这是其设计上的已知取舍。

### ConcurrentSkipList：概率平衡的有序并发结构

`ConcurrentSkipListMap`与`ConcurrentSkipListSet`基于跳表（Skip List）实现，由William Pugh于1990年提出。跳表用多层索引链表在O(log n)期望时间内完成查找、插入和删除，其平衡性来自概率而非旋转（不同于红黑树需要复杂的旋转平衡，跳表节点晋升层级的概率通常为0.25或0.5）。

并发跳表的删除分为两阶段：首先对目标节点的`value`字段CAS设为`null`（逻辑删除标记），之后在后续的遍历操作中顺带完成物理节点摘链（延迟物理删除）。这避免了在删除时需要同时修改多个层级指针所带来的原子性难题。`ConcurrentSkipListMap`的`firstKey()`、`lastKey()`、`headMap()`、`tailMap()`、`subMap()`等范围操作都是O(log n)，这是`ConcurrentHashMap`无法提供的能力。

### BlockingQueue：生产者-消费者协调

`ArrayBlockingQueue`用单锁+双条件变量（`notEmpty`与`notFull`）实现有界阻塞队列，容量在构造时指定且不可更改。`LinkedBlockingQueue`则用两把独立锁（`takeLock`和`putLock`）分别控制出队和入队，使得生产者与消费者操作不互斥，并发吞吐量高于`ArrayBlockingQueue`。`SynchronousQueue`的容量为0，每次`put()`必须等待一个对应的`take()`，常用于线程池的任务传递（`Executors.newCachedThreadPool()`默认使用它）。

---

## 实际应用

**本地缓存场景**：使用`ConcurrentHashMap`实现简单的本地缓存时，`computeIfAbsent(key, loader)`方法原子性地完成"检查-计算-插入"三步，避免重复计算。JDK 8中该方法对同一桶加锁，但要注意：在`loader`函数内部不能再对同一`ConcurrentHashMap`调用`computeIfAbsent`，否则会死锁（同一线程对同一桶的`synchronized`重入问题，JDK 9已修复）。

**日志聚合统计**：高并发计数场景中，`ConcurrentHashMap<String, LongAdder>`比`ConcurrentHashMap<String, AtomicLong>`吞吐量更高，因为`LongAdder`内部分散多个`Cell`减少CAS竞争，在64核机器压测中吞吐量差距可达3倍以上。

**有序事件流**：需要按时间戳或优先级有序处理事件时，`ConcurrentSkipListMap<Long, Event>`是标准选择，其`pollFirstEntry()`操作是O(log n)无锁操作，适用于定时任务调度器（Netty的`HashedWheelTimer`即借鉴了类似思路）。

**线程池任务队列**：`LinkedBlockingQueue`是`ThreadPoolExecutor`默认使用的工作队列类型，`Executors.newFixedThreadPool(n)`传入的即是无界`LinkedBlockingQueue`——这也是为什么该工厂方法在生产环境中不建议使用，无界队列会导致OOM。

---

## 常见误区

**误区一：认为ConcurrentHashMap的复合操作是原子的**
`map.containsKey(k)`为`true`后调用`map.get(k)`，两次操作之间其他线程可能已删除该键，导致`get()`返回`null`。正确做法是使用`map.get(k)`的返回值判断null，或使用`computeIfAbsent`/`putIfAbsent`等原子复合方法。`size()`返回值也是近似值，不应用于精确控制逻辑。

**误区二：认为ConcurrentLinkedQueue适合所有队列场景**
`ConcurrentLinkedQueue`是无界无锁队列，没有背压机制，生产速度远超消费速度时会无限增长直至OOM。需要流量控制时必须选用`ArrayBlockingQueue`或`LinkedBlockingQueue`等有界阻塞队列。此外，`ConcurrentLinkedQueue`的`isEmpty()`比`size()==0`性能好，因为前者只检查头节点，后者需要遍历。

**误区三：认为跳表比红黑树慢因此不应在并发场景使用**
单线程下红黑树（`TreeMap`）确实比跳表快，但在多线程下红黑树的旋转操作需要锁住多个节点，实现无锁红黑树极为复杂且实际性能不理想。跳表的分层指针结构使局部修改成为可能，JDK选择跳表实现`ConcurrentSkipListMap`而非并发红黑树正是基于这一工程权衡。

---

## 知识关联

**依赖无锁编程基础**：理解`ConcurrentHashMap`的桶级CAS初始化（`casTabAt`）、`ConcurrentLinkedQueue`的MS算法、跳表的逻辑删除，都需要掌握CAS语义、ABA问题（`AtomicStampedReference`解决）以及`volatile`的可见性保证。没有这些基础，只能作为黑盒使用并发数据结构，无法正确处理边界情况。

**与内存模型的关联**：Java内存模型（JMM）规定对`volatile`写操作happens-before后续对同一字段的读操作，`ConcurrentHashMap`节点的`val`和`next`字段均为`volatile`，这正是读操作无需加锁但仍能保证可见性的理论依据。

**与线程池的协作**：`BlockingQueue`的实现直接决定了`ThreadPoolExecutor`的排队策略——有界队列触发线程数增长至`maximumPoolSize`，无界队列使`maximumPoolSize`形同虚设，`SynchronousQueue`则使每个任务都直接转交给线程，三种行为截然不同，是线