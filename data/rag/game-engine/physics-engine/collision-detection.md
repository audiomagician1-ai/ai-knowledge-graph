---
id: "collision-detection"
concept: "碰撞检测"
domain: "game-engine"
subdomain: "physics-engine"
subdomain_name: "物理引擎"
difficulty: 2
is_milestone: false
tags: ["碰撞"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 48.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.419
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 碰撞检测

## 概述

碰撞检测（Collision Detection）是物理引擎中判断两个或多个几何体是否发生空间重叠或接触的计算过程，其输出包括接触点坐标、接触法线方向和穿透深度（Penetration Depth），这三个量直接驱动后续的约束求解器产生分离力。没有碰撞检测，刚体动力学的积分结果会导致物体相互穿透，破坏模拟的物理可信度。

碰撞检测算法的系统化研究始于1970年代的计算几何领域。1988年，Gilbert、Johnson和Keerthi三人发表了著名的GJK算法论文，这是凸体距离计算的里程碑。同年，AABB层次包围盒（Bounding Volume Hierarchy）用于加速宽阶段检测的方案也在机器人路径规划中得到验证。Erin Catto于2005年在GDC演讲中展示的Box2D引擎，将上述算法工程化为游戏开发者可直接使用的完整流水线，此后Bullet、PhysX等引擎均沿用这一两阶段架构。

碰撞检测的计算开销与场景中物体数量N的关系是朴素做法的O(N²)对，而现代游戏场景可能包含数千个刚体，因此算法优化直接决定物理帧率能否维持在60Hz以上。一次典型的游戏物理帧，宽阶段可将候选对数量从N²级别压缩至线性级别，窄阶段再精确计算真正的接触信息，这种分层策略是现代实时碰撞检测的基础架构。

## 核心原理

### 宽阶段（Broad Phase）：快速排除不可能碰撞对

宽阶段使用简化的包围体代替真实几何形状，以极低代价剔除绝大多数不相交对。最常用的包围体是**AABB（Axis-Aligned Bounding Box）**，其相交测试只需比较6个浮点数（两轴对齐包围盒各3个区间是否重叠）。更精确但略慢的是**OBB（Oriented Bounding Box）**，需要进行15次分离轴测试。

主流宽阶段算法包括：
- **SAP（Sweep And Prune）**：将所有AABB的X轴端点排序后扫描，利用帧间连续性维护一个已排序列表，每帧仅做增量更新，时间复杂度接近O(N)。
- **BVH（Bounding Volume Hierarchy）**：用树状结构组织静态物体的AABB，动态物体查询时沿树遍历，适合静多动少的场景，查询复杂度为O(log N)。
- **空间哈希（Spatial Hashing）**：将空间划分为固定大小格子并哈希，适合均匀分布的小物体，格子尺寸通常取最大物体直径的2倍。

### 窄阶段（Narrow Phase）：精确接触计算

通过宽阶段筛选的候选对需要进行精确的几何相交测试，提取接触流形（Contact Manifold）。两种核心算法分别适用于不同场景：

**SAT（Separating Axis Theorem，分离轴定理）**：两个凸多边形不相交，当且仅当存在一条轴使两形状在该轴上的投影不重叠。对于3D多面体，需要测试所有面法线以及所有边对的叉积，边数为m和n的多面体最多需要测试 m + n + m×n 条轴。SAT的优点是代码直观，且可直接得到最小穿透深度轴（MTV, Minimum Translation Vector），缺点是轴数量随多边形复杂度平方增长。

**GJK（Gilbert–Johnson–Keerthi）算法**：利用Minkowski差的性质——两凸体相交当且仅当它们的Minkowski差包含原点。GJK通过迭代构造Minkowski差上的单纯形（Simplex，2D为三角形，3D为四面体）来判断原点是否被包含，每次迭代通过支撑函数（Support Function）沿最优方向采样新顶点。GJK的核心公式为：

> **d(A, B) = min{ ||a - b|| : a ∈ A, b ∈ B }**

当d = 0时两体相交。GJK本身只能判断是否相交，穿透深度的计算需要配合**EPA（Expanding Polytope Algorithm）**完成，EPA从GJK得到的初始单纯形出发，向外扩张多面体直到找到最近面，其法线即为接触法线。

### 连续碰撞检测（CCD）

离散检测在高速物体（如子弹）中会出现**穿隧效应（Tunneling）**——物体在两帧之间完全穿过薄壁。连续碰撞检测通过计算物体在时间区间[t₀, t₁]内的运动扫掠体（Swept Volume）来解决此问题。常用方法是**保守前进（Conservative Advancement）**：迭代缩小时间步长，每步用GJK计算距离并估算最大前进量，直到距离小于容差阈值（通常取0.001米），该方法通常在5~10次迭代内收敛。

## 实际应用

**角色控制器的胶囊体碰撞**：Unity和Unreal Engine均使用胶囊体（Capsule）表示人形角色，因为胶囊体与任意凸体的GJK支撑函数可以解析求解，无需网格顶点迭代，角色与地形的碰撞检测帧耗时通常在0.01ms以内。

**子弹物理的CCD配置**：在Bullet物理库中，对快速移动的刚体需要显式调用`setCcdMotionThreshold(radius)`和`setCcdSweptSphereRadius(radius)`开启CCD，否则速度超过自身尺寸/帧时间的物体必然发生穿隧。一颗直径1cm、速度900m/s的子弹在60Hz物理帧中每帧移动15m，必须开启CCD。

**PhysX的MBP（Multi-Box Pruning）宽阶段**：PhysX 3.x引入MBP作为默认宽阶段，将场景划分为若干区域，每个区域内使用SAP，区域间使用粗粒度的AABB测试，在拥有10,000个动态刚体的场景中宽阶段耗时约1.2ms（对比朴素O(N²)的约200ms）。

## 常见误区

**误区一：SAT和GJK可以互相完全替代**。实际上两者有明显适用范围差异。SAT对凸多边形的面数敏感，超过20面的凸体SAT性能急剧下降；GJK通过支撑函数工作，对光滑曲面（球体、胶囊体）天然高效，只需解析支撑函数即可，不依赖顶点数量。此外SAT直接给出MTV，而GJK需要额外运行EPA才能得到穿透深度。

**误区二：宽阶段只是粗略剔除，精度不影响正确性**。错误。如果宽阶段的AABB未能完全包住对应几何体（例如旋转后未更新AABB），窄阶段将永远不会测试该对，导致碰撞被完全漏检。宽阶段必须保证**保守性**（Conservative）：所有真实相交对都必须通过宽阶段，允许假阳性但不允许假阴性。

**误区三：碰撞检测直接产生物理响应**。碰撞检测只负责输出接触数据（法线、穿透深度、接触点），物理响应（冲量计算、摩擦力模拟）由后续的**约束求解器**（Constraint Solver）完成。将两者混淆会导致在物理引擎架构设计时错误地将响应逻辑耦合进几何检测模块。

## 知识关联

碰撞检测以**刚体动力学**的积分结果作为输入——每帧积分后得到的新位置和姿态被送入宽阶段进行配对测试，GJK/EPA使用这些变换后的顶点坐标进行Minkowski差计算。如果没有刚体运动方程提供位置更新，碰撞检测将无从得知物体的当前状态。

碰撞检测的输出——接触点、接触法线和穿透深度——是**约束求解器**的直接输入。约束求解器将这些接触数据转化为非穿透约束（Non-penetration Constraint），通过Projected Gauss-Seidel或LCP（Linear Complementarity Problem）求解器计算分离冲量。碰撞检测的精度（尤其是接触法线的准确性）直接影响约束求解的稳定性。

在**破坏物理**（Destructible Physics）场景中，碰撞检测面临额外挑战：破碎后的碎片数量可能在单帧内从1个变为数百个，BVH树需要实时重建，且碎片的凸分解（Convex Decomposition，通常使用HACD算法将凹体分解为凸体集合）质量直接决定GJK能否正确工作。V-HACD库的典型分解精度参数为最大凸体数量32、最大顶点数64。