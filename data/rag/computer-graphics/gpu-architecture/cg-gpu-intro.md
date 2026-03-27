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

GPU（图形处理单元）是一种专为大规模并行计算设计的处理器，其架构与CPU存在根本性的差异。CPU通常拥有4到64个强大的计算核心，每个核心配备大容量缓存和复杂的分支预测电路，专为处理串行逻辑密集型任务优化。而现代GPU（例如NVIDIA RTX 4090）拥有超过16,384个较小的CUDA核心，这些核心以高度并行的方式同时处理成千上万个线程。

GPU的独立发展历史可追溯至1999年，NVIDIA发布GeForce 256时首次提出"GPU"这一术语，并将几何变换与光照计算（T&L）集成到硬件中。此前，图形加速卡只能处理简单的2D渲染，几何运算依赖CPU完成。2006年NVIDIA G80架构引入统一着色器模型，将顶点着色器与像素着色器合并为通用计算单元，这标志着现代GPU可编程并行架构的成熟。

GPU之所以重要，是因为图形渲染本质上是对数百万个像素或顶点执行相同数学操作的任务，这种"数据并行"特性与GPU的硬件设计天然契合。同时，深度学习训练中矩阵乘法的大规模并行需求，使GPU超越图形领域成为AI计算的核心基础设施。

## 核心原理

### CPU与GPU的架构对比

CPU的芯片面积主要被控制逻辑、分支预测单元和多级缓存（L1/L2/L3）占据，实际ALU（算术逻辑单元）的比例不足芯片面积的30%。GPU则相反，其大部分晶体管用于ALU阵列，缓存容量相对较小——例如NVIDIA A100 GPU的L2缓存为40MB，而其计算单元数量高达6912个。这种设计选择意味着GPU擅长吞吐量密集型计算，但对于需要大量条件分支和随机内存访问的串行代码，性能反而不如CPU。

CPU采用乱序执行（Out-of-Order Execution）和超标量技术，单个核心可同时执行多条不相关指令，延迟可低至几个纳秒。GPU则采用延迟隐藏（Latency Hiding）策略：当一组线程等待内存访问时，硬件调度器立即切换到另一组准备好的线程执行，从而掩盖内存延迟。这一机制要求GPU同时驻留大量活跃线程，通常单个流多处理器（SM）需要驻留数百到数千个线程才能充分隐藏延迟。

### SIMT执行模型

SIMT（Single Instruction, Multiple Threads，单指令多线程）是GPU执行的基本模型，由NVIDIA在2007年G80架构中正式提出。与CPU的SIMD（单指令多数据）不同，SIMT在编程模型上让每个线程看起来独立执行，但硬件层面实际上将32个线程（称为一个Warp）捆绑在一起，同步执行同一条指令。

SIMT的执行公式可以简化描述为：若Warp中N个线程执行分支A，(32-N)个线程执行分支B，则GPU需要执行分支A和分支B两次，但每次只有对应的线程处于活跃状态（Active Mask = 1），其余线程被屏蔽（Predicated Off）。这种现象称为**Warp Divergence（Warp分歧）**，会导致执行效率降低至最坏情况下的1/32。

### 流多处理器（SM）与线程层次

GPU的基本计算单元是流多处理器（Streaming Multiprocessor，SM）。以NVIDIA Ampere架构为例，一个SM包含128个CUDA核心、4个Tensor Core、1个RT Core、256KB寄存器文件和192KB可配置的L1缓存/共享内存。整块GPU由数十个SM组成，例如A100包含108个SM。

线程在GPU中按三级层次组织：Thread（线程）→ Thread Block（线程块）→ Grid（网格）。一个Thread Block在同一个SM内执行，Block内的线程可通过共享内存（Shared Memory）相互通信，通信延迟约为1-5个时钟周期。不同Block之间无法直接通信，必须通过全局内存（Global Memory，延迟约200-800个时钟周期）中转。

## 实际应用

**光栅化渲染管线**：在传统游戏渲染中，GPU对屏幕上每个像素并行执行片元着色器（Fragment Shader）。以1080p分辨率（1920×1080 = 2,073,600像素）为例，GPU可同时对数万个像素执行光照计算，每帧16ms内完成CPU绝对无法胜任的计算量。

**深度学习训练**：矩阵乘法 C = A × B 中，C的每个元素计算相互独立，天然适合SIMT并行。NVIDIA A100的FP16 Tensor Core峰值算力为312 TFLOPS，而Intel最强CPU的FP16性能不超过2 TFLOPS，相差超过150倍，这正是SIMT大规模并行架构的直接体现。

**物理模拟**：布料模拟、流体粒子系统等场景中，每个粒子的受力计算相互独立（或仅依赖局部邻居），可以将数百万个粒子分配给GPU的数千个线程并行计算，实时性能远超CPU逐粒子串行更新的方式。

## 常见误区

**误区一：GPU核心数量越多，所有程序运行越快。** 这是错误的。GPU高核心数量只对数据并行程序有利。若代码含有大量串行逻辑或分支跳转（如递归算法、链表遍历），GPU的延迟隐藏机制无法发挥作用，性能可能比单核CPU慢10倍以上。GPU加速的前提是算法本身具有充分的数据并行性。

**误区二：GPU的"线程"与CPU的线程是同一概念。** GPU的一个CUDA线程极其轻量，寄存器状态直接存储在SM的寄存器文件中，线程切换无需保存/恢复上下文，切换开销接近零。而CPU线程切换需要保存完整的寄存器状态和栈指针，开销约为1000-10000个时钟周期。这也是GPU可以同时维持数万个活跃线程的原因。

**误区三：共享内存（Shared Memory）就是CPU意义上的缓存。** GPU的共享内存是程序员显式管理的片上内存，必须在着色器代码中用`__shared__`关键字手动声明和读写，编译器不会自动将全局内存访问替换为共享内存访问。L1缓存才是GPU中透明的自动缓存，而共享内存本质上是一块由程序员控制的暂存器（Scratchpad Memory）。

## 知识关联

理解GPU架构概述为后续学习奠定了必要的硬件认知基础。**GPU硬件管线**课题将在SM和线程层次的基础上，细化顶点处理、光栅化、片元处理各阶段如何映射到GPU硬件单元。**Warp/Wavefront**课题会深入SIMT模型中Warp Divergence的具体量化分析与优化手段，这直接依赖本文对SIMT执行机制的描述。**Compute Shader**编程需要程序员手动设置Thread Block尺寸，这与SM的最大线程容量（Ampere架构为1536线程/SM）直接相关，不理解SM结构则无法做出合理的线程组织决策。**DX12/Vulkan基础**中GPU命令队列、同步原语的设计逻辑，也源于GPU并行执行模型中异步性的内在需求。**GPU性能分析**中占用率（Occupancy）、带宽利用率等核心指标，均以本文的SM结构和延迟隐藏原理为分析前提。