---
id: "cg-gpu-scheduling"
concept: "GPU调度"
domain: "computer-graphics"
subdomain: "gpu-architecture"
subdomain_name: "GPU架构"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 44.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.448
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# GPU调度

## 概述

GPU调度（GPU Scheduling）是指GPU硬件如何将线程块（Thread Block）分配到流式多处理器（SM，Streaming Multiprocessor）上执行，以及SM内部如何在多个Warp之间进行上下文切换的机制。与CPU调度不同，GPU的调度完全由硬件控制，程序员无法通过软件指令干预Warp的执行顺序。这一设计使得GPU调度能够做到真正意义上的"零开销上下文切换"。

GPU调度机制最早在NVIDIA的Tesla架构（2006年）中得到系统性实现。彼时的核心设计思想是：通过在SM上同时驻留大量Warp，当某个Warp因内存访问而进入等待状态时，调度器可以立刻切换到另一个就绪Warp，从而隐藏内存延迟。这与CPU依靠缓存来降低延迟的策略截然不同——GPU选择用并发度来掩盖延迟。

理解GPU调度对于编写高性能CUDA程序至关重要。线程块的分配方式直接决定了SM的利用率，而Warp调度策略则影响着指令流水线的填充效率。错误地配置线程块大小，可能导致整个SM只有少量Warp可供调度，使得延迟无法被隐藏，GPU的实际吞吐量大幅下降。

## 核心原理

### 线程块到SM的静态分配

当CUDA内核启动时，GPU的全局调度器（GigaThread Engine）负责将线程块分配给各个SM。这一分配在内核启动时完成，整个执行过程中线程块不会在SM之间迁移——这与CPU进程可以在核心间迁移的动态调度截然不同。每个SM能够同时驻留的最大线程块数量受到硬件寄存器总量、共享内存总量和线程块槽位数的三重限制。以NVIDIA Ampere架构（A100）为例，每个SM最多同时驻留32个线程块或1536个线程，以先达到上限的为准。

### Warp调度器与零开销切换

每个SM内部包含若干个Warp调度器（Warp Scheduler）。在Turing架构之前，每个SM通常有4个Warp调度器；Turing（2018年）及之后的架构中每个子分区（Sub-core）拥有1个调度器。每个时钟周期，每个Warp调度器从"就绪态"Warp池中选择一个Warp发射指令。

零开销上下文切换的实现依赖于一个关键设计：每个Warp的寄存器文件、程序计数器和栈指针全部**常驻于片上寄存器文件**中，切换时不需要将任何状态保存到内存。这与CPU的上下文切换形成鲜明对比——CPU切换线程需要将寄存器内容压栈，耗费数十到数百个时钟周期。GPU的Warp切换则真正做到在单个时钟周期内完成，切换代价为**0个周期**。

### Warp状态机

每个Warp在任意时刻处于以下三种状态之一：

- **就绪态（Ready）**：所有操作数已就绪，可以在下一周期被调度执行。
- **停滞态（Stalled）**：正在等待内存访问返回、同步栅栏（`__syncthreads()`）或长延迟指令（如超越函数`sin`、`exp`，典型延迟约100个时钟周期）完成。
- **未选中态（Eligible but not selected）**：操作数就绪但本周期未被调度器选中。

调度器的核心任务是在每个时钟周期从就绪态Warp中选一个执行。常见的选择策略包括**轮转调度（Round-Robin）**和**最近最少使用（Greedy-then-oldest, GTO）**策略。NVIDIA的GTO策略倾向于优先让同一Warp连续执行，以利用数据的局部性，同时当该Warp停滞时立即切换到最老的就绪Warp。

### 延迟隐藏的数学条件

要完全隐藏内存延迟，SM上驻留的Warp数必须满足：

> **所需Warp数 ≥ 内存访问延迟（时钟周期数） ÷ 每个Warp每次发射消耗的周期数**

以全局内存延迟约为400个时钟周期为例，若每个Warp每次发射占用1个周期，则至少需要400个就绪Warp——这远超单个SM的容量（通常最多64个Warp）。这说明仅靠Warp切换无法完全隐藏全局内存延迟，L1/L2缓存命中（延迟约20-30周期）才是可以被Warp调度完全掩盖的场景。

## 实际应用

**案例一：线程块大小对调度的影响**
若将线程块大小设置为32（即1个Warp），而SM最多支持32个线程块，则该SM最多驻留32个Warp。但若将线程块设为128（4个Warp），在同样占用32个线程块槽位的情况下，SM可驻留128个Warp，调度器拥有更多候选Warp，延迟隐藏效果更好。使用NVIDIA Nsight Compute工具的"Warp State Statistics"面板可以直接观察各状态Warp的分布，诊断调度效率。

**案例二：`__syncthreads()`对调度的影响**
线程块内部的同步屏障会将该线程块的所有Warp同时置为停滞态，等待最慢的那个Warp到达屏障。若某个Warp因分支发散而执行了额外指令，同一线程块的其他Warp会在屏障处空等，但此时调度器可以调度**其他线程块**的就绪Warp——这是GPU通过多线程块并发来消化同步开销的经典机制。

**案例三：寄存器溢出对调度的影响**
当每个线程使用超过SM寄存器文件所能承载的量时（以A100为例，每个SM有65536个32位寄存器），编译器会将部分寄存器溢出到本地内存（Local Memory，实际映射到全局内存）。溢出后的访问延迟约400周期，导致更多Warp进入停滞态，即使SM驻留Warp数不变，调度效率也会显著下降。

## 常见误区

**误区一：Warp调度顺序是可预测的**
许多初学者认为同一线程块内的Warp会按线程ID顺序执行，因此编写了依赖Warp执行顺序的代码（如用Warp 0的结果覆盖Warp 1需要读取的内存，且不使用同步）。实际上，NVIDIA硬件的调度顺序在不同SM、不同硬件代际之间均无保证，任何依赖Warp间隐式执行顺序的代码都会引发数据竞争。

**误区二：线程块数越多调度效率越高**
增加线程块数可以提高SM的并发Warp数，但当SM已经达到最大驻留线程数时，进一步增加线程块数只会增加全局调度器的排队开销，对SM内部的Warp调度毫无帮助。例如在A100上，一旦每个SM的活跃线程数已达1536，再将线程块从16个增加到32个（将线程块大小从96减至48）不会改变Warp总数，但会消耗更多线程块槽位。

**误区三：零开销切换意味着调度本身没有代价**
零开销指的是**上下文保存/恢复**的代价为零，但Warp调度器本身每个周期仍需消耗逻辑资源来评估哪些Warp就绪、选择发射对象。当SM上就绪Warp极少时（如只有1-2个），调度器可能在某些周期找不到可发射的Warp，造成流水线空泡（Pipeline Bubble），此时零开销的优势无从体现。

## 知识关联

GPU调度直接建立在**占用率（Occupancy）**概念之上：占用率描述了SM上实际驻留Warp数与最大可驻留Warp数的比值，而GPU调度机制正是在这些驻留Warp之间进行切换。较高的占用率为调度器提供了更大的候选Warp池，是延迟隐藏得以实现的前提条件。通过CUDA的`__launch_bounds__`修饰符或`cudaOccupancyMaxPotentialBlockSize` API，开发者可以引导编译器限制寄存器使用量，进而影响SM驻留Warp数，最终改变调度器的可用资源。

在理解GPU调度之后，自然可以深入探讨**内存访问模式**（合并访问如何减少Warp停滞时间）和**指令级并行性**（ILP，通过在单个Warp内发射多条独立指令来减少对Warp切换的依赖）等更高级主题，这些都是在GPU调度框架下进一步提升性能的进阶手段。
