---
id: "se-atomic"
concept: "原子操作"
domain: "software-engineering"
subdomain: "multithreading"
subdomain_name: "多线程"
difficulty: 3
is_milestone: false
tags: ["底层"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.448
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 原子操作

## 概述

原子操作（Atomic Operation）是指在执行过程中不可被中断的操作序列——对于多线程环境中的其他线程而言，该操作要么完全执行完毕，要么完全未执行，不存在中间状态。"原子"一词源自希腊语"atomos"（不可分割），在硬件层面，现代 CPU 通过 `LOCK` 前缀指令（x86架构）或 Load-Linked/Store-Conditional（LL/SC，ARM/RISC-V架构）来保障这种不可分割性。

原子操作的概念在20世纪60年代随多处理器系统的出现而被正式提出。1968年，Dijkstra 在信号量论文中已隐含了原子性要求，但直到 Intel 486 处理器（1989年）将 `CMPXCHG` 指令引入主流 ISA，硬件级 CAS 才得以普及。C++11 标准在2011年将 `std::atomic<T>` 纳入标准库，使原子操作在语言层面得到统一规范。

与互斥锁相比，原子操作的核心价值在于**零内核态切换**：`std::atomic<int>` 的自增操作在 x86 上仅编译为一条 `LOCK ADD` 指令，延迟约 20-40 纳秒；而 `pthread_mutex_lock` 在无竞争时也需要约 25 纳秒，在高竞争时可达数微秒。对于计数器、标志位、指针交换等简单场景，原子操作性能优势显著。

---

## 核心原理

### Compare-And-Swap（CAS）机制

CAS 是原子操作的核心操作原语，其语义可用以下伪代码表达：

```
bool CAS(T* addr, T expected, T desired):
    if (*addr == expected):
        *addr = desired
        return true
    else:
        return false
```

整个"比较+赋值"过程在硬件层面是原子的。x86 对应的汇编指令为 `LOCK CMPXCHG`，ARM 则使用 `LDXR`/`STXR` 指令对。Java 的 `AtomicInteger.compareAndSet(expected, update)` 和 C++ 的 `std::atomic<T>::compare_exchange_strong()` 均基于此原语实现。CAS 失败时调用方需重试（称为 CAS Loop），这是构建无锁数据结构的基础模式。

### ABA 问题

CAS 存在一个特有缺陷：若内存地址中的值从 A 变为 B 再变回 A，CAS 无法感知这次"中途变化"，会错误地认为值从未改变。典型场景是无锁栈：线程1读取栈顶指针后被挂起，线程2弹出并重新压入同一个节点，线程1恢复后 CAS 成功但链表结构已被破坏。解决方案是使用**带版本号的 CAS**：Java 的 `AtomicStampedReference<V>` 将引用与整型 stamp 打包为128位值，每次修改递增 stamp，使相同指针值但不同历史的情况可被区分。

### 内存序（Memory Order）

原子操作不仅保障操作本身的原子性，还通过内存序约束编译器和 CPU 的指令重排行为。C++11 定义了六种内存序，常用的三种如下：

| 内存序 | 枚举值 | 特性 |
|---|---|---|
| 宽松序 | `memory_order_relaxed` | 只保障原子性，不限制重排 |
| 获取-释放序 | `memory_order_acquire` / `memory_order_release` | 构成 happens-before 关系 |
| 顺序一致序 | `memory_order_seq_cst` | 全局顺序，最强，也最慢 |

`acquire` 对应读操作：该原子读之后的所有内存操作不可重排到其前面。`release` 对应写操作：该原子写之前的所有内存操作不可重排到其后面。两者配对使用，可在无锁场景下建立精确的同步关系，比 `seq_cst` 减少约15-30%的总线流量（在多核 ARM 系统上效果尤为明显）。

### `std::atomic<T>` 的类型限制

C++ 的 `std::atomic<T>` 要求 T 必须是 **TriviallyCopyable** 类型。对于大于平台原生字长（通常为64位）的类型，`is_lock_free()` 可能返回 `false`，此时标准库会退化为内部使用互斥锁实现，原子操作的性能优势随之消失。可通过 `std::atomic<T>::is_always_lock_free`（C++17静态常量）在编译期检测。

---

## 实际应用

**引用计数**：`std::shared_ptr` 的控制块使用 `std::atomic<int>` 存储强引用计数，`use_count` 的加减操作均为原子操作。在多线程环境中，不同线程可以安全地持有和释放同一 `shared_ptr` 的副本，计数归零时恰好触发一次析构。

**无锁计数器**：高并发 Web 服务器统计请求数量时，使用 `std::atomic<uint64_t> request_count` 配合 `fetch_add(1, memory_order_relaxed)` 即可，`relaxed` 序足够（仅需原子性，无需与其他内存操作同步），在32核机器上比 `mutex` 保护的计数器吞吐量高约5倍。

**双重检查锁定（DCLP）的正确实现**：单例模式中，错误的 DCLP 在 C++03 时代因指令重排会导致返回未完全初始化的对象。C++11 后，将单例指针声明为 `std::atomic<Singleton*>`，并在写入时使用 `memory_order_release`、读取时使用 `memory_order_acquire`，可正确实现无锁单例而无需 `seq_cst` 的额外开销。

---

## 常见误区

**误区一：原子操作=线程安全的复合操作**。`atomic<int>` 的 `++i` 是原子的，但 `if (i > 0) i--` 不是。读取和判断是两个独立的原子操作，中间可能被其他线程插入，整个条件自减序列仍需 CAS Loop 或互斥锁保护。

**误区二：默认使用 `memory_order_seq_cst` 总是最安全的**。`seq_cst` 在 x86 上代价较小（本身是强内存模型），但在 ARM、PowerPC 等弱内存模型架构上需要插入完整的内存屏障指令（如 ARM 的 `DMB ISH`），在高频原子操作路径上会造成显著的性能回归。应按需选择最弱的满足语义要求的内存序。

**误区三：原子操作能替代所有互斥锁**。CAS Loop 在高竞争下会导致**活锁**（livelock）——多个线程反复尝试 CAS 但持续失败，CPU 利用率高但有效进展为零。互斥锁的阻塞语义反而能在高竞争场景下保证公平调度。原子操作最适合竞争极低或单写多读的场景。

---

## 知识关联

**前置概念——互斥锁**：互斥锁通过操作系统的阻塞机制保障互斥访问，是理解原子操作的参照系。原子操作可视为"硬件层面的极简互斥"，其 `acquire`/`release` 语义与互斥锁的加锁/解锁在 happens-before 关系上等价，但省去了线程调度开销。理解互斥锁的临界区概念，有助于判断哪些场景可以将粗粒度的锁操作替换为细粒度的原子操作。

**后续概念——无锁编程**：无锁数据结构（无锁队列、无锁哈希表等）完全基于原子操作的 CAS Loop 构建。Michael-Scott 无锁队列算法（1996年）是其经典范例，其入队和出队操作均由若干 CAS 原语组合而成，需要深入掌握 ABA 问题的规避手段。

**后续概念——内存模型**：C++11 内存模型（基于 Herb Sutter 和 Hans Boehm 的工作）形式化地定义了多线程程序中所有可能的合法执行序列，原子操作的六种内存序是这一模型的直接实现接口。理解内存模型能够精确推断两个线程间的 happens-before 关系，是编写正确无锁代码的理论基础。
