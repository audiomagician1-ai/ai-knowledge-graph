---
id: "se-false-sharing"
concept: "False Sharing"
domain: "software-engineering"
subdomain: "multithreading"
subdomain_name: "多线程"
difficulty: 3
is_milestone: false
tags: ["性能"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 82.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---


# 伪共享（False Sharing）

## 概述

伪共享是多核处理器环境中一种特殊的性能退化现象：多个线程分别访问**逻辑上独立**的变量，但这些变量恰好位于同一条缓存行（Cache Line）内，导致硬件缓存一致性协议将它们当作同一数据单元反复争用和失效，从而产生严重的性能损耗。关键在于，这种争用并非因为线程真正共享同一数据，而是因为缓存行的物理布局造成了"假共享"的错觉。

伪共享问题随着多核CPU的普及而凸显。Intel在2003年推出奔腾4（Netburst架构）时，缓存行已固定为64字节；之后的x86体系结构沿用至今。MESI协议（Modified-Exclusive-Shared-Invalid）是触发伪共享的核心机制——当一个核修改了缓存行中的任意字节，该缓存行在其他所有核上的副本必须被标记为Invalid，即使那些核只需要该行中完全不同的字节。

伪共享之所以难以察觉，是因为代码逻辑完全正确、无需加锁，但性能却远低于预期。在一项对Java并发队列的基准测试中，引入缓存行填充（Padding）后吞吐量提升幅度可超过**3倍**，足见其危害。

## 核心原理

### 缓存行与MESI协议的交互

现代x86/ARM处理器的L1/L2缓存以64字节为一个缓存行单位进行数据加载和写回。MESI协议规定，当核A将某缓存行状态从Shared（S）升级为Modified（M）时，必须向总线广播一条RFO（Request For Ownership）消息，使其他所有持有该行副本的核将其状态置为Invalid（I）。此后，核B若要读取同一缓存行（哪怕只读其中另一个独立变量），必须等待核A将脏行写回内存或直接通过Cache-to-Cache Transfer传输，这一延迟可达**数十至数百个CPU时钟周期**。

### 伪共享的量化模型

设两个线程T1和T2分别以频率 $f$ 更新变量 $a$ 和 $b$，若 $a$ 和 $b$ 同处一条缓存行，每次更新所引发的RFO无效化代价为 $C_{rfo}$（约60~300纳秒，取决于CPU架构和NUMA拓扑），则伪共享导致的额外开销约为：

$$\text{Overhead} \approx 2 \times f \times C_{rfo}$$

而若将 $a$ 和 $b$ 分离至不同缓存行，该项开销降为零。此公式说明更新频率越高、CPU核间延迟越大，伪共享的破坏力越强。

### 缓存行填充（Padding）技术

消除伪共享最直接的方法是在热点变量周围插入填充字节，使每个独立变量独占一条完整的64字节缓存行。Java中著名的`Disruptor`框架使用如下模式：

```java
// 前置填充7个long（7×8=56字节）+ value自身8字节 = 64字节
public long p1, p2, p3, p4, p5, p6, p7;
public volatile long value;
public long p8, p9, p10, p11, p12, p13, p14;
```

Java 8引入了`@Contended`注解（位于`sun.misc`包，JVM启动需加`-XX:-RestrictContended`），可由JVM自动在被标注字段前后各插入128字节的填充区域，避免手动维护。C++11及以后版本则可使用`alignas(64)`关键字强制变量对齐至缓存行边界。

### GPU环境下的类似现象

在GPU计算中，类似的问题出现在共享内存（Shared Memory）的Bank冲突（Bank Conflict）中：多个线程同时访问同一内存Bank时，访问被串行化。与CPU伪共享不同，GPU Bank冲突针对的是同一Warp内线程对同一Bank的真实冲突，而非缓存一致性协议引发的假冲突，但二者都以填充（Padding）作为主要解决手段——在共享内存数组中插入哑元列可将32路Bank冲突降为0路。

## 实际应用

**Disruptor无锁队列**：LMAX公司开发的`RingBuffer`对序列号（Sequence）字段应用缓存行填充，使生产者与消费者的序列号各占独立缓存行，单线程吞吐量可达每秒6亿事件。

**Linux内核的`per-cpu`变量**：Linux使用`__cacheline_aligned_in_smp`宏（本质是`__attribute__((aligned(64)))`）将频繁更新的每CPU计数器对齐至缓存行边界，避免不同CPU核的计数器互相失效。

**JDK中的`LongAdder`**：Java 8的`LongAdder`内部维护一个`Cell[]`数组，每个`Cell`对象用`@Contended`注解修饰，确保不同线程在不同核上累加时各自的Cell位于独立缓存行，避免全局计数器的伪共享，在高并发下比`AtomicLong`性能提升可达**10倍以上**。

## 常见误区

**误区一：加了volatile或synchronized就能消除伪共享**。`volatile`保证可见性，`synchronized`提供互斥，但两者都不改变变量在内存中的物理布局。只要 $a$ 和 $b$ 仍在同一64字节缓存行内，MESI协议依然会因任一变量的写操作而使整行失效，伪共享照常发生。

**误区二：伪共享只影响写操作**。实际上，写操作引发RFO后，其他核的读操作也会因缓存行失效而被迫重新从上级缓存或内存加载数据，读性能同样受损。在读多写少的场景中，一个高频写变量与多个只读变量共处同一缓存行，会持续驱逐只读数据，造成"单向伪共享"性能瓶颈。

**误区三：填充越多越好**。过度填充会增加数据结构的内存占用，降低缓存利用率，在访问模式为顺序扫描（而非随机并发写）的场景中，填充会使可用的L1/L2缓存行数量减少，反而降低缓存命中率。Padding只应用于**高频并发写**的热点变量。

## 知识关联

理解伪共享需要以MESI缓存一致性协议为前提，而GPU计算中对共享内存Bank冲突的学习（前置知识）使学习者已熟悉"填充换性能"这一思路，可以将GPU Padding的直觉直接迁移到CPU缓存行Padding上，但需注意两者的冲突触发机制不同——GPU是真实地址冲突，CPU是缓存行粒度的假冲突。

在后续学习**并发数据结构**时，伪共享是设计无锁队列、并发哈希表时必须主动规避的内存布局问题。例如，设计一个多生产者多消费者队列时，头指针（head）和尾指针（tail）若相邻存放，则生产者线程与消费者线程会因更新各自指针而互相失效对方的缓存行；将两者分置于独立缓存行是并发队列实现的标准做法，而这一设计决策正是从伪共享原理直接推导出的。