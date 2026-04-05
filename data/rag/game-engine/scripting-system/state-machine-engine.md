---
id: "state-machine-engine"
concept: "通用状态机"
domain: "game-engine"
subdomain: "scripting-system"
subdomain_name: "脚本系统"
difficulty: 2
is_milestone: false
tags: ["模式"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# 通用状态机

## 概述

通用状态机（General State Machine）是游戏脚本系统中用于管理对象行为逻辑的有限状态自动机模型，包含有限状态机（FSM）、层次化有限状态机（HFSM）和下推自动机（Pushdown Automaton）三种主要变体。其数学定义为一个五元组 **M = (Q, Σ, δ, q₀, F)**，其中 Q 为有限状态集合，Σ 为输入字母表（触发事件集），δ 为转移函数 δ: Q × Σ → Q，q₀ 为初始状态，F 为终止状态集。

状态机思想最早可追溯至 1943 年 McCulloch 和 Pitts 的神经网络形式化论文，而 FSM 在游戏中的系统性应用则随 1990 年代 AI 驱动的 NPC 行为设计兴起。《毁灭战士》（1993）中的怪物 AI 使用了简单 FSM，每个敌人仅有"巡逻/追击/攻击/逃跑"等约 4–6 个状态，这成为游戏状态机工程化的早期范本。

在脚本系统中引入通用状态机的核心价值在于：将对象的行为逻辑分解为离散的状态节点，每个状态封装独立的 `OnEnter`、`OnUpdate`、`OnExit` 回调，避免了在单一 Update 函数中嵌套大量 `if-else` 分支所导致的逻辑耦合与维护困难。Unity 的 Animator Controller 和 Unreal Engine 的 AI Behavior Tree 底层均采用了类似状态机机制。

---

## 核心原理

### 基本有限状态机（FSM）

FSM 的运行逻辑遵循严格的单一当前状态约束：在任意时刻，对象仅处于 Q 中的唯一一个状态。转移条件满足时，系统依次执行：当前状态的 `OnExit()` → 更新当前状态指针 → 新状态的 `OnEnter()`。一个典型的角色 FSM 包含以下状态与转移：

- **Idle → Run**：检测到移动输入时触发
- **Run → Jump**：按下跳跃键且 `isGrounded == true`
- **Jump → Fall**：垂直速度 `vy < 0`
- **Fall → Idle**：`isGrounded == true`

FSM 的状态数量与转移数量之间存在 O(n²) 的潜在增长关系：n 个状态最多可产生 n×(n-1) 条转移边，当角色状态超过 10 个时，维护成本急剧上升，这是促使 HFSM 出现的直接原因。

### 层次化有限状态机（HFSM）

HFSM 允许状态嵌套：一个"超状态"（Superstate）可以包含若干子状态机，子状态机共享超状态级别的转移规则。例如，将"In Combat"定义为超状态，其内部包含"Melee/Ranged/Dodge"三个子状态；无论当前处于哪个子状态，只要触发"HP < 20%"事件，都会统一转移到顶层的"Flee"状态，无需在每个子状态中单独配置该转移。

HFSM 的层级深度通常建议不超过 3–4 层，过深的嵌套会导致调试时状态路径追踪困难。Unreal Engine 4 的 AnimGraph 支持 HFSM，其"State Machine"节点内可以再嵌套"State Machine"节点即为该机制的工程实现。

### 下推自动机（Pushdown Automaton, PDA）

PDA 在 FSM 的基础上增加了一个后进先出（LIFO）的**状态栈**，其转移函数扩展为 δ: Q × Σ × Γ → Q × Γ*，其中 Γ 为栈字母表。在游戏脚本中，PDA 最常用于实现可恢复的状态中断，例如：

1. 角色当前处于"Run"状态，栈为 [Run]
2. 触发对话事件，将"Run"压栈，切换到"Dialogue"状态，栈为 [Dialogue, Run]
3. 对话结束后，弹出"Dialogue"，恢复到"Run"状态，栈还原为 [Run]

若用普通 FSM 实现上述逻辑，需要为每个可能被打断的状态单独添加"从 Dialogue 返回至 X"的转移边，状态数量越多，转移边数量呈线性增长；PDA 则用一个通用的"弹栈"操作统一处理所有返回场景。

---

## 实际应用

**RPG 敌人 AI**：在《黑暗之魂》类游戏中，敌人 AI 通常采用 HFSM，顶层状态为"Passive/Alert/Combat/Dead"，Combat 超状态内嵌"Approach/Attack/Recover/Guard"子状态机，配合每帧执行的感知检测更新转移条件。

**UI 界面管理**：使用 PDA 管理多层界面跳转是游戏开发中的标准实践。主菜单→设置→按键映射的三层界面，通过连续压栈进入，连续弹栈退出，确保返回顺序正确且无需硬编码每层界面的"上一页"目标。

**动画状态机**：Unity Animator 的 Animator Controller 本质是一个 HFSM。每个 State 对应一个 AnimationClip，Transition 配置转移条件（如参数 `Speed > 0.1f`），Sub-State Machine 对应 HFSM 的超状态，在项目中一个角色的 Animator Controller 通常包含 15–40 个状态节点。

---

## 常见误区

**误区一：认为 FSM 只适合简单 AI，复杂行为必须用行为树替代。**  
实际上，FSM 与行为树并非替代关系。行为树擅长表达任务分解与条件选择，FSM 擅长表达持续性状态与状态间转移。许多商业游戏将二者混合使用：行为树的叶节点调用状态机切换，或状态机的某个状态内部运行一棵行为树。

**误区二：PDA 的状态栈可以无限深度压栈。**  
在实际游戏脚本实现中，未加限制的压栈会因逻辑 bug（如重复触发压栈事件）导致栈溢出或状态混乱。工程实践中通常设置最大栈深度（常见值为 8–16 层），并在 `Push` 操作前检查是否已达上限，超出时打印警告并拒绝压栈。

**误区三：HFSM 的子状态切换会自动触发超状态的 OnEnter。**  
当转移发生在同一超状态的子状态之间时，超状态的 `OnEnter` 和 `OnExit` **不会**被重复调用，仅子状态的对应回调触发。只有当转移跨越超状态边界时，才会触发超状态级别的生命周期回调。混淆此规则会导致超状态中的初始化逻辑被意外多次执行。

---

## 知识关联

通用状态机建立在**脚本系统概述**所介绍的脚本生命周期（Awake/Start/Update/Destroy）基础之上：FSM 的 `OnUpdate` 回调直接映射到脚本的逐帧 Update 调用，而 `OnEnter`/`OnExit` 对应对象组件的激活与禁用模式。理解脚本组件的挂载机制，有助于在工程中选择"每个状态作为独立脚本组件"还是"单一脚本内部用枚举管理状态"两种实现范式。

通用状态机所建立的**状态封装与转移驱动**思维，是后续学习行为树（Behavior Tree）、目标导向行动规划（GOAP）等更复杂 AI 架构的直接前置认知：理解 FSM 的局限性（状态爆炸问题、缺乏并发状态支持），正是这些高级架构被设计出来的动机所在。