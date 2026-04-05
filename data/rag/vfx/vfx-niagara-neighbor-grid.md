---
id: "vfx-niagara-neighbor-grid"
concept: "邻域网格"
domain: "vfx"
subdomain: "niagara"
subdomain_name: "Niagara系统"
difficulty: 4
is_milestone: false
tags: ["高级"]

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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 邻域网格

## 概述

邻域网格（Neighbor Grid 3D）是Unreal Engine Niagara系统中专用于粒子间空间查询的数据结构模块，通过将三维空间划分为均匀格栅，使每个粒子能够在O(1)时间复杂度内找到其周围指定半径范围内的所有相邻粒子。该技术于UE4.25版本正式稳定化，在此之前粒子间的距离检测需要对全体粒子进行O(N²)的暴力遍历，在粒子数量超过数千时性能急剧崩溃。

邻域网格的设计思想来源于计算流体动力学（CFD）中的空间哈希技术。传统粒子系统若要让10,000个粒子互相感知彼此位置，每帧需要约5000万次距离计算；而邻域网格将同等规模粒子的查询代价压缩到约每粒子平均30次局部格元检索，性能差异达到三到四个数量级。这一特性使群集行为模拟、粒子排斥力、流体SPH近似等交互效果从理论变为实时可行。

## 核心原理

### 空间分割与格元索引映射

邻域网格将用户定义的世界空间包围盒等分为NumCellsX × NumCellsY × NumCellsZ个格元。每个格元的边长（Cell Size）由总包围盒尺寸除以各轴格元数量得出：

**CellSize = BoundsExtent × 2 / NumCells**

粒子位置P映射到格元坐标的公式为：

**CellCoord = floor((P - BoundsMin) / CellSize)**

当粒子位置超出预设包围盒时，该粒子不参与邻域查询，因此正确设置Bounds Extent是使用邻域网格的第一个关键参数。格元数量通常在每轴8到64之间选取，格元边长应设置为查询半径的1.5到2倍，过小会导致跨格元查询增多，过大则使单格元粒子数膨胀。

### 写入阶段与读取阶段的Simulation Stage分离

邻域网格**必须配合Simulation Stage使用**，整个工作流分为两个独立Stage。第一个Stage称为"Population Stage"，所有粒子执行 **Neighbor Grid 3D → Set Particle Neighbors** 节点，将自身位置注册到对应格元。第二个Stage称为"Query Stage"，粒子执行 **Neighbor Grid 3D → Get Particles In Neighborhood** 迭代器遍历邻居，在此Stage中可读取邻居的任意属性（位置、速度、颜色等）并据此修改自身状态。若将写入与读取混入同一Stage，格元数据在同一帧内处于不一致状态，会产生依赖执行顺序的竞态错误。

### 最大邻居数与链表容量参数

每个格元内部使用固定大小的链表存储粒子索引，该链表容量由参数 **Max Neighbors Per Cell** 控制，默认值为2，实用场景通常需设置为8到32。该值与NumCellsX × NumCellsY × NumCellsZ的乘积决定了邻域网格消耗的GPU显存总量：一个32×32×32、每格最多16邻居的网格需要约 32³ × 16 × 4 bytes ≈ 67 MB 的缓冲区。Max Neighbors Per Cell设置过小时，超出容量的粒子将被静默丢弃，造成粒子交互不对称的视觉瑕疵——这是该模块最常见的隐性bug来源。

### 查询半径与格元遍历范围

Get Particles In Neighborhood节点接受一个 **Query Radius** 参数，该值需小于或等于CellSize的数倍。在内部实现上，节点以查询粒子所在格元为中心，遍历半径为 ceil(QueryRadius / CellSize) 的立方体格元区域，再对每格内的候选粒子执行精确距离判断。因此QueryRadius与CellSize的比值直接影响遍历格元数量：比值为2时遍历5³=125个格元，比值为4时遍历9³=729个格元，保持比值在1到2之间是性能最优区间。

## 实际应用

**Boid群集模拟**：在鸟群或鱼群效果中，每个个体需要对齐邻居速度（Alignment）、靠近邻居质心（Cohesion）并与过近邻居分离（Separation）。使用邻域网格，10,000只鸟的Boid模拟可在RTX 3080上维持60fps，而暴力O(N²)实现在同样硬件上帧率不足2fps。Population Stage注册位置与速度，Query Stage累加邻居速度向量取均值实现Alignment，累加位置取均值实现Cohesion，检测距离阈值（通常设为CellSize的0.5倍）触发Separation力。

**粒子液体表面张力近似**：SPH（Smoothed Particle Hydrodynamics）流体模拟使用核函数W(r, h)计算压力与粘性，其中h为平滑半径即QueryRadius。邻域网格将每帧密度估算的计算量从O(N²)降至O(N × k)，其中k为平均邻居数量，使实时运行100,000粒子量级的SPH液体成为可能。

**碰撞避让与群体AI粒子**：在城市场景中模拟行人人群时，每个行人粒子通过邻域网格查询2米半径内（对应QueryRadius=200 Unreal Units）的其他行人，计算排斥力方向向量叠加到速度上，避免粒子穿插堆叠，产生自然的人流绕行效果。

## 常见误区

**误区一：在单个Simulation Stage内同时执行写入和读取**。许多初学者将Set与Get节点放入同一Stage以简化图表，导致部分粒子读到的是上一帧数据、另一部分读到本帧已更新数据，群集行为出现方向性偏移或抖动。正确做法是严格分离两个Stage，且Population Stage必须排列在Query Stage之前。

**误区二：将Bounds Extent设置为粒子最大扩散范围的精确边界**。粒子在边界附近移动时若偶尔超出包围盒，该帧不被注册，邻居会瞬间消失产生闪烁。应在预期扩散范围基础上额外增加10%到20%的余量，同时可通过Clamp To Bounds节点将超出粒子推回包围盒内。

**误区三：将Max Neighbors Per Cell设置为与粒子总数相关的大值**。部分开发者为"保险起见"将该值设为1000，导致32×32×32的网格消耗超过4 GB显存直接崩溃。正确理解是该值代表**单个格元**的最大容纳量，格元的物理体积决定了理论最大密度，设置为实际密度峰值的1.5倍即可。

## 知识关联

邻域网格依赖**Simulation Stage**提供多次Pass执行能力，如果不理解Stage的执行顺序控制，写入/读取分离就无从实现——因此Simulation Stage是使用邻域网格的硬性前置知识。邻域网格中的格元索引机制与图形学课程中的空间哈希（Spatial Hashing）和均匀网格加速结构（Uniform Grid BVH）属于同源技术，理解三者的共同前提有助于直觉把握CellSize选取对性能的影响。

后续学习**音频可视化**时，邻域网格的使用模式会以间接方式出现：音频频谱数据驱动粒子位移后，粒子间距发生动态变化，此时需要邻域网格实时重新索引空间分布以维持粒子间的排斥约束，防止音频驱动的位移导致粒子穿插。掌握邻域网格的Bounds参数调整习惯，也直接服务于音频可视化中粒子阵列随Beat扩张时的边界维护需求。