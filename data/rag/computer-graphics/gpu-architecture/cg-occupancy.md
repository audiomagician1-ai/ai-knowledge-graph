---
id: "cg-occupancy"
concept: "占用率"
domain: "computer-graphics"
subdomain: "gpu-architecture"
subdomain_name: "GPU架构"
difficulty: 3
is_milestone: false
tags: ["优化"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 50.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.452
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 占用率（Occupancy）

## 概述

占用率（Occupancy）是GPU架构中的一个量化指标，定义为**SM（流式多处理器）上实际活跃的Warp数量与该SM理论上能容纳的最大Warp数量之比**。以NVIDIA A100 GPU为例，每个SM最多可同时驻留64个Warp，若某内核启动后每个SM仅活跃16个Warp，则占用率为25%。这个比值直接反映了GPU计算资源的利用程度。

占用率的概念随着NVIDIA在2006年发布CUDA 1.0时被正式引入开发者工具链。在此之前，程序员几乎无法量化Warp调度层面的资源竞争情况。NVIDIA配套提供了"CUDA Occupancy Calculator"电子表格工具，允许开发者在不实际运行代码的情况下估算占用率，这一工具至今仍被集成在Nsight Compute分析器中。

占用率的重要性在于其与**延迟隐藏（Latency Hiding）**的直接关联。GPU通过在等待内存访问（典型延迟为400-800个时钟周期）时切换到其他就绪Warp来隐藏延迟。若活跃Warp数量不足，当所有Warp都在等待内存返回时，执行单元将空转（stall），吞吐量急剧下降。

---

## 核心原理

### 占用率的计算公式

SM上的最大活跃Warp数由三个硬件资源同时约束，取三者中最严格的限制：

```
活跃Block数 = min(
    floor(最大Warp数 / 每Block的Warp数),
    floor(寄存器总量 / 每Block寄存器用量),
    floor(共享内存总量 / 每Block共享内存用量)
)

占用率 = (活跃Block数 × 每Block的Warp数) / SM最大Warp数
```

以NVIDIA Ampere架构（A100）为例：每个SM拥有65536个32位寄存器、164KB共享内存、最大64个Warp。若一个内核每线程使用64个寄存器，Block大小为256线程（即8个Warp），则每个Block消耗 256×64 = 16384 个寄存器，65536/16384 = 4个Block可同时驻留，活跃Warp数为32，占用率恰好为50%。

### 寄存器压力对占用率的影响

寄存器压力（Register Pressure）是导致占用率下降最常见的因素。每个SM的寄存器堆大小固定，Warp之间必须共享这一资源。当编译器为每个线程分配过多寄存器时，能同时驻留的Warp数量减少。

NVCC编译器提供 `__launch_bounds__(maxThreadsPerBlock, minBlocksPerMultiprocessor)` 修饰符，以及 `-maxrregcount=N` 编译选项来强制限制寄存器使用量。例如设置 `-maxrregcount=32` 可使Kepler架构GPU上的理论最大占用率从25%提升至100%，但编译器被迫将溢出的变量写入**本地内存（Local Memory）**（实际存储在L2缓存或DRAM中），反而可能引入额外延迟。这是寄存器优化中最典型的权衡取舍。

### 延迟隐藏的Warp数量阈值

对于计算密集型（Arithmetic Bound）内核，隐藏算术指令延迟（约4-8个时钟周期）只需6-8个活跃Warp；而对于内存密集型（Memory Bound）内核，隐藏全局内存访问延迟（约400个时钟周期）则需要更多Warp。

粗略估算所需Warp数的公式为：

```
所需活跃Warp数 ≈ 指令延迟周期数 × 每Warp每周期的吞吐量
```

以Volta架构为例，全局内存延迟约为530个时钟周期，每个SM的Warp调度器可在1个周期发射1条指令，则需要约530个活跃Warp才能**完全**隐藏延迟——而SM最大只有64个Warp，因此高内存延迟在实践中通常无法被完全掩盖，这也解释了为何内存访问模式优化比单纯提升占用率更加关键。

---

## 实际应用

**矩阵乘法内核调优**：在cuBLAS的GEMM实现中，开发者通常选择每Block使用128或256线程，并将每线程寄存器数控制在32-48之间，以在Ampere架构上维持约50%-75%的占用率。实验数据表明，对于矩阵乘法，将占用率从25%提升至50%通常带来15%-30%的性能提升，但从50%提升至100%往往没有收益，因为此时瓶颈已转移至Tensor Core的计算吞吐。

**图像处理内核的共享内存权衡**：在使用共享内存实现的2D卷积内核中，若每个Block分配48KB共享内存（A100每SM共有164KB），则同时最多驻留3个Block。若Block大小为16×16=256线程（8个Warp），活跃Warp仅24个，占用率37.5%。此时开发者可选择减小Tile大小或使用L1缓存替代显式共享内存，以换取更高占用率。

**Nsight Compute的占用率分析**：在实际性能分析中，Nsight Compute的"Occupancy"部分会直接列出理论占用率与实测占用率，并标注限制占用率的首要资源瓶颈是寄存器、共享内存还是Block数量限制，为优化提供明确方向。

---

## 常见误区

**误区一：占用率越高性能越好**。这是最普遍的误解。占用率100%并不保证最优性能，因为过度压缩寄存器使用量会导致寄存器溢出至本地内存，引入数百周期的额外延迟。NVIDIA官方文档明确指出，对于计算密集型内核，25%-50%的占用率通常已足够隐藏算术延迟，继续提升占用率收益递减。

**误区二：共享内存越大占用率越低一定越差**。共享内存用于数据复用，可大幅减少全局内存访问次数。在内存带宽受限的内核中，用较低占用率（如25%）换取更高的L1/共享内存命中率，最终吞吐量反而可能更高。衡量标准应是实际的指令吞吐（IPC）或内存带宽利用率，而非占用率本身。

**误区三：占用率是静态固定的**。实际上，CUDA动态并行（Dynamic Parallelism）和CUDA Graphs等特性会在运行时改变活跃Block分布，使得同一内核在不同调度时刻呈现不同的实测占用率。此外，Warp Divergence导致部分线程提前退出也会动态降低有效占用率。

---

## 知识关联

**前置概念——Warp/Wavefront**：占用率的计算单位是Warp（NVIDIA）或Wavefront（AMD，通常为64线程）。若不理解Warp的固定大小（32线程）及其作为调度基本单元的角色，就无法建立"SM上Warp数量竞争硬件资源"的直觉。每个Block的Warp数 = Block线程数 / 32，这是代入占用率公式的第一步。

**后续概念——GPU调度**：占用率决定了调度器的候选池大小。在学习GPU调度时，需要理解GigaThread引擎如何在SM层面分配Block，以及Warp调度器（每个SM通常有4个调度器）如何从活跃Warp池中选择就绪Warp发射指令。占用率低意味着就绪Warp数量少，调度器更容易遭遇无可发射指令的空转周期（Issue Slot Utilization下降），这正是调度策略研究的核心问题。