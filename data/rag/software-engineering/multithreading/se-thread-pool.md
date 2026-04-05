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
quality_tier: "A"
quality_score: 76.3
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

# 线程池

## 概述

线程池（Thread Pool）是一种预先创建并维护固定数量线程的并发编程模式。程序启动时，线程池一次性创建 N 个工作线程并使其进入等待状态，当任务到来时从池中取出空闲线程执行，任务完成后线程不销毁而是归还池中继续等待下一个任务。这种"借还"机制避免了每次任务都经历线程创建（通常耗时 1–100 微秒）和销毁的开销。

线程池的概念随 Java 1.5（2004年）引入 `java.util.concurrent.ThreadPoolExecutor` 而得到广泛规范化。该类提供了 `corePoolSize`、`maximumPoolSize`、`keepAliveTime` 等可调参数，成为现代线程池实现的参考模板。在此之前，开发者需要手工管理线程生命周期，极易因频繁创建销毁线程导致 GC 压力或资源耗尽。

线程池的意义不仅限于性能优化。通过限制并发线程数上限，线程池防止了"线程爆炸"——即任务激增时系统试图创建数千个线程，导致上下文切换开销超过实际计算量。合理配置的线程池是服务端应用稳定性的重要保障。

## 核心原理

### 任务队列与线程复用

线程池内部维护一个**任务队列**（通常是阻塞队列，如 `LinkedBlockingQueue`）和一组**工作线程**。每个工作线程的主循环如下：

```
while (running) {
    task = queue.take();   // 阻塞直到有任务（依赖条件变量实现）
    task.execute();
}
```

`queue.take()` 在队列为空时使线程挂起，底层正是利用条件变量（`pthread_cond_wait` 或 Java 的 `Condition.await()`）实现等待，从而避免了空转轮询浪费 CPU。任务提交方调用 `queue.put()` 后发出信号唤醒工作线程，实现生产者-消费者解耦。

### 池大小策略

线程池大小直接影响吞吐量。经典公式为：

**N_threads = N_CPU × U_CPU × (1 + W/C)**

其中 `N_CPU` 是处理器核数，`U_CPU` 是目标 CPU 利用率（0~1），`W` 是任务等待时间，`C` 是任务计算时间。对于纯计算型任务（W/C ≈ 0），最优线程数约等于 CPU 核数；对于 I/O 密集型任务（W/C 可达 10~100），线程数需要相应扩大以填满 CPU 空闲时间。Java 中 `Executors.newCachedThreadPool()` 采用无上限策略，适合短时 I/O 任务；`Executors.newFixedThreadPool(n)` 则固定线程数，适合 CPU 密集场景。

### 工作窃取（Work Stealing）

标准线程池使用单一共享队列，在高竞争场景下队列锁成为瓶颈。**工作窃取**算法（由 Doug Lea 为 Java `ForkJoinPool` 设计，Java 7 引入）为每个工作线程分配独立的**双端队列（deque）**。线程优先从自己 deque 的头部取任务执行；当本地 deque 为空时，随机选取其他线程的 deque 从**尾部**窃取任务。头尾分离操作大幅减少了线程间的锁竞争。`ForkJoinPool` 中的 `fork()` 将子任务压入本地 deque 头部，`join()` 等待子任务完成，递归分治任务因此能高效并行化。

### 拒绝策略

当任务队列已满且线程数达到 `maximumPoolSize` 时，线程池触发**拒绝策略**。Java `ThreadPoolExecutor` 提供四种内置策略：`AbortPolicy`（抛出异常，默认）、`CallerRunsPolicy`（由提交线程自己执行，起到限流作用）、`DiscardPolicy`（静默丢弃）、`DiscardOldestPolicy`（丢弃最旧任务）。生产系统中常选 `CallerRunsPolicy`，因为它能自动降低任务提交速率而不丢失任务。

## 实际应用

**Web 服务器请求处理**：Tomcat 默认配置 `minSpareThreads=10`、`maxThreads=200`，每个 HTTP 请求由线程池中的一个线程处理。当并发请求超过 200 时触发排队或拒绝，保护 JVM 不因线程过多崩溃。

**图像批处理**：将 1000 张图片的压缩任务分割为 1000 个 Runnable，提交给 `FixedThreadPool(8)`（8 核机器）。所有任务进入队列，8 个线程循环取任务执行，全部完成后关闭池。与串行处理相比，耗时约降低为原来的 1/7（考虑 I/O 和调度开销）。

**ForkJoin 递归归并排序**：将数组递归二分，每次 `fork()` 产生子任务，通过工作窃取在多核间自动负载均衡。对于长度 10^7 的数组，`ForkJoinPool` 通常比串行归并排序快 3~5 倍（4 核环境）。

## 常见误区

**误区一：线程池越大越快**。线程数超过 CPU 核数后，计算密集型任务的吞吐量不再提升，反而因上下文切换增加延迟。在 4 核机器上将计算密集型线程池从 4 扩大到 64，实测延迟可能上升 20%~50%。线程数应基于任务类型和上述公式计算，而非随意设大。

**误区二：`shutdown()` 会立即终止所有任务**。`shutdown()` 只是停止接受新任务，已在队列中的任务仍会执行完毕；要立即停止须调用 `shutdownNow()`，它会向工作线程发送中断信号，但不能保证正在执行的任务响应中断。混淆二者会导致优雅关闭失败或任务丢失。

**误区三：线程池能处理任意多任务而不阻塞调用者**。使用有界队列（如容量 100 的 `ArrayBlockingQueue`）时，`execute()` 在队列满且线程数达上限后会阻塞或触发拒绝策略。使用无界队列虽不阻塞调用者，但任务堆积可导致内存溢出（OOM）。生产环境必须为队列设置合理上界并配合监控报警。

## 知识关联

**前置概念**：理解线程池的阻塞队列实现必须掌握**条件变量**——`take()` 和 `put()` 的等待/通知机制正是条件变量的直接应用。**线程基础**中的线程生命周期（NEW → RUNNABLE → WAITING → TERMINATED）解释了工作线程在 `take()` 阻塞时处于 WAITING 状态，而非占用 CPU。

**后续概念**：**Future/Promise** 建立在线程池之上——`ExecutorService.submit(Callable)` 返回 `Future<T>`，允许调用者异步获取任务结果或取消任务，是线程池从"执行并遗忘"升级到"结果追踪"的关键抽象。**任务系统**（Task System）则进一步封装线程池，加入优先级调度、任务依赖图、超时控制等能力，常见于游戏引擎（如 Naughty Dog 的 Fiber-based Job System）和流处理框架。