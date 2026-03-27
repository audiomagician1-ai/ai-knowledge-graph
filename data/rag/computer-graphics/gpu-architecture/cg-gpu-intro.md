---
id: "cg-gpu-intro"
concept: "GPU架构概述"
domain: "computer-graphics"
subdomain: "gpu-architecture"
subdomain_name: "GPU架构"
difficulty: 1
is_milestone: false
tags: ["基础"]

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


# GPU架构概述

## 概述

GPU（图形处理器）是一种专门为大规模并行计算设计的处理器，其架构与CPU存在根本性的设计哲学差异。CPU的设计目标是以最低延迟执行单条复杂指令序列，而GPU的设计目标是以最高吞吐量同时处理数千条相似指令。现代高端GPU如NVIDIA RTX 4090拥有16,384个CUDA核心，而顶级服务器CPU通常只有64-128个物理核心，这个数量级的差距直接体现了两者设计取向的不同。

GPU的诞生源于3D图形渲染的计算需求。1999年NVIDIA发布GeForce 256时首次引入"GPU"这一术语，彼时其主要功能是硬件变换和光照计算（T&L）。2006年NVIDIA推出的G80架构（GeForce 8800）是历史性转折点——它引入了统一着色器架构，将顶点着色器和像素着色器合并为通用流处理器，为后来的GPGPU（通用GPU计算）奠定了基础。

理解GPU架构对图形开发者的意义在于：它直接决定了着色器代码的执行效率、Draw Call的性能开销以及内存带宽的利用率。同样一段HLSL代码，理解GPU架构的开发者可以通过减少分支和优化内存访问模式将性能提升数倍。

## 核心原理

### CPU与GPU的芯片面积分配差异

CPU芯片中大约50%以上的晶体管用于缓存（L1/L2/L3）和分支预测逻辑，目的是减少单线程的执行延迟。GPU则反其道而行之：NVIDIA Ada Lovelace架构（RTX 40系列）中，绝大部分晶体管用于算术逻辑单元（ALU），缓存相对较小。GPU依靠"以并发隐藏延迟"的策略——当一组线程在等待内存数据时，GPU立即切换到另一组就绪的线程继续执行，从而将内存延迟掩盖在计算中。这种设计要求应用程序提供足够多的并行线程（通常数万至数十万个）才能充分利用GPU资源。

### SIMT执行模型

GPU使用SIMT（Single Instruction, Multiple Threads，单指令多线程）执行模型。SIMT与CPU上的SIMD（单指令多数据）既有联系又有本质区别：SIMD要求程序员显式地用向量化指令操作数据，而SIMT允许程序员编写看起来像普通标量代码的着色器，GPU硬件自动将多个线程的相同指令打包成宽向量操作执行。

在NVIDIA架构中，32个线程组成一个**Warp**，这32个线程在同一时钟周期内执行完全相同的指令，只是操作不同的数据。在AMD架构中对应单元称为**Wavefront**，传统上包含64个线程（RDNA架构之后也支持32线程波前）。当Warp内的线程遇到`if-else`分支且各线程的判断结果不同时，GPU不得不先让满足条件的线程执行`if`分支（其他线程屏蔽），再让另一批线程执行`else`分支，两段代码串行执行，这一现象称为**Warp分歧（Warp Divergence）**，是GPU性能损失的主要原因之一。

### SM/CU的层级结构

NVIDIA GPU的基本计算单元称为**流多处理器（SM，Streaming Multiprocessor）**，AMD对应称为**计算单元（CU，Compute Unit）**。以NVIDIA Ampere架构的SM为例，每个SM包含：128个CUDA核心（FP32）、4个Tensor核心、1个RT核心（光线追踪）、共享内存/L1缓存（最大128KB可配置）以及寄存器文件（每个SM最多65536个32位寄存器）。整块GPU由数十个SM组成，所有SM共享L2缓存和显存带宽。寄存器文件是每个线程私有的最快存储，每个线程分配的寄存器数量越多，SM能同时驻留的线程数量（**占用率，Occupancy**）就越低，这是性能调优中必须权衡的关键矛盾。

## 实际应用

**游戏渲染中的Draw Call开销**：每次CPU向GPU提交一个Draw Call时，涉及状态切换、命令编码和驱动验证，这部分工作在CPU端串行执行。理解GPU的大规模并行特性后，开发者会将数千个相似网格合并为一次Instanced Draw Call，让GPU并行处理所有实例，而非让CPU反复调用。现代引擎如Unreal Engine 5的Nanite系统正是将数百万三角形的绘制压缩为有限的GPU端遍历操作，绕开了Draw Call瓶颈。

**着色器中的分支优化**：在像素着色器中编写`if (roughness > 0.5)`这样的条件判断，如果同一个2×2像素块内的四个线程（构成一个Quad）的roughness值跨越阈值两侧，则会触发Warp分歧，实际执行时间等于两条分支时间之和。有经验的图形工程师会用`lerp()`或`step()`等数学函数替代分支，或将不同材质的物体合并批次以保证Warp内线程走相同分支路径。

**Compute Shader的线程组设计**：在DX12/Vulkan的Compute Shader中，`numthreads`属性直接对应Warp/Wavefront的大小。将线程组X维度设置为32的倍数（NVIDIA）或64的倍数（AMD传统架构）可以避免产生空闲的"尾部线程"，保证SM的满负荷运转。

## 常见误区

**误区一：GPU核心数量越多性能越强**。GPU核心数只代表峰值FP32算力，实际性能还受限于内存带宽、缓存容量和特定任务的占用率。GTX 1080拥有2560个CUDA核心，但在带宽密集型任务上，内存带宽为484 GB/s的RTX 3080Ti表现远优于带宽仅320 GB/s的GTX 1080，尽管后者在某些场景核心利用率更高。片面以核心数比较不同架构的GPU没有意义。

**误区二：着色器中的循环总是比分支快**。这一说法在CPU时代有一定道理，但在GPU上固定次数的循环若展开后导致寄存器用量激增，会大幅降低SM的线程占用率，反而比一个不引起分歧的条件判断性能更差。实际情况取决于寄存器压力与分歧程度的综合权衡。

**误区三：GPU显存越大帧率越高**。显存容量决定的是能驻留的资源上限（纹理、Mesh、RT加速结构等），显存带宽才是每帧数据传输效率的瓶颈。在未超出显存容量的情况下，将显存从8GB提升到16GB对帧率几乎没有影响，而带宽从400 GB/s提升到700 GB/s则在带宽受限场景下有显著提升。

## 知识关联

本文介绍的SM/Warp概念是学习**Warp/Wavefront**执行细节的直接前置知识——后者会深入分析Warp调度器的工作方式、Occupancy计算公式（`Occupancy = Active Warps / Maximum Warps per SM`）以及Bank Conflict对共享内存的影响。GPU的层级存储结构（寄存器→共享内存→L1→L2→显存）是**GPU性能分析**中使用NSight等工具定位瓶颈时的核心分析框架。SIMT模型与着色器编程范式的对应关系，是理解**Compute Shader**中线程组、线程ID映射以及同步原语`GroupMemoryBarrierWithGroupSync()`语义的必要背景。**GPU硬件管线**部分会将本文的通用并行架构知识具体化到顶点处理、光栅化、像素着色的固定功能单元上，揭示哪些阶段在SM上运行、哪些阶段由专用硬件完成。