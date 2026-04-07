---
id: "animation-blueprint"
concept: "动画蓝图"
domain: "game-engine"
subdomain: "animation-system"
subdomain_name: "动画系统"
difficulty: 2
is_milestone: false
tags: ["UE5"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 动画蓝图

## 概述

动画蓝图（Animation Blueprint，简称 AnimBP）是 Unreal Engine 中专门用于控制骨骼网格体动画逻辑的可视化脚本系统。它与普通蓝图共用同一套节点图编辑界面，但内部分为两个独立的图表：**EventGraph**（事件图）负责读取游戏状态数据，**AnimGraph**（动画图）负责将这些数据转化为最终的骨骼姿势输出。两张图之间通过动画蓝图自身的成员变量传递信息，形成"数据计算 → 姿势合成"的单向流水线。

动画蓝图最早在 UE4 时代引入，用于取代此前基于代码驱动的动画状态管理方式，目标是让美术和技术美术人员无需编写 C++ 也能构建复杂的角色动画逻辑。到 UE5 阶段，AnimBP 进一步整合了 Control Rig、IK Rig 等节点，使其可以在同一个 AnimGraph 内完成程序化骨骼修正，覆盖从简单的跑步循环到全身 IK 的宽泛需求。

对于初学者而言，动画蓝图是让角色"活起来"的第一道关卡。它将静态的动画片段（Animation Sequence）与角色的运行时状态（速度、是否在空中、武器状态等）连接起来，决定每一帧播放哪个片段、如何过渡、如何叠加。

---

## 核心原理

### EventGraph 与 AnimGraph 的职责分离

EventGraph 在动画蓝图中以固定频率（默认与游戏线程同步，约 60Hz）执行 Tick 逻辑。开发者在这里通过 `Try Get Pawn Owner` 节点获取拥有该骨骼的 Pawn，进而读取速度向量、布尔状态等数值，并将结果写入动画蓝图的成员变量，例如 `float Speed`、`bool bIsInAir`。

AnimGraph 则是纯粹的**姿势计算图**，它在渲染线程或动画工作线程（Animation Worker Thread）上执行，每帧从 Output Pose 节点反向"拉取"骨骼数据。AnimGraph 本身不允许执行任何游戏逻辑，它只能读取 EventGraph 已经计算好并存入成员变量的值。这种分离保证了动画线程的安全性，同时也是初学者最常混淆两张图用途的根源。

### 状态机（State Machine）

在 AnimGraph 内可以创建状态机节点。每个**状态（State）**内部可以放置一个或多个动画节点（例如播放单个序列的 `Play Idle`），状态之间由**过渡规则（Transition Rule）**连接。过渡规则是一个返回布尔值的微型蓝图图，例如 `Speed > 150.0` 时从 Idle 过渡到 Walk。

状态机的执行逻辑遵循"任意时刻只有一个活跃状态"的原则（除非使用了 Conduit 或并行状态机）。过渡发生时，引擎会根据 Transition 属性中设置的混合时长（默认 0.2 秒）对前后两个状态的姿势进行线性插值，直到过渡完成后旧状态的权重降为 0。

### AnimGraph 中的姿势节点与 Final Output

AnimGraph 的数据流方向是从左到右，最右侧固定为 `Output Pose` 节点，它代表最终写入骨骼的姿势。每帧引擎从 Output Pose 向左"拉"数据，沿途每个节点计算自己的姿势输出再传递下去。常见节点包括：

- **Play Sequence**：播放单个 AnimationSequence，输出当前时间对应的骨骼姿势。
- **Blend Poses by bool / by int**：根据变量值在两个或多个姿势之间切换。
- **State Machine**：将整个状态机的输出压缩为单一姿势引脚，再连接进后续节点。

节点的计算顺序由 Output Pose 的依赖链决定，与节点在画布上的位置无关。

---

## 实际应用

### 基础角色移动动画

以第三人称角色为例，最常见的 AnimBP 结构如下：

1. **EventGraph**：每帧调用 `GetVelocity()`，计算速度向量的长度赋值给 `float Speed`；调用 `IsFalling()` 赋值给 `bool bIsInAir`。
2. **AnimGraph → 状态机**：创建三个状态——`Idle`（Speed < 10）、`Walk`（10 ≤ Speed < 300）、`Run`（Speed ≥ 300），每个状态内放对应的 AnimationSequence 节点。
3. 过渡规则分别以 `Speed` 阈值作为条件，`bIsInAir` 为真时强制过渡到独立的 `Jump` 状态。

这种结构可以在 30 分钟内完成原型搭建，是学习动画蓝图的标准起点。

### 绑定到骨骼网格体组件

动画蓝图必须**指定目标骨骼（Skeleton）**，例如 `SK_Mannequin_Skeleton`，只有使用同一套骨骼的骨骼网格体组件才能在 `Anim Class` 属性中选择该动画蓝图。绑定后，动画蓝图实例随组件创建而实例化，每个角色拥有独立的动画蓝图实例，成员变量互不干扰。

---

## 常见误区

### 误区一：在 AnimGraph 中执行游戏逻辑

许多初学者尝试在 AnimGraph 中直接调用 `GetVelocity()` 或修改角色属性，但 AnimGraph 不提供这些节点入口——它在动画线程运行，无法安全访问游戏对象。正确做法是在 EventGraph 的 Tick 中计算所有需要的数值，存入成员变量，AnimGraph 只负责读取这些变量。

### 误区二：状态机过渡规则条件写反

新手常将"进入新状态的条件"理解为"退出旧状态的条件"。在 UE5 中，过渡箭头的方向从**源状态**指向**目标状态**，过渡规则为 `true` 时**立即开始**从源到目标的混合，而不是等到当前动画播放完毕才跳转（除非勾选了 `Automatic Rule Based on Sequence Player in State`）。忽视这一点会导致循环动画被提前打断。

### 误区三：混淆动画蓝图与普通蓝图的继承关系

动画蓝图可以像普通蓝图一样设置父类，子 AnimBP 会继承父 AnimBP 的 AnimGraph 逻辑。但如果在子类中**覆写（Override）**了同名的状态机，父类中该状态机的全部内容会被完全替换，而非追加，这与普通蓝图函数覆写的"可以调用父函数"行为不同。UE5 提供了 **Linked Anim Graph** 节点来实现模块化组合，而非依赖继承叠加。

---

## 知识关联

学习动画蓝图之前，必须掌握**动画片段（Animation Sequence）**的基本属性——帧率、循环设置、根运动开关——因为这些属性直接影响 AnimBP 中 Play Sequence 节点的行为表现，例如根运动模式为 `Root Motion from Everything` 时需要在动画蓝图中开启对应的 Root Motion 支持选项。

在动画蓝图的基础上，后续可以深入**混合树（Blend Space）**——它是专门处理二维速度/方向插值的资产，通常作为一个节点嵌入到 AnimGraph 的某个状态中，替代手动写多个 Blend by Float 节点。**动画状态机**则是将本文介绍的状态机概念进行系统性扩展，涵盖 Conduit、子状态机、别名等高级特性。**Montage 系统**在动画蓝图中通过 `Slot` 节点接入，允许一次性攻击、受击等不循环动画叠加在状态机输出的基础姿势之上，两者是互补而非互斥的关系。最后，理解 **Actor-Component 模型**有助于明确动画蓝图实例挂载在骨骼网格体组件上、而组件又属于 Actor 的层级关系，避免在 `Try Get Pawn Owner` 类型转换时出现空指针错误。