---
id: "cg-bvh"
concept: "BVH加速结构"
domain: "computer-graphics"
subdomain: "ray-tracing"
subdomain_name: "光线追踪"
difficulty: 3
is_milestone: false
tags: ["算法"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# BVH加速结构

## 概述

BVH（Bounding Volume Hierarchy，层次包围盒）是光线追踪渲染中用于加速光线-场景求交计算的树形空间数据结构。其核心思想是将场景中的几何体（三角形）递归地分组，并为每组计算一个紧包围盒（AABB，轴对齐包围盒），形成一棵二叉树。当一条光线射入场景时，首先与根节点的包围盒求交，若相交则递归检测子节点，直到到达叶节点才与实际三角形求交。这种层次剔除策略使求交复杂度从O(N)降低到平均O(log N)。

BVH结构最早在1980年由Clark提出用于场景管理，随后被广泛应用于离线渲染器（如Pixar的RenderMan）。相比同期的KD-Tree，BVH的构建速度更快，且对动态场景的更新更友好——重新拟合（refit）叶节点包围盒不需要重建整棵树。2018年NVIDIA发布Turing架构GPU，首次在硬件层面实现了专用的BVH遍历单元（RT Core），使BVH成为实时光线追踪的标准加速结构。

## 核心原理

### AABB包围盒表示

BVH中每个节点存储一个轴对齐包围盒（Axis-Aligned Bounding Box），用两个三维向量表示：最小角点 $\mathbf{p}_{min} = (x_{min}, y_{min}, z_{min})$ 和最大角点 $\mathbf{p}_{max} = (x_{max}, y_{max}, z_{max})$。光线与AABB的求交使用"slab法"：对x、y、z三对平面分别计算光线进入时间 $t_{min}$ 和离开时间 $t_{max}$，若三个区间的交集 $[\max(t_{x,min}, t_{y,min}, t_{z,min}),\ \min(t_{x,max}, t_{y,max}, t_{z,max})]$ 非空且不在光线起点之后，则判定相交。AABB的计算量约为6次除法、6次比较，远低于三角形求交的约20次浮点运算。

### SAH构建算法

表面积启发式（Surface Area Heuristic，SAH）是目前质量最高的BVH构建策略。其代价函数如下：

$$C = C_{trav} + \frac{S_A}{S_P} \cdot N_A \cdot C_{isect} + \frac{S_B}{S_P} \cdot N_B \cdot C_{isect}$$

其中 $C_{trav}$ 为遍历内部节点的代价，$S_P$ 为父节点包围盒的表面积，$S_A, S_B$ 分别为两个子节点的表面积，$N_A, N_B$ 为各子节点所含三角形数量，$C_{isect}$ 为单次三角形求交代价（通常取 $C_{trav} : C_{isect} = 1:8$）。构建时对每个节点沿三个坐标轴枚举分割平面（通常将每轴等分为32个桶），选择代价最小的分割方案。完整SAH构建复杂度为 $O(N \log^2 N)$，生成的树质量接近最优。

### LBVH：线性快速构建

LBVH（Linear BVH）利用莫顿码（Morton Code）实现 $O(N \log N)$ 甚至近似 $O(N)$ 的并行构建，特别适合GPU场景。具体步骤：①计算每个三角形质心的三维莫顿码（通常30位，每轴10位）；②对莫顿码进行基数排序；③根据排序后序列中相邻莫顿码的最高不同位（highest differing bit）递归划分，生成树结构。LBVH的遍历效率比SAH低约15%~30%，但GPU上的构建时间可比SAH快10倍以上，因此常用于动态场景（粒子、布料）的每帧重建，或作为TLAS（Top-Level Acceleration Structure）的快速更新手段。

### BVH遍历策略

遍历时维护一个栈存储待访问节点，采用"最近子节点优先"策略：当光线同时击中两个子节点时，先遍历较近的子节点有更大概率提前更新最近命中距离 $t_{hit}$，从而剪枝另一子节点。现代实现还会区分TLAS（Top-Level Acceleration Structure，管理BVH实例）和BLAS（Bottom-Level Acceleration Structure，管理单个mesh的三角形），两级结构使场景实例化（Instancing）成为可能：同一个BLAS可被多个TLAS节点引用，极大降低内存占用。

## 实际应用

**静态场景离线渲染**：Blender的Cycles渲染器使用带有BVH拆分（Split BVH）的SAH变体，允许一个三角形的AABB出现在多个叶节点中，换取更紧的包围，对细长三角形场景（如头发）的求交效率提升可达40%。

**实时游戏渲染**：Unreal Engine 5的Lumen系统将场景划分为TLAS+BLAS两级结构，每帧对TLAS执行快速重建以支持动态物体，而静态BLAS使用预计算SAH结构。帧内TLAS重建采用基于GPU的LBVH算法，在RTX 3080上可在0.3ms内完成包含数千个实例的场景更新。

**光追降噪前的重要性采样**：路径追踪中的多重重要性采样（MIS）需要对光源采样，BVH的每个内部节点可附加子树内所有光源的辐射度之和，实现 $O(\log N)$ 的光源采样，这种结构称为光源BVH（Light BVH），在Disney的Hyperion渲染器中有实际部署。

## 常见误区

**误区1：叶节点只能存储单个三角形**。实践中叶节点通常存储4~8个三角形。SAH代价函数中存在一个叶节点基础代价 $C_{leaf}$，当继续分裂的代价高于直接在叶节点做线性求交时，停止分裂。过度分裂反而因节点内存访问碎片化导致cache miss增加，性能下降。

**误区2：BVH一旦构建就无法更新**。BVH支持两种动态更新：①**Refit（重新拟合）**，仅自底向上更新包围盒大小，不改变树拓扑，适合小幅形变（如骨骼动画），复杂度 $O(N)$；②**Rebuild（重建）**，对于大幅运动场景完整重建。NVIDIA OptiX API明确区分了`FAST_BUILD`（速度优先，类似LBVH）和`FAST_TRACE`（质量优先，类似SAH）两种构建标志，对应这两种策略的权衡。

**误区3：BVH节点数量等于三角形数量**。一棵包含 $N$ 个叶节点的完全二叉BVH恰好有 $2N-1$ 个节点。若使用宽树（4叉或8叉BVH），节点总数约为 $\frac{4N}{3}$，但每个节点需同时测试4个或8个AABB，可用SIMD指令（SSE/AVX）并行化处理，NVIDIA研究表明4叉BVH在GPU上比2叉BVH遍历性能高约20%。

## 知识关联

BVH加速结构直接依赖**光线求交**的基础知识——理解光线参数方程 $\mathbf{r}(t) = \mathbf{o} + t\mathbf{d}$ 与AABB/三角形的求交算法（Möller–Trumbore方法），才能理解BVH剪枝逻辑中 $t_{hit}$ 的更新机制。SAH代价函数中表面积项 $S/S_P$ 的概率解释来自光线投射的几何概率模型。

学习BVH之后，可直接进入**RTX硬件加速**和**光追硬件单元**的内容：NVIDIA RT Core在硬件层实现了AABB求交测试和三角形求交测试的固定功能流水线，其输入正是符合DXR/Vulkan Ray Tracing规范的TLAS+BLAS两级BVH结构。理解软件层BVH的遍历栈机制，有助于分析RT Core中并发遍历请求的调度方式，以及`TraceRay()`调用的性能瓶颈来源。