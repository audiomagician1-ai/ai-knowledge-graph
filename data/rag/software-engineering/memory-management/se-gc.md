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
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
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

垃圾回收（Garbage Collection，GC）是一种自动内存管理机制，由运行时系统负责识别程序不再使用的内存对象并将其释放，程序员无需手动调用 `free()` 或 `delete`。GC 的核心判断标准是**可达性**（Reachability）：从根集合（Root Set，包括栈变量、全局变量、寄存器中的引用）出发，能够被引用链追踪到的对象视为存活，无法到达的对象即为垃圾。

GC 概念由 John McCarthy 于 1959 年在实现 Lisp 语言时首次引入，最初采用的是标记-清除算法。此后数十年间，GC 技术随着 Java（1995）、Go、Python、JavaScript V8 等语言和运行时的普及而不断演进。现代 GC 已从简单的全局停顿发展为支持并发、增量、分代等复杂策略，将平均停顿时间压缩至毫秒级以下。

GC 的重要性在于它消除了两类最危险的手动内存错误：悬挂指针（dangling pointer，释放后继续访问）和内存泄漏（忘记释放已不使用的对象）。代价是引入了额外的 CPU 开销（通常为 5%–20%）以及不可预测的停顿（Stop-The-World，STW），这也是理解和优化 GC 的核心动机。

---

## 核心原理

### 标记-清除算法（Mark-Sweep）

标记-清除是最基础的 GC 算法，分为两个阶段：

1. **标记阶段**：从根集合出发，通过深度优先或广度优先遍历对象图，对所有可达对象打上"存活"标记。
2. **清除阶段**：线性扫描整个堆，将未标记的对象回收至空闲列表。

标记-清除的时间复杂度为 O(Live + Heap)，其中 Live 是存活对象总大小，Heap 是堆总大小。其最大缺陷是**内存碎片化**：回收后空闲空间散布在堆中，导致大对象分配失败，即使总空闲量充足。标记-压缩（Mark-Compact）算法通过在清除后将存活对象移动到堆的一端来解决碎片问题，但代价是需要更新所有指向移动对象的引用。

### 分代垃圾回收（Generational GC）

分代 GC 基于一个经验性观察——**弱代际假说（Weak Generational Hypothesis）**：大多数对象在分配后很快就会死亡（"朝生夕灭"）。以 Java HotSpot JVM 为例，堆被划分为：

- **新生代（Young Generation）**：占堆的约 1/3，细分为 Eden 区和两个 Survivor 区（比例默认为 8:1:1）。新对象在 Eden 分配，Minor GC 发生时存活对象复制到 Survivor 区。
- **老年代（Old Generation）**：对象在 Survivor 区经历默认 15 次 Minor GC 仍存活后晋升（Promotion）至此，触发 Major GC（或 Full GC）的频率远低于 Minor GC。

Minor GC 只扫描新生代，因为新生代通常只占堆的小部分，停顿时间极短（通常 < 10ms）。为处理老年代指向新生代的引用，JVM 使用**卡表（Card Table）**记录跨代引用，每张卡对应 512 字节的堆区域，Minor GC 扫描时只需检查被标脏的卡表条目。

### 增量与并发 GC（Incremental / Concurrent GC）

全局 STW 会导致明显的延迟抖动，对交互式应用影响尤为严重。增量 GC 将标记工作切分为小片，与应用线程交替执行，每次 GC 增量的时间固定（如 5ms），以此降低单次最大停顿时间。

并发 GC 则让 GC 线程与应用线程**同时运行**，但这引入了一个新问题：应用线程在 GC 标记过程中可能修改对象引用，导致本应存活的对象被错误回收（**漏标**）。解决方案是**写屏障（Write Barrier）**：每次应用线程修改引用时插入一段额外逻辑，记录引用变更。Go 语言的三色标记法（Tri-color Marking）将对象分为白色（未访问）、灰色（已发现但子对象未扫描）、黑色（已完全扫描），通过维护"黑色对象不能直接指向白色对象"的不变式来保证正确性，写屏障负责在违反该不变式时将相关对象重新染灰。

---

## 实际应用

**Java G1 GC（Garbage First）**：自 Java 9 起成为默认 GC，将堆划分为 2048 个大小相等的 Region（默认 1MB–32MB），优先回收垃圾密度最高的 Region，以满足用户设定的停顿时间目标（`-XX:MaxGCPauseMillis`，默认 200ms）。

**Go 的并发三色标记**：Go 1.5 引入并发 GC 后，GC 停顿时间从秒级降至 < 1ms。Go 使用混合写屏障（Hybrid Write Barrier，Go 1.14 引入），同时处理堆上对象和栈上对象的引用变更，避免了对每个 goroutine 栈单独 STW 的需求。

**Python 的引用计数 + 分代**：CPython 主要依赖引用计数（Reference Counting），每个对象维护一个 `ob_refcnt` 字段，归零时立即释放。但引用计数无法处理循环引用（如 `a.x = b; b.x = a`），因此 CPython 额外引入了一个周期检测器（Cyclic Garbage Collector），专门针对容器对象执行分代标记回收。

---

## 常见误区

**误区一：GC 能解决所有内存泄漏**
GC 只回收不可达对象。如果代码将不再使用的对象持续存入一个长生命周期的集合（如静态 `HashMap`），这些对象仍然可达，GC 不会回收它们——这是 Java 中最典型的"逻辑泄漏"。Android 开发中 Activity 被静态变量持有导致无法回收是该误区的经典案例。

**误区二：引用计数是 GC 的一种，且没有 STW**
引用计数确实能立即回收无引用对象，但它天然无法处理循环引用（需要额外的周期检测器），且每次修改引用都需原子操作更新计数，在多线程场景下开销显著。严格意义上，引用计数属于 GC 的一种实现策略，但其循环引用问题使得大多数语言不会单独依赖它。

**误区三：GC 停顿只与堆大小线性相关**
实际上，分代 GC 的 Minor GC 停顿时间主要取决于**存活对象数量**而非堆总大小，因此即便堆设置为 8GB，如果新生代存活率低，Minor GC 仍可在几毫秒内完成。Full GC 的停顿才与老年代存活对象规模强相关。盲目增大堆只会推迟 Full GC 触发时机，不会减少单次 Full GC 的停顿时长。

---

## 知识关联

**前置概念：内存管理概述**
理解 GC 需要先掌握堆（Heap）与栈（Stack）的区别：栈内存随函数调用自动释放，GC 管理的是堆上动态分配的对象。此外，理解指针和引用的语义是掌握可达性分析的基础——GC 通过追踪引用图而非内存地址值来判断对象存活状态。

**后续概念：GC 优化**
掌握 Mark-Sweep、分代和增量 GC 原理后，GC 优化的学习重点包括：调整新生代与老年代比例（`-Xmn`）、选择适合低延迟场景的 ZGC 或 Shenandoah（停顿目标 < 1ms）、分析 GC 日志中的晋升速率（Promotion Rate）和分配速率（Allocation Rate），以及通过对象池（Object Pool）减少短生命周期对象的分配压力来降低 Minor GC 频率。