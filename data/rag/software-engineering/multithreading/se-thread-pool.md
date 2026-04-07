# 线程池

## 概述

线程池（Thread Pool）是一种预先分配并持久化维护固定数量工作线程的并发编程模式。其本质是将**线程生命周期管理**与**任务执行逻辑**解耦：程序启动时一次性创建 $N$ 个工作线程并令其阻塞在任务队列上，当外部任务到来时从池中调度空闲线程执行，任务完成后线程不销毁而是归还池中继续等待。这种"借还"模型将每次任务的线程创建开销（Linux 上 `pthread_create` 通常耗时 50–100 微秒，Windows 上约 20–50 微秒）压缩为一次性的启动成本。

线程池的概念随 Java 1.5（2004 年）引入 `java.util.concurrent.ThreadPoolExecutor` 而得到广泛规范化。该类由 Doug Lea 主导设计，提供 `corePoolSize`、`maximumPoolSize`、`keepAliveTime`、`workQueue`、`RejectedExecutionHandler` 五大核心参数，成为现代线程池实现的事实参考模板（Lea, 1999；JSR-166 规范）。在此之前，Java 开发者需手工管理线程生命周期，极易因频繁创建销毁线程引发 GC 压力或文件描述符耗尽。

线程池的价值不仅限于减少线程创建开销。更关键的是，通过限制并发线程数上限，线程池防止了"线程爆炸"——当并发请求激增时，若系统为每个请求创建独立线程，数千个线程的上下文切换本身就可消耗 30%–80% 的 CPU 时间（Ousterhout, 1996，"Why Threads Are a Bad Idea"）。合理配置的线程池通过队列缓冲流量峰值，是服务端应用在高负载下保持稳定吞吐量的核心机制。

---

## 核心原理

### 任务队列与工作线程的生产者-消费者模型

线程池内部维护一个**阻塞任务队列**（如 Java 的 `LinkedBlockingQueue` 或 `ArrayBlockingQueue`）和一组**工作线程**。每个工作线程的主循环逻辑如下：

```
while (running) {
    task = queue.take();   // 队列空时挂起，底层依赖条件变量
    task.execute();
}
```

`queue.take()` 在队列为空时令线程挂起，底层使用条件变量（POSIX 的 `pthread_cond_wait` 或 Java 的 `ReentrantLock + Condition.await()`）实现，避免空转轮询浪费 CPU 周期。提交线程调用 `queue.put()` 后触发信号唤醒工作线程，形成经典的**生产者-消费者**解耦。`LinkedBlockingQueue` 使用两把锁（`putLock` 和 `takeLock`）分别保护队列头尾，使生产与消费可以并发进行，吞吐量显著高于单锁设计。

### 线程池大小的量化公式

线程池大小直接决定吞吐量与资源消耗的平衡。Brian Goetz 在《Java Concurrency in Practice》（2006）中给出经典量化公式：

$$N_{\text{threads}} = N_{\text{CPU}} \times U_{\text{CPU}} \times \left(1 + \frac{W}{C}\right)$$

其中：
- $N_{\text{CPU}}$ 为处理器核数（可通过 `Runtime.getRuntime().availableProcessors()` 获取）
- $U_{\text{CPU}}$ 为目标 CPU 利用率，取值 $(0, 1]$
- $W$ 为任务平均等待时间（如等待 I/O、锁、网络响应）
- $C$ 为任务平均计算时间

**纯计算型任务**（$W/C \approx 0$）：最优线程数 $\approx N_{\text{CPU}} + 1$，多出的 1 个线程用于补偿偶发的缺页中断或时钟中断导致的停顿。**I/O 密集型任务**（$W/C$ 可达 10–100）：线程数需大幅扩充，例如数据库连接池场景下 $W/C \approx 50$，则 8 核机器上最优线程数约为 $8 \times 0.9 \times 51 \approx 367$，此时线程数与核数相差悬殊，说明盲目套用"线程数 = CPU 核数"的经验值是错误的。

### 工作窃取算法（Work Stealing）

标准线程池共享单一任务队列，在高并发场景下队列锁成为性能瓶颈。**工作窃取**（Work Stealing）算法由 Burton and Sleep（1981）提出，后由 Robert Blumofe 和 Charles Leiserson 在 Cilk 系统（1994, MIT）中形式化证明其时间最优性（Blumofe & Leiserson, 1999，"Scheduling Multithreaded Computations by Work Stealing"，JACM）。

Java 7 引入的 `ForkJoinPool` 由 Doug Lea 基于此算法实现。其核心设计为：每个工作线程持有一个**双端队列（deque）**，自身产生的子任务压入 deque **头部（top）**，本线程也从头部取任务执行（LIFO 顺序，有利于缓存局部性）；当某线程本地 deque 为空时，随机选取另一线程的 deque 从**尾部（base）**窃取任务（FIFO 顺序）。头尾分离操作使得绝大多数情况下无需加锁，仅在 deque 中只剩最后一个任务时才需要 CAS 竞争，大幅降低了锁竞争开销。

`ForkJoinPool.commonPool()` 在 Java 8 中成为并行流（parallel stream）的默认执行引擎，其并行度默认设为 $N_{\text{CPU}} - 1$（预留 1 个核给主线程）。

### 拒绝策略与饱和处理

当线程池已达 `maximumPoolSize` 且任务队列已满时，新提交的任务触发**拒绝策略**（`RejectedExecutionHandler`）。Java 内置四种策略：
- `AbortPolicy`（默认）：抛出 `RejectedExecutionException`，调用方感知过载
- `CallerRunsPolicy`：由提交者线程直接执行任务，形成天然的背压（back-pressure）机制，减缓提交速率
- `DiscardPolicy`：静默丢弃，适合允许丢失的非关键任务（如统计采样）
- `DiscardOldestPolicy`：丢弃队列最旧的任务，让新任务进入，适合实时性优先场景

`CallerRunsPolicy` 是服务端系统最常用的策略，因为它将过载压力反传给调用方（通常是 HTTP 请求处理线程），自动降低接入速率，避免雪崩。

---

## 关键方法与参数配置

### ThreadPoolExecutor 七参数构造

Java `ThreadPoolExecutor` 完整构造器接受 7 个参数：

```java
ThreadPoolExecutor(
    int corePoolSize,          // 核心线程数，即使空闲也不销毁
    int maximumPoolSize,       // 最大线程数上限
    long keepAliveTime,        // 非核心线程的空闲存活时间
    TimeUnit unit,             // keepAliveTime 的时间单位
    BlockingQueue<Runnable> workQueue,  // 任务缓冲队列
    ThreadFactory threadFactory,        // 线程创建工厂（可命名线程）
    RejectedExecutionHandler handler    // 拒绝策略
)
```

线程池的动态伸缩逻辑为：提交任务时，若当前线程数 $<$ `corePoolSize`，直接新建线程（即使有空闲线程）；若 $\geq$ `corePoolSize` 且队列未满，入队等待；若队列已满且线程数 $<$ `maximumPoolSize`，新建非核心线程；若线程数已达 `maximumPoolSize` 且队列已满，触发拒绝策略。

### 队列类型的选择对吞吐量的影响

| 队列类型 | 容量 | 适用场景 |
|---|---|---|
| `LinkedBlockingQueue` | 默认无界（Integer.MAX_VALUE） | `FixedThreadPool`、`SingleThreadExecutor`，注意 OOM 风险 |
| `ArrayBlockingQueue` | 有界 | 需要精确控制背压的场景 |
| `SynchronousQueue` | 零容量，直接移交 | `CachedThreadPool`，任务必须立即被线程接收 |
| `PriorityBlockingQueue` | 无界优先级队列 | 任务有优先级差异，低优先级任务可能饥饿 |

`Executors.newFixedThreadPool(n)` 使用无界 `LinkedBlockingQueue`，意味着任务可无限堆积。在生产环境中，应始终使用有界队列配合明确的拒绝策略，而非使用 `Executors` 工厂方法的默认配置（阿里巴巴 Java 开发手册明确禁止直接使用 `Executors` 工厂类，正是基于此风险）。

---

## 实际应用

### 案例一：Web 服务器的请求处理线程池

Tomcat 的 `org.apache.tomcat.util.threads.ThreadPoolExecutor`（Tomcat 7+）是对 Java 标准 `ThreadPoolExecutor` 的定制扩展。其关键改动在于：当队列已满时，优先创建新线程（而非立即拒绝），直到达到 `maximumPoolSize`，之后才入队。这与标准 Java 线程池的"先入队再扩容"逻辑相反，更符合 Web 服务"快速响应请求"的特性。Tomcat 默认配置 `minSpareThreads=10`、`maxThreads=200`，在 8 核服务器上处理 I/O 密集的 HTTP 请求时，200 个线程基本符合 $W/C \approx 24$ 的 I/O 密集型公式结果。

### 案例二：ForkJoinPool 的递归任务分解

计算斐波那契数列的第 $n$ 项可用 `RecursiveTask` 利用 `ForkJoinPool` 进行分治：

```java
class FibTask extends RecursiveTask<Long> {
    final int n;
    FibTask(int n) { this.n = n; }
    @Override protected Long compute() {
        if (n <= 1) return (long) n;
        FibTask f1 = new FibTask(n - 1);
        f1.fork();                    // 将 f1 压入当前线程 deque 头部
        return new FibTask(n - 2).compute() + f1.join();  // 先计算 f2，再等待 f1
    }
}
// 使用：new ForkJoinPool().invoke(new FibTask(40));
```

此处 `f1.fork()` 后先执行 `new FibTask(n-2).compute()`（直接递归，留在当前线程），再 `f1.join()` 等待。若此时 f1 尚未被窃取，当前线程可直接从 deque 顶部取回执行（无需同步），避免了不必要的线程切换。

### 案例三：线程池监控与动态调参

阿里巴巴开源的 **动态线程池框架 DynamicTp** 支持在运行时通过配置中心（Nacos/Apollo）动态调整 `corePoolSize` 和 `maximumPoolSize`，无需重启服务。`ThreadPoolExecutor` 的 `setCorePoolSize()` 和 `setMaximumPoolSize()` 方法本身是线程安全的，可在运行时调用。监控指标包括：活跃线程数（`getActiveCount()`）、队列积压深度（`getQueue().size()`）、已完成任务总数（`getCompletedTaskCount()`）、任务拒绝次数（需自定义计数器包装拒绝策略）。

---

## 常见误区

**误区一：线程数越多吞吐量越高。**
实验数据表明，当线程数超过最优值后，吞吐量因上下文切换开销反而下降。Intel Xeon E5-2680 v4（14 核 28 线程）上的 CPU 密集型基准测试显示，线程数从 28 增至 200 时，QPS 下降约 35%，同时 `vmstat` 显示 cs（context switch）指标从每秒 5 万次飙升至 80 万次。

**误区二：`Executors.newCachedThreadPool()` 是"万能"线程池。**
`CachedThreadPool` 的 `maximumPoolSize` 为 `Integer.MAX_VALUE`，使用 `SynchronousQueue` 直接移交。在任务提交速率持续超过线程处理速率时，线程数会无限增长直至 OOM 或系统崩溃。某电商公司曾因在秒杀场景下误用 `CachedThreadPool` 导致服务器在 30 秒内