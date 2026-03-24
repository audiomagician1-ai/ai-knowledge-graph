---
id: "se-memory-allocator"
concept: "内存分配器"
domain: "software-engineering"
subdomain: "memory-management"
subdomain_name: "内存管理"
difficulty: 3
is_milestone: false
tags: ["高级"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.2
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.419
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 内存分配器

## 概述

内存分配器（Memory Allocator）是负责管理堆内存的系统组件，它将操作系统提供的大块连续内存拆分为不同大小的块，并追踪哪些块正在使用、哪些块已释放。标准C库中的 `malloc`/`free` 背后就是一个通用分配器（如 glibc 的 ptmalloc2），但通用分配器为了兼顾所有使用场景，不得不在分配速度、内存利用率和碎片控制之间做出折中。

内存分配器的历史可以追溯到1970年代。Doug Lea 在1987年发布了 dlmalloc，成为日后众多分配器的基础；后来 Wolfram Gloger 在此基础上引入了线程竞技场（thread arena）机制，形成了 ptmalloc2，这也是 glibc 至今仍在使用的实现。2000年前后，高并发场景的需求推动了 tcmalloc（来自 Google）和 jemalloc（来自 FreeBSD）的诞生，二者分别采用了线程本地缓存和大小类（size class）来大幅减少锁竞争。

定制化分配器的意义在于，对于**特定访问模式**的程序，通用分配器的头部元数据（header metadata，通常占用8~16字节/块）、查找空闲块的链表遍历、以及线程间的锁争用会成为可测量的瓶颈。了解不同分配策略的设计原理，是进行内存性能优化的前提。

---

## 核心原理

### 空闲块管理：边界标记与空闲链表

最基础的分配器使用**边界标记法**（Boundary Tag，由 Knuth 于1973年提出）：每个内存块在头部和尾部各存储一个大小字段及一个"已分配/空闲"标志位。释放后，分配器通过尾部标记定位前一块，实现 O(1) 的合并（Coalescing）操作。空闲块通过**显式链表**（explicit free list）或**分离适配链表**（segregated fit）组织：例如，jemalloc 将对象划分为小型（≤14KB）、中型（≤1792KB）、大型三类，每类维护独立的大小类链表，使分配操作接近 O(1)。

### Arena 分配策略

Arena（竞技场）分配器预先从操作系统申请一大块内存（如 `mmap` 一段 2MB 的区域），然后用一个简单的**碰撞指针**（bump pointer）在其中顺序分配：

```
arena->next_free += requested_size;
```

所有对象在同一个 Arena 中线性排列，无需每块独立的元数据头。当 Arena 被整体释放时，所有内部对象一并回收，避免了对每个对象逐一调用 `free` 的开销。这种策略适合生命周期一致的对象群（如编译器中的 AST 节点：解析完成后整棵树一次性销毁）。代价是单个对象**无法提前独立释放**。

### Slab 分配策略

Slab 分配器（由 Jeff Bonwick 于1994年为 Solaris 内核设计）针对**固定大小对象的频繁创建/销毁**场景。它将内存划分为一组"slab"，每个 slab 仅存储同一类型的对象（例如，一个专门存放 `struct task_struct` 的 slab）。Slab 内部用**位图或空闲对象链表**追踪哪些槽位可用，分配时只需从链表头弹出一个槽位，时间复杂度为 O(1)。更重要的是，Slab 分配器可以在释放时**保留对象的构造状态**（如已初始化的锁、引用计数），避免下次分配时重复初始化，这在 Linux 内核中称为"对象缓存"（object caching）。

### 线程本地缓存（Thread-Local Cache）

tcmalloc 的核心创新是为每个线程维护一个线程本地的小对象缓存（ThreadCache），大小通常为4~8MB。小于32KB的分配请求优先从 ThreadCache 满足，完全**无需加锁**。只有当 ThreadCache 耗尽时，才批量向中央缓存（CentralCache）申请，此时才需要锁。基准测试显示，tcmalloc 的小对象分配速度约是 ptmalloc2 的5倍。

---

## 实际应用

**游戏引擎帧分配器**：每帧开始时重置一个 bump pointer Arena，所有帧内临时数据（粒子坐标、AI 决策树节点）从此 Arena 分配，帧结束后整体重置。这消除了碎片并使分配速度接近栈（单次指针加法）。Unreal Engine 的 `FMemStack` 和 id Software 的 Quake 引擎中的 Hunk Allocator 均采用此思路。

**网络服务器连接对象池**：Nginx 为每个 HTTP 请求创建一个专属 `ngx_pool_t`，请求期间所有字符串、头部解析结果均从该 Pool 分配；请求结束时调用 `ngx_destroy_pool` 一次性释放，避免了对每个 `ngx_str_t` 单独调用 `free`，并消除了请求处理中的内存泄漏风险。

**Linux 内核 Slab 缓存**：`kmem_cache_alloc(&inode_cachep, GFP_KERNEL)` 从专门的 inode 缓存中分配一个预初始化的 `struct inode`，其内部的互斥锁和引用计数已处于正确初始状态，不需要每次重新调用 `inode_init_once`。

---

## 常见误区

**误区一：认为自定义分配器总是比 malloc 快**。实际上，Arena 分配器只有在对象批量销毁时才有优势；如果需要频繁单独释放对象，Arena 分配器反而会造成内存浪费（因为无法回收单个对象）。Slab 分配器在对象大小不均匀时也会引入内部碎片（同一 slab 中槽位大小固定，小对象会浪费空间）。

**误区二：Arena 分配器没有内存泄漏风险，所以不需要管理生命周期**。Arena 本身的内存在 `arena_destroy` 之前始终占用，如果 Arena 的生命周期设计不当（如全局 Arena 从不销毁），整体内存使用会持续增长，与传统内存泄漏效果相同。

**误区三：只要用了线程本地缓存就能消除所有锁竞争**。tcmalloc 的 ThreadCache 仅覆盖小于32KB的分配；大对象分配仍需访问全局 PageHeap，此处使用自旋锁。高并发大对象分配场景下，锁竞争问题依然存在，需要配合对象池或应用层缓存解决。

---

## 知识关联

学习内存分配器需要先掌握**栈与堆**的区别：栈内存由编译器以 `LIFO` 方式自动管理，堆内存则需要分配器手动追踪，这正是分配器存在的原因。理解了通用分配器的设计权衡后，可以进一步学习**池分配器**（固定大小对象的简化版 Slab）和 **Arena 分配器**（bump pointer 策略的完整实现），两者都是本文策略的具体落地形式。随着分配策略复杂化，**内存碎片化**成为必须正视的问题——外部碎片由不当的合并策略引起，内部碎片由大小类对齐引起。最终，对分配器的改进效果需要通过**性能分析**工具（如 Valgrind massif、heaptrack）来量化验证，才能判断特定场景下定制分配器是否真正带来收益。
