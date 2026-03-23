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
quality_tier: "pending-rescore"
quality_score: 39.9
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 0.4
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
---
# 线程基础

## 概述

线程（Thread）是操作系统能够独立调度的最小执行单元，与同一进程内的其他线程共享堆内存、全局变量和文件描述符，但每个线程拥有独立的程序计数器（PC）、寄存器组和栈空间（通常默认 8MB，Linux 下可通过 `ulimit -s` 查看）。从 POSIX 标准（1995 年 POSIX.1c 正式发布）开始，`pthread` 库定义了线程的创建、同步和销毁接口，成为 Unix/Linux 生态的基础线程规范。

线程基础涵盖三项核心操作：**创建（Create）**、**同步（Synchronize）** 和**生命周期管理（Lifecycle Management）**。线程的轻量性体现在切换代价上——进程上下文切换需保存完整的内存映射，而同进程内的线程切换只需保存寄存器状态，耗时通常在微秒级别（约 1–10 μs），远低于进程切换的数十微秒。

理解线程基础的意义在于：几乎所有并发程序的 bug（竞态条件、死锁、数据损坏）都根源于对线程创建时机、栈生命周期或同步时序的误判。在 Java、C++、Python 等主流语言中，线程库的 API 虽有差异，但底层语义完全对应这三项操作。

---

## 核心原理

### 线程创建

POSIX 接口使用 `pthread_create(&tid, attr, start_routine, arg)` 创建线程，其中 `start_routine` 是函数指针，`arg` 是传递给该函数的参数指针。Java 的等价操作是 `new Thread(Runnable r).start()`，C++11 则提供 `std::thread t(func, args...)`。

创建线程时，操作系统会为新线程分配独立的**栈帧**。需要注意参数 `arg` 的生命周期：若在主线程中将局部变量地址传给子线程，而主线程随后退出或修改该变量，子线程读取到的将是无效数据。标准做法是通过堆分配（`malloc`/`new`）传递参数，并由子线程在使用完毕后释放，或使用结构体封装多个参数。

线程创建的开销不可忽视：Linux 下 `clone()` 系统调用（`pthread_create` 的底层实现）平均耗时约 10–50 μs，频繁创建销毁线程会产生显著的 CPU 开销，这正是线程池存在的根本原因。

### 线程生命周期

线程完整的状态机包含以下五个状态：

1. **新建（New）**：线程对象已创建，但 `start()` 尚未调用。
2. **就绪（Runnable）**：已提交给调度器，等待 CPU 时间片。
3. **运行（Running）**：正在 CPU 上执行。
4. **阻塞（Blocked/Waiting）**：等待 I/O、锁、或条件变量，不占用 CPU。
5. **终止（Terminated）**：`start_routine` 返回或调用 `pthread_exit()`/`Thread.interrupt()` 后进入该状态。

线程终止后，其资源（栈、线程描述符）不会立即释放，需要另一线程调用 `pthread_join(tid, &retval)` 回收，这一过程称为"收割"（Reaping）。若不调用 `join`，也可在创建时将线程设置为**分离状态**（`pthread_detach`），系统将在线程终止时自动回收资源。**未被 join 也未 detach 的线程会造成资源泄漏**，类似于未释放的堆内存。

### 线程同步的基础语义

最基础的同步需求是**等待另一线程完成**，即 `join` 操作。`pthread_join` 会使调用线程阻塞，直到目标线程终止并返回其退出值。Java 的 `thread.join()` 语义完全相同，其底层由 `wait/notify` 机制实现，等待线程释放监视器锁并挂起。

线程同步的另一基础机制是**原子性保障**。现代 CPU 不保证对普通变量的读写是原子的——即使是 `int` 类型，在 32 位 ARM 上写入 64 位 `long` 仍可能被拆分为两次 16 位操作，导致其他线程读到中间状态。C++11 引入 `std::atomic<T>` 类型（对应 Java 的 `java.util.concurrent.atomic` 包），通过硬件级的 CAS（Compare-And-Swap）指令保证不可分割的读改写操作，是互斥锁之前的轻量级同步手段。

---

## 实际应用

**Web 服务器的请求处理**：Nginx 的 worker 线程模型中，主线程 `accept()` 新连接后，将连接交由 worker 线程处理，每个 worker 线程执行独立的 HTTP 解析与响应写入，互不干扰。主线程通过 `join` 或信号机制等待 worker 完成，确保在关闭服务器前所有请求得到响应。

**C++11 线程创建示例**：
```cpp
#include <thread>
#include <iostream>

void process(int id) {
    std::cout << "Worker " << id << " running\n";
}

int main() {
    std::thread t1(process, 1);
    std::thread t2(process, 2);
    t1.join();  // 主线程等待 t1 完成
    t2.join();  // 主线程等待 t2 完成
    return 0;
}
```
若省略 `t1.join()` 或 `t1.detach()`，程序在 `main` 返回时调用 `std::thread` 析构函数，会触发 `std::terminate()` 强制终止程序——这是 C++11 对遗忘 join 的强制惩罚。

**Java 线程状态监控**：通过 `Thread.getState()` 可在运行时查询线程所处的生命周期阶段，`jstack` 工具可打印 JVM 内所有线程的完整状态快照，是排查死锁和线程泄漏的首要手段。

---

## 常见误区

**误区一：`thread.start()` 之后线程立即开始执行**。调用 `start()` 只是将线程提交给调度器进入就绪队列，实际执行时间完全由 OS 调度策略决定。编写依赖"先 start 的线程先执行"的代码会产生不可复现的竞态 bug。

**误区二：`pthread_cancel` 可以安全地强制终止线程**。`pthread_cancel` 只是向目标线程发送取消请求，线程仅在到达**取消点**（如 `sleep`、`read`、`write` 等系统调用）时才会响应。若线程处于纯计算循环中且未调用任何取消点函数，`cancel` 完全无效。正确的线程终止设计应使用共享的 `volatile bool stop_flag` 或 `std::atomic<bool>`，由线程自身在每次循环迭代时检查并主动退出。

**误区三：线程栈上的局部变量对所有线程可见**。共享内存指的是堆（Heap）和全局/静态区，每个线程的栈是私有的。将子线程中栈变量的地址传递给主线程并在子线程结束后使用，会造成悬空指针（Dangling Pointer），这类 bug 在 Valgrind 检测中归类为 `Invalid read of size N`。

---

## 知识关联

**前置概念**：多线程概述提供了线程与进程的区别、并发与并行的定义。线程基础的 `join`/`detach` 和生命周期状态机是所有后续并发原语的行为基础。

**后续概念**：
- **互斥锁（Mutex）**：解决多个线程同时访问共享堆变量时的竞态条件，是 `pthread_join` 同步机制的细粒度扩展。
- **条件变量（Condition Variable）**：在互斥锁基础上增加"等待特定条件成立"的能力，需要配合线程的 Blocked/Waiting 状态理解其唤醒语义。
- **线程池**：通过预先创建固定数量的线程并复用，直接解决本节提到的每次 `pthread_create` 耗时 10–50 μs 的开销问题。
- **Future/Promise**：将线程的返回值（`pthread_join` 的 `retval`）抽象为可组合的异步计算句柄，是现代高级并发编程模型的起点。
