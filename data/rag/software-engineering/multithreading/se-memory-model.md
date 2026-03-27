---
id: "se-memory-model"
concept: "内存模型"
domain: "software-engineering"
subdomain: "multithreading"
subdomain_name: "多线程"
difficulty: 3
is_milestone: false
tags: ["底层"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 50.2
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.467
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 内存模型

## 概述

内存模型（Memory Model）是编程语言规范中定义的一套规则，规定了多线程程序中各线程如何读写共享内存、以及这些操作的可见性和有序性保证。C++ 在 2011 年发布的 C++11 标准（ISO/IEC 14882:2011）中首次正式引入内存模型，Java 则在 2004 年的 Java 5（JSR-133）中修订了原有缺陷的内存模型。这两个时间节点标志着主流语言开始将多线程语义纳入语言规范本身，而非依赖平台实现。

在没有内存模型规范的情况下，编译器和 CPU 均可对指令进行重排序优化。例如，Intel x86 架构允许 Store-Load 重排序，而 ARM 架构允许更多类型的重排序。内存模型正是为了在允许这些优化的同时，为程序员提供一套可推理的正确性保证，避免数据竞争（Data Race）导致的未定义行为。

## 核心原理

### Happens-Before 关系

Happens-Before 是内存模型的核心语义工具，记作 A hb→ B，表示操作 A 的结果对操作 B 可见。它是一种偏序关系（Partial Order），具有传递性：若 A hb→ B 且 B hb→ C，则 A hb→ C。

Java 内存模型（JMM）中，以下操作会建立 Happens-Before 关系：

- **监视器锁规则**：对同一锁的 `unlock` Happens-Before 后续的 `lock`
- **volatile 变量规则**：对 `volatile` 变量的写 Happens-Before 后续的读
- **线程启动规则**：`Thread.start()` Happens-Before 新线程中的任何操作
- **线程终止规则**：线程中所有操作 Happens-Before `Thread.join()` 返回后的操作

C++11 内存模型中，等价机制通过 `std::atomic` 的内存序（memory_order）参数表达，`memory_order_release` 写入与 `memory_order_acquire` 读取配对时建立 synchronizes-with 关系，进而推导出 Happens-Before。

### C++11 的六种内存序

C++11 定义了六种 `memory_order` 枚举值，覆盖从最严格到最宽松的语义：

| 内存序 | 含义 |
|---|---|
| `memory_order_seq_cst` | 顺序一致性，所有线程看到相同的全局操作顺序 |
| `memory_order_acq_rel` | 兼具 acquire 和 release 语义 |
| `memory_order_release` | 写操作，阻止之前的写操作向后重排 |
| `memory_order_acquire` | 读操作，阻止之后的读操作向前重排 |
| `memory_order_consume` | 弱化的 acquire，仅对数据依赖链有效（实践中几乎不用） |
| `memory_order_relaxed` | 仅保证原子性，不提供任何顺序约束 |

`memory_order_seq_cst` 是默认值，性能最低；`memory_order_relaxed` 性能最高但语义最弱，仅适合计数器累加等不需要同步的场景。

### 数据竞争与未定义行为

C++11 标准明确规定：若两个线程并发访问同一内存位置，且至少有一个是写操作，且两者之间不存在 Happens-Before 关系，则程序存在数据竞争，行为未定义（Undefined Behavior）。这意味着编译器可以合法地假设数据竞争不存在，从而执行可能导致错误结果的优化。

Java 内存模型对数据竞争的处理稍宽松：对于存在数据竞争的程序，JMM 保证每次读操作只会读到某次合法的写操作的值（out-of-thin-air safety），但不保证顺序，因此逻辑正确性仍然无法依赖。

## 实际应用

### 双重检查锁定（DCL）

单例模式中的双重检查锁定是内存模型问题的经典案例。在 Java 5 之前，以下代码是错误的：

```java
// 错误写法（Java 5 之前）
if (instance == null) {
    synchronized (Singleton.class) {
        if (instance == null)
            instance = new Singleton(); // 对象构造可能被重排序！
    }
}
```

`instance = new Singleton()` 在字节码层面分为三步：分配内存、调用构造函数、赋值给 `instance`。后两步可能被重排序，导致另一线程读到未初始化的对象。修复方案是将 `instance` 声明为 `volatile`，利用 volatile 写入的 release 语义禁止重排序。

在 C++11 中，等价修复是将 `instance` 声明为 `std::atomic<Singleton*>`，并在读取时使用 `memory_order_acquire`，在写入时使用 `memory_order_release`。

### Release-Acquire 构建消息传递

```cpp
std::atomic<bool> ready{false};
int data = 0;

// 线程 1（生产者）
data = 42;  // 普通写
ready.store(true, std::memory_order_release);  // release 写

// 线程 2（消费者）
while (!ready.load(std::memory_order_acquire));  // acquire 读
assert(data == 42);  // 保证成立
```

此模式中，release-store 与 acquire-load 建立 synchronizes-with 关系，保证线程 1 对 `data` 的写入对线程 2 可见，`assert` 永远不会触发。

## 常见误区

**误区一：`volatile` 在 Java 和 C++ 中语义相同**
Java 的 `volatile` 提供了完整的 Happens-Before 保证，等同于 `memory_order_seq_cst` 语义，可用于线程同步。而 C++ 的 `volatile` 仅防止编译器将变量值缓存在寄存器中（主要用于内存映射 I/O），不提供任何多线程内存顺序保证。用 C++ `volatile` 替代 `std::atomic` 是严重错误。

**误区二：Happens-Before 意味着操作物理上按顺序执行**
Happens-Before 是可见性保证，不是执行顺序的物理约束。CPU 仍可乱序执行，只要结果对观察线程而言符合 Happens-Before 的语义即可。两者的混淆会导致过度使用 `memory_order_seq_cst` 或不必要的内存屏障（Memory Barrier），损失性能。

**误区三：对 `std::atomic` 的操作一定是无锁的**
`std::atomic<T>` 并不保证无锁实现。对于超过平台原生字长的类型（如 `struct { int a, b, c; }`），`std::atomic` 的实现可能内部使用互斥锁。可通过 `std::atomic<T>::is_lock_free()` 方法或 `ATOMIC_INT_LOCK_FREE` 等宏在编译期或运行期检查。

## 知识关联

内存模型建立在原子操作的基础之上：原子操作（`std::atomic` 或 Java `AtomicInteger` 等）是表达内存序语义的载体，而内存模型规定了这些原子操作之间如何建立 Happens-Before 关系。没有原子操作，就无法精细控制内存序；没有内存模型，原子操作的跨线程可见性语义就无从定义。

理解内存模型是分析无锁数据结构（Lock-Free Data Structures）正确性的必要前提，例如 Michael-Scott 无锁队列的每个 CAS 操作都需要精确的内存序标注才能保证正确性。此外，内存模型知识也直接指导 Java 中 `synchronized`、`volatile`、`java.util.concurrent` 包的正确使用，以及 C++ 中 `std::mutex`、`std::condition_variable` 与 `std::atomic` 协同工作时的语义边界。