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


# 光追硬件单元

## 概述

光追硬件单元是现代GPU中专门负责加速光线与场景几何体求交计算的固定功能电路模块。NVIDIA将其命名为RT Core，AMD将其称为Ray Accelerator，两者的核心任务相同：在硬件层面执行BVH（层次包围盒）树的节点遍历与光线-三角形求交测试，从而将这部分计算从着色器程序中卸载出来，让CUDA核心或流处理器专注于光照计算。NVIDIA于2018年随Turing架构（RTX 20系列）首次将RT Core引入消费级GPU，这是图形硬件史上首次为光线追踪专设独立功能单元。

在没有光追硬件单元之前，软件光线追踪必须用通用着色器遍历BVH树，每次光线-AABB（轴对齐包围盒）测试都要占用着色器指令槽，导致GPU利用率极低。以RTX 2080为例，其RT Core在光线-盒子测试吞吐量上比纯着色器实现快约10倍，使实时光线追踪在消费级硬件上首次具备可行性。光追硬件单元的引入从根本上改变了实时渲染管线的分工逻辑。

## 核心原理

### BVH遍历的硬件流水线

RT Core内部实现了一条专用的BVH遍历状态机。当着色器通过`TraceRay()`（DXR/DirectX Raytracing API）或`optixTrace()`（OptiX框架）发起光线追踪调用时，RT Core接管该光线，维护一个节点栈（node stack），按照深度优先顺序测试BVH的内部节点。每个内部节点包含两个子节点的AABB信息，RT Core同时对两个子AABB执行光线-盒子求交（即Slab方法：计算光线参数 $t_{min} = \max(\frac{x_{min}-o_x}{d_x}, \frac{y_{min}-o_y}{d_y}, \frac{z_{min}-o_z}{d_z})$，$t_{max} = \min(...)$，若 $t_{min} \leq t_{max}$ 则相交），并根据结果决定是否进入子树。这一遍历逻辑完全固化在硬件中，无需消耗着色器指令。

### 光线-三角形求交单元

当BVH遍历到达叶子节点时，RT Core中的三角形求交单元执行Möller–Trumbore算法的硬件实现。该算法将求交问题转化为求解线性方程组：令 $\mathbf{e}_1 = V_1 - V_0$，$\mathbf{e}_2 = V_2 - V_0$，$\mathbf{h} = \mathbf{d} \times \mathbf{e}_2$，则重心坐标 $u = \frac{(\mathbf{o}-V_0)\cdot\mathbf{h}}{\mathbf{e}_1 \cdot \mathbf{h}}$，硬件以单时钟周期或极低延迟完成上述浮点运算并返回命中参数 $t$、重心坐标 $(u, v)$。AMD RDNA 2架构的Ray Accelerator每个Shader Engine包含一个专用的光线-三角形相交单元，其最大支持同时处理的光线数与Shader Engine中的CU数量直接绑定。

### 与着色器的协同调度

RT Core并非独立运行，而是与着色器管线紧耦合。NVIDIA Ampere（RTX 30系列）中每个SM配备1个RT Core，Ada Lovelace（RTX 40系列）将RT Core的遍历吞吐量提升了约2倍，并新增了对不透明度微图（Opacity Micromaps）的硬件支持，允许以次三角形精度标记透明区域，减少着色器调用。当RT Core发现命中一个标记为非透明的三角形时，它可以在不唤醒着色器的情况下直接跳过该图元，极大减少了植被、栅栏等场景的性能瓶颈。RT Core完成求交后，将结果写回光线payload，再由GPU调度器触发相应的任意命中着色器（Any Hit Shader）或最近命中着色器（Closest Hit Shader）。

## 实际应用

**游戏中的阴影与反射加速**：在《赛博朋克2077》的光线追踪反射实现中，GPU每帧需要发射数亿条次级光线。RT Core将BVH遍历从着色器时钟中解耦，使RTX 3080在4K分辨率下的光追反射帧率相比纯软件实现提升约3-4倍。没有专用硬件，实时光追反射在该场景规模下完全不可行。

**离线渲染与DCC工具集成**：Pixar的RenderMan 24及以后版本支持通过OptiX 7调用RT Core执行GPU离线渲染，将原本需要数小时的帧渲染时间缩短至分钟级。在这一工作流中，RT Core负责所有BVH遍历，CUDA核心执行路径积分（Path Integration）的蒙特卡洛采样计算，两者并行运行，互不阻塞。

**AI降噪与光追协同**：现代光追管线通常仅每像素发射1-4条光线（欠采样），再由Tensor Core运行的DLSS或XeSS进行降噪重建。RT Core在此流程中的角色是以极低延迟完成稀疏光线的高质量求交，保证降噪器获得准确的几何命中信息（世界坐标、法线、材质ID），这些信息质量直接影响降噪输出的正确性。

## 常见误区

**误区一：RT Core可以独立执行完整的光线追踪渲染**。RT Core仅处理BVH遍历和几何求交两个步骤，不执行任何光照计算、纹理采样或材质求值。着色器（Closest Hit Shader、Miss Shader等）仍运行在普通的流处理器上。对于简单场景，RT Core空转等待着色器的时间甚至可能成为瓶颈，这时启用硬件光追未必比软件光追快。

**误区二：更多RT Core数量等于更好的光追性能**。RTX 4090拥有128个RT Core（每个SM一个），但实际光追性能瓶颈往往是着色器吞吐量或内存带宽，而非RT Core本身。当场景BVH质量差（如频繁动态更新导致BVH退化）时，RT Core处理的节点测试数量会急剧增加，此时优化BVH构建算法（如SAH启发式，Surface Area Heuristic）比增加RT Core数量更有效。

**误区三：软件BVH遍历与RT Core遍历的行为完全一致**。RT Core使用的BVH格式是厂商私有的，NVIDIA的压缩宽BVH（Compressed Wide BVH，有资料显示Turing使用BVH8结构）与标准二叉BVH的遍历顺序和剪枝策略存在差异，直接用CPU端生成的BVH结构传入GPU并不能得到最优性能——驱动层或构建库（如OptiX的`optixAccelBuild`）会自动将用户提供的三角形数据重新构建为硬件最优格式。

## 知识关联

光追硬件单元的前置知识是BVH加速结构：理解BVH如何将场景几何体组织为层次AABB树，是理解RT Core内部状态机和节点栈操作的必要基础。SAH（表面积启发式）构建策略决定了BVH树的质量，直接影响RT Core每条光线平均需要测试的节点数量，而TLAS（顶层加速结构）与BLAS（底层加速结构）的两级BVH设计是DXR和Vulkan Ray Tracing API中RT Core工作的标准模式，BLAS对应单个网格的几何体BVH，TLAS对应场景实例化层级，RT Core按先TLAS后BLAS的顺序递归遍历。掌握光追硬件单元的工作方式，是进一步理解光追降噪管线、DLSS 3.5光线重建以及下一代全局光照算法（如硬件加速的Lumen HWRT模式）如何调度GPU资源的关键出发点。