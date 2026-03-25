---
id: "physics-query"
concept: "物理查询"
domain: "game-engine"
subdomain: "physics-engine"
subdomain_name: "物理引擎"
difficulty: 2
is_milestone: false
tags: ["查询"]

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
# 物理查询

## 概述

物理查询（Physics Query）是游戏引擎物理系统提供的一类主动检测接口，允许游戏逻辑在不依赖碰撞事件回调的前提下，主动向物理场景"提问"：某个位置是否有碰撞体？某条射线经过哪些物体？某个形状扫过空间后会触碰什么？物理查询的结果由物理引擎的空间加速结构（通常是 BVH 树或八叉树）实时计算，返回命中信息、命中点坐标、法线向量和距离等数据，供业务逻辑直接使用。

物理查询的概念随着商业物理中间件的普及而被标准化。PhysX 2.x 时代（2006 年前后）将 Raycast、Sweep、Overlap 作为三类独立 API 固定下来，这一分类被 Unity、Unreal Engine 等主流引擎沿用至今。在 Unreal Engine 5 中，这三类查询对应 `LineTraceSingleByChannel`、`SweepSingleByChannel` 和 `OverlapMultiByChannel` 等函数；在 Unity 中对应 `Physics.Raycast`、`Physics.SphereCast` 和 `Physics.OverlapSphere` 等 API。

物理查询之所以被广泛应用，根本原因在于它将"检测需求"与"物理仿真循环"解耦。角色是否能看见敌人、武器子弹落点在哪里、技能范围内包含多少目标——这些逻辑需要即时、精确的空间信息，而不是等待下一帧物理仿真碰撞结果的回调，物理查询恰好满足这一要求。

---

## 核心原理

### Raycast（射线检测）

Raycast 以一条无体积的射线为查询形状，参数为起点 `origin`、方向 `direction`（单位向量）和最大距离 `maxDistance`。射线方程为：

```
P(t) = origin + direction × t，  0 ≤ t ≤ maxDistance
```

物理引擎用 BVH 树快速剔除不可能命中的包围盒，再对候选碰撞体执行精确的几何求交（AABB、球体、凸包、三角网格各有专用算法）。`RaycastSingle` 只返回距离最近的一个命中结果，`RaycastAll` 返回射线路径上所有命中结果并按距离排序。命中结果 `RaycastHit` 包含五个常用字段：命中对象引用、命中世界坐标 `point`、表面法线 `normal`、射线行进距离 `distance`、UV 坐标（若网格开启了碰撞 UV 读取）。

### Sweep（扫描检测）

Sweep 可以理解为"有形状的 Raycast"，它将一个几何体（胶囊体、球体、盒体）沿指定方向移动，检测运动路径上是否与其他碰撞体相交。胶囊扫描（CapsuleCast）最常用于角色控制器：给定胶囊半径 `r`、半高 `h`、起点和移动向量，引擎计算 Minkowski 差之后转化为对膨胀形状的 Raycast，从而找到首次接触位置，精度优于逐帧位移叠加检测。Sweep 只能返回首次命中（SweepSingle），不支持穿透返回多结果，因为形状被前方物体阻挡后无法继续运动。

### Overlap（重叠检测）

Overlap 在空间中放置一个静止形状，查询所有与它相交的碰撞体，无方向性，无距离排序。`OverlapSphere(center, radius)` 返回球形区域内所有碰撞体的列表，是范围技能伤害判定、环境感知 AI 的标准实现方式。Overlap 不计算命中点和法线，只关心"谁在范围内"，因此计算开销低于同等条件下的 Sweep。Unity 的 `Physics.OverlapSphereNonAlloc` 版本可传入预分配数组，避免每帧在托管堆上产生 GC 分配，适合高频调用场景。

### 过滤机制

三类查询都支持两种过滤维度：**层级掩码（Layer Mask / Collision Channel）** 和 **查询过滤回调（Query Filter Callback）**。层级掩码是一个 32 位整数，每一位对应一个物理层，按位与运算决定是否参与查询；回调过滤则允许在 BVH 遍历过程中逐对象执行自定义逻辑（如忽略发起查询的角色自身碰撞体）。PhysX 的过滤回调分为 `preFilter`（精确检测前，基于形状标志过滤）和 `postFilter`（精确检测后，基于命中结果过滤）两个阶段，合理使用可显著减少无效的几何求交运算。

---

## 实际应用

**武器射击命中判定**：第一人称射击游戏通常用 `RaycastSingle` 从枪口沿摄像机视线方向检测，最大距离设置为武器射程（如 500 单位），命中结果的 `normal` 用于生成弹孔贴花的旋转，`distance` 用于计算弹道下坠修正。

**角色地面检测**：角色控制器常在角色胶囊体底端向下发出一条长度为 `0.2` 单位的 Raycast 或半径与胶囊相等的 SphereCast，每帧检测是否接触地面，以决定是否播放落地动画、允许跳跃输入。若改用碰撞事件回调，在角色站在斜面边缘时可能产生频繁的 OnCollisionEnter/Exit 抖动，而短距离 Raycast 更稳定。

**视线遮挡检测（Line of Sight）**：AI 敌人在执行"是否能看见玩家"判断时，先用 `OverlapSphere` 筛选感知半径（如 15 米）内的目标列表，再对每个候选目标用 `RaycastSingle` 确认两者之间是否有遮挡物，这种先粗后精的两步查询策略，比直接对场景中所有对象执行 Raycast 效率高出数倍。

**技能范围伤害**：AOE 技能落点触发时调用 `Physics.OverlapSphere(hitPoint, 5f, enemyLayerMask)`，返回半径 5 米内的所有敌人碰撞体列表，再逐一读取碰撞体所附属的生命值组件执行伤害计算，整个流程无需预先注册监听器。

---

## 常见误区

**误区一：用 Raycast 代替 Sweep 检测移动物体穿透**。如果在每帧末对高速子弹仅做一次位置的 Raycast 而不是 Sweep，当子弹在单帧内移动距离超过目标厚度时，射线起点和终点都在目标之外，检测会直接漏掉命中——这就是经典的"穿墙bug"（Tunneling）。正确做法是使用 `SphereCast` 或 PhysX 的连续碰撞检测（CCD），以上一帧位置为起点、当前帧位置为终点做扫描。

**误区二：Overlap 返回空列表等于该区域没有任何物体**。Overlap 只查询**具有碰撞体组件**的对象，场景中纯视觉网格、粒子系统、触发器（Trigger）的参与取决于查询时的 `QueryTriggerInteraction` 参数设置。Unity 默认的 `QueryTriggerInteraction.UseGlobal` 由项目全局设置决定，若项目将触发器查询关闭，Overlap 将不返回任何 Trigger 碰撞体，开发者需显式传入 `QueryTriggerInteraction.Collide` 才能包含触发器。

**误区三：物理查询可以在任意线程随意调用**。PhysX 场景查询（Scene Query）并非线程安全，若在 Unity 的 Job System 或非主线程中直接调用 `Physics.Raycast`，可能导致数据竞争崩溃。Unity 2022 起提供了 `Physics.BatchQuery`（实验性 API），允许批量提交查询并在 Job 中异步处理结果，但普通 `Physics.Raycast` 仍须在主线程调用。

---

## 知识关联

**与物理引擎概述的关系**：物理引擎概述中介绍的碰撞体类型（球体、胶囊体、凸包、三角网格）直接决定了物理查询的精度和开销——三角网格碰撞体的 Raycast 开销可达凸包的 10 倍以上，因此静态场景通常保留网格碰撞体用于查询精度，动态角色只使用胶囊碰撞体。

**与导航网格系统的衔接**：导航网格（NavMesh）的路径规划描述了角色"应该走哪里"，但不解决"前方有无动态障碍物"的问题。实际项目中，NavMesh Agent 在执行移动时，引擎底层用 Sweep 检测来处理动态障碍物的局部回避（Local Avoidance），而上层 AI 感知模块仍需依赖 Raycast/Overlap 来获取环境信息，两套系统协同工作，分别处理路径规划和即时空间感知两个不同层面的需求。
