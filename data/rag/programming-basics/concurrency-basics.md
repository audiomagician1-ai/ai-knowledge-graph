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
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 并发编程基础

## 概述

并发编程（Concurrent Programming）是指在同一时间段内管理多个计算任务的编程范式，其中多个任务可以交替执行（并发）或真正同时执行（并行）。并发（Concurrency）与并行（Parallelism）是两个极易混淆的概念：并发强调任务的**逻辑同时性**，单核CPU通过时间片轮转让多个线程交替执行；并行强调任务的**物理同时性**，需要多核CPU同时运行多个线程。Rob Pike（Go语言设计者）将这一区别精炼为："并发是关于同时处理多件事，并行是关于同时做多件事。"

并发编程的历史可追溯至1960年代操作系统对多任务的需求。Dijkstra在1965年提出信号量（Semaphore）机制，这是最早的并发协调原语之一。此后，Java在1996年发布时内置了`synchronized`关键字，将线程同步引入主流编程语言。POSIX线程标准（pthreads）于1995年发布，规范了Unix系统的线程API。

在AI工程领域，数据预处理管道、模型推理服务以及分布式训练框架（如PyTorch的DataLoader）都大量依赖并发编程。理解并发基础能帮助AI工程师正确使用多线程数据加载（`num_workers`参数）、避免共享模型权重时的竞态条件，以及利用多进程规避Python的GIL（全局解释器锁）限制。

---

## 核心原理

### 竞态条件与临界区

竞态条件（Race Condition）发生在两个或多个线程同时读写同一共享数据，且最终结果依赖于线程的执行顺序时。经典示例是两个线程同时对整数`counter`执行`counter += 1`：在底层，这个操作会被拆分为**读取→修改→写回**三步（Read-Modify-Write），若两个线程在"读取"后均读到旧值，则一次自增操作将丢失，这称为**写-写冲突**。包含竞态条件的代码段称为**临界区**（Critical Section），必须受到保护。

### 互斥锁（Mutex）

互斥锁是保护临界区最基础的机制。`mutex.lock()`确保同一时刻只有一个线程能进入临界区，其他线程将在`lock()`处**阻塞**，直到持有者调用`mutex.unlock()`。Python中对应`threading.Lock()`：

```python
import threading

counter = 0
lock = threading.Lock()

def increment():
    global counter
    with lock:          # 自动 acquire 和 release
        counter += 1    # 临界区，同一时刻仅一线程执行
```

使用`with lock`语法可防止因异常导致锁未释放的**死锁**（Deadlock）风险。死锁的经典场景是线程A持有锁1等待锁2，线程B持有锁2等待锁1，双方永久阻塞。Coffman（1971年）定义了死锁成立的四个必要条件：互斥、占有并等待、非抢占、循环等待——破坏任意一个即可预防死锁。

### 原子操作

原子操作（Atomic Operation）是不可中断的最小操作单元，执行过程中不会被线程切换打断。现代CPU提供硬件级原子指令，如x86架构的`LOCK XADD`（原子加法）和`CMPXCHG`（比较并交换，CAS）。CAS的语义是：若内存中的值等于期望值，则将其更新为新值，否则不做操作，整个过程原子完成。

Python的`threading`模块下，GIL为CPython的字节码级别提供了有限的原子性保证，但Python整数的`+=`操作**不是**原子的（需要多条字节码）。在C++中，`std::atomic<int>`提供了真正的硬件原子操作：

```cpp
std::atomic<int> counter(0);
counter.fetch_add(1, std::memory_order_relaxed);  // 无锁原子自增
```

### 并发原语：信号量与条件变量

信号量（Semaphore）是整数计数器，`acquire()`将其减1（若为0则阻塞），`release()`将其加1并唤醒等待线程。信号量可控制同时访问资源的线程数量，例如限制最多3个线程同时访问GPU：`semaphore = threading.Semaphore(3)`。

条件变量（Condition Variable）用于**生产者-消费者模型**：消费者在队列为空时调用`condition.wait()`进入睡眠并释放锁，生产者放入数据后调用`condition.notify()`唤醒消费者，这避免了消费者忙等待（Busy Waiting）导致的CPU浪费。

---

## 实际应用

**PyTorch DataLoader多进程加载**：DataLoader通过`num_workers`参数启动多个**子进程**（Process）而非线程，以绕过Python GIL限制。每个worker进程独立读取磁盘数据并放入共享内存队列，主进程从队列取批次送入GPU。这里使用进程而非线程的原因正是GIL——GIL使得多线程无法真正并行执行Python字节码，而CPU密集型的图像解码任务需要真正的并行性。

**模型推理服务**：生产环境中的推理服务（如Triton Inference Server）使用线程池（Thread Pool）处理并发请求。多个请求线程可并行执行预处理（I/O密集型），但模型前向计算通常在单一GPU上串行执行，通过请求队列+批处理（Dynamic Batching）提升吞吐量。

**分布式训练中的梯度同步**：AllReduce操作（如NCCL库实现）本质上是多GPU/多机之间的并发原语——所有进程在`barrier`点同步，聚合梯度后继续下一步，这是并发编程中**屏障（Barrier）**同步模式的直接应用。

---

## 常见误区

**误区一：认为Python多线程能加速CPU密集型任务**。由于CPython的GIL（Global Interpreter Lock）在同一时刻只允许一个线程执行Python字节码，多线程在CPU密集任务（如纯Python的矩阵计算）上不仅不能并行，反而因线程切换开销而变慢。正确做法是使用`multiprocessing`模块创建多进程，或使用NumPy/PyTorch（它们在底层C代码中释放GIL）。

**误区二：加锁越多越安全**。过度使用锁会导致两类问题：（1）**死锁**——多把锁的嵌套获取顺序不一致时产生循环等待；（2）**锁竞争瓶颈**——所有线程在同一把粗粒度锁上排队，并发度退化为串行度。正确做法是最小化临界区范围，对独立资源使用独立的细粒度锁（Fine-grained Locking）。

**误区三：认为volatile关键字（Java/C++）能替代同步**。`volatile`仅保证变量的**可见性**（每次读取直接从主内存读而非寄存器缓存），但不保证**原子性**。例如，`volatile int counter`的`counter++`仍然存在竞态条件，必须配合`synchronized`或`std::atomic`使用。

---

## 知识关联

**前置知识**：理解并发编程必须先掌握**进程与线程**的概念——进程拥有独立内存空间，线程共享进程内存，正是这种共享内存结构才导致了竞态条件问题。**函数**是并发编程的基本执行单元，线程的入口就是一个可调用函数（`target=func`）。**循环**是并发场景下忙等待和轮询逻辑的基础结构，理解`while not condition: pass`的低效性才能体会条件变量的价值。

**横向扩展**：掌握并发基础后，可进一步学习Python的`asyncio`异步编程模型——它用单线程事件循环（Event Loop）实现并发，用`await`代替阻塞调用，特别适合大量I/O等待的AI推理服务场景。分布式训练中的进程组（Process Group）通信、消息传递接口（MPI）也直接建立在多进程并发协调的原理之上。