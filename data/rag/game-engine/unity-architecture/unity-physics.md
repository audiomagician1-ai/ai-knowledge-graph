---
id: "unity-physics"
concept: "Unity Physics"
domain: "game-engine"
subdomain: "unity-architecture"
subdomain_name: "Unity架构"
difficulty: 2
is_milestone: false
tags: ["物理"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---


# Unity Physics：内置PhysX与DOTS Physics对比

## 概述

Unity物理系统提供了两套截然不同的物理模拟方案：基于NVIDIA PhysX 4.1的传统物理系统（Built-in Physics），以及专为数据导向技术栈（DOTS）设计的新一代Unity Physics包（com.unity.physics）。两者并非简单的版本迭代关系，而是底层架构哲学的根本分歧——前者依赖面向对象的Rigidbody组件驱动，后者完全基于ECS（Entity Component System）实体结构运行。

传统PhysX集成随Unity 3.x时代引入，历经多年迭代已深度融合于Unity编辑器中，开发者通过挂载Rigidbody和Collider组件即可启用物理模拟。Unity Physics（DOTS版本）于Unity 2019 DOTS预览包中首次亮相，正式版本随Unity 2022 LTS逐步稳定，其核心代码采用C# Burst Compiler编译，可完全绕开传统托管堆内存分配。理解这两套系统的选型逻辑，直接影响项目能否在移动端实现60帧稳定物理模拟，或在开放世界中支撑数千个动态刚体同时运算。

## 核心原理

### 传统PhysX的工作机制

Built-in Physics的更新发生在Unity主循环的**FixedUpdate**阶段，默认固定时间步长为0.02秒（即50Hz）。每帧物理计算由PhysX引擎接管，GameObject的Transform数据通过Rigidbody组件与PhysX内部Actor对象同步。PhysX引擎在独立线程运行碰撞检测，但其结果回写到主线程GameObject上时会引发线程同步开销。

碰撞检测精度由Rigidbody上的`Collision Detection`枚举控制：
- **Discrete（离散）**：每帧检测一次，高速物体可能穿透薄壁碰撞体
- **Continuous（连续）**：对动态与静态碰撞体执行扫掠测试（Sweep Test），CPU开销提升约30-50%
- **Continuous Speculative（推测连续）**：通过膨胀凸包预测碰撞位置，误判率低于Continuous但存在幽灵碰撞边缘案例

碰撞回调函数`OnCollisionEnter`、`OnTriggerStay`等均在主线程C#托管环境中执行，每次回调都会产生GC Allocation，在每秒数百次碰撞事件的场景中可导致明显的帧率抖动。

### Unity Physics（DOTS）的工作机制

Unity Physics完全以**Job System + Burst Compiler**为基础，物理世界数据存储在NativeArray等非托管内存容器中，消除了GC压力。其物理更新通过`PhysicsSystemGroup`在ECS World的SystemGroup调度中执行，与传统FixedUpdate并行存在，可在同一项目中同时运行两套物理系统（需注意资源消耗叠加）。

DOTS物理的核心数据结构为**BroadphaseTree**（宽相树），基于轴对齐包围盒（AABB）的分层结构加速碰撞对筛选。窄相碰撞使用GJK（Gilbert–Johnson–Keerthi）算法配合EPA（Expanding Polytope Algorithm）求解接触点，这与PhysX使用的SAT算法有明显差异，导致两套系统对同一几何体的碰撞结果存在毫米级偏差。

Unity Physics默认**无状态（Stateless）**——每帧从零重建碰撞世界，不缓存碰撞对历史。这意味着摩擦力和弹性系数的表现与PhysX有细微差异，但同时使物理仿真具有完美的确定性（Determinism），相同输入在任意平台产生逐位相同的结果，这对帧同步网络游戏（Lockstep Networking）至关重要。

### 两套系统的性能对比维度

| 维度 | Built-in PhysX | Unity Physics (DOTS) |
|---|---|---|
| 刚体上限（稳定60fps） | 约100-500个（视硬件） | 数千至数万个 |
| 内存分配 | 每帧产生GC | 零GC（NativeArray） |
| 确定性 | 不保证跨平台一致 | 完全确定性 |
| 编辑器集成 | 原生支持 | 需ECS转换流程 |
| 关节（Joint）支持 | 完整（6自由度关节等） | 较有限（受限关节类型） |

## 实际应用

**移动端格斗游戏**：人物碰撞检测使用Built-in Physics中的`Physics.OverlapSphere`（传统API），在Update中对半径0.5m范围检测敌方Layer，既利用PhysX缓存的宽相结果，又避免创建多余Rigidbody。每次查询不产生碰撞回调，规避GC开销。

**RTS游戏大规模单位模拟**：数千个士兵单位切换至Unity Physics（DOTS），每个单位以`PhysicsBody` + `PhysicsShape` ECS组件描述，Burst编译的`CollisionWorld.CastRay` Job在4核移动CPU上可并行处理8000次射线检测，耗时约1.2ms，而相同场景下传统`Physics.Raycast`串行调用需要约18ms。

**车辆物理**：传统PhysX的`WheelCollider`组件封装了完整的悬挂弹簧-阻尼模型和轮胎侧偏力曲线（Pacejka模型近似），是需要快速原型验证车辆手感的首选。DOTS目前（Unity 6.0）尚未提供等效的WheelCollider实现，开发者需自行用约束关节组合模拟悬挂行为。

## 常见误区

**误区一：认为升级到DOTS Physics就必然提升性能**。对于刚体数量少于200个的普通游戏场景，切换至DOTS Physics不但无法带来收益，反而因ECS Baking转换管线（AuthoringComponent → BlobAsset）增加了构建时间和调试复杂度。DOTS物理的性能优势需在大规模并行场景下才能体现，阈值通常在500个以上动态刚体并发。

**误区二：混用两套系统时认为它们会自动交互**。Built-in Physics管理的GameObject Rigidbody与DOTS Physics管理的Entity PhysicsBody完全处于不同物理世界（PhysicsWorld实例），两者之间**不存在**自动碰撞检测。若需要交互，必须自行编写System从ECS查询碰撞结果并手动更新GameObject Transform，这是常见的架构陷阱。

**误区三：以为传统PhysX的`OnCollisionStay`性能无关紧要**。当场景中存在大量静止接触的刚体时（例如堆叠的木箱），`OnCollisionStay`每帧针对每对接触面调用一次，100个相互接触的箱子可产生每帧数百次回调，即使回调函数体为空也会消耗约0.5-2ms，清空内容不等于消除调用开销。

## 知识关联

学习Unity Physics之前需要掌握**Unity引擎概述**中的MonoBehaviour生命周期（FixedUpdate执行时机）以及Unity的Layer系统（物理层碰撞矩阵由Layer Collision Matrix配置，位于Project Settings → Physics），这两点直接影响PhysX如何筛选碰撞对。

完成本节后进入**物理引擎概述**时，可以用Unity这两套系统作为具体锚点理解更广泛的概念：PhysX代表了行业主流的宽相+窄相两阶段检测管线，而DOTS Physics的无状态设计则呼应了函数式物理引擎（如Bullet Physics确定性分支）的设计哲学。Unity 6.0中引入的**Havok Physics for Unity**（com.havok.physics）作为第三选项，在DOTS架构上叠加有状态模拟，可与Unity Physics无缝切换，代表了两种哲学的折衷路线。