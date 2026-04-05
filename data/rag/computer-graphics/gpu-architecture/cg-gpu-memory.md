---
id: "cg-gpu-memory"
concept: "GPU内存层级"
domain: "computer-graphics"
subdomain: "gpu-architecture"
subdomain_name: "GPU架构"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 95.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---


# GPU内存层级

## 概述

GPU内存层级是指从寄存器到VRAM（显存）之间按访问速度和容量分层排列的存储体系，共分为五个主要层级：寄存器（Register）、共享内存（Shared Memory）、L1缓存、L2缓存和VRAM。每一层级的访问延迟相差数十倍甚至数百倍，直接决定了GPU能否充分发挥其数千个并行计算核心的性能。以NVIDIA H100 SXM5为例，其寄存器访问延迟仅为1个时钟周期，而VRAM访问延迟高达约650个周期——两者相差650倍，这意味着一次错误的全局内存访问所造成的停顿，足以"吃掉"数百次寄存器操作的时间窗口。

这一层级体系随GPU架构演进而逐渐清晰。NVIDIA在2006年发布的Tesla架构（G80芯片）中首次引入了程序员可控的共享内存，容量为每个SM 16KB，使开发者能够绕过硬件缓存自行管理片上存储。2012年的Kepler架构（GK110）将L1缓存与共享内存合并为可配置的片上存储池，提供48KB共享内存+16KB L1，或16KB共享内存+48KB L1两档配置。2020年的Ampere架构（A100）进一步将这一统一存储扩展至192KB，并允许最多164KB分配给共享内存。理解内存层级对于CUDA程序优化至关重要：访问模式不当时，实际带宽利用率可低至理论峰值的不足8%（参见《Programming Massively Parallel Processors》，Kirk & Hwu, 2022, 第4版，Morgan Kaufmann）。

---

## 核心原理

### 寄存器：零共享的私有最快存储

寄存器是GPU内存层级中访问延迟最低的存储单元，通常仅需**1个时钟周期**即可完成读写，且不存在缓存未命中的概念——寄存器文件直接硬连线到ALU。每个CUDA线程独占自己的寄存器空间，在NVIDIA Ampere架构（A100）中，每个SM最多拥有**65536个32位寄存器**，折算为256KB容量。若一个SM同时运行2048个线程，则每线程可用寄存器数为65536÷2048 = **32个**；若内核编译后每线程实际使用40个寄存器，则该SM最多并发运行 65536÷40 ≈ 1638 个线程，占理论最大值的80%，影响占用率（Occupancy）。

当线程使用的寄存器数量超过硬件上限（编译器通常设定为255个32位寄存器/线程），溢出数据会被写入**本地内存（Local Memory）**。本地内存在物理上映射至VRAM，延迟骤升至600个周期以上——此现象称为**寄存器溢出（Register Spilling）**。可用NVCC编译选项 `--ptxas-options=-v` 查看每个内核的寄存器使用量，并通过 `__launch_bounds__(maxThreadsPerBlock, minBlocksPerSM)` 提示编译器约束寄存器分配。

### 共享内存：线程块内协作的片上暂存区

共享内存（Shared Memory）位于SM片上，一个线程块（Thread Block）内的所有线程共享同一块共享内存，访问延迟约为**32个时钟周期**（无bank冲突时接近L1缓存速度）。在Ampere架构中，每个SM的L1缓存与共享内存合并为最大**192KB**的统一存储（Unified Data Cache），其中共享内存最多可配置为**164KB**，其余作为L1缓存使用；也可配置为128KB共享内存+64KB L1，或64KB共享内存+128KB L1等多档，通过 `cudaFuncSetAttribute()` 在运行时调整。

共享内存被划分为**32个bank**，每个bank宽度为**4字节**（32位），相邻地址分属不同bank循环排列。当一个Warp（32线程）中的多个线程访问同一bank的**不同地址**时，发生**bank冲突**，硬件将访问串行化为多次操作，带宽最坏情况下降为无冲突时的**1/32**。经典解决方案是在共享内存数组末尾添加1列填充（padding），例如将 `float tile[32][32]` 改为 `float tile[32][33]`，使每行起始地址错开一个bank，彻底消除列方向访问时的冲突。

### L1缓存与L2缓存：硬件透明的中间层

**L1缓存**与共享内存共享同一物理存储池（192KB），由硬件自动管理（对CUDA程序员透明，无法手动控制驱逐策略）。L1的缓存行（Cache Line）大小为**128字节**，这意味着一个Warp若以步幅=1访问连续的32个float（共128字节），仅需1次L1事务；若步幅=2（访问地址不连续），则需要2次事务，带宽利用率下降50%——这正是**合并访问（Coalesced Access）**的核心意义。

**L2缓存**由GPU上所有SM共享，A100配备**40MB** L2，H100扩展至**50MB**。L2访问延迟约为**200个时钟周期**，片上带宽在A100上约为**5 TB/s**（远高于VRAM的1.555 TB/s）。Ampere架构起，L2引入了**持久化缓存（Persistent L2 Cache）**功能：可将最多20MB（A100上）标记为"持久驻留"，通过 `cudaStreamAttrValue` 中的 `accessPolicyWindow` 配置，使频繁重用的只读数据（如权重矩阵）固定在L2中，避免被其他访问驱逐。

---

## 关键公式与代码

### 有效带宽计算公式

评估CUDA内核是否高效利用内存的核心指标是**有效带宽（Effective Bandwidth）**：

$$
BW_{eff} = \frac{(R_{bytes} + W_{bytes})}{t \times 10^9} \quad \text{(GB/s)}
$$

其中 $R_{bytes}$ 为内核读取的总字节数，$W_{bytes}$ 为写入的总字节数，$t$ 为内核执行时间（秒）。将 $BW_{eff}$ 除以设备理论峰值带宽（如A100的1555 GB/s）即得到**带宽利用率**。一个优化良好的矩阵加法内核可达到85%以上的利用率，而未做合并访问的随机读写内核可能低于5%。

### 共享内存矩阵分块乘法（Tiled GEMM）代码片段

```cuda
// 使用共享内存分块优化矩阵乘法，块大小 TILE_SIZE=16
#define TILE_SIZE 16

__global__ void tiledMatMul(float *A, float *B, float *C, int N) {
    // 声明共享内存 tile，添加 +1 列避免 bank 冲突
    __shared__ float As[TILE_SIZE][TILE_SIZE + 1];
    __shared__ float Bs[TILE_SIZE][TILE_SIZE + 1];

    int row = blockIdx.y * TILE_SIZE + threadIdx.y;
    int col = blockIdx.x * TILE_SIZE + threadIdx.x;
    float sum = 0.0f;

    for (int t = 0; t < N / TILE_SIZE; t++) {
        // 协作加载：每线程从 VRAM 加载一个元素到共享内存
        As[threadIdx.y][threadIdx.x] = A[row * N + t * TILE_SIZE + threadIdx.x];
        Bs[threadIdx.y][threadIdx.x] = B[(t * TILE_SIZE + threadIdx.y) * N + col];
        __syncthreads(); // 确保 tile 加载完毕再计算

        for (int k = 0; k < TILE_SIZE; k++)
            sum += As[threadIdx.y][k] * Bs[k][threadIdx.x];
        __syncthreads(); // 确保计算完毕再加载下一 tile
    }
    if (row < N && col < N) C[row * N + col] = sum;
}
```

此优化将每个元素从VRAM的读取次数从 $N$ 次降低至 $N / \text{TILE\_SIZE}$ 次，对于 TILE_SIZE=16，内存访问量减少**16倍**，计算访存比（Arithmetic Intensity）从 $1/4$ FLOP/Byte 提升至 $16/4 = 4$ FLOP/Byte。

---

## 实际应用

### 深度学习推理中的内存层级调度

在大型语言模型（LLM）推理场景中，GPU内存层级的管理直接影响吞吐量。以Transformer的Multi-Head Attention计算为例：FlashAttention算法（Dao et al., 2022，《FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness》）的核心创新正是将注意力矩阵的计算分块在共享内存中完成，避免将大小为 $O(N^2)$ 的注意力矩阵写入VRAM，将VRAM读写量从 $O(N^2)$ 降至 $O(N)$，在A100上实现了相对标准Attention实现**3倍**的速度提升和**10倍**的显存节省。

### 图形渲染管线中的纹理缓存

在图形渲染场景中，纹理单元拥有独立的**纹理缓存（Texture Cache）**，其逻辑上位于L1层级，但针对2D/3D空间局部性优化，采用Morton码（Z-order）排列存储，使相邻像素访问的纹理数据在物理上也连续。NVIDIA Turing架构（RTX 20系列）的每个SM配备32KB纹理缓存，当着色器对同一纹理进行双线性插值时，4个相邻采样点通常命中同一缓存行，有效减少对L2和VRAM的压力。

---

## 各层级带宽对比（A100 SXM4）

| 层级 | 典型延迟 | 容量（每SM / 全局） | 带宽（估算） |
|------|----------|---------------------|--------------|
| 寄存器文件 | ~1 周期 | 256 KB / SM | >20 TB/s（片上） |
| 共享内存 | ~32 周期 | 最大164 KB / SM | ~19 TB/s（片上） |
| L1 缓存 | ~28 周期 | 共享至多192 KB / SM | ~19 TB/s（片上） |
| L2 缓存 | ~200 周期 | 40 MB（全局共享） | ~5 TB/s（片上） |
| VRAM（HBM2e） | ~650 周期 | 40 GB（全局） | 1.555 TB/s |
| PCIe主机内存 | ~数万周期 | 主机RAM容量 | ~32 GB/s（PCIe 4.0 x16） |

---

## 常见误区

**误区一：共享内存越大越好，应始终配置最大值。**  
实际上，共享内存与L1缓存共享同一物理存储池。将共享内存配置为164KB意味着L1仅剩28KB。若内核访问模式具有良好时间局部性但不使用显式共享内存（如不规则图访问），L1命中率对性能更关键，此时应缩减共享内存分配，让硬件L1发挥作用。NVIDIA官方建议通过 `cuda-profiler` 对比不同配置下的 `l1tex__t_sectors_pipe_lsu_mem_global_op_ld.sum` 指标来决策。

**误区二：VRAM带宽越高，程序运行越快。**  
带宽利用率取决于访问模式。随机、非合并的全局内存访问会导致每次事务传输128字节缓存行但只使用其中4字节（1个float），有效利用率仅为3.1%。此时即便VRAM带宽提升10倍，实际性能也几乎不变——瓶颈在于**延迟**而非带宽。真正的瓶颈识别需区分"带宽绑定（Bandwidth-bound）"与"延迟绑定（Latency-bound）"两种模式。

**误区三：寄存器溢出是小概率事件，无需关注。**  
在处理高维特征的着色器或复杂CUDA内核中，寄存器溢出相当常见。以Unreal Engine 5的Lumen全局光照着色器为例，其部分Pass在早期版本中因寄存器溢出导致实际性能低于预期40%，通过代码重构拆分内核后才得到解决。每次寄存器溢出到本地内存的读写延迟约为650个周期，等同于一次VRAM访问。

---

## 知识关联

### 与GPU占用率（Occupancy）的关系

GPU占用率 =