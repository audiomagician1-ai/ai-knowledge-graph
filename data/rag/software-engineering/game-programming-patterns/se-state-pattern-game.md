---
id: "se-state-pattern-game"
concept: "状态模式(游戏)"
domain: "software-engineering"
subdomain: "game-programming-patterns"
subdomain_name: "游戏编程模式"
difficulty: 2
is_milestone: false
tags: ["AI"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 82.9
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

# 状态模式（游戏）

## 概述

状态模式在游戏开发中专指用有限状态机（Finite State Machine，FSM）来管理角色或AI行为的设计方案。其核心思想是：将角色在不同状态下的行为逻辑封装为独立的状态对象，角色持有一个指向当前状态的指针，所有行为调用委托给该状态对象执行，当转换条件满足时切换指针指向新状态。这种结构由计算机科学家 George H. Mealy 和 Edward F. Moore 在 1950 年代形式化定义，后被游戏工业广泛采用。

在游戏史上，FSM 最经典的应用是 1990 年代 id Software 的《毁灭战士》中敌人 AI 的实现：每个�怪物有 Spawn、See、Pain、Melee、Missile、Death 等明确状态，每帧根据输入（玩家距离、受伤事件）在状态间切换。这种实现的意义在于彻底解决了"巨型 if-else 地狱"——当角色拥有 10 种以上行为时，不使用状态模式会导致每帧的条件判断代码膨胀到数百行，且每次新增行为都需要修改已有的条件分支，违反开闭原则。

游戏中使用状态模式的必要性还体现在多帧持续行为上：普通函数调用在单帧内完成，但"奔跑后滑行 0.3 秒"、"硬直帧 12 帧内不可打断"等行为需要跨帧维持状态信息，而状态对象天然地承载了这些帧间持久数据。

## 核心原理

### 基础结构：状态接口与上下文

游戏 FSM 的最小实现由三个部分组成：`IState` 接口（定义 `Enter`、`Update`、`Exit` 三个生命周期方法）、若干具体状态类（如 `IdleState`、`RunState`、`AttackState`）、以及上下文类（通常是角色类本身，持有 `currentState` 指针并在每帧调用 `currentState.Update()`）。

```csharp
interface IState {
    void Enter(Character ctx);
    void Update(Character ctx);
    void Exit(Character ctx);
}
```

`Enter` 在状态切换时执行一次性初始化（如播放动画、重置计时器），`Exit` 在离开时做清理（如解除锁定），`Update` 每帧执行持续逻辑。这三个方法的分离是游戏状态模式区别于通用设计模式中简化版状态模式的关键特征——通用版通常只有 `Handle` 一个方法，无法处理"进入瞬间"和"退出瞬间"的事件。

### 状态转换的两种实现方式

**方式一：状态自驱动转换**——由当前状态对象内部决定何时切换，在 `Update` 中检查条件后调用 `ctx.ChangeState(new RunState())`。优点是每个状态完全自治，缺点是状态间存在直接依赖（`IdleState` 需要 `import RunState`）。

**方式二：转换表（Transition Table）**——在上下文或独立的配置文件中定义 `(当前状态, 触发事件) → 目标状态` 的映射表。例如《塞尔达传说》系列的敌人 AI 使用数据驱动的转换表，策划可以在不修改代码的情况下调整 AI 行为。转换表的存储结构通常是二维数组或字典：`Dictionary<(StateType, EventType), StateType>`。

游戏工业实践中，规模超过 7 个状态的 FSM 推荐使用转换表，否则状态间的相互引用会形成紧耦合网。

### 层次状态机（HSM）与并发状态机

当角色状态数量超过 15 个时，扁平 FSM 难以维护，游戏工业引入**层次状态机（Hierarchical State Machine）**。其核心是"超状态（superstate）"概念：`OnGround` 超状态包含 `Idle`、`Run`、`Crouch` 三个子状态，共有逻辑（如重力计算、摩擦力）写在 `OnGround` 的 `Update` 中，子状态仅处理差异逻辑。Unity 的 Animator Controller 本质上就是一个 HSM 编辑器，其 `Any State` 节点实现了从任意子状态到指定状态的全局转换。

**并发状态机**解决角色同时有多个独立状态维度的问题，例如角色同时有"移动状态"（Idle/Run/Jump）和"装备状态"（Unarmed/Sword/Gun），两个维度各自独立运行，组合出 3×3=9 种表现，但只需维护 3+3=6 个状态类。

## 实际应用

### 平台跳跃角色控制器

以马里奥式角色为例，标准实现包含 `GroundState`（检测跳跃输入后切换到 `JumpState`）、`JumpState`（在 `Enter` 中施加向上速度 `velocity.y = 8.5f`，在 `Update` 中检测碰地后切换回 `GroundState`）、`FallState`（从平台边缘走出后触发）、`DashState`（进入时记录 `dashTimer = 0.2f`，每帧递减，归零时退出）。这 4 个状态覆盖了基础手感所需的全部跨帧行为，且新增"攀墙跳"状态只需添加 `WallState` 类，无需修改其他状态。

### 敌人 AI 巡逻-追击-攻击循环

RPG 或动作游戏中最常见的敌人 AI FSM 包含：`PatrolState`（沿路径点循环移动，检测到玩家进入半径 8 单位内时切换到 `ChaseState`）、`ChaseState`（持续向玩家移动，当距离小于 1.5 单位时切换 `AttackState`，当玩家距离超过 15 单位时返回 `PatrolState`）、`AttackState`（播放攻击动画，锁定 0.6 秒后返回 `ChaseState`）。这三个状态和两组距离阈值完整定义了敌人的战斗逻辑，策划数值调整只需修改阈值常量。

### 游戏 UI 流程管理

状态模式同样适用于管理游戏 UI 流程：`MainMenuState`、`GameplayState`、`PauseState`、`GameOverState` 各自管理自己的 UI 层显示/隐藏、输入监听的开关，避免了在一个庞大的 UIManager 类中用布尔标志位判断当前应该响应哪些输入事件。

## 常见误区

**误区一：每帧 new 一个新状态对象**。初学者实现状态切换时常写 `ChangeState(new RunState())`，在 60fps 的游戏中状态频繁切换会产生大量 GC 压力。正确做法是在角色初始化时预分配所有状态实例并缓存：`states[StateType.Run] = new RunState()`，切换时只交换引用而不创建对象。

**误区二：将状态做成单例（Singleton）**。若多个同类角色共享同一个状态单例，而状态对象内部存储了与特定角色绑定的帧间数据（如 `attackTimer`），则不同角色的状态数据会互相覆盖。游戏中状态对象应设计为无状态（将帧间数据存在上下文/角色类中）或每角色独立实例。

**误区三：用状态机管理所有游戏逻辑**。FSM 不适合描述"按顺序执行一系列动作"的行为（如 Boss 的多阶段连招），这类行为用**行为树（Behavior Tree）**或**协程（Coroutine）**更合适。强行用 FSM 实现 10 步连招会产生 `Attack1State → Attack2State → … → Attack10State` 的线性链，与简单的数组迭代相比毫无优势。

## 知识关联

状态模式（游戏）直接建立在 GoF **状态模式**的基础上，但添加了 `Enter`/`Exit` 生命周期和 Unity Animator 等工具层实现。与**原型模式（游戏）**的关联在于：当需要克隆一个处于特定状态的角色时（如生成与原版角色行为完全相同的分身），需要同时深拷贝角色的当前状态对象及其内部计时器数据，浅拷贝只复制状态引用会导致两个角色共享同一状态实例。

学习状态模式之后，下一步是**命令模式（游戏）**。命令模式解决的问题与状态模式形成互补：状态模式管理角色"当前能做什么"，命令模式管理"玩家的操作指令如何映射到行为"，两者组合使用时，命令对象负责触发状态转换事件，而状态对象负责决定是否响应该事件（例如处于硬直状态时忽略所有移动命令）。