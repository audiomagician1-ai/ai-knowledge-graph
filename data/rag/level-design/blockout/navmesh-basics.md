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

导航网格（Navigation Mesh，简称NavMesh）是一种将游戏世界中AI可行走区域抽象为多边形集合的数据结构，每个多边形单元描述一块平坦且可通行的地面区域。与传统的路点（Waypoint）系统不同，NavMesh以连续的面覆盖地形，使AI角色能在面内任意位置行走，而不是只能沿固定节点连线移动。

NavMesh技术在2000年代初期随《半条命2》和Havok AI等中间件的普及而被广泛采用。在此之前，大多数游戏使用稀疏路点图处理AI寻路，这导致AI在障碍物附近表现僵硬。NavMesh的引入让AI能够平滑绕过复杂几何体，大幅提升了关卡中NPC的可信度。

对关卡设计师而言，理解NavMesh的生成逻辑直接影响Blockout阶段的几何构建决策：一个未能正确生成NavMesh的关卡，无论视觉效果多精良，AI都将无法正常在其中活动，导致战斗、巡逻或追逐等核心玩法失效。

---

## 核心原理

### NavMesh的生成流程

引擎（以Unreal Engine 5为例）通过体素化（Voxelization）流程生成NavMesh。系统首先将场景几何体切割为小型立方体体素，默认体素尺寸（Cell Size）为**19cm**，Cell Height为**10cm**。体素化完成后，引擎识别出顶部开放且水平的体素面，将其合并为凸多边形区域，最终构成可供寻路使用的NavMesh面片。

这一流程的关键参数包括：
- **Agent Radius（代理半径）**：决定AI角色距离墙壁或障碍物的最小通行间距，默认值34cm对应人形角色
- **Agent Height（代理高度）**：NavMesh不会在低于此高度的空间（如低矮洞穴顶部）下方生成，默认144cm
- **Max Slope（最大坡度）**：超过此角度的斜面不会被标记为可行走区域，默认44°

### 碰撞体积与NavMesh的依赖关系

NavMesh生成完全依赖场景中物体的**碰撞几何体（Collision Geometry）**，而非可见的渲染网格。一个有视觉细节但缺少碰撞体积的装饰物，不会对NavMesh产生任何阻挡效果，AI将直接穿过它行走。反之，一个隐藏的碰撞盒若放置在地面以上约30cm高度，可能意外截断该区域的NavMesh生成，造成AI无法进入某个本应可通行的房间。

在Blockout阶段，设计师通常使用BSP体或简单Box Mesh构建空间，这些物体的碰撞体积与外形一致，NavMesh生成最为可靠。当引入带有复杂碰撞形状的美术资产时，必须重新验证NavMesh覆盖区域是否符合设计意图。

### NavMesh Link与垂直连通性

水平地面之间的NavMesh面片由引擎自动连接，但**垂直位移**（如跳跃、攀爬、从平台落下）无法自动生成连接关系。设计师需手动放置**NavMesh Link（导航网格链接）**组件，在两个不相连的NavMesh区域之间建立逻辑通道，并在链接上标注AI是否能双向通行。例如，一个高度差为200cm的平台跳落动作，可设置为单向NavLink（仅允许AI向下跳，不允许向上）。忽略NavLink配置是Blockout阶段最常见的AI寻路失效原因之一。

---

## 实际应用

**仓库关卡巡逻区域调试**：设计师在Unreal中按P键可视化当前NavMesh覆盖范围（绿色区域代表AI可行走）。当发现某排货架之间的过道（宽度约80cm）未生成NavMesh时，检查后发现Agent Radius（34cm × 2 = 68cm）加上容错间距导致该通道被判定为过窄。解决方案是将通道宽度调整至**100cm以上**，或针对体型更小的AI角色单独配置一个Agent Radius为20cm的NavMesh配置文件。

**楼梯的NavMesh处理**：楼梯在NavMesh生成中是高频问题点。当单级台阶高度超过Agent Step Height（默认35cm）时，楼梯将被视为不可行走的坡面，NavMesh断开。Blockout阶段建议将楼梯坡度保持在45°以内，或直接在楼梯下方放置一个隐形斜坡碰撞体以辅助NavMesh连通，待美术阶段再替换为正式楼梯资产。

---

## 常见误区

**误区一：NavMesh会跟随场景几何体实时自动更新**
静态场景中NavMesh在编辑器中预计算并烘焙，运行时不会因为关卡中添加了新的静态障碍物而自动重算。若需要动态障碍物（如可推动的箱子）影响AI寻路，必须使用**NavMesh Obstacle（导航网格障碍组件）**，该组件会在运行时动态挖除其覆盖区域的NavMesh。将普通静态碰撞盒误当动态障碍使用，会导致AI穿越可见障碍物。

**误区二：NavMesh覆盖意味着AI一定能到达该区域**
NavMesh描述的是"物理上可行走的区域"，但AI的实际寻路还受到**NavMesh区域过滤（Area Filter）**的限制。危险区域（如熔岩地面）可能在NavMesh上被标记为Cost极高的区域（默认危险区域Cost为1.0，普通地面为1.0，水面为2.0），AI将主动绕开，即使该区域在NavMesh覆盖范围内。设计师不能仅凭NavMesh可视化为绿色就断定AI会使用该路径。

**误区三：Blockout几何体可以随意使用非凸多边形碰撞**
NavMesh生成算法对凸多边形碰撞处理效率远高于非凸多边形。在Blockout阶段使用L形或U形的单一碰撞体（Concave Mesh Collision）会显著增加NavMesh烘焙时间，有时还会造成NavMesh面片在凹陷处出现异常孔洞，应将复杂形状拆分为多个凸多边形碰撞体叠加。

---

## 知识关联

**前置概念——碰撞体积设计**：NavMesh的生成质量直接取决于场景碰撞体积的精确程度。在学习碰撞体积设计时掌握的Simple Collision与Complex Collision区别，在NavMesh调试中具有直接应用价值：NavMesh生成默认使用Simple Collision，若某物体仅设置了Complex Collision而未设置Simple Collision，该物体对NavMesh完全透明。

**后续概念——AI巡逻范围**：AI巡逻范围的设计建立在合法NavMesh区域之上——巡逻路点必须放置在有效的NavMesh面片内，超出NavMesh边界的巡逻点会导致AI原地静止或产生寻路错误。掌握NavMesh的覆盖规律，能帮助设计师预判哪些空间适合设置巡逻回路，哪些区域需要额外NavLink才能纳入巡逻范围。