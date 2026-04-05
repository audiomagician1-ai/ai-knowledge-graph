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


# 战斗状态机

## 概述

战斗状态机（Combat State Machine）是专门用于管理角色战斗行为切换的有限状态机系统，其核心由 **Idle → Attack → Hit → Dodge → Block** 五个基础状态及其转换条件构成。与移动状态机关注位移逻辑不同，战斗状态机需要精确处理帧级别的攻击判定窗口、无敌帧（I-Frame）区间和动作打断优先级。

战斗状态机最早在街机格斗游戏时代（1991年《街头霸王II》）被系统化应用，彼时状态数量极为有限，通常不超过8个。现代3A游戏如《黑暗之魂》系列将战斗状态扩展至数十个，并引入了状态叠加（State Layering）机制，允许上半身和下半身同时运行不同状态。理解战斗状态机对动画工程师至关重要，因为错误的状态转换会直接导致攻击判定与动画帧不同步，产生"幽灵攻击"或"漏判"等严重玩法缺陷。

## 核心原理

### 五大基础状态的定义与职责

**Idle（待机）** 是战斗状态机的默认状态，角色处于可接受任意输入的完全响应模式。Idle 状态会持续检测攻击指令（Attack Button）、被击事件（Hit Event）和闪避输入（Dodge Input），一旦检测到有效输入即立即触发转换。

**Attack（攻击）** 状态内部通常包含三个子阶段：前摇（Startup）、活跃帧（Active）和后摇（Recovery）。以典型动作游戏为例，一个普通攻击的时序可能为：前摇 6 帧 → 活跃帧 3 帧 → 后摇 12 帧，共 21 帧。只有 Active 阶段才触发碰撞盒（Hitbox）检测，前摇和后摇阶段的攻击输入会被记录为"缓冲指令"（Input Buffer），用于连段衔接。

**Hit（受击）** 状态负责播放受击动画并施加击退（Knockback）位移。此状态通常具有最高的被打断优先级，即使角色正在执行 Attack 动作，接收到足够硬直值（Hitstun Value）的打击也会强制切换至 Hit 状态。Hit 状态的持续时间由伤害方攻击的 Hitstun 参数决定，典型范围为 10~30 帧。

**Dodge（闪避）** 状态是战斗状态机中唯一包含**无敌帧**的状态。无敌帧通常设置在闪避动画的第 3~12 帧，在此区间内角色的受击碰撞盒（Hurtbox）被完全禁用。Dodge 状态仅能从 Idle 状态转入，不能从 Hit 状态直接触发（防止玩家在被连击时逃脱）。

**Block（格挡）** 状态将受到的伤害按固定比例削减，典型配置为削减 70%~80% 的物理伤害，但无法防御魔法或投技（Grab）。Block 状态在成功格挡时会触发一个短暂的 **Parry Window**（通常为 2~4 帧），若攻击恰好落在此窗口内则触发完美格挡（Perfect Block），使攻击方进入强制硬直。

### 状态转换矩阵

战斗状态机的合法转换关系可用矩阵表达：

| 当前状态 \ 目标状态 | Idle | Attack | Hit | Dodge | Block |
|---|---|---|---|---|---|
| **Idle** | — | ✓ | ✓ | ✓ | ✓ |
| **Attack** | ✓（后摇结束） | ✓（连段缓冲） | ✓（被打断） | ✗ | ✗ |
| **Hit** | ✓（硬直结束） | ✗ | ✗ | ✗ | ✗ |
| **Dodge** | ✓（动画结束） | ✓（取消帧） | ✗（无敌期） | ✗ | ✗ |
| **Block** | ✓（松开格挡键） | ✗ | ✓（格挡破防） | ✓ | — |

### 优先级系统与状态打断规则

战斗状态机需要为每个状态分配一个**打断优先级（Interrupt Priority）**整数值。典型配置为：Hit = 10、Dodge = 7、Block = 5、Attack = 3、Idle = 0。当新状态请求的优先级高于当前状态的"防打断阈值（Interrupt Resistance）"时，才允许强制切换。攻击的活跃帧阶段通常设置 Interrupt Resistance = 8，意味着只有 Hit 事件（优先级10）可以打断活跃攻击，而 Dodge（优先级7）无法在出招时取消。

## 实际应用

**《艾尔登法环》的动作取消系统**：游戏中每个攻击动画在特定帧数后进入"取消窗口（Cancel Window）"，玩家可在此窗口内输入闪避将 Attack 状态强制转换为 Dodge 状态，即所谓的"攻击取消闪避"。这一机制通过在 Attack 状态的后摇阶段临时将 Dodge 的转换权限从 ✗ 改为 ✓ 来实现，无需修改整体状态矩阵。

**Unity Animator 中的实现**：在 Unity 的 Animator Controller 中，战斗状态机的五个状态对应五个 Animation State，通过 `SetBool("IsBlocking", true)` 和 `SetTrigger("Hit")` 等参数驱动转换。Hit 状态通常使用 Trigger（而非 Bool）参数，确保受击响应为一次性事件，不会因 Bool 值滞留而导致状态卡死。攻击连段的 Input Buffer 则通过 `OnStateEnter` 回调中的协程实现，缓冲窗口通常设置为 0.1~0.15 秒（约 6~9 帧，以60fps计）。

**横版动作游戏的连段状态链**：格斗游戏中连段通过在 Attack 状态内嵌套子状态机实现。以三段连击为例：Attack_1 → Attack_2 → Attack_3，每段攻击在其活跃帧结束后开放一个 150ms 的连段接受窗口，期间若检测到再次按下攻击键，则转换至下一段攻击子状态，否则进入后摇并最终回到 Idle。

## 常见误区

**误区一：Dodge 状态可以从任何状态触发**。初学者常误将 Dodge 设计为全局转换（Any State → Dodge），导致角色在 Hit 硬直期间也能通过闪避逃脱。正确设计应限制 Dodge 仅从 Idle 和 Block 状态触发，保持战斗的风险惩罚。部分游戏（如《忍者外传》）刻意允许受击取消，但这需要在 Hit 状态中额外检测"受击闪避"输入并设置专属的短无敌帧，而非直接共用常规 Dodge 的无敌帧数值。

**误区二：Attack 状态是单一不可分割的状态**。许多新手将整个攻击动画视为一个黑盒状态，忽略前摇/活跃帧/后摇的子阶段划分。这会导致无论攻击处于哪个阶段，其打断规则完全相同——实际上活跃帧应有最高的打断抵抗值，而后摇阶段应更容易被打断甚至允许玩家主动取消。

**误区三：Block 状态完全免疫 Hit 状态转换**。格挡并非无敌，当攻击伤害超过格挡韧性值（Block Stamina）上限时，应强制将 Block 状态切换至 Hit 状态（格挡破防）。若不实现此机制，玩家可以无限格挡而不消耗资源，破坏战斗平衡。

## 知识关联

**前置概念——移动状态机**：移动状态机处理 Walk、Run、Jump、Fall 等位移状态，与战斗状态机通常以**并行层（Parallel Layer）**方式运行。在 Unity Animator 中，移动逻辑占据 Base Layer，战斗逻辑运行在独立的 Combat Layer（权重设为1），两者通过 Avatar Mask 分离控制区域——战斗层可仅影响上半身骨骼，从而实现角色跑动时挥剑的自然混合。

**后续概念——行为树与动画**：当战斗状态数量超过15个时，纯状态机的转换矩阵会急剧膨胀（N个状态理论上需要管理 N²个转换条件）。行为树（Behavior Tree）通过将决策逻辑从状态本身中剥离，以选择节点（Selector）和序列节点（Sequence）组织战斗决策，能更优雅地处理复杂AI战斗行为。战斗状态机中积累的"状态定义"和"帧数据"知识，会直接成为行为树叶节点（Action Node）的执行内容。