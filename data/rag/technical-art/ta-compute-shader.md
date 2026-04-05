---
id: "ta-compute-shader"
concept: "Compute Shader"
domain: "technical-art"
subdomain: "shader-dev"
subdomain_name: "Shader开发"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
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


# Compute Shader

## 概述

Compute Shader（计算着色器）是一种运行在GPU上、但不参与传统渲染管线的可编程着色阶段，专门用于执行通用并行计算任务（GPGPU，General-Purpose GPU Computing）。与顶点着色器或片元着色器不同，Compute Shader 没有固定的输入（顶点、纹理坐标）和固定的输出（颜色缓冲），而是通过可读写的 UAV（Unordered Access View，无序访问视图）自由读写任意缓冲区或纹理。

Compute Shader 在 DirectX 11（2009年随 Direct3D 11 发布）中作为正式特性引入，HLSL 中的 Shader Model 5.0 规范定义了其完整语义。OpenGL 对应的是 Compute Shader（4.3版本，2012年）；Vulkan 和 Metal 也有等价实现。在技术美术领域，Compute Shader 被广泛用于 GPU 粒子系统、程序化纹理生成、物理模拟预计算、后处理特效以及蒙皮动画计算等场景，将原本在 CPU 端串行执行的逻辑迁移到 GPU 的数千个并行核心上。

理解 Compute Shader 的关键在于掌握 GPU 的线程分组模型：GPU 并不像 CPU 那样顺序执行指令，而是将任务拆分为数量庞大的轻量级线程，由硬件调度器同时执行。Compute Shader 让开发者可以直接控制这种并行结构，而不必将计算"伪装"成渲染操作（旧时代常用的"渲染到纹理"黑客技巧）。

---

## 核心原理

### 线程层次结构：Thread、Group 与 Dispatch

Compute Shader 的执行单位是**线程（Thread）**，线程被组织为**线程组（Thread Group）**，线程组再由 CPU 端的 `Dispatch(X, Y, Z)` 调用来批量启动。在 HLSL 中，每个线程组的线程数量通过 `[numthreads(X, Y, Z)]` 属性声明，三维结构最大为 `[numthreads(1024, 1, 1)]` 或 `[numthreads(32, 32, 1)]` 等（总数上限为 1024）。实际执行时，NVIDIA GPU 以 32 个线程为一组（称为 **Warp**）调度，AMD GPU 以 64 个线程为一组（称为 **Wavefront**）调度；`numthreads` 应尽量是这两个数字的倍数，否则会出现空闲线程浪费带宽。

每个线程可通过以下系统语义值定位自身：
- `SV_GroupID`：当前线程组在 Dispatch 网格中的三维坐标
- `SV_GroupThreadID`：线程在当前线程组内的局部坐标
- `SV_DispatchThreadID`：全局线程坐标，等于 `SV_GroupID * numthreads + SV_GroupThreadID`
- `SV_GroupIndex`：线程在组内的一维扁平化下标

### UAV 读写与 RWTexture/RWStructuredBuffer

Compute Shader 最核心的 I/O 机制是 UAV。在 HLSL 中声明为 `RWTexture2D<float4>`、`RWStructuredBuffer<MyStruct>` 或 `RWByteAddressBuffer` 等类型，支持任意线程的随机读写。与之对比，普通的 `Texture2D` 在 Compute Shader 中仍可绑定为 SRV（只读视图）。需要注意：**多个线程同时写同一地址会产生竞争（race condition）**，因此 HLSL 提供了原子操作函数，如 `InterlockedAdd`、`InterlockedMax`、`InterlockedCompareExchange` 等，用于安全地累加计数器或进行无锁算法实现。

### 共享内存（GroupShared Memory）

线程组内的线程可以共享一块高速的片上 SRAM，即 `groupshared` 内存（NVIDIA 架构中称为 Shared Memory 或 L1 Cache 的可配置部分）。典型声明如下：

```hlsl
groupshared float sharedData[64];
```

其大小上限通常为 **32KB**（DX11 规范保证最低 32KB）。访问 `groupshared` 内存的延迟约为全局显存的 **1/100**，因此前缀和（Prefix Sum/Scan）、直方图统计、卷积核缓存等算法都依赖它来减少全局内存带宽压力。使用 `GroupMemoryBarrierWithGroupSync()` 可在线程组内设置同步屏障，确保所有线程写入完成后再进行读取。

---

## 实际应用

**GPU 粒子系统**：在 Unity/UE 中，粒子的位置、速度、生命周期存储在 `RWStructuredBuffer<ParticleData>` 中。每帧 Dispatch 一个线程处理一个粒子的物理积分（速度 += 重力 * dt，位置 += 速度 * dt），完全绕过 CPU 数组遍历，百万粒子仍可实时运行。

**屏幕空间环境遮蔽（SSAO）的模糊 Pass**：SSAO 生成的噪点遮蔽图需要做分离式高斯模糊。Compute Shader 先在横向 Pass 中将一行像素的采样值缓存到 `groupshared float`，再做纵向 Pass，相比两个全屏四边形 Draw Call 减少了约 40% 的纹理采样次数。

**蒙皮动画预计算（GPU Skinning）**：角色的骨骼矩阵调色板传入 StructuredBuffer，Compute Shader 对每个顶点并行执行蒙皮混合矩阵乘法，结果写入 `RWByteAddressBuffer`，后续顶点着色器直接读取，避免 CPU 端的顶点流操作。

**直方图生成**：后处理自动曝光需要统计帧画面的亮度直方图（通常 256 个桶）。Compute Shader 利用 `groupshared uint histogram[256]` 在组内累加，再用 `InterlockedAdd` 合并到全局 UAV，整帧只需一次 Dispatch，无需 CPU 回读。

---

## 常见误区

**误区一：认为 Dispatch 的线程数越多越快**
实际上，过多的线程组会导致 GPU 资源争抢（寄存器、共享内存溢出），反而降低 Occupancy（占用率）。例如将 `numthreads` 设为 `[numthreads(1024, 1, 1)]` 时，每个线程组需要占用更多寄存器，可能使 SM（Streaming Multiprocessor）上同时驻留的 Warp 数量从 8 降至 2，GPU 利用率反而下降。应使用 NVIDIA Nsight 或 RenderDoc 的 Occupancy 分析工具校验。

**误区二：把 UAV 写入当作同步操作**
Compute Shader 中的全局内存写入在不同线程组之间**没有顺序保证**，也没有跨 Dispatch 的自动同步。若需要上一个 Dispatch 的写入结果在下一个 Dispatch 中可见，必须在 CPU 端使用 `ID3D11DeviceContext::Dispatch` + UAV 资源屏障（DX12/Vulkan 中的 `ResourceBarrier` 或 `vkCmdPipelineBarrier`），而不是依赖代码编写的先后顺序。

**误区三：在 Compute Shader 中使用大量分支会自动优化**
GPU 的 Warp/Wavefront 机制要求同一组 32/64 个线程执行相同的指令路径。若 `if-else` 分支导致组内线程分歧（Divergence），两个分支会被串行执行，吞吐量降至理论峰值的 1/2 甚至更低。应尽量将分支条件设计为 **组内一致**（Group-Uniform），或使用位掩码、查找表替代复杂条件判断。

---

## 知识关联

**前置知识**：学习 Compute Shader 前需要具备 HLSL 基础，包括变量类型（`float4`、`uint3`）、寄存器绑定（`register(u0)`、`register(t0)`）以及内置函数（`dot`、`lerp`、`GroupMemoryBarrierWithGroupSync`）的用法，否则无法理解 UAV 的声明语法和线程同步语义。

**后续延伸——程序化网格**：掌握 Compute Shader 后，可进一步学习程序化网格生成。通过 Compute Shader 输出顶点/索引数据到 `RWByteAddressBuffer`，再绑定为顶点缓冲区，可实现完全在 GPU 上生成 Marching Cubes 等地形网格，无需 CPU 端的几何数据上传。

**后续延伸——异步计算**：DX12 和 Vulkan 支持将 Compute Shader 放在独立的**异步计算队列（Async Compute Queue）**中执行，与图形队列并行运行，充分利用 GPU 中专用的 Compute CU（Compute Unit）。理解 Compute Shader 的资源绑定模型和同步机制，是进一步掌握异步计算的前提，因为异步计算的难点正是正确管理跨队列的资源竞争与信号量同步。