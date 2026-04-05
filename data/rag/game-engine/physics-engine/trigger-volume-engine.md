---
id: "trigger-volume-engine"
concept: "触发体积"
domain: "game-engine"
subdomain: "physics-engine"
subdomain_name: "物理引擎"
difficulty: 2
is_milestone: false
tags: ["事件"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "A"
quality_score: 73.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 触发体积

## 概述

触发体积（Trigger Volume）是游戏物理引擎中一种特殊的碰撞形状，它能够检测其他物理对象进入、停留或离开其空间范围，但**不产生任何物理碰撞响应**——即不施加力、不阻挡运动、不改变对象的速度或方向。玩家或其他物体可以直接穿越触发体积，仿佛它不存在，但引擎会在后台静默记录这次"穿越"事件并触发相应回调函数。

触发体积的概念伴随着事件驱动游戏逻辑的需求而成熟。早期的2D游戏通过简单的矩形区域检测玩家坐标来实现类似功能，但这属于逐帧手动查询（Polling），效率低下。随着Unreal Engine 1（1998年）和Unity等引擎引入基于物理层的事件回调机制，触发体积成为标准工具，将"进入特定区域"这一几何事件自动转化为游戏逻辑调用，彻底替代了大量的坐标范围判断代码。

触发体积之所以重要，在于它将**空间关系与游戏逻辑解耦**。一个关卡设计师无需编写每帧检测玩家位置的代码，只需在场景中放置一个触发体积并绑定回调，即可实现剧情触发、敌人生成、音效播放、传送门激活等几乎所有需要"玩家到达某处"才发生的交互。

---

## 核心原理

### 碰撞标志位与物理层过滤

触发体积在物理引擎中本质上是一个将 `isTrigger` 标志位设为 `true` 的碰撞体（Collider/Shape）。以Unity为例，Rigidbody组件下的Box Collider勾选 `Is Trigger` 后，PhysX引擎会将其从**实体碰撞对（Solid Pair）**列表中移除，加入**触发器对（Trigger Pair）**列表。两类列表在求解器（Solver）阶段的处理完全不同：实体碰撞对会产生接触约束（Contact Constraint），而触发器对只执行AABB重叠检测（Axis-Aligned Bounding Box Overlap），不进入约束求解步骤，因此计算开销远低于真实碰撞。

### 三种标准回调事件

标准物理引擎为触发体积提供三个生命周期回调，以Unity的命名为典型参考：

| 回调函数 | 触发条件 | 调用频率 |
|---|---|---|
| `OnTriggerEnter` | 另一碰撞体首次进入体积的帧 | 仅一次 |
| `OnTriggerStay` | 另一碰撞体持续在体积内部 | 每个物理步长一次 |
| `OnTriggerExit` | 另一碰撞体离开体积的帧 | 仅一次 |

`OnTriggerStay` 默认在每个固定物理时间步（Unity中默认为 0.02 秒，即 50Hz）执行一次，而非每渲染帧执行，这一点常被初学者混淆。Unreal Engine中对应的事件名为 `OnComponentBeginOverlap`、`OnComponentEndOverlap` 和 `OnActorBeginOverlap`，概念相同但颗粒度分为组件级和Actor级两层。

### 必要触发条件：至少一方需要Rigidbody

触发体积并非对所有对象都能产生回调。在PhysX（Unity/Unreal的底层物理库）的规则中，触发器对必须满足：**两个物体中至少有一个拥有Rigidbody（动力学或运动学均可）**。若两个静态碰撞体之间发生重叠，PhysX不会产生任何触发事件，这是因为静态对静静态的碰撞对在宽相检测（Broad Phase）之后不会进入窄相（Narrow Phase）处理流程。这一底层规则直接决定了触发体积的使用约束：玩家角色控制器通常需要附带Rigidbody或CharacterController才能被触发体积感知。

---

## 实际应用

**关卡加载与区域流送：** 开放世界游戏中，触发体积被放置在通道或门口，当玩家进入时调用 `OnTriggerEnter` 异步加载下一区域的资源。《塞尔达传说：旷野之息》的地图分区加载边界本质上就是一系列不可见触发体积。

**剧情事件激活：** RPG游戏中，在NPC附近放置触发体积，玩家走进时播放过场动画。`OnTriggerEnter` 回调中检查 `other.CompareTag("Player")` 确保只有玩家（而非普通物体）能触发剧情，避免一只掉落的木桶意外启动BOSS战。

**伤害区域（DamageZone）：** 熔岩、毒雾等持续伤害区域使用 `OnTriggerStay` 回调，每个物理帧对目标施加 `damagePerSecond × Time.fixedDeltaTime` 的伤害量，精确控制每秒伤害数值而不依赖帧率。

**传送门与检查点：** 竞速游戏的计时检查点使用触发体积记录玩家通过顺序，`OnTriggerExit` 在玩家完全穿越后记录时间戳，避免玩家在边界处徘徊导致重复计时。

---

## 常见误区

**误区一：触发体积不需要Collider，只需要脚本**
部分初学者认为触发体积是纯脚本功能，删除Collider后仍期望事件被调用。实际上触发回调完全依赖物理引擎的重叠检测，必须存在带 `isTrigger = true` 的Collider组件，没有Collider就没有任何物理几何形状供引擎计算重叠，脚本中的 `OnTriggerEnter` 永远不会被调用。

**误区二：`OnTriggerStay` 每渲染帧调用一次**
`OnTriggerStay` 在物理更新循环中执行，频率由 `Fixed Timestep` 决定（默认50Hz），与渲染帧率（可能是120fps或30fps）完全独立。若在 `OnTriggerStay` 中基于 `Time.deltaTime`（渲染帧时间）而非 `Time.fixedDeltaTime`（物理步长时间）计算伤害，会导致在高帧率设备上伤害异常偏低。

**误区三：触发体积可以替代射线检测做精准交互**
触发体积的重叠检测基于碰撞体外形，无法判断"玩家看向哪里"或"子弹从哪个方向射入"等带方向性的交互。对于需要方向信息、精确命中点坐标或细长形状（如激光）的检测，应使用射线投射（Raycast）或形状投射（ShapeCast），而非触发体积。

---

## 知识关联

触发体积建立在**物理引擎概述**的基础之上，特别依赖对碰撞体（Collider）、刚体（Rigidbody）以及宽相/窄相检测流程的基本认知。理解"触发器对不进入约束求解器"这一行为，需要知道物理引擎将碰撞处理分为检测（Detection）和响应（Response）两个独立阶段——触发体积只参与检测阶段，完全跳过响应阶段。

触发体积与**碰撞事件回调**（`OnCollisionEnter`/`OnCollisionExit`）形成一组对比概念：碰撞事件附带法线方向、接触点坐标、相对速度等接触信息，适用于需要物理响应数据的场景；触发事件则只提供"谁进入了"的最简信息，适用于纯逻辑判断。在实际项目中，两者经常配合使用——碰撞体处理物理阻挡，触发体积处理游戏逻辑判定，各司其职，共同构成完整的区域交互体系。