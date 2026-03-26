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
quality_tier: "B"
quality_score: 46.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.452
last_scored: "2026-03-22"
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

Compute Shader 是 DirectX 11（2009年随 Direct3D 11 引入）和 OpenGL 4.3（2012年）中加入的着色器阶段，其本质是一个**不绑定渲染管线**的 GPU 程序。与 Vertex Shader 或 Fragment Shader 不同，Compute Shader 没有固定的输入（顶点属性、插值器）和固定的输出（颜色缓冲区），它通过 **UAV（Unordered Access View，无序访问视图）** 对任意缓冲区进行读写，使 GPU 成为通用并行计算设备（GPGPU）。

Compute Shader 的出现填补了 GPU 在图形之外的应用空白。在此之前，开发者要做 GPGPU 必须把计算任务"伪装"成渲染调用（Render To Texture），极为繁琐。Compute Shader 使得粒子模拟、物理求解、图像处理、神经网络推理等任务可以直接在 GPU 上以原生方式执行。在技术美术领域，它是实现程序化内容生成、GPU 粒子系统、FFT 海浪等效果的核心工具。

在 Unity 中 Compute Shader 以 `.compute` 文件形式存在，使用 HLSL 语法编写；在 Unreal Engine 中通过 `GlobalShader` 或插件 API 提交；在 GLSL 环境中对应的是 `GL_COMPUTE_SHADER` 类型。

---

## 核心原理

### 线程分组模型：Thread / Group / Dispatch

Compute Shader 的并发单位由三层层级组成。最小单位是**线程（Thread）**，线程按三维方式组织成**线程组（Thread Group）**，线程组的数量由 CPU 端的 `Dispatch(X, Y, Z)` 调用决定。

在 HLSL 中，每个线程组的维度由属性 `[numthreads(Tx, Ty, Tz)]` 声明，例如：

```hlsl
[numthreads(8, 8, 1)]
void CSMain(uint3 id : SV_DispatchThreadID) { ... }
```

此时每个线程组包含 8×8×1 = 64 个线程。若调用 `Dispatch(4, 4, 1)`，则总线程数为 4×4×64 = 1024 个。`SV_DispatchThreadID` 的计算公式为：

> **SV_DispatchThreadID = SV_GroupID × numthreads + SV_GroupThreadID**

`numthreads` 的乘积必须是 **Warp/Wave 大小的整数倍**（NVIDIA GPU 上 Warp = 32，AMD 上 Wave = 64），否则会产生空闲线程造成浪费。常见推荐值为 `[numthreads(64,1,1)]`（线性任务）或 `[numthreads(8,8,1)]`（纹理/图像任务）。

### UAV 与 RWBuffer 读写

Compute Shader 通过 **UAV** 绕过渲染管线直接读写 GPU 资源。在 HLSL 中，对应的绑定类型包括：

- `RWTexture2D<float4>` —— 读写纹理
- `RWStructuredBuffer<MyStruct>` —— 读写结构体数组
- `RWByteAddressBuffer` —— 按字节寻址的原始缓冲区
- `AppendStructuredBuffer` / `ConsumeStructuredBuffer` —— 生产-消费队列

UAV 是**无序**的，即不同线程对同一内存位置的写入顺序不保证。若多个线程需要安全地累加同一计数器，必须使用原子操作：

```hlsl
InterlockedAdd(buffer[0], 1);  // 原子加，保证无竞态
```

常用原子操作包括 `InterlockedAdd`、`InterlockedMin`、`InterlockedMax`、`InterlockedCompareExchange`，均定义在 HLSL 内置函数库中。

### 组内共享内存（Group Shared Memory）

线程组内部可以声明**共享内存（Shared Memory / LDS）**，在 HLSL 中使用 `groupshared` 关键字：

```hlsl
groupshared float4 sharedData[64];
```

NVIDIA Turing 架构中每个线程组最多可用 **48KB** 的共享内存（可配置为最大 96KB，但会减少寄存器）。共享内存的访问延迟约为全局显存的 **100倍以上更快**（~1-4 个时钟周期 vs ~600 时钟周期），因此将高频访问数据先加载进 `groupshared` 再计算（即 Tiling 策略）是 Compute Shader 性能优化的标准手段。

线程组内部的同步通过 `GroupMemoryBarrierWithGroupSync()` 完成，它确保所有线程到达该点后才继续执行，防止读脏数据。

---

## 实际应用

**GPU 粒子系统**：CPU 仅提交一次 `Dispatch` 调用，所有粒子的位置、速度更新均在 Compute Shader 的 `RWStructuredBuffer` 中完成。Unity URP 的 VFX Graph 正是以 Compute Shader 作为底层驱动，支持数百万粒子实时模拟。

**屏幕空间环境光遮蔽（HBAO+）**：深度图采样、方向遮蔽计算、模糊降噪三个阶段均可用 Compute Shader 实现，利用 `groupshared` 缓存深度列，避免重复从全局显存读取，减少 60% 以上的显存带宽消耗。

**FFT 海浪（Gerstner Wave / IFFT）**：Phillips 频谱初始化 → 时域演化 → 2D FFT → 法线生成，全部在 Compute Shader 中完成。Cooley-Tukey FFT 算法中 Butterfly 操作的共享内存访问模式是 Compute Shader 的经典教学案例。海面大小通常为 512×512，使用 `[numthreads(512,1,1)]` 对每行/列做水平/垂直 FFT 各一趟。

**Hi-Z GPU Culling**：在 `RWByteAddressBuffer` 中写入可见物体的 DrawCall 参数，配合 `DrawMeshInstancedIndirect`，将视锥体剔除和遮挡剔除完全搬至 GPU，CPU 端几乎零开销。

---

## 常见误区

**误区一：`numthreads` 越大越好**

很多人认为将线程数设到最大（如 `[numthreads(1024,1,1)]`）会使 GPU 更"忙"从而更快。事实是，线程数过多会导致每个线程可用的寄存器数量减少（寄存器压力上升），GPU 被迫在 Warp 之间频繁切换（Occupancy 虽高但 IPC 下降）。最优 `numthreads` 需要结合具体算法的寄存器用量和共享内存用量通过 Nsight / RenderDoc 的 Occupancy 分析工具来确定，并无通用最大值。

**误区二：UAV 写入顺序无所谓**

Compute Shader 的 UAV 是"无序"的，但"无序"不代表"无害"。多线程写入同一地址如果不使用 `InterlockedAdd` 等原子操作，结果是**未定义行为**，在不同硬件、不同驱动版本上结果可能不一致。很多初学者在写粒子计数器时直接做 `buffer[0]++` 而忽略原子性，导致粒子数目随机丢失。

**误区三：Compute Shader 可以替代所有渲染阶段**

Compute Shader 没有硬件光栅化、深度测试、混合等固定功能，若要输出渲染结果必须额外写入纹理并在后续 Pass 采样。纯 Compute Shader 渲染管线（Visibility Buffer + Compute Shading）虽然可行，但实现复杂度和调试成本远高于传统 Deferred/Forward，在通用游戏项目中并非默认选择。

---

## 知识关联

**前置知识——HLSL 基础**：Compute Shader 的语法直接沿用 HLSL 的数据类型（`float4`、`uint3`）、内置函数（`sin`、`mul`）和绑定语义（`:register(u0)`），掌握 HLSL 基础是理解 UAV 绑定槽位（`u0-u7`）和 SRV 绑定（`t0-tN`）的前提。不了解 HLSL 寄存器语义直接写 Compute Shader 会导致绑定错误难以排查。

**后续概念——程序化网格（Procedural Mesh）**：Compute Shader 可将顶点数据写入 `RWStructuredBuffer<float3>`，CPU 端通过 `GraphicsBuffer` 将其绑定为顶点缓冲区，从而实现**完全在 GPU 端生成和变形的网格**。这是理解程序化网格 GPU 化实现的关键桥梁。

**后续概念——异步计算（Async Compute）**：现代 GPU（如 AMD GCN 及后续架构）拥有独立的 Compute Queue 和 Graphics Queue。将 Compute Shader 提交至 Compute Queue 可与渲染管线**并行执行**，隐藏 GPU 闲置时间。理解 Compute Shader 的线程调度和资源依赖是使用异步计算做帧内 overlap 的直接基础。