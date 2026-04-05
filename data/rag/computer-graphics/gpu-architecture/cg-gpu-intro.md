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
quality_tier: "A"
quality_score: 73.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---



# GPU架构概述

## 概述

GPU（图形处理器）是一种专门为大规模并行计算设计的处理器，其架构与CPU存在根本性的设计哲学差异。CPU的设计目标是以最低延迟执行单条复杂指令序列，而GPU的设计目标是以最高吞吐量同时处理数千条相似指令。现代高端GPU如NVIDIA RTX 4090拥有16,384个CUDA核心、每秒82.6 TFLOPS的FP32算力；而顶级服务器CPU（如AMD EPYC 9654，96核）的浮点算力仅约6 TFLOPS，差距高达一个数量级以上。

GPU的诞生源于3D图形渲染的计算需求。1999年NVIDIA发布GeForce 256时首次引入"GPU"这一术语，彼时其主要功能是硬件变换和光照计算（T&L，Transform & Lighting），将原本依赖CPU软件实现的矩阵变换卸载到专用硬件。2006年NVIDIA推出的G80架构（GeForce 8800 GTX）是历史性转折点——它引入了**统一着色器架构**，将顶点着色器和像素着色器合并为128个通用流处理器（SP），并首次支持DirectX 10，为后来的GPGPU（通用GPU计算）奠定了基础。2007年NVIDIA随即发布CUDA编程框架，正式开启GPU通用计算时代。

理解GPU架构对图形开发者的意义极为直接：同样一段HLSL像素着色器，在不了解Warp结构的情况下随意写入`if-else`分支，可能导致Warp利用率从100%跌至50%，帧率直接减半。本文档是理解后续GPU硬件管线、Warp/Wavefront调度及Compute Shader优化的必要前提。

参考资料：《GPU Gems 3》(Nguyen, 2007, NVIDIA/Addison-Wesley)；以及Patterson & Hennessy《Computer Organization and Design: ARM Edition》(2017) 第4章中对SIMD/SIMT的对比分析。

---

## 核心原理

### CPU与GPU的芯片面积分配差异

CPU芯片中大约50%以上的晶体管用于缓存（L1/L2/L3）和分支预测、乱序执行逻辑，目的是将单线程指令延迟压缩至极致——现代Intel Core i9-13900K的单核IPC可在一个时钟周期内退休多达6条指令。GPU则反其道而行之：以NVIDIA Ada Lovelace架构（RTX 40系列，台积电4N工艺，762亿晶体管）为例，绝大部分晶体管面积分配给算术逻辑单元（ALU）阵列，L2缓存虽有72MB之多，但平摊到每个CUDA核心上不足5KB——远低于CPU核心可用的L3缓存量。

GPU依靠**"以并发隐藏延迟"（Latency Hiding by Concurrency）**策略弥补这一缺陷：当一个Warp（32线程）在等待显存数据（延迟约400-800个时钟周期）时，SM的调度器立即切换到另一个已就绪的Warp继续执行，从而将内存延迟淹没在连续的计算中。这要求应用程序向GPU提供足够多的并行线程——通常在每个SM上维持至少8个活跃Warp（NVIDIA称之为**Occupancy，占用率**），才能充分填满执行单元。

### SIMT执行模型详解

GPU使用**SIMT（Single Instruction, Multiple Threads，单指令多线程）**执行模型，由NVIDIA在2007年随Fermi架构论文中正式命名和描述（Lindholm et al., 2008, *IEEE Micro*）。SIMT与CPU上的SIMD既有联系又有本质区别：

- **SIMD**（如x86 AVX-512）要求程序员或编译器显式地将数据排列成512位宽的向量，用专用向量指令操作，寄存器宽度硬编码在ISA中。
- **SIMT**允许程序员编写看起来像普通标量C/HLSL代码的着色器，GPU硬件自动将同一Warp内32个线程的相同指令**打包**成一次宽向量操作执行，每个线程使用独立的寄存器和程序计数器（PC）。

SIMT对程序员屏蔽了向量化细节，但带来了**Warp分歧（Warp Divergence）**问题：当Warp内各线程执行到`if-else`时判断结果不一致，GPU须先"屏蔽"掉`else`分支的线程，执行`if`分支；再反向屏蔽执行`else`分支，两段本可并行的代码被迫串行，有效吞吐量减半乃至更低。

### SM/CU层级结构与寄存器文件

NVIDIA GPU的基本计算单元称为**流多处理器（SM，Streaming Multiprocessor）**，AMD对应称为**计算单元（CU，Compute Unit）**。以NVIDIA Ampere架构（A100）的SM为例，单个SM包含：

- **128个CUDA核心**（FP32 ALU，分为4组，每组32个）
- **64个FP64 CUDA核心**（双精度，针对科学计算）
- **4个第三代Tensor Core**（每个每时钟执行1024次FP16 FMA运算）
- **共享内存/L1缓存**：最大192KB可配置（可拆分为共享内存与L1缓存的不同比例）
- **寄存器文件**：每SM共256KB，即65,536个32位寄存器，多个Warp分时共享

整块A100 GPU由**108个SM**组成，合计139,264个CUDA核心，所有SM共享40MB或80MB HBM2E显存（内存带宽2,039 GB/s）。寄存器文件是最快的存储层级（零延迟），但每个线程能分配的寄存器数量直接影响SM上能同时驻留的Warp数量，进而影响Occupancy。

---

## 关键公式：理论峰值算力与带宽计算

GPU的**理论峰值FP32算力**计算公式为：

$$
\text{TFLOPS} = \text{CUDA核心数} \times \text{GPU基础频率(GHz)} \times 2
$$

其中系数2来源于每个CUDA核心每时钟执行1次FMA（Fused Multiply-Add），等效于1次乘法 + 1次加法，即2次浮点运算。

以RTX 4090为例：

$$
82.6 \text{ TFLOPS} = 16384 \times 2.52 \text{ GHz} \times 2
$$

**内存带宽**计算公式为：

$$
\text{带宽(GB/s)} = \text{位宽(bits)} \div 8 \times \text{显存频率(MHz)} \times 2 \div 1000
$$

RTX 4090使用384位GDDR6X，等效频率21 Gbps：

$$
1008 \text{ GB/s} = 384 \div 8 \times 21000 \times 2 \div 1000
$$

**运算强度（Arithmetic Intensity）**是判断着色器是计算瓶颈还是带宽瓶颈的关键指标：

$$
I = \frac{\text{浮点运算次数(FLOP)}}{\text{内存访问字节数(Bytes)}}
$$

当 $I$ 大于 $\frac{\text{峰值算力}}{\text{峰值带宽}} = \frac{82600 \text{ GFLOPS}}{1008 \text{ GB/s}} \approx 81.9 \text{ FLOP/Byte}$（RTX 4090的"屋顶线拐点"）时，该着色器是**计算绑定（Compute Bound）**；反之则是**带宽绑定（Bandwidth Bound）**。这是Roofline模型（Williams et al., 2009, *Communications of the ACM*）的核心应用。

---

## 实际应用

### 案例1：理解Draw Call与状态切换开销

CPU向GPU提交一次Draw Call本质上是向GPU命令缓冲区写入一条绘制命令。在DX11及早期API下，每次Draw Call前驱动程序须在CPU侧验证渲染状态、编译着色器变体、更新常量缓冲区，CPU端开销通常在10-100µs之间。当场景含5000个Draw Call时，CPU的Draw Call提交耗时即达50-500ms，远超16.7ms的帧预算。这正是DX12/Vulkan引入**命令列表（Command List）**直接录制GPU命令、绕过驱动验证层的根本原因。

### 案例2：分支对Warp效率的量化影响

考虑一段像素着色器伪代码：

```hlsl
// 低效写法：Warp内约50%线程走if，50%走else，执行时间≈2x
float4 PS(float2 uv : TEXCOORD) : SV_Target
{
    if (uv.x > 0.5)
        return tex2D(texA, uv);   // 分支A：50%线程执行
    else
        return tex2D(texB, uv);   // 分支B：50%线程执行
}

// 优化写法：用lerp代替分支，全部32线程同时执行
float4 PS_Opt(float2 uv : TEXCOORD) : SV_Target
{
    float t = step(0.5, uv.x);
    return lerp(tex2D(texB, uv), tex2D(texA, uv), t);
}
```

第二种写法虽然无条件采样了两张纹理（多了一次纹理读取），但消除了Warp分歧，在纹理缓存命中率高的场景下综合性能往往更优。

### 案例3：Occupancy调优

假设某Compute Shader每线程使用48个寄存器。Ampere SM寄存器文件共65,536个，每Warp（32线程）消耗 $32 \times 48 = 1536$ 个寄存器。SM最多同时驻留 $\lfloor 65536 \div 1536 \rfloor = 42$ 个Warp，但SM硬性上限为64 Warp，因此瓶颈在寄存器。若通过`#pragma unroll`减少循环展开，将每线程寄存器压到32个，则可驻留 $\lfloor 65536 \div 1024 \rfloor = 64$ 个Warp，达到100% Occupancy，SM调度器有更多机会隐藏内存延迟。

---

## 常见误区

**误区1：CUDA核心数越多，游戏帧率越高**
CUDA核心数决定的是FP32吞吐量，但现代游戏帧率往往受限于三角形光栅化速率（ROPs数量）、纹理采样吞吐（TMUs数量）或驱动CPU端开销，而非FP32算力。RTX 4080（9728个CUDA核心）在部分光追场景下因RT Core更多而超越某些CUDA核心数更多的老架构GPU。

**误区2：Warp分歧一定导致50%性能损失**
Warp分歧的实际开销取决于分支两侧的指令数量与分歧程度。若`if`分支只有1条指令而`else`分支有20条指令，且仅1/32线程走`else`，则额外开销极小。真正灾难性的分歧是两侧代码量相当且分歧线程数接近50%时。

**误区3：共享内存越大越好，无脑开满**
Ampere架构下共享内存与L1缓存共用192KB空间。若Compute Shader申请过多共享内存（如每线程组128KB），SM上能同时驻留的线程组数量将降至1，Occupancy极低，反而得不偿失。需要在共享内存用量与Occupancy之间做精细权衡。

**误区4：GPU显存带宽等于实际可用带宽**
理论峰值带宽（如RTX 4090的1008 GB/s）是在所有显存通道满载、访问模式完全合并（Coalesced Access）时才能达到的理论值。随机访问或非对齐访问会使实际有效带宽跌至峰值的10%以下。

---

## 知识关联

理解本文档中的SIMT模型和SM层级结构，是深入以下后续概念的直接基础：

- **GPU硬件管线**：顶点着色器、光栅化、像素着色器各阶段在SM上如何调度，图元组装器和ROP如何与SM协同。
- **Warp/Wavefront**：Warp调度器的零开销切换机制（Zero-overhead Thread Switching）、活跃Warp数量与Occupancy的精确计算方法。
- **Compute Shader**：线程组（Thread Group）与SM的映射关系，共享内存（Group Shared Memory）的Bank Conflict问题，Dispatch调用的线程网格布局。
- **DX12/Vulkan基础**：命令列表、描述符堆、Pipeline State Object（PSO）的设计动机均源于降低CPU提交Draw Call