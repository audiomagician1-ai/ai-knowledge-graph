---
id: "cg-ray-tracing-hw"
concept: "光追硬件单元"
domain: "computer-graphics"
subdomain: "gpu-architecture"
subdomain_name: "GPU架构"
difficulty: 4
is_milestone: false
tags: ["硬件"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.5
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# 光追硬件单元

## 概述

光追硬件单元是GPU芯片上专门负责加速光线与场景求交运算的固定功能硬件模块。NVIDIA将其称为**RT Core**（首次出现于2018年的Turing架构，型号RTX 2080），AMD则称之为**Ray Accelerator**（首次出现于2020年的RDNA 2架构），两者在功能上都承担同一核心任务：在不占用着色器（Shader Core/SIMD单元）计算资源的情况下，独立完成BVH节点遍历与光线-三角形求交测试。

在没有光追硬件单元的时代，光线追踪必须完全依赖通用着色器来执行BVH遍历与求交，这会消耗大量可编程计算资源，导致帧率极低。Turing架构的RT Core使得实时光追在游戏中首次商业可行，RTX 2080 Ti拥有68个RT Core，每个RT Core能够在单个时钟周期内完成一次AABB（轴对齐包围盒）与光线的求交判断，而同等操作在Shader Core上需要消耗若干个时钟周期的ALU运算。

光追硬件单元的重要性在于它将原本属于算法层面的**BVH遍历状态机**固化进了硅片逻辑，使得遍历栈管理、子节点排序等控制逻辑完全脱离可编程流水线，实现了计算资源的解耦与并行度的最大化。

---

## 核心原理

### BVH遍历的硬件状态机

RT Core内部实现了一个固定的BVH遍历状态机，其工作流程包含以下阶段：**光线变换 → 节点读取 → AABB求交测试 → 子节点入栈 → 三角形求交测试 → 结果返回**。当着色器通过`TraceRay()`或`vkCmdTraceRaysKHR()`等API发射一条光线后，RT Core接管该光线的所有遍历工作，着色器线程进入等待状态，此时GPU调度器可以切换到其他线程继续执行，从而隐藏遍历延迟。

遍历过程中，RT Core维护一个**遍历栈（Traversal Stack）**，记录待访问的BVH节点。NVIDIA第二代RT Core（Ampere，RTX 3080，2020年）将每个光线的栈深度上限设定为与BVH层级数匹配，并在硬件中缓存了最近访问的BVH节点，减少重复的显存读取。

### 光线-AABB与光线-三角形求交

RT Core硬件中内置了两种固定精度的求交电路：

1. **光线-AABB求交**（用于BVH内部节点测试）：采用slab方法计算光线与三个轴对齐平面对的交点，公式为：
   $$t_{min} = \max\!\left(\frac{b_{min} - o}{\vec{d}}\right),\quad t_{max} = \min\!\left(\frac{b_{max} - o}{\vec{d}}\right)$$
   若 $t_{min} \leq t_{max}$ 且 $t_{max} > 0$，则光线击中该AABB。此电路在硬件中以**单时钟周期**完成一对轴的计算，三对轴并行，整体延迟极低。

2. **光线-三角形求交**（用于BVH叶节点测试）：采用Möller–Trumbore算法的硬件实现，计算重心坐标 $(u, v)$ 并判断是否位于三角形内部，同时输出交点深度 $t$，供后续着色使用。

### RT Core与Shader Core的协作模型

RT Core并不独立完成完整的光追渲染，它只负责几何求交阶段，着色逻辑（任意命中着色器 Any-Hit Shader、最近命中着色器 Closest-Hit Shader）仍在Shader Core上执行。两者通过**异步协作**工作：Shader Core发射光线 → RT Core遍历返回命中结果 → Shader Core执行命中着色器 → 着色器可能再次调用`TraceRay()`发射次级光线 → RT Core再次接管。NVIDIA Ada Lovelace架构（RTX 4090，2022年）的第三代RT Core加入了对**不透明几何体快速路径**的优化，跳过Any-Hit着色器调用，可将遍历速度提升约2倍。

---

## 实际应用

**游戏中的实时阴影与反射**：《赛博朋克2077》使用DXR（DirectX Raytracing）API，依赖RT Core加速光线追踪阴影与反射，在RTX 3080上4K分辨率下启用完整光追可维持约30 FPS，若全部回退至Shader Core软件模拟则帧率将骤降至个位数。

**NVIDIA DLSS与光追的协同**：由于RT Core产生的噪声图像仍需降噪，实际流程是RT Core每像素仅发射极少数光线（如1条或0.5条/像素的稀疏采样），RT Core快速完成求交，然后由Tensor Core上运行的DLSS神经网络进行时间累积降噪与超分辨率重建，三类专用硬件各司其职。

**ProRender与离线渲染加速**：AMD的Ray Accelerator不仅服务于游戏，也被AMD ProRender等离线渲染工具调用。RX 6900 XT的Ray Accelerator吞吐量达到约**61亿次光线-三角形求交/秒**，可直接通过Vulkan `VK_KHR_ray_tracing_pipeline`扩展访问。

---

## 常见误区

**误区1：RT Core可以独立完成整个光线追踪渲染流程**
RT Core只负责BVH遍历和几何求交，不能执行任何着色计算。纹理采样、光照计算、材质求值均发生在Shader Core。若场景使用了大量Any-Hit着色器（如半透明植被），遍历工作会频繁回到Shader Core，RT Core的加速效果会被着色开销部分抵消。

**误区2：光追硬件单元处理的BVH是应用层直接构建的原始BVH**
实际上，驱动和硬件层会对应用通过`vkBuildAccelerationStructureKHR()`提交的BVH执行**内部重新打包（refit/rebuild）**，将其转换为适合RT Core内存访问模式的内部格式。应用层构建的BLAS/TLAS结构与RT Core实际读取的内存布局并不完全一致，开发者无法直接查看RT Core的内部BVH格式。

**误区3：更多RT Core数量等比例提升性能**
RT Core数量与性能提升并非线性关系。RTX 3090拥有82个RT Core，但其光追性能相比RTX 3080（68个RT Core）的提升幅度远小于12/82的比例差距，因为瓶颈通常在于BVH数据的显存带宽（RT Core需要持续读取加速结构数据），以及着色阶段回到Shader Core后的计算延迟。

---

## 知识关联

学习光追硬件单元需要掌握**BVH加速结构**的原理，包括BLAS（底层加速结构）与TLAS（顶层加速结构）的两级层次划分——RT Core的遍历正是按照先TLAS后BLAS的顺序进行，实例变换（Instance Transform）也在TLAS-to-BLAS跳转时由RT Core内部的矩阵变换单元完成，而非在Shader Core上计算。理解slab法AABB求交和Möller–Trumbore三角形求交算法的数学推导，有助于判断为何RT Core能将这两个操作设计为单周期电路而非可编程指令流。

此外，RT Core与**DirectX Raytracing（DXR）**和**Vulkan Ray Tracing**的API调用链紧密耦合：`TraceRay()`指令在DXIL字节码层面会被驱动翻译为特定的硬件调用序列，触发RT Core接管光线。理解这一软硬件接口有助于在性能分析工具（如NVIDIA Nsight Graphics的光追分析视图）中正确解读RT Core利用率与Shader Core利用率的关系。