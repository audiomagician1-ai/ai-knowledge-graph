---
id: "anim-combat-sm"
concept: "战斗状态机"
domain: "animation"
subdomain: "state-machine"
subdomain_name: "状态机"
difficulty: 3
is_milestone: false
tags: ["实战"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.2
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# 战斗状态机

## 概述

战斗状态机（Combat State Machine）是专门用于管理角色战斗行为的有限状态机，其核心节点通常包含 Idle（待机）、Attack（攻击）、Hit（受击）、Dodge（闪避）和 Block（格挡）五个基础战斗状态。与移动状态机处理位移和方向不同，战斗状态机的转换条件主要来自输入指令、伤害事件和帧计时，每个状态都与特定的动画片段和伤害判定窗口紧密绑定。

战斗状态机的概念随着格斗游戏的发展在1990年代趋于成熟。Capcom在《街头霸王II》（1991年）的开发中便使用了基于帧的状态切换逻辑，每个动作状态以帧（Frame）为单位定义持续时长、无敌帧、受击判定和攻击判定。这种设计思路后来成为动作游戏角色控制的通用范式，在Unity、Unreal Engine等现代引擎的Animator Controller中均有直接体现。

战斗状态机的意义在于它将"何时能做什么"的逻辑从动画播放逻辑中解耦。若没有状态机约束，角色可能在攻击动画播放中途被打断跳回待机，导致动画撕裂和伤害判定错误；通过为每个状态设置明确的优先级和可中断条件，开发者能够精确控制"攻击命中瞬间即使玩家松手也必须播放完整收招动画"这类细节。

---

## 核心原理

### 五状态的拓扑结构与转换规则

战斗状态机的五个核心状态并非全连通图，而是遵循特定的有向拓扑结构：

- **Idle → Attack**：玩家按下攻击键触发，Idle 是唯一可以主动发起攻击的源状态（部分设计允许 Dodge 取消接攻击）。
- **Attack → Hit**：在攻击的"受击可打断窗口"（通常是前摇帧）内被命中时触发，收招阶段一般设为无法被 Hit 打断，即"霸体帧"。
- **Hit → Idle**：受击硬直（Hitstun）持续固定帧数后自动返回，典型值为 12~30 帧（60fps 基准）。
- **Any → Dodge**：闪避拥有最高主动优先级，可从 Idle、Attack 前摇、Hit 中途触发，但 Block 状态下通常禁止闪避以防止防御循环利用。
- **Idle → Block / Block → Idle**：Block 是持续型状态，依赖持续按键保持，松开立刻退出，期间角色受到的伤害会路由到格挡逻辑而非 Hit 状态。

关键设计原则：**优先级队列**。当多个转换条件同时满足时（如同帧内受到攻击且玩家按下闪避键），需要预先定义 Dodge > Hit > Block > Attack > Idle 的优先级顺序。

### 帧数据与状态持续时间

战斗状态机的每个状态都必须携带精确的帧数据，而不是仅靠动画时长控制。以攻击状态为例，一次普通攻击状态通常拆分为三段：

| 子阶段 | 典型帧数 | 特殊属性 |
|--------|----------|----------|
| 前摇（Startup） | 5~8 帧 | 可被 Hit 打断，不可取消 |
| 活跃（Active） | 2~4 帧 | 伤害盒激活，部分设计有无敌帧 |
| 后摇（Recovery） | 10~20 帧 | 可设置取消窗口（Cancel Window） |

"取消窗口"是战斗状态机中的关键设计——在后摇的第 N 帧到第 M 帧之间允许接受新的 Attack 输入，从而实现连击系统（Combo Chain）。若将后摇取消窗口设置为第 12~18 帧，则玩家必须在此窗口内再次按键才能无缝衔接下一段攻击。

### 状态机中的伤害路由逻辑

战斗状态机不仅控制动画，还充当伤害判定的路由中心。当角色处于不同状态时，同一个"受到攻击"事件会产生不同的处理结果：

- **Idle/Attack 前摇状态下受击**：进入 Hit 状态，扣除血量，播放受击动画，触发硬直。
- **Block 状态下受击**：不进入 Hit 状态，仅扣除耐力值（Stamina），播放格挡弹反动画，角色保持 Block 状态。
- **Dodge 无敌帧内受击**：事件被吸收，不触发任何状态转换，不扣血。
- **Attack 霸体帧内受击**：扣血但不中断状态，动画继续播放到收招。

这种路由逻辑在代码层面通常通过"状态持有者询问当前状态"的方式实现，而非在碰撞检测回调中直接调用 TakeDamage，从而保证状态机对伤害处理拥有完整的控制权。

---

## 实际应用

**Unity Animator Controller 实现示例**  
在 Unity 中构建战斗状态机时，每个战斗状态对应一个 Animator State，转换条件使用 Trigger 参数（如 `attackTrigger`、`hitTrigger`）和 Bool 参数（如 `isBlocking`）驱动。关键设置是关闭"Can Transition to Self"选项，防止 Attack 状态在自身播放期间重复触发，同时为 Hit 状态启用"Interrupt Source: Next State Priority"以允许 Dodge 在硬直中途打断。

**《黑暗之魂》的战斗状态机设计**  
FromSoftware 在《黑暗之魂》系列中将战斗状态机与资源消耗紧密结合。每次攻击、闪避和格挡都消耗耐力值（Stamina），当耐力耗尽时，Block 状态强制退出并触发"盾击破碎（Guard Break）"状态——这是一个额外的 Stunned 状态，它不属于基础五状态，但通过扩展战斗状态机添加为特殊受击变体，持续时间（约 90 帧）远长于普通 Hit 硬直。

**连击系统的状态机实现**  
在格斗游戏中，三段连击"弱攻击→弱攻击→强攻击"可以用三个独立的 Attack 子状态（Attack_1、Attack_2、Attack_3）建模，分别携带不同的伤害盒和动画。Attack_1 的取消窗口内输入攻击键跳转到 Attack_2，Attack_2 的取消窗口内输入重攻击键跳转到 Attack_3，超出窗口则回归 Idle。

---

## 常见误区

**误区一：用布尔标志位代替状态枚举**  
初学者常使用 `isAttacking`、`isBlocking`、`isDodging` 等多个布尔值管理战斗逻辑，这会导致同时有多个标志为 true 的非法状态（如 `isAttacking = true` 且 `isBlocking = true`），产生无法预料的动画混合和伤害判定错误。正确做法是使用单一枚举值 `CombatState { Idle, Attack, Hit, Dodge, Block }` 保证互斥性，每帧只处于且仅处于一个状态。

**误区二：将 Hit 状态设置为可以被任意状态中断**  
若 Hit 状态没有霸体保护机制，连续快速攻击的敌人可以将角色锁定在 Hit 状态的无限循环中（"打桩机效应"），角色永远无法执行 Dodge 或 Block 来反击。解决方案是为 Hit 状态添加"无敌帧后段"（通常在受击动画的后 30% 时长内），或实现"硬直衰减（Hitstun Decay）"机制：同一来源的连续攻击每次减少 20% 的硬直时长，第 5 次以后强制触发"受身（Tech）"状态而不再进入完整 Hit 状态。

**误区三：忽略跨状态的动画过渡时间**  
在 Unity Animator 中，从 Attack 到 Hit 的状态转换如果设置了 0.1 秒的过渡时间（Transition Duration），那么在这段过渡期间，角色处于两个状态的混合动画中，但状态机逻辑已进入 Hit 状态，伤害判定代码开始执行 Hit 逻辑，而攻击的伤害盒可能仍在过渡中残留激活。战斗状态机的动画过渡时间应尽可能设置为 0（即时切换），或者单独用代码控制伤害盒的激活与关闭，与动画过渡时间解耦。

---

## 知识关联

**前置知识：移动状态机**  
移动状态机（Walk、Run、Jump、Fall）与战斗状态机在许多动作游戏中以层级或并行方式共存。移动状态机处理角色的位移向量，战斗状态机处理攻击判定；在实现时，通常将两者合并为一个 Animator Controller 的不同 Layer，战斗层设置为 Override 模式并将权重设为 1，在攻击时覆盖移动层的上半身动画，下半身仍播放移动动画，这就是"动画遮罩（Avatar Mask）"技术的典型应用场景。

**后续知识：行为树与动