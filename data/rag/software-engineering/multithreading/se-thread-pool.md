---
id: "se-thread-pool"
concept: "线程池"
domain: "software-engineering"
subdomain: "multithreading"
subdomain_name: "多线程"
difficulty: 2
is_milestone: false
tags: ["模式"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 41.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.444
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 线程池

## 概述

线程池（Thread Pool）是一种预先创建并维护一组工作线程的并发编程模式。它的核心思想是：在程序启动时（或首次需要时）创建固定数量的线程，将这些线程放入"池"中待命，当任务到来时从池中取出空闲线程执行，任务完成后线程归还到池中而不是被销毁。这种"线程复用"机制避免了频繁创建和销毁线程带来的开销。

线程池的概念在1990年代随着服务器端编程的普及而逐渐成熟。Java在JDK 1.5（2004年）通过`java.util.concurrent.Executors`正式将其标准化，提供了`newFixedThreadPool`、`newCachedThreadPool`等工厂方法。线程创建和销毁一次的系统开销约为数十微秒至数百微秒，当一个Web服务器每秒处理数万请求时，若每个请求都新建线程，这种开销会快速累积成性能瓶颈。

线程池解决的不仅是性能问题，更是资源管理问题。若不加限制地创建线程，每个线程默认需要占用约1MB的栈内存（Linux x86-64下默认为8MB），一台4GB内存的服务器最多只能同时维持数千个线程，超过这个上限会导致`OutOfMemoryError`。线程池通过设定上限将并发资源约束在可控范围内。

## 核心原理

### 线程复用与任务队列

线程池的工作流程围绕一个**阻塞队列（BlockingQueue）**展开。提交方将任务（`Runnable`或`Callable`对象）放入队列，工作线程在队列为空时阻塞等待（调用`queue.take()`），任务到来后被唤醒取出执行。这一设计将"任务生产者"与"任务消费者"解耦，生产者无需关心哪个线程执行任务。

Java的`ThreadPoolExecutor`构造函数接受7个参数，其中最关键的三个决定了线程池的动态行为：
- `corePoolSize`：核心线程数，即使空闲也不会被销毁
- `maximumPoolSize`：最大线程数，队列满时可临时扩充至此值
- `keepAliveTime`：超过核心数的线程在空闲此时长后会被销毁

任务提交时的决策顺序为：当前线程数 < corePoolSize → 新建线程；否则尝试入队；队列已满且线程数 < maximumPoolSize → 新建临时线程；否则执行拒绝策略（`RejectedExecutionHandler`）。

### 工作窃取算法（Work Stealing）

标准线程池使用单一共享队列，所有线程竞争同一个队列会产生锁争用。Java 7引入的`ForkJoinPool`采用**工作窃取（Work Stealing）**算法解决了这一问题：每个工作线程维护自己的**双端队列（deque）**，线程优先从自己队列的**头部**取任务执行；当自己的队列为空时，从其他线程队列的**尾部**"窃取"任务。

这种设计之所以高效，在于窃取操作发生在队列尾部，而队列所有者在头部操作，两端争用的概率极低，几乎实现了无锁化。`ForkJoinPool`特别适合**递归分治**型任务（如归并排序、树的遍历），任务会不断拆分成子任务放入deque，负载自动在各线程间均衡。`ForkJoinPool.commonPool()`是Java 8并行流（parallel stream）底层使用的线程池，默认线程数等于`Runtime.getRuntime().availableProcessors() - 1`。

### 线程池大小的选择公式

线程池大小不是越大越好。对于**CPU密集型任务**，推荐线程数 = CPU核心数 + 1，多出的1个线程用于补偿偶发的缺页中断。对于**I/O密集型任务**，推荐公式为：

> **线程数 = CPU核心数 × (1 + 等待时间 / 计算时间)**

例如，一台8核服务器上，若某任务的I/O等待时间是计算时间的9倍，则最优线程数 = 8 × (1 + 9) = 80。这个公式来源于利特尔法则（Little's Law）在CPU利用率最大化中的应用。

## 实际应用

**Web服务器请求处理**：Tomcat内置线程池默认`maxThreads=200`，`minSpareThreads=10`。每个HTTP请求到来时从池中取线程处理，响应完成后归还，避免了为每个TCP连接新建线程的开销。在压测场景下，线程池满时会进入等待队列（默认队列长度100），超出后返回503错误，这是线程池拒绝策略在生产环境的典型体现。

**数据库连接池的类比**：线程池与数据库连接池（如HikariCP）设计思想相同——连接的创建代价高（约需200ms建立TCP+TLS握手），因此预先创建并复用。理解线程池后，连接池的`maximumPoolSize`、`connectionTimeout`等配置的含义自然类推可得。

**Android AsyncTask的演变**：Android早期的`AsyncTask`底层使用串行的`SerialExecutor`（单线程池），后改为`THREAD_POOL_EXECUTOR`（核心线程数=CPU数+1），这一变更导致并发执行顺序不确定，曾引发大量开发者的任务顺序依赖Bug，是线程池并发语义改变影响上层应用的经典案例。

## 常见误区

**误区一：线程池越大，吞吐量越高**。实际上，线程数超过CPU核心数后，额外线程会引入上下文切换（context switch）开销。在纯CPU密集型场景下，将线程数从32增加到256，吞吐量可能不升反降15%~30%，因为操作系统的线程调度本身会消耗CPU时钟。

**误区二：`newCachedThreadPool`适合所有高并发场景**。`CachedThreadPool`的`maximumPoolSize`为`Integer.MAX_VALUE`（约21亿），当请求瞬间涌入时，它会疯狂创建线程直至内存耗尽。阿里巴巴Java开发手册明确禁止在生产代码中直接使用`Executors`工厂方法，要求手动设置`maximumPoolSize`上限，正是针对这一风险。

**误区三：`shutdown()`会立即停止所有任务**。`shutdown()`只是停止接受新任务，已在队列中的任务和正在执行的任务会继续运行直到完成。若需要立即中断，应调用`shutdownNow()`，它会向正在执行的线程发送`interrupt()`信号，并以列表形式返回队列中尚未执行的任务。

## 知识关联

**前置概念——线程基础**：理解线程池需要先掌握`Thread`对象的创建、`Runnable`接口、以及`synchronized`/`wait`/`notify`机制。线程池的阻塞队列内部正是通过`ReentrantLock`和`Condition`（`wait`/`notify`的高级封装）实现线程的阻塞与唤醒。

**后续概念——任务系统**：线程池是任务系统的执行引擎。游戏引擎（如Unreal Engine 5的TaskGraph）和服务器框架（如Netty的EventLoop）的任务系统都在线程池之上增加了任务优先级、任务依赖（DAG调度）、任务取消等功能。`CompletableFuture`（Java 8）和`async/await`（C#、Kotlin）的异步编程模型，本质上是将回调函数封装成任务提交到线程池，将多线程的复杂度从显式线程管理转移到运行时框架层。
