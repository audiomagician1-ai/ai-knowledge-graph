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
quality_tier: "pending-rescore"
quality_score: 35.0
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 0.393
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
---
# 无锁编程

## 概述

无锁编程（Lock-Free Programming）是一种多线程并发技术，其核心承诺是：在任意时刻，至少有一个线程能在有限步骤内完成其操作，整个系统不会因为某个线程被挂起而陷入停滞。与互斥锁（mutex）不同，无锁算法不使用任何阻塞原语，而是依赖硬件提供的原子指令——最典型的是 CAS（Compare-And-Swap，比较并交换）——来协调多线程对共享数据的访问。

无锁编程的理论基础来自 1991 年 Maurice Herlihy 发表的论文《Wait-Free Synchronization》，该论文引入了"共识数（Consensus Number）"的概念，证明 CAS 指令的共识数为无穷大，意味着它可以无等待地实现任意数量线程之间的协调，是构造无锁数据结构的理想原语。这一理论突破直接推动了后来工业界对无锁容器的大规模研究。

无锁编程的价值在于：它彻底消除了死锁和优先级反转问题，并在高竞争场景下避免了操作系统线程调度带来的上下文切换开销（每次上下文切换约消耗 1–10 微秒）。Java 的 `java.util.concurrent` 包、Linux 内核的无锁环形缓冲区 kfifo 以及 C++ 的 `std::atomic` 都在底层大量运用了这一思想。

---

## 核心原理

### CAS 指令与无锁操作的基石

CAS 的语义可以用以下伪代码精确描述：

```
bool CAS(T* addr, T expected, T desired) {
    if (*addr == expected) { *addr = desired; return true; }
    else { return false; }
}
```

该操作在 x86-64 平台上对应 `LOCK CMPXCHG` 指令，整条指令在总线级别保证原子性。无锁算法的典型模式是"读取 → 计算新值 → CAS 写回"，若 CAS 失败则重试（称为 CAS 循环）。重试次数无上界，这也是"无锁"比"无等待（Wait-Free）"宽松的地方——无锁只保证系统整体进展，不保证单个线程的进展。

### 无锁栈（Treiber Stack）

Michael Scott 和 R. Kent Treiber 于 1986 年提出的无锁栈是最经典的无锁数据结构。其 `push` 操作逻辑如下：

1. 创建新节点 `node`，令 `node->next = top`；
2. 用 CAS 尝试将全局 `top` 从当前值更新为 `node`；
3. 若 CAS 失败（说明另一线程已修改 `top`），重新读取 `top` 并返回步骤 1。

`pop` 操作则读取 `top` 后，尝试将 `top` CAS 更新为 `top->next`。整个栈无需任何锁，入栈和出栈均为 O(1) 均摊复杂度。

### 无锁队列（Michael-Scott Queue）

1996 年，Maged M. Michael 和 Michael L. Scott 提出了 MS 无锁队列，这是 Java `ConcurrentLinkedQueue` 的直接前身。该队列维护两个独立的 `head` 和 `tail` 指针，入队操作只修改 `tail`，出队操作只修改 `head`，两者之间的竞争被拆解开来，吞吐量显著高于单指针方案。入队时需要两步 CAS：先将新节点挂到 `tail->next`，再将 `tail` 推进到新节点；若第二步尚未完成就被其他线程观察到，其他线程会"帮助"完成这一推进，这就是无锁队列中的"帮助机制（helping）"。

### ABA 问题

ABA 问题是无锁编程中最隐蔽的 Bug 来源。假设线程 T1 读取地址 `A` 处的值为 `X`，随后被挂起；线程 T2 将 `A` 处改为 `Y`，又改回 `X`；T1 恢复后执行 CAS，发现 `A` 处仍为 `X`，认为数据未变，CAS 成功——但实际上内存已被修改过，结果可能导致节点被重复释放或链表被破坏。

解决 ABA 问题的标准方案是**带版本号的 CAS（Tagged Pointer / Double-Word CAS）**：将指针与一个单调递增的版本计数器打包成一个 128 位的原子对象，每次修改时版本号加 1。即使指针值从 `X` 变回 `X`，版本号也已从 `v` 变为 `v+2`，CAS 会正确失败。在 x86-64 上，这依赖 `LOCK CMPXCHG16B` 指令来原子地比较并交换 16 字节。另一种方案是**Hazard Pointer（风险指针）**，通过让每个线程声明"我当前正在访问这个指针"，延迟节点的内存回收，从根本上阻断 ABA 问题的发生路径。

---

## 实际应用

**Java ConcurrentLinkedQueue**：基于 MS 无锁队列实现，`offer()` 和 `poll()` 方法内部均使用 `sun.misc.Unsafe.compareAndSwapObject`，在高并发日志收集场景中，其吞吐量比 `LinkedBlockingQueue` 高出约 30%–50%（因为后者在每次操作时都需要获取 `ReentrantLock`）。

**Linux kfifo 环形缓冲区**：单生产者-单消费者场景下，`kfifo` 利用读写指针的自然分离完全避免了 CAS，仅依赖内存屏障（`smp_mb()`）保证可见性，是无锁编程中"分离关注点以降低同步开销"的典型范例。

**用户态网络栈（如 DPDK）**：DPDK 的 `rte_ring` 无锁环形队列使用带版本号的头尾指针，支持多生产者多消费者，在 10 Gbps 网络处理中每个包的入队出队操作延迟低于 50 纳秒，远低于加锁方案的 200–500 纳秒。

---

## 常见误区

**误区一：无锁一定比有锁快。** 在低竞争场景（如每秒只有几百次操作）中，CAS 循环重试的开销与 mutex 相当甚至更高，因为每次 CAS 都会触发缓存行的独占获取（MESI 协议中的 Modified 状态迁移），产生额外的缓存一致性流量。只有在中高竞争且临界区很短时，无锁才有明显优势。

**误区二：解决了 ABA 问题就是完整的无锁实现。** 无锁编程还需要处理**内存回收问题**：当线程 T1 持有指向某节点的本地指针时，另一线程不能立即将该节点 `free()`，否则 T1 访问的是悬空指针。这与 ABA 问题是独立的两个问题，必须通过 Hazard Pointer、RCU（Read-Copy-Update）或基于 Epoch 的内存回收来分别解决。

**误区三：无锁等同于无等待（Wait-Free）。** 无锁（Lock-Free）仅保证系统整体不停滞，某个倒霉的线程可能在 CAS 竞争中不断失败，理论上永远得不到执行机会（活锁）。无等待（Wait-Free）则保证每个线程都在有界步骤内完成操作，约束更强，实现也更复杂，代表性算法是 2011 年 Kogan 和 Petrank 提出的 Wait-Free Queue。

---

## 知识关联

**前置知识**：无锁编程直接建立在**原子操作**之上，需要理解 `std::memory_order` 中各个内存序（`relaxed`、`acquire`、`release`、`seq_cst`）对 CPU 重排序的约束，因为不正确的内存序会导致无锁算法在 ARM 等弱内存模型平台上出现数据可见性错误，即使 CAS 本身成功也可能读到过期的值。

**后续知识**：掌握无锁队列和栈之后，可以进一步学习**并发数据结构**，包括无锁哈希表（如 cliff click 的 NonBlockingHashMap）、无锁跳表（`java.util.concurrent.ConcurrentSkipListMap` 的底层实现）以及 RCU 保护的链表。这些数据结构在无锁栈/队列的基础上引入了更复杂的多节点原子更新问题，需要结合版本号技术和 Hazard Pointer 综合运用。
