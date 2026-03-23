---
id: "cg-kd-tree"
concept: "KD-Tree"
domain: "computer-graphics"
subdomain: "ray-tracing"
subdomain_name: "光线追踪"
difficulty: 3
is_milestone: false
tags: ["算法"]

# Quality Metadata (Schema v2)
content_version: 6
quality_tier: "pending-rescore"
quality_score: 40.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.407
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# KD-Tree（K维树）

## 概述

KD-Tree（K-Dimensional Tree）是一种将K维空间递归地划分为轴对齐半空间的二叉树数据结构。在光线追踪领域，KD-Tree通常工作在三维空间（K=3），其核心思想是通过将场景的轴对齐包围盒（AABB）沿某一坐标轴平面反复二分，将场景中的几何图元组织成层次结构，使光线求交的时间复杂度从朴素的O(n)降低至平均O(log n)。

KD-Tree由Jon Louis Bentley于1975年在论文《Multidimensional binary search trees used for associative searching》中提出，最初用于多维数据的最近邻搜索。1980年代后，KD-Tree被引入光线追踪领域，成为加速结构的主流选择之一。在2000年代之前，KD-Tree曾是离线渲染器（如PBRT v1）的首选加速结构，其后逐渐被BVH（层次包围体）部分取代，但在点云处理和静态场景渲染中至今仍被广泛使用。

KD-Tree对光线追踪的意义在于：在一个包含100万个三角形的场景中，不使用任何加速结构需要逐一测试100万次求交，而深度约为20层的KD-Tree理论上只需测试约20~40个节点，效率提升达数万倍。这种加速效果在静态场景中尤为显著。

---

## 核心原理

### 1. 空间划分策略

KD-Tree的每个内部节点存储一个**分割平面**，该平面平行于某一坐标轴（X、Y或Z），由两个参数描述：分割轴（axis ∈ {0,1,2}）和分割位置（split_pos，一个浮点数）。节点将当前AABB沿该平面一分为二，所有图元按其包围盒与分割平面的关系分配到左子树或右子树——若图元跨越分割平面，则**同时存入两侧**（这是KD-Tree与排序数组不同的关键特性，会造成图元重复存储）。

常见的分割轴选择策略有三种：
- **循环切换**：按X→Y→Z→X顺序轮换，实现简单但效果一般。
- **最长轴优先**：每次选当前AABB最长的那条轴，确保子节点形状趋于立方体，减少细长节点的出现。
- **SAH（Surface Area Heuristic，表面积启发式）**：计算代价函数 C = C_trav + (S_L/S_parent)·N_L·C_isect + (S_R/S_parent)·N_R·C_isect，其中S表示对应AABB的表面积，N_L、N_R为两侧图元数量，C_trav为遍历代价，C_isect为求交代价（通常取C_trav=1, C_isect=80）。SAH能找到使总体代价最小的分割位置，是构建高质量KD-Tree的标准方法。

### 2. 树的构建终止条件

KD-Tree的递归构建在以下两个条件之一满足时停止，形成**叶节点**：
- 当前节点包含的图元数量 ≤ 预设阈值（通常为1~8个三角形）。
- 当前递归深度达到上限（一般设为 `8 + 1.3 × log₂(N)`，其中N为场景总图元数）。

叶节点直接存储图元列表（或图元索引），光线在此处执行实际的几何求交运算。

### 3. 光线遍历算法

KD-Tree的遍历采用**栈辅助的前序遍历**。对于给定光线 r(t) = o + t·d，遍历步骤如下：

1. 首先与根节点的AABB做光线-AABB求交，得到区间 [t_near, t_far]。若不相交则光线错过整个场景。
2. 在内部节点处，计算光线与分割平面的交点参数 t_split = (split_pos - o[axis]) / d[axis]。
3. 根据 t_split 与 [t_near, t_far] 的关系，决定遍历顺序：
   - 若 t_split < t_near：只需遍历远侧子树。
   - 若 t_split > t_far：只需遍历近侧子树。
   - 否则：先遍历近侧子树，将远侧压栈，待近侧遍历完毕后弹出继续。
4. 当在某叶节点找到交点时，若交点的 t 值落在 [t_near, t_split] 内（即交点位于近侧子节点空间内），可立即返回，无需继续处理栈中的远侧节点——这是KD-Tree的**早期终止优化**，是其遍历效率的关键所在。

---

## 实际应用

**PBRT渲染器中的KD-Tree实现**：PBRT（Physically Based Rendering Toolkit）v1和v2均以KD-Tree作为默认加速结构，其实现采用SAH构建策略，节点内存布局经过精心设计：每个节点仅占用8字节，其中低2位标记分割轴（00=X，01=Y，10=Z，11=叶节点），其余位存储分割位置（浮点数）或图元索引。这种紧凑布局有效提升了CPU缓存命中率。

**静态建筑可视化场景**：在包含约50万个三角形的室内建筑模型中，使用SAH-KD-Tree后，典型光线（主光线+阴影光线）的平均遍历节点数可控制在30~60个，相比BVH在此类高度不均匀场景中的表现相当甚至略优，原因在于KD-Tree的空间划分对重叠度低的几何体更精确。

**点云最近邻加速**：在光子映射（Photon Mapping）算法中，KD-Tree用于存储光子并加速K近邻查询（kNN search）。与光线求交的遍历不同，kNN查询需要维护一个大小为K的最大堆，并以当前最远光子距离作为剪枝球半径，这与光线遍历使用的t_split剪枝逻辑完全不同。

---

## 常见误区

**误区一：认为KD-Tree节点不重复存储图元**
许多初学者误以为每个三角形只出现在KD-Tree的一个叶节点中。事实上，由于三角形可能跨越分割平面，同一个三角形可以被复制到多个叶节点。在极端情况下，一个"坏"的分割可能导致场景内所有图元都出现在两侧，树的图元总存储量可达原始数量的数倍。SAH正是通过最小化代价函数来抑制这种无效分割。

**误区二：认为KD-Tree比BVH对动态场景同样适用**
KD-Tree以场景的全局空间为划分对象，其分割平面和层次结构在构建后是固定的。当场景中有物体运动时，必须完整重建KD-Tree，代价极高。而BVH只需对发生运动的节点做局部重拟合（refit）。这是现代实时光线追踪（如DXR/Vulkan Ray Tracing）几乎全部采用BVH而非KD-Tree的根本原因。

**误区三：KD-Tree深度越深越好**
增加KD-Tree深度会细化空间划分，但超过`8 + 1.3 × log₂(N)`的经验上限后，收益急剧递减：更深的树意味着更多的遍历节点和栈操作开销，叶节点包围盒的重叠比例也可能上升，反而导致性能下降。此外，过深的树会占用更多内存并破坏缓存局部性。

---

## 知识关联

KD-Tree的遍历算法直接建立在**光线-AABB求交**的基础上：每个内部节点的分割平面求交本质上是光线与无限平面的t值计算（t_split = (split_pos - o[axis]) / d[axis]），而进入/离开判断（t_near, t_far更新）则来自slab法求交的逻辑。若不能正确处理d[axis]=0的退化情况（此时分割平面与光线平行），KD-Tree遍历会产生除零错误，需用IEEE 754无穷大规则或显式判断处理。

在加速结构的谱系中，KD-Tree属于**空间划分（Space Subdivision）**类方法，与之对应的是**对象划分（Object Subdivision）**的BVH。理解KD-Tree的设计取舍——精确的空间剪枝能力与不支持动态更新之间的矛盾——是深入学习BVH、HLBVH（Hierarchical LBVH）等后续结构时的重要对照参考。光子映射中对KD-Tree的kNN应用，则展示了同一数据结构如何通过改变遍历目标函数，服务于完全不同的查询语义。
