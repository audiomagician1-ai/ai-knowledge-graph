# GPU计算

## 概述

GPU计算（GPU Computing）是指利用图形处理单元（Graphics Processing Unit）执行通用数学计算任务的技术范式，其核心理念是以大量简单计算核心替代少量复杂核心来处理高度并行的数据工作负载。现代GPU（如NVIDIA H100 SXM5）集成了16896个CUDA核心与528个Tensor Core，峰值FP32算力达到67 TFLOPS，峰值BF16 Tensor算力达到1979 TFLOPS，与同时代CPU相比在矩阵乘法等密集计算场景下算力优势超过100倍。

GPU计算的历史转折点是2006年11月NVIDIA发布的CUDA 1.0框架（Compute Unified Device Architecture），此前研究者只能将通用计算任务伪装成着色器（Shader）操作借助OpenGL/DirectX接口执行，这一方式被学界称为"GPGPU黑客时代"（Owens et al., 2007）。2008年苹果主导发布的OpenCL 1.0标准（由Khronos Group维护）打破了NVIDIA的生态垄断，使AMD Radeon、Intel Arc等异构硬件均可接入通用计算生态。2017年NVIDIA发布Volta架构，首次引入专用Tensor Core，专门加速$A \times B + C$形式的混合精度矩阵乘加（MMA）运算，将深度学习训练吞吐量提升至Pascal架构的12倍。

GPU通用计算的普及直接推动了深度学习的第二次复兴。Krizhevsky等人（2012）在论文《ImageNet Classification with Deep Convolutional Neural Networks》中首次展示了在2块GTX 580 GPU上训练的AlexNet模型，将ImageNet Top-5错误率从26.2%降至15.3%，证明GPU算力是现代大规模神经网络训练不可或缺的基础设施。

## 核心原理

### SIMT执行模型与Warp调度

GPU采用**SIMT（Single Instruction, Multiple Threads）**执行模型，这是NVIDIA对Flynn分类中SIMD的延伸创新。在CUDA中，线程被组织为四级层次结构：**Thread → Warp → Block（Thread Block）→ Grid**。最小硬件调度单元是**Warp**，每个Warp固定包含**32个线程**，这32个线程在同一时钟周期内同步执行相同的指令，各自操作独立的寄存器文件。

当Warp内线程因条件分支走向不同执行路径时，产生**Warp Divergence（束散射）**：硬件被迫串行执行各分支并用掩码屏蔽不参与该路径的线程，最坏情况（32个线程走32条不同路径）性能退化至1/32。因此，高性能Kernel设计的首要原则是使同一Warp内所有线程走相同的控制流路径。

一个SM（Streaming Multiprocessor）上可同时驻留多个Warp，当某个Warp因等待内存访问而停滞时，SM调度器立即切换到另一个就绪Warp执行，这一机制称为**延迟隐藏（Latency Hiding）**。H100的每个SM最多支持64个Warp并发驻留（即2048个线程），高占用率（Occupancy）是充分发挥延迟隐藏效果的前提。

### 存储器层次结构与访存优化

GPU存储器层次的延迟差异是编程优化的核心战场：

| 存储层级 | 作用域 | 访问延迟 | 典型容量（H100）|
|---|---|---|---|
| 寄存器（Register）| 每线程私有 | ~1周期 | 256KB/SM（65536×32bit寄存器）|
| 共享内存（Shared Memory）| Block内共享 | ~20-30周期 | 228KB/SM（可配置）|
| L1缓存 | SM内 | ~30周期 | 与共享内存统一管理 |
| L2缓存 | 全芯片 | ~200周期 | 50MB |
| 全局内存（HBM3）| 全芯片 | ~600-800周期 | 80GB |

**合并访存（Coalesced Memory Access）**是全局内存优化的黄金法则：当一个Warp的32个线程访问128字节对齐的连续内存区域时，硬件将32次访问合并为单次128字节事务，内存带宽利用率达到100%。若访问地址完全随机分散，则退化为32次独立的32字节事务，有效带宽降至理论峰值的1/32（Kirk & Hwu, 2016）。

**共享内存Bank冲突（Bank Conflict）**是另一类常见性能陷阱。共享内存被分为32个Bank，每个Bank宽度为4字节（32位），同一Warp内若多个线程同时访问同一Bank的不同地址，则访问被串行化。矩阵转置操作中若直接读写共享内存，每行32个float元素恰好各占一个Bank，第$i$个线程访问第$i$个Bank，无冲突；但若按列写回时每列元素地址步长为32个float（128字节），导致32个线程全部落在同一Bank，产生32路Bank冲突。标准解决方案是为共享内存声明添加1列填充：`__shared__ float tile[TILE][TILE+1]`，将步长破坏为非32倍数。

### Compute Shader与图形API通用计算

在非CUDA生态中，Compute Shader是GPU通用计算的主要入口。DirectX 11引入Compute Shader 5.0，DirectX 12与Vulkan则进一步通过显式命令队列控制将Compute与Graphics管线并行化。Compute Shader使用HLSL（DirectX）或GLSL（OpenGL/Vulkan）编写，以`[numthreads(X, Y, Z)]`标注每个线程组的尺寸，对应CUDA的`blockDim`。线程组内共享内存通过`groupshared`关键字声明。

Vulkan的Compute Pipeline允许开发者绕过所有图形光栅化状态，直接提交Dispatch命令执行计算着色器，延迟与开销低于传统图形管线，适合在游戏引擎中实现粒子物理、屏幕空间环境光遮蔽（SSAO）、卷积后处理等效果的GPU加速。

### OpenCL异构计算模型

OpenCL将计算设备抽象为**Platform → Device → Context → Command Queue → Kernel**的层次模型。其线程组织与CUDA对应关系为：NDRange（Grid）→ Work-Group（Block）→ Work-Item（Thread）。OpenCL的独特优势在于可在同一Context中混合使用CPU、GPU、FPGA等多种设备，通过`clEnqueueCopyBuffer`实现设备间数据迁移，适合需要在CPU复杂控制逻辑与GPU密集计算之间频繁切换的科学计算场景（Munshi et al., 2011）。

## 关键公式与性能模型

### Roofline模型

评估GPU Kernel性能的标准工具是**Roofline模型**（Williams et al., 2009），它通过算术强度（Arithmetic Intensity）判断Kernel的性能瓶颈：

$$I = \frac{\text{浮点运算量（FLOP）}}{\text{内存访问量（Byte）}}$$

GPU的**Roofline上界**由两个硬件参数决定：

$$P = \min\left(\pi,\ \beta \cdot I\right)$$

其中 $\pi$ 为峰值计算性能（FLOPS），$\beta$ 为峰值内存带宽（Bytes/s）。当 $I < \pi/\beta$（称为**计算屋脊点**，Ridge Point）时，Kernel受内存带宽限制（Memory Bound）；当 $I \geq \pi/\beta$ 时，受计算单元吞吐限制（Compute Bound）。

以H100 SXM5为例：$\pi_{\text{FP32}} = 67\ \text{TFLOPS}$，$\beta_{\text{HBM3}} = 3.35\ \text{TB/s}$，因此Ridge Point为 $67 \times 10^{12} / 3.35 \times 10^{12} \approx 20\ \text{FLOP/Byte}$。矩阵乘法（GEMM）的算术强度在矩阵边长 $N=4096$ 时约为 $N/2 = 2048\ \text{FLOP/Byte}$，远超Ridge Point，属于典型的Compute Bound操作，充分利用了Tensor Core的峰值算力。

### 占用率计算

SM的**理论占用率（Occupancy）**定义为：

$$\text{Occupancy} = \frac{\text{实际驻留Warp数}}{\text{SM最大驻留Warp数}}$$

限制占用率的资源包括：每线程寄存器数量、共享内存用量、Block大小。使用NVIDIA的`nvcc --ptxas-options=-v`编译选项可查看每个Kernel的寄存器与共享内存消耗，CUDA Occupancy Calculator工具可据此计算理论占用率上限。

## 实际应用

### 案例：并行归约（Parallel Reduction）

并行求数组总和是GPU计算的经典基准案例。朴素做法是让每个线程处理一个元素然后逐层叠加，Mark Harris（NVIDIA，2007）在《Optimizing Parallel Reduction in CUDA》中系统分析了6种优化方案：

1. **交错寻址（Interleaved Addressing）**：基础实现，但产生Warp Divergence，效率仅约25%
2. **顺序寻址（Sequential Addressing）**：消除Divergence，带宽利用率提升至50%
3. **减少空闲线程（Idle Threads）**：首次加载时完成第一轮归约，线程利用率翻倍
4. **循环展开（Loop Unrolling）**：对最后32线程（单Warp内）展开同步障碍，消除`__syncthreads()`开销
5. **完全展开（Complete Unrolling）**：使用模板元编程在编译期展开所有循环
6. **多元素/线程（Multiple Elements per Thread）**：最终方案，每线程处理多个元素，充分隐藏内存延迟

最终优化后的归约Kernel相比初始版本吞吐量提升约30倍，达到H100峰值内存带宽的约85%。

### 深度学习中的Tensor Core应用

NVIDIA的cuBLAS与cuDNN库在检测到Volta及以上架构时自动调用Tensor Core执行GEMM。Tensor Core每个时钟周期执行一次$4 \times 4 \times 4$的矩阵乘加（FP16输入，FP32累加），等效于每周期完成128次FMA（Fused Multiply-Add）操作。在训练GPT-3（1750亿参数）时，使用A100 80GB GPU集群，每个A100的Tensor Core吞吐约为312 TFLOPS（BF16），相比V100 FP16的112 TFLOPS提升约2.8倍，大幅缩短了大模型训练周期。

## 常见误区

**误区一：线程数越多性能越好。** 实际上过多线程会导致每线程可用寄存器数量减少（寄存器溢出至本地内存，延迟从1周期暴增至600周期），反而降低性能。需要通过CUDA Occupancy Calculator在并发度与寄存器压力之间寻找最优点。

**误区二：GPU适合所有并行任务。** GPU的PCIe数据传输带宽（~64 GB/s，PCIe 5.0 x16）远低于HBM3的3.35 TB/s，若计算量不足以摊销数据搬运开销（即算术强度过低），GPU版本可能比CPU慢。Amdahl定律告诉我们：若程序中串行部分占比为$s$，最大加速比为$1/s$，即使GPU加速并行部分至无限快，整体加速比也不超过$1/s$。

**误区三：Compute Shader与CUDA功能等价。** Compute Shader受图形API限制，缺乏CUDA的统一虚拟寻址（UVA）、动态并行（Dynamic Parallelism）和CUDA Graph等高级特性，在复杂算法（如稀疏矩阵运算）的实现灵活性上不如CUDA。

**误区四：OpenCL与CUDA性能相当。** 由于NVIDIA驱动对OpenCL的优化投入远低于CUDA，同一算法的OpenCL实现在NVIDIA GPU上通常比CUDA版本慢20%~40%，这是生态策略差异而非硬件限制。

## 知识关联

**→ CUDA内存模型** 是本文存储层次结构的直接延伸，涵盖统一内存（Unified Memory）、零拷贝内存（Zero-Copy Memory）与Peer-to-Peer传输。

**→ 多线程同步原语** GPU中的`__syncthreads()`对应CPU中的屏障（Barrier），但GPU还提供Warp级原语如`__shfl_sync()`实现Warp内线程通信，开销仅为1个时钟周期