---
id: "process-thread"
concept: "进程与线程"
domain: "ai-engineering"
subdomain: "cs-fundamentals"
subdomain_name: "计算机基础"
difficulty: 3
is_milestone: false
tags: ["process", "thread", "concurrency"]

# Quality Metadata (Schema v2)
content_version: 6
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 进程与线程

## 概述

进程（Process）是操作系统进行资源分配和调度的基本单位，代表一个正在执行的程序实例。每个进程拥有独立的虚拟地址空间、文件描述符表、信号处理器和其他系统资源。1960年代，IBM OS/360首次引入多道程序设计概念，现代进程模型由此演化而来。

线程（Thread）是进程内部的执行单元，是CPU调度和分派的基本单位。同一进程内的多个线程共享进程的代码段、数据段、堆空间和文件描述符，但每个线程拥有独立的栈空间（默认大小通常为8MB，在Linux系统中可通过`ulimit -s`查看）、程序计数器（PC）和寄存器组。

在AI工程场景中，理解进程与线程的区别直接影响深度学习训练框架的设计选择。Python的全局解释器锁（GIL）导致CPython解释器中多线程无法真正并行执行CPU密集型任务，这是为何PyTorch的DataLoader默认采用多进程（`num_workers`参数控制子进程数量）而非多线程来并行加载数据的根本原因。

---

## 核心原理

### 进程的内存布局与资源隔离

每个进程的虚拟地址空间在Linux x86-64系统中通常为128TB，由内核空间（高位）和用户空间（低位）组成。用户空间自低到高依次排列：代码段（.text）、数据段（.data/.bss）、堆（向高地址增长）、内存映射区、栈（向低地址增长）。进程间的内存隔离由操作系统通过页表机制实现——两个进程访问同一虚拟地址实际指向不同的物理内存页，因此一个进程崩溃不会直接破坏另一个进程的内存。

### 线程的上下文切换开销

线程切换的代价远低于进程切换，因为同一进程内线程共享页表，无需切换内存映射。进程切换时，CPU需要刷新TLB（Translation Lookaside Buffer，快表），这一操作在多核系统中代价尤为显著。具体数据上，线程上下文切换耗时约为1~10微秒，而进程切换由于TLB刷新可达10~100微秒。Linux内核通过`task_struct`结构体同时表示进程和线程（线程在Linux内核中称为轻量级进程，LWP），`clone()`系统调用通过不同的标志位控制资源共享粒度：`CLONE_VM`共享内存空间，`CLONE_FILES`共享文件描述符。

### 线程的同步与互斥原语

由于线程共享堆内存，并发写操作会引发竞争条件（Race Condition）。解决方案包括：
- **互斥锁（Mutex）**：通过`pthread_mutex_lock/unlock`实现，保证同一时刻只有一个线程进入临界区。
- **读写锁（RWLock）**：允许多个线程同时读，但写操作独占，适合读多写少的场景（如AI推理服务的模型权重访问）。
- **信号量（Semaphore）**：由Dijkstra于1965年提出，通过P（`wait`）和V（`signal`）操作控制对有限资源的并发访问数量，常用于限制线程池中的并发任务数。

原子操作（Atomic Operation）是无锁编程的基础，CPU通过`LOCK`前缀指令保证操作的不可分割性，例如`fetch_and_add`可在不加锁的情况下对共享计数器进行线程安全的递增。

### 进程间通信（IPC）机制对比

进程间无法直接访问对方内存，需要借助操作系统提供的IPC机制：

| 机制 | 特点 | 典型延迟 |
|------|------|----------|
| 管道（Pipe） | 单向、字节流、亲缘进程间 | ~1μs |
| 命名管道（FIFO） | 允许非亲缘进程通信 | ~1μs |
| 消息队列 | 有边界的消息、内核缓冲 | ~5μs |
| 共享内存（SHM） | 最快IPC，需配合信号量同步 | ~100ns |
| 套接字（Socket） | 可跨主机，分布式系统基础 | 本地~10μs |

PyTorch多进程训练（`torch.multiprocessing`）在同一机器上默认使用共享内存传递张量，正是利用了共享内存接近内存访问速度的延迟优势。

---

## 实际应用

**Python多进程绕过GIL**：在数据预处理、特征工程等CPU密集型任务中，使用`multiprocessing.Pool`创建多个独立Python解释器进程，每个进程拥有独立的GIL，从而实现真正的多核并行。例如：

```python
from multiprocessing import Pool
with Pool(processes=4) as pool:
    results = pool.map(preprocess_fn, data_chunks)
```

**Web服务器的进程/线程模型选择**：Nginx采用多进程单线程模型（Master-Worker架构），每个Worker进程独立处理请求，故障隔离性强；uWSGI服务Python AI推理服务时，可配置`--processes 4 --threads 2`，即4个进程各含2个线程，在隔离性与并发效率间取得平衡。

**CUDA多流与线程的关系**：GPU深度学习训练中，CUDA Stream本质上是GPU端的任务队列，由CPU线程提交。多个CPU线程可分别管理不同的CUDA Stream，实现数据传输与计算的异步重叠（overlap），这要求开发者理解CPU线程与GPU流之间的所有权关系。

---

## 常见误区

**误区一：Python多线程可以加速CPU密集型计算**
由于CPython的GIL在同一时刻只允许一个线程执行Python字节码，多线程在CPU密集任务中不仅不能提速，反而因线程切换开销略慢于单线程。但对于I/O密集型任务（网络请求、文件读写），线程在等待I/O时会释放GIL，多线程仍然有效。区分任务类型是选择多进程还是多线程的第一步。

**误区二：线程越多，程序越快**
线程数超过CPU核心数后，额外线程只会增加上下文切换开销而非提升吞吐量。经验公式：对于CPU密集型任务，最优线程数≈CPU核心数；对于I/O密集型任务，最优线程数可达核心数的数倍（具体取决于I/O等待时间占比）。在AI推理服务中盲目增大线程池大小是常见的性能调优误区。

**误区三：共享内存是"免费"的IPC**
共享内存虽然避免了数据拷贝，但写操作必须配合锁或信号量同步，否则会产生数据竞争。此外，多个进程频繁修改同一缓存行（64字节）会引发缓存一致性协议（MESI）中的"False Sharing"问题，使实际性能远低于预期。

---

## 知识关联

理解进程与线程的资源共享模型是学习**死锁**的前提：死锁的四个必要条件（互斥、占有并等待、不可剥夺、循环等待）全部建立在多个线程或进程竞争共享资源的基础上，而共享资源的边界正是由进程的隔离性和线程的共享性所定义的。

进程的阻塞与非阻塞行为直接引出**I/O模型**的讨论。当一个线程执行阻塞式`read()`系统调用时，该线程进入睡眠状态，操作系统将CPU调度给其他线程——这一机制是区分阻塞I/O、非阻塞I/O、I/O多路复用（select/poll/epoll）和异步I/O的核心差异所在。

在**并发编程基础**中，进程与线程的调度单位差异决定了不同并发模型的适用场景：基于线程的并发（Thread-per-request）、基于事件循环的协程并发（Python asyncio、Node.js）、以及Actor模型（Erlang、Akka）各自对应不同的进程/线程使用策略，其性能权衡需要以本文所述的上下文切换开销和内存隔离代价为量化依据。