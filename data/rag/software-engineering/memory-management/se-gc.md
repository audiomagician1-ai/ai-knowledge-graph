---
id: "se-gc"
concept: "垃圾回收"
domain: "software-engineering"
subdomain: "memory-management"
subdomain_name: "内存管理"
difficulty: 3
is_milestone: false
tags: ["GC"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.2
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# 垃圾回收

## 概述

垃圾回收（Garbage Collection，GC）是一种自动内存管理机制，由运行时系统负责识别并释放程序不再使用的堆内存对象，从而避免开发者手动调用 `malloc`/`free` 或 `new`/`delete` 所引发的内存泄漏与悬挂指针问题。其核心判断标准是"对象的可达性"（Reachability）：从程序的根集合（Root Set，包括栈变量、全局变量、寄存器引用）出发，无法通过引用链访问到的对象即被视为垃圾。

垃圾回收概念最早由 John McCarthy 于 1959 年在 Lisp 语言的实现中提出并应用，距今已有超过 60 年历史。McCarthy 的原始方案采用标记-清除思想，为后续所有 GC 算法奠定了基础。20 世纪 80 年代随着 Smalltalk 的流行，分代回收策略被引入；1990 年代 Java 虚拟机（JVM）将 GC 带入工业主流，使其成为现代高级语言（Java、C#、Go、Python、JavaScript）运行时的标配组件。

GC 的核心价值在于消除两类经典内存错误：其一是内存泄漏，即程序持续分配但从不释放内存，导致堆空间耗尽；其二是二次释放（Double Free），即同一块内存被释放两次导致堆结构损坏。代价则是 GC 暂停（Stop-The-World，STW）带来的延迟抖动，以及额外的 CPU 和内存开销，这正是 GC 优化研究的核心动力。

## 核心原理

### 标记-清除算法（Mark-Sweep）

标记-清除分为两个独立阶段。**标记阶段**从根集合出发，通过深度优先或广度优先遍历对象图，将所有可达对象打上"存活"标记，时间复杂度为 O(存活对象数量)。**清除阶段**线性扫描整个堆，回收所有未被标记的对象所占内存块，时间复杂度为 O(堆总大小)。

标记-清除的致命缺陷是**内存碎片化**：回收后的空闲块散落在堆中，当需要分配一个大对象时可能因找不到连续空间而触发 OOM，即使空闲总量足够。为此衍生出**标记-整理（Mark-Compact）**算法，在清除后将存活对象移动到堆的一端，消除碎片，但移动对象需要更新所有引用指针，代价更高。

### 分代假说与分代回收（Generational GC）

分代回收基于**弱分代假说（Weak Generational Hypothesis）**：大多数对象在分配后很快就会死亡（实验数据表明，在 Java 程序中约 80%~98% 的新生对象在第一次 GC 前即成为垃圾）。据此将堆划分为：

- **新生代（Young Generation / Eden + Survivor）**：存放新分配对象，使用复制算法（Copying GC），每次只复制存活对象到另一个半空间，效率极高。
- **老年代（Old Generation / Tenured）**：存放经历多次 GC 仍存活的长生命周期对象（JVM 默认晋升阈值为 15 次 Minor GC），使用标记-整理算法。

新生代 GC（Minor GC）频繁发生但速度快（毫秒级）；老年代 GC（Major GC / Full GC）代价高，会触发全堆扫描。跨代引用通过**写屏障（Write Barrier）**配合**记忆集（Remembered Set）**追踪：每次老年代对象引用新生代对象时，写屏障将该引用记录到记忆集中，Minor GC 时将记忆集内容加入根集合，避免扫描整个老年代。

### 增量式与并发 GC（Incremental / Concurrent GC）

传统 Mark-Sweep 需要 Stop-The-World：暂停所有应用线程，GC 线程独占运行，导致 Java 应用可能产生数百毫秒甚至秒级的 STW 暂停。增量式 GC 将标记工作切分为若干小步骤，与应用线程交替执行，每次只标记一部分对象，将长暂停分散为多个短暂停（每次 < 5ms）。

并发 GC（如 JDK 9 引入的 G1 GC 的并发标记阶段、JDK 15 中 ZGC 实现的几乎全并发方案）允许 GC 线程与应用线程同时运行。但并发带来**三色不变性（Tri-color Invariant）**问题：应用线程在标记过程中修改对象引用，可能导致本应存活的对象被误判为垃圾（漏标）。解决方案是**SATB（Snapshot-At-The-Beginning）**或**增量更新（Incremental Update）**写屏障，G1 使用 SATB，CMS 使用增量更新。ZGC 通过**染色指针（Colored Pointer）**在 64 位地址的高位嵌入 GC 状态元数据，实现 STW 暂停 < 1ms（在 JDK 16 后的基准测试中，ZGC 在 128GB 堆上的最大暂停时间通常低于 0.5ms）。

## 实际应用

**JVM 垃圾回收器选择**：吞吐量优先的批处理应用（如 Hadoop MapReduce）选用 Parallel GC（JDK 8 默认），以最大化 CPU 利用率；低延迟的交互式服务（如在线游戏、金融交易系统）选用 ZGC 或 Shenandoah GC，将 STW 控制在亚毫秒级；G1 GC（JDK 9 后默认）适合大多数中等规模堆（4GB~32GB）的通用服务端应用，通过 `-XX:MaxGCPauseMillis=200` 参数设定目标暂停时间软目标。

**Python 的引用计数 + 循环检测**：CPython 使用引用计数（Reference Counting）作为主要 GC 机制，每个对象维护一个 `ob_refcnt` 字段，计数归零时立即释放；但循环引用（如 `a.next = b; b.prev = a`）会导致计数永不归零，因此 CPython 额外实现了一个分代式的循环引用检测器（`gc` 模块），专门处理 `list`、`dict`、`class` 等可能形成环的容器对象。

**Go 的三色并发标记清除**：Go 的 GC 自 1.5 版本起采用并发三色标记，目标是将 STW 控制在 1ms 以内；通过 `GOGC` 环境变量（默认值 100，表示堆增长 100% 时触发 GC）调节触发频率与内存占用之间的平衡。

## 常见误区

**误区一：GC 能完全防止内存泄漏。** 实际上，只要对象仍被根集合可达，GC 就不会回收它，即便程序逻辑上已不再使用该对象。Java 中最典型的案例是静态集合（如 `static List<Object>`）持续累积对象引用，或者监听器/回调注册后忘记反注册，导致对象永远可达但永远无用，形成"逻辑泄漏"。这类问题需要借助 VisualVM、MAT 等堆分析工具检测。

**误区二：分代 GC 中老年代 GC 不频繁，因此可以忽略。** Full GC 虽然频率低，但其单次暂停时间可达数秒，是导致服务超时和 SLA 违规的主要原因。老年代过早晋升（Premature Promotion）——即本属短生命周期的大对象因新生代空间不足直接进入老年代——会大幅加速 Full GC 频率，需要通过调整 `-Xmn`（新生代大小）或 `-XX:PretenureSizeThreshold` 参数避免。

**误区三：增量 GC 一定比 STW GC 整体性能更好。** 增量/并发 GC 降低了最大暂停时间，但引入了写屏障、并发标记等额外开销，总吞吐量（Throughput）通常低于 Parallel GC。以 JDK 基准测试为例，Parallel GC 的吞吐量往往比 ZGC 高出 5%~15%，因此对于批量数据处理场景，选择低延迟 GC 反而可能降低整体处理速度。

## 知识关联

学习垃圾回收需要以**内存管理概述**为前提，特别是堆（Heap）与栈（Stack）的区别、动态内存分配的工作方式，以及指针/引用的本质——这是理解"可达性"判断逻辑的必要基础。三色标记算法中对对象图（Object Graph）的遍历本质上是图论的广度/深度优先搜索，若熟悉该算法，可直接类比理解标记阶段的执行逻辑。

在此基础上，**GC 优化**是直接的后续主题：涵盖 JVM GC 日志解读（`-Xlog:gc*`）、堆大小调优、选择合适的回收器、识别 GC 压力根因（如大对象分配、高分配速率），以及 Go 的 `GOGC`/`GOMEMLIMIT` 参数调节策略。此外，理解 GC 原理后可以更好地分析**内存分析