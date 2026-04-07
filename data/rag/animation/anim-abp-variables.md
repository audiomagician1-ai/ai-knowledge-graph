---
id: "anim-abp-variables"
concept: "动画变量"
domain: "animation"
subdomain: "animation-blueprint"
subdomain_name: "动画蓝图"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# 动画变量

## 概述

动画变量（Animation Variables）是动画蓝图中专门用于驱动状态机、混合空间和动画逻辑的数据载体。不同于普通蓝图中的临时变量，动画变量在每一帧的 `AnimGraph` 求值过程中被读取，直接决定骨骼网格体播放哪个动画剪辑、两个动画之间的混合权重是多少。典型的内置例子包括 `Speed`（角色移动速度，单位 cm/s）、`Direction`（运动方向，范围 -180° ~ 180°）以及 `IsInAir`（布尔型，是否离地）。

动画变量的设计理念来自 Unreal Engine 3 时代的 AnimTree 系统，在 UE4 引入动画蓝图（2014年正式发布）时被重新设计为基于蓝图节点的变量机制。这一改变使美术和程序员都能直观地在 `EventGraph` 中更新变量，再由 `AnimGraph` 单向读取，从而实现逻辑与渲染的分离。

动画变量之所以重要，是因为它构成了游戏逻辑与骨骼动画之间的唯一数据桥梁。角色控制器产生的物理数据（速度向量、是否着地、瞄准角度等）必须先被写入动画变量，状态机才能做出正确的状态转换判断。如果缺少这个中间层，状态机的每条转换条件都必须直接调用游戏逻辑，导致严重的耦合问题。

---

## 核心原理

### 变量类型与用途对应关系

动画蓝图支持的变量类型与其驱动的动画功能直接对应：

- **Float 型**：驱动混合空间的轴坐标。例如 `Speed` 输入一维混合空间（0 ~ 600 cm/s 对应步行到奔跑），`Direction` 输入二维混合空间的 X 轴（-180 ~ 180 度）。
- **Bool 型**：驱动状态机的转换条件。`IsInAir == true` 触发从 `Grounded` 状态跳转到 `InAir` 状态；`IsCrouching` 切换蹲伏动画层。
- **Integer 型**：常用于选择动画蒙太奇的变体序号，例如 `WeaponType = 0/1/2` 对应空手、步枪、手枪三套上半身叠加动画。
- **Vector / Rotator 型**：驱动程序化的 IK 或 AimOffset，例如将角色的 `AimRotation` 存储为 Rotator 变量，再通过 `Aim Offset Player` 节点读取实现瞄准偏移。

### EventGraph 中的更新机制

动画变量的正确更新位置是 `EventGraph` 里的 `Event Blueprint Update Animation` 节点，该节点以与游戏帧率相同的频率触发（默认与渲染线程同步，启用多线程动画后在 Worker Thread 执行）。标准写法是：

1. 通过 `Try Get Pawn Owner` 获取拥有该骨骼网格体的 Pawn 引用。
2. 调用 `GetVelocity()` 返回 `FVector`，使用 `VectorLength` 节点得到标量速度，赋值给 `Speed` 变量。
3. 调用 `CalculateDirection(Velocity, ActorRotation)` 函数，返回值直接赋给 `Direction` 变量。
4. 调用 `GetMovementComponent → IsFalling()` 的布尔结果赋给 `IsInAir`。

**注意**：`EventGraph` 只能写变量，`AnimGraph` 只能读变量，两者之间不存在反向数据流。

### 变量作用域与可见性

动画变量默认的作用域是当前动画蓝图实例。如果子动画蓝图（Sub-Anim Instance）需要读取父层的变量，必须启用变量的 **`Expose to Parent Instance`** 选项，并在父蓝图的 `AnimGraph` 中通过 `Sub-Anim Instance` 节点的属性面板手动绑定。Epic 官方在 UE5 的 Lyra 示例项目中，将 `Speed`、`IsADS`（瞄准镜状态）等共用变量统一定义在 `ABP_Mannequin_Base` 父类中，子类动画蓝图通过继承直接访问，避免重复定义。

---

## 实际应用

**第三人称角色移动**：在 `ThirdPersonCharacter` 的动画蓝图中，`Speed` 变量控制 `Walk/Run BlendSpace 1D` 的横坐标。当 `Speed < 3.0 cm/s` 时混合空间输出 Idle 姿势，`Speed = 300 cm/s` 输出步行循环，`Speed = 600 cm/s` 输出奔跑循环。这三个数值必须与混合空间编辑器中设置的采样点精确匹配，否则会出现动画滑步。

**扫射移动（Strafe）**：使用 `Speed`（前向速度）和 `Direction`（横向偏角）组合驱动二维混合空间 `Walk_Strafe_BS`，可以让角色向左跑时播放向左倾斜的动画。`Direction` 由 UE 内置函数 `CalculateDirection` 计算，返回值范围严格限定在 -180 到 180 度之间，不需要手动 Clamp。

**武器切换时的上半身叠加**：将整数变量 `OverlayState` 设为 0（空手）、1（步枪）、2（手枪），在 `AnimGraph` 的 `Layered Blend Per Bone` 节点之前用 `Switch on Int` 节点选择对应的上半身叠加动画序列，实现下半身移动动画与上半身持枪动画的独立控制。

---

## 常见误区

**误区一：在 AnimGraph 中直接调用函数获取速度**
部分初学者在 `AnimGraph` 的 `Pure Function` 节点中调用 `GetVelocity`，看似简洁，但这会导致在多线程动画模式下触发线程安全警告甚至崩溃，因为 `GetVelocity` 访问的 `UMovementComponent` 数据并非线程安全。正确做法是将所有 Pawn 数据的读取集中在 `EventGraph` 的 Update 节点中，写入动画变量后再由 `AnimGraph` 读取。

**误区二：Speed 变量使用世界空间速度向量的 Z 分量**
`GetVelocity` 返回的 `FVector` 包含 Z 轴速度（跳跃上升/下落速度）。如果直接取向量长度赋给 `Speed`，角色在跳跃时 `Speed` 值会虚高，导致混合空间错误输出奔跑动画而不是跳跃动画。正确做法是在赋值前将 Z 分量清零：`VSize(FVector(Velocity.X, Velocity.Y, 0.0))`，只计算水平面速度。

**误区三：误以为 Bool 变量状态改变会立即触发状态机跳转**
状态机的转换条件在当前状态的最小停留时间（`Min State Time`）到期后才会被评估，即使 `IsInAir` 在同一帧从 `false` 变为 `true`，如果当前状态设置了 0.1 秒的最小停留，状态跳转仍会延迟。这不是动画变量本身的问题，而是状态机转换规则的限制，两者需要分开调试。

---

## 知识关联

**前置：事件图（EventGraph）**
动画变量的更新逻辑全部写在 EventGraph 的 `Event Blueprint Update Animation` 节点下。理解 EventGraph 的执行顺序（每帧调用一次，早于 AnimGraph 求值）是正确使用动画变量的前提——只有 EventGraph 先完成变量写入，AnimGraph 在同一帧读取时才能拿到最新数据。

**后续：多线程动画（Multi-Threaded Animation）**
启用 `Use Multi-Threaded Animation Update` 后，`Event Blueprint Update Animation` 会在 Worker Thread 而非 Game Thread 执行。这要求动画变量的更新代码只能访问线程安全的数据（如已缓存的 Float/Bool 值），不能在 Update 节点中直接调用非线程安全的 Actor 函数。因此，在学习多线程动画之前，养成"先缓存到动画变量、再在 AnimGraph 中读取"的习惯，能让代码在开启多线程后无需大规模重构。