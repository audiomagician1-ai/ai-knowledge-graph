# 着色器互操作

## 概述

着色器互操作（Shader Interoperability）是指在同一帧渲染管线中，Compute Shader与图形着色器（Vertex、Pixel、Geometry等）之间直接共享GPU资源、传递数据的机制。其核心在于：无需通过CPU回读（Readback）或重新上传，Compute Shader写入的计算结果可以直接被后续的图形着色器读取，或者图形着色器渲染产生的深度、颜色数据可以直接被Compute Shader消费。

这一机制在DirectX 11（2009年随D3D11正式引入）随着无序访问视图（Unordered Access View，UAV）的标准化而成为主流工作流。在此之前，GPU计算与图形渲染彼此隔离，计算结果必须回读到CPU再重新上传，产生严重的PCIe总线带宽瓶颈——以PCIe 3.0 x16为例，理论双向带宽约为16 GB/s，而现代GPU的片上L2缓存带宽可达数TB/s，两者相差三个数量级。DirectX 12（2015年）和Vulkan 1.0（2016年，由Khronos Group发布）进一步将资源屏障（Resource Barrier）语义显式化，程序员需要手动声明资源在Compute队列与Graphics队列之间的所有权转移。

着色器互操作之所以关键，是因为现代渲染技术（如GPU粒子、屏幕空间反射、DLSS类上采样算法）都依赖Compute Shader高效处理数据后将结果无缝注入光栅化流程。若缺少这一机制，每帧都要进行CPU-GPU往返同步，在1080p/60fps的目标下，单次同步延迟（通常为1~3ms）会直接成为渲染预算的杀手。以60fps为例，每帧总预算仅有约16.67ms，若每帧因缺乏互操作机制而产生两次3ms的同步停顿，则有效渲染时间压缩至10.67ms，帧率实际上限将跌破50fps。

**思考问题：** 在同一帧中，若Compute Shader和Pixel Shader需要交替读写同一张纹理三次，最少需要插入多少个资源屏障？屏障数量与数据依赖关系之间遵循什么规律？若将多个独立纹理的屏障合并为一次批量调用（`ResourceBarrier`数组形式），GPU驱动能否真正并行处理这些状态转换，从而降低总开销？更进一步：当AsyncCompute队列与Graphics队列并行运行时，跨队列的资源同步语义与单队列屏障有何本质区别，是否存在死锁风险？

---

## 核心原理

### UAV作为共享数据桥梁

无序访问视图（UAV，`RWTexture2D`、`RWStructuredBuffer`、`RWByteAddressBuffer`等）是实现着色器互操作的主要资源类型。UAV允许Compute Shader以随机读写方式操作纹理或缓冲区，写入完成后，同一资源可以绑定为Shader Resource View（SRV）供图形着色器以只读方式采样，或继续绑定为Render Target供后续Pass渲染。

在HLSL中，典型的共享缓冲区声明如下：

```hlsl
// Compute Shader阶段：以UAV形式写入粒子数据
RWStructuredBuffer<ParticleData> particleBuffer : register(u0);

// Vertex Shader阶段：以SRV形式读取同一Buffer
StructuredBuffer<ParticleData> particleBuffer : register(t0);
```

同一块GPU显存，通过UAV绑定时是可写的，通过SRV绑定时是只读的，这种视图转换本身不涉及数据拷贝，其带宽开销为 $0$ 字节——切换的仅是驱动层对该内存区域访问权限的描述符元数据。需要特别注意的是，`RWByteAddressBuffer`以字节为寻址粒度（32位对齐），常用于跨类型数据打包，而`RWStructuredBuffer<T>`则以结构体步长（Stride）为寻址粒度，适合规整的顶点或粒子数据，两者的缓存访问模式差异可影响L1命中率达20%以上（Uralsky，2007）。

此外，DirectX 12引入的描述符堆（Descriptor Heap）机制允许程序员在一次Draw/Dispatch调用中同时绑定多达数千个SRV/UAV，相比D3D11逐槽绑定的方式，显著降低了驱动层的状态切换开销。Vulkan对应的机制为描述符集（Descriptor Set），同样支持大规模批量绑定。

### 资源屏障与同步点的量化分析

在DirectX 12中，若Compute Pass写入一张纹理后，Graphics Pass需要对其采样，必须在两者之间插入资源屏障：

```cpp
D3D12_RESOURCE_BARRIER barrier = {};
barrier.Type = D3D12_RESOURCE_BARRIER_TYPE_TRANSITION;
barrier.Transition.pResource = pSharedTexture;
barrier.Transition.StateBefore = D3D12_RESOURCE_STATE_UNORDERED_ACCESS;
barrier.Transition.StateAfter  = D3D12_RESOURCE_STATE_PIXEL_SHADER_RESOURCE;
commandList->ResourceBarrier(1, &barrier);
```

这个转换的代价并非免费：GPU驱动需要等待之前所有针对该资源的UAV写操作完成，并将缓存刷新至L2或全局内存，才能允许后续的图形着色器以一致的方式读取数据。若资源屏障插入位置不当（如过于频繁地在同一资源上来回切换UAV↔SRV），会导致GPU流水线停顿，实测可造成5%~15%的帧率损失（Wihlidal，2016）。

设一帧中对某资源的状态切换次数为 $n$，则最坏情况下同步开销近似满足：

$$T_{\text{sync}} = n \times (T_{\text{flush}} + T_{\text{invalidate}})$$

其中 $T_{\text{flush}}$ 为缓存刷新时延（GPU将脏缓存行写回共享L2或VRAM所需时间），$T_{\text{invalidate}}$ 为下游缓存无效化时延（使后续读操作无法命中过期缓存行所需时间），$n$ 为当帧内该资源经历的状态切换总次数。在NVIDIA Ampere架构（GA102，2020年）上，实测单次L2级刷新约为 $0.8\sim2.0\,\mu s$，因此将 $n$ 从8次优化至3次，可节省约 $4\sim10\,\mu s$ 的空闲气泡（Bubble）。

Vulkan 1.0在语义上与D3D12类似，但通过`VkImageMemoryBarrier`和`VkBufferMemoryBarrier`分别针对图像和缓冲区，并以`srcStageMask`/`dstStageMask`精确声明上下游管线阶段，粒度比D3D12更细。例如，若后续只有Fragment Shader（而非所有图形阶段）需要读取该资源，`dstStageMask`可设为`VK_PIPELINE_STAGE_FRAGMENT_SHADER_BIT`而非`ALL_GRAPHICS`，驱动可据此省略对顶点和几何阶段的等待，进一步减少气泡。Vulkan 1.3（2022年）引入的同步对象2（Synchronization2，`VK_KHR_synchronization2`）扩展进一步将阶段掩码扩展为64位，支持对光线追踪管线（Ray Tracing Pipeline）与Compute管线之间的资源共享进行更精确的依赖声明。

### Append/Consume Buffer模式与GPU驱动渲染

着色器互操作的另一种典型模式是`AppendStructuredBuffer`与`ConsumeStructuredBuffer`配对。Compute Shader在视锥剔除（Frustum Culling）阶段将可见物体写入AppendBuffer，之后的间接绘制（ExecuteIndirect / DrawIndirect）调用直接消费这个列表，整个过程对象数量由GPU内部的原子计数器管理，CPU端完全不感知具体写入了多少个元素。

例如，在一个包含10,000个静态网格的场景中，CPU提交的DrawCall仅有1次（ExecuteIndirect），Compute Shader在剔除后可能只保留2,347个可见物体——这一数字无需回传CPU，直接驱动后续的顶点着色器处理对应数量的实例。这是零回读的GPU驱动渲染（GPU-Driven Rendering）的基础模式，也是寒霜引擎（Frostbite）在《战地1》（2016年）中实现超大规模场景渲染的核心技术之一。间接绘制命令结构体`D3D12_DRAW_INDEXED_ARGUMENTS`包含`IndexCountPerInstance`、`InstanceCount`、`StartIndexLocation`、`BaseVertexLocation`、`StartInstanceLocation`五个字段，均可由Compute Shader按需填充，赋予GPU完全的绘制参数自主权，无需CPU介入。

### 异步计算队列（AsyncCompute）与互操作的并行化

现代GPU（如AMD RDNA 2及NVIDIA Turing/Ampere架构）支持独立的AsyncCompute队列，允许Compute任务与Graphics任务在同一GPU上并行执行，前提是两者之间不存在资源依赖。着色器互操作在AsyncCompute场景下需要跨队列同步原语：D3D12使用`ID3D12Fence`，Vulkan使用`VkSemaphore`（针对队列间同步）或`VkEvent`（针对队列内精细同步）。

典型的AsyncCompute互操作模式：当前帧Graphics队列正在执行Shadow Map渲染时，AsyncCompute队列同步执行上一帧的后处理（如时域抗锯齿TAA、曝光直方图统计），两者通过Fence信号在帧边界对齐。AMD在GCN架构白皮书（2012年）中指出，合理的AsyncCompute调度可将GPU占用率从约65%提升至85%以上，相当于在不增加硬件的情况下获得约30%的有效吞吐量提升。

---

## 关键公式与理论模型

### 屏障开销模型

如前述，屏障总开销由切换次数 $n$、刷新时延和无效化时延共同决定：

$$T_{\text{sync}} = n \times (T_{\text{flush}} + T_{\text{invalidate}})$$

在实际优化中，目标是在保证数据正确性的前提下最小化 $n$。常见策略包括：将同一资源的多次读写合并为单次Pass（减少 $n$）、将多个独立资源的屏障批量提交（并行处理，降低单次屏障的平均延迟）、以及在AsyncCompute队列中将Compute Pass与Graphics Pass流水线化（令 $T_{\text{flush}}$ 与Graphics工作重叠执行）。

值得注意的是，上述模型为线性近似。实际上，若多个独立资源的屏障通过数组形式批量提交，驱动可将部分 $T_{\text{flush}}$ 操作并行化，使总开销趋近于：

$$T_{\text{sync,batch}} \approx n_{\text{serial}} \times (T_{\text{flush}} + T_{\text{invalidate}}) + T_{\text{overhead}}$$

其中 $n_{\text{serial}}$ 为存在真实数据依赖的串行屏障数量（不可并行化部分），$T_{\text{overhead}}$ 为批量调用本身的固定开销（通常为数十纳秒量级）。

### 深度重建世界坐标公式

在SSAO、HBAO+等依赖深度Buffer的互操作链路中，Compute Shader需从屏幕空间深度值重建世界空间坐标：

$$\mathbf{P}_{\text{world}} = M_{\text{proj}}^{-1} \cdot \begin{pmatrix} 2u/W - 1 \\ 1 - 2v/H \\ d \\ 1 \end{pmatrix}$$

其中 $u, v$ 为像素屏幕坐标（单位：像素），$W, H$ 为渲染分辨率宽高，$d$ 为深度缓冲中存储的非线性深度值（D3D约定范围 $[0,1]$，OpenGL约定范围 $[-1,1]$），$M_{\text{proj}}^{-1}$ 为逆投影矩阵（4×4）。由于该公式对每个像素都需执行矩阵-向量乘法，Compute Shader的线程组大小（Thread Group Size）通常选取 $8\times8=64$ 或 $16\times16=256$，以匹配GPU Warp/Wavefront的宽度（NVIDIA为32线程，AMD RDNA为64线程），确保线程不空闲浪费。

若使用逆深度（Reverse-Z）技术——即将近平面映射到深度值1.0、远平面映射到0.0——可显著提升浮点精度