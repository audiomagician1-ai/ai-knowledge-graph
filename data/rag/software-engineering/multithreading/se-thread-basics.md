# 线程基础

## 概述

线程（Thread）是操作系统调度的最小执行单元，与进程（Process）的根本区别在于资源共享粒度：同一进程内的所有线程共享堆内存、全局变量、文件描述符表和信号处理程序，但每个线程维护独立的栈空间（Linux 默认 8 MB，可通过 `ulimit -s` 调整）、程序计数器（PC）、寄存器组和线程局部存储（TLS）。这种"共享地址空间、独立执行流"的设计，使线程间通信代价远低于进程间通信（无需 IPC 机制），但也引入了竞态条件（Race Condition）和死锁等并发缺陷。

线程概念的形式化始于 1960 年代 IBM OS/360 的多任务设计，POSIX 工作组于 1995 年正式发布 POSIX.1c-1995 标准（即 pthreads），统一了 Unix/Linux 环境下线程的创建、同步与销毁 API（Butenhof, 1997）。Java 在 1996 年随 JDK 1.0 将 `java.lang.Thread` 内置于核心语言，成为首批将线程支持作为一等公民的主流语言之一（Lea, 1999）。C++ 直到 2011 年的 C++11 标准才通过 `<thread>` 头文件引入标准线程库，结束了长达数十年依赖平台特定 API 的局面。

理解线程基础的实际意义不仅是"会写多线程代码"：在 Linux 上通过 `clone()` 系统调用创建一个线程约需 10～50 微秒的内核态开销，若在每次 HTTP 请求处理时都新建线程，百万级 QPS 下光是线程创建就会消耗数十秒的 CPU 时间。这也是线程池（Thread Pool）存在的工程动因——复用已有线程，将创建开销摊薄到整个服务生命周期中。

---

## 核心原理

### 线程的内存模型与栈布局

每个线程在进程虚拟地址空间中拥有独立的栈区域。以 64 位 Linux 为例，线程栈默认大小为 8 MB，调用深度超限时触发栈溢出（Stack Overflow），表现为 `SIGSEGV` 信号。线程的栈变量（局部变量）天然是线程私有的，无需同步；而堆上分配的对象、全局变量和静态变量则被所有线程共享，是竞态条件的来源。

Java 内存模型（Java Memory Model, JMM）由 JSR-133 在 Java 5（2004 年）正式规范化，定义了"主内存（Main Memory）"与"工作内存（Working Memory）"的抽象：每个线程有自己的工作内存缓存主内存变量的副本。在没有同步的情况下，线程对变量的修改可能永远不可见于其他线程——这正是 `volatile` 关键字的语义所在：声明为 `volatile` 的变量，每次读写都直接操作主内存，禁止编译器和 CPU 对其进行指令重排序。

线程局部存储（Thread-Local Storage, TLS）是另一个关键概念：在 C 中使用 `__thread` 关键字，在 Java 中使用 `ThreadLocal<T>` 类，可以为每个线程维护变量的独立副本，彻底避免共享。例如，Java Web 框架中常用 `ThreadLocal<HttpSession>` 将请求上下文绑定到处理线程，无需通过方法参数层层传递。

### 线程的生命周期状态机

线程从创建到消亡严格经历以下五个状态，状态转换不可逆（终止后无法重启）：

1. **新建（New）**：线程对象已在堆上分配（Java `new Thread()`），底层操作系统线程尚未创建，不占用任何 CPU 或内核资源。
2. **就绪（Runnable）**：调用 `start()`（Java）或 `pthread_create()`（C），内核线程已创建并加入调度队列，等待 CPU 时间片分配。
3. **运行（Running）**：线程被 CPU 调度，正在执行 `run()` 方法体或 `start_routine` 函数体。在多核系统上，多个线程可真正并行执行（Parallelism），区别于单核上的并发（Concurrency）。
4. **阻塞（Blocked/Waiting/Timed\_Waiting）**：线程主动或被动让出 CPU。Java 进一步细分三种阻塞子状态：等待获取 `synchronized` 锁（BLOCKED）、调用 `Object.wait()` 无超时等待（WAITING）、调用 `Thread.sleep(ms)` 带超时等待（TIMED\_WAITING）。
5. **终止（Terminated）**：`run()` 方法正常返回，或因未捕获异常退出。调用 `Thread.interrupt()` 不会强制终止线程，仅设置中断标志位，线程需主动检测 `Thread.currentThread().isInterrupted()` 或响应 `InterruptedException` 才会停止。

Java 的 `Thread.getState()` 返回 `Thread.State` 枚举，可在运行时监控线程状态，是排查线程泄漏和死锁的基础工具。对同一个 Java `Thread` 对象调用两次 `start()` 必然抛出 `IllegalThreadStateException`——这一行为是规范强制的，与是否已终止无关。

### 线程调度模型

操作系统以两种模型管理线程：

- **内核级线程（KLT, Kernel-Level Thread）**：每个用户态线程对应一个内核调度实体，Linux 的 POSIX 线程即采用此模型，通过 `clone(CLONE_VM | CLONE_FS | CLONE_FILES | ...)` 创建，可真正利用多核并行，但线程切换需经历用户态→内核态→用户态的模式切换，成本约 1～10 微秒。
- **用户级线程（ULT, User-Level Thread）**：由用户态运行时（如 Go runtime 的 Goroutine、Python 的 gevent）自行调度，切换无需陷入内核，成本约 100 纳秒，但单个 ULT 阻塞会导致整个内核线程阻塞。

Java 的 `java.lang.Thread` 历史上是对内核线程的 1:1 映射；JDK 21（2023 年）引入的虚拟线程（Virtual Thread）则实现了 M:N 调度模型，允许数百万个虚拟线程复用少量平台线程，使 `Thread.sleep()` 等阻塞操作不再占用平台线程。

---

## 关键方法与公式

### POSIX 线程核心 API

```c
// 创建线程
int pthread_create(pthread_t *tid, const pthread_attr_t *attr,
                   void *(*start_routine)(void *), void *arg);

// 等待线程结束（阻塞调用者直到 tid 对应线程终止）
int pthread_join(pthread_t tid, void **retval);

// 分离线程（线程结束后自动回收资源，不可再 join）
int pthread_detach(pthread_t tid);

// 线程主动退出
void pthread_exit(void *retval);
```

`pthread_join()` 的语义类似于进程的 `waitpid()`——若不对非分离线程调用 `join`，线程终止后其资源（内核线程描述符等）无法被回收，形成"僵尸线程"，长期运行的服务器进程会因此耗尽 `/proc/sys/kernel/threads-max` 限制的线程数配额。

### Java 线程的中断协议

Java 没有提供安全的线程强制终止 API（`Thread.stop()` 在 JDK 1.2 后标记为废弃，因为它会在任意点释放锁导致数据不一致）。标准的停止模式依赖中断标志：

```java
// 线程体内的典型中断响应写法
while (!Thread.currentThread().isInterrupted()) {
    try {
        doWork();
        Thread.sleep(1000); // sleep 响应中断会抛出 InterruptedException
    } catch (InterruptedException e) {
        Thread.currentThread().interrupt(); // 恢复中断标志
        break; // 或 return
    }
}
```

注意：`InterruptedException` 被捕获后，JVM 会**自动清除**中断标志位。若在 `catch` 块中不调用 `Thread.currentThread().interrupt()` 重新设置标志，上层调用栈将无从感知中断请求，造成"中断吞咽"（Interrupt Swallowing）缺陷。

### Amdahl 定律与线程并行加速比

引入多线程的根本动机是加速。Amdahl 定律（Gene Amdahl, 1967）给出了并行化的理论加速上限：

$$S(n) = \frac{1}{(1 - p) + \frac{p}{n}}$$

其中 $S(n)$ 为使用 $n$ 个线程时的加速比，$p$ 为程序中可并行化的比例（$0 \leq p \leq 1$）。

例如，若某任务 80% 可并行（$p = 0.8$），使用 8 个线程时理论加速比为：

$$S(8) = \frac{1}{(1 - 0.8) + \frac{0.8}{8}} = \frac{1}{0.2 + 0.1} = \frac{1}{0.3} \approx 3.33$$

这意味着即使 CPU 资源翻 8 倍，实际只能加速约 3.3 倍。Amdahl 定律揭示了盲目增加线程数的边际效益递减规律——当串行部分占比 5% 时，无论使用多少线程，加速比上限为 20 倍。

---

## 实际应用

### Java 线程的三种创建范式对比

**范式一：继承 Thread 类**

```java
class MyThread extends Thread {
    @Override
    public void run() {
        System.out.println("Running in: " + getName());
    }
}
new MyThread().start();
```

缺点：Java 单继承限制导致 `MyThread` 无法再继承其他类；线程逻辑与线程管理耦合。

**范式二：实现 Runnable 接口**

```java
Runnable task = () -> System.out.println("Task executed");
new Thread(task).start();
```

推荐用于简单场景，将任务逻辑（Runnable）与线程载体（Thread）解耦。

**范式三：使用 ExecutorService（工业级推荐）**

```java
ExecutorService pool = Executors.newFixedThreadPool(4);
Future<Integer> future = pool.submit(() -> {
    return computeExpensiveResult();
});
int result = future.get(); // 阻塞直到结果就绪
pool.shutdown();
```

`ExecutorService` 内部维护线程池，避免频繁创建/销毁线程的开销，并通过 `Future` 机制支持异步结果获取。《Java 并发编程实践》（Goetz et al., 2006）明确建议：生产代码中应始终通过 `Executor` 框架管理线程，而非直接 `new Thread()`。

### 案例：使用线程并行计算数组求和

将一个包含 10⁸ 个元素的 `int[]` 数组拆分为 4 段，分配给 4 个线程分别求和，再汇总：

```java
int[] data = new int[100_000_000]; // 填充数据
int nThreads = 4;
int chunkSize = data.length / nThreads;
long[] partialSums = new long[nThreads];
Thread[] threads = new Thread[nThreads];

for (int i = 0; i < nThreads; i++) {
    final int id = i;
    threads[i] = new Thread(() -> {
        long sum = 0;
        int start = id * chunkSize;
        int end = (id == nThreads - 1) ? data.length : start + chunkSize;
        for (int j = start; j < end; j++) sum += data[j];
        partialSums[id] = sum; // 每个线程写不同下标，无竞态
    });
    threads[i].start();
}
for (Thread t : threads) t.join(); // 等待所有线程完成
long total = Arrays.stream(partialSums).sum();
```

此案例中每个线程写 `partialSums` 数组的不同下标，不存在共享写竞态，是"无锁并行"（Embarrassingly Parallel）的典型形式。在 4 核机器上实测加速比约为 3.5～3.8 倍（受内存带宽瓶颈影响，低于 4 倍理论值）。

---

## 常见误区

### 误区一：`Thread.sleep()` 释放持有的锁

`Thread.sleep(ms)` 仅使当前线程暂停执行，**不会释放任何已持有的 `synchronized` 锁或 `ReentrantLock`**。若持锁线程在 `sleep`，其他等待该锁的线程将全部阻塞，造成系统吞吐量下降。需