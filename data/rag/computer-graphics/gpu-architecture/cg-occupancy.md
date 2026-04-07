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
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
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

占用率（Occupancy）是指GPU上某个流式多处理器（SM，Streaming Multiprocessor）中**实际活跃Warp数量与该SM理论最大Warp容量的比值**，通常以百分比表示。例如，NVIDIA Ampere架构的SM最多可同时驻留64个Warp，若某个kernel运行时每个SM只有32个活跃Warp，则占用率为50%。这个比值直接决定了GPU能够用于隐藏内存延迟（Latency Hiding）的线程资源量。

占用率的概念随NVIDIA CUDA编程模型的发展而逐渐系统化。2006年CUDA 1.0发布时，开发者便已需要考虑寄存器与共享内存对线程块（Thread Block）数量的限制。NVIDIA专门提供了"CUDA Occupancy Calculator"电子表格工具，帮助开发者在编译前估算特定kernel的占用率，该工具至今仍随CUDA Toolkit发布。

占用率之所以重要，是因为GPU的计算管线依赖大量并发Warp来掩盖内存访问的数百周期延迟（全局内存延迟通常为400–800个时钟周期）。当SM中活跃Warp不足时，调度器在等待内存数据返回时无法切换到其他就绪Warp，造成流水线空泡（Stall），吞吐量下降。

---

## 核心原理

### 占用率的计算公式

占用率由以下公式定义：

$$\text{Occupancy} = \frac{\text{Active Warps per SM}}{\text{Max Warps per SM}}$$

实际的活跃Warp数量受到三个硬件资源的**同时约束**，取其中最严格的限制：

1. **寄存器数量**：每个SM拥有固定数量的32位寄存器（Ampere架构为65536个）。若一个线程使用 $R$ 个寄存器，每个Warp有32个线程，则每个SM能驻留的最大Warp数为 $\lfloor 65536 / (R \times 32) \rfloor$。
2. **共享内存大小**：每个线程块申请 $S$ 字节共享内存，SM的共享内存总量（如96KB）限制了并发线程块数，进而限制Warp数。
3. **线程块数量上限**：每个SM最多同时驻留的线程块数量有硬件上限（Ampere为32个线程块/SM）。

### 寄存器压力对占用率的影响

寄存器压力（Register Pressure）是导致占用率下降最常见的原因。编译器（NVCC或ROCm HCC）在编译kernel时，会为每个线程分配寄存器。若一个kernel逻辑复杂，编译器可能为每个线程分配64个甚至更多寄存器。

以NVIDIA Turing架构（TU102）为例，SM拥有65536个寄存器，理论最大Warp数为32。若每线程使用32个寄存器，可驻留 $65536 / (32 \times 32) = 64$ 个Warp（受限于最大Warp数32，实际为32，占用率100%）；若每线程使用64个寄存器，则可驻留 $65536 / (64 \times 32) = 32$ 个Warp（占用率仍为100%）；但若每线程使用128个寄存器，则只有16个Warp（占用率50%）。

开发者可通过 `__launch_bounds__(maxThreadsPerBlock, minBlocksPerSM)` 指令告知编译器目标占用率，使编译器主动限制寄存器分配；也可使用 `-maxrregcount=N` 编译选项强制限制每个线程的寄存器上限。

### 延迟隐藏与占用率的关系

GPU通过Warp切换（Zero-Cost Context Switch）来隐藏内存延迟。当一个Warp发出全局内存读取请求后，调度器立即切换到另一个就绪Warp继续执行。若要完全掩盖400周期的内存延迟，且每条指令吞吐为1条/周期，则理论上需要至少约25–30个活跃Warp才能保持计算单元不空闲。

这意味着**100%占用率并非总是必要的**。若一个kernel以计算密集型为主（算术强度高），即使只有25%的占用率，只要活跃Warp足够覆盖流水线深度，也可达到较高吞吐。反之，内存密集型kernel（如矩阵转置）则更依赖高占用率来隐藏延迟。

---

## 实际应用

**矩阵乘法（GEMM）优化**：cuBLAS的SGEMM kernel通常使用每线程128–256个寄存器以保留大量数据在寄存器中（避免频繁内存访问），导致占用率仅为12%–25%。但由于其算术强度极高（每次内存访问对应大量浮点运算），低占用率完全可以接受，实测吞吐仍可达到峰值算力的80%以上。

**归约（Reduction）kernel**：全局内存归约操作内存访问频繁，通常需要将占用率提升至75%以上才能有效隐藏延迟。CUDA Sample中的标准归约kernel使用256线程/块、共享内存归约，在V100上实测可达到约78%占用率，内存带宽利用率超过80%。

**使用NVIDIA Nsight Compute分析**：该工具可直接报告kernel的理论占用率（Theoretical Occupancy）与实测占用率（Achieved Occupancy），并标注是寄存器、共享内存还是线程块数量成为瓶颈，是实际优化中的标准工具。

---

## 常见误区

**误区1：占用率越高，性能一定越好**
这是最普遍的错误认知。对于寄存器密集型kernel（如GEMM），强制降低寄存器数量以提升占用率，会导致寄存器溢出（Register Spilling）——数据被迫写入本地内存（Local Memory，物理上是L1缓存或全局内存），访问延迟大幅增加，最终性能反而下降。寄存器溢出的代价通常远大于低占用率带来的损失。

**误区2：共享内存增加不影响占用率**
实际上，共享内存与寄存器同样是SM的有限资源。若一个线程块申请了48KB共享内存，而SM共享内存总量为96KB，则每个SM最多只能驻留2个线程块，即使寄存器用量很低，占用率也会被共享内存严重限制。Volta架构引入了可配置的L1缓存/共享内存比例（最大96KB共享内存），部分缓解了这一问题。

**误区3：占用率是静态固定的**
占用率的理论值由编译期参数决定，但实际运行时的"已实现占用率"（Achieved Occupancy）还受到尾部效应（Tail Effect）影响——当线程块总数不能被SM数量整除时，最后一轮线程块只能部分分配，导致实测占用率低于理论值。例如用320个线程块跑在84个SM的A100上，最后一轮只有 $320 \mod 84 = 68$ 个线程块，整体平均占用率下降。

---

## 知识关联

**前置概念——Warp/Wavefront**：Warp是占用率的基本计数单位。SM上并发驻留的Warp数量直接构成占用率的分子，理解Warp的32线程结构和零开销上下文切换机制是量化占用率收益的前提。

**后续概念——GPU调度**：占用率决定了调度器（GigaThread Engine及SM内部的Warp Scheduler）的可用候选Warp池大小。Ampere SM配备4个Warp调度器，每个调度器每周期可发射1条指令；只有当活跃Warp数量充足（至少4个就绪Warp）时，4个调度器才能全部满载工作，进而理解双发射（Dual-Issue）等调度策略需要以占用率为基础。