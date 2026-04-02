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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 物理查询

## 概述

物理查询（Physics Query）是游戏引擎物理系统提供的一类主动探测接口，允许开发者在不创建刚体或碰撞对象的前提下，向物理场景发射几何形状并获取与场景中碰撞体的相交信息。与被动的碰撞回调不同，物理查询由代码逻辑主动触发，返回命中点坐标、法线方向、被命中对象引用等具体数据。

物理查询的概念最早在PhysX 2.x版本中以`NxScene::raycastSingleShape`等函数形式正式成型，后经NVIDIA在PhysX 3.0的重构中统一归入`PxScene`的查询体系，形成了Raycast、Sweep、Overlap三大类接口的现代标准架构。Unity和Unreal Engine均直接封装了PhysX的查询层，其中Unreal Engine 4的`UWorld::LineTraceSingleByChannel`函数族至今仍是行业参考实现。

物理查询在游戏开发中具有不可替代性，因为绝大多数游戏玩法逻辑——包括命中判定、视线检测、角色站立检测、AI感知范围——都依赖于对场景几何的精确探测，而这些探测必须在单帧内完成并返回精确的几何信息，传统碰撞事件机制无法满足这一同步性要求。

## 核心原理

### Raycast（射线检测）

Raycast向场景中投射一条无限细的射线，定义为起点`origin`加方向向量`direction`乘以最大距离`maxDistance`。物理引擎对场景中所有启用查询标志（`PxQueryFlag`）的碰撞形状执行射线-AABB宽相（Broad Phase）过滤，再进行精确的射线-凸多面体或射线-三角网格窄相测试。命中结果包含`hitPoint = origin + direction × t`，其中`t`为射线参数（0到maxDistance之间的浮点数）。Raycast分为Single（返回最近命中）、Any（返回任意命中，性能更优）和All（返回全部命中，按距离排序）三种模式。

### Sweep（扫掠检测）

Sweep将一个实心几何体（球体、胶囊体、Box或凸多面体）沿指定方向滑动，检测其运动路径上最早发生接触的碰撞体。其数学本质是闵可夫斯基和（Minkowski Sum）：将查询体与场景中每个碰撞体做闵可夫斯基差后，对结果形状执行Raycast。球体Sweep性能最优，因为球-球或球-凸体的GJK求解只需约3-5次迭代；Box Sweep最慢，凸多面体对之间的GJK通常需要10-20次迭代。Unity中的`Physics.CapsuleCast`是Sweep的典型用例，角色控制器用它检测移动路径上的障碍物。

### Overlap（重叠检测）

Overlap测试一个静置几何体是否与场景中任何碰撞体相交，不涉及运动方向，返回所有与之重叠的碰撞体列表。Overlap不返回接触点或穿透深度，只返回碰撞体引用（`PxOverlapHit`只含`actor`和`shape`字段）。其性能开销介于单次Raycast和全All模式Raycast之间，常用于范围技能检测（如爆炸范围内的所有单位）和传送前的目标点安全性校验。PhysX内部对Overlap使用SAT（Separating Axis Theorem）而非GJK，对于凸多面体对测试最多检查15个分离轴。

### 查询过滤层（Query Filter）

三类查询均支持两级过滤机制：第一级为层掩码（Layer Mask），以32位整数位运算排除无关层，在宽相阶段完成，零性能开销；第二级为查询过滤回调（`PxQueryFilterCallback`），允许开发者以自定义C++函数逐个审查候选命中对象，可实现"忽略自身碰撞体""忽略无敌状态单位"等逻辑。Unity将这两级分别暴露为`layerMask`参数和`QueryTriggerInteraction`枚举，Unreal Engine通过`FCollisionQueryParams`结构提供`AddIgnoredActor`等方法。

## 实际应用

**射击游戏命中判定**：服务端在每帧处理玩家开枪事件时，从枪口位置沿准星方向执行Raycast Single，最大距离设为武器射程（如步枪800米）。命中后取`hitNormal`用于计算弹孔贴花的旋转方向，取`hitPoint`传递给伤害系统计算距离衰减。

**第三人称摄像机碰墙检测**：在理想摄像机位置与角色头部之间执行球体Sweep（半径通常0.2米），若命中则将摄像机拉近至命中点的`sweepFraction × armLength`处，避免摄像机穿入墙壁。

**AI视线检测**：AI每隔0.1秒从眼部位置向目标位置执行Raycast Any（层掩码仅包含遮挡层，不含敌我单位层），若无命中则视线畅通，触发警觉状态切换。使用Any模式而非Single模式可将该检测耗时降低约40%。

**角色站立地面检测**：胶囊体角色每帧向正下方执行胶囊体Sweep，距离为0.05米，检测是否仍站在地面上。命中法线角度超过45°（与世界上向量点积小于0.707）则判定为斜坡不可站立，切换为滑落状态。

## 常见误区

**误区一：将Overlap用于连续运动检测**。Overlap仅检测静态位置的相交，若用于快速移动的子弹（每帧位移超过碰撞体直径），会因两帧之间完全穿越目标而漏检。正确做法是对子弹使用两帧位置之间的Sweep，或改用连续碰撞检测（CCD）。

**误区二：每帧对所有AI执行Raycast而不做时间分片**。100个AI每帧各做一次Raycast视线检测，在复杂场景中可能消耗2-3毫秒。正确做法是将AI视线查询分散到多帧（每个AI每3-5帧检测一次），或使用Unreal Engine的`AsyncLineTrace`接口在工作线程上异步执行查询。

**误区三：混淆查询层掩码与碰撞矩阵**。查询层掩码（Query Filter Layer Mask）只控制物理查询接口的可见性，碰撞矩阵控制刚体之间的物理模拟碰撞响应，两者完全独立。一个碰撞体可以对刚体物理模拟不可见（碰撞矩阵排除），但对Raycast可见（查询掩码包含），这在实现"只对子弹检测、不受重力影响"的触发区时非常有用。

## 知识关联

物理查询建立在物理引擎概述中介绍的宽相/窄相分层加速结构之上——没有BVH（层次包围盒树）或八叉树等宽相结构，Raycast对复杂场景的遍历成本将从O(log n)退化到O(n)，无法在帧预算内完成。掌握物理查询后，导航网格系统的学习将直接受益：导航代理的落地检测（验证采样点是否在可行走表面上）正是通过向下的Raycast实现的，而NavMesh烘焙过程中的可达性连通测试也依赖Overlap查询排除被几何体占据的采样位置。