---
id: "navmesh-basics"
concept: "导航网格基础"
domain: "level-design"
subdomain: "blockout"
subdomain_name: "Blockout"
difficulty: 2
is_milestone: false
tags: ["AI"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 48.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 导航网格基础

## 概述

导航网格（Navigation Mesh，简称 NavMesh）是一种将游戏关卡中AI可行走区域抽象为多边形集合的数据结构。引擎通过分析场景几何体，自动烘焙生成一张覆盖可行走表面的网格，AI角色在寻路时不再逐像素检测碰撞，而是在这张多边形网格上计算从A点到B点的最短路径。NavMesh技术最早在2000年代初随Unreal Engine 3和Unity引擎的普及而成为关卡设计的标准工具，极大降低了AI寻路的运算复杂度。

NavMesh的核心价值在于它将三维几何碰撞问题简化为二维图搜索问题。传统射线检测寻路需要每帧发射数十条射线来验证路径可行性，而NavMesh只需在预烘焙的多边形图上运行A*算法（A-star），时间复杂度从O(n²)降至接近O(n log n)。对于关卡设计师而言，NavMesh的生成质量直接决定了AI是否能够到达关卡中每个预设的战术位置，因此在Blockout阶段就必须配合碰撞体积同步检验NavMesh覆盖范围。

## 核心原理

### NavMesh的生成参数

NavMesh烘焙依赖若干关键参数，其中最重要的是**Agent Radius（代理半径）**和**Max Slope（最大坡度角）**。以Unity引擎为例，默认Agent Radius为0.5单位，意味着宽度小于1.0单位的通道将被NavMesh排除，AI无法通过。Max Slope默认值为45度，超过该角度的斜面不会被烘焙为可行走区域。**Step Height（台阶高度）**参数控制AI能翻越的最大垂直落差，Unity默认值为0.4单位，低于此高度的台阶边缘NavMesh会自动连接，高于此值则产生断裂。

Unreal Engine 5中的NavMesh参数集中在`RecastNavMesh`组件内，其中`Cell Size`（体素单元尺寸）默认为19cm，该值越小生成的NavMesh边界越精确但烘焙耗时越长；`Cell Height`默认为10cm，控制垂直方向的采样精度。关卡设计师在Blockout阶段通常将这些参数调至粗糙值以加快迭代速度，在关卡几何确定后再精细化烘焙。

### 多边形网格的寻路逻辑

NavMesh生成后，每个可行走区域被分解为若干凸多边形（Convex Polygon）。AI寻路时首先定位起点和终点各属于哪个多边形节点，再以多边形为节点运行A*算法找到跨多边形路径，最后通过**漏斗算法（Funnel Algorithm）**将多边形序列平滑为实际的移动折线路径。这一流程意味着NavMesh的多边形数量越少，A*的搜索空间越小，寻路越高效——这也是为什么引擎会尽量将相邻平坦区域合并为更大的凸多边形。

NavMesh上相邻多边形之间的共享边称为**Portal Edge（门户边）**，漏斗算法正是沿着这些Portal Edge收紧路径。当关卡中存在门洞、拱廊等窄口时，Portal Edge的宽度直接影响AI通过时的移动轨迹平滑程度。若Portal Edge过窄（小于Agent Radius的2倍），AI可能在通过时产生卡边现象。

### NavMesh Link与动态障碍物

标准NavMesh只覆盖静态几何体，无法自动处理跳跃、攀爬或传送等非连续移动。引擎提供**NavMesh Link（导航链接）**组件来手动连接两段不相邻的NavMesh区域，例如将一段平台跳跃的起跳点与落点用Off-Mesh Link连接，并标注该连接需要播放跳跃动画。在Unreal Engine中，这类连接通过`NavLinkProxy` Actor实现，设计师可以为其设置触发距离和双向/单向属性。

动态障碍物（如可移动的箱子或关门的大门）通过**NavMesh Obstacle**组件实时修改NavMesh局部区域，在Unity中对应`NavMeshObstacle`组件，其`Carve`属性开启后引擎每帧重新裁剪被遮挡区域的NavMesh。频繁Carve操作有性能代价，因此设计师应在Blockout阶段明确哪些障碍物是动态的，提前规划NavMesh的动态区域范围。

## 实际应用

在第一人称射击游戏的室内关卡Blockout阶段，设计师搭建走廊后需立即检查NavMesh是否覆盖所有巡逻路点。若走廊宽度为80cm但Agent Radius设为50cm，NavMesh宽度仅剩负数，该走廊对AI完全不可通行。正确做法是关卡走廊净宽至少保证`Agent Radius × 2 + 30cm`的余量，即至少130cm宽才能保障单个AI流畅通过。

在开放世界关卡中，NavMesh通常以**分块（Tiled NavMesh）**方式烘焙，Unreal Engine默认每块Tile大小为1000cm×1000cm。设计师应确保关键战斗区域的地面高度差不超过Max Slope限制，否则山坡顶部将出现NavMesh空洞，导致AI无法登上预设的狙击位。通过在编辑器中开启NavMesh可视化（Unity的Scene视图绿色叠加层，或UE5的`P`键显示导航网格），可以在Blockout阶段直观发现这类覆盖缺口。

## 常见误区

**误区一：认为碰撞体积与NavMesh完全同步。** 碰撞体积的存在不代表NavMesh一定覆盖该表面。NavMesh烘焙时还会受到Agent Radius、Max Slope、Step Height等参数约束，一个玩家可以行走的斜坡（因为玩家不受NavMesh约束），AI可能完全无法通行。设计师必须在为玩家设计通道后，额外验证对应的NavMesh生成结果，而不能假设两者一致。

**误区二：NavMesh面积越大越好。** 部分设计师会将NavMesh烘焙范围最大化，覆盖所有几何体表面，包括屋顶、橱柜顶部等非预期区域。这不仅增加了A*搜索空间，还会导致AI出现翻越障碍物、站在玩家无法预期的位置等行为异常。正确做法是通过NavMesh Volume（Unreal中的`NavMeshBoundsVolume`）精确限制烘焙范围，并对不应可行走的表面添加`NavModifierVolume`设置为`Null Area`（完全不可行走区域）。

**误区三：Off-Mesh Link可以替代完整的几何过渡设计。** 有些设计师在发现两段NavMesh无法连接时，直接添加Off-Mesh Link了事，而不检查断裂原因。若NavMesh断裂是因为台阶高度超出Step Height参数，正确的修复是调整台阶几何形状或修改Step Height，而非依赖Off-Mesh Link。Over-Link会让AI的移动看起来像传送，破坏游戏表现的可信度。

## 知识关联

NavMesh基础直接依赖**碰撞体积设计**的质量：NavMesh烘焙时以碰撞体（Collider/Collision Mesh）为输入源，若碰撞体网格存在穿模、悬空或漏洞，NavMesh会在对应位置产生不可预测的覆盖错误。确保碰撞体积在Blockout阶段贴合几何体表面，是获得干净NavMesh的前提条件。

掌握NavMesh基础后，下一步是设计**AI巡逻范围**：巡逻路点（Patrol Point）必须全部落在NavMesh覆盖区域内，巡逻路径的每段连接都需要NavMesh多边形支撑。设计巡逻范围时还需考虑NavMesh的连通性——若两个巡逻点分属互不连通的NavMesh岛屿，AI将在两点之间陷入寻路失败状态，这是AI巡逻设计中最常见的关卡结构问题之一。