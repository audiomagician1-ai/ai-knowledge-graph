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
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
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

内存模型（Memory Model）是编程语言规范中明确定义多线程程序如何读写共享内存的规则集合。它回答了一个关键问题：当线程A写入某变量后，线程B在何种条件下能"看到"这次写入？C++11标准在`<atomic>`头文件和`std::memory_order`枚举中首次将内存模型纳入语言规范，Java则更早在2004年的JSR-133（Java内存模型规范）中重新定义了JMM（Java Memory Model），修复了Java 1.4及之前版本中`double`和`long`类型非原子读写的问题。

在没有内存模型之前，程序员只能依赖特定CPU架构的行为编写多线程代码。x86架构提供了相对强的内存一致性（Total Store Order），而ARM和PowerPC则是弱内存模型，允许更多指令重排。内存模型的价值在于提供了跨平台的统一抽象：只要代码符合语言内存模型的规则，编译器和CPU可以自由优化，但最终可见的结果必须符合规范保证。

## 核心原理

### Happens-Before 关系

Happens-Before（先行发生）是内存模型的核心语义，写作 **A hb→ B**，表示操作A的所有内存效果在B执行时均可见。注意这不等于时间上A在B之前执行——它是逻辑可见性保证，而非物理时序约束。在Java内存模型中，以下操作自动建立Happens-Before：

- 同一线程内，程序顺序（Program Order）构成 hb→
- `monitor.unlock()` hb→ 对同一`monitor`的`lock()`
- 对`volatile`变量的写 hb→ 后续对该变量的读
- `Thread.start()` hb→ 被启动线程的所有操作
- 线程所有操作 hb→ 其他线程对该线程调用`Thread.join()`返回后的操作

如果两个操作之间不存在 Happens-Before 链，它们就是**数据竞争（Data Race）**，程序行为未定义（C++）或结果不确定（Java）。

### C++ 的六种内存序

C++11 定义了 `std::memory_order` 的六个枚举值，控制原子操作的排序强度：

| 枚举值 | 含义 |
|---|---|
| `memory_order_relaxed` | 无同步，只保证本操作原子性 |
| `memory_order_consume` | 依赖链上的数据依赖序（实践中通常被提升为acquire） |
| `memory_order_acquire` | 读屏障：本操作之后的读写不得重排到本操作之前 |
| `memory_order_release` | 写屏障：本操作之前的读写不得重排到本操作之后 |
| `memory_order_acq_rel` | acquire + release 的组合（用于读-改-写操作） |
| `memory_order_seq_cst` | 顺序一致性，最强，所有线程看到相同的全局操作顺序 |

典型的发布-订阅模式使用 release/acquire 配对：
```cpp
// 线程A（生产者）
data.store(42, std::memory_order_relaxed);
flag.store(true, std::memory_order_release); // 释放屏障

// 线程B（消费者）
while (!flag.load(std::memory_order_acquire)); // 获取屏障
assert(data.load(std::memory_order_relaxed) == 42); // 保证可见
```
当线程B的`acquire`读到线程A的`release`写入值时，A的release之前所有写操作对B的acquire之后均可见，构成同步关系（synchronizes-with），进而推导出 Happens-Before。

### Java volatile 与 synchronized 的内存语义

Java的`volatile`不仅防止指令重排，还禁止编译器将变量缓存在寄存器中。JMM规定：对`volatile`变量的写会将线程工作内存中所有变量刷新到主内存，对`volatile`变量的读会使线程工作内存中所有变量失效并重新从主内存加载。这意味着`volatile`写/读承担了完整的内存屏障语义，其成本高于C++的`memory_order_release`/`memory_order_acquire`配对，相当于C++的`memory_order_seq_cst`。

`synchronized`块除了提供互斥，还保证：进入`synchronized`时相当于全局`acquire`，退出时相当于全局`release`。因此受同一锁保护的代码块之间天然存在 Happens-Before 链。

## 实际应用

**双重检查锁定（Double-Checked Locking）的正确实现**是内存模型最经典的应用场景。在Java中，单例模式的懒加载若不用`volatile`，会因为对象初始化与引用赋值的指令重排导致另一线程获得半初始化的对象：

```java
// 错误版本：instance赋值可能在构造函数完成前被其他线程观察到
private static Singleton instance;

// 正确版本：volatile 阻止重排
private static volatile Singleton instance;
```

在C++中，`std::call_once`配合`std::once_flag`是实现线程安全初始化的标准方法，其内部实现依赖`memory_order_seq_cst`保证所有线程在初始化完成后看到一致状态。

**无锁队列**的实现需要精细的内存序控制：入队操作的节点写入使用`release`，出队操作的节点读取使用`acquire`，而队列头尾指针的更新使用`acq_rel`，通过最小化内存屏障代价来最大化吞吐量。

## 常见误区

**误区一：volatile 在 C++ 中等同于原子操作**。C++的`volatile`仅阻止编译器优化掉对该变量的访问（主要用于内存映射I/O），不提供任何线程间同步保证，没有内存屏障语义。Java的`volatile`则完全不同，具有完整的 Happens-Before 语义。混淆这两个语言中`volatile`的含义是跨语言开发者的高频错误。

**误区二：顺序一致性（seq_cst）能消除所有数据竞争**。`memory_order_seq_cst`保证存在一个所有线程都同意的全局操作顺序，但它只适用于被标记为`seq_cst`的原子操作本身。非原子的普通内存访问仍然存在数据竞争，`seq_cst`的原子操作无法保护周围的非原子读写。

**误区三：Happens-Before 意味着操作在时间上先发生**。HB是逻辑可见性关系，编译器和CPU可以乱序执行，只要最终对外暴露的可见性结果符合HB约束即可。两个操作在时间上的先后与HB关系完全无关；判断是否存在数据竞争要看HB链，而不是看运行时的时序日志。

## 知识关联

内存模型建立在**原子操作**的语义之上：原子操作保证单次读或写不被撕裂（tearing），而内存模型在此基础上进一步规定多次原子操作之间的可见性顺序。没有原子操作的底层保证，内存模型中release/acquire的同步关系无从建立。

理解内存模型后，可以进一步学习**无锁数据结构**（lock-free data structures）——它们的正确性证明完全依赖 Happens-Before 推导链，每一处`memory_order`的选择都需要严格对应到算法需要保证的可见性约束。内存模型也是理解**顺序一致性（Linearizability）**这一并发正确性形式化定义的必要前提，后者用于证明并发数据结构在语义上等价于某种串行执行。