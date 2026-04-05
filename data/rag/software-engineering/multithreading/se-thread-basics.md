---
id: "se-thread-basics"
concept: "线程基础"
domain: "software-engineering"
subdomain: "multithreading"
subdomain_name: "多线程"
difficulty: 2
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 线程基础

## 概述

线程（Thread）是操作系统调度的最小执行单元，同一进程内的多个线程共享该进程的堆内存、全局变量和文件描述符，但每个线程拥有独立的栈空间（通常默认 1~8 MB）、程序计数器（PC）和寄存器组。这种"共享但独立"的内存模型是多线程编程既高效又危险的根本原因。

线程概念最早随 1970 年代的 Unix 系统演化而来，POSIX 于 1995 年正式发布 pthreads 标准（POSIX.1c-1995），统一了 C/C++ 环境下的线程 API。Java 在 1.0 版本（1996 年）就将线程支持内置于语言核心，提供 `java.lang.Thread` 类，使线程管理成为开发者的日常工作。

理解线程基础的意义在于：线程创建本身有开销——Linux 上通过 `clone()` 系统调用创建线程约需 10~50 微秒，若在请求热路径上频繁创建/销毁线程，延迟会显著上升。正确管理线程生命周期和同步原语，是后续使用互斥锁、条件变量和线程池的前提。

---

## 核心原理

### 线程的创建方式

在 POSIX C 中，使用 `pthread_create(&tid, &attr, start_routine, arg)` 创建线程，其中 `start_routine` 是线程入口函数，签名为 `void* func(void*)` 。Java 提供两种方式：继承 `Thread` 类并重写 `run()` 方法，或实现 `Runnable` 接口后传入 `new Thread(runnable)` 构造器。推荐使用 `Runnable` 方式，因为 Java 是单继承语言，实现接口不会占用继承槽位。

C++11 起，标准库提供 `std::thread`，语法更简洁：

```cpp
std::thread t([]() { /* 线程体 */ });
t.join(); // 等待线程结束
```

若不调用 `join()` 或 `detach()` 就让 `std::thread` 对象析构，程序会调用 `std::terminate()` 直接崩溃，这是初学者最常见的编译运行陷阱之一。

### 线程的生命周期

线程从创建到消亡经历以下五个状态：

1. **新建（New）**：线程对象已创建，底层系统线程尚未启动。
2. **就绪（Runnable）**：已调用 `start()` 或 `pthread_create()`，等待 CPU 时间片。
3. **运行（Running）**：获得 CPU，正在执行 `run()` / `start_routine`。
4. **阻塞（Blocked/Waiting）**：等待 I/O、锁或条件变量，主动让出 CPU。
5. **终止（Terminated）**：入口函数返回，或调用 `pthread_exit()` / `Thread.interrupt()` 后处理完成。

Java 的 `Thread.getState()` 方法可在运行时返回上述枚举状态，便于监控和调试。线程一旦进入终止状态，不能再次启动——对同一个 Java `Thread` 对象调用两次 `start()` 会抛出 `IllegalThreadStateException`。

### 线程同步的基本手段

多个线程并发读写同一变量时会产生**竞争条件（Race Condition）**。以自增操作 `count++` 为例，它在底层对应"读-改-写"三步，若两个线程在未加保护的情况下同时执行，最终结果可能少计一次。

最基础的同步手段是**原子操作**与**内存可见性保证**。Java 提供 `volatile` 关键字，确保写操作立即刷回主内存，读操作总从主内存加载，但它只保证可见性，不保证复合操作的原子性（`volatile int count; count++` 仍不安全）。若需原子性，应使用 `java.util.concurrent.atomic.AtomicInteger`，其 `incrementAndGet()` 底层依赖 CPU 的 CAS（Compare-And-Swap）指令，在 x86 上对应 `LOCK XADD`，无需操作系统介入即可完成原子自增。

线程间协调还需要**等待/通知机制**。Java 中所有对象都内置一个监视器（Monitor），调用 `object.wait()` 会释放该对象的锁并进入等待队列；另一线程执行 `object.notify()` 或 `object.notifyAll()` 后，等待线程被唤醒并重新竞争锁。`wait()` 必须在 `synchronized` 块内调用，否则抛出 `IllegalMonitorStateException`。

---

## 实际应用

**场景一：后台日志写入线程**  
主线程处理业务逻辑，创建一个守护线程（`thread.setDaemon(true)`）专门将日志异步写入磁盘。守护线程在 Java 中的特殊性在于：JVM 在所有非守护线程结束后会强制终止守护线程，无需显式关闭，适合日志、GC 等辅助任务。

**场景二：生产者-消费者模型的线程协调**  
一个线程生产数据放入缓冲区，另一线程消费。使用 `synchronized + wait/notifyAll` 实现：缓冲区满时生产者调用 `wait()`，消费者取走数据后调用 `notifyAll()` 唤醒生产者。这是条件变量的前身，实际工程中更推荐 `java.util.concurrent.LinkedBlockingQueue`，它内部封装了上述逻辑并处理了虚假唤醒（Spurious Wakeup）问题。

**场景三：`pthread_join` 收集子线程结果**  
在 C 中，主线程通过 `pthread_join(tid, &retval)` 阻塞等待子线程，并通过 `retval` 获取子线程 `return` 的指针值，这是 C 语言层面最原始的线程结果传递机制，等价于 Java `Future` 的无状态前身。

---

## 常见误区

**误区一：`Thread.start()` 和直接调用 `run()` 等价**  
直接调用 `thread.run()` 不会创建新线程，而是在当前线程中同步执行 `run()` 方法体，与普通方法调用无异。只有 `thread.start()` 才会触发 JVM 向操作系统申请新线程并在其中执行 `run()`。

**误区二：`volatile` 可以替代 `synchronized` 保证线程安全**  
`volatile` 仅解决内存可见性问题：写线程的修改能被读线程立即看到，禁止 JIT 编译器和 CPU 对该变量访问进行重排序。但对于"检查后执行（Check-Then-Act）"复合操作，如 `if (singleton == null) singleton = new Obj()`，`volatile` 无法防止两个线程同时通过 `null` 检查，必须配合 `synchronized` 或改用双重检查锁定（Double-Checked Locking）模式。

**误区三：线程越多，并发性能越高**  
线程数量超过 CPU 核心数后，额外的线程不仅不能提升吞吐量，反而会增加上下文切换（Context Switch）的开销。Linux 上一次上下文切换约需 1~10 微秒，高并发场景下这一损耗会累积成毫秒级延迟。线程池（ThreadPoolExecutor）通过复用固定数量的线程来规避这一问题。

---

## 知识关联

**前置概念**：多线程概述建立了"进程 vs 线程"的内存模型认知，使本文的"共享堆、独立栈"描述有了对照基础。

**直接后续**：掌握竞争条件和 `wait/notify` 机制后，自然引出**互斥锁**（Mutex/synchronized）和**条件变量**（Condition）的需求——互斥锁解决"同时只能一个线程进入临界区"，条件变量解决"线程在特定条件满足前高效等待"，两者是对 `synchronized + wait/notify` 的解耦和泛化。

**并行后续**：反复创建销毁线程的性能问题，直接驱动了**线程池**的设计；而需要从线程中取回计算结果、或对异步任务设置超时，则引出了 **Future/Promise** 模型，它们都依赖本文所述的线程生命周期管理和同步原语作为底层实现。