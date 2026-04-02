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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 导航网格系统

## 概述

导航网格系统（Navigation Mesh，简称 NavMesh）是游戏引擎中专门用于 AI 角色自动寻路的多边形网格结构。与早期基于栅格（Grid）的寻路方案不同，NavMesh 将可行走的地面区域表示为一组相互连接的凸多边形（Convex Polygon），使 AI 角色能够在三维场景中流畅地规划从起点到终点的路径，而无需逐格检测碰撞。

NavMesh 的理论基础源于 1997 年 Greg Snook 在《Game Developer Magazine》中提出的"可行走面网格"概念，此后 Mikko Mononen 于 2009 年发布的开源库 Recast & Detour 成为行业标准实现，被 Unity、Unreal Engine 4/5 等主流引擎直接采用或参考。其核心优势在于：相比 1024×1024 的栅格地图需要存储超过百万个节点，同等规模的 NavMesh 往往只需数千个多边形，寻路计算量降低约 100 倍。

在物理引擎的体系中，NavMesh 依赖物理查询（尤其是射线检测和重叠测试）来采样场景几何体、判断区域可达性，因此它是物理查询能力的直接上层应用。游戏中 NPC 的巡逻、追击、躲避等所有自主移动行为，都以 NavMesh 的存在为前提。

---

## 核心原理

### NavMesh 生成：从场景几何体到可行走多边形

NavMesh 的生成流程（Baking）分为四个阶段：

1. **体素化（Voxelization）**：引擎将场景几何体光栅化为三维体素网格，默认体素尺寸（Cell Size）通常为 0.3 米，Cell Height 为 0.2 米（Recast 的默认值）。每个体素被标记为"可行走"、"障碍"或"悬空"。
2. **区域划分（Region Segmentation）**：通过分水岭算法（Watershed Algorithm）将可行走体素合并为若干独立区域，每个区域代表地形上的一个连通块。
3. **轮廓提取与多边形化**：对每个区域的边界执行轮廓简化，随后利用 Delaunay 三角剖分或直接凸分解，将区域划分为凸多边形集合。
4. **细节网格生成**：在高度变化剧烈的区域（如斜坡）添加额外顶点，确保多边形与真实地面高度误差不超过 `maxError`（默认 1.3cm）。

关键参数 `AgentRadius`（代理半径，典型值 0.4 米）会在生成时将所有障碍物的碰撞边界向外膨胀对应距离，从而保证生成的 NavMesh 多边形内任意一点对该尺寸的代理都是安全可达的。

### A* 寻路与多边形图遍历

NavMesh 上的寻路分为两个层级：**宏观路径规划**使用 A* 算法在多边形连接图（Portal Graph）上计算经过哪些多边形；**微观路径平滑**则使用"漏斗算法"（Funnel Algorithm / String Pulling）在相邻多边形共享边（Portal Edge）上收紧路径，消除 A* 路径中的锯齿折角。

A* 中的启发函数通常选用欧氏距离（Euclidean Distance），代价函数为：

```
f(n) = g(n) + h(n)
```

其中 `g(n)` 是从起点到节点 n 的实际行走代价（以多边形中心间距累加），`h(n)` 是节点 n 到终点的欧氏距离估算。漏斗算法的时间复杂度为 O(n)，n 为路径经过的多边形数量，远优于对每个路径点单独做物理查询验证。

### 动态障碍与 NavMesh 更新

动态障碍（Dynamic Obstacles）分两类处理机制：

- **局部障碍回避（Local Avoidance）**：使用 RVO（Reciprocal Velocity Obstacles）或 ORCA 算法，在不修改 NavMesh 几何体的前提下，实时计算每帧每个代理的速度调整量，使多个 AI 互相避让。Unity 的 NavMesh Obstacle 组件在"Carve"模式关闭时即采用此方式。
- **NavMesh 雕刻（Carving）**：当障碍物静止超过 `carveOnlyStationary` 阈值时，引擎重新烘焙障碍物周围的局部区域（Tile），将障碍物形状从 NavMesh 中扣除。Unity 的 Tile Size 默认为 256 体素宽，每次局部更新仅重新计算受影响的 Tile，而非全图重烘焙，以此控制运行时开销。

---

## 实际应用

**场景一：多层建筑内的 NPC 导航**  
在具有楼梯和电梯的室内场景中，NavMesh 通过"离网连接"（Off-Mesh Link）手动定义楼梯顶端与底端之间的连接边。角色到达离网连接入口时，引擎暂停 A* 路径跟随，播放攀爬动画，到达出口后恢复正常导航。Unreal Engine 5 的 Navigation System 支持自动检测高度差在 `AgentMaxStepHeight`（默认 35cm）以内的台阶，自动生成离网连接。

**场景二：RTS 游戏中的大规模单位寻路**  
在《星际争霸 II》中，Blizzard 使用分层导航网格（Hierarchical NavMesh）：顶层为低分辨率的区域连通图用于宏观规划，底层为高分辨率 NavMesh 用于局部移动。单位密集时，ORCA 算法保证数百个单位同时移动不发生互相穿插，且每帧计算量控制在 O(n log n) 以内。

**场景三：动态地形破坏**  
在有墙壁爆破或地形塌陷的游戏中，破坏事件触发后系统标记受影响的 NavMesh Tile 为脏数据（Dirty），在下一帧或下若干帧内异步重新烘焙对应 Tile，确保 AI 不会规划穿越已塌陷区域的路径。

---

## 常见误区

**误区一：NavMesh 烘焙一次即可永久使用**  
NavMesh 是对**烘焙时刻**场景状态的静态快照。如果场景中的静态障碍物在运行时被移动或销毁，NavMesh 不会自动更新。开发者必须显式调用 `NavMesh.RemoveNavMeshData()` 并重新烘焙，或使用支持局部更新的 Tile-based NavMesh。许多初学者发现 AI 仍然"绕着消失的墙走"，根本原因正是此处。

**误区二：提高体素分辨率总能改善寻路精度**  
将 Cell Size 从 0.3 米降低到 0.05 米会使体素数量增加约 216 倍（三维立方关系），烘焙时间从秒级变为分钟级，同时生成的多边形数量激增导致运行时 A* 搜索时间上升。正确做法是仅在需要高精度导航的局部区域（如室内）使用小 Cell Size，室外开阔地带使用较大值。

**误区三：NavMesh 代理可以直接跟随 NavMesh 路径而无需速度控制**  
A* + 漏斗算法输出的是一条几何折线路径（Waypoints），而非考虑物理动力学的运动轨迹。如果直接将代理瞬移至路径点，会产生方向突变、穿插其他代理等问题。实际工程中必须结合速度插值（Steering Behaviors）或物理引擎的角色控制器（Character Controller）来驱动移动，NavMesh 只负责告知"应该去哪里"，而非"如何移动"。

---

## 知识关联

**依赖物理查询**：NavMesh 的生成阶段大量使用射线检测（Raycast）和球体扫描（SphereCast）来判断地面可达性和障碍物边界，`AgentRadius` 的膨胀计算本质上是对场景几何体执行批量重叠测试（Overlap Test）。如果不熟悉物理查询的层掩码（Layer Mask）配置，极易出现特定图层的障碍物被忽略导致 AI 穿墙的 Bug。

**延伸至行为树与 AI 决策**：NavMesh 负责解决"如何到达目标位置"的运动层问题，上层的行为树（Behavior Tree）或状态机决定"何时向何处移动"。两者通过"设置目标点"（SetDestination）接口解耦，NavMesh 系统对行为树的决策逻辑完全透明，仅暴露路径是否可达（`HasPath`）和当前剩余距离（`remainingDistance`）等查询接口供决策层使用。