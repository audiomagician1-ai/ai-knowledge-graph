---
id: "physics-engine-intro"
concept: "物理引擎概述"
domain: "game-engine"
subdomain: "physics-engine"
subdomain_name: "物理引擎"
difficulty: 1
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 82.9
generation_method: "research-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "textbook"
    title: "Game Physics Engine Development"
    author: "Ian Millington"
    year: 2010
    isbn: "978-0123819765"
  - type: "textbook"
    title: "Real-Time Collision Detection"
    author: "Christer Ericson"
    year: 2004
    isbn: "978-1558607323"
  - type: "textbook"
    title: "Game Engine Architecture"
    author: "Jason Gregory"
    year: 2018
    isbn: "978-1138035454"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 物理引擎概述

## 概述

物理引擎是游戏引擎中负责模拟牛顿力学、刚体碰撞、约束求解等物理现象的独立子系统，其核心任务是在每帧16.67毫秒（60fps）或更短的时间窗口内完成整个场景的物理状态更新。与离线物理仿真（如有限元分析）不同，游戏物理引擎刻意牺牲精度以换取实时性——例如位置修正（Position Correction）步骤会直接移动物体来消除穿透，而非通过精确积分恢复物理真实。

物理引擎的独立化发展始于2000年代初期。2004年Havok物理引擎随《半条命2》正式进入大众视野，证明了实时刚体模拟在商业游戏中的可行性。2005年开源引擎Bullet发布，其创始人Erwin Coumans将迭代冲量（Iterative Impulse）求解器引入大众开发者视野。此后Epic Games于2020年在虚幻引擎5中推出自研的Chaos物理系统，Unity则先后经历PhysX集成与Unity Physics（基于DOTS架构）两代方案，形成了当前行业的主要技术格局。

物理引擎在游戏开发中的不可替代性体现在两个维度：一是玩法层面，布娃娃系统、车辆模拟、破坏系统等机制直接依赖物理引擎的约束求解能力；二是视觉反馈层面，碎布效果、抛物线弹道、液体溅射等视觉现象若完全依靠美术手工制作成本极高，而物理引擎可以程序化生成这些行为。

## 核心原理

### 离散时间步长与积分方法

物理引擎不以连续时间运行，而是将时间离散为固定步长Δt进行数值积分，常见值为0.02秒（即物理帧率50Hz，对应Unity的`Time.fixedDeltaTime`默认值）。最常用的积分方法是半隐式欧拉积分（Semi-implicit Euler Integration）：

```
v(t+Δt) = v(t) + a(t) × Δt
x(t+Δt) = x(t) + v(t+Δt) × Δt
```

注意速度更新先于位置更新，这与显式欧拉不同，使得该方法在能量守恒上更稳定。更高精度的Runge-Kutta 4（RK4）虽然误差为O(Δt⁴)，但因计算量是欧拉法的4倍，游戏引擎中几乎不采用。

### 宽相与窄相碰撞检测的两阶段架构

物理引擎将碰撞检测分为宽相（Broad Phase）与窄相（Narrow Phase）两个阶段，目的是将O(n²)的物体对检测复杂度降低到接近O(n log n)。宽相使用AABB（轴对齐包围盒）配合SAP（Sweep And Prune）算法或BVH（包围体层次结构）快速排除不可能碰撞的物体对；窄相仅对宽相筛选出的候选对执行精确几何求交，常用算法包括GJK（Gilbert-Johnson-Keerthi）算法用于凸体距离计算，以及EPA（Expanding Polytope Algorithm）用于穿透深度求解。

### 约束求解器与冲量迭代

碰撞响应与关节约束统一通过约束求解器（Constraint Solver）处理。现代游戏物理引擎普遍采用PGS（Projected Gauss-Seidel）迭代求解器，每帧对所有约束迭代4到10次（Havok默认为4次，Bullet默认为10次）。每次迭代计算冲量J并将其施加到刚体上：

```
J = -(1 + e) × v_rel · n / (1/m_A + 1/m_B + (r_A × n)·I_A⁻¹·(r_A × n) + (r_B × n)·I_B⁻¹·(r_B × n))
```

其中e为碰撞恢复系数，n为碰撞法线，r为接触点相对质心的向量，I为惯性张量。迭代次数越多结果越稳定，但计算成本线性增长，这是物理引擎调优时最需要权衡的参数之一。

### 物理场景的数据组织

物理引擎维护独立于渲染场景的物理世界（Physics World），包含刚体列表、碰撞形状树、约束列表和材质库。物理更新完成后，引擎将刚体变换同步回游戏对象（Transform Sync），这一步骤在Unity中发生在`FixedUpdate`之后、`Update`之前的内部同步阶段。物理世界与渲染世界的解耦使物理引擎可以独立线程运行，例如PhysX 3.x引入了异步物理（Asynchronous Physics）模式，允许物理计算与渲染并行执行。

## 实际应用

在第一人称射击游戏中，子弹穿透力学要求物理引擎在单帧内处理射线检测（Raycast）、冲量施加和布娃娃激活三个连续步骤。《毁灭战士：永恒》的物理系统在极端情况下每帧需要处理超过200个活跃刚体的碰撞响应，通过限制布娃娃最大数量（通常为8-12个）来维持帧率稳定。

车辆物理是物理引擎应用的高度专业化场景。《极品飞车》系列使用专用的车辆动力学库，将车辆悬挂建模为弹簧-阻尼系统（Spring-Damper），轮胎摩擦力则采用Pacejka"魔法公式"（Magic Formula）计算侧向力与纵向力。这类需求远超通用刚体求解器的能力边界，因此大多数引擎为车辆提供专用组件（如Unity的`WheelCollider`）。

在建筑游戏（如《我的世界》dungeons扩展包）中，物理引擎负责大规模结构体的实时坍塌模拟，通常结合Voronoi碎裂预计算与运行时刚体激活（Sleeping/Waking机制）实现：静止物体进入休眠状态不参与计算，受力后唤醒，将活跃刚体数量控制在可接受范围内。

## 常见误区

**误区一：物理帧率越高越精确**。提高物理帧率（将Δt从0.02秒降至0.01秒）确实减少了积分误差，但同时会使每帧的物理计算时间翻倍，且不会改变PGS求解器因迭代次数有限而产生的约束误差。对于大多数游戏场景，调整求解器迭代次数比单纯提高帧率更有效。将物理帧率设置为渲染帧率的整数倍（而非相等）是更常见的工程实践，可避免渲染与物理时间步不同步导致的抖动。

**误区二：碰撞形状应尽量贴合视觉网格**。使用完整三角网格（Triangle Mesh）作为碰撞形状会导致窄相检测成本急剧上升，且GJK算法要求碰撞形状为凸体。实际项目中，开发者通常用数个简单凸体（如胶囊体、长方体的组合）拼合复杂物体的碰撞体积，视觉网格与物理网格分离维护是标准工作流。

**误区三：物理引擎负责所有"碰撞"逻辑**。触发器（Trigger）碰撞体虽然经过物理引擎的宽相与窄相检测，但不产生冲量响应，属于纯几何重叠检测。游戏中大量"碰到就触发"的逻辑（捡取道具、进入区域、技能判定）应优先使用触发器而非刚体碰撞，以避免不必要的约束求解开销。

## 知识关联

学习物理引擎概述需要具备游戏引擎整体架构的认知，理解物理引擎作为独立子系统如何与渲染、脚本、动画系统协作；同时Chaos物理系统与Unity Physics作为当前主流实现，其架构选择（如Chaos的多线程破坏、Unity Physics的ECS无状态设计）都是本文理论在具体引擎中的体现。

在此基础上，**刚体动力学**将深入展开质量、惯性张量、力矩等概念的数学细节；**碰撞形状**将具体讲解各类几何体的碰撞检测算法与性能特征；**物理材质**涉及摩擦系数与恢复系数在约束方程中的参数化方式；**布料模拟**则引入基于位置的动力学（Position-Based Dynamics，PBD）这一与刚体求解器完全不同的模拟范式；**物理场景管理**将讨论大规模物理世界的空间分区与休眠管理策略。这些后续概念共同构成游戏物理引擎的完整技术栈。