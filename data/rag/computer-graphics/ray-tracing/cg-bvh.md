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
quality_tier: "pending-rescore"
quality_score: 42.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.406
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# BVH加速结构

## 概述

BVH（Bounding Volume Hierarchy，层次包围盒）是光线追踪中用于加速光线与场景几何体求交的树形空间数据结构。其核心思想是将场景中的所有三角形按空间关系组织成一棵二叉树，每个内部节点存储其子树中所有几何体的轴对齐包围盒（AABB），叶节点则直接存储若干三角形图元。当一条光线与某节点的AABB不相交时，该节点整个子树中的所有三角形可被立刻跳过，从而将朴素O(n)逐三角形测试降低到平均O(log n)级别。

BVH的概念最早由Clark于1976年提出，用于可见性剔除。直到1990年代，Kay和Kajiya将其引入光线追踪领域，并提出了成本函数驱动的构建方法。2009年前后，随着GPU并行计算的普及，针对GPU的LBVH（Linear BVH）算法被提出，使BVH构建时间缩短至毫秒量级，成为现代实时光线追踪的基础。2018年NVIDIA Turing架构推出RT Core专用硬件单元，其本质是固化的BVH遍历电路，充分说明BVH已成为实时光追的标准加速结构。

与kd-tree相比，BVH的每个图元只出现在树的一个叶节点中（kd-tree允许图元跨越分割平面时被重复存储），因此BVH占用内存更可预测，且场景动态变化时只需局部更新而非重建整棵树，这是BVH在游戏引擎中替代kd-tree成为主流的根本原因。

---

## 核心原理

### AABB与光线-盒求交

每个BVH节点存储一个轴对齐包围盒，定义为三对区间 [x_min, x_max] × [y_min, y_max] × [z_min, z_max]。光线表示为 **P**(t) = **O** + t·**D**，光线与AABB的求交使用"slab方法"：对每条轴分别计算进入时刻 t_near 和离开时刻 t_far，最终取三轴的 max(t_near) 与 min(t_far)，若 max(t_near) ≤ min(t_far) 且 t_far ≥ 0，则相交。此计算仅需6次除法和6次比较，是BVH快速剔除的计算基础。

### SAH构建算法

表面积启发式（Surface Area Heuristic，SAH）是目前质量最高的BVH离线构建算法，由MacDonald和Booth于1990年正式提出。SAH的代价函数为：

> **C = C_trav + (S_L / S_P) × N_L × C_isect + (S_R / S_P) × N_R × C_isect**

其中 C_trav 是遍历一个内部节点的固定代价（通常取1），C_isect 是单次三角形求交代价（通常取1.2~1.5），S_L、S_R 是左右子节点AABB的表面积，S_P 是父节点AABB的表面积，N_L、N_R 是左右子节点中的图元数量。构建时沿x、y、z三轴分别扫描所有可能的分割位置（实践中取每轴8~32个候选分割桶），选择使 C 最小的分割方案。SAH构建的时间复杂度为 O(n log²n)，生成的BVH通常比中点分割法少30%~50%的光线-盒测试次数。

### LBVH算法与Morton码

LBVH（Linear BVH）由Lauterbach等人于2009年提出，其核心是将三维空间坐标映射为一维Morton码（Z曲线编码）。具体做法是将每个图元质心坐标归一化到 [0,1]³，然后对每个维度取10位整数，交错排列三个维度的位得到30位Morton码。将所有图元按Morton码排序后（GPU基数排序约需数毫秒），相邻Morton码的图元在空间上也相邻，因此可以用Karras 2012年提出的并行算法在GPU上同时确定所有内部节点的分割位置，整棵树构建时间与图元数量呈线性关系。对于包含100万三角形的场景，LBVH在RTX 3090上约需2~5毫秒完成构建，使每帧重建BVH成为可能。

### BVH遍历策略

遍历时维护一个栈存储待访问节点。对于每个内部节点，先测试两个子节点的AABB，若两者均命中，则优先访问距离较近（t_near较小）的子节点，这种"近子节点优先"策略能更早找到命中点并更新光线的 t_max，从而剔除更多远处节点。实践中每条光线平均需访问约 log₂(N) 个节点数量级的节点，对于100万个三角形约需检测20~50个节点。

---

## 实际应用

**静态场景的离线渲染**：在Blender Cycles、PBRT等离线渲染器中，场景在渲染前使用SAH算法构建一次高质量BVH，叶节点通常存储1~4个三角形。PBRT-v4的BVH实现中，叶节点阈值默认为4个图元，当图元数量少于此阈值时停止递归分割。

**动态场景的实时光追**：在DXR（DirectX Raytracing）API体系中，BVH被称为加速结构（Acceleration Structure），分为BLAS（Bottom-Level AS，存储单个网格的三角形）和TLAS（Top-Level AS，存储各BLAS实例的变换矩阵）两层。刚体运动时只需更新TLAS中的变换矩阵，无需重建BLAS，每帧TLAS重建约消耗0.1~0.5毫秒。骨骼动画导致网格顶点位移时，则需对BLAS执行Refit操作（仅更新AABB，不改变树拓扑），比完整重建快3~5倍但BVH质量会随时间退化。

**光子映射加速**：BVH同样可用于加速光子映射中的最近邻光子查询，但此场景下kd-tree因点查询特性更优，BVH主要用于光子发射阶段的几何求交。

---

## 常见误区

**误区一：BVH的深度越浅越好**。实际上叶节点存储单个三角形且树完全平衡时，遍历深度约为 log₂(N)，但SAH有时会故意创建不平衡的树——将包含大量小三角形的密集区域分配到更深的子树中，而将空旷区域尽早剔除，这样反而减少总代价。一棵深度不均匀的SAH树往往比强制平衡的BVH性能高20%以上。

**误区二：LBVH质量等同于SAH**。LBVH构建速度虽快，但由于Morton码排序只近似空间局部性（特别是在Z曲线跨越象限边界处），其生成的BVH质量通常比SAH差15%~25%（以光线-图元测试次数衡量）。因此离线渲染仍优先用SAH，实时渲染中才权衡构建速度选择LBVH或HLBVH（Hierarchical LBVH，前几层用SAH后几层用LBVH的混合方案）。

**误区三：更新比重建总是更快**。对于变形幅度超过30%的蒙皮网格，多帧连续Refit后AABB重叠度（overlap）急剧增加，光线遍历效率可能下降至接近无加速结构的线性搜索。此时应定期（如每隔5~10帧）完整重建BLAS，而非无限期Refit。

---

## 知识关联

BVH加速结构以**光线-AABB求交**和**光线-三角形求交**（Möller-Trumbore算法）为直接前置计算单元，没有这两种求交测试，BVH的每个节点和叶节点都无法完成访问。SAH代价函数中的表面积比率项直接来源于光线与凸体相交的概率积分推导，理解其数学含义需要熟悉蒙特卡洛积分的基本概念。

在后续主题中，**RTX硬件加速**（RT Core）将BVH的AABB遍历和三角形求交固化为专用电路，其输入格式正是DXR标准的BLAS/TLAS两层BVH结构；**光追硬件单元**的设计约束（如栈深度限制为64层、节点宽度为4叉而非二叉以提高SIMD效率）反过来影响了软件层面BVH的构建参数选择。理解BVH的软件实现是读懂RT Core微架构白皮书的必要前提。
