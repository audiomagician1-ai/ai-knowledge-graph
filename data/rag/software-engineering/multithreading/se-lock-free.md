---
id: "se-lock-free"
concept: "无锁编程"
domain: "software-engineering"
subdomain: "multithreading"
subdomain_name: "多线程"
difficulty: 3
is_milestone: true
tags: ["高级"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 无锁编程

## 概述

无锁编程（Lock-Free Programming）是一种多线程并发技术，通过原子操作（如CAS指令）直接协调线程间共享数据的访问，完全绕过互斥锁（mutex）机制。与基于锁的同步不同，无锁算法在任意时刻都保证至少有一个线程能完成进展，即便其他线程被操作系统挂起或延迟，系统整体仍能向前推进。

无锁数据结构的理论奠基于1990年代。Maurice Herlihy在1991年发表的论文《Wait-Free Synchronization》中正式定义了无锁（Lock-Free）与无等待（Wait-Free）的区别，并证明了CAS（Compare-And-Swap）指令的通用性——任何无锁算法都可以用CAS指令实现。IBM在PowerPC架构中使用的LL/SC（Load-Link/Store-Conditional）指令对，与x86的CMPXCHG指令是CAS的两种主要硬件实现。

无锁编程的实际价值体现在高竞争场景下的性能优势：传统mutex在线程切换和内核态陷入上的开销约为微秒级，而CAS操作在缓存命中时仅需纳秒级。游戏引擎的任务调度队列、网络服务器的连接池、日志系统的环形缓冲区等场景均大量使用无锁结构以规避锁竞争带来的延迟抖动。

---

## 核心原理

### CAS操作与循环重试

无锁编程的核心指令是CAS（Compare-And-Swap），其原子语义为：

```
bool CAS(addr, expected, new_value):
    if *addr == expected:
        *addr = new_value
        return true
    return false
```

线程在修改共享数据前，先读取当前值作为`expected`，计算出`new_value`，然后调用CAS。若期间有其他线程修改了该地址的值，CAS失败，当前线程必须重新读取并重试。这种**读-计算-CAS**的循环称为CAS循环（CAS loop）。C++11标准将此封装为`std::atomic<T>::compare_exchange_weak`与`compare_exchange_strong`，其中`weak`版本在虚假失败时允许自动重试，适合放入循环中使用。

### 无锁栈的实现

Michael与Scott在1996年提出了经典的无锁单链表栈（Treiber Stack）。其`push`操作如下：

```cpp
void push(Node* node) {
    do {
        node->next = head.load();
    } while (!head.compare_exchange_weak(node->next, node));
}
```

每次CAS失败意味着另一个线程已修改了`head`，循环读取新的`head`后继续竞争。`pop`操作同样用一个CAS将`head`更新为`head->next`。Treiber Stack的单次push/pop操作的时间复杂度为O(1)（无竞争时），在高竞争下退化为O(k)，k为并发线程数。

### ABA问题

ABA问题是无锁编程中最经典的正确性陷阱。假设线程T1读取指针`head`的值为A，在T1准备执行CAS之前，线程T2将A弹出、处理后释放内存，又将一个恰好复用了同一内存地址的新节点B推入，再将B弹出，最终重新推入地址为A的节点。此时T1的CAS成功（因为`head`仍为A），但实际上数据结构已经历了"A→B→A"的变化，T1的操作基于一个已失效的假设执行，导致链表结构损坏。

解决ABA问题最常用的方案是**带版本号的指针（Tagged Pointer）**：将指针与一个单调递增的版本计数器打包成一个128位（在64位系统上）的原子值，CAS同时比较指针与版本号。即便地址相同，版本号不同也会导致CAS失败。实现上通常使用`std::atomic<std::pair<T*, uint64_t>>`或利用x86的CMPXCHG16B指令实现双字CAS（DCAS）。另一方案是**Hazard Pointer**（Michael 2004年提出），线程在访问节点前将其地址发布到线程局部的风险指针表，内存回收器在释放节点前检查该表，确保无其他线程正在读取该节点。

---

## 实际应用

**无锁MPSC队列（多生产者单消费者）**是游戏引擎任务系统中最常见的结构。生产者用CAS竞争队列尾指针，消费者无需CAS直接读取头部，消除了消费端的原子操作开销。Unreal Engine的`TQueue`与Intel TBB的`concurrent_queue`均采用此变体。

**无锁环形缓冲区（Ring Buffer）**在日志框架与网络IO中广泛应用。生产者用`fetch_add`原子地申请写入槽位（slot），消费者通过序列号判断槽位是否已写入完毕，完全避免锁。LMAX Disruptor框架（Java）正是基于此思想，其在2011年的基准测试中达到每秒2500万次消息吞吐，远超基于BlockingQueue的方案。

**引用计数的无锁管理**：`std::shared_ptr`的引用计数操作在C++标准中使用原子增减，但整个`shared_ptr`对象的复制并非原子操作。C++20引入`std::atomic<std::shared_ptr<T>>`，通过拆分控制块的CAS操作实现真正无锁的共享指针访问。

---

## 常见误区

**误区一：无锁一定比有锁快。** 无锁在低竞争场景下性能优势不明显，CAS循环在高竞争下会因大量重试而导致活锁（Livelock）——多个线程持续互相打断对方的CAS，吞吐量急剧下降。测量表明，当并发写线程超过CPU物理核心数时，无锁队列的延迟可能高于自旋锁实现。

**误区二：只要操作是原子的就没有ABA问题。** ABA问题本质上是语义层面的错误，而非原子性层面。即便每一步CAS操作都是原子的，"地址相等"并不意味着"对象状态相等"，尤其在使用内存池或分配器复用地址时，不加版本号保护的无锁栈极易出现此问题。

**误区三：无锁编程无需考虑内存序。** 无锁代码必须显式指定内存顺序（Memory Order）。在x86上，由于TSO（Total Store Order）模型，乱序问题相对较少；但在ARM和POWER架构上，`memory_order_relaxed`的CAS可能导致其他线程看到不一致的写入顺序，必须配合`memory_order_acquire/release`使用才能保证happens-before关系。

---

## 知识关联

无锁编程直接建立在**原子操作**（`std::atomic`、CAS、fetch_add）的基础上，要求学习者理解CPU层面的原子指令语义以及C++内存模型中的六种内存序。ABA问题的解决方案（Hazard Pointer、版本号指针）本身就是更复杂**并发数据结构**设计的入门，后者进一步涵盖无锁跳表、无锁哈希表等结构。掌握无锁队列后，可直接应用于**任务系统**的工作窃取调度器（Work-Stealing Scheduler）——每个工作线程维护一个无锁双端队列（Chase-Lev Deque），本地线程从队尾取任务，空闲线程从队头窃取任务，这是现代游戏引擎与并发运行时（如Intel TBB、Folly Executor）的标准架构。