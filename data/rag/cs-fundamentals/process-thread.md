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
quality_tier: "pending-rescore"
quality_score: 40.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.364
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 进程与线程

## 概述

进程（Process）是操作系统进行资源分配和调度的基本单位，代表一个正在运行的程序实例。每个进程拥有独立的虚拟地址空间、文件描述符表、信号处理表以及至少一个执行线程。线程（Thread）则是CPU调度和执行的基本单位，同一进程内的多个线程共享该进程的内存空间和系统资源，但各自维护独立的程序计数器（PC）、寄存器组和栈空间。

进程概念随1960年代分时操作系统的出现而诞生。UNIX系统在1969年正式引入进程模型，通过`fork()`系统调用创建子进程。线程概念则在1980年代随着多核处理器的发展逐渐普及，POSIX线程标准（pthreads）于1995年正式确立，为不同操作系统提供了统一的线程编程接口。

在AI工程中，进程与线程的差异直接影响模型训练的并行效率。Python的全局解释器锁（GIL）导致CPython解释器在同一时刻只允许一个线程执行Python字节码，这迫使AI框架（如PyTorch的DataLoader）在CPU密集型任务中使用多进程而非多线程来实现真正的并行数据加载。

## 核心原理

### 进程的内存布局与隔离机制

每个进程在Linux系统中拥有独立的虚拟地址空间，64位系统下通常为128TB。该空间从低地址到高地址依次划分为：代码段（.text）、已初始化数据段（.data）、未初始化数据段（.bss）、堆（向高地址增长）、内存映射区、栈（向低地址增长）以及内核空间。进程间的这种硬隔离通过MMU（内存管理单元）的页表机制实现，一个进程的崩溃不会直接污染其他进程的内存，这是多进程架构比多线程架构更健壮的根本原因。

### 线程的上下文切换开销

线程上下文切换需要保存和恢复的状态远少于进程切换。进程上下文切换必须切换页表（触发TLB刷新），而同进程内的线程切换只需保存/恢复寄存器状态（约16个通用寄存器 + FPU/SSE寄存器）。实测数据表明，Linux上进程切换耗时约3-5μs，而线程切换约为1-2μs。在高并发场景下，这种差异会显著影响系统吞吐量。每个线程默认栈大小在Linux上为8MB（可通过`ulimit -s`查看），创建大量线程会导致明显的内存消耗。

### 进程间通信（IPC）机制

进程因内存隔离而需要专门的IPC机制，主要包括：
- **管道（Pipe）**：单向字节流，容量通常为64KB（Linux内核4.x默认值），适合父子进程间的简单通信
- **共享内存（Shared Memory）**：最快的IPC方式，通过`mmap()`或`shmget()`让多个进程映射同一物理页，需配合信号量（Semaphore）防止竞态条件
- **消息队列（Message Queue）**：以消息为单位传递数据，支持按消息类型选择性接收，适合AI系统中Worker进程向主进程汇报训练指标
- **Socket**：支持跨机器通信，PyTorch分布式训练的`torch.distributed`模块底层使用TCP Socket或InfiniBand RDMA

线程间通信则更直接，同进程内的线程可直接读写共享变量，但必须通过互斥锁（Mutex）、条件变量（Condition Variable）或读写锁（RWLock）来保证数据一致性。

### 进程与线程的创建方式对比

Linux中`fork()`创建进程采用写时复制（Copy-on-Write）技术，父子进程共享物理页，只有在写操作时才真正复制，大幅降低了`fork()`的开销。`pthread_create()`创建线程时，操作系统为新线程分配独立的栈空间和线程控制块（TCB），但不需要复制地址空间。Python的`multiprocessing`模块在Unix系统上默认使用`fork`，在Windows上则使用`spawn`（完整启动新解释器），这导致Windows上多进程启动时间显著更长。

## 实际应用

**PyTorch DataLoader的多进程数据加载**：PyTorch DataLoader将`num_workers`参数设为大于0时，会使用`multiprocessing`模块创建多个工作进程并行预处理数据。主进程与工作进程之间通过共享内存传递Tensor数据（利用`torch.multiprocessing`的`share_memory_()`），避免了大数据量序列化的开销。若使用多线程替代，GIL会使CPU密集型的图像解码操作无法真正并行。

**TensorFlow的线程池推理服务**：TensorFlow Serving在处理推理请求时，使用线程池（默认线程数 = CPU核心数）来并发处理多个请求。由于TensorFlow的C++底层不受GIL约束，线程间可真正并行执行算子计算，同时共享已加载的模型权重内存，相比多进程模型节省了数倍的内存占用。

**Ray分布式框架中的Actor模型**：Ray将每个Actor封装为独立进程，利用进程隔离保障不同任务的容错性。Ray Worker进程间通过Plasma共享内存对象存储传递大型NumPy数组，零拷贝传输使得在同一机器上传输1GB数据的延迟低于1ms。

## 常见误区

**误区一：多线程一定比多进程快**。许多初学者认为线程更轻量所以更快，但在Python中受GIL限制，CPU密集型任务（如纯Python实现的矩阵运算）使用多线程不仅无法并行，还会因线程竞争GIL产生额外开销，实测性能可能比单线程还低10%-20%。只有I/O密集型任务（等待网络、磁盘时GIL会释放）才适合用Python多线程加速。

**误区二：进程隔离意味着进程间完全无法共享数据**。进程的虚拟地址空间独立，但可以通过`mmap()`将同一文件或匿名内存区域映射到不同进程的地址空间，实现零拷贝的高效数据共享。PyTorch的`tensor.share_memory_()`正是利用这一机制，使不同进程可以直接访问同一块物理内存中的模型参数。

**误区三：线程数越多并发性能越好**。线程数超过CPU核心数后，额外的线程不仅无法提升CPU并行度，还会引入频繁的上下文切换开销。一般建议CPU密集型任务的线程数等于CPU核心数，I/O密集型任务可设为核心数的2-4倍，具体上限需通过压测确定。

## 知识关联

**前置知识衔接**：理解进程与线程需要CPU执行原理中程序计数器和寄存器的概念——线程本质上是一个独立的CPU执行流，其私有状态就是CPU在某一时刻的寄存器快照。操作系统基础中的虚拟内存和页表机制则直接解释了为何进程间地址空间相互隔离而线程不隔离。

**后续知识延伸**：多线程共享内存的特性直接引出死锁问题——当线程A持有锁1等待锁2、线程B持有锁2等待锁1时发生死锁，需要理解加锁顺序一致性等预防策略。I/O模型（阻塞/非阻塞/异步）的选择与线程管理开销密切相关，高并发I/O场景下单线程事件循环（如Node.js、Python asyncio）可避免为每个连接创建线程的开销。并发编程基础中的原子操作、内存屏障和无锁数据结构，均以多线程共享同一进程内存这一特性为基础。
