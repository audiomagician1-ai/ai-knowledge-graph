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
quality_tier: "A"
quality_score: 73.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---


# 内存分配器

## 概述

内存分配器（Memory Allocator）是管理堆内存生命周期的用户态软件组件，实现了 `malloc`/`free`（C语言）与 `new`/`delete`（C++）背后的具体分配策略。当程序调用 `malloc(100)` 时，操作系统并不会每次都被打扰——分配器会预先通过 `brk()` 或 `mmap()` 系统调用向内核申请一大块连续内存（通常以 128KB 为最小粒度），然后在用户空间自主切分、追踪和回收，从而将每次分配的成本从微秒级内核陷入降至纳秒级用户态操作。

内存分配器的历史可追溯到 1979 年由 Doug Lea 设计的 dlmalloc，它成为后来 glibc 中 ptmalloc2 的直接原型。2005 年，Google 开源了 tcmalloc（Thread-Caching Malloc），同年 Facebook 工程师 Jason Evans 为 FreeBSD 开发了 jemalloc（2006 年正式合并入 FreeBSD 基础系统）。jemalloc 目前被 Redis、Rust 标准库（从 1.32.0 起在 Linux 上默认启用）以及 Meta 的后端服务大量采用。这些分配器的核心动机是解决 dlmalloc 在多线程场景下依赖单一全局锁所导致的严重竞争——在 32 核服务器上，ptmalloc 的 `malloc` 吞吐量仅为 tcmalloc 的 1/5 左右（参见 Ghemawat & Menage, 2005，*TCMalloc: Thread-Caching Malloc*，Google 技术报告）。

理解分配器的工作机制是写出低延迟服务、规避内存碎片和定位内存泄漏的必要前提。

---

## 核心原理

### 空闲链表与边界标记

最基础的分配器使用**空闲链表（Free List）**追踪可用内存块。每个内存块的头部存储元数据，经典的**边界标记（Boundary Tag）**格式由 Donald Knuth 于1973年在《计算机程序设计艺术》第一卷中首次描述：

```
[Header: size | is_free] [....data....] [Footer: size | is_free]
```

头尾各存一个字段的设计使相邻块合并（Coalescing）可以在 $O(1)$ 时间内完成——释放一个块时，只需读取其左邻块的 Footer 和右邻块的 Header，即可判断是否能合并，无需遍历整个链表。

分配时，分配器遍历空闲链表寻找满足大小要求的块，常见策略有三种：

- **首次适配（First Fit）**：返回第一个大小满足要求的块，平均搜索时间 $O(n/2)$，低地址易产生外部碎片；
- **最佳适配（Best Fit）**：找到大小最接近请求的块，理论上碎片最小，但每次需遍历全表 $O(n)$；
- **下次适配（Next Fit）**：从上次分配结束位置继续搜索，碎片分布更均匀，在实测中常优于 Best Fit。

内存利用率上界由 Wilson 等人于1995年证明：对于任意分配序列，First Fit 策略的碎片率不超过已使用内存的 $O(\log n)$ 倍（Wilson et al., 1995，*Dynamic Storage Allocation: A Survey and Critical Review*）。

### 分级分配（Size Class）

现代分配器的关键优化是按对象大小将请求**分流到不同的尺寸类别（Size Class）**，彻底避免对任意大小块的线性搜索。以 jemalloc 3.x 为例，其尺寸分级如下：

| 类别     | 大小范围         | 管理粒度              |
|--------|-------------|--------------------|
| Small  | 8B ～ 14KB  | 按 2 的幂次对齐（8、16、32、48、64、80…字节，共 44 个 size class） |
| Large  | 14KB ～ 4MB | 以 4KB 页面（Page）为单位  |
| Huge   | > 4MB       | 直接 `mmap`，独占整数个页面 |

tcmalloc 维护 **88 个尺寸类别**，每个线程持有一个独立的 **Thread Cache**（默认上限 32KB），缓存小对象的空闲链表。Thread Cache 满时，将 L 个对象（L 为该 size class 的 `batch_size`，通常为 32～512）批量归还到进程级 **Central Cache**（一个基数树索引的 Span 管理结构），彻底消除了小对象分配的锁竞争。

### Slab 分配器原理

Slab 分配器由 Jeff Bonwick 于 1994 年为 Solaris 2.4 内核设计，论文《*The Slab Allocator: An Object-Caching Kernel Memory Allocator*》发表于 USENIX 1994 年年会（Bonwick, 1994）。其核心思想是：为**每种固定大小的对象类型**（如内核的 `struct inode`、`struct task_struct`）预先分配若干 slab，每个 slab 包含固定数量的对象槽位。

每种对象维护三条 slab 链表：
- `full`：所有槽位已分配；
- `partial`：部分槽位空闲（优先从此处分配）；
- `empty`：所有槽位空闲（可释放回操作系统）。

Slab 分配的核心优势是**对象缓存（Object Caching）**：释放对象时不清零、不销毁，而是保留其初始化状态（构造函数已调用过一次），下次分配同类对象时直接复用，省去重复初始化的 CPU 开销。Linux 内核从 2.2 版本引入 Slab，后续演化出 SLUB（2.6.22，2007 年）和 SLOB（嵌入式场景），其中 SLUB 消除了 Slab 的三条链表，改用每 CPU 的 active slab 指针，降低了元数据开销。

---

## 关键公式与性能模型

评估分配器性能时，常用以下两个核心指标：

**内存利用率（Memory Utilization）**定义为：

$$U = \frac{\sum_{i} s_i}{H_{max}}$$

其中 $s_i$ 是第 $i$ 次分配请求的有效载荷大小，$H_{max}$ 是堆的峰值占用字节数（包含元数据和碎片）。理想分配器的 $U$ 趋近于 1，实际系统中 tcmalloc 在小对象密集场景下 $U$ 约为 0.85～0.92。

**吞吐量（Throughput）**常以每秒可完成的 `malloc`/`free` 对数衡量。以下为一个使用 C 标准库与自定义 Arena 分配器的对比示例：

```c
// 标准 malloc：每次调用约 50～200ns（视竞争情况）
for (int i = 0; i < 1000000; i++) {
    void *p = malloc(64);
    free(p);
}

// Arena 分配器：批量预分配 4MB，单次分配仅需指针移动，约 2～5ns
typedef struct {
    char  *base;
    size_t used;
    size_t capacity;
} Arena;

void *arena_alloc(Arena *a, size_t size) {
    size = (size + 7) & ~7ULL;          // 8字节对齐
    if (a->used + size > a->capacity) return NULL;
    void *ptr = a->base + a->used;
    a->used += size;
    return ptr;
}
// arena_free 只需将 a->used 归零，整体释放 O(1)
```

Arena 分配器（也称线性分配器/Bump Pointer Allocator）的 `arena_alloc` 本质上只是一次加法和一次比较，其时间复杂度严格为 $O(1)$，在游戏引擎（如 Unreal Engine 的帧级 Arena）和编译器（LLVM 的 `BumpPtrAllocator`）中被广泛采用。

---

## 实际应用场景

**高频小对象服务（如 Redis）**：Redis 在 Linux 上默认使用 jemalloc 而非 glibc 的 ptmalloc2，原因是 ptmalloc2 在频繁 `malloc`/`free` 小键值对（通常 8～128 字节）后会产生严重的内存碎片，导致进程占用的 RSS（Resident Set Size）远超实际数据大小，而 jemalloc 的 size class 设计将外部碎片率控制在 4% 以内。Redis 4.0 引入 `mem_allocator` 配置项，允许运行时报告所用分配器类型。

**游戏引擎与实时系统**：Unreal Engine 5 在每帧渲染开始时重置一个 64MB 的帧级 Arena，所有帧内临时对象从此 Arena 分配，帧结束时整体释放。这种模式完全避免了碎片和 `free` 的开销，使帧间内存分配的 CPU 耗时从 ~0.5ms（通用分配器）降至 ~0.02ms。

**Rust 自定义分配器（Global Allocator API）**：Rust 1.28（2018年）稳定化了 `#[global_allocator]` 属性，允许替换默认分配器：

```rust
use tikv_jemallocator::Jemalloc;

#[global_allocator]
static GLOBAL: Jemalloc = Jemalloc;
```

TiKV（PingCAP 的分布式 KV 存储）通过此机制将默认的 System allocator 替换为 jemalloc，在写密集型负载下吞吐量提升约 20%。

---

## 常见误区

**误区1：`free` 会立即将内存归还给操作系统。**  
实际上，`free` 仅将块放回分配器的空闲链表，内核并不感知。分配器只有在持有超过阈值（ptmalloc 默认为 128KB）的连续空闲内存时，才会调用 `brk()` 缩减堆顶，或以 `munmap()` 归还 `mmap` 分配的块。这意味着进程的 RSS 在 `free` 后通常不会立即下降，这是监控脚本常见的误判来源。

**误区2：小对象分配开销可以忽略不计。**  
在每秒千万次分配的场景（如解析引擎、消息队列），通用分配器的元数据写入（每个块至少 8 字节 header）和锁竞争会构成显著瓶颈。Facebook 在其 Folly 库中实现的 `folly::small_vector` 和 `folly::Arena` 正是为了消除这类开销——内部测试表明，在 JSON 解析场景中使用 Arena 分配器可将分配相关 CPU 时间从总耗时的 18% 降至 2%。

**误区3：自定义分配器总是比通用分配器快。**  
Arena 分配器不支持单独释放中间对象，Slab 分配器只适合固定大小对象。错误地将 Arena 用于生命周期不统一的对象会导致大量内存无法释放，RSS 持续增长。选择分配策略必须匹配对象的**生命周期模式**：生命周期统一用 Arena，固定大小高频用 Slab，通用场景用 tcmalloc/jemalloc。

---

## 知识关联

**前置知识**：理解内存分配器需要掌握**栈与堆**的区别——栈内存由编译器通过 `rsp` 寄存器移动自动管理，而堆内存的生命周期由程序员（或 GC）显式控制，分配器正是这一控制的具体实现层。

**后续概念**：
- **池分配器（Pool Allocator）**：Slab 分配器的简化形式，专用于单一固定大小对象，常用于网络连接对象、数据库行缓存等场景；
- **Arena 分配器**：本文代码示例的正式形式，LLVM、CPython 的 `pymalloc`（针对 ≤512 字节对象的三级 Arena 结构，引入于 Python 2.3）均采用此模式；
- **内存碎片化**：分配器设计的核心挑战，分为外部碎片（空闲块无法被利用）和内部碎片（块内部的元数据/对齐浪费），是选择 size class 粒度的主要权衡依据；
- **性能分析**：使用 `heaptrack`、`massif`（Valgrind 套件）或 `jemalloc` 内置的 `mallctl` 接口可以定量分析分配热点和碎片率，是优化分配策略的第一步。

**思考问题**：jemalloc 为 Redis 解决了碎片问题