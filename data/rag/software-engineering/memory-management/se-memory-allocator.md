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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 内存分配器

## 概述

内存分配器（Memory Allocator）是负责管理堆内存的软件组件，它实现了 `malloc`/`free`（C语言）或 `new`/`delete`（C++）等接口背后的具体策略。当程序调用 `malloc(100)` 时，操作系统并不会每次都被打扰——内存分配器会预先向操作系统申请一大块内存（通过 `brk()` 或 `mmap()` 系统调用），然后在用户空间自主切分和回收，以此避免频繁陷入内核态。

内存分配器的历史可以追溯到1979年由 Doug Lea 设计的 dlmalloc，它成为后来 glibc 中 ptmalloc 的原型。现代系统中常见的分配器包括 Google 的 tcmalloc（2005年）和 Facebook 的 jemalloc（2006年首次用于 FreeBSD），后者被 Redis 和 Rust 标准库默认采用。这些分配器的出现解决了 dlmalloc 在多线程场景下因全局锁导致的严重竞争问题。

内存分配器的设计直接影响程序的吞吐量和延迟。在高频分配场景（如每秒百万次小对象分配）中，不同分配器的性能差距可达5～10倍。理解分配器的工作机制，是写出低延迟服务、避免内存泄漏和碎片化的前提。

## 核心原理

### 空闲链表与分配策略

最基础的分配器使用**空闲链表（Free List）**来追踪可用内存块。每个空闲块的头部存储元数据（大小、前后块指针），形成一个链表。分配时，分配器遍历链表寻找满足大小要求的块，常见策略有三种：

- **首次适配（First Fit）**：返回第一个足够大的块，速度快但容易在低地址产生碎片；
- **最佳适配（Best Fit）**：找到大小最接近的块，减少浪费但产生大量细小碎片；
- **下次适配（Next Fit）**：从上次分配位置继续搜索，分布更均匀。

块的元数据格式通常为：`[size|prev_free|next_free|...data...|size]`，头尾各存一个大小字段，使得相邻块合并（Coalescing）时可以 O(1) 定位邻居。

### 分级分配（Size Class）

现代分配器的关键优化是按对象大小将请求分流到不同的**尺寸类别（Size Class）**。以 jemalloc 为例，它将对象分为三类：
- **Small**：8字节 ～ 14KB，对齐到2的幂次或特定间隔（如8、16、32、48、64...字节）；
- **Large**：14KB ～ 4MB，以4KB页面为单位管理；
- **Huge**：>4MB，直接用 `mmap` 分配，独占整数个页面。

tcmalloc 维护88个尺寸类别，每个线程持有一个独立的**Thread Cache**，缓存小对象的空闲链表。当 Thread Cache 超过阈值（默认32KB）时，批量归还到进程级别的 Central Cache，彻底消除了小对象分配时的锁竞争。

### Slab 分配器原理

Slab 分配器由 Jeff Bonwick 于1994年为 Solaris 内核设计，专用于**固定大小对象的高频分配回收**。其核心思想是：为每种对象类型（如 `struct inode`）预先分配若干"slab"，每个 slab 包含固定数量的对象槽位，并维护三条链表：`full`（全满）、`partial`（部分使用）、`empty`（全空）。

分配时优先从 `partial` 链表取对象，避免了头部元数据开销和地址对齐计算。更重要的是，Slab 保留已销毁对象的**构造状态**（如已初始化的互斥锁），下次分配时跳过构造步骤，在 Linux 内核中这使 `kmem_cache_alloc` 的开销比通用 `kmalloc` 低约30%。

### Arena 与多线程扩展

Arena（竞技场）分配策略将堆内存划分为多个独立区域，每个线程或线程组绑定一个 Arena，从而将锁的粒度从全局缩小到单个 Arena。ptmalloc2（glibc 默认分配器）最多支持 `8 × CPU核心数` 个 Arena，避免了线程间的堆争用。

## 实际应用

**游戏引擎中的帧分配器**：Unity 和 Unreal Engine 在每帧开始时将一个线性分配器（Linear Allocator）的指针重置到基地址，帧内所有临时对象（粒子、碰撞查询结果）都从该 Arena 顺序分配，帧结束时一次性全部"释放"（仅移动指针），完全不需要逐个调用 `free`，单帧分配吞吐量可达数 GB/s。

**Redis 的 jemalloc 集成**：Redis 使用 jemalloc 的 `je_nallocx()` 接口查询实际分配大小，从而在记录对象内存占用时做到精确统计，避免了因分配器内部对齐补齐导致的统计偏差。这是 Redis `MEMORY USAGE` 命令能够返回准确值的底层依据。

**自定义对象池**：C++ 中通过重载 `operator new` 和 `operator delete`，可以为特定类接入 Slab 风格的池分配器，将该类对象的分配耗时从约100ns（系统 `malloc`）降低到约5ns（池分配）。

## 常见误区

**误区一：认为 `free` 会立即归还内存给操作系统**。实际上，`free` 只是将块标记为可用并加回分配器的空闲链表，操作系统看到的进程 RSS（常驻内存）通常不会立即缩小。jemalloc 会在空闲内存超过阈值后调用 `madvise(MADV_FREE)` 惰性归还，而 ptmalloc 仅对堆顶的空闲块调用 `brk()` 收缩，中间碎片无法归还。

**误区二：认为使用自定义分配器必然比 `malloc` 快**。Slab 和线性分配器仅在**单一对象类型或生命周期批量释放**的场景下才有优势。若将通用 `malloc` 替换为错配场景的分配器（如对变长字符串使用固定大小 Slab），反而会因外部碎片严重造成内存浪费数倍。

**误区三：混淆分配器的"分配粒度"与"对齐要求"**。x86-64 上 `malloc` 保证返回16字节对齐的地址（满足 SSE 指令要求），但这是 ABI 要求而非分配器的最小分配单元。分配器实际的最小块大小通常为32或48字节（需容纳空闲链表指针），因此 `malloc(1)` 实际消耗远超1字节。

## 知识关联

学习内存分配器需要先掌握**栈与堆**的区别——分配器管理的正是堆区，栈上对象由编译器通过调整 `rsp` 寄存器自动管理，无需分配器介入。

掌握内存分配器的基本原理后，可以进一步学习两个专用变体：**池分配器（Pool Allocator）** 是 Slab 思想的简化实现，专注于单一类型对象；**Arena 分配器**则将线性分配策略推向极致，通过放弃单独释放能力换取最大吞吐。这两个概念都建立在本文介绍的空闲链表、尺寸分级和 Arena 隔离机制之上。

理解分配器的碎片行为（内部碎片和外部碎片的产生条件）是研究**内存碎片化**问题的直接前提，而分配器性能的量化分析（吞吐量、延迟分布、RSS 增长曲线）则是**性能分析**实践中内存专项调优的核心内容。