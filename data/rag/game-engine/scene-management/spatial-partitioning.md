---
id: "spatial-partitioning"
concept: "空间分区"
domain: "game-engine"
subdomain: "scene-management"
subdomain_name: "场景管理"
difficulty: 2
is_milestone: false
tags: ["索引"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "pending-rescore"
quality_score: 40.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.4
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 空间分区

## 概述

空间分区（Spatial Partitioning）是游戏引擎场景管理中将三维世界划分为多个子区域，从而加速空间查询的一类数据结构与算法。其核心思想是：若一个物体不在某个区域内，则与该区域相交的查询结果可以直接跳过该物体，将碰撞检测、渲染可见性判断、射线投射等操作的复杂度从 O(n) 降至 O(log n) 甚至更优。

空间分区的研究可追溯至1969年 Bentley 提出的 k-d 树，以及1980年代早期图形学中广泛使用的 BSP（Binary Space Partitioning）树。Quake（1996年）是第一款在商业游戏中将 BSP 树用于完整室内场景可见性预计算的引擎，其 .bsp 文件格式至今仍被 Source 引擎继承。现代引擎（如 Unreal Engine 5 和 Unity）则普遍使用八叉树（Octree）或均匀网格（Uniform Grid）作为运行时动态对象的空间索引。

空间分区直接决定了引擎每帧可处理的实体规模上限。一个未经任何空间分区优化的场景，若存在 10,000 个碰撞体，每帧潜在碰撞测试对数为 n(n-1)/2 ≈ 5000 万次；引入四叉树或八叉树后，平均测试次数可下降至数百次量级。

---

## 核心原理

### 均匀网格（Uniform Grid）

均匀网格将世界空间切割为等大小的单元格（Cell），每个物体根据其 AABB（轴对齐包围盒）注册到它所覆盖的单元格列表中。查询时只需检索目标区域覆盖的单元格集合，时间复杂度在物体均匀分布时接近 O(1)。

均匀网格的主要参数是**格子边长 cellSize**，通常建议设为场景中最大移动物体直径的 1.5～2 倍。若 cellSize 过小，单个物体跨越的格子数爆炸；若 cellSize 过大，每个格子包含的物体数过多，查询效率退化回暴力遍历。均匀网格对静态、密度均匀的场景（如 RTS 游戏的单位管理）效果极好，但对稀疏大场景浪费严重。

### 八叉树（Octree）

八叉树递归地将三维 AABB 沿 X、Y、Z 轴的中点各切一刀，将父节点分裂为 8 个子节点（四叉树 Quadtree 是其在 2D 的对应结构，分为 4 个子节点）。分裂条件通常为：节点内物体数量超过阈值（常用值为 8～16 个），且当前深度未超过最大深度（常用值为 8～12 层）。

设根节点包围盒边长为 L，则第 d 层节点的边长为 L / 2^d。一个深度为 10 的八叉树，最细粒度格子边长为根节点边长的 1/1024。八叉树适合**动静混合场景**：静态物体构建一次后缓存，动态物体每帧重新插入"动态八叉树"层。Unreal Engine 使用层级式 Octree 管理 Actor 的可见性和碰撞查询，其实现位于 `Engine/Source/Runtime/Core/Public/Math/GenericOctree.h`。

### BSP 树（Binary Space Partitioning Tree）

BSP 树使用任意方向的超平面（而非轴对齐平面）将空间递归分为"前"与"后"两个半空间。平面方程为 **ax + by + cz + d = 0**，其中 (a, b, c) 为平面法向量。判断点 P = (x₀, y₀, z₀) 在平面哪一侧，计算 ax₀ + by₀ + cz₀ + d 的正负即可。

BSP 树的最大优势是可以离线预计算场景的**正确深度排序**（画家算法），这正是 Quake 时代用来解决室内场景可见性（PVS，Potentially Visible Sets）的关键。BSP 树的构建代价很高，面数较多的场景可能需要数分钟预计算，因此只适合静态几何体，运行时不可动态修改。BSP 树已基本退出现代实时引擎的动态场景管理，但在 Constructive Solid Geometry（CSG）编辑器和光线追踪预处理中仍有使用。

### 层次包围体（BVH）

BVH（Bounding Volume Hierarchy）是一种自底向上构建的树形空间分区，每个叶节点包含一个几何体，每个内部节点存储子节点的合并包围盒。射线与 BVH 相交测试遵循剪枝规则：若射线不与父节点包围盒相交，则跳过整棵子树。GPU 光线追踪（DXR / Vulkan Ray Tracing）标准的 TLAS/BLAS（Top-Level / Bottom-Level Acceleration Structure）本质上就是两层 BVH。

---

## 实际应用

**碰撞检测宽相（Broad Phase）**：PhysX（Unreal 和 Unity 的物理后端）使用 SAP（Sweep And Prune）结合 AABB 树实现宽相剔除，在 10,000 个刚体场景下将每帧碰撞对候选数量控制在数百以内。

**射线投射（Raycasting）**：Minecraft 的方块拾取使用均匀网格进行射线-方块测试，每次投射只需遍历射线经过的格子序列（DDA 算法），与总方块数无关。

**AI 视野与寻路**：Unreal Engine 的 Environment Query System（EQS）在生成候选点时，依赖八叉树快速查询半径 R 内的所有 Actor，避免遍历全图实体列表。

**编辑器场景拾取**：Unity Editor 的 Scene View 点击选取物体，使用 BVH 进行屏幕空间射线与场景所有 Renderer 的相交测试，而非逐三角面检测。

---

## 常见误区

**误区一：八叉树适用于所有场景类型**
八叉树在物体分布极度不均匀（如大型开放世界，99% 的物体集中在地表 5% 的区域）时会退化为不平衡树，导致某些叶节点包含大量物体。此时分层网格（Hierarchical Grid）或 k-d 树通常效果更好，后者能根据数据分布自适应选择分割平面。

**误区二：BSP 树可以用于动态物体**
BSP 树的构建（特别是多边形分裂步骤）时间复杂度为 O(n²) 甚至更高，无法在运行时对移动物体重建。把 BSP 用于管理动态角色或抛射物会造成每帧毫秒级卡顿。动态物体应使用可增量更新的结构，如松散八叉树（Loose Octree）或动态 AABB 树。

**误区三：空间分区节点数越多越快**
将八叉树最大深度设置过大（如 20 层），导致叶节点边长小于 1 厘米，单次插入需要沿树路径更新 20 个节点，内存访问的缓存缺失（Cache Miss）反而使总体性能低于深度为 8 的版本。游戏引擎性能分析工具（如 Unreal Insights）中，可以通过追踪 `PhysicsTree::Insert` 耗时来诊断此类问题。

---

## 知识关联

**前置概念——场景图（Scene Graph）**：场景图描述物体的层级变换关系（父子节点的 Transform 继承），而空间分区描述物体的**空间位置索引**关系。两者独立存在于引擎中：场景图节点变换更新后，引擎需将新的世界坐标 AABB 同步写入空间分区结构。理解场景图的世界坐标计算是正确使用空间分区插入接口的前提。

**后续概念——视锥剔除（Frustum Culling）**：视锥剔除需要快速找出摄像机视锥体内的所有物体，其高效实现依赖空间分区提供候选集——先用视锥与八叉树/BVH 节点的包围盒做快速测试，通过的节点再做精确的每物体视锥测试，从而避免对场景内所有物体逐一判断。

**后续概念——环境查询系统（EQS）与程序化放置**：EQS 的"查询半径 R 内所有障碍物"以及程序化放置的"避免在已有物体 D 米范围内重复生成"，都需要调用空间分区的**球形范围查询**或**AABB 重叠查询**接口。没有高效的空间分区，这两个系统在实体数量超过数千时将无法在单帧预算内完成计算。