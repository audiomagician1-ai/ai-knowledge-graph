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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 原子操作

## 概述

原子操作（Atomic Operation）是指在多线程环境中，不可被中断或分割的最小执行单元。一个原子操作要么完整执行，要么完全不执行，中间状态对其他线程不可见。这一特性在硬件层面由 CPU 指令保证，例如 x86 架构上的 `LOCK CMPXCHG`（带锁前缀的比较并交换）指令，执行期间会锁定总线或缓存行，阻止其他处理器访问同一内存地址。

原子操作的概念随着多核处理器的普及而进入主流软件工程视野。2011 年发布的 C++11 标准将 `std::atomic<T>` 纳入标准库，同年 Java 的 `java.util.concurrent.atomic` 包也已广泛使用，标志着原子操作从底层汇编技巧演变为高级语言的一等公民。

相较于互斥锁，原子操作的开销通常低 2～10 倍。互斥锁需要系统调用进入内核态，而原子操作仅需数条 CPU 指令即可完成，因此在计数器、标志位、引用计数等高频场景中，原子操作能显著减少线程同步的性能损耗。

---

## 核心原理

### 比较并交换（CAS）

CAS（Compare-And-Swap）是原子操作的基础算法原语，其语义可用以下伪代码表达：

```
bool CAS(T* addr, T expected, T desired) {
    if (*addr == expected) {
        *addr = desired;
        return true;
    }
    return false;
}
```

整个读-比较-写序列在硬件层面不可分割。C++11 对应的接口是 `compare_exchange_strong(expected, desired)` 和 `compare_exchange_weak(expected, desired)`。`weak` 版本允许在某些平台（如 ARM 的 LL/SC 指令对）上发生"虚假失败"（spurious failure），但在循环重试场景中性能更高。CAS 的核心挑战是 **ABA 问题**：地址内容从 A 变为 B 再变回 A，CAS 无法察觉中间状态，解决方案是引入版本号（如 Java 的 `AtomicStampedReference`）。

### Atomic 类型与基本操作

C++ 的 `std::atomic<T>` 支持的基本原子操作包括：`load()`、`store()`、`exchange()`、`fetch_add()`、`fetch_sub()` 等。对于整数类型，`fetch_add(1)` 等价于原子自增，其底层在 x86 上编译为 `LOCK XADD` 指令。需要注意，`std::atomic<T>` 中的 `T` 若为复合结构体且大小超过 CPU 原生支持的字长（通常为 8 字节），则操作可能退化为加锁实现，可通过 `is_lock_free()` 方法查询。Java 中 `AtomicInteger.incrementAndGet()` 的内部实现同样依赖 `Unsafe.compareAndSwapInt()` 的 CAS 循环。

### 内存序（Memory Order）

原子操作不仅控制操作的原子性，还通过**内存序**控制编译器和 CPU 对内存访问的重排规则。C++11 定义了 6 种内存序，常用的有三类：

| 内存序 | 枚举值 | 语义 |
|---|---|---|
| 宽松序 | `memory_order_relaxed` | 仅保证原子性，不限制重排 |
| 获取-释放序 | `memory_order_acquire` / `memory_order_release` | 建立 happens-before 关系 |
| 顺序一致序 | `memory_order_seq_cst` | 所有线程看到相同的操作全局顺序 |

`seq_cst` 是默认选项，最安全但开销最大；在 ARM 架构上，`seq_cst` 的 store 操作需要插入 `DMB ISH`（数据内存屏障）指令，代价明显。`acquire`/`release` 配对是构建无锁数据结构的基础——生产者用 `release` 写入，消费者用 `acquire` 读取，确保生产者在写标志位之前的所有写操作对消费者可见。

---

## 实际应用

**引用计数**：`std::shared_ptr` 的控制块内部使用原子变量维护强引用计数和弱引用计数。每次拷贝时调用 `fetch_add(1, memory_order_relaxed)`（因为单纯增加计数不需要同步其他内存），析构时调用 `fetch_sub(1, memory_order_acq_rel)` 并检测归零，此处需要 `acquire` 语义以确保看到对象的完整销毁状态。

**自旋锁实现**：可用一个 `std::atomic<bool>` 实现轻量自旋锁：
```cpp
std::atomic<bool> flag{false};
// 加锁
while (flag.exchange(true, memory_order_acquire)) { /* spin */ }
// 解锁
flag.store(false, memory_order_release);
```
`exchange` 原子地写入 `true` 并返回旧值，若旧值为 `false` 则加锁成功。

**无等待计数器**：高性能服务器（如 Nginx、Redis）常用原子整型统计请求数，避免为每次计数操作加互斥锁。Linux 内核的 `atomic_t` 类型也广泛用于设备引用计数、模块使用计数等场景。

---

## 常见误区

**误区一：原子操作可以替代所有互斥锁**。原子操作只能保证单个变量的单次操作不可分割，若业务逻辑需要在多个变量之间维持一致性（例如同时更新链表的头指针和元素计数），单纯的原子操作无法保证复合不变量，必须借助互斥锁或更复杂的无锁算法。

**误区二：`memory_order_relaxed` 不安全，应总是使用 `seq_cst`**。宽松序在仅需要原子性、不需要跨线程同步副作用的场景（如独立的统计计数器）是完全正确的，且性能更优。盲目使用 `seq_cst` 会在多核 ARM 平台上产生不必要的内存屏障，降低吞吐量。

**误区三：整型的 `++` 运算在声明为 `std::atomic<int>` 后是原子的**。实际上，`atomic_var++` 中的后缀 `++` 运算符被重载为调用 `fetch_add(1)`，这是原子操作。但若写成 `atomic_var = atomic_var + 1`，则会先 `load`、再做普通加法、再 `store`，三步之间可能被打断，不是原子操作。

---

## 知识关联

学习原子操作需要对**互斥锁**（前置概念）有清晰认识：互斥锁通过阻塞线程实现串行化，而原子操作通过硬件指令实现非阻塞的数据安全访问，两者在适用粒度和开销上形成互补。理解 CAS 的循环重试模式和 `acquire`/`release` 语义，是进入**无锁编程**（后续概念）的必要基础——无锁栈、无锁队列、Hazard Pointer 等数据结构均以原子操作为基本构建块。原子操作的内存序规则则直接引出**内存模型**（后续概念）的完整讨论，包括 Sequential Consistency、Total Store Order（x86 默认模型）与 Relaxed Memory Model（ARM/POWER）之间的差异，以及 happens-before 关系的形式化定义。