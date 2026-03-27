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

Compute Shader（计算着色器）是运行在GPU上、不依赖图形管线固定阶段（顶点→光栅化→片段）的通用计算程序。它由微软在Direct3D 11（2009年）中正式引入，以"Compute Shader 5.0"规范落地，随后被OpenGL 4.3（2012年）和Vulkan/Metal采纳。与Vertex Shader或Pixel Shader不同，Compute Shader不产生任何渲染输出，它直接读写缓冲区（Buffer）或纹理（Texture），输出结果由开发者自行定义。

Compute Shader的意义在于它打破了GPU"只能做渲染"的认知边界。在引入它之前，开发者若想用GPU加速物理模拟或图像处理，必须将数据"伪装"成纹理坐标，借用片段着色器间接计算——这种技巧被称为GPGPU hack。Compute Shader提供了专用的UAV（Unordered Access View）读写接口、线程间通信机制和原子操作，使GPU通用计算成为图形API的一等公民。

---

## 核心原理

### 线程组（Thread Group）模型

Compute Shader的执行单元是**线程组（Thread Group，HLSL中称为`numthreads`）**。调度时，CPU通过`Dispatch(X, Y, Z)`指令发出一个三维网格，其中X×Y×Z指定线程组的数量。每个线程组内部又有`numthreads(tx, ty, tz)`个线程，因此总线程数为：

```
总线程数 = X × Y × Z × tx × ty × tz
```

每个线程拥有三个内置语义标识符：
- `SV_GroupID`：线程组在调度网格中的三维坐标
- `SV_GroupThreadID`：线程在其所在线程组内的局部坐标
- `SV_DispatchThreadID`：全局线程坐标，等于 `SV_GroupID × numthreads + SV_GroupThreadID`

在HLSL中，线程组大小上限为 **1024个线程**（D3D11/D3D12规范），且单一维度不超过1024，Z维度不超过64。Metal的规范略有不同，M1 GPU的线程组最大为1024线程。这些限制直接影响算法分块设计。

### 组共享内存（Group Shared Memory）

线程组内的所有线程可以访问一块**组共享内存（Group Shared Memory，HLSL关键字 `groupshared`，GLSL中为 `shared`）**。D3D11规定每个线程组最多使用 **32KB** 的共享内存，这是决定每个线程组能缓存多少数据的硬性上限。

共享内存的典型用途是减少全局显存带宽消耗。例如在计算图像模糊时，若每个线程独立从全局纹理采样，相邻线程会大量重复采样同一像素；改用共享内存后，线程组先协作将一个图块载入共享内存，再各自读取本地数据，带宽消耗可降低数倍。

### 同步原语

线程组内的线程并非完全顺序执行，必须用同步指令协调。HLSL提供了三个层级的屏障：

- **`GroupMemoryBarrier()`**：仅同步共享内存访问，确保所有线程完成对共享内存的写入后，其他线程才能读取。
- **`DeviceMemoryBarrier()`**：同步UAV（全局缓冲区/纹理）访问。
- **`AllMemoryBarrier()`**：同时同步共享内存和设备内存。

若在屏障后还需等待**所有线程到达该点**（线程同步点，而非仅内存可见性），需使用带`Sync`后缀的版本：`GroupMemoryBarrierWithGroupSync()`。这两个概念经常被混淆：内存屏障保证"数据可见"，而`WithGroupSync`额外保证"执行位置对齐"。

**原子操作**（`InterlockedAdd`、`InterlockedCompareExchange`等）作用于共享内存或UAV的单个32位整数，保证多线程并发写入时不产生数据竞争，但代价是串行化该内存位置的访问，滥用会造成严重的性能瓶颈。

---

## 实际应用

**后处理效果**：屏幕空间环境光遮蔽（SSAO）、景深（DoF）、Bloom等效果用Compute Shader实现时，可利用共享内存缓存局部像素，显著减少纹理采样次数。Unity的URP管线的Bloom实现从片段着色器迁移到Compute Shader后，在移动端带宽降低约30%。

**粒子系统模拟**：将100万个粒子的位置和速度存入StructuredBuffer，每帧用Compute Shader的`Dispatch(1000000/64, 1, 1)`更新状态，完全在GPU侧完成，无需回读CPU。粒子排序（用于透明度混合）也可通过GPU Bitonic Sort在Compute Shader中实现，其复杂度为 O(n log²n)，适合大规模并行。

**生成式内容**：程序化地形生成中，Marching Cubes算法天然适合Compute Shader并行化——每个线程组处理一个体素块，共享内存存储该块的SDF值，最终将生成的三角形追加到AppendStructuredBuffer中，直接供后续渲染使用。

**压缩与解压**：BC7纹理压缩算法（块大小4×4像素）可在Compute Shader中并行处理，每个线程组处理一个4×4块，实时压缩运行时生成的纹理，这在传统片段着色器管线中几乎无法实现。

---

## 常见误区

**误区一：线程数越多、线程组越大，性能越好**
实际上，线程组大小必须是GPU Warp/Wave大小（NVIDIA为32，AMD RDNA为32或64）的整数倍，否则会产生"尾部Warp"浪费。更关键的是，`numthreads`越大，每个线程组占用的寄存器和共享内存越多，GPU能同时调度的线程组数量（Occupancy）反而下降。通常从`numthreads(64, 1, 1)`或`numthreads(8, 8, 1)`开始调优，而非直接用1024。

**误区二：`GroupMemoryBarrier()`和`GroupMemoryBarrierWithGroupSync()`可以互换**
前者只保证内存操作的可见性（数据写入刷新），不保证线程执行进度对齐。若线程A在屏障前写入共享内存、线程B在屏障后读取，只有`WithGroupSync`才能确保B等到A真正完成写入后再继续执行。仅使用`GroupMemoryBarrier()`在某些GPU驱动上可能恰好正确运行，但存在未定义行为。

**误区三：Compute Shader可以跨线程组共享数据**
`groupshared`内存的作用域严格限定在单个线程组内。不同线程组之间唯一的通信方式是通过全局UAV缓冲区，并在下一次Dispatch或显式屏障（Vulkan中的Pipeline Barrier）之后才能保证可见。试图让线程组之间通过共享内存"协调"是无效的，这与CUDA的`__shared__`语义一致。

---

## 知识关联

**前置概念——GPU架构概述**：理解Compute Shader需要知道GPU由大量SIMD执行单元（SM/CU）组成，每个SM/CU同时调度多个Warp/Wavefront。线程组的`numthreads`设计本质上是在为SM/CU的Warp调度器提供足够的并行度以隐藏内存延迟。

**后续概念——异步计算**：Compute Shader可以提交到独立的Compute Queue，与图形队列上的渲染命令并行执行，这是"异步计算"的硬件基础。理解线程组调度和资源屏障是掌握异步计算中队列间同步（Semaphore/Fence）的前提。

**后续概念——GPU Driven Pipeline**：现代GPU Driven渲染中，剔除（Culling）、LOD选择、DrawCall生成均在Compute Shader中完成，结果写入IndirectBuffer，再由`ExecuteIndirect`/`DrawIndirect`驱动渲染。Compute Shader的UAV读写能力和原子操作是这一架构的直接支撑。

**后续概念——着色器互操作**：Compute Shader的输出（StructuredBuffer、RWTexture2D）可以直接绑定为后续图形着色器的输入，无需经过CPU中转，这种"着色器间数据传递"构成了现代帧图（Frame Graph）设计的基础。