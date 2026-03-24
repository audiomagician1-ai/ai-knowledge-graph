---
id: "concurrency-basics"
concept: "并发编程基础"
domain: "ai-engineering"
subdomain: "programming-basics"
subdomain_name: "编程基础"
difficulty: 4
is_milestone: false
tags: ["concurrency", "parallelism", "lock", "atomic"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 41.5
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.387
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 并发编程基础

## 概述

并发编程（Concurrent Programming）是指程序在同一时间段内处理多个任务的编程范式。与串行程序按顺序逐行执行不同，并发程序允许多个执行流（线程或进程）在逻辑上同时推进。注意"逻辑上同时"这一限定——在单核CPU上，并发通过快速切换任务上下文（Context Switching）实现，而并非物理意义上的同时执行。

"并发"（Concurrency）与"并行"（Parallelism）是两个经常被混淆的概念。并发强调结构上的同时处理能力，而并行特指多个任务在物理上同一时刻同时执行，需要多核CPU或多处理器支持。Rob Pike（Go语言设计者之一）在2012年的演讲中用经典比喻区分二者：并发是同时处理多件事情的能力（Dealing with lots of things at once），并行是同时做多件事情（Doing lots of things at once）。一个单核系统可以并发但不能并行，而多核系统既可以并发也可以并行。

在AI工程领域，并发编程尤为重要。训练数据的预处理、模型推理服务的批量请求处理、分布式训练中的梯度同步，都依赖并发机制来提升吞吐量。Python的`asyncio`异步框架、PyTorch的`DataLoader`多进程数据加载（`num_workers`参数），都是并发编程在AI场景中的直接体现。

## 核心原理

### 竞态条件与共享状态

当多个线程同时访问并修改同一块内存（共享状态）时，程序的输出取决于线程的执行顺序，这种不确定性称为**竞态条件**（Race Condition）。经典示例是对共享计数器执行`counter += 1`：该操作在底层被拆分为三步——读取当前值、加1、写回内存（读-改-写序列）。若线程A读取值为5后被中断，线程B也读取5并写回6，再切换回A写回6，两次递增的结果却只增加了1，这就是数据竞争（Data Race）的典型案例。

### 互斥锁（Mutex）

互斥锁（Mutual Exclusion Lock）是解决竞态条件最基础的同步原语。锁保证同一时刻只有一个线程能进入临界区（Critical Section）——即访问共享资源的代码段。在Python中，`threading.Lock()`提供互斥锁，其使用模式如下：

```python
import threading
lock = threading.Lock()
counter = 0

def increment():
    global counter
    with lock:          # 自动acquire和release
        counter += 1    # 临界区，保证原子性
```

使用锁需注意**死锁**（Deadlock）风险：若线程A持有锁1等待锁2，而线程B持有锁2等待锁1，两者互相等待，程序永久阻塞。预防死锁的一种方法是规定所有线程必须按固定顺序获取多把锁。此外，锁的粒度（Granularity）影响性能——粒度过粗会使并发退化为串行，粒度过细则引入过多锁管理开销。

### 原子操作

原子操作（Atomic Operation）是不可分割的操作，执行过程中不会被其他线程中断。与锁相比，原子操作通常由CPU指令直接支持（如x86的`LOCK CMPXCHG`指令），开销更低。Python的`threading`模块中，GIL（全局解释器锁，Global Interpreter Lock）使得简单的Python对象引用计数操作是原子的，但复合操作（如`counter += 1`）不是。若需真正的原子整型操作，可使用`multiprocessing.Value`配合锁，或在C扩展中使用原子类型。

Java和C++11提供了专门的原子类型：Java的`java.util.concurrent.atomic.AtomicInteger`提供`getAndIncrement()`方法，C++11的`std::atomic<int>`支持`fetch_add()`，这些操作在底层映射到CPU原子指令，无需显式加锁。

### 信号量与条件变量

信号量（Semaphore）是比互斥锁更通用的同步原语，由Edsger Dijkstra在1965年提出，包含一个整数计数器和`P`（wait/acquire）、`V`（signal/release）两个操作。互斥锁可视为计数器初始值为1的特殊信号量。信号量常用于限制并发资源访问数量，例如限制同时最多10个线程访问数据库连接池：`semaphore = threading.Semaphore(10)`。

条件变量（Condition Variable）允许线程在某个条件不满足时挂起等待，直到另一个线程修改条件并通知。经典的生产者-消费者模式中，消费者在队列为空时调用`condition.wait()`释放锁并阻塞，生产者放入数据后调用`condition.notify()`唤醒消费者，避免了轮询带来的CPU空转。

## 实际应用

**AI推理服务的并发请求处理**：使用FastAPI部署模型时，多个HTTP请求需要并发处理。利用`asyncio`的异步IO，单线程即可处理大量等待IO的请求（如数据库查询），而CPU密集的模型推理则通过`ProcessPoolExecutor`分发到多进程，绕过Python的GIL限制。

**PyTorch多进程数据加载**：`DataLoader(dataset, num_workers=4)`启动4个子进程并行预处理数据，主进程GPU训练与数据预处理流水线并发执行。每个worker进程独立维护内存空间，避免共享状态，这是规避Python GIL的常见设计模式。内部使用`multiprocessing.Queue`在进程间传递预处理完成的数据批次，Queue本身通过操作系统级锁保证线程安全。

**分布式训练中的梯度同步**：AllReduce算法要求所有GPU节点在参数更新前同步梯度，这本质上是一个全局屏障（Barrier）同步——每个节点完成本地计算后等待，直到所有节点都到达屏障才继续。PyTorch DDP（DistributedDataParallel）内部使用NCCL通信库实现这一同步语义。

## 常见误区

**误区一：Python多线程可以利用多核实现并行加速**。由于GIL的存在，CPython解释器中同一时刻只有一个线程能执行Python字节码。对于CPU密集型任务（如纯Python的矩阵运算），多线程不仅无法加速，还因上下文切换开销而更慢。正确做法是使用`multiprocessing`模块开启多进程（每个进程有独立GIL），或使用NumPy/PyTorch等释放GIL的C扩展库。

**误区二：使用了锁就绝对线程安全**。锁只保护临界区内的代码，若对同一共享变量的某些访问路径未加锁，仍然存在竞态。另一个陷阱是`check-then-act`模式：`if counter > 0: counter -= 1`，即使counter是原子类型，两行代码之间仍可能被中断，必须将整个检查-操作序列放在同一把锁的保护下。

**误区三：并发程序的bug可以通过测试稳定复现**。竞态条件高度依赖线程调度时序，在开发机上可能运行数千次无误，在高负载生产环境中才偶发崩溃。这类Heisenbug（观测行为时消失的bug）需要通过代码审查、静态分析工具（如Java的FindBugs）或动态检测工具（如C/C++的ThreadSanitizer）来发现，而非依赖功能测试。

## 知识关联

并发编程以**进程与线程**概念为直接前置——线程是并发的基本调度单位，理解线程的栈空间独立、堆空间共享的内存模型，是理解为何需要锁的物理基础。**函数**是并发任务的基本执行单元，每个线程通常以一个函数作为入口点（如Python的`threading.Thread(target=func)`）。**循环**结构在并发中需格外注意：`for`循环体内的共享变量修改是典型的竞态条件来源，而`while True`形式的轮询循环在并发中应改用条件变量来避免忙等待（Busy Waiting）。

掌握锁和原子操作后，可进一步学习无锁数据结构（Lock-free Data Structures）、内存模型与内存序（Memory Ordering，如C++11的`std::memory_order_relaxed`）等高级主题，以及Python `asyncio`协程（Coroutine）这一以单线程实现高并发的替代方案。在AI工程方向，并发编程知识直接支撑分布式训练框架的理解与调优。
