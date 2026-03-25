---
id: "anim-fsm-basics"
concept: "状态机基础"
domain: "animation"
subdomain: "state-machine"
subdomain_name: "状态机"
difficulty: 1
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.448
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 状态机基础

## 概述

有限状态机（Finite State Machine，简称 FSM）是动画系统中用于管理角色行为的逻辑框架，其核心思想是：一个对象在任意时刻只能处于**有限个状态中的一个**，并在特定条件满足时从一个状态切换到另一个状态。在游戏动画中，FSM 解决了"角色此刻应该播放哪段动画"这个根本问题，将动画逻辑从代码中分离出来，用可视化节点图来表达。

FSM 的理论来源于 1955 年 George H. Mealy 和 Edward F. Moore 提出的自动机理论。游戏引擎将这一数学模型引入动画系统后，Unity 的 Animator Controller（2012 年随 Unity 4.0 推出的 Mecanim 系统）和虚幻引擎的 Animation Blueprint 都以 FSM 为基础架构。对于动画师和开发者而言，理解 FSM 意味着能够用逻辑化的方式组织数十甚至数百段动画片段，而不是编写混乱的 `if-else` 嵌套代码。

## 核心原理

### 状态（State）

状态是 FSM 中最基本的单元，代表角色在某一时刻正在执行的动画行为。一个典型角色动画 FSM 包含的状态例如：**Idle（待机）、Walk（行走）、Run（奔跑）、Jump（跳跃）、Fall（下落）、Attack（攻击）**。每个状态内部绑定一段或一组动画片段，当角色处于该状态时，对应的动画持续循环或单次播放。

在 Unity Animator 中，每个状态节点可以指定一个 Animation Clip，也可以指定一个 Blend Tree（混合树）。FSM 中有一个特殊的**默认状态（Default State）**，以橙色节点标示，系统初始化时自动进入该状态，通常设置为 Idle。

### 转换（Transition）

转换是连接两个状态的有向箭头，表示"从状态 A 切换到状态 B"这一过程。转换本身也携带两个关键参数：

- **Exit Time（退出时间）**：以归一化时间表示，值为 0.75 意味着当前动画播放到 75% 时才允许触发该转换。
- **Transition Duration（过渡时长）**：两段动画之间的混合时长，默认值通常为 0.25 秒，决定动画切换的平滑程度。

转换的方向性非常重要。从 Idle 到 Run 的转换和从 Run 到 Idle 的转换是两条独立的箭头，各自可以设置不同的条件和参数。忽视方向性是初学者最常见的设置错误。

### 条件（Condition）

条件是触发转换的判断依据，依赖于**参数（Parameter）**的值。FSM 支持四种参数类型：

| 参数类型 | 数据类型 | 典型用途 |
|---------|---------|---------|
| Float | 浮点数 | 移动速度（Speed > 0.1 时进入 Walk） |
| Int | 整数 | 攻击连击计数 |
| Bool | 布尔值 | isGrounded（是否落地） |
| Trigger | 单次触发 | Jump 触发跳跃，自动复位 |

条件的逻辑关系为**AND（与）**：同一个转换上的多个条件必须同时满足才能触发。若需要 OR（或）逻辑，则需要设置多条从同一起点出发的并行转换。

### 有限性的含义

"有限"不仅指状态数量有限，更重要的约束是**任意时刻只能处于一个状态**（不考虑 Sub-State Machine 和 Layer 叠加的情况）。这意味着 FSM 天然排斥状态冲突：角色不可能同时处于 Walk 和 Run 两个状态，系统必须明确地完成一次转换才能进入新状态。这一约束使动画逻辑具有可预测性，但也带来了状态数量爆炸的问题——10 个状态之间理论上存在 `10 × 9 = 90` 条可能的转换路径。

## 实际应用

**基础角色控制器**是 FSM 最典型的应用场景。一个第三人称跑酷游戏角色通常包含以下 FSM 结构：

1. 默认进入 **Idle** 状态
2. 当 Float 参数 `Speed` 大于 0.1 时，转换至 **Walk**；大于 5.0 时转换至 **Run**
3. 当 Trigger 参数 `JumpTrigger` 被激活且 Bool 参数 `isGrounded` 为 true 时，转换至 **Jump**
4. 当 `isGrounded` 变为 false 且垂直速度为负时，从 Jump 转换至 **Fall**
5. 当 `isGrounded` 再次变为 true 时，从 Fall 转换回 **Idle**

这条状态链路覆盖了玩家 80% 以上的日常操作，仅用 5 个状态和约 8 条转换即可实现。

在 Unity 的具体实现中，代码端通过 `animator.SetFloat("Speed", currentSpeed)` 和 `animator.SetTrigger("JumpTrigger")` 来驱动参数，FSM 根据这些参数值自主决定何时切换状态，动画逻辑与游戏逻辑因此解耦。

## 常见误区

**误区一：认为转换是即时完成的**
许多初学者设置好条件后，发现动画切换有明显的"拖尾"感，误以为是条件设置错误。实际上是 Transition Duration（默认 0.25 秒）造成的混合过渡。对于需要即时响应的动作（如格挡被击），应将 Transition Duration 设为 0，并勾选"Interruption Source"来允许打断当前过渡。

**误区二：所有转换都依赖 Exit Time**
Exit Time 适用于动画必须播放到特定进度才能切换的场景（如攻击动画播放至 90% 再回到 Idle）。若 Exit Time 和条件同时启用，两者须**同时满足**才触发转换。大量使用 Exit Time 会导致角色响应迟钝，移动类状态（Idle/Walk/Run 之间的转换）通常应关闭 Exit Time，仅依赖参数条件驱动。

**误区三：用大量 Bool 参数代替 Trigger**
将跳跃等一次性动作绑定到 Bool 参数（如 `isJumping = true`），需要在代码中手动将其重置为 false，极易因时序问题导致状态卡死。Trigger 参数在转换被消耗后**自动归零**，天然适合描述瞬时事件，这是它区别于 Bool 的根本设计意图。

## 知识关联

**前置概念**：游戏动画与影视动画的本质差异在于**交互性**——玩家输入随时可能改变动画播放意图，这正是 FSM 存在的理由。影视动画按时间轴顺序播放，不需要状态管理；游戏动画必须响应运行时输入，因此需要 FSM 这样的条件驱动系统。

**后续概念**：掌握状态与转换的基本概念后，下一步是学习**状态转换的高级控制**，包括转换优先级（同一状态有多条出发转换时，排列顺序决定检测优先级）以及如何调试 FSM 中的转换冲突。**Any State 转换**则解决了"无论当前处于哪个状态，满足条件时都必须切换"的场景（如受到致命伤害时无论处于何种状态都进入 Death 状态），是 FSM 有限性约束的重要补充机制。
