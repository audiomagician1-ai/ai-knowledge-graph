---
id: "cg-gpu-driven"
concept: "GPU Driven Pipeline"
domain: "computer-graphics"
subdomain: "gpu-architecture"
subdomain_name: "GPU架构"
difficulty: 4
is_milestone: false
tags: ["前沿"]

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
updated_at: 2026-04-01
---


# GPU驱动渲染管线

## 概述

GPU驱动渲染管线（GPU Driven Pipeline）是一种将场景剔除、绘制命令生成、资源绑定等传统上由CPU主导的工作完全交给GPU执行的渲染架构。在传统的CPU驱动渲染中，CPU每帧需要遍历场景中所有物体、执行可见性测试、逐一提交DrawCall，当场景包含数万个网格时，这一过程会产生严重的CPU瓶颈。GPU驱动渲染管线通过Compute Shader在GPU上并行完成这些工作，再以间接绘制命令（Indirect Draw）驱动光栅化阶段，使CPU只需提交极少量的绘制指令。

这一架构在2015年由Ubisoft的Graham Wihlidal在GDC演讲《Optimizing the Graphics Pipeline with Compute》中系统性地提出并推广，其在《刺客信条：大革命》中应用GPU剔除处理了超过10000个独立网格物体，这是CPU驱动方案难以实现的规模。同年，Wihlidal展示了在主机平台上将DrawCall数量从原先的数千次压缩到几十次的实测数据。此后Epic Games在虚幻引擎5的Nanite系统中将其发展为面向虚拟几何体的极致形态，能够实时处理数以亿计的三角形。

GPU驱动管线的重要性在于它将渲染系统的性能瓶颈从CPU-GPU提交开销转移到了GPU自身的吞吐量，从根本上改变了游戏引擎对DrawCall数量的依赖关系，并为后续的Bindless资源和虚拟几何体等技术奠定了基础。

## 核心原理

### 间接绘制（Indirect Draw）

间接绘制是GPU驱动管线的执行入口。与`DrawIndexed(indexCount, instanceCount, startIndex, ...)`这种CPU直接传参的调用不同，`DrawIndexedIndirect(buffer, offset)`从一个GPU缓冲区中读取绘制参数。该缓冲区的结构在D3D12中定义为：

```
struct D3D12_DRAW_INDEXED_ARGUMENTS {
    UINT IndexCountPerInstance;
    UINT InstanceCount;
    UINT StartIndexLocation;
    INT  BaseVertexLocation;
    UINT StartInstanceLocation;
};
```

Compute Shader在前一个Pass中向这个参数缓冲区写入每个待绘制物体的具体参数，被剔除的物体将`InstanceCount`设为0，从而跳过光栅化，完全避免无效的GPU工作。`ExecuteIndirect`（D3D12）或`vkCmdDrawIndexedIndirect`（Vulkan）允许用单次API调用执行缓冲区中存储的多条绘制命令，即Multi-Draw Indirect（MDI），将数千次DrawCall折叠为1次CPU API调用。

### GPU剔除（GPU Culling）

GPU剔除是在Compute Shader中并行执行的多级可见性测试，取代了CPU端的单线程剔除循环。典型的剔除流水线包括：

**视锥体剔除（Frustum Culling）**：每个线程处理一个物体的包围球或AABB，将其与相机的6个裁剪平面做点积测试。对于一个包含N个物体的场景，GPU以N/64（每Dispatch组64线程）个线程组并行完成，而CPU需串行执行N次测试。

**遮挡剔除（Occlusion Culling）**：使用上一帧的Hierarchical Z-Buffer（Hi-Z）作为遮挡查询的深度参考。将物体包围盒投影到屏幕空间后，计算其覆盖的最大Mip Level，再与Hi-Z中对应像素的最大深度比较。若包围盒的最近深度大于Hi-Z深度，则判定为被遮挡。这种"时间复用"方案存在一帧延迟，通常需要补充一个Two-Phase Occlusion Culling来处理新出现的物体。

**背面剔除与小三角形剔除**：在Compute Shader中提前剔除相对屏幕面积小于一个像素的三角形，避免其进入光栅化阶段产生的细碎开销，这是Nanite虚拟几何体的关键前置步骤。

### 场景数据的GPU常驻布局

为了让GPU能自主访问场景所有物体的变换、材质等信息，GPU驱动管线要求将场景数据以大型结构化缓冲区（StructuredBuffer）的形式常驻显存。典型的布局包括：

- **InstanceBuffer**：每条记录存储一个实例的世界变换矩阵（4×4 float）、包围球（float4）和材质索引（uint）。
- **MeshletBuffer**：存储每个Meshlet（通常包含最多128个顶点和256个三角形）的顶点偏移和索引范围。
- **MaterialBuffer**：存储各材质参数，配合Bindless纹理数组索引，使Compute Shader无需切换管线状态即可访问任意材质数据。

Compute Shader通过`globalInvocationID`直接索引上述缓冲区，完全无需CPU介入数据的读取与分发。

## 实际应用

**《刺客信条：大革命》（2014）**是最早将GPU驱动管线应用于AAA游戏的案例之一。其地图中巴黎城市场景包含大量重复的建筑模块，Ubisoft使用Compute Shader对约10000个独立可见性单元执行GPU剔除，并通过Indirect Draw批量提交，最终在PlayStation 4上将每帧的CPU提交时间减少约70%。

**虚幻引擎5 Nanite**将GPU驱动推进到三角形级别的粒度。其Visibility Buffer Pass使用一个128位的G-Buffer像素，存储InstanceID、ClusterID和BarycentricCoord，随后在Compute Shader中按材质分类像素并重建几何属性，彻底消除了OverDraw与材质切换开销。Nanite宣传数据显示其能在PS5上实时渲染单帧超过10亿个三角形。

**移动端的受限应用**：由于Mali等移动GPU的Tile-Based架构与间接绘制的交互存在额外开销，GPU驱动管线在移动平台上通常仅应用于静态大型场景的LOD选择阶段，而非完整的逐帧剔除流水线。

## 常见误区

**误区一：GPU剔除一定优于CPU剔除**。对于场景物体数量少于约1000个的情况，将剔除数据上传GPU、执行Dispatch、再读回可见性结果的同步开销（Readback延迟）会超过CPU直接剔除的收益。GPU剔除的收益随场景规模呈超线性增长，在物体数量达到10000量级时才明显体现优势。且Indirect Draw在某些驱动实现中无法与Early-Z硬件完全协同，需要额外的Depth Pre-Pass配合。

**误区二：使用Indirect Draw就等于实现了GPU驱动管线**。仅将DrawCall参数放入缓冲区而不在Compute Shader中执行GPU剔除和参数生成，只是形式上使用了间接绘制，CPU仍然是逻辑驱动者。完整的GPU驱动管线要求场景数据常驻GPU、剔除逻辑运行在GPU、绘制参数由GPU填充这三个条件同时满足。

**误区三：GPU驱动管线可以消除所有DrawCall开销**。即便使用ExecuteIndirect，每次调用仍有固定的命令队列处理开销，且每次状态切换（如切换渲染目标）都会打断批次。GPU驱动管线最大化收益的前提是配合Bindless资源技术，使所有物体共享同一套管线状态，否则材质切换仍会造成大量小批次。

## 知识关联

**前置基础——Compute Shader**：GPU驱动管线中的剔除、LOD选择、参数填充全部运行在Compute Shader中。理解Compute Shader的线程组（ThreadGroup）划分、共享内存（GroupShared Memory）以及原子操作（`InterlockedAdd`用于写入Indirect参数计数）是实现GPU剔除的必要条件。特别是`AppendStructuredBuffer`与`ConsumeStructuredBuffer`语义在填充可见物体列表时被广泛使用。

**后续技术——Bindless资源**：GPU驱动管线在剔除阶段完成后，不同物体在绘制阶段可能需要访问完全不同的纹理和常量缓冲区。若沿用传统的根签名绑定，GPU无法在单一DrawCall中处理多种材质物体。Bindless资源通过将所有纹理注册到一个无边界的描述符堆（Descriptor Heap）中，允许着色器通过动态索引访问任意纹理，从而使GPU驱动管线生成的批次无需在DrawCall间切换资源绑定状态，是实现完整GPU驱动渲染的必要延伸。