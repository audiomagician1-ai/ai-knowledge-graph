---
id: "navmesh-engine"
concept: "导航网格系统"
domain: "game-engine"
subdomain: "physics-engine"
subdomain_name: "物理引擎"
difficulty: 2
is_milestone: false
tags: ["AI"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 44.2
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.464
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 导航网格系统

## 概述

导航网格系统（Navigation Mesh，简称 NavMesh）是游戏引擎中用于 AI 代理寻路的空间表示技术。它将游戏世界的可行走区域预先烘焙为一组相互连接的凸多边形（Convex Polygon），AI 角色通过在这些多边形上搜索路径来实现从起点到终点的导航，而无需逐像素或逐体素地检测碰撞。

NavMesh 的概念由 Greg Snook 于 2000 年在《Game Programming Gems》文章"Simplified 3D Movement and Pathfinding Using Navigation Meshes"中正式提出并推广。在此之前，游戏 AI 寻路主要依赖路点图（Waypoint Graph），开发者需要手动放置数百个路点节点，维护成本极高且覆盖精度有限。NavMesh 将可行走表面作为连续区域建模，显著减少了路径节点数量，同时提升了路径的自然流畅度。

NavMesh 相较于路点图的核心优势在于：单个凸多边形内部的任意两点之间可以直线穿行而无需额外碰撞检测，因此 A* 算法只需在多边形粒度而非像素粒度上运算，大型场景中搜索节点数量可从数万个降低至数百个，寻路开销减少约 90% 以上。

---

## 核心原理

### NavMesh 的生成流程

NavMesh 生成（Baking）分为体素化、区域划分和多边形化三个阶段。

**第一阶段：体素化（Voxelization）**
引擎将场景几何体光栅化为三维体素网格，Unity 默认体素大小（Cell Size）为 0.3 单位。系统标记每个体素表面是否可行走，判断标准包括：法线角度不超过 `Max Slope`（Unity 默认 45°）、距离障碍物的水平间距（Agent Radius）和垂直净空高度（Agent Height）是否满足代理体型要求。

**第二阶段：区域划分（Region Segmentation）**
体素化完成后，系统通过距离场（Distance Field）算法将可行走体素聚合为若干独立区域，常用的算法包括 Watershed 分割。Recast 库（被 Unity 和 Unreal 底层使用）采用此方法，每个区域后续独立生成轮廓。

**第三阶段：多边形化（Polygon Generation）**
每个区域的轮廓被简化并三角剖分，最终输出一组**凸多边形**。之所以强制要求凸多边形，是因为凸集内部任意两点的连线不会超出多边形边界，这保证了代理在多边形内直线移动时始终在可行走面上。相邻多边形之间通过共享边（Portal Edge）连接，构成导航图。

### A* 在 NavMesh 上的寻路过程

寻路时，引擎首先将代理当前位置和目标位置分别映射（Project）到最近的 NavMesh 多边形，然后在多边形图上运行 A* 算法，得到一条多边形序列（Polygon Corridor）。原始多边形走廊通常不是最短路径，因此需要进一步运行**漏斗算法（Funnel Algorithm）**，将走廊收缩为由多边形共享边的端点（Apex）组成的折线路径，时间复杂度为 O(n)，其中 n 为走廊多边形数量。最终路径是一系列三维航点（Waypoints），代理依次转向各航点前进。

启发函数通常采用欧几里得距离：`h(n) = √((x₂-x₁)² + (y₂-y₁)² + (z₂-z₁)²)`，在三维 NavMesh 上保持可接受性（Admissible），不会高估实际代价。

### 动态障碍与 NavMesh 的实时更新

静态烘焙的 NavMesh 无法反映运行时变化的障碍物。处理动态障碍有两种主流机制：

**NavMesh Obstacle（障碍物组件）**：Unity 的 `NavMeshObstacle` 和 Unreal 的 `NavModifierVolume` 允许在运行时将碰撞体标记为障碍。Carve 模式会在 NavMesh 上"切除"障碍物占据的区域，生成新的多边形边界；非 Carve 模式仅触发局部回避（Local Avoidance），不修改网格拓扑。Carve 操作有最小移动阈值（Unity 默认 0.1 单位），避免频繁重新烘焙。

**局部回避（Local Avoidance，RVO）**：速度障碍（Velocity Obstacle）算法的变体 ORCA（Optimal Reciprocal Collision Avoidance）允许多个代理在不重新生成 NavMesh 的前提下互相避让。ORCA 假设每对代理共同承担一半回避责任，可在单帧内以 O(n²) 复杂度计算 n 个代理的无碰撞速度，适合处理 100 人以下规模的人群场景。

---

## 实际应用

**开放世界 NPC 巡逻**：《荒野大镖客：救赎 2》中城镇 NPC 的日常路径使用预烘焙 NavMesh，建筑内外通过 NavLink（Off-Mesh Link）连接，允许角色执行翻越矮墙、推开大门等跨越 NavMesh 间隙的行为。Off-Mesh Link 是连接两个不直接相邻多边形区域的有向或双向桥接，可附带动画触发事件。

**RTS 单位移动**：《星际争霸 II》采用 NavMesh 结合流场（Flow Field）的混合方案，对于大规模军队移动，流场预计算每个多边形朝向目标的最优速度向量，避免所有单位重复执行 A* 计算，将寻路成本从 O(n) 次 A* 降低到 1 次 A* + O(1) 次查表。

**多层建筑导航**：NavMesh 可以分层（NavMesh Layer / Area Type）标记不同区域的移动代价，例如将泥地标记为代价系数 2、沼泽标记为代价系数 4，A* 在计算路径代价时会自动绕开高代价区域或选择更短的高代价路径，实现地形感知寻路。

---

## 常见误区

**误区一：NavMesh 精度越高越好**
增大体素分辨率（缩小 Cell Size）会使烘焙时间和内存占用呈立方级增长。将 Cell Size 从 0.3 缩小到 0.1，体素数量增加约 27 倍。在绝大多数第三人称游戏中，0.25～0.33 单位的 Cell Size 已足够精确，过度提升分辨率只会增加烘焙时间而对实际寻路质量改善有限。

**误区二：动态障碍物可以实时"Carve"而无性能代价**
Carve 操作需要重新三角剖分受影响区域，每次 Carve 在 Unity 中默认有约 1 帧的延迟，且同时存在多个 Carving Obstacle 时，更新开销会叠加。对于频繁移动的物体（如子弹、快速移动的载具），应使用 RVO 局部回避而非 Carve，否则每帧触发重新烘焙会导致明显的性能抖动。

**误区三：NavMesh 代理会精确遵循物理碰撞**
NavMesh 代理的移动由寻路系统直接控制位移，与 Rigidbody 物理系统相互独立。在 Unity 中，若同时给代理挂载 `NavMeshAgent` 和 `Rigidbody`，两套系统会争夺位置控制权，导致代理抖动或穿越地形。正确做法是二选其一，或在代码中根据状态切换控制权（如跌落时禁用 NavMeshAgent，改由 Rigidbody 物理接管）。

---

## 知识关联

**前置概念：物理查询**
NavMesh 生成阶段的体素化依赖物理引擎的射线检测（Raycast）和重叠检测（OverlapTest）来判断每个体素是否被几何体占据，理解物理查询的空间加速结构（BVH/AABB 树）有助于理解为何烘焙在场景三角形数量较多时耗时显著增加。运行时的 `NavMesh.SamplePosition` 和 `NavMesh.Raycast` 接口同样是物理空间查询在导航网格坐标系上的投影操作。

**横向关联：行为树与状态机**
NavMesh 寻路通常被封装为行为树（Behavior Tree）的叶节点动作，例如 Unreal Engine 内置的 `MoveTo` 任务节点直接调用 NavMesh 的 `FindPath` 接口。NavMesh 只负责计算"走哪条路"，而何时触发寻路、何时停止、遇到路径被完全封堵时如何响应，则由上层的行为树或有限状态机负责决策。
