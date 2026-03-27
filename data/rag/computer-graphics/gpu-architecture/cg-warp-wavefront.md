---
id: "cg-warp-wavefront"
concept: "Warp/Wavefront"
domain: "computer-graphics"
subdomain: "gpu-architecture"
subdomain_name: "GPU架构"
difficulty: 3
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 49.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.433
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# Warp/Wavefront：线程束执行模型与分支发散代价

## 概述

Warp（NVIDIA术语）和 Wavefront（AMD术语）都指 GPU 中**同时以 SIMD 方式执行同一条指令的一组线程**。在 NVIDIA GPU 上，一个 Warp 固定包含 **32 个线程**；在 AMD GPU 上，Wavefront 的大小历史上为 64 个线程，但从 RDNA 架构（2019年）起可配置为 32 或 64。这个固定的线程分组数量并非随意设定，而是由 GPU 硬件的 SIMD 执行单元宽度直接决定的。

Warp 的概念起源于 NVIDIA 2006 年发布的 Tesla 架构，该架构首次将 GPU 从固定功能流水线转变为可编程的通用计算平台（GPGPU）。"Warp"这个词借用自纺织术语，意为织布机上的经线——多根线同时被编织，恰好类比多个线程并行执行。从此，Warp 成为理解所有 NVIDIA CUDA 程序性能的基础执行单位。

理解 Warp 对 GPU 编程至关重要，因为它是**调度的最小单位**而非单个线程。当程序员写下 `dim3 blockDim(128)` 启动一个 128 线程的 block 时，硬件实际上将其拆分为 4 个 Warp 进行调度。Warp 的执行效率直接决定了 SM（Streaming Multiprocessor）的利用率，进而影响整个 GPU 的吞吐量。

---

## 核心原理

### SIMT 执行模型与 Warp 的物理含义

GPU 采用 **SIMT（Single Instruction, Multiple Threads）** 模型。一个 Warp 内的 32 个线程共享同一个程序计数器（PC），在同一时钟周期内执行完全相同的指令，但各自操作不同的数据（不同的寄存器编号）。SM 内部的 Warp 调度器每个时钟周期从**就绪的 Warp 池**中选取一个 Warp 发射指令。在 Ampere 架构的 SM 中，每个 SM 包含 4 个 Warp 调度器，每调度器每周期可发射 1 条指令，理论上允许同时追踪多达 **64 个活跃 Warp**。

### 分支发散（Branch Divergence）机制与代价

分支发散是 Warp 执行中最重要的性能陷阱。当一个 Warp 内的 32 个线程在执行 `if-else` 时，由于各线程数据不同，部分线程走 `if` 分支，部分走 `else` 分支，但硬件**无法将同一 Warp 分裂成两组独立执行**。

硬件的处理方式是**谓词掩码（Predicate Mask）**：使用一个 32 位的活跃线程掩码（Active Mask），先屏蔽走 `else` 的线程，执行 `if` 分支；再屏蔽走 `if` 的线程，执行 `else` 分支。两段代码**串行**执行。若一个 Warp 内恰好 16 线程走 `if`、16 线程走 `else`，则执行效率降为理论峰值的 **50%**，因为每一时刻只有一半线程在做有效工作。最坏情况下（如 `if (threadIdx.x == 0)`），效率降至 **1/32 ≈ 3.1%**，仅 1 个线程有效工作，其余 31 个被掩码屏蔽空转。

发散代价的计算公式可以表述为：
$$\text{实际吞吐} = \text{峰值吞吐} \times \frac{1}{\text{分支路径数}}$$
其中"分支路径数"是 Warp 内实际存在的不同执行路径数量（最大为 Warp 大小 32）。

### Warp 的创建与线程到 Warp 的映射

线程 ID 到 Warp 的映射遵循严格的线性规则：线程编号 `threadIdx.x + threadIdx.y * blockDim.x + threadIdx.z * blockDim.x * blockDim.y` 计算出线性 ID，再除以 32 得到所属 Warp 编号。例如，对于 `blockDim = (8, 4, 1)` 的 block，线程 `(4, 2, 0)` 的线性 ID 为 `4 + 2×8 = 20`，属于 Warp 0（线程 0–31）。这意味着二维/三维线程组织时，相邻的 `threadIdx.x` 值的线程位于同一 Warp，而不同 `threadIdx.y` 行的线程可能跨越 Warp 边界——这一细节对内存合并访问（Coalescing）有直接影响。

---

## 实际应用

**纹理采样中的 Warp 协作**：在光栅化管线中，像素着色器以 **2×2 像素的 Quad** 为最小单位触发，这是为了计算偏导数 `ddx/ddy` 支持 MipMap 选择。一个典型的 Warp（32 个像素线程）覆盖 8 个这样的 Quad。在三角形边缘处，部分像素位于三角形外（Helper Lane），它们依然执行着色器指令（以提供正确的偏导数），但其写出结果会被丢弃——这是一种不可避免的发散开销。

**GPU 粒子系统的分支优化**：若粒子更新着色器中写有 `if (particle.alive)` 控制更新逻辑，当 Warp 内同时存在存活和死亡粒子时将触发发散。常见优化是**按生命状态排序粒子缓冲区**，使存活粒子在前、死亡粒子在后，确保同一 Warp 内粒子状态一致，消除该分支的发散。Unity 的 VFX Graph 在粒子容量系统设计上就采用了类似的紧凑策略。

**光线追踪中的 Warp 发散**：路径追踪是 Warp 发散的重灾区。同一 Warp 内的 32 条光线弹射后可能击中不同材质（漫反射、镜面、折射），触发不同的材质着色分支。这是 Wavefront Path Tracing（波前路径追踪）架构提出的动机——将同类材质的光线重新分组后批量处理，以恢复 Warp 一致性，相比朴素的 Megakernel 方案可提升 **2–5倍** 吞吐量。

---

## 常见误区

**误区一：认为可以独立控制 Warp 内的单个线程**。初学者常认为 `if (threadIdx.x == 5) { ... }` 只有第 5 号线程在"运行"，其余线程在"休眠"。实际上，当条件不满足的线程被掩码屏蔽时，它们仍然**占用着 SM 的执行时间**——处理器在串行地执行两个分支，掩码控制写出结果，而不是真正跳过指令。这意味着发散分支的延迟是所有路径延迟之和，而非最长路径延迟。

**误区二：将 Warp 大小与 Block 大小混淆**。Block 大小是程序员在 CPU 端指定的逻辑组织（如 `dim3(256)`），而 Warp 大小 32 是硬件固定的物理调度单位。若 Block 大小不是 32 的倍数（如设为 `48`），则最后一个 Warp 只有 16 个有效线程，剩余 16 个线程槽位被**填充为无效线程（Inactive Threads）**，浪费了一半的 Warp 资源。NVIDIA Nsight 工具中的"Warp Efficiency"指标直接反映这一浪费程度。

**误区三：认为分支发散只影响着色器的计算部分**。实际上，发散分支内的**内存访问指令**同样会被串行化，且若不同路径访问非连续地址，还会进一步破坏内存合并（Memory Coalescing），使带宽利用率雪上加霜。一个发散的全局内存读取不仅增加了指令延迟，还可能将 1 次合并事务膨胀为多次分散事务。

---

## 知识关联

**前置概念——GPU 架构概述**：理解 SM（Streaming Multiprocessor）的物理结构是理解 Warp 的基础。SM 内的 CUDA Core 数量（如 Ampere SM 有 128 个 FP32 CUDA Core）与 Warp 大小 32 的关系，解释了为何 SM 可以每周期执行多个 Warp 的指令（128 Core ÷ 32 = 4个Warp并发执行FP32）。

**后续概念——占用率（Occupancy）**：Warp 是占用率计算的基本单元。SM 的最大活跃 Warp 数（如 Ampere 为 64）除以实际驻留 Warp 数得到占用率。Warp 数量受寄存器、共享内存用量约束，是占用率分析的核心变量。

**后续概念——Wave Intrinsics**：Wave Intrinsics（HLSL）或 Warp-level Primitives（CUDA）是在 Warp/Wavefront 粒度上操作的编程接口，如 `WaveActiveSum()`（HLSL）或 `__shfl_sync()`（CUDA）。这些指令允许 Warp 内线程直接交换寄存器数据，完全绕过共享