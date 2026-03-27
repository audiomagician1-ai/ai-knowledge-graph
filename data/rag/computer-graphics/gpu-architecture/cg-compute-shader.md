---
id: "cg-compute-shader"
concept: "Compute Shader"
domain: "computer-graphics"
subdomain: "gpu-architecture"
subdomain_name: "GPU架构"
difficulty: 3
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 49.8
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.424
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# Compute Shader

## 概述

Compute Shader（计算着色器）是GPU上执行通用并行计算的可编程阶段，与渲染管线中的顶点着色器、片段着色器不同，它不绑定任何固定的渲染输出目标，可以读写任意结构的缓冲区和纹理资源。Compute Shader最早随DirectX 11（2009年）正式引入图形API，对应HLSL中的`cs_5_0`着色器模型；OpenGL则通过4.3版本（2012年）将其纳入核心规范，GLSL中以`layout(local_size_x, local_size_y, local_size_z)`声明线程组维度。

从硬件执行角度来看，Compute Shader绕过了光栅化、深度测试等渲染固定功能单元，直接调度GPU的通用计算单元（CUDA Core / Shader Processor）。这使它非常适合图像后处理（如屏幕空间环境光遮蔽SSAO）、物理模拟、GPU排序、光线追踪前处理等大规模并行任务。Compute Shader的重要性还体现在它是GPU Driven Rendering和机器学习推理在图形引擎中落地的基础执行单元。

## 核心原理

### 线程层级模型：Thread、Group与Dispatch

Compute Shader的执行单元由三层层级构成。最顶层是**Dispatch**调用，形式为`Dispatch(X, Y, Z)`，指定线程组（Thread Group）在三个维度上的数量；中间层是**线程组**（Thread Group），每个线程组在GPU上作为一个调度原子被分配到同一个计算单元（Compute Unit / SM）中执行；最底层是**线程**（Thread），在HLSL中以`SV_DispatchThreadID`、`SV_GroupThreadID`、`SV_GroupID`三种内置语义区分线程的全局ID、组内ID和组ID。

线程组的大小上限在DX11/DX12中为每轴1024，且三轴乘积不超过1024。实践中常见的配置是`[numthreads(8, 8, 1)]`（适合2D图像处理）或`[numthreads(64, 1, 1)]`（适合一维数组处理）。线程组大小的选择直接影响GPU Occupancy：太小会导致寄存器和共享内存利用率低，太大会因寄存器压力降低并行Warp数量。

### 共享内存（Group Shared Memory）

同一线程组内的所有线程可以访问一块**组共享内存**（Group Shared Memory，在HLSL中以`groupshared`关键字声明，在GLSL中称为`shared`）。这块内存位于片上L1/Scratch Pad，访问延迟约为全局显存的1/10到1/100。在NVIDIA架构上，每个SM的共享内存容量通常为32KB至164KB（Ampere架构为164KB可配置），超出则导致Spill到全局内存，性能急剧下降。

共享内存的典型用途是**分块（Tile）数据预取**：在图像卷积计算中，将一个16×16像素的Tile连同其Halo区域一次性加载进共享内存，避免同一像素被重复从全局内存读取多次，从而将内存带宽消耗降低数倍。

### 同步原语：Barrier与原子操作

Compute Shader提供两类关键同步原语：

**内存屏障（Barrier）**：`GroupMemoryBarrierWithGroupSync()`在HLSL中同时实现**执行同步**（等待组内所有线程到达该点）和**内存可见性同步**（确保共享内存写入对所有线程可见）。仅需内存可见性而不需要执行同步时，可使用`GroupMemoryBarrier()`以减少开销。DeviceMemoryBarrier系列则用于全局内存的可见性保证。

**原子操作（Atomic）**：HLSL提供`InterlockedAdd`、`InterlockedMin`、`InterlockedMax`、`InterlockedCompareExchange`等原子指令，作用于`RWByteAddressBuffer`或`RWStructuredBuffer`中的32位整型数据。原子操作代价高昂，在数百线程同时竞争同一地址时会形成严重的内存访问序列化，因此常见的优化是先在共享内存中做组内规约（Reduction），再对全局内存执行一次原子写入。

## 实际应用

**GPU粒子系统**：粒子的物理更新（位置、速度积分）完全在Compute Shader中完成，粒子数据存储在`RWStructuredBuffer`中，每帧通过`Dispatch(ceil(N/64), 1, 1)`调度，N为粒子数量。死亡粒子的回收和新粒子的发射使用`InterlockedAdd`维护一个GPU端的活跃粒子计数器，避免CPU回读。

**Hierarchical Z-Buffer（Hi-Z）生成**：深度图的Mipmap逐级降采样通过Compute Shader实现，每一级取四个子像素的最大深度值写入下一级。`[numthreads(8,8,1)]`配合共享内存缓存当前Tile，使每个像素仅从全局内存读取一次，整个1024×1024深度图的Hi-Z构建耗时通常不超过0.1ms。

**前缀和（Prefix Sum / Scan）**：GPU排序（如GPU Radix Sort）的核心子算法，Compute Shader实现Work-Efficient Parallel Scan算法（Blelloch 1990），在Up-Sweep和Down-Sweep两个阶段中共使用O(N)次加法和O(log N)次同步，每次同步使用`GroupMemoryBarrierWithGroupSync()`确保正确性。

## 常见误区

**误区一：认为`GroupMemoryBarrierWithGroupSync()`可以跨线程组同步**。该函数的作用域严格限于单个线程组内部，不同线程组之间在同一个Dispatch调用中无法直接同步。跨组通信必须通过全局内存的原子操作间接实现，或拆成两次独立的Dispatch调用，中间插入API层的资源屏障（Resource Barrier / Pipeline Barrier）。

**误区二：认为线程组越大越好**。增大线程组固然可以在组内共享更多数据，但每个线程组的寄存器总用量等于`numthreads × 单线程寄存器数`。当总寄存器超出SM容量时，GPU无法同时在同一SM上调度多个Wave/Warp，Occupancy下降，延迟隐藏能力减弱，实测吞吐量反而降低。RTX 3090（Ampere）每个SM拥有65536个32位寄存器，若每线程使用32个寄存器，则每个线程组最多可包含2048个线程。

**误区三：混淆`SV_GroupThreadID`与`SV_DispatchThreadID`**。前者是线程在本组内的局部坐标（范围为`[0, numthreads-1]`），用于共享内存的索引；后者是全局唯一坐标，用于访问全局缓冲区。两者混用会导致越界写入或多线程数据覆盖，且此类Bug往往在小数据集上不可复现，在大规模Dispatch时才触发。

## 知识关联

从**GPU架构概述**出发，Compute Shader直接对应其中的SIMT执行模型：一个线程组在GPU上以若干Warp（NVIDIA，32线程）或Wave（AMD，64线程）的形式执行，共享内存即SM内的LDS（Local Data Share）。理解SIMT的分支发散（Divergence）规则对编写高效Compute Shader至关重要——组内线程的条件分支若不一致，会导致两条分支路径串行执行，吞吐减半。

掌握Compute Shader后，可以进入**异步计算**（Async Compute）的学习：现代GPU（如GCN架构起）具有独立的Compute Queue，Compute Shader可与图形队列的渲染任务在时间上重叠执行，需要理解队列间同步的Fence/Semaphore机制。进而在**GPU Driven Pipeline**中，Compute Shader承担场景剔除（Culling）、间接绘制参数生成（`ExecuteIndirect` / `DrawIndirectCommand`）的角色，是实现百万级Draw Call的关键技术。**着色器互操作**则涉及Compute Shader与光线追踪着色器（DXR）之间的数据共享与同步策略。